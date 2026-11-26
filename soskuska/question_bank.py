"""Subject-scoped topics and multiple-choice authoring."""
from theme import COLORS as C
from localization_widgets import LocalizedOptionMenu
from localization import tr
import sqlite3
import unicodedata

import customtkinter as ctk
from content import DIFFICULTIES
from csv_import_panel import CsvImportPanel
from ai_generation_panel import NoteGenerationPanel


class QuestionBankPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.app = app
        self.subject_id = None
        self.subject_snapshot = None
        self.editing_question_id = None
        self.question_snapshot = None
        self.unavailable_topic_id = None
        self.editing_topic_id = None
        self.editing_topic_snapshot = None
        self.pending_delete = None
        self.filter_topics = {"All topics": "all", "No topic": None}
        self.form_topics = {"No topic": None}
        self.grid_columnconfigure(0, weight=1)

        app.button(self, tr(self.app, '← My Subjects'), lambda: app.navigate("My Subjects"), width=140).grid(row=0, column=0, sticky="w", pady=(0, 16))
        header = app.frame(self, card=True)
        header.grid(row=1,column=0,rowspan=3,sticky="ew",pady=(0,16))
        header.grid_columnconfigure(0,weight=1)
        self.heading = app.label(header, tr(self.app, 'Question bank'), 26, bold=True, wraplength=650)
        self.heading.grid(row=0, column=0, sticky="ew",padx=18,pady=(16,4))
        self.count_label = app.label(header, "", 13, "secondary")
        self.count_label.grid(row=1,column=0,sticky="ew",padx=18,pady=(0,12))
        actions = app.frame(header)
        actions.grid(row=2,column=0,sticky="w",padx=18,pady=(0,16))
        self.add_question_button = app.button(actions, tr(self.app, '+ New question'), self.show_question_form, primary=True, width=150)
        self.add_question_button.pack(side="left", padx=(0, 8))
        self.add_topic_button = app.button(actions, tr(self.app, '+ New topic'), self.show_topic_form, width=125)
        self.add_topic_button.pack(side="left", padx=(0, 8))
        self.csv_button=app.button(actions,tr(self.app, 'Import CSV'),lambda:self.importer.open(),width=125)
        self.csv_button.pack(side='left', padx=(0, 8))
        self.generate_button=app.button(actions,tr(self.app, 'Generate with AI'),lambda:self.generator.open(),width=150)
        self.generate_button.pack(side='left')

        self.topic_form = app.frame(self, card=True)
        self.topic_form.grid(row=5, column=0, sticky="ew", pady=(0, 16))
        self.topic_form.grid_columnconfigure(0, weight=1)
        self.topic_form_title = app.label(self.topic_form, tr(self.app, 'New topic'), 16, bold=True)
        self.topic_form_title.grid(row=0, column=0, sticky="w", padx=18, pady=(14, 8))
        self.topic_entry = ctk.CTkEntry(self.topic_form, height=38, font=app.font(), placeholder_text=tr(self.app, 'Topic name (1–120 characters)'), placeholder_text_color=C["secondary"])
        self.topic_entry.grid(row=1, column=0, sticky="ew", padx=18)
        self.topic_error = app.label(self.topic_form, "", 12, "secondary", wraplength=600)
        self.topic_error.grid(row=2, column=0, sticky="ew", padx=18, pady=6)
        actions = app.frame(self.topic_form)
        actions.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 14))
        self.save_topic_button = app.button(actions, tr(self.app, 'Save topic'), self.save_topic, primary=True, width=115)
        self.save_topic_button.pack(side="left", padx=(0, 8))
        app.button(actions, tr(self.app, 'Cancel'), self.hide_topic_form, width=80).pack(side="left")
        self.topic_form.grid_remove()

        self.question_form = app.frame(self, card=True)
        self.question_form.grid(row=6, column=0, sticky="ew", pady=(0, 16))
        self.question_form.grid_columnconfigure(0, weight=1)
        self.question_form_title = app.label(self.question_form, tr(self.app, 'New question'), 18, bold=True)
        self.question_form_title.grid(row=0, column=0, sticky="w", padx=18, pady=(16, 10))
        app.label(self.question_form, tr(self.app, 'Question (required, up to 2,000 characters)'), 12, "secondary").grid(row=1, column=0, sticky="w", padx=18)
        self.prompt_entry = ctk.CTkTextbox(self.question_form, height=70, font=app.font(), wrap="word", border_width=1, border_color=C["border"])
        self.prompt_entry.grid(row=2, column=0, sticky="ew", padx=18, pady=(4, 12))
        self.answer_fields = []
        self.option_entries = []
        self.answers_panel = app.frame(self.question_form)
        self.answers_panel.grid(row=3,column=0,rowspan=8,sticky="ew",padx=18,pady=(0,12))
        for i, letter in enumerate("ABCD"):
            field = app.frame(self.answers_panel)
            field.grid_columnconfigure(0,weight=1)
            self.answer_fields.append(field)
            app.label(field,tr(self.app,'Answer {v0} (required, up to 500 characters)',v0=letter),12,"secondary",wraplength=300,justify="left").grid(row=0,column=0,sticky="ew",pady=(0,4))
            entry = ctk.CTkEntry(field, height=38, font=app.font(), placeholder_text_color=C["secondary"])
            entry.grid(row=1,column=0,sticky="ew")
            self.wrap_labels(field)
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
            app.label(selectors, tr(self.app,label), 12, "secondary").grid(row=0, column=col, sticky="w", padx=(0, 8))
            menu = self.menu(selectors, variable, values)
            menu.grid(row=1, column=col, sticky="ew", padx=(0, 8), pady=(4, 0))
            if col == 2:
                self.question_topic_menu = menu
        app.label(self.question_form, tr(self.app, 'Explanation (optional, up to 2,000 characters)'), 12, "secondary").grid(row=12, column=0, sticky="w", padx=18)
        self.explanation_entry = ctk.CTkTextbox(self.question_form, height=65, font=app.font(), wrap="word", border_width=1, border_color=C["border"])
        self.explanation_entry.grid(row=13, column=0, sticky="ew", padx=18, pady=(4, 8))
        self.question_error = app.label(self.question_form, "", 12, "secondary", wraplength=600)
        self.question_error.grid(row=14, column=0, sticky="ew", padx=18)
        actions = app.frame(self.question_form)
        actions.grid(row=15, column=0, sticky="w", padx=18, pady=(6, 16))
        self.save_question_button = app.button(actions, tr(self.app, 'Save question'), self.save_question, primary=True, width=140)
        self.save_question_button.pack(side="left", padx=(0, 8))
        app.button(actions, tr(self.app, 'Cancel'), self.hide_question_form, width=80).pack(side="left")
        self.question_form.grid_remove()

        self.delete_panel = app.frame(self, card=True)
        self.delete_panel.grid(row=7, column=0, sticky="ew", pady=(0, 16))
        self.delete_panel.grid_columnconfigure(0, weight=1)
        self.delete_text = app.label(self.delete_panel, "", 14, wraplength=600)
        self.delete_text.grid(row=0, column=0, sticky="ew", padx=18, pady=14)
        actions = app.frame(self.delete_panel)
        actions.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 14))
        self.delete_button = app.button(actions, tr(self.app, 'Confirm deletion'), self.confirm_delete, width=150)
        self.delete_button.configure(fg_color=C["danger"], hover_color=C["danger_hover"], text_color=C["on_primary"])
        self.delete_button.pack(side="left", padx=(0, 8))
        app.button(actions, tr(self.app, 'Cancel'), self.cancel_delete, width=80).pack(side="left")
        self.delete_panel.grid_remove()

        filters = app.frame(self, card=True)
        filters.grid(row=8, column=0, sticky="ew", pady=(0, 12))
        filters.grid_columnconfigure((0, 1), weight=1, uniform="filter")
        self.topic_filter = ctk.StringVar(value="All topics")
        self.difficulty_filter = ctk.StringVar(value="All difficulties")
        self.topic_filter_menu = self.menu(filters, self.topic_filter, list(self.filter_topics), self.filter_changed)
        app.label(filters,tr(app,"Topic"),12,"secondary").grid(row=0,column=0,sticky="w",padx=18,pady=(12,4))
        app.label(filters,tr(app,"Difficulty"),12,"secondary").grid(row=0,column=1,sticky="w",padx=18,pady=(12,4))
        self.topic_filter_menu.grid(row=1,column=0,sticky="ew",padx=(18,8))
        self.menu(filters, self.difficulty_filter, ["All difficulties", *DIFFICULTIES], self.filter_changed).grid(row=1,column=1,sticky="ew",padx=(0,18))
        topic_actions = app.frame(filters)
        topic_actions.grid(row=2,column=0,columnspan=2,sticky="w",padx=18,pady=(12,12))
        self.edit_topic_button = app.button(topic_actions, tr(self.app, 'Rename selected topic'), self.edit_selected_topic, width=180)
        self.edit_topic_button.pack(side="left", padx=(0, 8))
        self.delete_topic_button = app.button(topic_actions, tr(self.app, 'Delete selected topic'), self.delete_selected_topic, width=180)
        self.delete_topic_button.pack(side="left")
        self.query = ctk.StringVar()
        app.label(filters,tr(app,"Search question text…"),12,"secondary").grid(row=3,column=0,columnspan=2,sticky="w",padx=18)
        self.search = ctk.CTkEntry(filters, height=38, textvariable=self.query, font=app.font(), placeholder_text=tr(self.app, 'Search question text…'), placeholder_text_color=C["secondary"])
        self.search.grid(row=4,column=0,columnspan=2,sticky="ew",padx=18,pady=(4,16))
        self.status = app.label(self, "", 12, "secondary", wraplength=650)
        self.status.grid(row=11, column=0, sticky="ew", pady=(0, 12))
        self.question_page=0
        pages=app.frame(self)
        pages.grid(row=12,column=0,sticky='ew',pady=(0,12))
        self.previous_page=app.button(pages,tr(self.app, 'Previous page'),lambda:self.move_question_page(-1),width=130)
        self.previous_page.grid(row=0,column=0,sticky='w',padx=(0,8))
        self.next_page=app.button(pages,tr(self.app, 'Next page'),lambda:self.move_question_page(1),width=120)
        self.next_page.grid(row=0,column=1,sticky='w')
        self.page_label=app.label(pages,'',12,'secondary');self.page_label.grid(row=1,column=0,columnspan=2,sticky='w',pady=(6,0))
        self.cards = app.frame(self)
        self.cards.grid(row=13, column=0, sticky="ew")
        self.cards.grid_columnconfigure(0, weight=1)
        self.importer=CsvImportPanel(self,app,self)
        self.importer.grid(row=4,column=0,sticky='ew',pady=(0,16));self.importer.grid_remove()
        self._generator=None  # Built on first use to keep startup light.
        self.query.trace_add("write", lambda *_: self.render_questions())
        for panel in (header,self.topic_form,self.question_form,self.delete_panel):
            self.wrap_labels(panel)
        self.answers_panel.bind("<Configure>", self.layout_answers)

    @property
    def generator(self):
        if self._generator is None:
            self._generator=NoteGenerationPanel(self,self.app,self)
            self._generator.grid(row=9,column=0,sticky='ew',pady=(0,16));self._generator.grid_remove()
        return self._generator

    def close_generator(self, *, notify=False):
        return self._generator.close(notify=notify) if self._generator is not None else False

    def wrap_labels(self, parent):
        labels = [w for w in parent.winfo_children() if isinstance(w,ctk.CTkLabel)]
        for label in labels:
            label.configure(justify="left",wraplength=500)
        def resize(event):
            width=max(200,self.app.scroll.logical_pixels(event.width)-36)
            for label in labels:
                label.configure(wraplength=width)
        parent.bind("<Configure>",resize,add="+")

    def layout_answers(self, event):
        columns=2 if self.app.scroll.logical_pixels(event.width)>=850 else 1
        for col in range(2):
            self.answers_panel.grid_columnconfigure(col,weight=1 if col<columns else 0,
                uniform="answers" if col<columns else "")
        for i,field in enumerate(self.answer_fields):
            field.grid(row=i//columns,column=i%columns,sticky="ew",padx=(0,12) if columns==2 and i%2==0 else 0,pady=(0,12))

    def menu(self, parent, variable, values, command=None):
        return LocalizedOptionMenu(parent,owner=self.app, variable=variable, values=values, command=command,
                                height=36, dynamic_resizing=False, font=self.app.font(13), fg_color=C["raised"],
                                button_color=C["border"], button_hover_color=C["selected"])

    def load_subject(self, subject_id):
        if self.importer.saving:return
        self.importer.cancel()
        if self.subject_id == subject_id:
            self.cancel_delete()
            try:
                self.refresh()
                self.status.configure(text='')
            except sqlite3.Error:
                self.status.configure(text=tr(self.app, 'Could not refresh the question bank. Your draft is kept; reopen Questions to retry.'))
            return
        self.subject_id = subject_id
        self.subject_snapshot = None
        discarded = self.close_generator()  # Drafts belong to the previous subject.
        self.hide_question_form()
        self.hide_topic_form()
        self.cancel_delete()
        self.topic_filter.set("All topics")
        self.difficulty_filter.set("All difficulties")
        self.query.set("")
        self.status.configure(text=tr(self.app, 'AI generation was closed; its unsaved drafts were discarded. Your notes are kept.') if discarded else '')
        self.refresh()

    def refresh(self):
        subject = self.app.store.subject(self.subject_id)
        self.subject_snapshot = dict(subject) if subject else None
        if self._generator is not None:
            self._generator.sync_target()
        if subject is None:
            self.subject_id = None
            self.heading.configure(text=tr(self.app, 'This subject no longer exists.'))
            self.add_question_button.configure(state="disabled")
            self.add_topic_button.configure(state="disabled")
            self.csv_button.configure(state="disabled")
            self.generate_button.configure(state="disabled")
            self.close_generator(notify=True)
            self.hide_question_form()
            self.hide_topic_form()
            self.cancel_delete()
        else:
            self.heading.configure(text=tr(self.app, '{v0} · Question bank', v0=subject['name']))
            self.add_question_button.configure(state="normal")
            self.add_topic_button.configure(state="normal")
            self.csv_button.configure(state="normal")
            self.generate_button.configure(state="normal")
        selected_filter = self.filter_topics.get(self.topic_filter.get(), "all")
        selected_label = self.question_topic.get()
        selected_form = self.form_topics.get(selected_label)
        topics = self.app.store.topics(self.subject_id) if subject else []
        choices = {f'Topic: {topic["name"]}': topic["id"] for topic in topics}
        self.filter_topics = {"All topics": "all", "No topic": None, **choices}
        self.form_topics = {"No topic": None, **choices}
        self.unavailable_topic_id = None
        if selected_form is not None and selected_form not in self.form_topics.values():
            self.unavailable_topic_id = selected_form
            # Keep the selected identity until the user explicitly replaces it.
            unavailable_label = selected_label if selected_label.startswith('Unavailable topic: ') else 'Unavailable topic: ' + selected_label.removeprefix('Topic: ')
            self.form_topics[unavailable_label] = selected_form
            self.question_error.configure(text=tr(self.app, 'The selected topic no longer exists. Choose another topic or No topic before saving.'))
        self.topic_filter_menu.configure(values=list(self.filter_topics))
        self.question_topic_menu.configure(values=list(self.form_topics))
        self.topic_filter.set(next((k for k, v in self.filter_topics.items() if v == selected_filter), "All topics"))
        self.question_topic.set(next((k for k, v in self.form_topics.items() if v == selected_form), "No topic"))
        self.filter_changed(reset=False)

    def filter_changed(self, _value=None, *, reset=True):
        selected = self.filter_topics.get(self.topic_filter.get(), "all")
        state = "normal" if isinstance(selected, int) else "disabled"
        self.edit_topic_button.configure(state=state)
        self.delete_topic_button.configure(state=state)
        self.render_questions(reset=reset)

    def show_topic_form(self, topic_id=None):
        if self.subject_id is None:
            return
        topic = self.app.store.topic(topic_id) if topic_id is not None else None
        if topic_id is not None and (topic is None or topic["subject_id"] != self.subject_id):
            self.status.configure(text=tr(self.app, 'This topic no longer exists in this subject.'))
            return
        self.hide_question_form()
        self.cancel_delete()
        self.editing_topic_id = topic_id
        self.editing_topic_snapshot = topic
        self.topic_form_title.configure(text=tr(self.app, 'Rename topic') if topic else tr(self.app, 'New topic'))
        self.topic_entry.delete(0, "end")
        self.topic_entry.insert(0, topic["name"] if topic else "")
        self.topic_error.configure(text=tr(self.app,''))
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
                self.app.store.update_topic(self.editing_topic_id, self.topic_entry.get(), expected_state=self.editing_topic_snapshot)
        except (ValueError, sqlite3.Error) as exc:
            self.topic_error.configure(text=tr(self.app,tr(self.app, str(exc)) if isinstance(exc, ValueError) else tr(self.app, 'Could not save the topic. Please try again.')))
            return
        self.hide_topic_form()
        self.refresh()
        self.app.refresh_data()
        self.status.configure(text=tr(self.app, 'Topic saved on this device.'))

    def show_question_form(self, question_id=None):
        if self.subject_id is None:
            return
        question = self.app.store.question(question_id) if question_id is not None else None
        if question_id is not None and (question is None or question["subject_id"] != self.subject_id):
            self.status.configure(text=tr(self.app, 'This question no longer exists in this subject.'))
            return
        self.hide_topic_form()
        self.cancel_delete()
        self.question_topic.set('No topic')
        self.unavailable_topic_id = None
        self.refresh()
        self.editing_question_id = question_id
        self.question_snapshot = question
        self.question_form_title.configure(text=tr(self.app, 'Edit question') if question else tr(self.app, 'New question'))
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
        self.question_error.configure(text=tr(self.app,''))
        self.question_form.grid()
        self.prompt_entry.focus_set()
        self.app.scroll._parent_canvas.yview_moveto(0)

    def hide_question_form(self):
        self.question_form.grid_remove()
        self.editing_question_id = None
        self.question_snapshot = None
        self.question_topic.set('No topic')
        self.unavailable_topic_id = None

    def save_question(self):
        values = (self.prompt_entry.get("1.0", "end-1c"), [entry.get() for entry in self.option_entries],
                  "ABCD".index(self.correct.get()), self.difficulty.get(),
                  self.form_topics.get(self.question_topic.get()), self.explanation_entry.get("1.0", "end-1c"))
        try:
            if self.unavailable_topic_id is not None and values[4] == self.unavailable_topic_id:
                raise ValueError('The selected topic no longer exists. Choose another topic or No topic before saving.')
            if self.editing_question_id is None:
                self.app.store.create_question(self.subject_id, *values)
            else:
                self.app.store.update_question(self.editing_question_id, *values, expected_state=self.question_snapshot)
        except (ValueError, sqlite3.Error) as exc:
            self.question_error.configure(text=tr(self.app,tr(self.app, str(exc)) if isinstance(exc, ValueError) else tr(self.app, 'Could not save the question. Please try again.')))
            return
        self.hide_question_form()
        self.refresh()
        self.app.refresh_data()
        self.status.configure(text=tr(self.app, 'Question saved on this device.'))

    def delete_selected_topic(self):
        selected = self.filter_topics.get(self.topic_filter.get())
        if isinstance(selected, int):
            self.ask_delete("topic", selected)

    def ask_delete(self, kind, record_id, *, changed=False):
        record = self.app.store.topic(record_id) if kind == "topic" else self.app.store.question(record_id)
        if record is None or record["subject_id"] != self.subject_id:
            self.cancel_delete()
            self.refresh()
            self.status.configure(text=tr(self.app, 'This topic no longer exists in this subject.' if kind == 'topic' else 'This question no longer exists in this subject.'))
            return False
        self.hide_question_form()
        self.hide_topic_form()
        self.pending_delete = (kind, record_id, dict(record))
        message = tr(self.app, 'Delete topic “{v0}”? Its questions will be kept without a topic.', v0=record["name"]) if kind == "topic" else tr(self.app, 'Delete question “{v0}” permanently? This cannot be undone.', v0=record["prompt"][:200])
        if changed:
            message = tr(self.app, 'This record changed. Review the updated warning before deleting it.') + '\n\n' + message
        self.delete_text.configure(text=message)
        self.delete_panel.grid()
        self.app.scroll._parent_canvas.yview_moveto(0)
        return True

    def cancel_delete(self):
        self.delete_panel.grid_remove()
        self.pending_delete = None

    def confirm_delete(self):
        if self.pending_delete is None:
            return
        kind, record_id, snapshot = self.pending_delete
        try:
            if kind == "topic":
                deleted = self.app.store.delete_topic(record_id, expected_state=snapshot)
            else:
                deleted = self.app.store.delete_question(record_id, expected_state=snapshot)
            if not deleted:
                self.cancel_delete()
                self.refresh()
                if self.ask_delete(kind, record_id, changed=True):
                    self.status.configure(text=tr(self.app, 'This record changed. Review the updated warning before deleting it.'))
                return
        except (ValueError, sqlite3.Error) as exc:
            self.status.configure(text=tr(self.app,tr(self.app, str(exc)) if isinstance(exc, ValueError) else tr(self.app, 'Could not delete the record. Please try again.')))
            return
        self.cancel_delete()
        self.refresh()
        self.app.refresh_data()
        self.status.configure(text=tr(self.app,tr(self.app, 'Topic deleted; its questions were kept.') if kind == 'topic' else tr(self.app, 'Question deleted.')))

    def move_question_page(self,offset):
        self.question_page+=offset
        self.render_questions(reset=False)

    def render_questions(self, reset=True):
        if reset:self.question_page=0
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
        self.count_label.configure(text=tr(self.app, '{v0} topics · {v1} of {v2} questions', v0=len(topics), v1=len(visible), v2=len(questions)))
        pages=max(1,(len(visible)+49)//50)
        self.question_page=max(0,min(self.question_page,pages-1))
        self.page_label.configure(text=tr(self.app, 'Page {v0} / {v1} · up to 50 questions per page', v0=self.question_page + 1, v1=pages))
        self.previous_page.configure(state='normal' if self.question_page>0 else 'disabled')
        self.next_page.configure(state='normal' if self.question_page+1<pages else 'disabled')
        if not visible:
            message = "No matching questions. Try different filters." if questions else "No questions yet. Add your first multiple-choice question."
            empty=self.app.frame(self.cards,card=True)
            empty.grid(row=0,column=0,sticky="ew")
            empty.grid_columnconfigure(0,weight=1)
            self.app.label(empty,tr(self.app,message),14,"secondary").grid(row=0,column=0,sticky="ew",padx=18,pady=20)
            self.wrap_labels(empty)
            return
        for row, question in enumerate(visible[self.question_page*50:(self.question_page+1)*50]):
            card = self.app.frame(self.cards, card=True)
            card.grid(row=row, column=0, sticky="ew", pady=(0, 14))
            card.grid_columnconfigure(0, weight=1)
            title = self.app.label(card, question["prompt"], 15, bold=True, wraplength=600)
            title.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
            self.app.label(card, tr(self.app, '{v0} · {v1}', v0=question['topic_name'] or tr(self.app,'No topic'), v1=tr(self.app,question['difficulty'])), 12, "secondary", wraplength=600).grid(row=1, column=0, sticky="ew", padx=18)
            field = ["option_a", "option_b", "option_c", "option_d"][question["correct_option"]]
            answer_panel=self.app.frame(card)
            answer_panel.configure(fg_color=C["raised"],corner_radius=8)
            answer_panel.grid(row=2,column=0,sticky="ew",padx=18,pady=(8,12))
            answer_panel.grid_columnconfigure(0,weight=1)
            answer = self.app.label(answer_panel, tr(self.app, 'Correct answer: {v0} · {v1}', v0='ABCD'[question['correct_option']], v1=question[field]), 13, "secondary", wraplength=600)
            answer.grid(row=0,column=0,sticky="ew",padx=12,pady=12)
            self.wrap_labels(answer_panel)
            self.wrap_labels(card)
            actions = self.app.frame(card)
            actions.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 16))
            self.app.button(actions, tr(self.app, 'Edit'), lambda qid=question["id"]: self.show_question_form(qid), width=85).pack(side="left", padx=(0, 8))
            self.app.button(actions, tr(self.app, 'Delete'), lambda qid=question["id"]: self.ask_delete("question", qid), width=85).pack(side="left")
