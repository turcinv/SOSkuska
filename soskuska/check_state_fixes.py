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
    print("PASS: subject refresh without draft loss, rename/delete identity, failed-read retry, stale question conflict/reload and expired-discard retained result, missing-attempt recovery and transient-write retry", flush=True)
