"""Check the native Dashboard with a disposable database and a virtual display."""
import argparse
from contextlib import closing
from datetime import date
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from unittest.mock import patch

import customtkinter as ctk

from app import Dashboard
from localization import LANGUAGE_CODES
from preferences import DEFAULTS
from storage import Store


def assert_visible(widget, viewport):
    left, top = widget.winfo_rootx(), widget.winfo_rooty()
    right, bottom = left + widget.winfo_width(), top + widget.winfo_height()
    assert widget.winfo_ismapped(), widget
    assert viewport.winfo_rootx() <= left < right <= viewport.winfo_rootx() + viewport.winfo_width(), widget
    assert viewport.winfo_rooty() <= top < bottom <= viewport.winfo_rooty() + viewport.winfo_height(), widget


def exam_marks(agenda):
    return {cell.cget('text') for cell in agenda.cells if '•' in cell.cget('text')}


def wait_for_reveal(app):
    ready = ctk.BooleanVar(master=app, value=False)
    app.after(240, lambda: ready.set(True))
    app.wait_variable(ready)


def verify(app, subject_id, app_date, storage_date):
    app.geometry('1024x700')
    app.update()
    app.reflow()
    app.update()
    viewport = app.scroll._parent_canvas
    clock = app.focus_clock
    assert app.brand_tile.cget('image') is app.brand_logo
    assert app.brand_tile.cget('text') == ''
    assert len(app.brand_window_icons) == (1 if sys.platform == 'darwin' else 6)
    names = set(app.tk.call('image', 'names'))
    assert all(str(icon) in names for icon in app.brand_window_icons)
    assert app.layout_mode == 'compact'
    assert (clock.time_label.cget('text'), clock.percent) == ('180:00', 0)
    assert exam_marks(app.agenda) == {'4 •', '10 •', '12 •', '15 •', '17 •', '18 •', '30 •'}
    selected = next(cell for cell in app.agenda.cells if cell.cget('text') == '10 •')
    assert selected.cget('fg_color') == app.start_button.cget('fg_color')
    assert len(app.exams.winfo_children()) == 5
    for row in app.exams.winfo_children():
        assert any('2026-11-' in label.cget('text') for label in row.winfo_children())

    for start in (0, 1):
        viewport.yview_moveto(start)
        assert app.focus_search() == 'break'
        app.update()
        assert_visible(app.search, viewport)
    visible_position = viewport.yview()
    app.focus_search()
    app.update()
    assert viewport.yview() == visible_position

    app.start_focus(subject_id)
    app.running_since -= 5400
    app.pause_focus()
    app.tick()
    assert (clock.time_label.cget('text'), clock.percent) == ('90:00', 50)
    assert clock.caption_label.cget('text') == app.translator.text('Paused')

    saved = app.store.save_preferences(
        dict(DEFAULTS, ui_language=app.translator.language, appearance_mode='Light', focus_minutes=1),
        expected_revision=1,
    )
    app.apply_preferences(saved)
    assert ctk.get_appearance_mode() == 'Light'
    assert app.focus_target == 10800 and clock.percent == 50

    app_date.today.return_value = storage_date.today.return_value = date(2026, 12, 1)
    app.tick()
    assert app.active_day == date(2026, 12, 1)
    assert exam_marks(app.agenda) == {'1 •'}
    assert sum(bool(cell.cget('text')) for cell in app.agenda.cells) == 31
    assert clock.time_label.cget('text') == '90:00'

    app.navigate('Settings')
    with patch.object(app.store, 'add_session', side_effect=sqlite3.OperationalError('full')):
        assert not app.finish_focus()
    app.toggle_sidebar()
    app.update()
    assert app.collapsed and app.focus_alert.cget('text') == '!'
    assert_visible(app.focus_alert, app.sidebar)
    with patch.object(app.scroll, 'scroll_to_widget', wraps=app.scroll.scroll_to_widget) as reveal:
        app.focus_alert.invoke()
        app.navigate('Settings')
        app.update()
        reveal.assert_not_called()
    assert app.current_page == 'Settings' and app.session_open
    app.focus_alert.invoke()
    app.update()
    assert app.current_page == 'Dashboard'
    assert_visible(app.finish_button, viewport)
    assert_visible(app.focus_retry_label, viewport)

    assert app.finish_focus()
    assert app.store.seconds() == 5400
    assert (clock.time_label.cget('text'), clock.percent) == ('01:00', 0)
    app.start_focus(subject_id)
    assert app.focus_target == 60
    assert app.finish_focus()

    checkpoint = app.store.start_focus_checkpoint(subject_id, 60)
    app.store.checkpoint_focus(checkpoint['id'], 30)
    app.store.release_focus()
    app.refresh_focus_recovery()
    app.focus_search()
    app.update()
    search_position = viewport.yview()
    wait_for_reveal(app)
    assert viewport.yview() == search_position
    assert_visible(app.search, viewport)

    app.refresh_focus_recovery()
    wait_for_reveal(app)
    assert_visible(app.recovery_status, viewport)
    assert_visible(app.recover_focus_button, viewport)
    assert_visible(app.discard_focus_button, viewport)
    app.recover_focus_button.invoke()
    assert app.session_open and app.running_since is None
    assert (clock.time_label.cget('text'), clock.percent) == ('00:30', 50)
    assert app.finish_focus()


def check(language, scale):
    ctk.set_widget_scaling(scale)
    ctk.set_window_scaling(scale)
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'study.sqlite3'
        with closing(Store(path)) as store:
            store.save_preferences(dict(DEFAULTS, focus_minutes=180, ui_language=language), expected_revision=0)
            subject_id = store.create_subject(('Математика ' * 10).strip(), exam_date='2026-11-04')
            exams = ('2026-11-10', '2026-11-12', '2026-11-15', '2026-11-17',
                     '2026-11-18', '2026-11-30', '2026-12-01')
            for index, exam in enumerate(exams, start=1):
                store.create_subject(f'Exam {index}', exam_date=exam)
        with patch('app.date', wraps=date) as app_date, patch('storage.date', wraps=date) as storage_date:
            app_date.today.return_value = storage_date.today.return_value = date(2026, 11, 10)
            app = Dashboard(path)
            errors = []
            app.report_callback_exception = lambda _kind, error, _traceback: errors.append(error)
            try:
                verify(app, subject_id, app_date, storage_date)
                assert not errors, errors
            finally:
                app.destroy()
                app.store.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language', choices=LANGUAGE_CODES)
    parser.add_argument('--scale', type=float, choices=(1.0, 1.5), default=1.0)
    args = parser.parse_args()
    if args.language:
        check(args.language, args.scale)
        return
    for language in LANGUAGE_CODES:
        for scale in (1.0, 1.5):
            subprocess.run(
                [sys.executable, '-X', 'faulthandler', __file__, '--language', language, '--scale', str(scale)],
                check=True,
                timeout=7,
            )
    print('PASS: Dashboard at 100/150% in four languages, compact search, exam marks and rollover, '
          'focus clock, preference changes and guarded retry reveal', flush=True)


if __name__ == '__main__':
    main()
