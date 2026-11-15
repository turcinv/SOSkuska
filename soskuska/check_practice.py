"""Native practice workflow with disposable content; never uses normal user data."""
import argparse
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from storage import Store


def run_check(path, resume=False):
    app = Dashboard(path)
    page = app.practice_page
    errors = []

    def guarded(callback):
        def run():
            try:
                callback()
            except Exception as exc:
                errors.append(str(exc))
                traceback.print_exc()
                app.destroy()
        return run

    def later(callback):
        app.after(250, guarded(callback))

    def initial():
        app.geometry("1024x700")
        app.navigate("Practice Tests")
        assert page.start_button.cget("state") == "disabled"
        assert not app.store.practice_history()
        sid = app.store.create_subject("Математика – skúška")
        tid = app.store.create_topic(sid, "Algebra")
        for index in range(3):
            app.store.create_question(sid, f"Question {index}?", ["one", "two", "three", "four"], index,
                                      "Easy" if index < 2 else "Hard", tid, f"Explanation {index}")
        other = app.store.create_subject("Physics")
        app.store.create_question(other, "Second subject?", ["a", "b", "c", "d"], 2)
        app.refresh_data()
        page.show_config()
        page.subject.set("Математика – skúška")
        page.subject_changed()
        page.topic.set("Topic: Algebra")
        page.difficulty.set("Easy")
        page.update_available()
        assert page.available.cget("text").startswith("2 matching")
        page.count.set("2")
        page.start_button.invoke()
        later(answering)

    def answering():
        assert page.run.winfo_ismapped() and not page.results.winfo_ismapped()
        assert page.prompt.winfo_width() <= page.winfo_width()
        assert page.radios[-1].winfo_rootx() + page.radios[-1].winfo_width() <= app.winfo_rootx() + app.winfo_width()
        aid = page.active_id
        correct = page.items[0]["correct_option"]
        page.radios[correct].invoke()
        page.next_button.invoke()
        assert app.store.practice_attempt(aid)["current_index"] == 1
        with patch.object(app.store, "save_practice_answer", side_effect=sqlite3.OperationalError("disk full")):
            page.radios[3].invoke()
        assert page.choice.get() == -1
        assert app.store.practice_items(aid)[1]["selected_option"] is None
        app.navigate("Dashboard")
        app.navigate("Practice Tests")
        assert page.attempt["current_index"] == 1
        assert page.choice.get() == -1
        page.previous_button.invoke()
        assert page.choice.get() == correct
        page.clear_button.invoke()
        assert app.store.practice_attempt(aid)["answered"] == 0
        page.radios[correct].invoke()
        page.finish_button.invoke()
        assert "1 questions are unanswered" in page.confirm_text.cget("text")
        page.cancel_action()
        assert app.store.practice_attempt(aid)["status"] == "in_progress"
        page.finish_button.invoke()
        with patch.object(app.store, "complete_practice", side_effect=sqlite3.OperationalError("database is locked")):
            page.confirm_button.invoke()
        assert page.finishing and page.radios[0].cget("state") == "disabled"
        with patch.object(page, "after"):
            page.tick()
        assert app.store.active_practice() is None
        assert app.store.practice_history()[0]["correct"] == 1
        assert app.store.practice_history()[0]["answered"] == 1
        assert not page.finishing
        # Source edits/deletion must not rewrite the completed review.
        old_id = aid
        sid = app.store.practice_attempt(aid)["subject_id"]
        app.store.delete_subject(sid)
        page.view_result(old_id)
        assert app.store.practice_items(aid)[0]["prompt"].startswith("Question")
        assert app.store.practice_attempt(aid)["subject_name"] == "Математика – skúška"
        later(timed_test)

    def timed_test():
        assert page.results.winfo_ismapped()
        page.show_config()
        page.subject.set("Physics")
        page.subject_changed()
        page.difficulty.set("All difficulties")
        page.update_available()
        page.count.set("1")
        page.limit.set("5 minutes")
        page.start_button.invoke()
        aid = page.active_id
        correct = page.items[0]["correct_option"]
        page.radios[correct].invoke()
        deadline = datetime.fromisoformat(page.attempt["deadline_at"])
        future = deadline + timedelta(seconds=1)
        with patch("practice_page.utc_now", return_value=future), patch("storage.utc_now", return_value=future), patch.object(page, "after"):
            with patch.object(app.store, "complete_practice", side_effect=sqlite3.OperationalError("disk full")):
                page.tick()
            assert page.finishing and app.store.active_practice()["answered"] == 1
            assert page.next_button.cget("state") == "disabled"
            page.tick()
        result = app.store.practice_attempt(aid)
        assert result["status"] == "completed" and result["correct"] == 1
        assert result["completed_at"] == deadline.isoformat()
        later(background_completion)

    def background_completion():
        page.show_config()
        page.start_button.invoke()
        page.radios[page.items[0]["correct_option"]].invoke()
        aid = page.active_id
        future = datetime.fromisoformat(page.attempt["deadline_at"]) + timedelta(seconds=1)
        subject = page.attempt["subject_id"]
        for index in range(8):
            app.store.create_question(subject, f"Long bank question {index}: " + "context " * 30, ["a", "b", "c", "d"], 0)
        app.open_question_bank(subject)
        app.question_bank.show_question_form()
        app.question_bank.prompt_entry.insert("1.0", "Unfinished authoring draft")
        app.update_idletasks()
        canvas = app.scroll._parent_canvas
        canvas.yview_moveto(0.5)
        before = canvas.yview()
        assert before[0] > 0
        with patch("practice_page.utc_now", return_value=future), patch("storage.utc_now", return_value=future), patch.object(page, "after"):
            page.tick()
        app.update_idletasks()
        assert app.current_page == "Question Bank" and not page.winfo_ismapped()
        assert canvas.yview() == before, (before, canvas.yview())
        assert app.question_bank.prompt_entry.get("1.0", "end-1c") == "Unfinished authoring draft"
        assert app.store.practice_attempt(aid)["status"] == "completed"
        # Leave an untimed attempt for a fresh process to resume.
        app.navigate("Practice Tests")
        page.show_config()
        page.limit.set("Untimed")
        page.start_button.invoke()
        page.radios[page.items[0]["correct_option"]].invoke()
        assert app.store.active_practice()["answered"] == 1
        app.close()

    def resumed():
        app.navigate("Practice Tests")
        assert page.active_id is not None
        assert page.choice.get() == page.items[0]["correct_option"]
        assert page.attempt["current_index"] == 0
        page.finish_button.invoke()
        page.confirm_button.invoke()
        assert app.store.active_practice() is None
        assert len(app.store.practice_history()) == 4
        assert app.store.practice_history()[0]["correct"] == 1
        assert app.store.seconds() == 0  # Practice results do not invent focus-session time.
        app.close()

    def callback_error(kind, value, tb):
        errors.append(str(value))
        traceback.print_exception(kind, value, tb)
        app.destroy()

    def timeout():
        errors.append("Practice UI check timed out")
        app.destroy()

    app.report_callback_exception = callback_error
    app.after(900, guarded(resumed if resume else initial))
    app.after(15000, timeout)
    try:
        app.mainloop()
    finally:
        app.store.close()
    assert not errors, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    ctk.set_appearance_mode("dark")
    if args.resume:
        run_check(args.resume, resume=True)
    else:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "practice.sqlite3"
            run_check(path)
            reopened = Store(path)
            try:
                assert reopened.active_practice()["answered"] == 1
                assert len(reopened.practice_history()) == 3
            finally:
                reopened.close()
            subprocess.run([sys.executable, "-u", str(Path(__file__).resolve()), "--resume", str(path)], check=True, timeout=25)
            print("PASS: practice setup/filtering, answer save/retry, navigation/resume, scoring, immutable history, timed completion/retry, compact layout, background completion without scroll/draft changes and fresh-process resume", flush=True)
