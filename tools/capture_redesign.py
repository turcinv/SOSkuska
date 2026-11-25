"""Capture disposable redesign fixtures under Xvfb; run from the repository root.

Example: xvfb-run -a -s '-screen 0 1920x1080x24' python tools/capture_redesign.py --output /tmp/design-before
This is a design artifact utility, not a manual platform acceptance test.
"""
import argparse
from contextlib import ExitStack, closing
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import platform
import sqlite3
import sys
import tempfile
from unittest.mock import patch

ROOT = Path.cwd() if __file__ == '<stdin>' else Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'soskuska'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--mode', choices=('Light', 'Dark'), default='Light')
    parser.add_argument('--language', choices=('English', 'Czech', 'Slovak', 'Russian'), default='English')
    parser.add_argument('--size', choices=('wide', 'compact'), default='wide')
    parser.add_argument('--dashboard-only', action='store_true')
    parser.add_argument('--practice-views', action='store_true', help='Capture running/setup/confirmation/result/history only')
    parser.add_argument('--flashcard-views', action='store_true', help='Capture deck/review/empty/history views only')
    parser.add_argument('--authoring-views', action='store_true', help='Capture Subjects and Question Bank only')
    parser.add_argument('--report-views', action='store_true', help='Capture Statistics and offline Tutor views only')
    parser.add_argument('--timed-practice', action='store_true', help='Use a frozen five-minute fixture instead of untimed')
    parser.add_argument('--empty', action='store_true', help='Empty Dashboard; requires --dashboard-only')
    args = parser.parse_args()
    if args.empty and not args.dashboard_only:
        parser.error('--empty requires --dashboard-only')
    if sum((args.practice_views, args.dashboard_only, args.flashcard_views, args.authoring_views, args.report_views)) > 1:
        parser.error('Choose only one of --practice-views, --dashboard-only, --flashcard-views, --authoring-views and --report-views')
    dimensions = (1440, 900) if args.size == 'wide' else (1024, 700)
    args.output.mkdir(parents=True, exist_ok=True)
    # Xvfb captures must never open a native macOS/Windows application window.
    if sys.platform != 'linux' or not os.environ.get('DISPLAY'):
        parser.error('Run inside the Linux/Xvfb test container.')
    import customtkinter as ctk
    from PIL import ImageGrab
    from app import Dashboard
    from preferences import DEFAULTS
    from storage import Store

    class FixtureDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 11, 25)

    now = datetime(2026, 11, 25, 12, tzinfo=timezone.utc)
    errors = []
    with tempfile.TemporaryDirectory(prefix='soskuska-design-') as folder, ExitStack() as stack:
        for module in ('app', 'storage'):
            stack.enter_context(patch(module + '.date', FixtureDate))
        for module in ('storage', 'flashcard_page', 'practice_page'):
            stack.enter_context(patch(module + '.utc_now', return_value=now))
        stack.enter_context(patch('storage.random.sample', side_effect=lambda pool, count: pool[:count]))
        stack.enter_context(patch('socket.create_connection', side_effect=AssertionError('Capture must stay offline')))
        path = Path(folder) / 'fixture.sqlite3'
        with closing(Store(path)) as store:
            store.save_preferences(dict(DEFAULTS, appearance_mode=args.mode, ui_language=args.language), expected_revision=0)
            if not args.empty:
                sid = store.create_subject('Computer Science', 'Disposable design fixture', '2026-12-15')
                if args.authoring_views:
                    store.create_subject('Mathematics', 'Second disposable subject for the responsive grid')
                topic = store.create_topic(sid, 'Data structures')
                store.create_question(sid, 'Which structure follows first in, first out?',
                                      ['Queue', 'Stack', 'Binary tree', 'Hash table'], 0, 'Easy', topic)
                store.create_question(sid, 'What is the purpose of a database transaction?',
                                      ['Group changes atomically', 'Draw a chart', 'Choose a font', 'Start a timer'], 0, 'Easy', topic)
                deck = store.create_deck(sid, 'Data structures', 'Disposable review cards')
                store.create_flashcard(deck, 'What does FIFO mean?', 'First in, first out: the earliest item added is removed first.')
                store.create_flashcard(deck, 'What does LIFO mean?', 'Last in, first out: the most recent item added is removed first.')
                store.add_session(1500, sid, 'Computer Science')
                attempt = store.start_practice(sid, 2, minutes=5 if args.timed_practice else None)
                store.save_practice_answer(attempt, 0, 1)
                if args.report_views:
                    store.complete_practice(attempt)
                    saved=store.begin_tutor_turn(None,'http://127.0.0.1:11434','study-model:latest',
                        'How do queues and stacks differ?','English')
                    store.finish_tutor_turn(saved['id'],saved['turn_id'],
                        'A queue removes the oldest item first (FIFO). A stack removes the newest item first (LIFO).\n\nUse a queue for work handled in arrival order, and a stack for undo history. This is a disposable captured reply, not a live model response.',
                        'completed',expected_revision=saved['revision'])
        ctk.set_default_color_theme('dark-blue')
        ctk.set_widget_scaling(1)
        ctk.set_window_scaling(1)
        app = Dashboard(path)
        app.geometry(f'{dimensions[0]}x{dimensions[1]}+0+0')

        def guard(callback):
            def run():
                try:
                    callback()
                except Exception as exc:
                    errors.append(repr(exc))
                    app.destroy()
            return run

        def capture(name):
            app.update_idletasks()
            bbox = (app.winfo_rootx(), app.winfo_rooty(),
                    app.winfo_rootx() + app.winfo_width(), app.winfo_rooty() + app.winfo_height())
            screen = ImageGrab.grab(xdisplay=os.environ['DISPLAY'])
            assert 0 <= bbox[0] < bbox[2] <= screen.width and 0 <= bbox[1] < bbox[3] <= screen.height, (bbox, screen.size)
            image = screen.crop(bbox)
            assert image.size == dimensions, image.size
            image.save(args.output / (name + '.png'))

        def dashboard():
            if args.report_views:
                app.navigate("Statistics")
                app.after(400,guard(statistics))
                return
            if args.authoring_views:
                app.navigate('My Subjects')
                app.after(400, guard(subjects))
                return
            if args.flashcard_views:
                app.navigate('Flashcards')
                app.flashcard_page.show_decks()
                app.after(400, guard(decks))
                return
            if not args.practice_views:
                capture('dashboard')
            if args.dashboard_only:
                app.close()
                return
            app.navigate('Practice Tests')
            app.after(400, guard(practice))

        def practice():
            assert app.practice_page.run.winfo_ismapped()
            assert app.practice_page.choice.get() == 1
            capture('practice')
            if args.practice_views:
                app.practice_page.show_config()
                app.after(400, guard(practice_setup))
            else:
                app.navigate('Flashcards')
                app.flashcard_page.start_review(deck)
                app.after(400, guard(flashcard))

        def practice_setup():
            capture('practice-setup')
            app.practice_page.resume()
            app.practice_page.finish_button.invoke()
            app.after(400, guard(practice_confirm))

        def practice_confirm():
            assert app.practice_page.confirm.winfo_ismapped()
            capture('practice-confirm')
            app.practice_page.confirm_button.invoke()
            app.after(400, guard(practice_result))

        def practice_result():
            assert app.practice_page.results.winfo_ismapped()
            capture('practice-result')
            app.practice_page.show_config()
            app.scroll._parent_canvas.yview_moveto(1)
            app.after(400, guard(practice_history))

        def practice_history():
            app.update_idletasks()
            app.scroll._parent_canvas.yview_moveto(1)
            app.after(300, guard(practice_history_ready))

        def practice_history_ready():
            capture('practice-history')
            app.close()

        def statistics():
            capture('statistics')
            app.scroll._parent_canvas.yview_moveto(1)
            app.after(400,guard(statistics_daily))

        def statistics_daily():
            capture('statistics-daily')
            with patch.object(app.store,'statistics',side_effect=sqlite3.OperationalError('locked')):
                app.statistics_page.load()
            app.scroll.scroll_to_top()
            app.after(400,guard(statistics_retry))

        def statistics_retry():
            capture('statistics-retry')
            app.navigate('AI Tutor')
            app.after(400,guard(tutor))

        def tutor():
            assert app.tutor_page.task is None and app.tutor_page.connected_endpoint is None
            capture('tutor')
            app.tutor_page.open_button.invoke()
            app.tutor_page.prompt.insert('1.0','Give me a short example to check my understanding.')
            app.scroll._parent_canvas.yview_moveto(.35)
            app.after(400,guard(tutor_conversation))

        def tutor_conversation():
            capture('tutor-conversation')
            app.scroll._parent_canvas.yview_moveto(1)
            app.after(400,guard(tutor_footer))

        def tutor_footer():
            capture('tutor-footer')
            app.close()

        def subjects():
            capture('subjects')
            app.subject_page.show_form(sid)
            app.after(400, guard(subject_editor))

        def subject_editor():
            capture('subject-editor')
            app.subject_page.hide_form()
            app.open_question_bank(sid)
            app.after(400, guard(question_bank))

        def question_bank():
            capture('question-bank')
            app.question_bank.show_question_form(app.store.questions(sid)[0]['id'])
            app.after(400, guard(question_editor))

        def question_editor():
            capture('question-editor')
            app.scroll._parent_canvas.yview_moveto(0.45)
            app.after(400, guard(question_footer))

        def question_footer():
            capture('question-editor-footer')
            app.question_bank.hide_question_form()
            app.question_bank.show_topic_form(topic)
            app.after(400, guard(topic_editor))

        def topic_editor():
            capture('topic-editor')
            app.question_bank.hide_topic_form()
            app.question_bank.query.set('no matching fixture')
            app.scroll.scroll_to_top()
            app.after(400, guard(question_empty))

        def question_empty():
            capture('question-empty')
            app.close()

        def decks():
            capture('decks')
            app.flashcard_page.show_deck(deck)
            app.after(400, guard(deck_view))

        def deck_view():
            capture('deck')
            app.flashcard_page.start_review(deck)
            app.after(400, guard(flashcard))

        def flashcard():
            assert not app.flashcard_page.revealed
            capture('flashcard')
            app.flashcard_page.reveal_button.invoke()
            app.after(400, guard(revealed))

        def revealed():
            assert app.flashcard_page.revealed
            capture('flashcard-revealed')
            if args.flashcard_views:
                page = app.flashcard_page
                assert [button.grid_info()['column'] for button in page.rating_buttons.values()] == ([0, 1, 2, 3] if args.size == 'wide' else [0, 1, 0, 1])
                page.rating_buttons['Good'].invoke()
                page.reveal_button.invoke()
                page.rating_buttons['Good'].invoke()
                assert page.current_card is None
                app.after(400, guard(flashcard_complete))
            else:
                app.close()

        def flashcard_complete():
            capture('flashcard-complete')
            app.flashcard_page.show_deck(deck)
            app.after(400, guard(deck_no_due))

        def deck_no_due():
            capture('deck-no-due')
            app.flashcard_page.show_history()
            app.after(400, guard(flashcard_history))

        def flashcard_history():
            app.scroll._parent_canvas.yview_moveto(0)
            app.after(300, guard(flashcard_history_ready))

        def flashcard_history_ready():
            capture('flashcard-history')
            app.close()

        app.report_callback_exception = lambda kind, value, tb: (errors.append(repr(value)), app.destroy())
        app.after(800, guard(dashboard))
        app.after(15000, lambda: (errors.append('Capture timed out'), app.destroy()))
        try:
            app.mainloop()
        finally:
            app.store.close()
        if errors:
            raise RuntimeError(errors)
    (args.output / 'capture.json').write_text(json.dumps({
        'fixture_date': now.isoformat(), 'mode': args.mode, 'size': list(dimensions), 'language': args.language, 'empty': args.empty,
        'platform': platform.platform(), 'python': platform.python_version(),
        'customtkinter': ctk.__version__, 'content': 'Disposable fixture only; no user data',
        'scope': 'Linux Xvfb capture; not native Windows/macOS acceptance',
        'screens': (['statistics', 'statistics-daily', 'statistics-retry', 'tutor', 'tutor-conversation', 'tutor-footer']
                    if args.report_views else ['subjects', 'subject-editor', 'question-bank', 'question-editor', 'question-editor-footer', 'topic-editor', 'question-empty']
                    if args.authoring_views else ['decks', 'deck', 'flashcard', 'flashcard-revealed', 'flashcard-complete', 'deck-no-due', 'flashcard-history']
                    if args.flashcard_views else ['practice', 'practice-setup', 'practice-confirm', 'practice-result', 'practice-history']
                    if args.practice_views else ['dashboard'] if args.dashboard_only
                    else ['dashboard', 'practice', 'flashcard', 'flashcard-revealed']),
        'timed_practice': args.timed_practice,
    }, indent=2) + '\n')
    print('PASS: disposable ' + args.mode + ' design captures')


if __name__ == '__main__':
    main()
