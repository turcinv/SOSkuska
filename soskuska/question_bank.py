"""Subject-scoped topics and multiple-choice authoring; no practice execution yet."""
import sqlite3
import unicodedata

import customtkinter as ctk
from content import DIFFICULTIES


class QuestionBankPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.app = app
        self.subject_id = None
        self.editing_question_id = None
        self.editing_topic_id = None
        self.pending_delete = None
        self.filter_topics = {"All topics": "all", "No topic": None}
        self.form_topics = {"No topic": None}
        self.grid_columnconfigure(0, weight=1)

        app.button(self, "← My Subjects", lambda: app.navigate("My Subjects"), width=140).grid(row=0, column=0, sticky="w", pady=(0, 16))
        self.heading = app.label(self, "Question bank", 26, bold=True, wraplength=650)
        self.heading.grid(row=1, column=0, sticky="ew")
        self.count_label = app.label(self, "", 13, "secondary")
        self.count_label.grid(row=2, column=0, sticky="w", pady=(4, 16))
        actions = app.frame(self)
        actions.grid(row=3, column=0, sticky="w", pady=(0, 16))
        self.add_question_button = app.button(actions, "+ New question", self.show_question_form, primary=True, width=150)
        self.add_question_button.pack(side="left", padx=(0, 8))
        self.add_topic_button = app.button(actions, "+ New topic", self.show_topic_form, width=125)
        self.add_topic_button.pack(side="left")

        self.topic_form = app.frame(self, card=True)
        self.topic_form.grid(row=4, column=0, sticky="ew", pady=(0, 16))
        self.topic_form.grid_columnconfigure(0, weight=1)
        self.topic_form_title = app.label(self.topic_form, "New topic", 16, bold=True)
        self.topic_form_title.grid(row=0, column=0, sticky="w", padx=18, pady=(14, 8))
        self.topic_entry = ctk.CTkEntry(self.topic_form, height=38, font=app.font(), placeholder_text="Topic name (1–120 characters)")
        self.topic_entry.grid(row=1, column=0, sticky="ew", padx=18)
        self.topic_error = app.label(self.topic_form, "", 12, "secondary", wraplength=600)
        self.topic_error.grid(row=2, column=0, sticky="ew", padx=18, pady=6)
        actions = app.frame(self.topic_form)
        actions.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 14))
        self.save_topic_button = app.button(actions, "Save topic", self.save_topic, primary=True, width=115)
        self.save_topic_button.pack(side="left", padx=(0, 8))
        app.button(actions, "Cancel", self.hide_topic_form, width=80).pack(side="left")
        self.topic_form.grid_remove()

        self.question_form = app.frame(self, card=True)
        self.question_form.grid(row=5, column=0, sticky="ew", pady=(0, 16))
        self.question_form.grid_columnconfigure(0, weight=1)
        self.question_form_title = app.label(self.question_form, "New question", 18, bold=True)
        self.question_form_title.grid(row=0, column=0, sticky="w", padx=18, pady=(16, 10))
        app.label(self.question_form, "Question (required, up to 2,000 characters)", 12, "secondary").grid(row=1, column=0, sticky="w", padx=18)
        self.prompt_entry = ctk.CTkTextbox(self.question_form, height=70, font=app.font(), wrap="word")
        self.prompt_entry.grid(row=2, column=0, sticky="ew", padx=18, pady=(4, 12))
        self.option_entries = []
        for i, letter in enumerate("ABCD"):
            app.label(self.question_form, f"Answer {letter} (required, up to 500 characters)", 12, "secondary").grid(row=3+i*2, column=0, sticky="w", padx=18)
            entry = ctk.CTkEntry(self.question_form, height=36, font=app.font())
            entry.grid(row=4+i*2, column=0, sticky="ew", padx=18, pady=(4, 10))
            self.option_entries.append(entry)
        selectors = app.frame(self.question_form)
        selectors.grid(row=11, column=0, sticky="ew", padx=18, pady=(2, 12))
        selectors.grid_columnconfigure((0, 1, 2), weight=1, uniform="editor")
        self.correct = ctk.StringVar(value="A")
        self.difficulty = ctk.StringVar(value="Medium")
        self.question_topic = ctk.StringVar(value="No topic")
        for col, (label, variable, values) in enumerate([
            ("Correct answer", self.correct, list("ABCD")),
            ("Difficulty", self.difficulty, list(DIFFICULTIES)),
            ("Topic", self.question_topic, ["No topic"]),
        ]):
            app.label(selectors, label, 12, "secondary").grid(row=0, column=col, sticky="w", padx=(0, 8))
            menu = self.menu(selectors, variable, values)
            menu.grid(row=1, column=col, sticky="ew", padx=(0, 8), pady=(4, 0))
            if col == 2:
                self.question_topic_menu = menu
        app.label(self.question_form, "Explanation (optional, up to 2,000 characters)", 12, "secondary").grid(row=12, column=0, sticky="w", padx=18)
        self.explanation_entry = ctk.CTkTextbox(self.question_form, height=65, font=app.font(), wrap="word")
        self.explanation_entry.grid(row=13, column=0, sticky="ew", padx=18, pady=(4, 8))
        self.question_error = app.label(self.question_form, "", 12, "secondary", wraplength=600)
        self.question_error.grid(row=14, column=0, sticky="ew", padx=18)
        actions = app.frame(self.question_form)
        actions.grid(row=15, column=0, sticky="w", padx=18, pady=(6, 16))
        self.save_question_button = app.button(actions, "Save question", self.save_question, primary=True, width=140)
        self.save_question_button.pack(side="left", padx=(0, 8))
        app.button(actions, "Cancel", self.hide_question_form, width=80).pack(side="left")
        self.question_form.grid_remove()

        self.delete_panel = app.frame(self, card=True)
        self.delete_panel.grid(row=6, column=0, sticky="ew", pady=(0, 16))
        self.delete_panel.grid_columnconfigure(0, weight=1)
        self.delete_text = app.label(self.delete_panel, "", 14, wraplength=600)
        self.delete_text.grid(row=0, column=0, sticky="ew", padx=18, pady=14)
        actions = app.frame(self.delete_panel)
        actions.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 14))
        self.delete_button = app.button(actions, "Confirm deletion", self.confirm_delete, width=150)
        self.delete_button.configure(fg_color="#7F1D1D", hover_color="#991B1B")
        self.delete_button.pack(side="left", padx=(0, 8))
        app.button(actions, "Cancel", self.cancel_delete, width=80).pack(side="left")
        self.delete_panel.grid_remove()

        filters = app.frame(self)
        filters.grid(row=7, column=0, sticky="ew", pady=(0, 12))
        filters.grid_columnconfigure((0, 1), weight=1, uniform="filter")
        self.topic_filter = ctk.StringVar(value="All topics")
        self.difficulty_filter = ctk.StringVar(value="All difficulties")
        self.topic_filter_menu = self.menu(filters, self.topic_filter, list(self.filter_topics), self.filter_changed)
        self.topic_filter_menu.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.menu(filters, self.difficulty_filter, ["All difficulties", *DIFFICULTIES], self.filter_changed).grid(row=0, column=1, sticky="ew")
        topic_actions = app.frame(self)
        topic_actions.grid(row=8, column=0, sticky="w", pady=(0, 12))
        self.edit_topic_button = app.button(topic_actions, "Rename selected topic", self.edit_selected_topic, width=180)
        self.edit_topic_button.pack(side="left", padx=(0, 8))
        self.delete_topic_button = app.button(topic_actions, "Delete selected topic", self.delete_selected_topic, width=180)
        self.delete_topic_button.pack(side="left")
        self.query = ctk.StringVar()
        self.search = ctk.CTkEntry(self, height=38, textvariable=self.query, font=app.font(), placeholder_text="Search question text…")
        self.search.grid(row=9, column=0, sticky="ew", pady=(0, 12))
        self.status = app.label(self, "", 12, "secondary", wraplength=650)
        self.status.grid(row=10, column=0, sticky="ew", pady=(0, 12))
        self.cards = app.frame(self)
        self.cards.grid(row=11, column=0, sticky="ew")
        self.cards.grid_columnconfigure(0, weight=1)
        self.query.trace_add("write", lambda *_: self.render_questions())
        self.bind("<Configure>", lambda event: self.heading.configure(wraplength=max(300, event.width - 20)))

    def menu(self, parent, variable, values, command=None):
        return ctk.CTkOptionMenu(parent, variable=variable, values=values, command=command,
                                height=36, font=self.app.font(13), fg_color="#202633",
                                button_color="#6D28D9", button_hover_color="#8B5CF6")

    def load_subject(self, subject_id):
        self.subject_id = subject_id
        self.hide_question_form()
        self.hide_topic_form()
        self.cancel_delete()
        self.topic_filter.set("All topics")
        self.difficulty_filter.set("All difficulties")
        self.query.set("")
        self.status.configure(text="")
        self.refresh()

    def refresh(self):
        subject = self.app.store.subject(self.subject_id)
        if subject is None:
            self.subject_id = None
            self.heading.configure(text="This subject no longer exists.")
            self.add_question_button.configure(state="disabled")
            self.add_topic_button.configure(state="disabled")
            self.hide_question_form()
            self.hide_topic_form()
            self.cancel_delete()
        else:
            self.heading.configure(text=f'{subject["name"]} · Question bank')
            self.add_question_button.configure(state="normal")
            self.add_topic_button.configure(state="normal")
        selected_filter = self.filter_topics.get(self.topic_filter.get(), "all")
        selected_form = self.form_topics.get(self.question_topic.get())
        topics = self.app.store.topics(self.subject_id) if subject else []
        choices = {f'Topic: {topic["name"]}': topic["id"] for topic in topics}
        self.filter_topics = {"All topics": "all", "No topic": None, **choices}
        self.form_topics = {"No topic": None, **choices}
        self.topic_filter_menu.configure(values=list(self.filter_topics))
        self.question_topic_menu.configure(values=list(self.form_topics))
        self.topic_filter.set(next((k for k, v in self.filter_topics.items() if v == selected_filter), "All topics"))
        self.question_topic.set(next((k for k, v in self.form_topics.items() if v == selected_form), "No topic"))
        self.filter_changed()

    def filter_changed(self, _value=None):
        selected = self.filter_topics.get(self.topic_filter.get(), "all")
        state = "normal" if isinstance(selected, int) else "disabled"
        self.edit_topic_button.configure(state=state)
        self.delete_topic_button.configure(state=state)
        self.render_questions()

    def show_topic_form(self, topic_id=None):
        if self.subject_id is None:
            return
        topic = self.app.store.topic(topic_id) if topic_id is not None else None
        if topic_id is not None and (topic is None or topic["subject_id"] != self.subject_id):
            self.status.configure(text="This topic no longer exists in this subject.")
            return
        self.hide_question_form()
        self.cancel_delete()
        self.editing_topic_id = topic_id
        self.topic_form_title.configure(text="Rename topic" if topic else "New topic")
        self.topic_entry.delete(0, "end")
        self.topic_entry.insert(0, topic["name"] if topic else "")
        self.topic_error.configure(text="")
        self.topic_form.grid()
        self.topic_entry.focus_set()
        self.app.scroll._parent_canvas.yview_moveto(0)

    def hide_topic_form(self):
        self.topic_form.grid_remove()
        self.editing_topic_id = None

    def edit_selected_topic(self):
        selected = self.filter_topics.get(self.topic_filter.get())
        if isinstance(selected, int):
            self.show_topic_form(selected)

    def save_topic(self):
        try:
            if self.editing_topic_id is None:
                self.app.store.create_topic(self.subject_id, self.topic_entry.get())
            else:
                self.app.store.update_topic(self.editing_topic_id, self.topic_entry.get())
        except (ValueError, sqlite3.Error) as exc:
            self.topic_error.configure(text=str(exc) if isinstance(exc, ValueError) else "Could not save the topic. Please try again.")
            return
        self.hide_topic_form()
        self.refresh()
        self.app.refresh_data()
        self.status.configure(text="Topic saved on this device.")

    def show_question_form(self, question_id=None):
        if self.subject_id is None:
            return
        question = self.app.store.question(question_id) if question_id is not None else None
        if question_id is not None and (question is None or question["subject_id"] != self.subject_id):
            self.status.configure(text="This question no longer exists in this subject.")
            return
        self.hide_topic_form()
        self.cancel_delete()
        self.refresh()
        self.editing_question_id = question_id
        self.question_form_title.configure(text="Edit question" if question else "New question")
        for textbox, value in [(self.prompt_entry, question["prompt"] if question else ""),
                               (self.explanation_entry, question["explanation"] if question else "")]:
            textbox.delete("1.0", "end")
            textbox.insert("1.0", value)
        for entry, field in zip(self.option_entries, ["option_a", "option_b", "option_c", "option_d"]):
            entry.delete(0, "end")
            entry.insert(0, question[field] if question else "")
        self.correct.set("ABCD"[question["correct_option"]] if question else "A")
        self.difficulty.set(question["difficulty"] if question else "Medium")
        topic_id = question["topic_id"] if question else self.filter_topics.get(self.topic_filter.get())
        self.question_topic.set(next((k for k, v in self.form_topics.items() if v == topic_id), "No topic"))
        self.question_error.configure(text="")
        self.question_form.grid()
        self.prompt_entry.focus_set()
        self.app.scroll._parent_canvas.yview_moveto(0)

    def hide_question_form(self):
        self.question_form.grid_remove()
        self.editing_question_id = None

    def save_question(self):
        values = (self.prompt_entry.get("1.0", "end-1c"), [entry.get() for entry in self.option_entries],
                  "ABCD".index(self.correct.get()), self.difficulty.get(),
                  self.form_topics.get(self.question_topic.get()), self.explanation_entry.get("1.0", "end-1c"))
        try:
            if self.editing_question_id is None:
                self.app.store.create_question(self.subject_id, *values)
            else:
                self.app.store.update_question(self.editing_question_id, *values)
        except (ValueError, sqlite3.Error) as exc:
            self.question_error.configure(text=str(exc) if isinstance(exc, ValueError) else "Could not save the question. Please try again.")
            return
        self.hide_question_form()
        self.refresh()
        self.app.refresh_data()
        self.status.configure(text="Question saved on this device.")

    def delete_selected_topic(self):
        selected = self.filter_topics.get(self.topic_filter.get())
        if isinstance(selected, int):
            self.ask_delete("topic", selected)

    def ask_delete(self, kind, record_id):
        record = self.app.store.topic(record_id) if kind == "topic" else self.app.store.question(record_id)
        if record is None or record["subject_id"] != self.subject_id:
            self.refresh()
            return
        self.hide_question_form()
        self.hide_topic_form()
        self.pending_delete = (kind, record_id)
        message = f'Delete topic “{record["name"]}”? Its questions will be kept without a topic.' if kind == "topic" else "Delete this question permanently? This cannot be undone."
        self.delete_text.configure(text=message)
        self.delete_panel.grid()
        self.app.scroll._parent_canvas.yview_moveto(0)

    def cancel_delete(self):
        self.delete_panel.grid_remove()
        self.pending_delete = None

    def confirm_delete(self):
        if self.pending_delete is None:
            return
        kind, record_id = self.pending_delete
        try:
            if kind == "topic":
                self.app.store.delete_topic(record_id)
            else:
                self.app.store.delete_question(record_id)
        except (ValueError, sqlite3.Error) as exc:
            self.status.configure(text=str(exc) if isinstance(exc, ValueError) else "Could not delete the record. Please try again.")
            return
        self.cancel_delete()
        self.refresh()
        self.app.refresh_data()
        self.status.configure(text="Topic deleted; its questions were kept." if kind == "topic" else "Question deleted.")

    def render_questions(self):
        for widget in self.cards.winfo_children():
            widget.destroy()
        questions = self.app.store.questions(self.subject_id) if self.subject_id is not None else []
        key = unicodedata.normalize("NFKC", self.query.get().strip()).casefold()
        topic = self.filter_topics.get(self.topic_filter.get(), "all")
        difficulty = self.difficulty_filter.get()
        visible = [q for q in questions if key in unicodedata.normalize("NFKC", q["prompt"]).casefold()
                   and (topic == "all" or q["topic_id"] == topic)
                   and (difficulty == "All difficulties" or q["difficulty"] == difficulty)]
        topics = self.app.store.topics(self.subject_id) if self.subject_id is not None else []
        self.count_label.configure(text=f"{len(topics)} topics · {len(visible)} of {len(questions)} questions")
        if not visible:
            message = "No matching questions. Try different filters." if questions else "No questions yet. Add your first multiple-choice question."
            self.app.label(self.cards, message, 14, "secondary", wraplength=600).grid(row=0, column=0, sticky="w", pady=20)
            return
        for row, question in enumerate(visible):
            card = self.app.frame(self.cards, card=True)
            card.grid(row=row, column=0, sticky="ew", pady=(0, 14))
            card.grid_columnconfigure(0, weight=1)
            title = self.app.label(card, question["prompt"], 15, bold=True, wraplength=600)
            title.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
            self.app.label(card, f'{question["topic_name"] or "No topic"} · {question["difficulty"]}', 12, "secondary", wraplength=600).grid(row=1, column=0, sticky="w", padx=18)
            field = ["option_a", "option_b", "option_c", "option_d"][question["correct_option"]]
            answer = self.app.label(card, f'Correct answer: {"ABCD"[question["correct_option"]]} · {question[field]}', 13, "secondary", wraplength=600)
            answer.grid(row=2, column=0, sticky="ew", padx=18, pady=(6, 12))
            card.bind("<Configure>", lambda event, title=title, answer=answer: (title.configure(wraplength=max(200, event.width-36)), answer.configure(wraplength=max(200, event.width-36))), add="+")
            actions = self.app.frame(card)
            actions.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 16))
            self.app.button(actions, "Edit", lambda qid=question["id"]: self.show_question_form(qid), width=85).pack(side="left", padx=(0, 8))
            self.app.button(actions, "Delete", lambda qid=question["id"]: self.ask_delete("question", qid), width=85).pack(side="left")
