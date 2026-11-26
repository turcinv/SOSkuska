"""Saved multiple-choice practice and result review on the Tk main thread."""
from theme import COLORS as C
from localization_widgets import LocalizedOptionMenu
from localization import tr
import sqlite3
from datetime import datetime

import customtkinter as ctk
from content import DIFFICULTIES
from question_explanation import MODES, read_prompt
from practice import MissingPracticeError, expired, seconds_left, utc_now


class PracticePage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.app = app
        self.active_id = None
        self.attempt = None
        self.items = []
        self.finishing = False
        self.subject_ids = {}
        self.topic_ids = {"All topics": "all", "No topic": None}
        self.pending_action = None
        self.result_id = None
        self.explanation_identity = None
        self.explanation_panel = None
        self.history_filters = (None, "", "")
        self.history_page = 0
        self.history_subjects = {tr(self.app, 'All subjects'): None}
        self.grid_columnconfigure(0, weight=1)
        app.label(self, tr(self.app, 'Practice Tests'), 28, bold=True).grid(row=0, column=0, sticky="w")
        self.status = app.label(self, tr(self.app, 'Answers are saved on this device. Results appear after submission.'), 13, "secondary", wraplength=650)
        self.status.grid(row=1, column=0, sticky="ew", pady=(6, 18))
        self.setup = app.frame(self)
        self.setup.grid(row=3, column=0, sticky="ew")
        self.setup.grid_columnconfigure(0, weight=1)
        self.active_panel = app.frame(self.setup, card=True)
        self.active_panel.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self.active_panel.grid_columnconfigure(0, weight=1)
        self.active_label = app.label(self.active_panel, "", 14, wraplength=600)
        self.active_label.grid(row=0, column=0, sticky="ew", padx=18, pady=14)
        actions = app.frame(self.active_panel)
        actions.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 14))
        app.button(actions, tr(self.app, 'Resume test'), self.resume, primary=True, width=125).pack(side="left", padx=(0, 8))
        app.button(actions, tr(self.app, 'Discard test'), lambda: self.ask_action("discard"), width=125).pack(side="left")
        self.subject = ctk.StringVar()
        self.topic = ctk.StringVar(value="All topics")
        self.difficulty = ctk.StringVar(value="All difficulties")
        self.count = ctk.StringVar(value="1")
        self.limit = ctk.StringVar(value="Untimed")
        self.config_panel = app.frame(self.setup, card=True)
        self.config_panel.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.config_panel.grid_columnconfigure((0, 1), weight=1, uniform="config")
        self.subject_menu = self.selector(self.setup, 1, "Subject", self.subject, ["Add a subject first"], self.subject_changed)
        self.topic_menu = self.selector(self.setup, 2, "Topic", self.topic, list(self.topic_ids), self.update_available)
        self.selector(self.setup, 3, "Difficulty", self.difficulty, ["All difficulties", *DIFFICULTIES], self.update_available)
        self.count_menu = self.selector(self.setup, 4, "Questions (up to 100)", self.count, ["1"])
        self.selector(self.setup, 5, "Time limit (continues while the app is closed)", self.limit,
                      ["Untimed", "5 minutes", "10 minutes", "15 minutes", "30 minutes", "60 minutes"])
        self.available = app.label(self.setup, "", 13, "secondary", wraplength=650)
        self.available.grid(row=12, column=0, sticky="ew", pady=(4, 12))
        actions = app.frame(self.setup)
        actions.grid(row=13, column=0, sticky="w", pady=(0, 24))
        self.start_button = app.button(actions, tr(self.app, 'Start test'), self.start, primary=True, width=125)
        self.start_button.pack(side="left", padx=(0, 8))
        app.button(actions, tr(self.app, 'Refresh subjects'), self.show_config, width=155).pack(side="left")
        app.label(self.setup, tr(self.app, 'Completed tests'), 18, bold=True).grid(row=14, column=0, sticky="w", pady=(0, 12))
        filters = app.frame(self.setup, card=True)
        filters.grid(row=15, column=0, sticky="ew", pady=(0, 12))
        filters.grid_columnconfigure(0, weight=1)
        app.label(filters, tr(self.app, 'Subject name saved with the test'), 13, "secondary").grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        self.history_subject = ctk.StringVar(value=tr(self.app, 'All subjects'))
        self.history_subject_menu = LocalizedOptionMenu(filters, owner=app, variable=self.history_subject,
            values=[tr(self.app, 'All subjects')], translate_values=False, height=38, font=app.font(), dynamic_resizing=False)
        self.history_subject_menu.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))
        self.history_date_entries = []
        for row, text in enumerate(('Completed from (YYYY-MM-DD, optional)', 'Completed through (YYYY-MM-DD, optional)'), 2):
            app.label(filters, tr(self.app, text), 13, "secondary").grid(row=row*2-2, column=0, sticky="w", padx=16, pady=(0, 4))
            entry = ctk.CTkEntry(filters, height=38, font=app.font(), placeholder_text_color=C["secondary"])
            entry.grid(row=row*2-1, column=0, sticky="ew", padx=16, pady=(0, 12))
            entry.bind('<Return>', lambda _event: self.apply_history())
            self.history_date_entries.append(entry)
        actions = app.frame(filters)
        actions.grid(row=6, column=0, sticky="w", padx=16, pady=(0, 14))
        self.history_apply = app.button(actions, tr(self.app, 'Apply filters'), self.apply_history, primary=True, width=135)
        self.history_apply.pack(side="left", padx=(0, 8))
        self.history_reset = app.button(actions, tr(self.app, 'Reset filters'), self.reset_history, width=135)
        self.history_reset.pack(side="left")
        self.history_status = app.label(self.setup, "", 13, "secondary", wraplength=650)
        self.history_status.grid(row=16, column=0, sticky="ew", pady=(0, 12))
        pagination = app.frame(self.setup)
        pagination.grid(row=17, column=0, sticky="w", pady=(0, 14))
        self.history_previous = app.button(pagination, tr(self.app, 'Previous'), lambda: self.move_history(-1), width=110)
        self.history_previous.pack(side="left", padx=(0, 8))
        self.history_next = app.button(pagination, tr(self.app, 'Next'), lambda: self.move_history(1), width=110)
        self.history_next.pack(side="left")
        self.history_previous.configure(state="disabled")
        self.history_next.configure(state="disabled")
        self.history = app.frame(self.setup)
        self.history.grid(row=18, column=0, sticky="ew")
        self.history.grid_columnconfigure(0, weight=1)

        self.run = app.frame(self)
        self.run.grid(row=4, column=0, sticky="ew")
        self.run.grid_columnconfigure(0, weight=1)
        self.history_button = app.button(self.run, tr(self.app, '← Test setup / history'), self.show_config, width=195)
        self.history_button.grid(row=0, column=0, sticky="w", pady=(0, 14))
        self.run_header = app.frame(self.run, card=True)
        self.run_header.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        self.run_header.grid_columnconfigure(0, weight=1)
        self.progress = app.label(self.run_header, "", 17, bold=True, wraplength=650)
        self.progress.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 4))
        self.timer = app.label(self.run_header, "", 14, "hover", bold=True, wraplength=650)
        self.timer.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 12))
        self.answer_progress = ctk.CTkProgressBar(self.run_header, height=6,
            fg_color=C["raised"], progress_color=C["accent"])
        self.answer_progress.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 16))
        question = app.frame(self.run, card=True)
        question.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        question.grid_columnconfigure(0, weight=1)
        self.prompt = app.label(question, "", 21, bold=True, wraplength=650)
        self.prompt.grid(row=0, column=0, sticky="ew", padx=18, pady=18)
        self.choice = ctk.IntVar(value=-1)
        self.radios, self.answer_labels, self.answer_rows = [], [], []
        for index, letter in enumerate("ABCD"):
            row = app.frame(self.run, card=True)
            row.grid(row=3+index, column=0, sticky="ew", pady=(0, 10))
            row.grid_columnconfigure(1, weight=1)
            radio = ctk.CTkRadioButton(row, text=letter, variable=self.choice, value=index,
                command=self.choose, font=app.font(), width=50, text_color=C["text"],
                fg_color=C["hover"], hover_color=C["hover"], border_color=C["secondary"])
            radio.grid(row=0, column=0, padx=(16, 8), pady=16)
            label = app.label(row, "", 14, wraplength=550)
            label.grid(row=0, column=1, sticky="ew", padx=(0, 18), pady=16)
            label.bind("<Button-1>", lambda _event, i=index: self.click_answer(i))
            row.bind("<Button-1>", lambda _event, i=index: self.click_answer(i))
            row.bind("<Configure>", lambda event, label=label: label.configure(
                wraplength=max(200, app.scroll.logical_pixels(event.width)-105)), add="+")
            self.radios.append(radio)
            self.answer_labels.append(label)
            self.answer_rows.append(row)
        navigation = app.frame(self.run)
        navigation.grid(row=7, column=0, sticky="ew", pady=(8, 16))
        navigation.grid_columnconfigure(3, weight=1)
        self.previous_button = app.button(navigation, tr(self.app, 'Previous'), lambda: self.move(-1), width=105)
        self.previous_button.grid(row=0, column=0, padx=(0, 8))
        self.next_button = app.button(navigation, tr(self.app, 'Next'), lambda: self.move(1), width=105)
        self.next_button.grid(row=0, column=1, padx=(0, 8))
        self.clear_button = app.button(navigation, tr(self.app, 'Clear answer'), lambda: self.click_answer(-1), width=125)
        self.clear_button.grid(row=0, column=2)
        self.finish_button = app.button(navigation, tr(self.app, 'Finish test'), lambda: self.ask_action("finish"), primary=True, width=150)
        self.finish_button.grid(row=0, column=4, padx=(12, 0))

        self.confirm = app.frame(self, card=True)
        self.confirm.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        self.confirm.grid_columnconfigure(0, weight=1)
        self.confirm_text = app.label(self.confirm, "", 14, wraplength=600)
        self.confirm_text.grid(row=0, column=0, sticky="ew", padx=18, pady=14)
        actions = app.frame(self.confirm)
        actions.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 14))
        self.confirm_button = app.button(actions, tr(self.app, 'Confirm'), self.confirm_action, primary=True, width=125)
        self.confirm_button.pack(side="left", padx=(0, 8))
        app.button(actions, tr(self.app, 'Cancel'), self.cancel_action, width=85).pack(side="left")
        self.results = app.frame(self)
        self.results.grid(row=5, column=0, sticky="ew")
        self.results.grid_columnconfigure(0, weight=1)
        self.run.grid_remove()
        self.results.grid_remove()
        self.confirm.grid_remove()
        self.active_panel.grid_remove()
        self.bind("<Configure>", self.reflow_text)
        self.load()
        self.after(250, self.tick)

    def scroll_to_top(self):
        # Timed completion can run while another screen owns the shared canvas.
        if self.app.current_page == "Practice Tests":
            self.app.scroll.scroll_to_top()

    def reflow_text(self, event):
        # CTkFrame binds Configure on its drawing canvas, not the wrapper.
        width = max(250, self.app.scroll.logical_pixels(event.width) - 36)
        for label in (self.prompt, self.progress, self.timer, self.status, self.available,
                      self.active_label, self.confirm_text, self.history_status):
            label.configure(wraplength=width)

    def selector(self, parent, row, text, variable, values, command=None):
        field = self.app.frame(self.config_panel)
        index = row - 1
        field.grid(row=index//2, column=index%2, columnspan=2 if index == 4 else 1,
                   sticky="new", padx=18, pady=(14, 0 if index < 4 else 14))
        field.grid_columnconfigure(0, weight=1)
        label = self.app.label(field, tr(self.app,text), 13, "secondary", wraplength=300)
        label.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        field.bind('<Configure>', lambda event: label.configure(
            wraplength=max(160, self.app.scroll.logical_pixels(event.width))), add='+')
        menu = LocalizedOptionMenu(field,owner=self.app,translate_values=text!="Subject",empty_text="Add a subject first" if text=="Subject" else None, variable=variable, values=values if text!="Subject" else [], command=command,
            dynamic_resizing=False, height=38, font=self.app.font(),
            fg_color=C["raised"], button_color=C["border"])
        menu.grid(row=1, column=0, sticky="ew")
        return menu

    def error(self, exc):
        self.status.configure(text=tr(self.app,tr(self.app, str(exc)) if isinstance(exc, ValueError) else tr(self.app, 'Could not access practice data. Please try again.')))

    def load(self):
        if self.finishing and self.active_id is not None:
            self.finish()
            return
        try:
            attempt = self.app.store.active_practice()
            if attempt:
                self.load_attempt(attempt)
            else:
                self.active_id = None
                self.finishing = False
                self.show_config()
        except (ValueError, sqlite3.Error) as exc:
            self.error(exc)

    def show_config(self):
        self.cancel_explanation()
        try:
            subjects = self.app.store.subjects()
            active = self.app.store.active_practice()
            history = self.read_history()
            items = self.app.store.practice_items(active["id"]) if active else []
            if active:
                self.items = items
                self.attempt = active
                self.active_id = active["id"]
            else:
                self.active_id = None
                self.finishing = False
            selected = self.subject_ids.get(self.subject.get())
            self.subject_ids = {s["name"]: s["id"] for s in subjects}
            self.subject_menu.configure(values=list(self.subject_ids))
            self.subject.set(next((k for k, v in self.subject_ids.items() if v == selected), next(iter(self.subject_ids), "Add a subject first")))
            self.subject_changed()
            self.render_history(history)
            if active:
                self.active_label.configure(text=tr(self.app, 'Unfinished test: {v0} · {v1}/{v2} answered. Resume or discard it before starting another.', v0=active['subject_name'], v1=active['answered'], v2=active['question_count']))
                self.active_panel.grid()
            else:
                self.active_panel.grid_remove()
            self.run.grid_remove()
            self.results.grid_remove()
            self.cancel_action()
            self.setup.grid()
            self.scroll_to_top()
            return True
        except (ValueError, sqlite3.Error) as exc:
            self.error(exc)
            return False

    def read_history(self, filters=None, page=None):
        subject, start, end = self.history_filters if filters is None else filters
        return self.app.store.practice_history_page(subject_name=subject, date_from=start, date_to=end,
            page=self.history_page if page is None else page)

    def render_history(self, report):
        # Preserve an unapplied subject draft across page changes and navigation.
        selected = self.history_subjects.get(self.history_subject.get())
        choices = {tr(self.app, 'All subjects'): None}
        choices.update({tr(self.app, 'Subject: {v0}', v0=name): name for name in report['subjects']})
        self.history_subjects = choices
        self.history_subject_menu.configure(values=list(choices))
        self.history_subject.set(next((label for label, name in choices.items() if name == selected), next(iter(choices))))
        self.history_page = report['page']
        for child in self.history.winfo_children():
            child.destroy()
        if not report['rows']:
            self.app.label(self.history, tr(self.app, 'No completed tests match these filters.'), 14, 'secondary').grid(row=0, column=0, sticky='w')
        for row, attempt in enumerate(report['rows']):
            card = self.app.frame(self.history, card=True)
            card.grid(row=row, column=0, sticky='ew', pady=(0, 12))
            card.grid_columnconfigure(0, weight=1)
            text = tr(self.app, '{v0} · {v1}/{v2} correct · {v3}', v0=attempt['subject_name'],
                v1=attempt['correct'], v2=attempt['question_count'], v3=self.local_time(attempt['completed_at']))
            label = self.app.label(card, text, 16, bold=True, wraplength=600)
            label.grid(row=0, column=0, sticky='ew', padx=18, pady=16)
            card.bind('<Configure>', lambda event, label=label: label.configure(wraplength=max(200,self.app.scroll.logical_pixels(event.width)-36)), add='+')
            self.app.button(card, tr(self.app, 'View result'), lambda aid=attempt['id']: self.view_result(aid), width=115).grid(row=1, column=0, sticky='w', padx=18, pady=(0, 14))
        self.history_status.configure(text=tr(self.app, 'Page {v0} / {v1} · {v2} completed tests',
            v0=report['page']+1, v1=report['pages'], v2=report['total']))
        self.history_previous.configure(state='normal' if report['page'] else 'disabled')
        self.history_next.configure(state='normal' if report['page']+1 < report['pages'] else 'disabled')

    def refresh_history(self, filters, page):
        try:
            report = self.read_history(filters, page)
        except (ValueError, sqlite3.Error) as exc:
            self.history_status.configure(text=tr(self.app, str(exc)) if isinstance(exc, ValueError) else
                tr(self.app, 'Could not load practice history. Previous results are kept; retry the filters or page.'))
            return False
        self.history_filters = filters
        self.render_history(report)
        return True

    def apply_history(self):
        if self.history_subject.get() not in self.history_subjects:
            return
        filters = (self.history_subjects[self.history_subject.get()],
            *(entry.get().strip() for entry in self.history_date_entries))
        self.refresh_history(filters, 0)

    def reset_history(self):
        if self.refresh_history((None, '', ''), 0):
            self.history_subject.set(next(iter(self.history_subjects)))
            for entry in self.history_date_entries:
                entry.delete(0, 'end')

    def move_history(self, offset):
        self.refresh_history(self.history_filters, max(0, self.history_page + offset))

    @staticmethod
    def local_time(value):
        return datetime.fromisoformat(value).astimezone().strftime("%Y-%m-%d %H:%M")

    def subject_changed(self, _value=None):
        self.start_button.configure(state="disabled")
        try:
            sid = self.subject_ids.get(self.subject.get())
            topics = self.app.store.topics(sid) if sid is not None else []
            self.topic_ids = {"All topics": "all", "No topic": None,
                              **{f'Topic: {t["name"]}': t["id"] for t in topics}}
            self.topic_menu.configure(values=list(self.topic_ids))
            self.topic.set("All topics")
            self.update_available()
        except (ValueError, sqlite3.Error) as exc:
            self.error(exc)

    def update_available(self, _value=None):
        try:
            sid = self.subject_ids.get(self.subject.get())
            pool = self.app.store.practice_pool(sid, self.topic_ids.get(self.topic.get(), "all"), self.filter_difficulty()) if sid is not None else []
            maximum = min(100, len(pool))
            values = [str(i) for i in range(1, maximum+1)] or ["0"]
            self.count_menu.configure(values=values)
            if self.count.get() not in values:
                self.count.set(str(min(10, maximum)))
            self.available.configure(text=tr(self.app, '{v0} matching questions. Add content through My Subjects → Questions.', v0=len(pool)) if not pool else tr(self.app, '{v0} matching questions. Questions will be randomly selected without repeats.', v0=len(pool)))
            self.start_button.configure(state="normal" if pool and self.active_id is None else "disabled")
        except (ValueError, sqlite3.Error) as exc:
            self.start_button.configure(state="disabled")
            self.error(exc)

    def filter_difficulty(self):
        return None if self.difficulty.get() == "All difficulties" else self.difficulty.get()

    def start(self):
        try:
            minutes = None if self.limit.get() == "Untimed" else int(self.limit.get().split()[0])
            aid = self.app.store.start_practice(self.subject_ids.get(self.subject.get()), int(self.count.get()),
                     self.topic_ids.get(self.topic.get(), "all"), self.filter_difficulty(), minutes)
            self.load_attempt(self.app.store.practice_attempt(aid))
        except (ValueError, sqlite3.Error) as exc:
            self.error(exc)

    def resume(self):
        self.load()

    def load_attempt(self, attempt):
        if attempt is None:
            raise ValueError("This test no longer exists. Refresh practice data.")
        items = self.app.store.practice_items(attempt["id"])
        if len(items) != attempt["question_count"]:
            raise ValueError("This test changed in another window. Refresh practice data.")
        self.attempt = attempt
        self.items = items
        self.active_id = attempt["id"]
        self.finishing = False
        self.setup.grid_remove()
        self.results.grid_remove()
        self.cancel_action()
        self.run.grid()
        self.show_question()
        self.scroll_to_top()
        self.status.configure(text=tr(self.app, 'Choose an answer to save it. You can change it before submitting.'))
        if expired(self.attempt["deadline_at"], utc_now()):
            self.finish()

    def show_question(self):
        item = self.items[self.attempt["current_index"]]
        self.choice.set(item["selected_option"] if item["selected_option"] is not None else -1)
        self.prompt.configure(text=item["prompt"])
        for label, field in zip(self.answer_labels, ["option_a", "option_b", "option_c", "option_d"]):
            label.configure(text=item[field])
        self.refresh_answer_selection()
        self.update_progress()
        self.set_controls(not self.finishing and not expired(self.attempt["deadline_at"], utc_now()))

    def refresh_answer_selection(self):
        selected = self.items[self.attempt["current_index"]]["selected_option"]
        for index, (row, radio, label) in enumerate(zip(self.answer_rows, self.radios, self.answer_labels)):
            active = index == selected
            row.configure(fg_color=C["selected"] if active else C["card"],
                          border_color=C["hover"] if active else C["border"],
                          border_width=2 if active else 1)
            radio.configure(text_color=C["hover"] if active else C["text"],
                            font=self.app.font(14, active))
            label.configure(text_color=C["hover"] if active else C["text"],
                            font=self.app.font(14, active))

    def update_progress(self):
        answered = sum(q["selected_option"] is not None for q in self.items)
        self.answer_progress.set(answered / len(self.items))
        self.progress.configure(text=tr(self.app, '{v0} · Question {v1}/{v2} · {v3} answered', v0=self.attempt['subject_name'], v1=self.attempt['current_index'] + 1, v2=len(self.items), v3=answered))

    def set_controls(self, enabled):
        state = "normal" if enabled else "disabled"
        for control in [*self.radios, self.clear_button, self.finish_button]:
            control.configure(state=state)
        self.previous_button.configure(state=state if self.attempt["current_index"] > 0 else "disabled")
        self.next_button.configure(state=state if self.attempt["current_index"] < len(self.items)-1 else "disabled")

    def can_answer(self):
        return (self.active_id is not None and not self.finishing
                and self.app.current_page == "Practice Tests"
                and self.run.winfo_manager() == "grid"
                and self.radios[0].cget("state") == "normal")

    def click_answer(self, index):
        if not self.can_answer():
            return
        self.choice.set(index)
        self.choose()

    def choose(self):
        if not self.can_answer():
            if self.attempt is not None and self.items:
                item = self.items[self.attempt["current_index"]]
                self.choice.set(item["selected_option"] if item["selected_option"] is not None else -1)
            return
        item = self.items[self.attempt["current_index"]]
        value = self.choice.get()
        try:
            self.app.store.save_practice_answer(self.active_id, item["position"], None if value == -1 else value)
        except (ValueError, sqlite3.Error) as exc:
            self.choice.set(item["selected_option"] if item["selected_option"] is not None else -1)
            self.refresh_answer_selection()
            self.error(exc)
            return
        item["selected_option"] = None if value == -1 else value
        self.refresh_answer_selection()
        self.cancel_action()
        self.update_progress()
        self.status.configure(text=tr(self.app, 'Answer saved on this device.'))

    def move(self, offset):
        if self.finishing or self.active_id is None:
            return
        position = self.attempt["current_index"] + offset
        try:
            self.app.store.set_practice_position(self.active_id, position)
        except (ValueError, sqlite3.Error) as exc:
            self.error(exc)
            return
        self.attempt["current_index"] = position
        self.cancel_action()
        self.show_question()
        self.scroll_to_top()

    def ask_action(self, action):
        if self.active_id is None or self.finishing:
            return
        self.pending_action = action
        unanswered = len(self.items) - sum(q["selected_option"] is not None for q in self.items)
        text = "Discard the unfinished test and its answers? This cannot be undone." if action == "discard" else f"Submit this test? {unanswered} questions are unanswered and will count as incorrect. Answers cannot be changed after submission."
        self.confirm_text.configure(text=tr(self.app,text))
        self.confirm.grid()
        self.scroll_to_top()

    def cancel_action(self):
        self.pending_action = None
        self.confirm.grid_remove()

    def confirm_action(self):
        if self.pending_action == "finish":
            self.finish()
        elif self.pending_action == "discard":
            try:
                if not self.app.store.discard_practice(self.active_id):
                    self.finish()  # The deadline saved this attempt instead.
                    return
                self.active_id = None
                self.finishing = False
                self.status.configure(text=tr(self.app, 'Unfinished test discarded.'))
                self.show_config()
            except MissingPracticeError:
                self.recover_missing_attempt()
            except (ValueError, sqlite3.Error) as exc:
                self.error(exc)

    def recover_missing_attempt(self):
        # Missing data is terminal, unlike a locked/failed read. Stop timer
        # retries before refreshing so even a failed setup read can be retried.
        self.active_id = None
        self.attempt = None
        self.items = []
        self.finishing = False
        self.cancel_action()
        self.run.grid_remove()
        self.results.grid_remove()
        self.active_panel.grid_remove()
        self.start_button.configure(state="disabled")
        self.setup.grid()
        if self.show_config():
            self.status.configure(text=tr(self.app, 'This test was discarded in another window. Practice setup refreshed.'))

    def finish(self):
        if self.active_id is None:
            return
        self.finishing = True
        self.set_controls(False)
        try:
            self.app.store.complete_practice(self.active_id)
            self.render_result(self.active_id)
        except MissingPracticeError:
            self.recover_missing_attempt()
        except (ValueError, sqlite3.Error) as exc:
            self.status.configure(text=tr(self.app,tr(self.app, str(exc)) if isinstance(exc, ValueError) else tr(self.app, 'Could not finish or load the result. Saved answers are kept; retrying automatically.')))

    def view_result(self, attempt_id):
        try:
            self.render_result(attempt_id)
        except (ValueError, sqlite3.Error) as exc:
            self.error(exc)

    def render_result(self, attempt_id):
        # Complete all reads before replacing the current screen. A retry can then
        # load a committed result without performing another submission.
        attempt = self.app.store.practice_attempt(attempt_id)
        items = self.app.store.practice_items(attempt_id)
        if attempt is None:
            raise MissingPracticeError("This test no longer exists.")
        if attempt["status"] != "completed":
            raise ValueError("This test has not been completed.")
        self.cancel_explanation()
        self.result_id = attempt_id
        for child in self.results.winfo_children():
            child.destroy()
        self.app.button(self.results, tr(self.app, '← Test setup / history'), self.show_config, width=195).grid(row=0, column=0, sticky="w", pady=(0, 16))
        summary = self.app.frame(self.results, card=True)
        summary.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        summary.grid_columnconfigure(0, weight=1)
        score = round(100 * attempt["correct"] / attempt["question_count"], 1)
        self.app.label(summary, tr(self.app, '{v0} · {v1}/{v2} correct · {v3}%', v0=attempt['subject_name'], v1=attempt['correct'], v2=attempt['question_count'], v3=score), 24, bold=True, wraplength=650).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 6))
        self.app.label(summary, tr(self.app, 'Completed {v0} · {v1} answered · {v2} unanswered', v0=self.local_time(attempt['completed_at']), v1=attempt['answered'], v2=attempt['question_count'] - attempt['answered']), 13, "secondary", wraplength=650).grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 16))
        summary.bind('<Configure>', lambda event: [label.configure(
            wraplength=max(200, self.app.scroll.logical_pixels(event.width)-36))
            for label in summary.winfo_children() if isinstance(label, ctk.CTkLabel)], add='+')
        for index, item in enumerate(items):
            card = self.app.frame(self.results, card=True)
            card.grid(row=index+3, column=0, sticky="ew", pady=(0, 14))
            card.grid_columnconfigure(0, weight=1)
            selected = item["selected_option"]
            fields = ["option_a", "option_b", "option_c", "option_d"]
            yours = tr(self.app,'Unanswered') if selected is None else f'{"ABCD"[selected]} · {item[fields[selected]]}'
            correct = item["correct_option"]
            state = "Correct" if selected == correct else ("Unanswered" if selected is None else "Incorrect")
            texts = [f'{index+1}. {item["prompt"]}', tr(self.app,'{v0} · {v1} · {v2}',v0=tr(self.app,state),v1=tr(self.app,item['difficulty']),v2=item['topic_name'] or tr(self.app,'No topic')),
                     tr(self.app,'Your answer: {v0}',v0=yours), tr(self.app,'Correct answer: {v0} · {v1}',v0='ABCD'[correct],v1=item[fields[correct]])]
            if item["explanation"]:
                texts.append(tr(self.app, 'Explanation: {v0}', v0=item['explanation']))
            labels = []
            for row, text in enumerate(texts):
                label = self.app.label(card, text, 14, bold=row == 0, wraplength=600)
                label.grid(row=row, column=0, sticky="ew", padx=18, pady=(14 if row == 0 else 0, 12))
                labels.append(label)
            self.app.button(card, tr(self.app, 'Explain this question'),
                lambda aid=attempt_id, pos=item['position']: self.explain_question(aid, pos),
                width=210).grid(row=len(texts), column=0, sticky="w", padx=18, pady=(0, 14))
            card.bind("<Configure>", lambda event, labels=labels: [label.configure(wraplength=max(200, self.app.scroll.logical_pixels(event.width)-36)) for label in labels], add="+")
        if self.active_id == attempt_id:
            self.active_id = None
            self.finishing = False
        self.setup.grid_remove()
        self.run.grid_remove()
        self.cancel_action()
        self.results.grid()
        self.scroll_to_top()
        self.status.configure(text=tr(self.app, 'Result saved. Questions and explanations below are snapshots from this test.'))

    def result_visible(self, attempt_id):
        return (self.app.current_page == "Practice Tests" and bool(self.results.grid_info())
                and self.result_id == attempt_id and not self.app.data_restoring)

    def cancel_explanation(self):
        self.explanation_identity = None
        if self.explanation_panel is not None:
            self.explanation_panel.destroy()
            self.explanation_panel = None

    def explain_question(self, attempt_id, position, mode='Explain answer'):
        if not self.result_visible(attempt_id) or mode not in MODES:
            return
        self.cancel_explanation()
        panel = self.explanation_panel = self.app.frame(self.results, card=True)
        panel.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        panel.grid_columnconfigure(0, weight=1)
        privacy = 'Preview only. Hint mode shares the question and four choices, without your answer, the stored answer key or explanation. Only Send shares this prompt with the selected Ollama server. AI may still reveal an answer.' if mode == 'Give me a hint' else 'Preview only. This question, all choices, your answer, the stored answer key and explanation will be shared with the selected Ollama server only after Send. AI may be wrong.'
        message = self.app.label(panel, tr(self.app, privacy), 13, wraplength=600)
        message.grid(row=0, column=0, sticky="ew", padx=18, pady=14)
        self.explanation_feedback = self.app.label(panel, "", 13, wraplength=600)
        self.explanation_feedback.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 14))
        panel.bind('<Configure>', lambda event: [label.configure(wraplength=max(200,
            self.app.scroll.logical_pixels(event.width)-36)) for label in (message, self.explanation_feedback)], add='+')
        selector = self.app.frame(panel)
        selector.grid(row=1, column=0, sticky='ew', padx=18)
        selector.grid_columnconfigure(0, weight=1)
        self.app.label(selector, tr(self.app, 'Study mode'), 13).grid(row=0, column=0, sticky='w', pady=(0, 6))
        choice = ctk.StringVar(master=selector, value=mode)
        self.explanation_mode_menu = LocalizedOptionMenu(selector, owner=self.app, variable=choice,
            values=list(MODES), font=self.app.font(), height=38, dynamic_resizing=False,
            command=lambda value: self.change_explanation_mode(panel, attempt_id, position, value))
        self.explanation_mode_menu.grid(row=1, column=0, sticky='ew', pady=(0, 12))
        actions = self.explanation_actions = self.app.frame(panel)
        actions.grid(row=3, column=0, sticky="w", padx=18, pady=14)
        try:
            prompt = read_prompt(self.app.store, attempt_id, position, mode=mode)
        except (ValueError, sqlite3.Error) as exc:
            self.explanation_feedback.configure(text=tr(self.app, str(exc)) if isinstance(exc, ValueError)
                else tr(self.app, 'Could not read the saved question. Nothing was sent. Reopen the preview to retry.'))
        else:
            self.explanation_identity = (attempt_id, position, prompt, mode)
            preview = ctk.CTkTextbox(panel, height=230, font=self.app.font(), wrap='word',
                border_width=1, border_color=C['border'])
            preview.insert('1.0', prompt)
            preview.configure(state='disabled')
            preview.grid(row=2, column=0, sticky='ew', padx=18)
            self.app.button(actions, tr(self.app, 'Prepare in Tutor'),
                lambda identity=self.explanation_identity: self.prepare_explanation(identity),
                primary=True, width=180).pack(side='left', padx=(0, 8))
        self.app.button(actions, tr(self.app, 'Cancel'), self.cancel_explanation, width=85).pack(side='left')
        self.scroll_to_top()

    def change_explanation_mode(self, panel, attempt_id, position, mode):
        if self.explanation_panel is panel and self.result_visible(attempt_id) and mode in MODES:
            self.explain_question(attempt_id, position, mode)

    def prepare_explanation(self, identity):
        if identity is not self.explanation_identity or identity is None or not self.result_visible(identity[0]):
            return
        try:
            prompt = read_prompt(self.app.store, identity[0], identity[1], mode=identity[3])
            if prompt != identity[2]:
                raise ValueError('This completed question is no longer available. Reopen the result and retry.')
        except (ValueError, sqlite3.Error) as exc:
            self.explanation_feedback.configure(text=tr(self.app, str(exc)) if isinstance(exc, ValueError)
                else tr(self.app, 'Could not read the saved question. Nothing was sent. Reopen the preview to retry.'))
            return
        if not self.app.tutor_page.can_prepare_question():
            self.explanation_feedback.configure(text=tr(self.app, 'Tutor has existing work or a pending action. Finish it or explicitly start a New chat with an empty prompt, then retry. Your work is kept.'))
            return
        if self.app.question_bank.importer.saving or self.app.flashcard_page.importer.saving:
            return
        self.app.navigate('AI Tutor')
        if self.app.current_page == 'AI Tutor':
            self.app.tutor_page.prepare_question_draft(prompt)

    def tick(self):
        try:
            if self.app.data_restoring:
                return
            if self.active_id is not None:
                remaining = seconds_left(self.attempt["deadline_at"], utc_now())
                self.timer.configure(text=tr(self.app, 'Untimed · answers saved as you choose') if remaining is None else tr(self.app, 'Time left · {v0:02d}:{v1:02d}', v0=remaining // 60, v1=remaining % 60))
                if self.finishing or remaining == 0:
                    self.finish()
        finally:
            self.after(250, self.tick)
