"""Persistent preferences with explicit Save, stale-write checks and kept drafts."""
from theme import COLORS as C
from localization_widgets import LocalizedOptionMenu
from localization import tr
from panel_layout import wrap_labels, responsive_actions
import sqlite3

import customtkinter as ctk
from preferences import preference_fields, UI_LANGUAGES, APPEARANCE_MODES
from tutor import LANGUAGES
from backup_panel import BackupPanel
from scheduled_backups import ScheduledBackups


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color='transparent', corner_radius=0)
        self.app = app
        self.snapshot = None
        self.baseline = None
        self.pending_reload = False
        self.grid_columnconfigure(0, weight=1)
        header=app.frame(self,card=True)
        header.grid(row=0,column=0,sticky='ew',pady=(0,16));header.grid_columnconfigure(0,weight=1)
        app.label(header,tr(app,'Settings'),28,bold=True).grid(row=0,column=0,sticky='w',padx=18,pady=(16,6))
        self.status=app.label(header,tr(app,'Preferences stay on this device. Save to apply and remember them.'),13,'secondary')
        self.status.grid(row=1,column=0,sticky='ew',padx=18,pady=(0,16));wrap_labels(header,app)
        self.preferences_grid=app.frame(self)
        self.preferences_grid.grid(row=1,column=0,sticky='ew')
        study=app.frame(self.preferences_grid,card=True);study.grid_columnconfigure(0,weight=1)
        app.label(study,tr(app,'Study'),18,bold=True).grid(row=0,column=0,sticky='w',padx=18,pady=(16,12))
        self.entries={}
        for index,(key,title) in enumerate([('focus_minutes','Focus duration (1–180 minutes; next session)'),('daily_goal_minutes','Daily focus goal (1–1,440 minutes)')]):
            app.label(study,tr(app,title),12,'secondary').grid(row=1+index*2,column=0,sticky='ew',padx=18,pady=(0,4))
            entry=ctk.CTkEntry(study,height=38,font=app.font(),placeholder_text_color=C['secondary'])
            entry.grid(row=2+index*2,column=0,sticky='ew',padx=18,pady=(0,16));self.entries[key]=entry
        interface=app.frame(self.preferences_grid,card=True);interface.grid_columnconfigure(0,weight=1)
        app.label(interface,tr(app,'Interface'),18,bold=True).grid(row=0,column=0,sticky='w',padx=18,pady=(16,12))
        app.label(interface,tr(app,'Interface language (applies after restart)'),12,'secondary').grid(row=1,column=0,sticky='ew',padx=18,pady=(0,4))
        self.ui_language=ctk.StringVar(value=app.preferences.get('ui_language','English'))
        self.ui_language_menu=LocalizedOptionMenu(interface,owner=app,variable=self.ui_language,translate_values='language_names',values=list(UI_LANGUAGES),dynamic_resizing=False,height=38,font=app.font())
        self.ui_language_menu.grid(row=2,column=0,sticky='ew',padx=18,pady=(0,12))
        app.label(interface,tr(app,'Appearance (applies on Save)'),12,'secondary').grid(row=3,column=0,sticky='ew',padx=18,pady=(0,4))
        self.appearance_mode=ctk.StringVar(value=app.preferences.get('appearance_mode','Dark'))
        self.appearance_menu=LocalizedOptionMenu(interface,owner=app,variable=self.appearance_mode,values=list(APPEARANCE_MODES),dynamic_resizing=False,height=38,font=app.font())
        self.appearance_menu.grid(row=4,column=0,sticky='ew',padx=18,pady=(0,12))
        app.label(interface,tr(app,'System follows Windows/macOS appearance; on Linux it uses Light.'),12,'secondary').grid(row=5,column=0,sticky='ew',padx=18,pady=(0,16))
        self.preference_cards=(study,interface);self.preference_columns=None
        for card in self.preference_cards:
            wrap_labels(card,app,source=self.preferences_grid,columns=lambda width:2 if width>=950 else 1)
        self.preferences_grid.bind('<Configure>',self.layout_preferences,add='+')
        ai=app.frame(self,card=True);ai.grid(row=2,column=0,sticky='ew',pady=(0,16));ai.grid_columnconfigure(0,weight=1)
        app.label(ai,tr(app,'AI Tutor'),18,bold=True).grid(row=0,column=0,sticky='w',padx=18,pady=(16,12))
        for index,(key,title) in enumerate([('ollama_endpoint','Ollama server URL'),('ollama_model','Preferred model name (optional; checked when you connect)')]):
            app.label(ai,tr(app,title),12,'secondary').grid(row=1+index*2,column=0,sticky='ew',padx=18,pady=(0,4))
            entry=ctk.CTkEntry(ai,height=38,font=app.font(),placeholder_text_color=C['secondary'])
            entry.grid(row=2+index*2,column=0,sticky='ew',padx=18,pady=(0,12));self.entries[key]=entry
        app.label(ai,tr(app,'AI answer language'),12,'secondary').grid(row=5,column=0,sticky='ew',padx=18,pady=(0,4))
        self.language=ctk.StringVar(value='Automatic')
        self.language_menu=LocalizedOptionMenu(ai,owner=app,variable=self.language,values=list(LANGUAGES),dynamic_resizing=False,height=38,font=app.font())
        self.language_menu.grid(row=6,column=0,sticky='ew',padx=18,pady=(0,12))
        app.label(ai,tr(app,'Saving never connects to Ollama. AI conversations are saved locally and included in backups. Active focus sessions keep their original duration. Use New chat before switching an existing chat to a different server.'),12,'secondary').grid(row=7,column=0,sticky='ew',padx=18,pady=(0,16));wrap_labels(ai,app)
        footer=app.frame(self,card=True);footer.grid(row=3,column=0,sticky='ew',pady=(0,16));footer.grid_columnconfigure(0,weight=1)
        actions=app.frame(footer);actions.grid(row=0,column=0,sticky='ew',padx=18,pady=(16,4))
        self.save_button=app.button(actions,tr(app,'Save settings'),self.save,primary=True,width=125)
        self.reload_button=app.button(actions,tr(app,'Reload'),self.reload,width=110)
        self.copy_button=app.button(actions,tr(app,'Use Tutor choices'),self.copy_tutor,width=155)
        responsive_actions(actions,app,(self.save_button,self.reload_button,self.copy_button))
        self.feedback=app.label(footer,self.status.cget('text'),12,'secondary')
        self.feedback.grid(row=1,column=0,sticky='ew',padx=18,pady=(0,16));wrap_labels(footer,app)
        self.schedule=ScheduledBackups(self,app);self.schedule.grid(row=4,column=0,sticky='ew',pady=(0,16))
        self.backups=BackupPanel(self,app);self.backups.grid(row=5,column=0,sticky='ew')
        self.baseline=self.values()

    def layout_preferences(self,event):
        columns=2 if self.app.scroll.logical_pixels(event.width)>=950 else 1
        if columns==self.preference_columns:return
        self.preference_columns=columns
        for col in range(2):
            self.preferences_grid.grid_columnconfigure(col,weight=1 if col<columns else 0,uniform='settings' if col<columns else '')
        for index,card in enumerate(self.preference_cards):
            card.grid(row=index//columns,column=index%columns,sticky='nsew',padx=(0,12) if columns==2 and index==0 else 0,pady=(0,16))

    def set_status(self,text):
        self.status.configure(text=text)
        self.feedback.configure(text=text)

    def values(self):
        return tuple(self.entries[k].get() for k in self.entries) + (self.language.get(), self.ui_language.get(), self.appearance_mode.get())

    def dirty(self):
        return self.baseline is not None and self.values() != self.baseline

    def cancel_reload(self):
        self.pending_reload = False
        self.reload_button.configure(text=tr(self.app, 'Reload'))

    def load(self, force=False):
        self.schedule.load()
        self.cancel_reload()
        if not force and self.dirty():
            self.set_status(tr(self.app, 'Your settings draft is kept. Save it or Reload to use the saved preferences.'))
            return
        try:
            saved = self.app.store.preferences()
        except sqlite3.Error:
            self.set_status(tr(self.app, 'Could not load settings. Your draft is kept; retry Reload.'))
            return
        for key, entry in self.entries.items():
            entry.delete(0, 'end')
            entry.insert(0, str(saved[key]))
        self.language.set(saved['answer_language'])
        self.ui_language.set(saved['ui_language'])
        self.appearance_mode.set(saved['appearance_mode'])
        self.snapshot = saved
        self.baseline = self.values()
        self.set_status(tr(self.app,tr(self.app, 'Saved preferences were invalid; safe defaults are shown. Save to repair them.') if saved['invalid'] else tr(self.app, 'Saved settings loaded. Changes apply only after Save.')))

    def reload(self):
        if self.dirty() and not self.pending_reload:
            self.pending_reload = True
            self.reload_button.configure(text=tr(self.app, 'Confirm reload'))
            self.set_status(tr(self.app, 'Click Confirm reload again to replace this draft with saved settings.'))
            return
        self.load(force=True)

    def copy_tutor(self):
        self.cancel_reload()
        tutor = self.app.tutor_page
        if tutor.task is not None:
            self.set_status(tr(self.app, 'Wait for or stop the Tutor request before copying its choices.'))
            return
        choices = {'ollama_endpoint': tutor.endpoint.get(),
                   'ollama_model': tutor.model.get() if tutor.model.get() in tutor.models else tutor.preferred_model}
        for key, value in choices.items():
            self.entries[key].delete(0, 'end')
            self.entries[key].insert(0, value)
        self.language.set(tutor.language.get())
        self.set_status(tr(self.app, 'Tutor choices copied into this draft. Save to remember them.'))

    def save(self):
        self.cancel_reload()
        if self.snapshot is None:
            self.set_status(tr(self.app, 'Reload settings successfully before saving.'))
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
            self.set_status(tr(self.app,tr(self.app, str(exc)) if isinstance(exc, ValueError) else tr(self.app, 'Could not save settings. Your draft is kept; retry Save.')))
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
        self.set_status(tr(self.app, 'Settings saved. Appearance applied. Restart the app to apply an interface language change. Active focus duration is unchanged; Ollama connects only after Connect.'))
