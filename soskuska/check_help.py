"""In-app Help on a virtual display: context topics, search, layout, sidebar fit and isolation."""
import argparse
import subprocess
import sys
import tempfile
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk

from app import Dashboard
from help_content import PAGE_TOPICS, load_topics
from localization import LANGUAGE_CODES
from preferences import DEFAULTS
from storage import Store
from theme import COLORS as C

PROBE_TIMEOUT = 60


def inside(widget, container):
    left, top = widget.winfo_rootx(), widget.winfo_rooty()
    right, bottom = left + widget.winfo_width(), top + widget.winfo_height()
    assert widget.winfo_ismapped(), widget
    assert container.winfo_rootx() <= left < right <= container.winfo_rootx() + container.winfo_width(), widget
    assert container.winfo_rooty() <= top < bottom <= container.winfo_rooty() + container.winfo_height(), widget


def labels_fit(page):
    """Every article label stays inside the article card; no raw label markers are shown."""
    article = page.article
    right = article.winfo_rootx() + article.winfo_width()
    for widget in article.winfo_children():
        if isinstance(widget, ctk.CTkLabel):
            assert '**' not in widget.cget('text'), widget.cget('text')
            assert widget.winfo_rootx() + widget.winfo_width() <= right, widget.cget('text')


def topic_buttons_fit(app, page):
    for topic_id, button in page.topic_buttons.items():
        if button.winfo_ismapped():
            # Unscaled CTkFont measures logical units; selected titles are bold.
            needed = app.font(13, True).measure(button.cget('text')) + 20
            assert needed <= app.scroll.logical_pixels(button.winfo_width()), (topic_id, button.cget('text'))


def verify(app, language, subject_id):
    assert app.help_page is None, 'Help must be built on first use, not at startup.'
    viewport = app.scroll._parent_canvas
    app.geometry('1024x700'); app.update(); app.reflow(); app.update()
    sidebar = app.sidebar
    # The Help control shares the Settings row: nothing in the 1024 x 700 sidebar is pushed out.
    inside(app.help_btn, sidebar)
    inside(app.settings_btn, sidebar)
    footer_bottom = app.footer.winfo_rooty() + app.footer.winfo_height()
    assert footer_bottom <= sidebar.winfo_rooty() + sidebar.winfo_height()
    assert app.help_btn.winfo_rooty() == app.settings_btn.winfo_rooty()

    before = app.store.db.total_changes
    # Unsaved drafts elsewhere survive a trip to Help.
    app.navigate('My Subjects'); app.subject_page.show_form()
    app.subject_page.name_entry.insert(0, 'Draft kept')
    assert app.open_help() == 'break'
    page = app.help_page
    assert app.current_page == 'Help' and page.selected == PAGE_TOPICS['My Subjects']
    assert app.help_btn.cget('fg_color') == C['nav_selected']
    assert not app.content.winfo_manager() and not app.subject_page.winfo_manager()
    app.update()
    # Compact: topics are listed above the article in two columns.
    assert page.side is False
    assert int(page.article.grid_info()['row']) == 1
    columns = {int(b.grid_info()['column']) for b in page.topic_buttons.values() if b.winfo_manager()}
    assert columns == {0, 1}
    topic_buttons_fit(app, page); labels_fit(page)
    app.navigate('My Subjects')
    assert app.subject_page.name_entry.get() == 'Draft kept'
    app.subject_page.hide_form()

    # Context topics for every page, including the question bank.
    for name in ('Dashboard', 'Practice Tests', 'Flashcards', 'Statistics', 'AI Tutor', 'Settings'):
        app.navigate(name); app.open_help()
        assert page.selected == PAGE_TOPICS[name], (name, page.selected)
        assert page.title.cget('text') == page.by_id[PAGE_TOPICS[name]]['title']
    app.open_question_bank(subject_id); app.open_help()
    assert page.selected == 'questions'
    # Reopening Help from Help keeps the reader's place.
    page.show('csv-import'); app.navigate('Help')
    assert page.selected == 'csv-import'

    # Every topic renders, and its Open action reaches a real page.
    topics = load_topics(language)
    assert len(page.topic_buttons) == len(topics)
    for topic in topics:
        page.topic_buttons[topic['id']].invoke(); app.update_idletasks()
        assert page.selected == topic['id']
        labels_fit(page)
        if topic['page']:
            assert page.open_button is not None
        else:
            assert page.open_button is None
    page.show('flashcards'); page.open_button.invoke()
    assert app.current_page == 'Flashcards'
    app.navigate('Help')

    # Search: Ctrl/Cmd+K focuses it, results narrow the list, Esc clears it.
    with patch.object(page.search, 'focus_set') as focus:
        assert app.focus_search() == 'break'
        focus.assert_called_once_with()
    page.query.set('zzz-no-such-help'); app.update_idletasks()
    assert not any(b.winfo_manager() for b in page.topic_buttons.values())
    assert page.matches.cget('text') == app.translator.text('No help topics match your search. Try another word.')
    backups_title = page.by_id['backups']['title']
    page.query.set(backups_title.split()[0])
    shown = [topic_id for topic_id, b in page.topic_buttons.items() if b.winfo_manager()]
    assert 'backups' in shown and len(shown) < len(topics), shown
    assert page.selected in shown
    app.clear_search()
    assert page.query.get() == '' and all(b.winfo_manager() for b in page.topic_buttons.values())
    assert not page.matches.winfo_manager() and page.search_label.winfo_ismapped()
    # A context opening clears an old search so the page's topic is listed.
    page.query.set('zzz-no-such-help'); app.navigate('Statistics'); app.open_help()
    assert page.query.get() == '' and page.selected == 'statistics'

    # Wide: topics sit beside the article in one column.
    app.geometry('1440x900'); app.update(); app.update()
    assert page.side is True
    assert int(page.article.grid_info()['column']) == 1
    assert {int(b.grid_info()['column']) for b in page.topic_buttons.values()} == {0}
    topic_buttons_fit(app, page); labels_fit(page)
    inside(page.topic_buttons['getting-started'], viewport)
    # Collapsed sidebar stacks Help below Settings and keeps both reachable.
    app.toggle_sidebar(); app.update()
    inside(app.help_btn, sidebar)
    assert app.help_btn.winfo_rooty() > app.settings_btn.winfo_rooty()
    app.toggle_sidebar(); app.update()
    assert app.help_btn.winfo_rooty() == app.settings_btn.winfo_rooty()

    # Reading help never writes the database.
    assert app.store.db.total_changes == before, 'Help must not write study data.'


def check(language, scale):
    ctk.set_widget_scaling(scale)
    ctk.set_window_scaling(scale)
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'help.sqlite3'
        with closing(Store(path)) as store:
            store.save_preferences(dict(DEFAULTS, ui_language=language), expected_revision=0)
            subject_id = store.create_subject('Biology')
        with patch('socket.create_connection', side_effect=AssertionError('Help must not connect')):
            app = Dashboard(path)
            errors = []
            app.report_callback_exception = lambda _kind, error, _traceback: errors.append(error)
            try:
                app.update()
                verify(app, language, subject_id)
                assert not errors, errors
            finally:
                app.destroy()
                app.store.close()
    print(f'{language} {scale:g}x: help topics, search, context and layout passed', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language', choices=LANGUAGE_CODES)
    parser.add_argument('--scale', type=float, choices=(1.0, 1.5), default=1.0)
    args = parser.parse_args()
    if args.language:
        check(args.language, args.scale)
        return
    runs = [(language, 1.0) for language in LANGUAGE_CODES] + [('Russian', 1.5)]
    for language, scale in runs:
        subprocess.run([sys.executable, '-X', 'faulthandler', __file__, '--language', language, '--scale', str(scale)],
                       check=True, timeout=PROBE_TIMEOUT)
    print('PASS: in-app Help in four languages (and 150%): lazy build, context topics, search, '
          'compact/wide layout, sidebar fit, drafts kept, no network or writes', flush=True)


if __name__ == '__main__':
    main()
