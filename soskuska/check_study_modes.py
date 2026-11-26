"""Mode consent and local history integration; disposable data and loopback only."""
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from localization import tr
from question_explanation import MODES, read_prompt
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from ollama_fixture import FakeOllama


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


def run(path):
    fixture = FakeOllama()
    app = Dashboard(path)
    page, tutor = app.practice_page, app.tutor_page
    errors = []
    app.report_callback_exception = lambda kind, value, tb: errors.append(value)

    def wait(predicate):
        if predicate():
            return
        done = ctk.BooleanVar(master=app, value=False)
        deadline = time.monotonic()+6
        def poll():
            if predicate() or time.monotonic() >= deadline:
                done.set(True)
            else:
                app.after(20, poll)
        app.after(20, poll)
        app.wait_variable(done)
        assert predicate() and not errors, errors

    def open_preview():
        app.navigate('Practice Tests')
        page.view_result(aid)
        # Exercise the actual second result-card closure, not only the page method.
        buttons = [w for w in descendants(page.results) if isinstance(w, ctk.CTkButton)
                   and w.cget('text') == tr(app, 'Explain this question')]
        assert len(buttons) == 2
        buttons[1].invoke()
        assert page.explanation_identity[:2] == (aid, 1)

    def select(mode):
        old_menu, old_panel, old_identity = page.explanation_mode_menu, page.explanation_panel, page.explanation_identity
        variable = old_menu.canonical
        old_menu.selected(tr(app, mode))
        assert not variable.trace_info(), 'destroyed menu retained canonical trace'
        identity = page.explanation_identity
        assert identity is not old_identity and identity[3] == mode
        page.prepare_explanation(old_identity)
        page.change_explanation_mode(old_panel, aid, 1, 'Explain answer')
        assert page.explanation_identity is identity and app.current_page == 'Practice Tests'
        return identity

    try:
        sid = app.store.create_subject('Study modes')
        app.store.create_question(sid, 'First saved question?', ['a', 'b', 'c', 'd'], 0, explanation='SECRET_FIRST_EXPLANATION')
        app.store.create_question(sid, 'Second saved question? Язык', ['one', 'two', 'three', 'four'],
                                  2, explanation='SECRET_EXPLANATION_SOURCE')
        aid = app.store.start_practice(sid, 2)
        app.store.save_practice_answer(aid, 1, 0)
        app.store.complete_practice(aid)
        items = app.store.practice_items(aid)
        # The store randomizes question order; snapshot position is the UI identity.
        app.store.delete_subject(sid)
        before = app.store.practice_attempt(aid), app.store.practice_items(aid)
        app.update()
        open_preview()
        for mode in MODES[1:]:
            identity = select(mode)
            assert identity[2] == read_prompt(app.store, aid, 1, mode=mode)
            if mode == 'Give me a hint':
                assert 'Stored correct answer:' not in identity[2]
                assert 'Stored explanation:' not in identity[2]
                assert 'Student answer:' not in identity[2]
                assert items[1]['explanation'] not in identity[2]
            tutor.prompt.insert('1.0', 'keep this exact draft')
            page.prepare_explanation(identity)
            assert app.current_page == 'Practice Tests'
            assert tutor.prompt.get('1.0', 'end-1c') == 'keep this exact draft'
            tutor.prompt.delete('1.0', 'end')
        assert fixture.requests == [] and tutor.conversation_id is None
        # Failed regeneration cannot leave a prior Prepare consent valid.
        expired = page.explanation_identity
        with patch.object(app.store, 'practice_items', side_effect=sqlite3.OperationalError('locked')):
            page.explanation_mode_menu.selected(tr(app, 'Give me a hint'))
        assert page.explanation_identity is None
        page.prepare_explanation(expired)
        assert app.current_page == 'Practice Tests'
        identity = select('Explain simply')
        # Switching modes must never connect; connection is still explicit.
        tutor.endpoint.delete(0, 'end')
        tutor.endpoint.insert(0, fixture.url)
        page.prepare_explanation(identity)
        assert fixture.requests == [] and app.current_page == 'AI Tutor'
        tutor.connect()
        wait(lambda: tutor.task is None)
        assert len(fixture.requests) == 1
        for index, mode in enumerate(MODES[1:]):
            if index:
                tutor.new_chat()
                tutor.new_chat()
                open_preview()
                identity = select(mode)
                page.prepare_explanation(identity)
            expected = identity[2]
            tutor.language.set('Russian')
            tutor.send()
            wait(lambda: tutor.task is None)
            sent = fixture.requests[-1][2]['messages']
            assert sent[-1]['content'] == expected
            assert 'Reply in Russian' in sent[0]['content']
            saved = app.store.tutor_conversation(tutor.conversation_id)
            assert len(saved['turns']) == 1 and saved['turns'][0]['prompt'] == expected
            assert f'Study mode: {mode}' in saved['turns'][0]['prompt']
            if mode == 'Quiz me':
                tutor.prompt.insert('1.0', 'My answer to the follow-up')
                tutor.send()
                wait(lambda: tutor.task is None)
                messages = fixture.requests[-1][2]['messages']
                assert messages[1]['content'] == expected
                assert messages[-1]['content'] == 'My answer to the follow-up'
                assert len(app.store.tutor_conversation(tutor.conversation_id)['turns']) == 2
        assert before == (app.store.practice_attempt(aid), app.store.practice_items(aid))
        app.navigate('Dashboard')
        previous = page.explanation_panel
        page.change_explanation_mode(previous, aid, 1, 'Give me a hint')
        assert page.explanation_panel is previous
        assert not errors, errors
    finally:
        tutor.shutdown()
        app.destroy()
        app.store.close()
        fixture.close()


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as directory:
        run(Path(directory)/'study.sqlite3')
    print('PASS: actual result action, mode consent/trace cleanup, hint payload, dirty drafts, read retry, explicit requests, saved modes and quiz continuation')
