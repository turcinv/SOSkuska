"""Persistent preferences with explicit Save, stale-write checks and kept drafts."""
from theme import COLORS as C
from localization_widgets import LocalizedOptionMenu
from localization import tr
import sqlite3

import customtkinter as ctk
from preferences import preference_fields, UI_LANGUAGES, APPEARANCE_MODES
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
        app.label(self, tr(self.app, 'Settings'), 28, bold=True).grid(row=0, column=0, sticky='w')
        self.status = app.label(self, tr(self.app, 'Preferences stay on this device. Save to apply and remember them.'), 13, 'secondary', wraplength=600)
        self.status.grid(row=1, column=0, sticky='ew', pady=(6, 16))
        self.entries = {}
        labels = [('focus_minutes','Focus duration (1–180 minutes; next session)'),
                  ('daily_goal_minutes','Daily focus goal (1–1,440 minutes)'),
                  ('ollama_endpoint','Ollama server URL'),
                  ('ollama_model','Preferred model name (optional; checked when you connect)')]
        for index, (key, title) in enumerate(labels):
            app.label(self, tr(self.app,title), 13, 'secondary').grid(row=2+index*2, column=0, sticky='w', pady=(4, 4))
            entry = ctk.CTkEntry(self, height=38, font=app.font(), placeholder_text_color=C["secondary"])
            entry.grid(row=3+index*2, column=0, sticky='ew', pady=(0, 10))
            self.entries[key] = entry
        app.label(self, tr(self.app, 'AI answer language'), 13, 'secondary').grid(row=10, column=0, sticky='w', pady=(4, 4))
        self.language = ctk.StringVar(value='Automatic')
        self.language_menu = LocalizedOptionMenu(self,owner=self.app, variable=self.language, values=list(LANGUAGES), dynamic_resizing=False, height=38, font=app.font())
        self.language_menu.grid(row=11, column=0, sticky='ew', pady=(0, 14))
        app.label(self, tr(self.app, 'Interface language (applies after restart)'), 13, 'secondary').grid(row=12,column=0,sticky='w',pady=(4,4))
        self.ui_language = ctk.StringVar(value=app.preferences.get('ui_language','English'))
        self.ui_language_menu = LocalizedOptionMenu(self,owner=self.app,variable=self.ui_language,translate_values="language_names",values=list(UI_LANGUAGES),dynamic_resizing=False,height=38,font=app.font())
        self.ui_language_menu.grid(row=13,column=0,sticky='ew',pady=(0,14))
        app.label(self, tr(self.app, 'Appearance (applies on Save)'), 13, 'secondary').grid(row=14,column=0,sticky='w',pady=(4,4))
        self.appearance_mode = ctk.StringVar(value=app.preferences.get('appearance_mode','Dark'))
        self.appearance_menu = LocalizedOptionMenu(self,owner=app,variable=self.appearance_mode,
            values=list(APPEARANCE_MODES),dynamic_resizing=False,height=38,font=app.font())
        self.appearance_menu.grid(row=15,column=0,sticky='ew',pady=(0,14))
        app.label(self, tr(self.app, 'System follows Windows/macOS appearance; on Linux it uses Light.'), 12, 'secondary', wraplength=600).grid(row=16,column=0,sticky='ew',pady=(0,14))
        info = app.label(self, tr(self.app, 'Saving never connects to Ollama. AI conversations are saved locally and included in backups. Active focus sessions keep their original duration. Use New chat before switching an existing chat to a different server.'), 12, 'secondary', wraplength=600)
        info.grid(row=17, column=0, sticky='ew', pady=(0, 14))
        actions = app.frame(self)
        actions.grid(row=18, column=0, sticky='w')
        self.save_button = app.button(actions, tr(self.app, 'Save settings'), self.save, primary=True, width=125)
        self.save_button.pack(side='left', padx=(0, 8))
        self.reload_button = app.button(actions, tr(self.app, 'Reload'), self.reload, width=110)
        self.reload_button.pack(side='left', padx=(0, 8))
        self.copy_button = app.button(actions, tr(self.app, 'Use Tutor choices'), self.copy_tutor, width=155)
        self.copy_button.pack(side='left')
        self.backups = BackupPanel(self, app)
        self.backups.grid(row=19, column=0, sticky='ew', pady=(20, 0))
        self.baseline = self.values()  # Even a failed first read must preserve later edits.
        self.bind('<Configure>', lambda event: [label.configure(wraplength=max(250,event.width-12)) for label in (self.status,info)], add='+')

    def values(self):
        return tuple(self.entries[k].get() for k in self.entries) + (self.language.get(), self.ui_language.get(), self.appearance_mode.get())

    def dirty(self):
        return self.baseline is not None and self.values() != self.baseline

    def cancel_reload(self):
        self.pending_reload = False
        self.reload_button.configure(text=tr(self.app, 'Reload'))

    def load(self, force=False):
        self.cancel_reload()
        if not force and self.dirty():
            self.status.configure(text=tr(self.app, 'Your settings draft is kept. Save it or Reload to use the saved preferences.'))
            return
        try:
            saved = self.app.store.preferences()
        except sqlite3.Error:
            self.status.configure(text=tr(self.app, 'Could not load settings. Your draft is kept; retry Reload.'))
            return
        for key, entry in self.entries.items():
            entry.delete(0, 'end')
            entry.insert(0, str(saved[key]))
        self.language.set(saved['answer_language'])
        self.ui_language.set(saved['ui_language'])
        self.appearance_mode.set(saved['appearance_mode'])
        self.snapshot = saved
        self.baseline = self.values()
        self.status.configure(text=tr(self.app,tr(self.app, 'Saved preferences were invalid; safe defaults are shown. Save to repair them.') if saved['invalid'] else tr(self.app, 'Saved settings loaded. Changes apply only after Save.')))

    def reload(self):
        if self.dirty() and not self.pending_reload:
            self.pending_reload = True
            self.reload_button.configure(text=tr(self.app, 'Confirm reload'))
            self.status.configure(text=tr(self.app, 'Click Confirm reload again to replace this draft with saved settings.'))
            return
        self.load(force=True)

    def copy_tutor(self):
        self.cancel_reload()
        tutor = self.app.tutor_page
        if tutor.task is not None:
            self.status.configure(text=tr(self.app, 'Wait for or stop the Tutor request before copying its choices.'))
            return
        choices = {'ollama_endpoint': tutor.endpoint.get(),
                   'ollama_model': tutor.model.get() if tutor.model.get() in tutor.models else tutor.preferred_model}
        for key, value in choices.items():
            self.entries[key].delete(0, 'end')
            self.entries[key].insert(0, value)
        self.language.set(tutor.language.get())
        self.status.configure(text=tr(self.app, 'Tutor choices copied into this draft. Save to remember them.'))

    def save(self):
        self.cancel_reload()
        if self.snapshot is None:
            self.status.configure(text=tr(self.app, 'Reload settings successfully before saving.'))
            return
        try:
            try:
                focus = int(self.entries['focus_minutes'].get())
                goal = int(self.entries['daily_goal_minutes'].get())
            except ValueError:
                raise ValueError('Focus duration and daily goal must be whole numbers.') from None
            fields = preference_fields(focus, goal, self.entries['ollama_endpoint'].get(),
                                       self.entries['ollama_model'].get(), self.language.get(), self.ui_language.get(), self.appearance_mode.get())
            self.app.validate_preferences_change(fields)
            saved = self.app.store.save_preferences(fields, expected_revision=self.snapshot['revision'])
        except (ValueError, sqlite3.Error) as exc:
            self.status.configure(text=tr(self.app,tr(self.app, str(exc)) if isinstance(exc, ValueError) else tr(self.app, 'Could not save settings. Your draft is kept; retry Save.')))
            return
        # The transaction has committed. Applying values performs no further reads.
        self.snapshot = saved
        self.app.apply_preferences(saved)
        for key, entry in self.entries.items():
            entry.delete(0, 'end')
            entry.insert(0, str(saved[key]))
        self.language.set(saved['answer_language'])
        self.ui_language.set(saved['ui_language'])
        self.appearance_mode.set(saved['appearance_mode'])
        self.baseline = self.values()
        self.status.configure(text=tr(self.app, 'Settings saved. Appearance applied. Restart the app to apply an interface language change. Active focus duration is unchanged; Ollama connects only after Connect.'))
