"""Short native-window smoke check; uses a disposable database."""
import tempfile
import traceback
from pathlib import Path

import customtkinter as ctk
from app import Dashboard

ctk.set_appearance_mode("dark")
temp = tempfile.TemporaryDirectory()
print("Creating Dashboard...", flush=True)
app = Dashboard(Path(temp.name) / "check.sqlite3")
errors = []


def fail(exc):
    errors.append(str(exc))
    traceback.print_exc()
    app.destroy()


def check_initial():
    try:
        assert app.title() == "SOSkúška", "Window title does not match the product name"
        assert app.content.winfo_ismapped(), "Dashboard content is not visible"
        assert app.start_button.winfo_ismapped(), "Start Studying is not visible"
        assert app.content.winfo_width() > 600
        app.query.set("Physics")
        app.after(100, check_search)
    except Exception as exc:
        fail(exc)


def check_search():
    try:
        assert sum(card.winfo_ismapped() for _, card in app.subject_cards) == 1
        app.query.set("no matching subject")
        app.after(100, check_empty)
    except Exception as exc:
        fail(exc)


def check_empty():
    try:
        assert app.empty.winfo_ismapped()
        app.query.set("")
        app.toggle_sidebar()
        assert app.collapsed
        app.toggle_sidebar()
        app.geometry("1024x700")
        app.after(400, check_compact)
    except Exception as exc:
        fail(exc)


def check_compact():
    try:
        app.reflow()
        assert app.layout_mode == "compact"
        canvas = app.scroll._parent_canvas
        canvas.yview_moveto(0)
        before = canvas.yview()[0]
        app.start_button.event_generate("<MouseWheel>", delta=-120)
        after_wheel = canvas.yview()[0]
        assert before < after_wheel < 0.2, "Mouse wheel did not scroll a moderate distance"
        if float(app.tk.call("package", "provide", "Tk").split(".")[0]) >= 9:
            app.start_button.event_generate("<TouchpadScroll>", delta=(-12 & 0xFFFF))
            after_touch = canvas.yview()[0]
            assert after_touch > after_wheel, "Trackpad did not scroll down"
            app.start_button.event_generate("<TouchpadScroll>", delta=12)
            assert canvas.yview()[0] < after_touch, "Trackpad did not scroll up"
            position = canvas.yview()[0]
            app.start_button.event_generate("<TouchpadScroll>", delta=(12 << 16))
            assert canvas.yview()[0] == position, "Horizontal gesture scrolled vertically"
            app.sidebar.event_generate("<TouchpadScroll>", delta=(-12 & 0xFFFF))
            assert canvas.yview()[0] == position, "Sidebar gesture moved the content"
        app.start_focus()
        app.running_since -= 95
        app.pause_focus()
        assert app.running_since is None
        app.finish_focus()
        assert app.store.seconds() == 95
        assert app.start_button.cget("state") == "normal"
        print("PASS: visible widgets, search, empty state, sidebar, resizing, wheel/trackpad scrolling, timer, persistence", flush=True)
        app.close()
    except Exception as exc:
        fail(exc)


def timeout():
    errors.append("Native UI check timed out")
    app.destroy()


app.after(1000, check_initial)
app.after(10000, timeout)
app.mainloop()
temp.cleanup()
raise SystemExit(1 if errors else 0)
