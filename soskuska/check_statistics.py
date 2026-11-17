"""Native Statistics integration check; disposable database and process reopen."""
import argparse
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard


def texts(widget):
    result = []
    for child in widget.winfo_children():
        if isinstance(child, ctk.CTkLabel):
            result.append(child.cget("text"))
        result.extend(texts(child))
    return result


def run_check(path, reopen=False):
    app = Dashboard(path)
    page = app.statistics_page
    errors = []
    today = date.today()
    noon = datetime.combine(today, time(12)).astimezone(timezone.utc)

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

    def choose(period):
        page.period.set(period)
        page.period_picker.cget("command")(period)

    def initial():
        app.navigate("Statistics")
        app.update_idletasks()
        assert app.current_page == "Statistics" and page.winfo_ismapped()
        assert page.report["focus_seconds"] == page.report["reviews"] == 0
        assert "No completed tests" in texts(page.body)
        assert len(page.daily_bars) == 7
        sid = app.store.create_subject("Математика — " + "dlhý názov " * 9)
        app.store.add_session(75, sid)
        with app.store.db:
            app.store.db.execute("INSERT INTO sessions(day,seconds,subject_id,subject_name) VALUES (?,?,?,?)",
                                 ((today - timedelta(days=10)).isoformat(), 125, sid, "Математика"))
        qid = app.store.create_question(sid, "Result?", ["one", "two", "three", "four"], 0)
        with patch("storage.utc_now", return_value=noon):
            aid = app.store.start_practice(sid, 1)
            app.store.save_practice_answer(aid, 0, 0)
            app.store.complete_practice(aid)
            did = app.store.create_deck(sid, "Review deck")
            cid = app.store.create_flashcard(did, "Question?", "Answer")
            app.store.rate_flashcard(cid, "Good", 0)
        page.refresh_button.invoke()
        assert page.report["focus_seconds"] == 75
        assert page.report["practice_accuracy"] == 100
        assert page.report["reviews"] == 1
        choose("Last 30 days")
        assert page.report["focus_seconds"] == 200
        assert len(page.daily_bars) == 30
        choose("All time")
        assert page.report["focus_seconds"] == 200
        assert page.report["start_day"] is None
        old = page.report
        with patch.object(app.store, "statistics", side_effect=sqlite3.OperationalError("locked")):
            page.refresh_button.invoke()
        assert page.report is old and "Could not refresh" in page.status.cget("text")
        page.refresh_button.invoke()
        assert "Could not refresh" not in page.status.cget("text")
        # Saved snapshots remain after deleting their source content.
        app.store.delete_subject(sid)
        page.refresh_button.invoke()
        assert page.report["focus_seconds"] == 200
        assert page.report["practice_correct"] == 1 and page.report["reviews"] == 1
        assert page.report["focus_by_subject"][0]["subject_id"] is None
        app.query.set("dashboard draft")
        app.focus_search()
        app.clear_search()
        assert app.query.get() == "dashboard draft"
        app.navigate("Dashboard")
        app.update_idletasks()
        assert not page.winfo_ismapped()
        app.navigate("Statistics")
        app.update_idletasks()
        assert page.period.get() == "All time"
        app.geometry("1024x700")
        later(compact)

    def compact():
        assert page.winfo_ismapped()
        right = app.winfo_rootx() + app.winfo_width()
        assert page.period_picker.winfo_rootx() + page.period_picker.winfo_width() <= right
        assert page.refresh_button.winfo_rootx() + page.refresh_button.winfo_width() <= right
        assert all(bar.winfo_rootx() + bar.winfo_width() <= right for bar in page.daily_bars + page.subject_bars)
        assert "subject deleted / unavailable" in " ".join(texts(page.body))
        app.scroll.scroll_to_top()
        # Long reports remain reachable through the shared scroll container.
        app.scroll.event_generate("<MouseWheel>", delta=-1200)
        later(scrolled)

    def scrolled():
        assert app.scroll._parent_canvas.yview()[0] > 0
        app.navigate("My Subjects")
        sid = app.store.create_subject("Draft subject")
        app.open_question_bank(sid)
        app.update_idletasks()
        assert not page.winfo_ismapped()
        app.question_bank.query.set("keep search")
        app.navigate("Statistics")
        app.update_idletasks()
        app.focus_search()
        app.clear_search()
        assert app.question_bank.query.get() == "keep search"
        # Opening Statistics does not count tests/reviews as timer sessions.
        assert app.store.seconds() == 200
        app.close()

    def resumed():
        app.navigate("Statistics")
        app.update_idletasks()
        choose("All time")
        assert page.report["focus_seconds"] == 200
        assert page.report["practice_completed"] == 1
        assert page.report["practice_accuracy"] == 100
        assert page.report["reviews"] == 1
        assert len(page.daily_bars) == 30
        app.close()

    def callback_error(kind, value, tb):
        errors.append(str(value))
        traceback.print_exception(kind, value, tb)
        app.destroy()

    def timeout():
        errors.append("Statistics check timed out")
        app.destroy()

    app.report_callback_exception = callback_error
    app.after(900, guarded(resumed if reopen else initial))
    app.after(20000, timeout)
    try:
        app.mainloop()
    finally:
        app.store.close()
    assert not errors, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reopen", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    ctk.set_appearance_mode("dark")
    if args.reopen:
        run_check(args.reopen, reopen=True)
    else:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "statistics.sqlite3"
            run_check(path)
            subprocess.run([sys.executable, "-u", str(Path(__file__).resolve()), "--reopen", str(path)], check=True, timeout=30)
            print("PASS: empty state, all period controls, weighted results, saved ratings, failure/retry, retained history, navigation/search isolation, compact layout, scrolling and process reopen", flush=True)
