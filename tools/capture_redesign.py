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
    parser.add_argument('--empty', action='store_true', help='Empty Dashboard; requires --dashboard-only')
    args = parser.parse_args()
    if args.empty and not args.dashboard_only:
        parser.error('--empty requires --dashboard-only')
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
                topic = store.create_topic(sid, 'Data structures')
                store.create_question(sid, 'Which structure follows first in, first out?',
                                      ['Queue', 'Stack', 'Binary tree', 'Hash table'], 0, 'Easy', topic)
                store.create_question(sid, 'What is the purpose of a database transaction?',
                                      ['Group changes atomically', 'Draw a chart', 'Choose a font', 'Start a timer'], 0, 'Easy', topic)
                deck = store.create_deck(sid, 'Data structures', 'Disposable review cards')
                store.create_flashcard(deck, 'What does FIFO mean?', 'First in, first out: the earliest item added is removed first.')
                store.create_flashcard(deck, 'What does LIFO mean?', 'Last in, first out: the most recent item added is removed first.')
                store.add_session(1500, sid, 'Computer Science')
                attempt = store.start_practice(sid, 2)
                store.save_practice_answer(attempt, 0, 1)
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
            app.navigate('Flashcards')
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
        'screens': ['dashboard'] if args.dashboard_only else ['dashboard', 'practice', 'flashcard', 'flashcard-revealed'],
    }, indent=2) + '\n')
    print('PASS: disposable ' + args.mode + ' design captures')


if __name__ == '__main__':
    main()
