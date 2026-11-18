"""Native AI Tutor checks using a loopback fixture, never a real model/service."""
import sys
import tempfile
import time
import traceback
from pathlib import Path

import customtkinter as ctk
from app import Dashboard
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from ollama_fixture import FakeOllama


def check(path):
    fixture = FakeOllama()
    app = Dashboard(path)
    page = app.tutor_page
    errors = []
    heartbeat = []

    def guarded(callback):
        def run():
            try:
                callback()
            except Exception as exc:
                errors.append(str(exc))
                traceback.print_exc()
                app.destroy()
        return run

    def wait_for(predicate, callback, deadline=None):
        deadline = deadline or time.monotonic()+5
        def poll():
            assert time.monotonic() < deadline, f'Timed out waiting for {callback.__name__}'
            if predicate():
                callback()
            else:
                app.after(50, guarded(poll))
        app.after(50, guarded(poll))

    def endpoint(value):
        page.endpoint.delete(0, 'end')
        page.endpoint.insert(0, value)

    def initial():
        assert fixture.requests == []
        app.geometry('1024x700')
        app.navigate('AI Tutor')
        app.update_idletasks()
        assert page.winfo_ismapped()
        right = app.winfo_rootx()+app.winfo_width()
        assert page.connect_button.winfo_rootx()+page.connect_button.winfo_width() <= right
        assert page.language_menu.winfo_rootx()+page.language_menu.winfo_width() <= right
        assert page.clear_button.winfo_rootx()+page.clear_button.winfo_width() <= right
        page.prompt.insert('1.0', 'What is a limit?')
        endpoint('http://user:secret@localhost')
        page.connect_button.invoke()
        assert 'credentials' in page.status.cget('text') and page.task is None
        assert page.prompt.get('1.0','end-1c') == 'What is a limit?'
        endpoint(fixture.url)
        page.connect_button.invoke()
        wait_for(lambda: page.task is None, connected)

    def connected():
        assert page.models == ['study-model:latest']
        assert 'Ready' in page.status.cget('text')
        page.language.set('Russian')
        page.send_button.invoke()
        page.prompt.insert('1.0', 'blocked while generating')
        assert page.prompt.get('1.0', 'end-1c') == ''
        assert page.send_button.cget('state') == 'disabled'
        wait_for(lambda: page.task is None, complete)

    def complete():
        assert page.turns[-1]['status'] == 'completed'
        assert 'svět / мир' in page.transcript.get('1.0','end-1c')
        assert 'Reply in Russian' in fixture.requests[-1][2]['messages'][0]['content']
        page.new_chat()
        assert page.pending_clear
        app.navigate('Dashboard')
        app.query.set('dashboard search')
        app.navigate('AI Tutor')
        assert not page.pending_clear and len(page.turns) == 1
        app.focus_search()
        app.clear_search()
        assert app.query.get() == 'dashboard search'
        page.prompt.insert('1.0', 'Keep explaining')
        fixture.mode = 'slow'
        page.send_button.invoke()
        wait_for(lambda: page.turns[-1]['answer'] == 'Hello ', partial)

    def partial():
        app.navigate('Dashboard')
        before = app.scroll._parent_canvas.yview()[0]
        app.after(100, lambda: heartbeat.append(True))
        def responsive():
            assert page.task is not None
            assert app.scroll._parent_canvas.yview()[0] == before
            app.navigate('AI Tutor')
            page.stop_button.invoke()
            wait_for(lambda: page.task is None, stopped)
        wait_for(lambda: heartbeat, responsive)

    def stopped():
        assert page.turns[-1]['status'] == 'stopped'
        assert page.turns[-1]['answer'] == 'Hello '
        fixture.mode = 'eof'
        fixture.gate.set()
        page.prompt.insert('1.0', 'Broken response')
        page.send_button.invoke()
        wait_for(lambda: page.task is None, failed)

    def failed():
        assert page.turns[-1]['status'] == 'failed'
        assert page.turns[-1]['answer'] == 'Hello '
        assert 'ended before' in page.status.cget('text')
        # Failed and cancelled partial responses never enter later model context.
        fixture.mode = 'ok'
        page.prompt.insert('1.0', 'Try again')
        page.send_button.invoke()
        wait_for(lambda: page.task is None, retried)

    def retried():
        assert page.turns[-1]['status'] == 'completed'
        sent = fixture.requests[-1][2]['messages']
        assert [m['content'] for m in sent if m['role']=='user'] == ['What is a limit?', 'Try again']
        endpoint('http://127.0.0.1:1')
        before = len(fixture.requests)
        page.connect_button.invoke()
        assert page.task is None and 'new chat' in page.status.cget('text')
        assert len(fixture.requests) == before
        # First click asks; invalid Send cancels the destructive confirmation.
        page.new_chat()
        assert page.pending_clear
        page.send()
        assert not page.pending_clear
        page.new_chat()
        page.new_chat()
        assert page.turns == []
        endpoint(fixture.url)
        fixture.model_names = []
        page.connect()
        wait_for(lambda: page.task is None, no_models)

    def no_models():
        assert page.models == [] and page.send_button.cget('state') == 'disabled'
        assert 'no models' in page.status.cget('text')
        fixture.model_names = [chr(0xd800)]
        page.connect()
        wait_for(lambda: page.task is None, malformed_models)

    def malformed_models():
        assert 'invalid' in page.status.cget('text')
        assert page.connect_button.cget('state') == 'normal'
        fixture.model_names = ['study-model:latest']
        fixture.models_payload = {'error': chr(0xd800)}
        fixture.status = 500
        page.connect()
        wait_for(lambda: page.task is None, unavailable)

    def unavailable():
        assert 'HTTP 500' in page.status.cget('text')
        assert page.send_button.cget('state') == 'disabled'
        fixture.status = 200
        fixture.models_payload = None
        fixture.mode = 'ok'
        page.connect()
        wait_for(lambda: page.task is None, malformed_answer)

    def malformed_answer():
        fixture.mode = 'surrogate'
        page.prompt.insert('1.0', 'Bad Unicode response')
        page.send()
        wait_for(lambda: page.task is None, unicode_recovered)

    def unicode_recovered():
        assert page.turns[-1]['status'] == 'failed'
        assert page.turns[-1]['answer'] == ''
        assert page.send_button.cget('state') == 'normal'
        close_during_stream()

    def close_during_stream():
        fixture.mode = 'slow'
        fixture.gate.clear()
        page.prompt.insert('1.0', 'Close during this answer')
        page.send()
        wait_for(lambda: page.turns[-1]['answer'] == 'Hello ', closing)

    def closing():
        assert app.store.seconds() == 0
        assert app.store.db.execute('PRAGMA user_version').fetchone()[0] == 5
        task = page.task
        app.close()
        task.thread.join(2)
        assert not task.thread.is_alive()

    def callback_error(kind, value, tb):
        errors.append(str(value))
        traceback.print_exception(kind,value,tb)
        app.destroy()

    def timeout():
        errors.append('AI Tutor native check timed out')
        app.destroy()

    app.report_callback_exception = callback_error
    app.after(900, guarded(initial))
    app.after(20000, timeout)
    try:
        app.mainloop()
    finally:
        app.store.close()
        fixture.close()
    assert not errors, errors


if __name__ == '__main__':
    ctk.set_appearance_mode('dark')
    with tempfile.TemporaryDirectory() as directory:
        check(Path(directory)/'tutor.sqlite3')
    print('PASS: explicit connection, model/error states, streamed UTF-8, Stop, responsive navigation, retry/context isolation, compact layout, clear confirmation and close during generation', flush=True)
