"""Disposable explanation flow; loopback fixture only, suitable for container/Xvfb."""
import argparse
import gc
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import tkinter
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from storage import Store
from question_explanation import MODES
from localization import tr
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from ollama_fixture import FakeOllama

# Hang guard for each wait on the loopback fixture, not a speed requirement;
# a normal wait takes about 0.1 s. The old 6 s bound failed intermittently
# because cyclic garbage collection in the Tutor worker thread finalized Tk
# objects there and stalled it for about 4 s (fixed by main_thread_gc). The
# timeout message records the Tutor task state so a real hang can be told from
# a slow machine, and the summary line prints every wait time.
WAIT_TIMEOUT = 30


def check_main_thread_gc(app):
    """A worker thread's allocations must not finalize Tk objects; the Tk timer must."""
    finalized_on_main = []
    original = tkinter.Variable.__del__

    def tracking(variable):
        finalized_on_main.append(threading.current_thread() is threading.main_thread())
        original(variable)

    class Holder:
        pass
    with patch.object(tkinter.Variable, '__del__', tracking):
        holder = Holder()
        holder.variable, holder.cycle = ctk.StringVar(master=app), holder
        del holder
        kept = []
        # Enough tracked allocations for CPython to collect in this thread if allowed.
        worker = threading.Thread(target=lambda: kept.append([[] for _ in range(5000)]))
        worker.start()
        worker.join()
        assert finalized_on_main == [], 'a Tk object was finalized on a worker thread'
        deadline = time.monotonic() + WAIT_TIMEOUT
        while not finalized_on_main and time.monotonic() < deadline:
            app.update()
            time.sleep(0.02)
        # Other unreachable app variables may be swept at the same time; none may be off-main.
        assert True in finalized_on_main and False not in finalized_on_main, finalized_on_main
    assert not gc.isenabled()


def run(path, language='English', scale=1, layout=False):
    ctk.set_widget_scaling(scale)
    ctk.set_window_scaling(1)
    store = Store(path)
    preferences = store.preferences()
    store.save_preferences(dict(preferences, ui_language=language), expected_revision=preferences['revision'])
    sid = store.create_subject('Opaque Settings русский')
    store.create_question(sid, 'Ktorá odpoveď platí?\nВопрос пользователя',
                          ['jedna', 'dve', 'tri', 'štyri'], 2, explanation='Pôvodné vysvetlenie')
    aid = store.start_practice(sid, 1)
    store.save_practice_answer(aid, 0, 0)
    store.complete_practice(aid)
    store.delete_subject(sid)
    store.close()
    fixture = FakeOllama()
    app = Dashboard(path)
    app.geometry('1024x700')
    page, tutor = app.practice_page, app.tutor_page
    callback_errors = []
    waits = []
    app.report_callback_exception = lambda kind, value, tb: callback_errors.append(value)

    def wait(predicate):
        if predicate():
            return
        done = ctk.BooleanVar(value=False)
        started = time.monotonic()
        deadline = started + WAIT_TIMEOUT
        def poll():
            if predicate() or time.monotonic() > deadline:
                done.set(True)
            else:
                app.after(20, poll)
        app.after(20, poll)
        app.wait_variable(done)
        waits.append((time.monotonic() - started, sys._getframe(1).f_lineno))
        task = tutor.task
        assert predicate(), ('Timed out waiting for Tutor', {
            'task_kind': getattr(task, 'kind', None),
            'thread_alive': task.thread.is_alive() if task else None,
            'queued_events': task.events.qsize() if task else None,
            'requests': len(fixture.requests), 'status': tutor.status.cget('text') if hasattr(tutor, 'status') else None,
            'errors': callback_errors})
        assert not callback_errors, callback_errors

    def preview():
        app.navigate('Practice Tests')
        page.view_result(aid)
        page.explain_question(aid, 0)
        assert page.explanation_identity is not None
        return page.explanation_identity

    def bounds(widget):
        app.update_idletasks()
        canvas = app.scroll._parent_canvas
        assert widget.winfo_rootx() >= canvas.winfo_rootx()
        assert widget.winfo_rootx()+widget.winfo_width() <= canvas.winfo_rootx()+canvas.winfo_width()+2

    try:
        app.update()
        if not layout:
            check_main_thread_gc(app)
        identity = preview()
        prompt = identity[2]
        assert prompt.startswith('Question:\nKtorá')
        assert 'Pôvodné vysvetlenie' in prompt and 'Student answer: A' in prompt
        assert fixture.requests == [] and not tutor.turns
        if layout:
            for study_mode in MODES:
                page.explanation_mode_menu.selected(tr(app, study_mode))
                identity = page.explanation_identity
                prompt = identity[2]
                assert identity[3] == study_mode
                assert page.explanation_mode_menu.display_variable.get() == tr(app, study_mode)
                for geometry in ('1024x700', '1440x900'):
                    app.geometry(geometry)
                    for mode in ('Light', 'Dark', 'System'):
                        ctk.set_appearance_mode(mode)
                        app.update_idletasks()
                        bounds(page.explanation_panel)
                        bounds(page.explanation_mode_menu)
                        for button in page.explanation_actions.winfo_children():
                            bounds(button)
            page.prepare_explanation(identity)
            assert tutor.prompt.get('1.0', 'end-1c') == prompt
            app.update_idletasks()
            canvas = app.scroll._parent_canvas
            assert canvas.winfo_rooty() <= tutor.prompt.winfo_rooty() < canvas.winfo_rooty()+canvas.winfo_height()
            assert fixture.requests == []
            return
        page.cancel_explanation()
        page.prepare_explanation(identity)
        assert app.current_page == 'Practice Tests' and not tutor.prompt.get('1.0', 'end-1c')
        # Obsolete consent cannot act on a replacement preview.
        identity = preview()
        page.cancel_explanation()
        page.explain_question(aid, 0)
        page.prepare_explanation(identity)
        assert app.current_page == 'Practice Tests'
        # All dirty/busy/recovery states preserve the exact draft and result.
        for attribute, value in (('task', object()), ('unsaved_reply', True),
                                 ('pending_clear', True), ('pending_discard', True),
                                 ('pending_delete', (1, 1)), ('pending_recover', True),
                                 ('conversation_id', 99), ('turns', [{'status': 'completed'}])):
            old = getattr(tutor, attribute)
            setattr(tutor, attribute, value)
            identity = page.explanation_identity
            page.prepare_explanation(identity)
            assert app.current_page == 'Practice Tests' and page.explanation_identity == identity
            setattr(tutor, attribute, old)
        tutor.prompt.insert('1.0', '   ')
        page.prepare_explanation(page.explanation_identity)
        assert tutor.prompt.get('1.0', 'end-1c') == '   '
        tutor.prompt.delete('1.0', 'end')
        with patch.object(app.store, 'practice_items', side_effect=sqlite3.OperationalError('locked')):
            page.prepare_explanation(page.explanation_identity)
            assert 'Nothing was sent' in page.explanation_feedback.cget('text')
        # Opening failures leave a usable result and Cancel action; oversize is never truncated.
        with patch.object(app.store, 'practice_items', side_effect=sqlite3.OperationalError('locked')):
            page.explain_question(aid, 0)
            assert page.explanation_identity is None and page.results.grid_info()
        item = app.store.practice_items(aid)[0]
        with patch.object(app.store, 'practice_items', return_value=[dict(item, explanation='x'*4000)]):
            page.explain_question(aid, 0)
            assert page.explanation_identity is None
            assert 'limit is 4000' in page.explanation_feedback.cget('text')
        page.cancel_explanation()
        page.explain_question(aid, 0)
        identity = page.explanation_identity
        app.navigate('Dashboard')
        page.prepare_explanation(identity)
        assert app.current_page == 'Dashboard'
        identity = preview()
        with patch.object(app.store, 'practice_attempt', return_value=None):
            page.prepare_explanation(identity)
            assert app.current_page == 'Practice Tests'
        page.prepare_explanation(identity)
        assert app.current_page == 'AI Tutor'
        assert tutor.prompt.get('1.0', 'end-1c') == prompt
        assert not tutor.prepare_question_draft(prompt)
        assert not tutor.turns and fixture.requests == []
        tutor.endpoint.delete(0, 'end')
        tutor.endpoint.insert(0, fixture.url)
        tutor.connect()
        wait(lambda: tutor.task is None)
        assert len(fixture.requests) == 1
        # A failed pending-turn write keeps the prepared draft and starts no HTTP.
        with patch.object(app.store, 'begin_tutor_turn', side_effect=sqlite3.OperationalError('locked')):
            tutor.send()
        assert tutor.prompt.get('1.0', 'end-1c') == prompt and len(fixture.requests) == 1
        # A failed reply write is retryable without sending the question twice.
        with patch.object(app.store, 'finish_tutor_turn', side_effect=sqlite3.OperationalError('locked')):
            tutor.send()
            wait(lambda: tutor.task is None)
            assert tutor.unsaved_reply and len(tutor.turns) == 1
        request = fixture.requests[-1][2]
        assert request['messages'][-1]['content'] == prompt
        assert request['model'] == 'study-model:latest'
        tutor.retry_save()
        tutor.retry_save()
        assert not tutor.unsaved_reply
        saved = app.store.tutor_conversation(tutor.conversation_id)
        assert len(saved['turns']) == 1 and saved['turns'][0]['prompt'] == prompt
        assert saved['turns'][0]['status'] == 'completed'
        # Explicit Stop still retains a partial and one ordinary saved turn.
        tutor.new_chat()
        tutor.new_chat()
        identity = preview()
        page.prepare_explanation(identity)
        fixture.mode = 'slow'
        tutor.send()
        wait(lambda: tutor.turns and tutor.turns[-1]['answer'] == 'Hello ')
        tutor.stop()
        wait(lambda: tutor.task is None)
        assert tutor.turns[-1]['status'] == 'stopped'
        assert app.store.practice_attempt(aid)['correct'] == 0
        assert app.store.practice_items(aid)[0]['selected_option'] == 0
        assert not callback_errors, callback_errors
        if waits:
            slowest = max(waits)
            print(f'Tutor waits: {len(waits)}, slowest {slowest[0]:.2f} s at line {slowest[1]} '
                  f'(timeout {WAIT_TIMEOUT} s); all: ' + ', '.join(f'{s:.2f}' for s, _ in waits), flush=True)
    finally:
        tutor.shutdown()
        app.destroy()
        app.store.close()
        fixture.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--layout', action='store_true')
    parser.add_argument('--language', default='English')
    parser.add_argument('--scale', type=float, default=1)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        run(Path(directory)/'study.sqlite3', args.language, args.scale, args.layout)
    if not args.layout:
        for language in ('English', 'Czech', 'Slovak', 'Russian'):
            for scale in ('1', '1.5'):
                subprocess.run([sys.executable, __file__, '--layout', '--language', language,
                                '--scale', scale], check=True, timeout=15)
    print('PASS: translated explanation layout' if args.layout else 'PASS: saved-question preview, guarded draft, explicit request, save retries, Stop and four-language startup layouts')
