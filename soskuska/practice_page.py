"""Saved multiple-choice practice and result review on the Tk main thread."""
from localization_widgets import LocalizedOptionMenu
from localization import tr
import sqlite3
from datetime import datetime

import customtkinter as ctk
from content import DIFFICULTIES
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
        app.label(self.setup, tr(self.app, 'Completed tests · most recent 20'), 18, bold=True).grid(row=14, column=0, sticky="w", pady=(0, 12))
        self.history = app.frame(self.setup)
        self.history.grid(row=15, column=0, sticky="ew")
        self.history.grid_columnconfigure(0, weight=1)

        self.run = app.frame(self)
        self.run.grid(row=4, column=0, sticky="ew")
        self.run.grid_columnconfigure(0, weight=1)
        app.button(self.run, tr(self.app, '← Test setup / history'), self.show_config, width=195).grid(row=0, column=0, sticky="w", pady=(0, 16))
        self.progress = app.label(self.run, "", 16, bold=True, wraplength=650)
        self.progress.grid(row=1, column=0, sticky="ew")
        self.timer = app.label(self.run, "", 14, "hover")
        self.timer.grid(row=2, column=0, sticky="w", pady=(6, 16))
        self.prompt = app.label(self.run, "", 20, bold=True, wraplength=650)
        self.prompt.grid(row=3, column=0, sticky="ew", pady=(0, 18))
        self.choice = ctk.IntVar(value=-1)
        self.radios = []
        self.answer_labels = []
        for index, letter in enumerate("ABCD"):
            row = app.frame(self.run, card=True)
            row.grid(row=4+index, column=0, sticky="ew", pady=(0, 10))
            row.grid_columnconfigure(1, weight=1)
            radio = ctk.CTkRadioButton(row, text=letter, variable=self.choice, value=index,
                                       command=self.choose, font=app.font(), width=50)
            radio.grid(row=0, column=0, padx=(16, 8), pady=16)
            label = app.label(row, "", 14, wraplength=550)
            label.grid(row=0, column=1, sticky="ew", padx=(0, 18), pady=16)
            label.bind("<Button-1>", lambda _event, i=index: self.click_answer(i))
            row.bind("<Configure>", lambda event, label=label: label.configure(wraplength=max(200, event.width-105)), add="+")
            self.radios.append(radio)
            self.answer_labels.append(label)
        navigation = app.frame(self.run)
        navigation.grid(row=8, column=0, sticky="w", pady=(8, 12))
        self.previous_button = app.button(navigation, tr(self.app, 'Previous'), lambda: self.move(-1), width=105)
        self.previous_button.pack(side="left", padx=(0, 8))
        self.next_button = app.button(navigation, tr(self.app, 'Next'), lambda: self.move(1), width=105)
        self.next_button.pack(side="left", padx=(0, 8))
        self.clear_button = app.button(navigation, tr(self.app, 'Clear answer'), lambda: self.click_answer(-1), width=125)
        self.clear_button.pack(side="left")
        self.finish_button = app.button(self.run, tr(self.app, 'Finish test'), lambda: self.ask_action("finish"), primary=True, width=150)
        self.finish_button.grid(row=9, column=0, sticky="w", pady=(0, 16))

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
        self.bind("<Configure>", lambda event: self.prompt.configure(wraplength=max(300, event.width-20)))
        self.load()
        self.after(250, self.tick)

    def scroll_to_top(self):
        # Timed completion can run while another screen owns the shared canvas.
        if self.app.current_page == "Practice Tests":
            self.app.scroll.scroll_to_top()

    def selector(self, parent, row, text, variable, values, command=None):
        self.app.label(parent, tr(self.app,text), 13, "secondary").grid(row=row*2, column=0, sticky="w", pady=(0, 4))
        menu = LocalizedOptionMenu(parent,owner=self.app,translate_values=text!="Subject",empty_text="Add a subject first" if text=="Subject" else None, variable=variable, values=values if text!="Subject" else [], command=command,
                                  dynamic_resizing=False, height=38, font=self.app.font(),
                                  fg_color="#202633", button_color="#6D28D9")
        menu.grid(row=row*2+1, column=0, sticky="ew", pady=(0, 14))
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
        try:
            subjects = self.app.store.subjects()
            active = self.app.store.active_practice()
            history = self.app.store.practice_history()
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
            for child in self.history.winfo_children():
                child.destroy()
            if not history:
                self.app.label(self.history, tr(self.app, 'No completed tests yet.'), 14, "secondary").grid(row=0, column=0, sticky="w")
            for row, attempt in enumerate(history):
                card = self.app.frame(self.history, card=True)
                card.grid(row=row, column=0, sticky="ew", pady=(0, 12))
                card.grid_columnconfigure(0, weight=1)
                text = tr(self.app,'{v0} · {v1}/{v2} correct · {v3}',v0=attempt['subject_name'],v1=attempt['correct'],v2=attempt['question_count'],v3=self.local_time(attempt['completed_at']))
                label = self.app.label(card, text, 14, wraplength=600)
                label.grid(row=0, column=0, sticky="ew", padx=18, pady=16)
                self.app.button(card, tr(self.app, 'View result'), lambda aid=attempt["id"]: self.view_result(aid), width=115).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 14))
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
        self.update_progress()
        self.set_controls(not self.finishing and not expired(self.attempt["deadline_at"], utc_now()))

    def update_progress(self):
        answered = sum(q["selected_option"] is not None for q in self.items)
        self.progress.configure(text=tr(self.app, '{v0} · Question {v1}/{v2} · {v3} answered', v0=self.attempt['subject_name'], v1=self.attempt['current_index'] + 1, v2=len(self.items), v3=answered))

    def set_controls(self, enabled):
        state = "normal" if enabled else "disabled"
        for control in [*self.radios, self.clear_button, self.finish_button]:
            control.configure(state=state)
        self.previous_button.configure(state=state if self.attempt["current_index"] > 0 else "disabled")
        self.next_button.configure(state=state if self.attempt["current_index"] < len(self.items)-1 else "disabled")

    def click_answer(self, index):
        if self.finishing or self.active_id is None:
            return
        self.choice.set(index)
        self.choose()

    def choose(self):
        if self.active_id is None or self.finishing:
            return
        item = self.items[self.attempt["current_index"]]
        value = self.choice.get()
        try:
            self.app.store.save_practice_answer(self.active_id, item["position"], None if value == -1 else value)
        except (ValueError, sqlite3.Error) as exc:
            self.choice.set(item["selected_option"] if item["selected_option"] is not None else -1)
            self.error(exc)
            return
        item["selected_option"] = None if value == -1 else value
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
        for child in self.results.winfo_children():
            child.destroy()
        self.app.button(self.results, tr(self.app, '← Test setup / history'), self.show_config, width=195).grid(row=0, column=0, sticky="w", pady=(0, 16))
        score = round(100 * attempt["correct"] / attempt["question_count"], 1)
        self.app.label(self.results, tr(self.app, '{v0} · {v1}/{v2} correct · {v3}%', v0=attempt['subject_name'], v1=attempt['correct'], v2=attempt['question_count'], v3=score), 24, bold=True, wraplength=650).grid(row=1, column=0, sticky="ew")
        self.app.label(self.results, tr(self.app, 'Completed {v0} · {v1} answered · {v2} unanswered', v0=self.local_time(attempt['completed_at']), v1=attempt['answered'], v2=attempt['question_count'] - attempt['answered']), 13, "secondary", wraplength=650).grid(row=2, column=0, sticky="ew", pady=(8, 20))
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
            card.bind("<Configure>", lambda event, labels=labels: [label.configure(wraplength=max(200, event.width-36)) for label in labels], add="+")
        if self.active_id == attempt_id:
            self.active_id = None
            self.finishing = False
        self.setup.grid_remove()
        self.run.grid_remove()
        self.cancel_action()
        self.results.grid()
        self.scroll_to_top()
        self.status.configure(text=tr(self.app, 'Result saved. Questions and explanations below are snapshots from this test.'))

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
