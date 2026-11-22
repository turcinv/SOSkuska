"""Native regressions for reviewed stale forms and practice state; temporary data."""
import sqlite3
import sys
import tempfile
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from storage import Store

NOW = datetime(2026, 11, 17, 12, tzinfo=timezone.utc)


def run_check(path):
    app = Dashboard(path)
    errors = []

    def deck_draft():
        app.navigate("Flashcards")
        page = app.flashcard_page
        page.deck_form()
        page.name_entry.insert(0, "My saved draft")
        page.description.insert("1.0", "Keep this description")
        app.navigate("My Subjects")
        app.subject_page.show_form()
        app.subject_page.name_entry.insert(0, "Biology")
        app.subject_page.save_subject()
        sid = app.store.subjects()[0]["id"]
        app.navigate("Flashcards")
        assert page.subject.get() == "Subject: Biology"
        assert page.name_entry.get() == "My saved draft"
        assert page.description.get("1.0", "end-1c") == "Keep this description"
        other = Store(path)
        try:
            other.update_subject(sid, "Biology renamed")
            page.refresh()
            assert page.subject.get() == "Subject: Biology renamed"
            with patch.object(app.store, "subjects", side_effect=sqlite3.OperationalError("locked")):
                page.refresh()
            assert page.view == "deck_form" and page.name_entry.get() == "My saved draft"
            assert "retry" in page.status.cget("text")
            physics = other.create_subject("Physics")
            other.delete_subject(sid)
            page.refresh()
            assert page.subject.get() == "Choose a subject"
            page.save_button.invoke()
            assert app.store.decks() == [] and page.name_entry.get() == "My saved draft"
            page.select_deck_subject("Subject: Physics")
            page.save_button.invoke()
            deck = app.store.decks()[0]
            assert deck["subject_id"] == physics
            assert deck["name"] == "My saved draft"
            assert deck["description"] == "Keep this description"
            # Losing the selection through an empty list must not auto-select
            # a later subject, even when its name matches a placeholder.
            page.deck_form()
            page.name_entry.insert(0, "No silent replacement")
            other.delete_subject(physics)
            page.refresh()
            assert page.subject.get() == "Add a subject first"
            replacement = other.create_subject("Choose a subject")
            page.save_button.invoke()
            assert len(app.store.decks()) == 1
            assert page.subject_choice_id is None and page.subject_requires_choice
            page.select_deck_subject("Subject: Choose a subject")
            page.save_button.invoke()
            assert len(app.store.decks()) == 2
            assert next(d for d in app.store.decks() if d["name"] == "No silent replacement")["subject_id"] == replacement
            # The other placeholder is also a valid, unambiguous real name.
            page.deck_form()
            page.name_entry.insert(0, "Explicit subject choice")
            last = other.create_subject("Add a subject first")
            other.delete_subject(replacement)
            page.refresh()
            page.save_button.invoke()
            assert len(app.store.decks()) == 2 and page.subject_choice_id is None
            page.select_deck_subject("Subject: Add a subject first")
            page.save_button.invoke()
            assert next(d for d in app.store.decks() if d["name"] == "Explicit subject choice")["subject_id"] == last
            return last
        finally:
            other.close()

    def main_review_findings(other_sid):
        sid=app.store.create_subject('Reviewed subject','Original description','2026-12-20')
        other=Store(path)
        try:
            app.navigate('My Subjects');subjects=app.subject_page;subjects.show_form(sid)
            subjects.name_entry.delete(0,'end');subjects.name_entry.insert(0,'My rename')
            other.update_subject(sid,'Reviewed subject','New description','2026-12-21')
            subjects.save_button.invoke()
            assert subjects.editing_id==sid and subjects.form.winfo_manager()=='grid'
            assert subjects.name_entry.get()=='My rename'
            assert 'changed in another window' in subjects.form_error.cget('text')
            assert other.subject(sid)['description']=='New description'
            subjects.show_form(sid);subjects.name_entry.delete(0,'end');subjects.name_entry.insert(0,'Merged subject')
            subjects.save_button.invoke();assert other.subject(sid)['name']=='Merged subject'
            tid=app.store.create_topic(sid,'Original topic')
            qid=app.store.create_question(sid,'Original prompt',['a','b','c','d'],0,topic_id=tid)
            app.open_question_bank(sid);bank=app.question_bank;bank.show_question_form(qid)
            bank.prompt_entry.delete('1.0','end');bank.prompt_entry.insert('1.0','Draft prompt')
            bank.explanation_entry.insert('1.0','Keep explanation')
            bank.correct.set('C');bank.difficulty.set('Hard')
            bank.option_entries[0].delete(0,'end');bank.option_entries[0].insert(0,'Draft answer')
            bank.query.set('Draft')
            original_snapshot=dict(bank.question_snapshot)
            app.navigate('Settings');app.open_question_bank(sid)
            assert bank.editing_question_id==qid and bank.question_snapshot==original_snapshot
            assert bank.prompt_entry.get('1.0','end-1c')=='Draft prompt'
            assert bank.option_entries[0].get()=='Draft answer' and bank.correct.get()=='C' and bank.difficulty.get()=='Hard'
            assert bank.explanation_entry.get('1.0','end-1c')=='Keep explanation' and bank.query.get()=='Draft'
            with patch.object(app.store,'subject',side_effect=sqlite3.OperationalError('read')):
                app.open_question_bank(sid)
            assert bank.editing_question_id==qid and bank.prompt_entry.get('1.0','end-1c')=='Draft prompt'
            assert 'draft is kept' in bank.status.cget('text')
            app.open_question_bank(sid);assert bank.status.cget('text')==''
            bank.save_question();assert app.store.question(qid)['prompt']=='Draft prompt'
            # Draft topic choices retain their IDs across rename and cannot silently
            # turn unassigned if that selected topic is removed elsewhere.
            draft_topic=other.create_topic(sid,'Draft topic choice')
            bank.show_question_form(qid);bank.question_topic.set('Topic: Draft topic choice')
            other.update_topic(draft_topic,'Renamed draft topic')
            app.navigate('Dashboard');app.open_question_bank(sid)
            assert bank.question_topic.get()=='Topic: Renamed draft topic'
            other.delete_topic(draft_topic)
            app.navigate('Dashboard');app.open_question_bank(sid)
            assert bank.question_topic.get()=='Unavailable topic: Renamed draft topic'
            replacement=other.create_topic(sid,'Renamed draft topic')
            app.open_question_bank(sid)
            assert bank.form_topics['Topic: Renamed draft topic']==replacement
            assert bank.form_topics[bank.question_topic.get()]==draft_topic
            bank.save_question();assert bank.editing_question_id==qid
            assert 'selected topic no longer exists' in bank.question_error.cget('text')
            assert app.store.question(qid)['topic_id']==tid
            bank.question_topic.set('No topic');bank.save_question()
            assert app.store.question(qid)['topic_id'] is None
            bank.show_question_form()
            assert bank.unavailable_topic_id is None and not any(label.startswith('Unavailable topic: ') for label in bank.form_topics)
            bank.prompt_entry.insert('1.0','Unsaved new question')
            app.navigate('Dashboard');app.open_question_bank(sid)
            assert bank.editing_question_id is None and bank.question_form.winfo_manager()=='grid'
            assert bank.prompt_entry.get('1.0','end-1c')=='Unsaved new question'
            bank.question_topic.set('Topic: Original topic')
            app.open_question_bank(other_sid)
            assert bank.question_topic.get()=='No topic' and bank.unavailable_topic_id is None
            assert tid not in bank.form_topics.values()
            app.open_question_bank(sid);bank.show_topic_form(tid)
            bank.topic_entry.delete(0,'end');bank.topic_entry.insert(0,'Topic draft')
            app.navigate('Dashboard');app.open_question_bank(sid)
            assert bank.editing_topic_id==tid and bank.topic_entry.get()=='Topic draft'
            bank.hide_topic_form();bank.ask_delete('question',qid)
            other.update_question(qid,'Changed before deletion',['one','two','three','four'],1,topic_id=tid)
            bank.confirm_delete()
            assert app.store.question(qid) is not None and bank.pending_delete is not None
            assert 'changed' in bank.status.cget('text') and 'Changed before deletion' in bank.delete_text.cget('text')
            assert 'This record changed' in bank.delete_text.cget('text')
            with patch.object(app.store,'question',side_effect=sqlite3.OperationalError('read')):
                bank.confirm_delete()
            assert bank.pending_delete is not None and other.question(qid) is not None
            bank.confirm_delete();assert app.store.question(qid) is None
            qid=app.store.create_question(sid,'Retained question',['a','b','c','d'],0,topic_id=tid)
            bank.ask_delete('topic',tid);other.update_topic(tid,'Renamed topic')
            bank.confirm_delete();assert app.store.topic(tid) is not None
            assert 'Renamed topic' in bank.delete_text.cget('text')
            bank.confirm_delete();assert app.store.topic(tid) is None and app.store.question(qid)['topic_id'] is None
        finally:
            other.close()
            app.navigate('Dashboard');app.store.delete_subject(sid);app.refresh_data()

    def question_conflict(sid):
        qid = app.store.create_question(sid, "Original?", ["A", "B", "C", "D"], 0)
        app.open_question_bank(sid)
        bank = app.question_bank
        bank.show_question_form(qid)
        other = Store(path)
        try:
            other.update_question(qid, "Latest?", ["E", "F", "G", "H"], 1, explanation="New explanation")
        finally:
            other.close()
        bank.explanation_entry.insert("1.0", "My draft")
        bank.save_question()
        assert bank.editing_question_id == qid
        assert bank.explanation_entry.get("1.0", "end-1c") == "My draft"
        assert "changed in another window" in bank.question_error.cget("text")
        assert app.store.question(qid)["prompt"] == "Latest?"
        assert app.store.question(qid)["correct_option"] == 1
        bank.show_question_form(qid)
        assert bank.prompt_entry.get("1.0", "end-1c") == "Latest?"
        bank.explanation_entry.delete("1.0", "end")
        bank.explanation_entry.insert("1.0", "Merged explanation")
        bank.save_question()
        assert app.store.question(qid)["explanation"] == "Merged explanation"

    def expired_discard(sid):
        page = app.practice_page
        with patch("storage.utc_now", return_value=NOW), patch("practice_page.utc_now", return_value=NOW):
            aid = app.store.start_practice(sid, 1, minutes=5)
            app.navigate("Practice Tests")
            page.click_answer(1)
            page.ask_action("discard")
        after = NOW + timedelta(minutes=5, seconds=1)
        with patch("storage.utc_now", return_value=after), patch("practice_page.utc_now", return_value=after):
            page.confirm_action()
        result = app.store.practice_attempt(aid)
        assert result["status"] == "completed" and result["correct"] == 1
        assert len(app.store.practice_items(aid)) == 1
        assert page.active_id is None and not page.finishing
        assert "Result saved" in page.status.cget("text")
        assert len(app.store.practice_history()) == 1

    def missing_practice(sid):
        page = app.practice_page
        aid = app.store.start_practice(sid, 1)
        page.load()
        other = Store(path)
        try:
            other.discard_practice(aid)
        finally:
            other.close()
        page.ask_action("finish")
        with patch.object(app.store, "complete_practice", wraps=app.store.complete_practice) as complete:
            page.confirm_action()
            assert page.active_id is None and not page.finishing
            assert "discarded in another window" in page.status.cget("text")
            with patch.object(page, "after"):
                for _ in range(3):
                    page.tick()
            assert complete.call_count == 1
        app.navigate("Dashboard")
        app.navigate("Practice Tests")
        assert page.active_id is None and page.start_button.cget("state") == "normal"
        page.start_button.invoke()
        assert page.active_id is not None and not page.finishing
        # A failed setup read must not restart completion of a missing attempt.
        other = Store(path)
        try:
            other.discard_practice(page.active_id)
        finally:
            other.close()
        with patch.object(app.store, "subjects", side_effect=sqlite3.OperationalError("locked")):
            page.finish()
        assert page.active_id is None and not page.finishing
        assert page.start_button.cget("state") == "disabled"
        page.show_config()
        assert page.start_button.cget("state") == "normal"
        # Actual write failures still retain completion retry behavior.
        page.start_button.invoke()
        aid = page.active_id
        with patch.object(app.store, "complete_practice", side_effect=sqlite3.OperationalError("locked")):
            page.finish()
        assert page.active_id == aid and page.finishing
        page.finish()
        assert page.active_id is None and not page.finishing
        assert app.store.practice_attempt(aid)["status"] == "completed"

    def initial():
        sid = deck_draft()
        main_review_findings(sid)
        question_conflict(sid)
        expired_discard(sid)
        missing_practice(sid)
        app.close()

    def guarded():
        try:
            initial()
        except Exception as exc:
            errors.append(str(exc))
            traceback.print_exc()
            app.destroy()

    def callback_error(kind, value, tb):
        errors.append(str(value))
        traceback.print_exception(kind, value, tb)
        app.destroy()

    def timeout():
        errors.append("Reviewed state checks timed out")
        app.destroy()

    app.report_callback_exception = callback_error
    app.after(900, guarded)
    app.after(20000, timeout)
    try:
        app.mainloop()
    finally:
        app.store.close()
    assert not errors, errors


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    with tempfile.TemporaryDirectory() as folder:
        run_check(Path(folder) / "state.sqlite3")
    print("PASS: reviewed subject conflicts, stale question/topic delete reconfirmation, same-subject editor drafts and read retry; subject refresh without draft loss, rename/delete identity, failed-read retry, stale question conflict/reload and expired-discard retained result, missing-attempt recovery and transient-write retry", flush=True)
