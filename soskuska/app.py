"""SOSkúška native Dashboard. Run: python soskuska/app.py."""
import argparse
import os
import platform
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import tkinter

# Apple's bundled Tk 8.5 can display an empty window on recent macOS.
# Fail before creating the root so the user gets an actionable error instead.
if sys.platform == "darwin" and tkinter.TkVersion < 8.6:
    raise SystemExit(
        "SOSkúška cannot use macOS system Tk 8.5.\n"
        "From the project directory, run: .venv-macos/bin/python soskuska/app.py\n"
        "Alternatively use Python with Tk 8.6 or newer."
    )

import customtkinter as ctk
from storage import Store, default_database
from scrolling import DashboardScrollFrame

C = dict(bg="#0D1117", sidebar="#11151C", card="#181D27", raised="#202633",
         border="#2A303C", accent="#8B5CF6", hover="#A78BFA", primary="#6D28D9",
         text="#F3F4F6", secondary="#9CA3AF", green="#22C55E", warning="#F59E0B")
SUBJECTS = [("Mathematics", "Calculus · Derivatives", 340, .72, "∑"),
            ("Computer Science", "Algorithms · Sorting", 215, .58, ">_"),
            ("Physics", "Mechanics · Motion", 180, .44, "λ"),
            ("English", "Vocabulary · Advanced", 420, .81, "Aa")]
NAV = [("Dashboard", "▦"), ("My Subjects", "▤"), ("Flashcards", "▱"),
       ("Practice Tests", "☑"), ("AI Tutor", "◇"), ("Statistics", "▥")]


def data_path():
    if sys.platform == "win32":
        base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Application Support"
    else:
        base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share"))
    return default_database(base)


class Dashboard(ctk.CTk):
    def __init__(self, database=None):
        super().__init__()
        self.title("SOSkúška")
        self.geometry("1440x900")
        self.minsize(1024, 700)
        self.configure(fg_color=C["bg"])
        self.family = "Segoe UI" if platform.system() == "Windows" else "Helvetica" if sys.platform == "darwin" else "Noto Sans"
        self.store = Store(database or data_path())
        self.running_since = None
        self.session_seconds = 0.0
        self.focus_target = 15 * 60
        self.collapsed = False
        self.layout_mode = None
        self.resize_job = None
        self.notice_job = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.build_sidebar()
        self.build_content()
        self.bind("<Configure>", self.on_resize)
        self.bind("<Control-k>", self.focus_search)
        self.bind("<Command-k>", self.focus_search)
        self.bind("<Escape>", self.clear_search)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.update_metrics()
        self.after(100, self.reflow)
        self.after(250, self.tick)

    def font(self, size=14, bold=False):
        return ctk.CTkFont(family=self.family, size=size, weight="bold" if bold else "normal")

    def label(self, parent, text, size=14, color="text", bold=False, **kwargs):
        return ctk.CTkLabel(parent, text=text, font=self.font(size, bold),
                            text_color=C[color], anchor="w", **kwargs)

    def frame(self, parent, card=False, **kwargs):
        return ctk.CTkFrame(parent, fg_color=C["card"] if card else "transparent",
                            corner_radius=12 if card else 0,
                            border_width=1 if card else 0, border_color=C["border"], **kwargs)

    def button(self, parent, text, command, primary=False, **kwargs):
        return ctk.CTkButton(parent, text=text, command=command, height=38,
                             corner_radius=8, font=self.font(14, primary),
                             fg_color=C["primary"] if primary else C["raised"],
                             hover_color="#7C3AED" if primary else C["border"],
                             text_color=C["text"], border_width=0 if primary else 1,
                             border_color=C["border"], **kwargs)

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=C["sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(3, weight=1)
        brand = self.frame(self.sidebar)
        brand.grid(row=0, column=0, padx=16, pady=(24, 26), sticky="ew")
        brand.grid_columnconfigure(0, weight=1)
        self.brand = self.label(brand, "▤  SOSkúška", 19, bold=True)
        self.brand.grid(row=0, column=0, sticky="w")
        self.collapse_btn = self.button(brand, "‹", self.toggle_sidebar, width=28)
        self.collapse_btn.grid(row=0, column=1)
        nav = self.frame(self.sidebar)
        nav.grid(row=1, column=0, padx=12, sticky="ew")
        self.nav_buttons = []
        for i, (name, icon) in enumerate(NAV):
            b = ctk.CTkButton(nav, text=f"{icon}   {name}", anchor="w", height=42,
                             font=self.font(14, i == 0), corner_radius=8,
                             fg_color="#211B35" if i == 0 else "transparent",
                             hover_color=C["raised"],
                             text_color=C["hover"] if i == 0 else C["secondary"],
                             command=lambda name=name: self.navigate(name))
            b.pack(fill="x", pady=2)
            self.nav_buttons.append(b)
        self.settings_btn = ctk.CTkButton(self.sidebar, text="⚙   Settings", anchor="w", height=40,
                                          font=self.font(), fg_color="transparent", hover_color=C["raised"],
                                          text_color=C["secondary"], command=lambda: self.navigate("Settings"))
        self.settings_btn.grid(row=4, column=0, padx=12, pady=12, sticky="ew")
        self.footer = self.frame(self.sidebar)
        self.footer.grid(row=5, column=0, sticky="ew", padx=20, pady=(8, 24))
        self.label(self.footer, "LOCAL WORKSPACE", 11, "secondary").pack(anchor="w", pady=(0, 12))
        self.label(self.footer, "Alex Morgan", bold=True).pack(anchor="w")
        self.label(self.footer, "Offline · Stored on this device", 12, "secondary").pack(anchor="w", pady=(2, 18))
        self.label(self.footer, "○  AI not connected", 12, "secondary").pack(anchor="w")
        self.label(self.footer, "Dashboard preview · v0.1.0", 11, "secondary").pack(anchor="w", pady=(6, 0))

    def build_content(self):
        self.scroll = DashboardScrollFrame(self, fg_color=C["bg"], corner_radius=0,
                                            scrollbar_button_color=C["border"],
                                            scrollbar_button_hover_color=C["secondary"])
        self.scroll.grid(row=0, column=1, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)
        self.content = self.frame(self.scroll)
        self.content.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.content.grid_columnconfigure(0, weight=1)
        head = self.frame(self.content)
        head.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        head.grid_columnconfigure(0, weight=1)
        self.label(head, date.today().strftime("%A, %B %d, %Y"), 12, "secondary").grid(row=0, column=0, sticky="w")
        self.label(head, "Ready to make progress?", 28, bold=True).grid(row=1, column=0, sticky="w", pady=(4, 2))
        self.label(head, "A little focus today goes a long way.", 14, "secondary").grid(row=2, column=0, sticky="w")
        self.start_button = self.button(head, "Start Studying  →", self.start_focus, primary=True, width=160)
        self.start_button.grid(row=1, column=1, rowspan=2, padx=(16, 0), sticky="e")
        self.metrics = self.frame(self.content)
        self.metrics.grid(row=1, column=0, sticky="ew", pady=(0, 24))
        self.metric_cards, self.metric_values = [], []
        for name, val in [("Total study time", "24h 35m"), ("Questions answered", "1,248"), ("Current streak", "7 days"), ("Overall accuracy", "86%")]:
            card = self.frame(self.metrics, card=True)
            self.label(card, name, 12, "secondary").pack(anchor="w", padx=16, pady=(16, 6))
            label = self.label(card, val, 26, bold=True)
            label.pack(anchor="w", padx=16, pady=(0, 16))
            self.metric_cards.append(card)
            self.metric_values.append(label)
        self.columns = self.frame(self.content)
        self.columns.grid(row=2, column=0, sticky="ew")
        self.columns.grid_columnconfigure(0, weight=1)
        self.main = self.frame(self.columns)
        self.main.grid_columnconfigure(0, weight=1)
        self.rail = self.frame(self.columns)
        self.rail.grid_columnconfigure(0, weight=1)
        self.build_focus()
        self.build_subjects()
        self.build_rail()
        self.notice = self.label(self.content, "Sample study data · Focus sessions and checklist changes are saved locally.", 12, "secondary", wraplength=650)
        self.notice.grid(row=3, column=0, sticky="w", pady=(22, 4))

    def build_focus(self):
        self.label(self.main, "Today's focus", 16, bold=True).grid(row=0, column=0, sticky="w", pady=(0, 12))
        focus = self.frame(self.main, card=True)
        focus.grid(row=1, column=0, sticky="ew")
        focus.grid_columnconfigure(0, weight=1)
        self.label(focus, "Daily goal", 12, "secondary").grid(row=0, column=0, sticky="w", padx=18, pady=(16, 4))
        self.goal = self.label(focus, "45 / 60 min", 22, bold=True)
        self.goal.grid(row=1, column=0, sticky="w", padx=18)
        self.goal_bar = ctk.CTkProgressBar(focus, height=6, fg_color=C["raised"], progress_color=C["accent"])
        self.goal_bar.grid(row=2, column=0, sticky="ew", padx=18, pady=(12, 16))
        for row, (key, text, default) in enumerate([("cards", "Review 20 overdue flashcards", True), ("test", "Complete 1 Mathematics practice test", False)], 3):
            var = ctk.BooleanVar(value=self.store.task(key, default))
            check = ctk.CTkCheckBox(focus, text=text, variable=var, font=self.font(14),
                                   text_color=C["text"], fg_color=C["primary"], hover_color=C["accent"],
                                   border_color=C["border"], checkbox_width=18, checkbox_height=18,
                                   command=lambda k=key, v=var: self.save_task(k, v.get()))
            check.grid(row=row, column=0, sticky="w", padx=18, pady=(0, 14))
        self.timer_frame = self.frame(focus)
        self.timer_frame.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 16))
        self.timer_frame.grid_columnconfigure(0, weight=1)
        self.timer_label = self.label(self.timer_frame, "15:00 · Focus session", 14, "hover", bold=True)
        self.timer_label.grid(row=0, column=0, sticky="w")
        self.pause_button = self.button(self.timer_frame, "Pause", self.pause_focus, width=74)
        self.pause_button.grid(row=0, column=1, padx=(8, 8))
        self.button(self.timer_frame, "Finish", self.finish_focus, width=70).grid(row=0, column=2)
        self.timer_frame.grid_remove()
        self.label(self.main, "Continue studying", 16, bold=True).grid(row=2, column=0, sticky="w", pady=(22, 12))
        resume = self.frame(self.main, card=True)
        resume.grid(row=3, column=0, sticky="ew")
        resume.grid_columnconfigure(0, weight=1)
        self.label(resume, "Mathematics", 15, bold=True).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 2))
        self.label(resume, "Calculus · Derivatives", 12, "secondary").grid(row=1, column=0, sticky="w", padx=18, pady=(0, 16))
        self.button(resume, "Resume session", self.start_focus, width=130).grid(row=0, column=1, rowspan=2, padx=16)

    def build_subjects(self):
        header = self.frame(self.main)
        header.grid(row=4, column=0, sticky="ew", pady=(22, 12))
        header.grid_columnconfigure(0, weight=1)
        self.label(header, "Subject progress", 16, bold=True).grid(row=0, column=0, sticky="w")
        self.query = ctk.StringVar()
        self.query.trace_add("write", lambda *_: self.filter_subjects())
        self.search = ctk.CTkEntry(header, placeholder_text="Search subjects…", width=190, height=34,
                                   textvariable=self.query, fg_color=C["sidebar"], border_color=C["border"],
                                   text_color=C["text"], font=self.font(12))
        self.search.grid(row=0, column=1, padx=(12, 0))
        self.subject_grid = self.frame(self.main)
        self.subject_grid.grid(row=5, column=0, sticky="ew")
        self.subject_grid.grid_columnconfigure((0, 1), weight=1, uniform="subject")
        self.subject_cards = []
        for name, topic, count, progress, icon in SUBJECTS:
            card = self.frame(self.subject_grid, card=True)
            card.grid_columnconfigure(0, weight=1)
            self.label(card, f"{icon}  {name}", 14, bold=True).grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")
            self.label(card, f"{count} questions  ·  {int(progress*100)}%", 12, "secondary").grid(row=1, column=0, padx=16, sticky="w")
            bar = ctk.CTkProgressBar(card, height=5, fg_color=C["raised"], progress_color=C["accent"])
            bar.set(progress)
            bar.grid(row=2, column=0, sticky="ew", padx=16, pady=(14, 16))
            self.subject_cards.append((name, card))
        self.empty = self.label(self.subject_grid, "No matching subjects. Try another name.", 14, "secondary")
        self.filter_subjects()

    def build_rail(self):
        self.label(self.rail, "Upcoming exams", 16, bold=True).grid(row=0, column=0, sticky="w", pady=(0, 12))
        exams = self.frame(self.rail, card=True)
        exams.grid(row=1, column=0, sticky="ew")
        exams.grid_columnconfigure(0, weight=1)
        for i, (name, days) in enumerate([("Mathematics", 4), ("Physics", 8), ("Computer Science", 13)]):
            row = self.frame(exams)
            row.grid(row=i, column=0, sticky="ew", padx=16, pady=14)
            row.grid_columnconfigure(0, weight=1)
            self.label(row, name, 14, bold=True).grid(row=0, column=0, sticky="w")
            self.label(row, (date.today() + timedelta(days=days)).strftime("%b %d"), 12, "secondary").grid(row=1, column=0, sticky="w")
            self.label(row, f"{days} days", 12, "warning" if i == 0 else "secondary").grid(row=0, column=1, rowspan=2, padx=(12, 0))
        self.label(self.rail, "Recent activity", 16, bold=True).grid(row=2, column=0, sticky="w", pady=(22, 12))
        activity = self.frame(self.rail, card=True)
        activity.grid(row=3, column=0, sticky="ew")
        for title, detail in [("Completed practice test", "Mathematics · Score 85%"), ("Reviewed flashcards", "English · 45 cards"), ("Studied a topic", "Physics · 20 minutes")]:
            self.label(activity, title, 14).pack(anchor="w", padx=16, pady=(16, 2))
            self.label(activity, detail, 12, "secondary").pack(anchor="w", padx=16, pady=(0, 14))

    def on_resize(self, event):
        if event.widget is self:
            if self.resize_job:
                self.after_cancel(self.resize_job)
            self.resize_job = self.after(120, self.reflow)

    def reflow(self):
        self.resize_job = None
        available = self.winfo_width() - (72 if self.collapsed else 230)
        mode = "wide" if available >= 1100 else "compact"
        if mode == self.layout_mode:
            return
        self.layout_mode = mode
        wide = mode == "wide"
        self.columns.grid_columnconfigure(1, weight=0, minsize=300 if wide else 0)
        self.main.grid(row=0, column=0, sticky="nsew", padx=(0, 24 if wide else 0))
        self.rail.grid(row=0 if wide else 1, column=1 if wide else 0, sticky="new", pady=(0 if wide else 24, 0))
        for i in range(4):
            self.metrics.grid_columnconfigure(i, weight=1 if wide or i < 2 else 0, uniform="metric" if wide or i < 2 else "")
        for i, card in enumerate(self.metric_cards):
            col, row = (i, 0) if wide else (i % 2, i // 2)
            card.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else 6, 0 if col == (3 if wide else 1) else 6), pady=(0, 12 if not wide and row == 0 else 0))

    def toggle_sidebar(self):
        self.collapsed = not self.collapsed
        self.sidebar.configure(width=72 if self.collapsed else 230)
        self.brand.configure(text="" if self.collapsed else "▤  SOSkúška")
        self.collapse_btn.configure(text="›" if self.collapsed else "‹")
        for button, (name, icon) in zip(self.nav_buttons, NAV):
            button.configure(text=icon if self.collapsed else f"{icon}   {name}", anchor="center" if self.collapsed else "w")
        self.settings_btn.configure(text="⚙" if self.collapsed else "⚙   Settings")
        self.footer.grid_remove() if self.collapsed else self.footer.grid()
        self.reflow()

    def navigate(self, name):
        self.show_notice("Dashboard is open." if name == "Dashboard" else f"{name} will be available in a later version.")

    def show_notice(self, text):
        self.notice.configure(text=text, text_color=C["hover"])

    def save_task(self, key, value):
        self.store.set_task(key, value)
        self.show_notice("Checklist saved on this device.")

    def filter_subjects(self):
        query = self.query.get().strip().casefold()
        shown = 0
        for name, card in self.subject_cards:
            card.grid_remove()
            if query in name.casefold():
                card.grid(row=shown // 2, column=shown % 2, sticky="ew", padx=(0, 6) if shown % 2 == 0 else (6, 0), pady=(0, 12))
                shown += 1
        self.empty.grid_remove()
        if not shown:
            self.empty.grid(row=0, column=0, columnspan=2, sticky="w", pady=20)

    def focus_search(self, _event=None):
        self.search.focus_set()
        return "break"

    def clear_search(self, _event=None):
        self.query.set("")

    def elapsed(self):
        return self.session_seconds + (time.monotonic() - self.running_since if self.running_since is not None else 0)

    def start_focus(self):
        if self.running_since is not None or self.session_seconds:
            self.show_notice("A focus session is already open. Use Resume or Finish below the daily goal.")
            return
        self.running_since = time.monotonic()
        self.pause_button.configure(text="Pause")
        self.timer_frame.grid()
        self.start_button.configure(state="disabled")
        self.show_notice("Focus session started · Mathematics / Derivatives")

    def pause_focus(self):
        if self.running_since is not None:
            self.session_seconds = self.elapsed()
            self.running_since = None
            self.pause_button.configure(text="Resume")
        else:
            self.running_since = time.monotonic()
            self.pause_button.configure(text="Pause")

    def finish_focus(self):
        elapsed = min(int(self.elapsed()), self.focus_target)
        self.store.add_session(elapsed)
        self.running_since = None
        self.session_seconds = 0.0
        self.timer_frame.grid_remove()
        self.start_button.configure(state="normal")
        self.update_metrics()
        self.show_notice(f"Session saved · {elapsed // 60}m {elapsed % 60:02d}s of focused study.")

    def update_metrics(self):
        # Baseline metrics are visibly marked sample data; actual session time is additive.
        seconds = self.store.seconds()
        minutes = 24 * 60 + 35 + seconds // 60
        self.metric_values[0].configure(text=f"{minutes // 60}h {minutes % 60:02d}m")
        today = 45 + self.store.seconds(today=True) // 60
        self.goal.configure(text=f"{today} / 60 min")
        self.goal_bar.set(min(today / 60, 1))

    def tick(self):
        if self.running_since is not None or self.session_seconds:
            remaining = max(0, self.focus_target - int(self.elapsed()))
            self.timer_label.configure(text=f"{remaining // 60:02d}:{remaining % 60:02d} · {'Paused' if self.running_since is None else 'Focus'}")
            if remaining == 0:
                self.finish_focus()
        self.after(250, self.tick)

    def close(self):
        if self.running_since is not None or self.session_seconds:
            self.store.add_session(min(int(self.elapsed()), self.focus_target))
        self.store.close()
        self.destroy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SOSkúška native desktop Dashboard")
    parser.add_argument("--data", type=Path, help="Override the local SQLite database path")
    args = parser.parse_args()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    Dashboard(args.data).mainloop()
