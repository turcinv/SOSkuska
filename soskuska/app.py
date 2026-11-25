"""SOSkúška native Dashboard. Run: python soskuska/app.py."""
from localization_widgets import LocalizedOptionMenu
from localization import tr, Translator
import argparse
import os
import platform
import sqlite3
import sys
import time
from datetime import date
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
from subjects import SubjectPage
from question_bank import QuestionBankPage
from practice_page import PracticePage
from flashcard_page import FlashcardPage
from statistics_page import StatisticsPage
from tutor_page import TutorPage
from settings_page import SettingsPage
from preferences import AI_KEYS
from startup_errors import report_startup_error
from appearance import apply_appearance

APP_VERSION = '0.24.0'

from theme import COLORS as C

SAVE_RETRY_NOTICE = "This session could not be saved. Press Finish to retry saving it."
REFRESH_RETRY_NOTICE = "Could not refresh the Dashboard. Retrying automatically."

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
        ctk.set_appearance_mode("Dark")  # Disable implicit OS polling before constructing Tk.
        super().__init__()
        self.title(tr(self, 'SOSkúška'))
        self.geometry("1440x900")
        self.minsize(1024, 700)
        self.configure(fg_color=C["bg"])
        self.family = "Segoe UI" if platform.system() == "Windows" else "Helvetica" if sys.platform == "darwin" else "Noto Sans"
        self.store = Store(database or data_path())
        self.preferences = self.store.preferences()
        apply_appearance(self.preferences["appearance_mode"])
        self.translator = Translator(self.preferences["ui_language"])
        self.saved_today_seconds = 0
        self.data_restoring = False
        self.running_since = None
        self.session_seconds = 0.0
        self.focus_run_id = None
        self.last_checkpoint = 0.0
        self.recovery_record = None
        self.pending_focus_discard = False
        self.session_open = False
        self.session_save_failed = False
        self.refresh_pending = False
        self.session_subject_id = None
        self.session_subject_name = None
        self.current_page = "Dashboard"
        self.selected_subject_id = None
        self.active_day = date.today()
        self.focus_target = self.preferences["focus_minutes"] * 60
        self.collapsed = False
        self.layout_mode = None
        self.resize_job = None
        self.notice_job = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.build_sidebar()
        self.build_content()
        self.backup_notice=self.label(self,'',12,'hover',wraplength=900)
        self.subject_page = SubjectPage(self.scroll, self)
        self.subject_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.subject_page.grid_remove()
        self.question_bank = QuestionBankPage(self.scroll, self)
        self.question_bank.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.question_bank.grid_remove()
        self.practice_page = PracticePage(self.scroll, self)
        self.practice_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.practice_page.grid_remove()
        self.flashcard_page = FlashcardPage(self.scroll, self)
        self.flashcard_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.flashcard_page.grid_remove()
        self.statistics_page = StatisticsPage(self.scroll, self)
        self.statistics_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.statistics_page.grid_remove()
        self.tutor_page = TutorPage(self.scroll, self)
        self.tutor_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.tutor_page.grid_remove()
        self.settings_page = SettingsPage(self.scroll, self)
        self.settings_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.settings_page.grid_remove()
        self.bind("<Configure>", self.on_resize)
        self.bind("<Control-k>", self.focus_search)
        self.bind("<Command-k>", self.focus_search)
        self.bind("<Escape>", self.clear_search)
        self.protocol("WM_DELETE_WINDOW", self.close)
        if self.tk.call("tk", "windowingsystem") == "aqua":
            # The native application-menu Quit does not send WM_DELETE_WINDOW.
            self.createcommand("::tk::mac::Quit", self.close)
        self.refresh_data()
        self.refresh_focus_recovery()
        self.after(100, self.reflow)
        self.after(250, self.tick)

    def display_date(self, day):
        if self.translator.language=='English':return day.strftime('%A, %B %d, %Y')
        return day.strftime('%d.%m.%Y')

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
        if self.translator.language!='English' and 'width' in kwargs:
            kwargs['width']=max(kwargs['width'],self.font(14,primary).measure(text)+24)
        return ctk.CTkButton(parent, text=text, command=command, height=38,
                             corner_radius=8, font=self.font(14, primary),
                             fg_color=C["primary"] if primary else C["raised"],
                             hover_color=C["primary_hover"] if primary else C["secondary_hover"],
                             text_color=C["on_primary"] if primary else C["text"],
                             text_color_disabled=C["disabled_on_primary"] if primary else C["secondary"], border_width=0 if primary else 1,
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
        self.brand = self.label(brand, tr(self, '▤  SOSkúška'), 19, bold=True)
        self.brand.grid(row=0, column=0, sticky="w")
        self.collapse_btn = self.button(brand, "‹", self.toggle_sidebar, width=28)
        self.collapse_btn.grid(row=0, column=1)
        nav = self.frame(self.sidebar)
        nav.grid(row=1, column=0, padx=12, sticky="ew")
        self.nav_buttons = []
        for i, (name, icon) in enumerate(NAV):
            b = ctk.CTkButton(nav, text=f"{icon}   {tr(self,name)}", anchor="w", height=42,
                             font=self.font(14, i == 0), corner_radius=8, border_width=1,
                             border_color=C["hover"] if i == 0 else C["sidebar"],
                             fg_color=C["selected"] if i == 0 else "transparent",
                             hover_color=C["raised"],
                             text_color=C["hover"] if i == 0 else C["secondary"],
                             command=lambda name=name: self.navigate(name))
            b.pack(fill="x", pady=2)
            self.nav_buttons.append(b)
        self.settings_btn = ctk.CTkButton(self.sidebar, text=tr(self, '⚙   Settings'), anchor="w", height=40,
                                          font=self.font(), fg_color="transparent", hover_color=C["raised"],
                                          border_width=1, border_color=C["sidebar"], corner_radius=8,
                                          text_color=C["secondary"], command=lambda: self.navigate("Settings"))
        self.settings_btn.grid(row=4, column=0, padx=12, pady=12, sticky="ew")
        self.footer = self.frame(self.sidebar)
        self.footer.grid(row=5, column=0, sticky="ew", padx=20, pady=(8, 24))
        self.label(self.footer, tr(self, 'LOCAL WORKSPACE'), 11, "secondary").pack(anchor="w", pady=(0, 12))
        self.label(self.footer, tr(self, 'Local student'), bold=True).pack(anchor="w")
        self.label(self.footer, tr(self, 'Offline · Stored on this device'), 12, "secondary", wraplength=190).pack(anchor="w", pady=(2, 18))
        self.focus_alert = self.button(self.sidebar,tr(self,'Focus needs saving'),self.show_focus_retry,width=40)
        self.ai_status = self.label(self.footer, tr(self, '○  AI not connected'), 12, "secondary", wraplength=190)
        self.ai_status.pack(anchor="w")
        self.label(self.footer, tr(self, 'Study workspace · {v0}',v0=f'v{APP_VERSION}'), 11, "secondary").pack(anchor="w", pady=(6, 0))

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
        head.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        head.grid_columnconfigure(0, weight=1)
        self.date_label = self.label(head, self.display_date(date.today()), 12, "secondary")
        self.date_label.grid(row=0, column=0, sticky="w")
        self.label(head, tr(self, 'Dashboard'), 28, bold=True).grid(row=1, column=0, sticky="w", pady=(4, 2))
        self.label(head, tr(self, 'Choose a subject and start a focused session.'), 14,
                   "secondary", wraplength=650).grid(row=2, column=0, sticky="w")
        self.columns = self.frame(self.content)
        self.columns.grid(row=1, column=0, sticky="ew")
        self.columns.grid_columnconfigure(0, weight=1)
        self.main = self.frame(self.columns)
        self.main.grid_columnconfigure(0, weight=1)
        self.rail = self.frame(self.columns)
        self.rail.grid_columnconfigure(0, weight=1)
        self.build_focus()
        self.build_subjects()
        self.build_rail()
        self.metrics = self.frame(self.content, card=True)
        self.metrics.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        self.label(self.metrics, tr(self, 'Lifetime summary'), 14, bold=True).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=16, pady=(12, 0))
        self.metric_cards, self.metric_values = [], []
        for name, val in [("Total study time", "0h 00m"), ("Study sessions", "0"), ("Current streak", "0 days"), ("Subjects", "0")]:
            card = self.frame(self.metrics)
            self.label(card, tr(self,name), 11, "secondary").pack(anchor="w", padx=16, pady=(4, 2))
            value = self.label(card, val, 18, bold=True)
            value.pack(anchor="w", padx=16, pady=(0, 4))
            self.metric_cards.append(card)
            self.metric_values.append(value)
        self.notice = self.label(self.content, tr(self, 'Your subjects and study time are stored on this device.'), 12, "secondary", wraplength=650)
        self.notice.grid(row=3, column=0, sticky="w", pady=(16, 4))

    def build_focus(self):
        self.study_panel = self.frame(self.main, card=True)
        self.study_panel.grid(row=0, column=0, sticky="ew")
        focus = self.study_panel
        focus.grid_columnconfigure(0, weight=1)
        self.label(focus, tr(self, "Today's Study"), 22, bold=True).grid(
            row=0, column=0, sticky="w", padx=18, pady=(16, 12))
        self.label(focus, tr(self, 'Choose a subject'), 12, "secondary").grid(
            row=1, column=0, sticky="w", padx=18, pady=(0, 4))
        self.study_actions = self.frame(focus)
        self.study_actions.grid(row=2, column=0, sticky="ew", padx=18)
        self.study_actions.grid_columnconfigure(0, weight=1)
        self.subject_selection = ctk.StringVar(value="Add a subject first")
        self.subject_picker = LocalizedOptionMenu(self.study_actions, owner=self,
            translate_values=False, empty_text="Add a subject first", variable=self.subject_selection,
            values=[], command=self.select_subject, font=self.font(), height=38, width=180,
            dynamic_resizing=False, fg_color=C["raised"], button_color=C["border"],
            button_hover_color=C["selected"])
        self.subject_picker.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.start_button = self.button(self.study_actions, tr(self, 'Start Studying  →'),
                                        self.start_focus, primary=True, width=160)
        self.start_button.grid(row=0, column=1, sticky="e")
        self.study_hint = self.label(focus, tr(self, 'Focus sessions are saved against the selected subject.'),
                                     12, "secondary", wraplength=650)
        self.study_hint.grid(row=3, column=0, sticky="ew", padx=18, pady=(8, 12))
        self.timer_frame = self.frame(focus)
        self.timer_frame.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 14))
        self.timer_frame.grid_columnconfigure(0, weight=1)
        self.timer_label = self.label(self.timer_frame, tr(self, '{v0:02d}:00 · Focus session',
                                      v0=self.focus_target // 60), 18, "hover", bold=True)
        self.timer_label.grid(row=0, column=0, sticky="w")
        self.pause_button = self.button(self.timer_frame, tr(self, 'Pause'), self.pause_focus, width=90)
        self.pause_button.grid(row=0, column=1, padx=(8, 8))
        self.finish_button = self.button(self.timer_frame, tr(self, 'Finish'), self.finish_focus,
                                          primary=True, width=100)
        self.finish_button.grid(row=0, column=2)
        self.focus_subject_label = self.label(self.timer_frame,'',12,'secondary',wraplength=650)
        self.focus_subject_label.grid(row=1,column=0,columnspan=3,sticky='ew',pady=(6,0))
        self.focus_retry_label = self.label(self.timer_frame,'',12,'hover',wraplength=650)
        self.focus_retry_label.grid(row=2,column=0,columnspan=3,sticky='ew',pady=(6,0))
        self.timer_frame.grid_remove()
        self.recovery_panel = self.frame(focus)
        self.recovery_panel.grid(row=5,column=0,sticky='ew',padx=18,pady=(0,14))
        self.recovery_panel.grid_columnconfigure(0,weight=1)
        self.label(self.recovery_panel,tr(self,'Saved focus session'),16,bold=True).grid(
            row=0,column=0,sticky='w',pady=(0,6))
        self.recovery_status = self.label(self.recovery_panel,'',13,'secondary',wraplength=650)
        self.recovery_status.grid(row=1,column=0,sticky='ew',pady=(0,10))
        recovery_actions=self.frame(self.recovery_panel)
        recovery_actions.grid(row=2,column=0,sticky='w')
        self.recover_focus_button=self.button(recovery_actions,tr(self,'Recover paused'),self.recover_focus,primary=True,width=155)
        self.recover_focus_button.pack(side='left',padx=(0,8))
        self.discard_focus_button=self.button(recovery_actions,tr(self,'Discard checkpoint'),self.discard_focus,width=175)
        self.discard_focus_button.pack(side='left',padx=(0,8))
        self.button(recovery_actions,tr(self,'Refresh'),self.refresh_focus_recovery,width=110).pack(side='left')
        self.recovery_panel.grid_remove()
        goal_row = self.frame(focus)
        goal_row.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 6))
        goal_row.grid_columnconfigure(0, weight=1)
        self.label(goal_row, tr(self, 'Daily goal'), 12, "secondary").grid(row=0, column=0, sticky="w")
        self.goal = self.label(goal_row, tr(self, '0 / 60 min'), 18, bold=True)
        self.goal.grid(row=0, column=1, sticky="e")
        self.goal_bar = ctk.CTkProgressBar(focus, height=6, fg_color=C["raised"], progress_color=C["accent"])
        self.goal_bar.grid(row=7, column=0, sticky="ew", padx=18, pady=(0, 14))
        self.task_vars = {}
        for row, (key, text, default) in enumerate([("review_subject", "Review a subject", False), ("focus", "Complete a focus session", False)], 8):
            var = ctk.BooleanVar(value=self.store.task(key, default))
            self.task_vars[key] = var
            check = ctk.CTkCheckBox(focus, text=tr(self,text), variable=var, font=self.font(14),
                text_color=C["text"], checkmark_color=C["on_primary"], fg_color=C["primary"],
                hover_color=C["primary_hover"], border_color=C["border"], checkbox_width=18,
                checkbox_height=18, command=lambda k=key, v=var: self.save_task(k, v.get()))
            check.grid(row=row, column=0, sticky="w", padx=18, pady=(0, 14))

    def build_subjects(self):
        header = self.frame(self.main)
        header.grid(row=1, column=0, sticky="ew", pady=(22, 12))
        header.grid_columnconfigure(0, weight=1)
        self.label(header, tr(self, 'My subjects'), 18, bold=True).grid(row=0, column=0, rowspan=2, sticky="w")
        self.label(header, tr(self, 'Search subjects…'), 11, 'secondary').grid(row=0, column=1, sticky='w', padx=12)
        self.query = ctk.StringVar()
        self.query.trace_add("write", lambda *_: self.filter_subjects())
        self.search = ctk.CTkEntry(header, placeholder_text=tr(self, 'Search subjects…'), width=190, height=38,
            textvariable=self.query, fg_color=C["sidebar"], border_color=C["border"],
            text_color=C["text"], font=self.font(12), placeholder_text_color=C["secondary"])
        self.search.grid(row=1, column=1, padx=(12, 12))
        self.manage_subjects_button = self.button(header, tr(self, 'Manage subjects'),
            lambda: self.navigate("My Subjects"), width=140)
        self.manage_subjects_button.grid(row=0, column=2, rowspan=2)
        self.subject_grid = self.frame(self.main)
        self.subject_grid.grid(row=2, column=0, sticky="ew")
        self.subject_grid.grid_columnconfigure((0, 1), weight=1, uniform="subject")
        self.subject_cards = []
        self.empty = self.label(self.subject_grid, "", 14, "secondary", wraplength=650)

    def build_rail(self):
        self.label(self.rail, tr(self, 'Upcoming exams'), 16, bold=True).grid(row=0, column=0, sticky="w", pady=(0, 12))
        self.exams = self.frame(self.rail, card=True)
        self.exams.grid(row=1, column=0, sticky="ew")
        self.exams.grid_columnconfigure(0, weight=1)
        self.label(self.rail, tr(self, 'Recent study sessions'), 16, bold=True).grid(row=2, column=0, sticky="w", pady=(22, 12))
        self.activity = self.frame(self.rail, card=True)
        self.activity.grid(row=3, column=0, sticky="ew")
        self.activity.grid_columnconfigure(0, weight=1)

    def refresh_rail(self):
        for panel in (self.exams, self.activity):
            for widget in panel.winfo_children():
                widget.destroy()
        exams = self.store.upcoming_exams()
        if not exams:
            self.label(self.exams, tr(self, 'No upcoming exams. Add a date in My Subjects.'), 13, "secondary", wraplength=250).grid(row=0, column=0, sticky="w", padx=16, pady=16)
        for i, exam in enumerate(exams):
            days = (date.fromisoformat(exam["exam_date"]) - date.today()).days
            self.label(self.exams, exam["name"], 14, bold=True, wraplength=250).grid(row=i*2, column=0, sticky="w", padx=16, pady=(14, 2))
            when = tr(self,'Today') if days == 0 else tr(self,'In {v0} days',v0=days)
            self.label(self.exams, tr(self, '{v0} · {v1}', v0=exam['exam_date'], v1=when), 12, "warning" if days <= 7 else "secondary").grid(row=i*2+1, column=0, sticky="w", padx=16, pady=(0, 12))
        sessions = self.store.recent_sessions()
        if not sessions:
            self.label(self.activity, tr(self, 'No saved sessions yet. Start with a short focus session.'), 13, "secondary", wraplength=250).grid(row=0, column=0, sticky="w", padx=16, pady=16)
        for i, session in enumerate(sessions):
            name = session["subject_name"] or tr(self,"Unassigned session")
            self.label(self.activity, name, 14, wraplength=250).grid(row=i*2, column=0, sticky="w", padx=16, pady=(14, 2))
            seconds = session["seconds"]
            self.label(self.activity, tr(self, '{v0} · {v1}m {v2:02d}s', v0=session['day'], v1=seconds // 60, v2=seconds % 60), 12, "secondary").grid(row=i*2+1, column=0, sticky="w", padx=16, pady=(0, 12))

    def on_resize(self, event):
        if event.widget is self or self.scroll.is_viewport(event.widget):
            if self.resize_job:
                self.after_cancel(self.resize_job)
            self.resize_job = self.after(120, self.reflow)

    def reflow(self):
        self.resize_job = None
        available = self.scroll.viewport_width()
        mode = "wide" if available >= 1100 else "compact"
        wide = mode == "wide"
        main_width = available - 56 - (324 if wide else 0)
        for widget in (self.study_hint, self.focus_subject_label, self.focus_retry_label,
                       self.recovery_status, self.empty):
            widget.configure(wraplength=max(220, main_width - 36))
        if mode == self.layout_mode:
            return
        self.layout_mode = mode
        self.columns.grid_columnconfigure(1, weight=0, minsize=300 if wide else 0)
        self.main.grid(row=0, column=0, sticky="nsew", padx=(0, 24 if wide else 0))
        self.rail.grid(row=0 if wide else 1, column=1 if wide else 0, sticky="new", pady=(0 if wide else 24, 0))
        for i in range(4):
            self.metrics.grid_columnconfigure(i, weight=1 if wide or i < 2 else 0, uniform="metric" if wide or i < 2 else "")
        for i, card in enumerate(self.metric_cards):
            col, row = (i, 0) if wide else (i % 2, i // 2)
            card.grid(row=row+1, column=col, sticky="ew", padx=8, pady=(0, 8))
        self.layout_subject_cards()

    def layout_subject_cards(self):
        columns = 1 if self.layout_mode == "compact" else 2
        self.subject_grid.grid_columnconfigure(1, weight=0 if columns == 1 else 1,
                                               uniform="" if columns == 1 else "subject")
        for i, (_, card) in enumerate(self.subject_cards):
            col = i % columns
            card.grid(row=i//columns, column=col, sticky="nsew",
                      padx=(0, 6) if columns == 2 and col == 0 else (6, 0) if columns == 2 else 0,
                      pady=(0, 12))

    def update_sidebar_selection(self, name):
        for button, (item, _) in zip(self.nav_buttons, NAV):
            active = item == name
            button.configure(fg_color=C["selected"] if active else "transparent",
                text_color=C["hover"] if active else C["secondary"],
                border_color=C["hover"] if active else C["sidebar"], font=self.font(14, active))
        active = name == "Settings"
        self.settings_btn.configure(fg_color=C["selected"] if active else "transparent",
            text_color=C["hover"] if active else C["secondary"],
            border_color=C["hover"] if active else C["sidebar"], font=self.font(14, active))

    def toggle_sidebar(self):
        self.collapsed = not self.collapsed
        self.sidebar.configure(width=72 if self.collapsed else 230)
        self.brand.configure(text="" if self.collapsed else tr(self, '▤  SOSkúška'))
        self.collapse_btn.configure(text="›" if self.collapsed else "‹")
        for button, (name, icon) in zip(self.nav_buttons, NAV):
            button.configure(text=icon if self.collapsed else f"{icon}   {tr(self,name)}", anchor="center" if self.collapsed else "w")
        self.settings_btn.configure(text="⚙" if self.collapsed else tr(self, '⚙   Settings'))
        self.footer.grid_remove() if self.collapsed else self.footer.grid()
        self.focus_alert.configure(text='!' if self.collapsed else tr(self,'Focus needs saving'))
        self.after_idle(self.reflow)

    def navigate(self, name):
        if self.question_bank.importer.saving or self.flashcard_page.importer.saving:
            (self.flashcard_page.importer if self.flashcard_page.importer.saving else self.question_bank.importer).status.configure(text=tr(self, 'Wait for the CSV import to finish before navigating.'))
            return
        self.question_bank.importer.cancel()
        self.flashcard_page.importer.cancel()
        if name not in ("Dashboard", "My Subjects", "Practice Tests", "Flashcards", "Statistics", "AI Tutor", "Settings"):
            self.show_notice(tr(self, '{v0} will be available in a later version.', v0=name))
            return
        self.cancel_focus_discard()
        self.subject_page.cancel_delete()
        self.settings_page.backups.cancel_pending()
        self.current_page = name
        self.question_bank.grid_remove()
        self.practice_page.grid_remove()
        self.flashcard_page.grid_remove()
        self.statistics_page.grid_remove()
        self.tutor_page.grid_remove()
        self.settings_page.grid_remove()
        if name == "Settings":
            self.content.grid_remove()
            self.subject_page.grid_remove()
            self.settings_page.load()
            self.settings_page.grid()
        elif name == "AI Tutor":
            self.content.grid_remove()
            self.subject_page.grid_remove()
            self.tutor_page.load()
            self.tutor_page.grid()
        elif name == "Statistics":
            self.content.grid_remove()
            self.subject_page.grid_remove()
            self.statistics_page.load()
            self.statistics_page.grid()
        elif name == "Flashcards":
            self.content.grid_remove()
            self.subject_page.grid_remove()
            self.flashcard_page.load()
            self.flashcard_page.grid()
        elif name == "Practice Tests":
            self.content.grid_remove()
            self.subject_page.grid_remove()
            self.practice_page.load()
            self.practice_page.grid()
        elif name == "My Subjects":
            self.content.grid_remove()
            self.subject_page.grid()
            self.subject_page.render()
        else:
            self.subject_page.grid_remove()
            self.content.grid()
            self.refresh_data()
        self.scroll._parent_canvas.yview_moveto(0)
        self.update_sidebar_selection(name)

    def open_question_bank(self, subject_id):
        if self.question_bank.importer.saving or self.flashcard_page.importer.saving:
            return
        self.flashcard_page.importer.cancel()
        self.cancel_focus_discard()
        try:
            subject = self.store.subject(subject_id)
        except sqlite3.Error:
            if self.question_bank.subject_id != subject_id:
                self.show_notice(tr(self, 'Could not refresh the question bank. Your draft is kept; reopen Questions to retry.'))
                return
            # Reopen the retained editor; load_subject owns the read retry notice.
            subject = True
        if subject is None:
            self.navigate("My Subjects")
            self.show_notice(tr(self, 'This subject no longer exists.'))
            return
        self.subject_page.cancel_delete()
        self.content.grid_remove()
        self.subject_page.grid_remove()
        self.practice_page.grid_remove()
        self.flashcard_page.grid_remove()
        self.statistics_page.grid_remove()
        self.tutor_page.grid_remove()
        self.settings_page.grid_remove()
        self.question_bank.load_subject(subject_id)
        self.question_bank.grid()
        self.current_page = "Question Bank"
        self.update_sidebar_selection("My Subjects")
        self.scroll._parent_canvas.yview_moveto(0)

    def show_notice(self, text):
        self.notice.configure(text=tr(self,text), text_color=C["hover"])
        if hasattr(self, "subject_page"):
            self.subject_page.status.configure(text=tr(self,text))
        if hasattr(self, "question_bank"):
            self.question_bank.status.configure(text=tr(self,text))

    def save_task(self, key, value):
        try:
            self.store.set_task(key, value)
        except sqlite3.Error:
            self.task_vars[key].set(not value)
            self.show_notice(tr(self, 'Could not save the checklist. Please try again.'))
            return
        self.show_notice(tr(self, 'Checklist saved on this device.'))

    def filter_subjects(self):
        for _, card in self.subject_cards:
            card.destroy()
        self.subject_cards = []
        query = self.query.get().strip().casefold()
        subjects = self.store.subjects()
        visible = [s for s in subjects if query in s["name"].casefold()]
        self.empty.grid_remove()
        for i, subject in enumerate(visible):
            card = self.frame(self.subject_grid, card=True)
            card.grid_columnconfigure(0, weight=1)
            title = self.label(card, subject["name"], 14, bold=True, wraplength=260)
            title.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 4))
            card.bind("<Configure>", lambda event, title=title: title.configure(wraplength=max(150, self.scroll.logical_pixels(event.width)-32)), add="+")
            self.label(card, tr(self, '{v0} sessions · {v1} min', v0=subject['session_count'], v1=subject['study_seconds'] // 60), 12, "secondary").grid(row=1, column=0, sticky="w", padx=16, pady=(0, 10))
            self.label(card, tr(self, '{v0} topics · {v1} questions', v0=subject['topic_count'], v1=subject['question_count']), 12, "secondary").grid(row=2, column=0, sticky="w", padx=16, pady=(0, 10))
            actions = self.frame(card)
            actions.grid(row=3, column=0, sticky="w", padx=16, pady=(0, 14))
            self.button(actions, tr(self, 'Study'), lambda sid=subject["id"]: self.start_focus(sid), primary=True, width=85).pack(side="left", padx=(0, 8))
            self.button(actions, tr(self, 'Questions'), lambda sid=subject["id"]: self.open_question_bank(sid), width=95).pack(side="left")
            card.grid(row=i//2, column=i%2, sticky="nsew", padx=(0, 6) if i%2 == 0 else (6, 0), pady=(0, 12))
            self.subject_cards.append((subject["name"], card))
        self.layout_subject_cards()
        if not visible:
            self.empty.configure(text=tr(self,tr(self, 'No matching subjects. Try another name.') if subjects else tr(self, 'No subjects yet. Open My Subjects to create your first one.')))
            self.empty.grid(row=0, column=0, columnspan=2, sticky="w", pady=20)

    def refresh_data(self):
        subjects = self.store.subjects()
        self.subject_ids = {s["name"]: s["id"] for s in subjects}
        selected = next((s for s in subjects if s["id"] == self.selected_subject_id), None)
        selected = selected or (subjects[0] if subjects else None)
        self.selected_subject_id = selected["id"] if selected else None
        self.subject_picker.configure(values=list(self.subject_ids),
                                      state="disabled" if self.session_open or not subjects else "normal")
        self.subject_selection.set(selected["name"] if selected else "Add a subject first")
        self.start_button.configure(text=tr(self, 'Start Studying  →' if subjects else 'Create your first subject'))
        self.update_metrics()
        self.filter_subjects()
        self.refresh_rail()
        if hasattr(self, "subject_page"):
            self.subject_page.render()

    def select_subject(self, name):
        self.selected_subject_id = self.subject_ids.get(name)

    def focus_search(self, _event=None):
        if self.current_page in ("Practice Tests", "Flashcards", "Statistics", "AI Tutor", "Settings"):
            return "break"
        if self.current_page == "Question Bank":
            self.question_bank.search.focus_set()
        else:
            (self.subject_page.search if self.current_page == "My Subjects" else self.search).focus_set()
        return "break"

    def clear_search(self, _event=None):
        if self.pending_focus_discard:
            self.cancel_focus_discard()
            return "break"
        if self.current_page in ("Practice Tests", "Flashcards", "Statistics", "AI Tutor", "Settings"):
            return
        if self.current_page == "Question Bank":
            self.question_bank.query.set("")
        else:
            (self.subject_page.query if self.current_page == "My Subjects" else self.query).set("")

    def elapsed(self):
        return self.session_seconds + (time.monotonic() - self.running_since if self.running_since is not None else 0)

    def focus_error(self,exc):
        return tr(self,'Could not access saved focus. Retry the action or Refresh recovery.') if isinstance(exc,(sqlite3.Error,OSError)) else tr(self,str(exc))

    def start_focus(self, subject_id=None):
        if self.session_open:
            self.navigate("Dashboard")
            self.show_notice(tr(self, 'A focus session is already open. Use Pause, Resume or Finish.'))
            return
        subject_id = subject_id if subject_id is not None else self.selected_subject_id
        if subject_id is None:
            self.navigate("My Subjects")
            self.subject_page.show_form()
            self.show_notice(tr(self, 'Create a subject before starting your first focus session.'))
            return
        try:
            row=self.store.start_focus_checkpoint(subject_id,self.preferences['focus_minutes']*60)
        except (sqlite3.Error,ValueError,OSError) as exc:
            self.refresh_focus_recovery()
            self.show_notice(self.focus_error(exc))
            return
        self.activate_focus(row,recovered=False)
        if self.refresh_pending:return
        self.show_notice(tr(self, 'Focus session started · {v0}',v0=row['subject_name']))

    def activate_focus(self,row,*,recovered):
        self.focus_run_id=row['id']
        self.session_subject_id=row['subject_id'];self.session_subject_name=row['subject_name']
        if row['subject_id'] is not None:self.selected_subject_id=row['subject_id']
        self.focus_target=row['target_seconds'];self.session_seconds=float(row['elapsed_seconds'])
        self.running_since=None if recovered else time.monotonic()
        self.last_checkpoint=time.monotonic();self.session_open=True;self.session_save_failed=False
        self.recovery_record=None;self.pending_focus_discard=False;self.recovery_panel.grid_remove()
        self.focus_retry_label.configure(text='')
        self.focus_alert.grid_remove()
        self.focus_subject_label.configure(text=tr(self,'Focus subject: {v0}',v0=row['subject_name']))
        remaining=max(0,self.focus_target-int(self.elapsed()))
        self.timer_label.configure(text=tr(self,'{v0:02d}:{v1:02d} · {v2}',v0=remaining//60,v1=remaining%60,v2=tr(self,'Paused' if recovered else 'Focus')))
        self.pause_button.configure(text=tr(self,'Resume' if recovered else 'Pause'),state='normal')
        self.timer_frame.grid();self.start_button.configure(state='disabled');self.subject_picker.configure(state='disabled')
        try:self.navigate('Dashboard')
        except sqlite3.Error:self.defer_refresh()

    def cancel_focus_discard(self):
        self.pending_focus_discard=False
        self.discard_focus_button.configure(text=tr(self,'Discard checkpoint'))
        if self.recovery_record is not None:
            row=self.recovery_record
            self.recovery_status.configure(text=tr(self,'{v0} · saved {v1}s of {v2}s. Recover paused or discard. Time while closed is not counted; another window may still own this session.',v0=row['subject_name'],v1=row['elapsed_seconds'],v2=row['target_seconds']))

    def refresh_focus_recovery(self):
        if self.session_open:return
        self.cancel_focus_discard()
        self.recovery_record=None
        self.recover_focus_button.configure(state='disabled')
        self.discard_focus_button.configure(state='disabled')
        self.start_button.configure(state='disabled')
        try:row=self.store.pending_focus()
        except sqlite3.Error:
            self.recovery_status.configure(text=tr(self,'Could not read saved focus. Retry Refresh; no checkpoint was discarded.'))
            self.recovery_panel.grid();return
        self.recovery_record=row
        if row is None:
            self.recovery_panel.grid_remove();self.start_button.configure(state='normal');return
        self.recover_focus_button.configure(state='normal')
        self.discard_focus_button.configure(state='normal')
        self.cancel_focus_discard()
        self.recovery_panel.grid()

    def recover_focus(self):
        if self.session_open:return
        self.cancel_focus_discard()
        if self.recovery_record is None:self.refresh_focus_recovery();return
        try:row=self.store.claim_focus_checkpoint(self.recovery_record['id'],self.recovery_record['revision'])
        except (sqlite3.Error,ValueError,OSError) as exc:
            self.recovery_status.configure(text=self.focus_error(exc));return
        self.activate_focus(row,recovered=True)
        if self.refresh_pending:return
        self.show_notice(tr(self,'Focus recovered paused. Resume or Finish when ready; app downtime was not counted.'))

    def discard_focus(self):
        if self.session_open:return
        if self.recovery_record is None:self.refresh_focus_recovery();return
        if not self.pending_focus_discard:
            self.pending_focus_discard=True
            self.discard_focus_button.configure(text=tr(self,'Confirm discard'))
            self.recovery_status.configure(text=tr(self,'Discard this saved focus checkpoint? Its uncompleted time will not enter Statistics. Click Confirm discard, or Refresh to cancel.'))
            return
        try:self.store.discard_focus_checkpoint(self.recovery_record['id'],self.recovery_record['revision'])
        except (sqlite3.Error,ValueError,OSError) as exc:
            self.pending_focus_discard=False;self.discard_focus_button.configure(text=tr(self,'Discard checkpoint'))
            self.recovery_status.configure(text=self.focus_error(exc));return
        self.recovery_record=None;self.refresh_focus_recovery()
        self.show_notice(tr(self,'Focus checkpoint discarded. Completed study history is unchanged.'))

    def show_focus_retry(self):
        try:self.navigate('Dashboard')
        except sqlite3.Error:self.defer_refresh()
        self.show_notice(SAVE_RETRY_NOTICE)
        self.timer_frame.update_idletasks()
        self.scroll._parent_canvas.yview_moveto(0)

    def focus_save_failure(self):
        self.pause_button.configure(state='disabled')
        self.focus_retry_label.configure(text=tr(self,SAVE_RETRY_NOTICE))
        self.focus_alert.configure(text='!' if self.collapsed else tr(self,'Focus needs saving'))
        self.focus_alert.grid(row=2,column=0,sticky='ew',padx=12,pady=(8,0))
        self.show_notice(SAVE_RETRY_NOTICE)

    def checkpoint_focus(self):
        elapsed=min(int(self.elapsed()),self.focus_target)
        try:self.store.checkpoint_focus(self.focus_run_id,elapsed)
        except (sqlite3.Error,ValueError):
            self.session_seconds=self.elapsed();self.running_since=None;self.session_save_failed=True
            self.focus_save_failure()
            return False
        self.last_checkpoint=time.monotonic();return True

    def pause_focus(self):
        if self.running_since is not None:
            self.session_seconds=self.elapsed();self.running_since=None
            self.pause_button.configure(text=tr(self,'Resume'))
            self.checkpoint_focus()
        elif self.session_save_failed:
            self.show_notice(SAVE_RETRY_NOTICE)
        elif self.session_open:
            if int(self.session_seconds)>=self.focus_target:self.finish_focus();return
            self.running_since=time.monotonic();self.last_checkpoint=time.monotonic()
            self.pause_button.configure(text=tr(self,'Pause'))

    def finish_focus(self):
        if not self.session_open:
            return False
        elapsed = min(int(self.elapsed()), self.focus_target)
        try:
            result=self.store.add_session(elapsed, self.session_subject_id, self.session_subject_name,focus_run_id=self.focus_run_id)
            elapsed=result["seconds"]
        except (sqlite3.Error,ValueError):
            self.session_seconds = self.elapsed()
            self.running_since = None
            self.session_save_failed = True
            self.focus_save_failure()
            return False
        self.focus_run_id = None
        self.running_since = None
        self.session_seconds = 0.0
        self.session_open = False
        self.session_save_failed = False
        self.session_subject_id = None
        self.session_subject_name = None
        self.timer_frame.grid_remove()
        self.focus_alert.grid_remove()
        self.focus_retry_label.configure(text="")
        self.start_button.configure(state="normal")
        if elapsed:
            try:
                self.store.set_task("focus", True)
                self.task_vars["focus"].set(True)
            except sqlite3.Error:
                pass  # The session itself has already been committed successfully.
        self.show_notice(tr(self, 'Session saved · {v0}m {v1:02d}s of focused study.', v0=elapsed // 60, v1=elapsed % 60))
        try:
            self.refresh_data()
        except sqlite3.Error:
            self.defer_refresh()
        else:
            self.refresh_pending = False
        return True

    def defer_refresh(self):
        self.refresh_pending = True
        # A refresh retry must never obscure an unsaved session's required action.
        self.show_notice(SAVE_RETRY_NOTICE if self.session_save_failed else REFRESH_RETRY_NOTICE)

    def update_metrics(self):
        summary = self.store.summary()
        minutes = summary["seconds"] // 60
        values = [tr(self,'{v0}h {v1:02d}m',v0=minutes//60,v1=minutes%60), str(summary["sessions"]),
                  tr(self,'{v0} days',v0=summary['streak']), str(summary["subjects"])]
        for label, value in zip(self.metric_values, values):
            label.configure(text=value)
        self.saved_today_seconds = summary["today_seconds"]
        self.update_goal()

    def update_goal(self):
        goal = self.preferences["daily_goal_minutes"]
        self.goal.configure(text=tr(self, '{v0} / {v1} min', v0=self.saved_today_seconds // 60, v1=goal))
        self.goal_bar.set(min(self.saved_today_seconds / (goal * 60), 1))

    def validate_preferences_change(self, fields):
        tutor = self.tutor_page
        if any(fields[key] != self.preferences[key] for key in AI_KEYS) and tutor.task is not None:
            raise ValueError("Wait for or stop the Tutor request before changing AI preferences.")
        if (fields["ollama_endpoint"] != self.preferences["ollama_endpoint"] and tutor.turns
                and fields["ollama_endpoint"] != (tutor.conversation_endpoint or tutor.connected_endpoint)):
            raise ValueError("Start a New chat in AI Tutor before saving a different server.")

    def apply_preferences(self, saved):
        previous = self.preferences
        self.preferences = dict(saved)
        if not self.session_open:
            self.focus_target = saved["focus_minutes"] * 60
        self.update_goal()
        self.tutor_page.apply_preferences(saved, previous)
        if saved["appearance_mode"] != previous["appearance_mode"]:
            apply_appearance(saved["appearance_mode"])

    def tick(self):
        try:
            if self.data_restoring:
                return
            if self.session_open:
                remaining = max(0, self.focus_target - int(self.elapsed()))
                self.timer_label.configure(text=tr(self, '{v0:02d}:{v1:02d} · {v2}', v0=remaining // 60, v1=remaining % 60, v2=tr(self,'Paused' if self.running_since is None else 'Focus')))
                if remaining == 0 and self.running_since is not None:
                    self.finish_focus()
                elif self.running_since is not None and time.monotonic()-self.last_checkpoint>=5:
                    self.checkpoint_focus()
            today = date.today()
            day_changed = today != self.active_day
            if day_changed or self.refresh_pending:
                # Daily state changes only after successful reads. Post-save refresh
                # retries are independent of the date and never repeat the write.
                retrying = self.refresh_pending
                tasks = {key: self.store.task(key) for key in self.task_vars} if day_changed else {}
                self.refresh_data()
                for key, value in tasks.items():
                    self.task_vars[key].set(value)
                self.date_label.configure(text=self.display_date(today))
                self.active_day = today
                self.refresh_pending = False
                if retrying and not self.session_save_failed:
                    self.show_notice(tr(self, 'Dashboard refreshed.'))
        except sqlite3.Error:
            self.defer_refresh()
        finally:
            self.after(250, self.tick)

    def close(self):
        if self.settings_page.schedule.busy:
            self.backup_notice.configure(text=tr(self,'Daily backup is running. Please wait before closing.'))
            self.backup_notice.grid(row=1,column=0,columnspan=2,sticky='ew',padx=12,pady=6)
            return
        if self.question_bank.importer.saving or self.flashcard_page.importer.saving:
            (self.flashcard_page.importer if self.flashcard_page.importer.saving else self.question_bank.importer).status.configure(text=tr(self, 'Wait for the CSV import to finish before closing.'))
            return
        if self.settings_page.backups.busy:
            self.settings_page.backups.status.configure(text=tr(self, 'Wait for the database operation to finish before closing.'))
            return
        self.settings_page.backups.cancel_pending()
        if self.session_open and not self.finish_focus():
            self.show_focus_retry()
            return
        if not self.tutor_page.prepare_close():
            self.navigate("AI Tutor")
            return
        self.tutor_page.shutdown()
        self.store.close()
        self.destroy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SOSkúška native desktop Dashboard")
    parser.add_argument("--data", type=Path, help="Override the local SQLite database path")
    args = parser.parse_args()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    try:
        Dashboard(args.data).mainloop()
    except (sqlite3.Error, ValueError) as exc:
        report_startup_error(exc)
        raise SystemExit(1) from None
