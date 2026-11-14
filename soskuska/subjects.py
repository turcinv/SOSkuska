"""Subject management screen; widget work stays on Tk's main thread."""
import sqlite3

import customtkinter as ctk


class SubjectPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.app = app
        self.editing_id = None
        self.deleting_id = None
        self.card_columns = 1
        self.grid_columnconfigure(0, weight=1)
        header = app.frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure(0, weight=1)
        app.label(header, "My Subjects", 28, bold=True).grid(row=0, column=0, sticky="w")
        app.label(header, "Your subjects, exam dates and focused study time.", 14, "secondary").grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.add_button = app.button(header, "+ New subject", self.show_form, primary=True, width=140)
        self.add_button.grid(row=0, column=1, rowspan=2, padx=(16, 0))

        self.form = app.frame(self, card=True)
        self.form.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.form.grid_columnconfigure(0, weight=1)
        self.form_title = app.label(self.form, "New subject", 18, bold=True)
        self.form_title.grid(row=0, column=0, sticky="w", padx=18, pady=(16, 12))
        app.label(self.form, "Subject name (required, up to 120 characters)", 12, "secondary").grid(row=1, column=0, sticky="w", padx=18)
        self.name_entry = ctk.CTkEntry(self.form, height=38, font=app.font(), placeholder_text="e.g. Mathematics")
        self.name_entry.grid(row=2, column=0, sticky="ew", padx=18, pady=(4, 12))
        app.label(self.form, "Description (optional)", 12, "secondary").grid(row=3, column=0, sticky="w", padx=18)
        self.description_entry = ctk.CTkTextbox(self.form, height=65, font=app.font(), wrap="word")
        self.description_entry.grid(row=4, column=0, sticky="ew", padx=18, pady=(4, 12))
        app.label(self.form, "Exam date (optional, YYYY-MM-DD)", 12, "secondary").grid(row=5, column=0, sticky="w", padx=18)
        self.exam_entry = ctk.CTkEntry(self.form, height=38, font=app.font(), placeholder_text="YYYY-MM-DD")
        self.exam_entry.grid(row=6, column=0, sticky="ew", padx=18, pady=(4, 12))
        self.form_error = app.label(self.form, "", 12, "secondary", wraplength=600)
        self.form_error.grid(row=7, column=0, sticky="ew", padx=18)
        actions = app.frame(self.form)
        actions.grid(row=8, column=0, sticky="w", padx=18, pady=(4, 16))
        self.save_button = app.button(actions, "Save subject", self.save_subject, primary=True, width=130)
        self.save_button.pack(side="left", padx=(0, 8))
        app.button(actions, "Cancel", self.hide_form, width=85).pack(side="left")
        self.form.grid_remove()

        self.delete_panel = app.frame(self, card=True)
        self.delete_panel.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        self.delete_panel.grid_columnconfigure(0, weight=1)
        self.delete_label = app.label(self.delete_panel, "", 14, wraplength=600)
        self.delete_label.grid(row=0, column=0, sticky="ew", padx=18, pady=14)
        actions = app.frame(self.delete_panel)
        actions.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 14))
        self.delete_button = app.button(actions, "Delete subject", self.confirm_delete, width=130)
        self.delete_button.configure(fg_color="#7F1D1D", hover_color="#991B1B")
        self.delete_button.pack(side="left", padx=(0, 8))
        app.button(actions, "Cancel", self.cancel_delete, width=85).pack(side="left")
        self.delete_panel.grid_remove()

        self.query = ctk.StringVar()
        self.search = ctk.CTkEntry(self, height=38, textvariable=self.query, font=app.font(), placeholder_text="Search subjects…")
        self.search.grid(row=3, column=0, sticky="ew", pady=(0, 16))
        self.query.trace_add("write", lambda *_: self.render())
        self.status = app.label(self, "", 12, "secondary", wraplength=650)
        self.status.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        self.cards = app.frame(self)
        self.cards.grid(row=5, column=0, sticky="ew")
        self.bind("<Configure>", self._resize)
        self.render()

    def _resize(self, event):
        # CTkFrame.bind forwards Configure events from its internal canvas.
        columns = 2 if event.width >= 850 else 1
        if columns != self.card_columns:
            self.card_columns = columns
            self.render()

    def show_form(self, subject_id=None):
        self.cancel_delete()
        subject = self.app.store.subject(subject_id) if subject_id is not None else None
        if subject_id is not None and subject is None:
            self.status.configure(text="This subject no longer exists.")
            return
        self.editing_id = subject_id
        self.form_title.configure(text="Edit subject" if subject else "New subject")
        for entry, value in [(self.name_entry, subject["name"] if subject else ""),
                             (self.exam_entry, (subject["exam_date"] or "") if subject else "")]:
            entry.delete(0, "end")
            entry.insert(0, value)
        self.description_entry.delete("1.0", "end")
        self.description_entry.insert("1.0", subject["description"] if subject else "")
        self.form_error.configure(text="")
        self.form.grid()
        self.app.scroll._parent_canvas.yview_moveto(0)
        self.name_entry.focus_set()

    def hide_form(self):
        self.form.grid_remove()
        self.editing_id = None

    def save_subject(self):
        fields = (self.name_entry.get(), self.description_entry.get("1.0", "end-1c"), self.exam_entry.get())
        try:
            if self.editing_id is None:
                self.app.store.create_subject(*fields)
            else:
                self.app.store.update_subject(self.editing_id, *fields)
        except ValueError as exc:
            self.form_error.configure(text=str(exc))
            return
        except sqlite3.Error:
            self.form_error.configure(text="Could not save the subject. Check disk space and try again.")
            return
        self.hide_form()
        self.app.refresh_data()
        self.status.configure(text="Subject saved on this device.")

    def ask_delete(self, subject_id):
        if self.app.session_open and self.app.session_subject_id == subject_id:
            self.status.configure(text="Finish the active focus session before deleting its subject.")
            return
        subject = self.app.store.subject(subject_id)
        if subject is None:
            self.render()
            return
        self.hide_form()
        self.deleting_id = subject_id
        topics = len(self.app.store.topics(subject_id))
        questions = len(self.app.store.questions(subject_id))
        content_warning = f" This permanently deletes {topics} topics and {questions} questions." if topics or questions else ""
        self.delete_label.configure(text=f'Delete “{subject["name"]}”?{content_warning} Saved study time and session history will be kept.')
        self.delete_panel.grid()
        self.app.scroll._parent_canvas.yview_moveto(0)

    def cancel_delete(self):
        self.delete_panel.grid_remove()
        self.deleting_id = None

    def confirm_delete(self):
        if self.deleting_id is None:
            return
        if self.app.session_open and self.app.session_subject_id == self.deleting_id:
            self.status.configure(text="Finish the active focus session before deleting its subject.")
            return
        try:
            self.app.store.delete_subject(self.deleting_id)
        except (ValueError, sqlite3.Error) as exc:
            self.status.configure(text=str(exc) if isinstance(exc, ValueError) else "Could not delete the subject. Please try again.")
            return
        self.cancel_delete()
        self.app.refresh_data()
        self.status.configure(text="Subject deleted. Previous study time is preserved.")

    def render(self):
        for child in self.cards.winfo_children():
            child.destroy()
        subjects = self.app.store.subjects()
        query = self.query.get().strip().casefold()
        visible = [s for s in subjects if query in s["name"].casefold()]
        for col in range(2):
            self.cards.grid_columnconfigure(col, weight=1 if col < self.card_columns else 0, uniform="subject" if col < self.card_columns else "")
        if not visible:
            message = "No matching subjects. Try another name." if subjects else "No subjects yet. Create your first subject to start studying."
            self.app.label(self.cards, message, 14, "secondary", wraplength=600).grid(row=0, column=0, columnspan=2, sticky="w", pady=20)
            return
        for i, subject in enumerate(visible):
            card = self.app.frame(self.cards, card=True)
            card.grid(row=i // self.card_columns, column=i % self.card_columns, sticky="nsew", padx=(0, 8) if self.card_columns == 2 and i % 2 == 0 else (8, 0) if self.card_columns == 2 else 0, pady=(0, 16))
            card.grid_columnconfigure(0, weight=1)
            title = self.app.label(card, subject["name"], 17, bold=True, wraplength=300)
            title.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 6))
            description = self.app.label(card, subject["description"] or "No description yet.", 13, "secondary", wraplength=300)
            description.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
            def resize_labels(event, title=title, description=description):
                title.configure(wraplength=max(200, event.width - 36))
                description.configure(wraplength=max(200, event.width - 36))
            card.bind("<Configure>", resize_labels, add="+")
            exam = f'Exam: {subject["exam_date"]}' if subject["exam_date"] else "No exam date set"
            self.app.label(card, exam, 12, "secondary").grid(row=2, column=0, sticky="w", padx=18)
            self.app.label(card, f'{subject["topic_count"]} topics · {subject["question_count"]} questions · {subject["study_seconds"] // 60} min studied', 12, "secondary").grid(row=3, column=0, sticky="w", padx=18, pady=(4, 12))
            actions = self.app.frame(card)
            actions.grid(row=4, column=0, sticky="w", padx=18, pady=(0, 16))
            for text, callback in [("Questions", lambda sid=subject["id"]: self.app.open_question_bank(sid)),
                                   ("Study", lambda sid=subject["id"]: self.app.start_focus(sid)),
                                   ("Edit", lambda sid=subject["id"]: self.show_form(sid)),
                                   ("Delete", lambda sid=subject["id"]: self.ask_delete(sid))]:
                self.app.button(actions, text, callback, width=78, primary=text == "Study").pack(side="left", padx=(0, 6))
