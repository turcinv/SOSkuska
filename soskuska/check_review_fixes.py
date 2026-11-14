"""Native regression checks for the full-main review; only disposable data."""
import argparse
import sqlite3
import subprocess
import sys
import tempfile
import tkinter
import traceback
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from storage import Store


def check_workflows(path):
    app = Dashboard(path)
    errors = []
    page = app.subject_page
    bank = app.question_bank
    sid = app.store.create_subject("Calculus")
    timer_subject = app.store.create_subject("Physics")

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

    def authoring():
        app.geometry("1024x700")
        app.navigate("My Subjects")
        page.ask_delete(sid)
        assert page.deleting_id == sid
        app.open_question_bank(sid)
        assert page.deleting_id is None
        bank.show_question_form()
        bank.prompt_entry.insert("1.0", "Derivative of x?")
        for entry, answer in zip(bank.option_entries, ["0", "1", "x", "2x"]):
            entry.insert(0, answer)
        bank.correct.set("B")
        bank.save_question_button.invoke()
        assert len(app.store.questions(sid)) == 1
        app.navigate("My Subjects")
        assert not page.delete_panel.winfo_ismapped()
        page.delete_button.invoke()  # The old confirmation must be inert.
        assert app.store.subject(sid)
        page.ask_delete(sid)
        # Another connection changes the content after the warning is displayed.
        other = Store(path)
        try:
            other.create_topic(sid, "Limits")
        finally:
            other.close()
        page.delete_button.invoke()
        assert app.store.subject(sid)
        assert "1 topics and 1 questions" in page.delete_label.cget("text")
        assert "changed" in page.status.cget("text")
        app.navigate("Dashboard")
        assert page.deleting_id is None
        later(midnight)

    def midnight():
        app.store.set_task("review_subject", True)
        app.task_vars["review_subject"].set(True)
        app.start_focus(timer_subject)
        app.running_since -= 180
        today = date.today()
        tomorrow = today + timedelta(days=1)
        old_header = app.date_label.cget("text")
        blocker = sqlite3.connect(path)
        app.store.db.execute("PRAGMA busy_timeout=30")
        try:
            blocker.execute("BEGIN EXCLUSIVE")
            with patch("app.date", wraps=date) as app_date, patch("storage.date", wraps=date) as storage_date, patch.object(app, "after") as after:
                app_date.today.return_value = tomorrow
                storage_date.today.return_value = tomorrow
                app.tick()
                after.assert_called_once_with(250, app.tick)
                assert app.active_day == today
                assert app.date_label.cget("text") == old_header
                assert app.task_vars["review_subject"].get()
                assert app.session_open and app.running_since is not None
        finally:
            blocker.rollback()
            blocker.close()
            app.store.db.execute("PRAGMA busy_timeout=5000")
        with patch("app.date", wraps=date) as app_date, patch("storage.date", wraps=date) as storage_date, patch.object(app, "after") as after:
            app_date.today.return_value = tomorrow
            storage_date.today.return_value = tomorrow
            app.tick()
            after.assert_called_once_with(250, app.tick)
            assert app.active_day == tomorrow
            assert app.date_label.cget("text") == tomorrow.strftime("%A, %B %d, %Y")
            assert not app.task_vars["review_subject"].get()
        # The recovered scheduler must still complete and persist a focus session.
        app.running_since -= 901
        with patch.object(app, "after") as after:
            app.tick()
            after.assert_called_once_with(250, app.tick)
        assert not app.session_open and app.store.seconds() == 900
        later(failed_save_at_midnight)

    def failed_save_at_midnight():
        app.start_focus(timer_subject)
        app.running_since -= 901
        today = date.today()
        tomorrow = today + timedelta(days=1)
        blocker = sqlite3.connect(path)
        app.store.db.execute("PRAGMA busy_timeout=30")
        try:
            blocker.execute("BEGIN EXCLUSIVE")
            with patch("app.date", wraps=date) as app_date, patch("storage.date", wraps=date) as storage_date, patch.object(app, "after") as after:
                app_date.today.return_value = tomorrow
                storage_date.today.return_value = tomorrow
                app.tick()
                after.assert_called_once_with(250, app.tick)
                assert app.session_open and app.running_since is None
                assert "Press Finish" in app.notice.cget("text")
                assert "automatically" not in app.notice.cget("text")
        finally:
            blocker.rollback()
            blocker.close()
            app.store.db.execute("PRAGMA busy_timeout=5000")
        with patch("app.date", wraps=date) as app_date, patch("storage.date", wraps=date) as storage_date, patch.object(app, "after"):
            app_date.today.return_value = tomorrow
            storage_date.today.return_value = tomorrow
            app.tick()
            app.tick()
            assert app.active_day == tomorrow and not app.refresh_pending
            assert app.session_open and app.store.seconds() == 900
            assert "Press Finish" in app.notice.cget("text")
            assert app.finish_focus()
            assert not app.session_save_failed and app.store.seconds() == 1800
        with patch.object(app, "after"):
            app.tick()  # Restore the real day after the simulated rollover.
        later(post_save_refresh)

    def post_save_refresh():
        app.start_focus(timer_subject)
        app.running_since -= 901
        blocker = sqlite3.connect(path)
        subjects = app.store.subjects
        app.store.db.execute("PRAGMA busy_timeout=30")

        def locked_subjects():
            if not blocker.in_transaction:
                blocker.execute("BEGIN EXCLUSIVE")
            return subjects()

        try:
            # The lock starts only after add_session and set_task committed.
            with patch.object(app.store, "subjects", side_effect=locked_subjects), patch.object(app, "after") as after:
                app.tick()
                after.assert_called_once_with(250, app.tick)
            assert not app.session_open and app.refresh_pending
            assert app.metric_values[1].cget("text") == "2"
            assert app.subject_picker.cget("state") == "disabled"
        finally:
            blocker.rollback()
            blocker.close()
            app.store.db.execute("PRAGMA busy_timeout=5000")
        assert app.store.seconds() == 2700
        with patch.object(app, "after"):
            app.tick()
            app.tick()
        assert not app.refresh_pending
        assert app.metric_values[1].cget("text") == "3"
        assert app.subject_picker.cget("state") == "normal"
        assert "Retrying" not in app.notice.cget("text")
        assert len(app.store.recent_sessions()) == 3  # Refresh retries never save twice.
        app.open_question_bank(sid)
        bank.show_question_form()
        bank.prompt_entry.insert("1.0", "\n".join(f"Question line {i}" for i in range(75)))
        later(long_text_scroll)

    def text_widget():
        return next(child for child in bank.prompt_entry.winfo_children() if isinstance(child, tkinter.Text))

    def long_text_scroll():
        text = text_widget()
        canvas = app.scroll._parent_canvas
        events = [("<MouseWheel>", -120)]
        if tkinter.TkVersion >= 9:
            events.append(("<TouchpadScroll>", -12 & 0xFFFF))
        elif app.tk.call("tk", "windowingsystem") == "x11":
            events.append(("<Button-5>", None))
        for event, delta in events:
            text.yview_moveto(0)
            canvas.yview_moveto(0)
            before = canvas.yview()
            text.event_generate(event, **({"delta": delta} if delta is not None else {}))
            assert text.yview()[0] > 0, (event, text.yview())
            assert canvas.yview() == before, (event, canvas.yview(), before)
            text.yview_moveto(1)
            canvas.yview_moveto(0)
            before = canvas.yview()
            text.event_generate(event, **({"delta": delta} if delta is not None else {}))
            assert canvas.yview() == before  # Contain gestures at editor boundaries too.
        if tkinter.TkVersion >= 9:
            # Exercise canvas surfaces without a native Text class binding.
            surfaces = [child for child in bank.prompt_entry.winfo_children()
                        if isinstance(child, tkinter.Canvas)]
            for child in bank.prompt_entry.winfo_children():
                if isinstance(child, ctk.CTkScrollbar):
                    surfaces.extend(w for w in child.winfo_children() if isinstance(w, tkinter.Canvas))
            assert len(surfaces) >= 2, surfaces
            for surface in surfaces:
                text.yview_moveto(0)
                canvas.yview_moveto(0)
                before = canvas.yview()
                surface.event_generate("<TouchpadScroll>", delta=-12 & 0xFFFF)
                assert text.yview()[0] > 0, (surface, text.yview())
                assert canvas.yview() == before, (surface, canvas.yview(), before)
                text.yview_moveto(1)
                surface.event_generate("<TouchpadScroll>", delta=-12 & 0xFFFF)
                assert canvas.yview() == before
        bank.prompt_entry.delete("1.0", "end")
        bank.prompt_entry.insert("1.0", "Short question")
        later(short_text_scroll)

    def short_text_scroll():
        canvas = app.scroll._parent_canvas
        canvas.yview_moveto(0)
        text_widget().event_generate("<MouseWheel>", delta=-120)
        assert canvas.yview()[0] > 0  # Short, non-scrolling editors still allow page scrolling.
        app.close()

    def callback_error(kind, value, tb):
        errors.append(str(value))
        traceback.print_exception(kind, value, tb)
        app.destroy()

    def timeout():
        errors.append("Regression workflow timed out")
        app.destroy()

    app.report_callback_exception = callback_error
    app.after(900, guarded(authoring))
    app.after(15000, timeout)
    try:
        app.mainloop()
    finally:
        app.store.close()
    assert not errors, errors
    print("PASS: stale deletion warnings, locked midnight retry, header rollover, timer recovery, unsaved-session instructions, same-day refresh retry and nested scrolling including editor canvas surfaces", flush=True)


def native_quit(app):
    """Invoke the actual Aqua application-menu action on Tk's main thread."""
    import ctypes
    from ctypes import c_char_p, c_long, c_void_p

    runtime = ctypes.CDLL("/usr/lib/libobjc.A.dylib")
    runtime.objc_getClass.argtypes = [c_char_p]
    runtime.objc_getClass.restype = c_void_p
    runtime.sel_registerName.argtypes = [c_char_p]
    runtime.sel_registerName.restype = c_void_p

    def message(obj, selector, result=c_void_p, argtypes=(), args=()):
        function = ctypes.CFUNCTYPE(result, c_void_p, c_void_p, *argtypes)(("objc_msgSend", runtime))
        return function(obj, runtime.sel_registerName(selector.encode()), *args)

    nsapp = message(runtime.objc_getClass(b"NSApplication"), "sharedApplication")
    main = message(nsapp, "mainMenu")
    apple = message(message(main, "itemAtIndex:", argtypes=(c_long,), args=(0,)), "submenu")
    for index in range(message(apple, "numberOfItems", c_long)):
        item = message(apple, "itemAtIndex:", argtypes=(c_long,), args=(index,))
        # Locate the command by its standard key equivalent, independent of locale.
        key = message(message(item, "keyEquivalent"), "UTF8String", c_char_p)
        if key == b"q":
            message(apple, "performActionForItemAtIndex:", None, (c_long,), (index,))
            return
    raise AssertionError("Native Quit menu item not found")


def check_quit_probe(path):
    app = Dashboard(path)
    errors = []
    sid = app.store.create_subject("Native Quit regression")
    app.start_focus(sid)
    app.running_since -= 180

    failed_save = patch.object(app.store, "add_session", side_effect=sqlite3.OperationalError("disk full"))

    def attempt_quit():
        failed_save.start()
        native_quit(app)
        # AppKit queues the Tcl Quit command; let Tk dispatch it before checking.
        app.after(250, check_failed_quit)

    def check_failed_quit():
        try:
            assert app.winfo_exists() and app.session_open
            assert app.running_since is None and app.store.seconds() == 0
            assert app.elapsed() >= 180
            failed_save.stop()
            app.after(250, native_quit, app)
        except Exception as exc:
            errors.append(str(exc))
            traceback.print_exc()
            app.destroy()

    def callback_error(kind, value, tb):
        errors.append(str(value))
        traceback.print_exception(kind, value, tb)
        app.destroy()

    def timeout():
        errors.append("Native Quit probe timed out")
        app.destroy()

    app.report_callback_exception = callback_error
    app.after(700, attempt_quit)
    app.after(10000, timeout)
    try:
        app.mainloop()
    finally:
        failed_save.stop()
        app.store.close()
    assert not errors, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quit-probe", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    ctk.set_appearance_mode("dark")
    if args.quit_probe:
        check_quit_probe(args.quit_probe)
    else:
        with tempfile.TemporaryDirectory() as directory:
            check_workflows(Path(directory) / "workflows.sqlite3")
            if sys.platform == "darwin":
                path = Path(directory) / "quit.sqlite3"
                subprocess.run([sys.executable, "-u", str(Path(__file__).resolve()), "--quit-probe", str(path)], check=True, timeout=20)
                reopened = Store(path)
                try:
                    assert len(reopened.recent_sessions()) == 1
                    assert 180 <= reopened.seconds() < 185
                finally:
                    reopened.close()
                print("PASS: native macOS Quit retains failed saves and persists the session on retry", flush=True)
            else:
                print("SKIP: native macOS Quit is only checked on macOS", flush=True)
