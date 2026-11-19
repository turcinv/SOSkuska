"""Persistent preferences with explicit Save, stale-write checks and kept drafts."""
import sqlite3

import customtkinter as ctk
from preferences import preference_fields
from tutor import LANGUAGES
from backup_panel import BackupPanel


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color='transparent', corner_radius=0)
        self.app = app
        self.snapshot = None
        self.baseline = None
        self.pending_reload = False
        self.grid_columnconfigure(0, weight=1)
        app.label(self, 'Settings', 28, bold=True).grid(row=0, column=0, sticky='w')
        self.status = app.label(self, 'Preferences stay on this device. Save to apply and remember them.', 13, 'secondary', wraplength=600)
        self.status.grid(row=1, column=0, sticky='ew', pady=(6, 16))
        self.entries = {}
        labels = [('focus_minutes','Focus duration (1–180 minutes; next session)'),
                  ('daily_goal_minutes','Daily focus goal (1–1,440 minutes)'),
                  ('ollama_endpoint','Ollama server URL'),
                  ('ollama_model','Preferred model name (optional; checked when you connect)')]
        for index, (key, title) in enumerate(labels):
            app.label(self, title, 13, 'secondary').grid(row=2+index*2, column=0, sticky='w', pady=(4, 4))
            entry = ctk.CTkEntry(self, height=38, font=app.font())
            entry.grid(row=3+index*2, column=0, sticky='ew', pady=(0, 10))
            self.entries[key] = entry
        app.label(self, 'AI answer language', 13, 'secondary').grid(row=10, column=0, sticky='w', pady=(4, 4))
        self.language = ctk.StringVar(value='Automatic')
        self.language_menu = ctk.CTkOptionMenu(self, variable=self.language, values=list(LANGUAGES), dynamic_resizing=False, height=38, font=app.font())
        self.language_menu.grid(row=11, column=0, sticky='ew', pady=(0, 14))
        info = app.label(self, 'Saving never connects to Ollama. AI chats still last only for this app session. Active focus sessions keep their original duration. Use New chat before switching an existing chat to a different server.', 12, 'secondary', wraplength=600)
        info.grid(row=12, column=0, sticky='ew', pady=(0, 14))
        actions = app.frame(self)
        actions.grid(row=13, column=0, sticky='w')
        self.save_button = app.button(actions, 'Save settings', self.save, primary=True, width=125)
        self.save_button.pack(side='left', padx=(0, 8))
        self.reload_button = app.button(actions, 'Reload', self.reload, width=110)
        self.reload_button.pack(side='left', padx=(0, 8))
        self.copy_button = app.button(actions, 'Use Tutor choices', self.copy_tutor, width=155)
        self.copy_button.pack(side='left')
        self.backups = BackupPanel(self, app)
        self.backups.grid(row=14, column=0, sticky='ew', pady=(20, 0))
        self.baseline = self.values()  # Even a failed first read must preserve later edits.
        self.bind('<Configure>', lambda event: [label.configure(wraplength=max(250,event.width-12)) for label in (self.status,info)], add='+')

    def values(self):
        return tuple(self.entries[k].get() for k in self.entries) + (self.language.get(),)

    def dirty(self):
        return self.baseline is not None and self.values() != self.baseline

    def cancel_reload(self):
        self.pending_reload = False
        self.reload_button.configure(text='Reload')

    def load(self, force=False):
        self.cancel_reload()
        if not force and self.dirty():
            self.status.configure(text='Your settings draft is kept. Save it or Reload to use the saved preferences.')
            return
        try:
            saved = self.app.store.preferences()
        except sqlite3.Error:
            self.status.configure(text='Could not load settings. Your draft is kept; retry Reload.')
            return
        for key, entry in self.entries.items():
            entry.delete(0, 'end')
            entry.insert(0, str(saved[key]))
        self.language.set(saved['answer_language'])
        self.snapshot = saved
        self.baseline = self.values()
        self.status.configure(text='Saved preferences were invalid; safe defaults are shown. Save to repair them.' if saved['invalid'] else 'Saved settings loaded. Changes apply only after Save.')

    def reload(self):
        if self.dirty() and not self.pending_reload:
            self.pending_reload = True
            self.reload_button.configure(text='Confirm reload')
            self.status.configure(text='Click Confirm reload again to replace this draft with saved settings.')
            return
        self.load(force=True)

    def copy_tutor(self):
        self.cancel_reload()
        tutor = self.app.tutor_page
        if tutor.task is not None:
            self.status.configure(text='Wait for or stop the Tutor request before copying its choices.')
            return
        choices = {'ollama_endpoint': tutor.endpoint.get(),
                   'ollama_model': tutor.model.get() if tutor.model.get() in tutor.models else tutor.preferred_model}
        for key, value in choices.items():
            self.entries[key].delete(0, 'end')
            self.entries[key].insert(0, value)
        self.language.set(tutor.language.get())
        self.status.configure(text='Tutor choices copied into this draft. Save to remember them.')

    def save(self):
        self.cancel_reload()
        if self.snapshot is None:
            self.status.configure(text='Reload settings successfully before saving.')
            return
        try:
            try:
                focus = int(self.entries['focus_minutes'].get())
                goal = int(self.entries['daily_goal_minutes'].get())
            except ValueError:
                raise ValueError('Focus duration and daily goal must be whole numbers.') from None
            fields = preference_fields(focus, goal, self.entries['ollama_endpoint'].get(),
                                       self.entries['ollama_model'].get(), self.language.get())
            self.app.validate_preferences_change(fields)
            saved = self.app.store.save_preferences(fields, expected_revision=self.snapshot['revision'])
        except (ValueError, sqlite3.Error) as exc:
            self.status.configure(text=str(exc) if isinstance(exc, ValueError) else 'Could not save settings. Your draft is kept; retry Save.')
            return
        # The transaction has committed. Applying values performs no further reads.
        self.snapshot = saved
        self.app.apply_preferences(saved)
        for key, entry in self.entries.items():
            entry.delete(0, 'end')
            entry.insert(0, str(saved[key]))
        self.language.set(saved['answer_language'])
        self.baseline = self.values()
        self.status.configure(text='Settings saved. Active focus duration is unchanged. Ollama connects only when you choose Connect.')
