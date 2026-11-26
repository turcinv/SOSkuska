"""Draft flashcards/questions from pasted notes with the optional Ollama server.

Tk-owned panel. The network request runs in a TutorTask worker that never
touches Tk or SQLite; results are reviewed here and saved on the Tk thread by
the existing atomic Store.import_* methods, which recheck the target and
duplicates under the write lock.
"""
import queue
import re
import sqlite3

import customtkinter as ctk

from csv_import import ImportValidationError
from localization import tr
from localization_widgets import LocalizedOptionMenu
from note_generation import (COUNTS, DEFAULT_COUNT, MAX_REPLY, OPTIONS, TOTAL_TIMEOUT,
                             generation_messages, item_message, parse_generated, response_schema)
from ollama_client import OllamaClient, OllamaError, endpoint_url
from panel_layout import wrap_labels, responsive_actions
from theme import COLORS as C
from tutor import TutorTask


def generation_client(endpoint):
    return OllamaClient(endpoint, total_timeout=TOTAL_TIMEOUT)


def generation_busy(app):
    """True while either note-generation panel has an Ollama request running."""
    pages = (getattr(app, 'flashcard_page', None), getattr(app, 'question_bank', None))
    return any(getattr(getattr(page, 'generator', None), 'busy', False) for page in pages)


class NoteGenerationPanel(ctk.CTkFrame):
    def __init__(self, parent, app, host, *, cards=False, client_factory=generation_client):
        super().__init__(parent, fg_color=C['card'], corner_radius=16, border_width=1, border_color=C['outline'])
        self.app = app; self.host = host; self.cards = cards; self.client_factory = client_factory
        self.kind = 'cards' if cards else 'questions'
        self.noun = 'flashcards' if cards else 'questions'
        self.task = None; self.buffer = []; self.received = 0
        self.preview = None; self.choices = []; self.target = None; self.request = None
        self.poll_id = None; self.closed = False
        self.grid_columnconfigure(0, weight=1)
        body = app.frame(self); body.grid(row=0, column=0, sticky='ew', padx=18, pady=16)
        body.grid_columnconfigure(0, weight=1)
        self.heading = app.label(body, tr(app, 'Generate {v0} with AI', v0=tr(app, self.noun)), 20, bold=True)
        self.heading.grid(row=0, column=0, sticky='ew', pady=(0, 6))
        self.status = app.label(body, '', 12, 'secondary')
        self.status.grid(row=1, column=0, sticky='ew', pady=(0, 6))
        self.server_label = app.label(body, '', 12, 'secondary')
        self.server_label.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        app.label(body, tr(app, 'Notes (up to 12,000 characters)'), 12, 'secondary').grid(row=3, column=0, sticky='w', pady=(0, 4))
        self.notes = ctk.CTkTextbox(body, height=150, font=app.font(), wrap='word', border_width=1, border_color=C['border'])
        self.notes.grid(row=4, column=0, sticky='ew', pady=(0, 10))
        count_row = app.frame(body); count_row.grid(row=5, column=0, sticky='w', pady=(0, 10))
        app.label(count_row, tr(app, 'Number of items'), 12, 'secondary').pack(side='left', padx=(0, 10))
        self.count = ctk.StringVar(master=self, value=str(DEFAULT_COUNT))
        self.count_menu = LocalizedOptionMenu(count_row, owner=app, translate_values=False, variable=self.count,
            values=[str(n) for n in COUNTS], width=90, height=34, dynamic_resizing=False, font=app.font(13),
            fg_color=C['raised'], button_color=C['border'], button_hover_color=C['selected'], text_color=C['text'])
        self.count_menu.pack(side='left')
        actions = app.frame(body); actions.grid(row=6, column=0, sticky='ew', pady=(0, 10))
        self.generate_button = app.button(actions, tr(app, 'Generate'), self.generate, primary=True, width=120)
        self.stop_button = app.button(actions, tr(app, 'Stop'), self.stop, width=90)
        self.close_button = app.button(actions, tr(app, 'Close'), self.close, width=90)
        responsive_actions(actions, app, (self.generate_button, self.stop_button, self.close_button))
        self.errors = ctk.CTkTextbox(body, height=80, font=app.font(12), wrap='word', state='disabled',
                                     border_width=1, border_color=C['border'])
        self.errors.grid(row=7, column=0, sticky='ew', pady=(0, 10)); self.errors.grid_remove()
        self.results = app.frame(body); self.results.grid(row=8, column=0, sticky='ew')
        self.results.grid_columnconfigure(0, weight=1)
        save = app.frame(body); save.grid(row=9, column=0, sticky='w', pady=(4, 0))
        self.save_button = app.button(save, tr(app, 'Save selected'), self.save, primary=True, width=150)
        self.save_button.pack(side='left', padx=(0, 8))
        self.discard_button = app.button(save, tr(app, 'Discard results'), self.discard, width=150)
        self.discard_button.pack(side='left')
        wrap_labels(body, app)
        self.controls()

    # ------------------------------------------------------------------ state
    @property
    def busy(self):
        return self.task is not None

    @property
    def target_id(self):
        return self.target['id'] if self.target else None

    def host_snapshot(self):
        snapshot = self.host.deck_snapshot if self.cards else self.host.subject_snapshot
        current = self.host.deck_id if self.cards else self.host.subject_id
        return dict(snapshot) if snapshot is not None and snapshot['id'] == current else None

    def settings(self):
        prefs = self.app.preferences
        return prefs['ollama_endpoint'], prefs['ollama_model'].strip(), prefs['answer_language']

    def controls(self):
        busy = self.busy
        rows = self.preview['rows'] if self.preview else []
        selected = sum(var.get() for var in self.choices)
        self.generate_button.configure(state='disabled' if busy else 'normal')
        self.stop_button.configure(state='normal' if busy else 'disabled')
        self.count_menu.configure(state='disabled' if busy else 'normal')
        self.save_button.configure(text=tr(self.app, 'Save {v0} selected', v0=selected),
                                   state='normal' if rows and selected and not busy else 'disabled')
        self.discard_button.configure(state='normal' if rows and not busy else 'disabled')

    def show_errors(self, lines):
        self.errors.configure(state='normal'); self.errors.delete('1.0', 'end')
        self.errors.insert('1.0', '\n'.join(self.translate_issue(line) for line in lines))
        self.errors.configure(state='disabled')
        self.errors.grid() if lines else self.errors.grid_remove()

    def translate_issue(self, line):
        line = item_message(line)
        match = re.fullmatch(r'Item (\d+): (.*)', line, re.S)
        if not match:
            return tr(self.app, line)
        detail = match[2]
        duplicate = re.fullmatch(r'Duplicate of item (\d+) (\(.*\)\.)', detail)
        if duplicate:
            detail = tr(self.app, 'Duplicate of item {v0} ' + duplicate[2], v0=duplicate[1])
        else:
            detail = tr(self.app, detail)
        return tr(self.app, 'Item {v0}: {v1}', v0=match[1], v1=detail)

    def describe_server(self):
        endpoint, model, _ = self.settings()
        try:
            endpoint = endpoint_url(endpoint)  # Show exactly the address a request would use.
        except OllamaError:
            pass
        if not model:
            self.server_label.configure(text=tr(self.app, 'No preferred AI model is saved. Choose one in Settings (or AI Tutor → Use Tutor choices, then Save).'))
        else:
            self.server_label.configure(text=tr(self.app, 'Server: {v0} · Model: {v1}', v0=endpoint, v1=model))

    # --------------------------------------------------------------- actions
    def open(self):
        snapshot = self.host_snapshot()
        if snapshot is None:
            self.host.status.configure(text=tr(self.app, 'This deck no longer exists.' if self.cards else 'This subject no longer exists.'))
            return
        if self.target_id != snapshot['id']:
            self.reset_results()
        self.target = {'id': snapshot['id'], 'name': snapshot['name']}
        if self.request is not None and self.request['target']['id'] == snapshot['id']:
            # Explicit reopen confirms the current name for drafts made for this target.
            self.request['target'] = dict(self.target)
        self.heading.configure(text=tr(self.app, 'Generate {v0} for {v1}', v0=tr(self.app, self.noun), v1=snapshot['name']))
        if not self.busy and self.preview is None:
            self.status.configure(text=tr(self.app, 'Paste your notes. They are sent only to the server below when you press Generate. Review every draft; nothing is saved until Save selected.'))
        self.describe_server(); self.controls(); self.grid()
        self.app.scroll.scroll_to_widget(self)

    def generate(self):
        if self.busy:
            return
        snapshot = self.host_snapshot()
        if snapshot is None or self.target_id != snapshot['id']:
            self.status.configure(text=tr(self.app, 'Reopen the deck before generating.' if self.cards else 'Reload the question bank before generating.'))
            return
        self.target = {'id': snapshot['id'], 'name': snapshot['name']}
        endpoint, model, language = self.settings()
        self.describe_server()
        if not model:
            self.status.configure(text=tr(self.app, 'Save a preferred AI model in Settings before generating.'))
            return
        try:
            endpoint = endpoint_url(endpoint)
            count = int(self.count.get())
            messages = generation_messages(self.kind, self.notes.get('1.0', 'end-1c'), count, language)
            task = TutorTask('chat', endpoint, model=model, messages=messages, client_factory=self.client_factory,
                             chat_options={'response_format': response_schema(self.kind, count),
                                           'options': dict(OPTIONS), 'max_reply': MAX_REPLY})
        except (ValueError, OllamaError) as exc:
            self.status.configure(text=tr(self.app, str(exc)))
            return
        # A new request always invalidates the previous drafts first.
        self.reset_results()
        self.buffer = []; self.received = 0
        self.request = {'count': count, 'target': dict(self.target), 'endpoint': endpoint, 'model': model}
        self.task = task
        task.start()
        self.status.configure(text=tr(self.app, 'Generating with {v0}… Your notes were sent to {v1}. You can Stop or use other pages; leaving this deck or subject discards the drafts.', v0=model, v1=endpoint))
        self.controls()
        self.schedule_poll()

    def stop(self):
        if self.task is not None:
            self.task.cancel()
            self.status.configure(text=tr(self.app, 'Stopping…'))

    def close(self, *, notify=False):
        """Hide the panel, cancel a running request and discard drafts; keep the notes."""
        discarded = self.busy or self.preview is not None
        self.cancel_task()
        self.reset_results()
        self.target = None
        self.grid_remove()
        if notify and discarded:
            self.host.status.configure(text=tr(self.app, 'AI generation was closed; its unsaved drafts were discarded. Your notes are kept.'))
        return discarded

    def sync_target(self):
        """Follow a rename of the same deck/subject once the host displays it."""
        snapshot = self.host_snapshot()
        if self.target is None or snapshot is None or snapshot['id'] != self.target['id']:
            return
        if snapshot['name'] != self.target['name']:
            self.target['name'] = snapshot['name']
            if self.request is not None and self.request['target']['id'] == snapshot['id']:
                self.request['target']['name'] = snapshot['name']
            self.heading.configure(text=tr(self.app, 'Generate {v0} for {v1}', v0=tr(self.app, self.noun), v1=snapshot['name']))

    def shutdown(self):
        self.closed = True
        self.cancel_task()

    def cancel_task(self):
        if self.task is not None:
            self.task.cancel()
            self.task = None  # Late events from the abandoned worker are ignored.
        if self.poll_id is not None:
            self.after_cancel(self.poll_id); self.poll_id = None
        self.controls()

    def discard(self):
        if self.busy:
            return
        self.reset_results()
        self.status.configure(text=tr(self.app, 'Generated drafts discarded. Your notes are kept.'))

    def reset_results(self):
        self.preview = None; self.choices = []
        for child in self.results.winfo_children():
            child.destroy()
        self.show_errors([])
        self.controls()

    # --------------------------------------------------------------- results
    def schedule_poll(self):
        if not self.closed:
            self.poll_id = self.after(50, self.poll)

    def poll(self):
        self.poll_id = None
        task = self.task
        if task is None:
            return
        terminal = None
        try:
            while True:
                event, value = task.events.get_nowait()
                if event == 'text':
                    self.buffer.append(value); self.received += len(value)
                else:
                    terminal = (event, value); break
        except queue.Empty:
            pass
        if terminal is None:
            self.status.configure(text=tr(self.app, 'Generating… {v0} characters received.', v0=self.received))
            self.schedule_poll()
            return
        self.task = None
        event, value = terminal
        try:
            if event == 'done':
                self.finish(''.join(self.buffer))
            elif event == 'stopped':
                self.status.configure(text=tr(self.app, 'Generation stopped. Nothing was saved; your notes are kept.'))
            else:
                self.status.configure(text=tr(self.app, 'Generation failed: {v0}', v0=tr(self.app, value)))
        finally:
            # Controls always leave the busy state, even if parsing fails unexpectedly.
            self.buffer = []
            self.controls()

    def finish(self, text):
        try:
            preview = parse_generated(self.kind, text, self.request['count'])
        except (ValueError, RecursionError) as exc:
            message = str(exc) if isinstance(exc, ValueError) else 'The model did not return valid JSON. Try again or choose another model.'
            self.status.configure(text=tr(self.app, message))
            return
        self.preview = preview
        self.render_results()
        self.show_errors(preview['errors'])
        self.status.configure(text=tr(self.app, '{v0} drafts ready to review; {v1} skipped. Untick anything wrong, then Save selected. AI drafts can contain mistakes.',
                                      v0=len(preview['rows']), v1=preview['total'] - len(preview['rows'])))

    def render_results(self):
        for child in self.results.winfo_children():
            child.destroy()
        self.choices = []
        for index, row in enumerate(self.preview['rows']):
            item = row['record'] - 1
            frame = ctk.CTkFrame(self.results, fg_color=C['raised'], corner_radius=12)
            frame.grid(row=index, column=0, sticky='ew', pady=(0, 8))
            frame.grid_columnconfigure(1, weight=1)
            var = ctk.BooleanVar(master=self, value=True)
            check = ctk.CTkCheckBox(frame, text='', variable=var, width=24, checkbox_width=18, checkbox_height=18,
                fg_color=C['primary'], hover_color=C['primary_hover'], border_color=C['border'],
                checkmark_color=C['on_primary'], text_color=C['text'], command=self.controls)
            check.grid(row=0, column=0, sticky='n', padx=(12, 6), pady=12)
            fields = row['fields']
            if self.cards:
                title, detail = fields[0], fields[1]
            else:
                title = fields[0]
                lines = [('✓ ' if i == fields[5] else '   ') + f'{letter}. {value}' for i, (letter, value) in enumerate(zip('ABCD', fields[1:5]))]
                meta = tr(self.app, 'Difficulty: {v0}', v0=tr(self.app, fields[6]))
                if row['topic']:
                    meta += ' · ' + tr(self.app, 'Topic: {v0}', v0=row['topic'])
                detail = '\n'.join([*lines, meta] + ([tr(self.app, 'Explanation: {v0}', v0=fields[7])] if fields[7] else []))
            heading = self.app.label(frame, tr(self.app, 'Item {v0}: {v1}', v0=item, v1=title), 13, bold=True, wraplength=600, justify='left')
            heading.grid(row=0, column=1, sticky='ew', padx=(0, 14), pady=(12, 2))
            body = self.app.label(frame, detail, 12, 'secondary', wraplength=600, justify='left')
            body.grid(row=1, column=1, sticky='ew', padx=(0, 14), pady=(0, 12))
            frame.bind('<Configure>', lambda event, labels=(heading, body): [label.configure(
                wraplength=max(200, self.app.scroll.logical_pixels(event.width) - 70)) for label in labels], add='+')
            self.choices.append(var)
        self.controls()

    def save(self):
        if self.busy or not self.preview:
            return
        rows = [row for row, var in zip(self.preview['rows'], self.choices) if var.get()]
        if not rows:
            return
        target = self.request['target']
        try:
            if self.cards:
                result = self.app.store.import_flashcards(target['id'], rows, expected_deck_name=target['name'])
                message = tr(self.app, 'Saved {v0} AI-drafted flashcards to {v1}. New cards are due now.', v0=result['cards'], v1=result['deck'])
            else:
                result = self.app.store.import_questions(target['id'], rows, expected_subject_name=target['name'])
                message = tr(self.app, 'Saved {v0} AI-drafted questions to {v1} and created {v2} topics.', v0=result['questions'], v1=result['subject'], v2=result['topics'])
        except ImportValidationError as exc:
            self.show_errors(exc.errors)
            self.status.configure(text=tr(self.app, 'Nothing was saved. Untick the listed items or reopen the target, then Save selected again.'))
            return
        except (sqlite3.Error, ValueError):
            self.status.configure(text=tr(self.app, 'Nothing was saved. Your drafts are kept; retry Save selected.'))
            return
        # Consume the saved batch before any refresh read; a retry must never write again.
        self.reset_results()
        self.status.configure(text=message)
        try:
            (self.host.refresh_csv_totals() if self.cards else self.host.refresh())
            self.app.refresh_data()
        except (sqlite3.Error, ValueError):
            self.status.configure(text=message + ' ' + tr(self.app, 'Could not refresh the list. Use Refresh; do not save again.'))

    def destroy(self):
        self.shutdown()
        super().destroy()
