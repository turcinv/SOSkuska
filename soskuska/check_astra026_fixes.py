"""Astra regressions with disposable Stores; run only in a container/virtual display."""
import argparse
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
import customtkinter as ctk
from app import Dashboard
from storage import Store
from localization import tr

NOW = datetime(2026, 11, 26, 12, tzinfo=timezone.utc)
DECK_CONFLICT = 'This deck changed in another window. Your draft is kept; copy your changes, then reopen Edit deck to reload.'
TOPIC_CONFLICT = 'This topic changed in another window. Your draft is kept; copy your changes, then reopen Rename topic to reload.'


def run(path, language, scale):
    ctk.set_widget_scaling(scale)
    ctk.set_window_scaling(1)
    store = Store(path)
    prefs = store.preferences()
    store.save_preferences(dict(prefs, ui_language=language), expected_revision=prefs['revision'])
    store.close()
    app = Dashboard(path)
    other = Store(path)
    errors = []
    app.report_callback_exception = lambda kind, value, tb: errors.append(value)
    f, q = app.flashcard_page, app.question_bank
    def name(text):
        f.name_entry.delete(0, 'end'); f.name_entry.insert(0, text)
    try:
        app.geometry('1024x700')
        sid = app.store.create_subject('Physics')
        deck = app.store.create_deck(sid, 'Motion', 'Original description')
        topic = app.store.create_topic(sid, 'Speed')
        app.navigate('Flashcards'); f.open_deck(deck); f.deck_form(deck)
        snapshot = f.editing_deck_snapshot
        other.update_deck(deck, 'Motion', 'New description')
        name('Draft title'); f.save_button.invoke()
        assert f.view == 'deck_form' and f.editing_deck_snapshot is snapshot
        assert f.deck_form_notice.cget('text') == tr(app, DECK_CONFLICT)
        assert f.name_entry.get() == 'Draft title'
        assert f.description.get('1.0','end-1c') == 'Original description'
        assert other.deck(deck)['description'] == 'New description'
        app.update_idletasks()
        app.scroll.scroll_to_widget(f.save_button)
        app.update_idletasks()
        canvas=app.scroll._parent_canvas
        assert f.save_button.winfo_rootx()+f.save_button.winfo_width() <= canvas.winfo_rootx()+canvas.winfo_width()+2
        assert f.deck_form_notice.winfo_rootx()+f.deck_form_notice.winfo_width() <= canvas.winfo_rootx()+canvas.winfo_width()+2
        app.navigate('Dashboard'); app.navigate('Flashcards')
        assert f.name_entry.get() == 'Draft title' and f.editing_deck_snapshot is snapshot
        f.deck_form(deck); name('My title'); f.save_button.invoke()
        assert f.view == 'deck' and f.deck_refresh_pending is None
        assert other.deck(deck)['description'] == 'New description'
        # A committed write followed by a failed read exposes Refresh, never another Save.
        for new in (False, True):
            f.deck_form(None if new else deck)
            name('Created deck' if new else 'Committed title')
            with patch.object(f, '_show_deck', side_effect=sqlite3.OperationalError('locked')):
                f.save_button.invoke()
                saved_id = f.editing_deck
                assert f.deck_refresh_pending == saved_id
                assert f.save_button.cget('text') == tr(app, 'Refresh deck')
                assert f.name_entry.cget('state') == 'disabled'
                saved_text=f.description.get('1.0','end-1c')
                f.description.insert('end',' must not edit saved content')
                assert f.description.get('1.0','end-1c') == saved_text
                assert tr(app, 'Deck saved. Refresh deck to load saved content; do not save it again.') in f.deck_form_notice.cget('text')
                other.update_deck(saved_id, 'External '+str(new), 'External description')
                changes=app.store.db.total_changes
                f.save_button.invoke()
                assert app.store.db.total_changes == changes
            f.refresh()
            assert f.view == 'deck' and f.deck_refresh_pending is None
            assert f.status.cget('text') == tr(app, 'Deck saved on this device.')
            assert other.deck(saved_id)['name'] == 'External '+str(new)
            assert app.store.db.total_changes == changes
        app.open_question_bank(sid); q.show_topic_form(topic)
        old=q.editing_topic_snapshot
        other.update_topic(topic, 'Velocity')
        q.topic_entry.delete(0,'end'); q.topic_entry.insert(0,'Draft topic'); q.save_topic_button.invoke()
        assert q.topic_form.grid_info() and q.editing_topic_snapshot is old
        assert q.topic_entry.get() == 'Draft topic' and q.topic_error.cget('text') == tr(app, TOPIC_CONFLICT)
        assert other.topic(topic)['name'] == 'Velocity'
        q.show_topic_form(topic)
        q.topic_entry.delete(0,'end'); q.topic_entry.insert(0,'Final topic'); q.save_topic_button.invoke()
        assert other.topic(topic)['name'] == 'Final topic'
        # The due queue and review UI must agree for a restored aware offset.
        card=app.store.create_flashcard(deck,'Front','Back')
        due=(NOW-timedelta(minutes=5)).astimezone(timezone(timedelta(hours=10))).isoformat()
        with app.store.db: app.store.db.execute('UPDATE flashcards SET due_at=? WHERE id=?',(due,card))
        app.navigate('Flashcards')
        with patch('storage.utc_now', return_value=NOW), patch('flashcard_page.utc_now', return_value=NOW):
            f.start_review(deck)
            assert f.current_card['id'] == card
            f.reveal()
            f.rating_buttons['Good'].invoke()
        assert app.store.flashcard(card)['review_count'] == 1
        # Extremely early accepted timestamps must remain renderable as well as queryable.
        with app.store.db: app.store.db.execute('UPDATE flashcards SET due_at=? WHERE id=?',('0001-01-01T00:00:00+01:00',card))
        f.open_deck(deck)
        assert f.view == 'deck'
        assert not errors,errors
    finally:
        app.tutor_page.shutdown(); app.destroy(); other.close(); app.store.close()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--language')
    parser.add_argument('--scale',type=float,default=1)
    args=parser.parse_args()
    if args.language:
        with tempfile.TemporaryDirectory() as directory:
            run(Path(directory)/'study.db',args.language,args.scale)
    else:
        for language in ('English','Czech','Slovak','Russian'):
            for scale in ('1','1.5'):
                subprocess.run([sys.executable,__file__,'--language',language,'--scale',scale],check=True,timeout=15)
    print('PASS: stale deck/topic drafts, explicit reload, committed refresh-only retry, timezone due/review and four-language startup layouts')
