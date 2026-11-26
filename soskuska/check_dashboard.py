"""Native integration check with temporary data; never opens the user's DB."""
import tempfile
import traceback
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from storage import Store
from theme import COLORS as C

ctk.set_appearance_mode("dark")
temp = tempfile.TemporaryDirectory()
path = Path(temp.name) / "check.sqlite3"
print("Creating study workspace...", flush=True)
app = Dashboard(path)
errors = []
subject_id = None


def fail(exc):
    errors.append(str(exc))
    traceback.print_exc()
    app.destroy()


def guarded(callback):
    def run():
        try:
            callback()
        except Exception as exc:
            fail(exc)
    return run


def next_step(callback, delay=120):
    app.after(delay, guarded(callback))


def assert_inside(widget, container):
    app.update_idletasks()
    assert widget.winfo_rootx() >= container.winfo_rootx()
    assert widget.winfo_rootx() + widget.winfo_width() <= container.winfo_rootx() + container.winfo_width(), (widget, widget.winfo_width(), container.winfo_width())


def check_initial():
    assert app.title() == "SOSkúška"
    assert app.content.winfo_ismapped() and app.empty.winfo_ismapped()
    assert app.metric_values[0].cget("text") == "0h 00m"
    assert app.metric_values[3].cget("text") == "0"
    assert app.start_button.cget('text') == 'Create your first subject'
    assert app.subject_picker.cget('state') == 'disabled'
    assert_inside(app.start_button, app.study_panel)
    assert_inside(app.subject_picker, app.study_panel)
    assert app.metrics.winfo_rooty() < app.study_panel.winfo_rooty() < app.search.winfo_rooty()
    assert int(app.rail.grid_info()['column']) == 1
    app.navigate('Settings')
    assert app.settings_btn.cget('fg_color') == C['nav_selected']
    app.toggle_sidebar(); app.toggle_sidebar()
    assert app.settings_btn.cget('fg_color') == C['nav_selected']
    app.navigate('Dashboard')
    assert app.settings_btn.cget('fg_color') != C['nav_selected']
    app.start_button.invoke()
    next_step(check_form)


def check_form():
    assert app.current_page == "My Subjects"
    page = app.subject_page
    assert page.form.winfo_ismapped()
    page.save_button.invoke()
    assert page.form_error.cget("text")
    assert app.store.subjects() == []
    page.name_entry.insert(0, "Математика – skúška")
    page.description_entry.insert("1.0", "Derivatives and exam preparation")
    page.exam_entry.insert(0, (date.today() + timedelta(days=4)).isoformat())
    page.save_button.invoke()
    next_step(check_saved)


def check_saved():
    global subject_id
    subjects = app.store.subjects()
    assert len(subjects) == 1
    subject_id = subjects[0]["id"]
    page = app.subject_page
    page.show_form(subject_id)
    page.name_entry.delete(0, "end")
    page.name_entry.insert(0, "Mathematics – skúška")
    page.save_button.invoke()
    assert app.store.subject(subject_id)["name"] == "Mathematics – skúška"
    # Test fixtures are explicit test data, not automatic demo content.
    for name in ["Physics", "English", "Long subject " + "математика " * 9]:
        app.store.create_subject(name)
    app.refresh_data()
    page.query.set("physics")
    next_step(check_subject_search)


def check_subject_search():
    page = app.subject_page
    assert len(page.cards.winfo_children()) == 1
    page.query.set("")
    next_step(check_wide_subject_layout)


def check_wide_subject_layout():
    page = app.subject_page
    assert app.scroll.logical_pixels(page.winfo_width()) >= 950
    assert page.card_columns == 2
    positions = [(int(card.grid_info()["row"]), int(card.grid_info()["column"]))
                 for card in page.cards.winfo_children()]
    assert positions == [(0, 0), (0, 1), (1, 0), (1, 1)], positions
    app.geometry("1024x700")
    next_step(check_compact_subject_layout, 400)


def check_compact_subject_layout():
    page = app.subject_page
    assert app.scroll.logical_pixels(page.winfo_width()) < 950
    assert page.card_columns == 1
    assert [int(card.grid_info()["column"]) for card in page.cards.winfo_children()] == [0, 0, 0, 0]
    app.navigate("Dashboard")
    assert app.metric_values[3].cget("text") == "4"
    assert len(app.store.upcoming_exams()) == 1
    app.query.set("Physics")
    next_step(check_dashboard_search)


def check_dashboard_search():
    assert sum(card.winfo_ismapped() for _, card in app.subject_cards) == 1
    app.query.set("no matching subject")
    next_step(check_empty)


def check_empty():
    assert app.empty.winfo_ismapped()
    app.query.set("")
    app.toggle_sidebar()
    assert app.collapsed
    app.toggle_sidebar()
    app.geometry("1024x700")
    next_step(check_compact, 400)


def check_compact():
    app.reflow()
    assert app.layout_mode == "compact"
    assert int(app.rail.grid_info()['row']) == 1 and int(app.rail.grid_info()['column']) == 0
    assert all(int(card.grid_info()['column']) == 0 for _, card in app.subject_cards)
    assert_inside(app.search, app.main)
    assert_inside(app.manage_subjects_button, app.main)
    assert_inside(app.start_button, app.study_panel)
    assert_inside(app.subject_picker, app.study_panel)
    app.query.set('Physics')
    app.toggle_sidebar(); app.toggle_sidebar()
    assert app.query.get() == 'Physics' and len(app.subject_cards) == 1
    app.query.set('')
    canvas = app.scroll._parent_canvas
    canvas.yview_moveto(0)
    before = canvas.yview()[0]
    app.start_button.event_generate("<MouseWheel>", delta=-120)
    after_wheel = canvas.yview()[0]
    assert before < after_wheel < 0.2
    if int(app.tk.call("package", "provide", "Tk").split(".")[0]) >= 9:
        app.start_button.event_generate("<TouchpadScroll>", delta=(-12 & 0xFFFF))
        after_touch = canvas.yview()[0]
        assert after_touch > after_wheel
        app.start_button.event_generate("<TouchpadScroll>", delta=12)
        assert canvas.yview()[0] < after_touch
        position = canvas.yview()[0]
        app.start_button.event_generate("<TouchpadScroll>", delta=(12 << 16))
        assert canvas.yview()[0] == position
        app.sidebar.event_generate("<TouchpadScroll>", delta=(-12 & 0xFFFF))
        assert canvas.yview()[0] == position
    app.start_focus(subject_id)
    app.subject_page.ask_delete(subject_id)
    assert app.subject_page.deleting_id is None
    assert app.store.subject(subject_id) is not None
    app.scroll._parent_canvas.yview_moveto(0)
    app.update_idletasks()
    assert app.finish_button.winfo_ismapped() and app.timer_frame.winfo_ismapped()
    assert_inside(app.finish_button, app.study_panel)
    assert app.finish_button.winfo_rooty() + app.finish_button.winfo_height() < app.winfo_rooty() + app.winfo_height()
    app.running_since -= 95
    app.pause_focus()
    assert app.running_since is None
    with patch.object(app.store, "add_session", side_effect=sqlite3.OperationalError("disk full")):
        assert not app.finish_focus()
    assert app.session_open and app.running_since is None
    assert app.focus_retry_label.winfo_ismapped() and app.focus_retry_label.cget('text')
    assert app.finish_button.winfo_ismapped()
    assert app.store.seconds() == 0
    assert app.finish_focus()
    assert not app.finish_focus()  # A repeated click must not save a duplicate session.
    assert app.store.seconds() == 95
    assert app.store.recent_sessions()[0]["subject_id"] == subject_id
    assert app.metric_values[0].cget("text") == "0h 01m"
    assert app.metric_values[1].cget("text") == "1"
    # An automatic save failure must not stop the tick loop.
    app.start_focus(subject_id)
    app.running_since -= 901
    with patch.object(app.store, "add_session", side_effect=sqlite3.OperationalError("database is locked")), patch.object(app, "after") as after:
        app.tick()
        after.assert_called_once_with(250, app.tick)
    assert app.session_open and app.running_since is None
    assert app.store.seconds() == 95
    assert app.finish_focus()
    assert app.store.seconds() == 995
    # Yesterday's checkbox values must be replaced when the local day changes.
    app.store.set_task("review_subject", True)
    app.task_vars["review_subject"].set(True)
    tomorrow = date.today() + timedelta(days=1)
    with patch("app.date", wraps=date) as app_date, patch("storage.date", wraps=date) as storage_date, patch.object(app, "after") as after:
        app_date.today.return_value = tomorrow
        storage_date.today.return_value = tomorrow
        app.tick()
        after.assert_called_once_with(250, app.tick)
        assert app.active_day == tomorrow
        assert not app.task_vars["review_subject"].get()
    app.active_day = date.today()
    for key, variable in app.task_vars.items():
        variable.set(app.store.task(key))
    app.navigate("My Subjects")
    app.subject_page.ask_delete(subject_id)
    next_step(check_delete)


def check_delete():
    assert app.subject_page.delete_panel.winfo_ismapped()
    app.subject_page.delete_button.invoke()
    assert app.store.subject(subject_id) is None
    assert app.store.seconds() == 995
    assert app.store.recent_sessions()[0]["subject_id"] is None
    assert app.store.recent_sessions()[0]["subject_name"] == "Mathematics – skúška"
    assert app.store.upcoming_exams() == []
    app.close()


def timeout():
    errors.append("Native UI check timed out")
    app.destroy()


app.report_callback_exception = lambda kind, value, tb: fail(value)
app.after(900, guarded(check_initial))
app.after(12000, timeout)
try:
    app.mainloop()
finally:
    app.store.close()
if not errors:
    reopened = Store(path)
    assert len(reopened.subjects()) == 3
    assert reopened.seconds() == 995
    assert reopened.task("focus")
    reopened.close()
    print("PASS: subject CRUD, wide/compact layouts, search, scrolling, timer save/retry and scheduling, midnight checklist, retained history and reopen", flush=True)
temp.cleanup()
raise SystemExit(1 if errors else 0)
