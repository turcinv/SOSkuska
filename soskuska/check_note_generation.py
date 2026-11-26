"""GUI checks for AI flashcard/question drafting with a loopback fixture only.

Disposable database; no real model, download or cloud request.
"""
import argparse
import json
import sqlite3
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from preferences import DEFAULTS
from storage import Store
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from ollama_fixture import FakeOllama

CARDS = {'items': [{'front': 'What is FIFO?', 'back': 'First in, first out.'},
                   {'front': 'What is LIFO?', 'back': 'Last in, first out.'},
                   {'front': '', 'back': 'invalid'}]}
QUESTIONS = {'items': [{'question': 'Which structure is FIFO?', 'options': ['Queue', 'Stack', 'Tree', 'Graph'],
                        'correct': 'A', 'difficulty': 'Easy', 'explanation': 'Oldest first.', 'topic': 'Structures'}]}
NOTES = 'Queues are FIFO. Stacks are LIFO.'


def inside(widget, container):
    left, right = widget.winfo_rootx(), widget.winfo_rootx() + widget.winfo_width()
    assert container.winfo_rootx() <= left < right <= container.winfo_rootx() + container.winfo_width(), widget


def check(path, language):
    fixture = FakeOllama()
    setup = Store(path)
    try:
        setup.save_preferences(dict(DEFAULTS, ollama_endpoint=fixture.url, ollama_model='study-model:latest',
                                    ui_language=language), expected_revision=setup.preferences()['revision'])
        sid = setup.create_subject('Computer Science')
        deck = setup.create_deck(sid, 'Structures')
        other = setup.create_deck(sid, 'Other deck')
    finally:
        setup.close()
    app = Dashboard(path)
    errors = []
    store = app.store
    assert app.translator.language == language
    flash = app.flashcard_page
    gen = flash.generator

    def guarded(callback):
        def run():
            try:
                callback()
            except Exception as exc:
                errors.append(repr(exc)); traceback.print_exc(); fixture.close(); app.destroy()
        return run

    def wait_for(predicate, callback, seconds=8):
        deadline = time.monotonic() + seconds
        def poll():
            assert time.monotonic() < deadline, f'Timed out before {callback.__name__}'
            if predicate():
                callback()
            else:
                app.after(50, guarded(poll))
        app.after(50, guarded(poll))

    def open_deck():
        app.geometry('1024x700'); app.navigate('Flashcards'); flash.open_deck(deck); app.update_idletasks()
        assert fixture.requests == []  # Opening never connects.
        flash.generate_button.invoke(); app.update_idletasks()
        assert gen.winfo_ismapped() and gen.target_id == deck
        assert fixture.url in gen.server_label.cget('text')
        for button in (gen.generate_button, gen.stop_button, gen.close_button):
            inside(button, gen)
        assert fixture.requests == []
        gen.generate_button.invoke()
        assert gen.task is None and fixture.requests == []  # Empty notes never send.
        gen.notes.insert('1.0', NOTES)
        fixture.mode = 'content'; fixture.content = json.dumps(CARDS)
        gen.count.set('3')
        gen.generate_button.invoke()
        assert gen.busy and gen.generate_button.cget('state') == 'disabled'
        try:
            app.validate_preferences_change(dict(app.preferences, ollama_model='other'))
        except ValueError as exc:
            assert 'AI generation' in str(exc)
        else:
            raise AssertionError('AI preference change allowed during generation')
        app.navigate('Dashboard')  # Hidden completion must not move other pages.
        wait_for(lambda: not gen.busy, generated)

    def generated():
        payload = fixture.requests[-1][2]
        assert payload['format']['properties']['items']['maxItems'] == 3
        assert NOTES in payload['messages'][1]['content']
        assert gen.preview and len(gen.preview['rows']) == 2 and len(gen.choices) == 2
        assert gen.errors.get('1.0', 'end-1c').strip()  # The invalid third item is reported.
        app.navigate('Flashcards'); app.update_idletasks()
        assert gen.winfo_ismapped() and gen.preview is not None
        flash.search.delete(0, 'end'); flash.search.insert(0, 'FIFO'); flash.search_cards()
        assert gen.preview is not None, 'Search inside the same deck must keep drafts'
        gen.choices[1].set(False); gen.controls()
        assert gen.save_button.cget('state') == 'normal'
        with patch.object(store, 'import_flashcards', side_effect=sqlite3.OperationalError('locked')):
            gen.save_button.invoke()
        assert gen.preview is not None and len(store.flashcards(deck)) == 0
        gen.save_button.invoke()
        cards = store.flashcards(deck)
        assert [c['front'] for c in cards] == ['What is FIFO?'], cards
        assert gen.preview is None and gen.save_button.cget('state') == 'disabled'
        assert gen.winfo_ismapped() and gen.notes.get('1.0', 'end-1c') == NOTES
        # Regenerating identical drafts: an existing duplicate blocks the whole save.
        gen.generate_button.invoke()
        wait_for(lambda: not gen.busy, duplicates)

    def duplicates():
        gen.save_button.invoke()
        assert len(store.flashcards(deck)) == 1
        prefix = app.translator.text('Item {v0}: {v1}', v0=1, v1='').strip()
        assert prefix in gen.errors.get('1.0', 'end-1c') and gen.preview is not None, gen.errors.get('1.0', 'end-1c')
        # Another deck discards drafts for this one, with a visible notice.
        flash.open_deck(other); app.update_idletasks()
        assert not gen.winfo_ismapped() and gen.preview is None and gen.target_id is None
        assert flash.status.cget('text') == app.translator.text('AI generation was closed; its unsaved drafts were discarded. Your notes are kept.')
        flash.open_deck(deck); flash.generate_button.invoke()
        fixture.mode = 'slow'; gen.generate_button.invoke()
        assert gen.busy
        gen.stop_button.invoke()
        wait_for(lambda: not gen.busy, stopped)

    def stopped():
        assert gen.preview is None
        if language == 'English':
            assert 'stopped' in gen.status.cget('text').lower(), gen.status.cget('text')
        fixture.mode = 'malformed'; gen.generate_button.invoke()
        wait_for(lambda: not gen.busy, malformed)

    def malformed():
        assert gen.preview is None and gen.status.cget('text')
        questions()

    def questions():
        bank = app.question_bank
        app.open_question_bank(sid); app.update_idletasks()
        bank.generate_button.invoke(); app.update_idletasks()
        qgen = bank.generator
        assert qgen.winfo_ismapped() and qgen.target_id == sid
        qgen.notes.insert('1.0', NOTES)
        fixture.mode = 'content'; fixture.content = json.dumps(QUESTIONS)
        qgen.generate_button.invoke()
        wait_for(lambda: not qgen.busy, lambda: question_saved(qgen))

    def question_saved(qgen):
        assert qgen.preview and len(qgen.preview['rows']) == 1
        # Renaming the subject elsewhere, then reopening its bank, follows the new name.
        current = store.subject(sid)
        store.update_subject(sid, 'Computer Science II', current['description'], current['exam_date'] or '', expected_state=dict(current))
        app.open_question_bank(sid); app.update_idletasks()
        assert qgen.preview is not None and qgen.request['target']['name'] == 'Computer Science II'
        qgen.save_button.invoke()
        saved_questions = store.questions(sid)
        assert len(saved_questions) == 1 and saved_questions[0]['correct_option'] == 0
        assert [t['name'] for t in store.topics(sid)] == ['Structures']
        # Close during a request cancels it without joining the worker.
        fixture.mode = 'slow'; qgen.generate_button.invoke()
        assert qgen.busy
        app.close()

    app.after(300, guarded(open_deck))
    app.mainloop()
    fixture.close()
    assert not errors, errors
    print(f'PASS: AI note generation ({language})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language')
    parser.add_argument('--data', type=Path)
    args = parser.parse_args()
    if args.language:
        check(args.data, args.language)
    else:
        with tempfile.TemporaryDirectory() as folder:
            for language in ('English', 'Russian'):
                subprocess.run([sys.executable, '-X', 'faulthandler', '-u', str(Path(__file__).resolve()),
                                '--language', language, '--data', str(Path(folder) / f'{language}.sqlite3')],
                               check=True, timeout=25)
        print('PASS: AI flashcard/question drafting from notes, review, atomic save and cancellation')
