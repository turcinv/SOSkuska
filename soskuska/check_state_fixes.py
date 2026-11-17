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
        assert page.subject.get() == "Biology"
        assert page.name_entry.get() == "My saved draft"
        assert page.description.get("1.0", "end-1c") == "Keep this description"
        other = Store(path)
        try:
            other.update_subject(sid, "Biology renamed")
            page.refresh()
            assert page.subject.get() == "Biology renamed"
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
            page.subject_menu.set("Physics")
            page.save_button.invoke()
            deck = app.store.decks()[0]
            assert deck["subject_id"] == physics
            assert deck["name"] == "My saved draft"
            assert deck["description"] == "Keep this description"
            return physics
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

    def initial():
        sid = deck_draft()
        question_conflict(sid)
        expired_discard(sid)
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
    print("PASS: subject refresh without draft loss, rename/delete identity, failed-read retry, stale question conflict/reload and expired-discard retained result", flush=True)
