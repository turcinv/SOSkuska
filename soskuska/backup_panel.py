from worker_command import worker_command
"""Main-thread backup/restore controls with worker-owned SQLite connections."""
from localization import tr
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk



class BackupPanel(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color='transparent')
        self.app = app
        self.busy = False
        self.kind = None
        self.pending = None
        self.process = None
        self.output = None
        self.validation_temp = None
        self.validation_cancelled = False
        self.closed = False
        self.grid_columnconfigure(0, weight=1)
        app.label(self, tr(self.app, 'Backup and restore'), 20, bold=True).grid(row=0, column=0, sticky='w', pady=(12, 8))
        self.status = app.label(self, tr(self.app, 'Backups contain saved data and preferences, including saved AI conversations, not unsaved drafts. Restore replaces saved data and closes the app. Only schema 9 backups are supported.'), 12, 'secondary', wraplength=600)
        self.status.grid(row=1, column=0, sticky='ew', pady=(0, 12))
        actions = app.frame(self)
        actions.grid(row=2, column=0, sticky='w')
        self.create_button = app.button(actions, tr(self.app, 'Create backup'), self.create, primary=True, width=135)
        self.create_button.pack(side='left', padx=(0, 8))
        self.restore_button = app.button(actions, tr(self.app, 'Choose backup…'), self.choose, width=145)
        self.restore_button.pack(side='left')
        self.confirmation = app.frame(self)
        self.confirmation.grid(row=3, column=0, sticky='ew', pady=(12, 0))
        self.confirmation.grid_remove()
        app.label(self.confirmation, tr(self.app, 'Restore replaces all saved data and preferences. Unsaved forms will be lost; saved conversations are replaced by those in the backup. The app will close; reopen it afterward. A safety copy is saved beside the database in backups/.'), 12, 'secondary', wraplength=600).pack(anchor='w', pady=(0, 8))
        self.confirm_button = app.button(self.confirmation, tr(self.app, 'Confirm restore and close'), self.confirm, width=210)
        self.confirm_button.pack(side='left', padx=(0, 8))
        self.cancel_button = app.button(self.confirmation, tr(self.app, 'Cancel'), self.cancel_pending, width=90)
        self.cancel_button.pack(side='left')
        self.bind('<Configure>', lambda event: self.status.configure(wraplength=max(250,event.width-12)), add='+')
        self.poll_id = self.after(50, self.poll)

    def cancel_pending(self):
        if self.kind == 'validate':
            self.validation_cancelled = True
        if self.pending is not None:
            self.pending.close()
            self.pending = None
            self.status.configure(text=tr(self.app, 'Restore cancelled. Your saved data is unchanged.'))
        self.confirmation.grid_remove()

    def guard_restore(self):
        if self.app.session_open:
            raise ValueError('Finish the current focus session before restoring.')
        if self.app.tutor_page.unsaved_reply:
            raise ValueError('Retry save reply or Discard unsaved in AI Tutor before restoring.')
        if self.app.tutor_page.task is not None:
            raise ValueError('Wait for or stop the Tutor request before restoring.')
        if self.app.store.active_practice() is not None:
            raise ValueError('Finish or discard the current practice test before restoring.')

    def launch(self, kind, active, selected):
        self.busy = True
        self.kind = kind
        for button in (self.create_button, self.restore_button, self.confirm_button, self.cancel_button):
            button.configure(state='disabled')
        self.status.configure(text=tr(self.app, 'Working… Wait for completion before closing. Backup and validation leave other screens usable.'))
        try:
            command = worker_command('backup',kind,active,selected)
            if kind == 'validate':
                self.validation_cancelled = False
                self.validation_temp = tempfile.TemporaryDirectory(prefix='soskuska-selection-')
                command += ['--staging',str(Path(self.validation_temp.name)/'validated.sqlite3')]
                self.selected_source = Path(selected)
            self.started = time.monotonic()
            self.output = tempfile.TemporaryFile()
            self.process = subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=self.output,stderr=subprocess.DEVNULL,
                                            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        except OSError as exc:
            if self.output is not None:
                self.output.close()
                self.output = None
            self.complete('error',str(exc))

    def create(self):
        if self.busy:
            return
        self.cancel_pending()
        selected = filedialog.asksaveasfilename(parent=self.app, title=tr(self.app, 'Create SOSkúška backup'),
                    initialfile='SOSkuska-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.sqlite3',
                    defaultextension='.sqlite3', filetypes=[(tr(self.app,'SQLite database'), '*.sqlite3'), (tr(self.app,'All files'), '*')])
        if selected:
            active = self.app.store.path
            self.launch('backup', active, selected)

    def choose(self):
        if self.busy:
            return
        self.cancel_pending()
        try:
            self.guard_restore()
        except Exception as exc:
            self.status.configure(text=tr(self.app, str(exc)))
            return
        selected = filedialog.askopenfilename(parent=self.app, title=tr(self.app, 'Choose SOSkúška backup'),
                    filetypes=[(tr(self.app,'SQLite database'), '*.sqlite3'), (tr(self.app,'All files'), '*')])
        if selected:
            active = self.app.store.path
            self.launch('validate', active, selected)

    def confirm(self):
        if self.busy or self.pending is None:
            return
        try:
            self.guard_restore()  # State may have changed since validation.
        except Exception as exc:
            self.status.configure(text=tr(self.app, str(exc)))
            return
        active = self.app.store.path
        prepared = self.pending
        self.pending = None
        self.confirmation.grid_remove()
        # Keep callbacks from reading a closed Store; modal blocks editing until close.
        self.busy = True
        self.app.data_restoring = True
        self.modal = ctk.CTkToplevel(self.app)
        self.modal.title(tr(self.app, 'Restoring saved data'))
        self.modal.geometry('440x170')
        self.app.label(self.modal, tr(self.app, 'Restoring… Please wait. The app will close when finished.'), 14, wraplength=390).pack(padx=20,pady=35)
        self.modal.protocol('WM_DELETE_WINDOW', lambda: None)
        self.modal.grab_set()
        self.app.store.close()
        self.restoring_selection = prepared
        self.launch('restore', active, prepared.path)

    def poll(self):
        if self.closed:
            return
        process = self.process
        if process is not None:
            if process.poll() is not None:
                self.output.seek(0)
                output = self.output.read(1024*1024)
                self.output.close()
                self.output = None
                self.process = None
                try:
                    state, value = json.loads(output)
                except (ValueError, UnicodeError):
                    state, value = 'error', 'The database helper stopped unexpectedly. Reopen the app to inspect saved data.'
                self.complete(state,value)
                if self.closed:
                    return
            elif time.monotonic()-self.started > 90:
                process.kill()
                # Reap on the next tick rather than waiting on Tk's thread.
        self.poll_id = self.after(50, self.poll)

    def complete(self, state, value):
        kind = self.kind
        self.kind = None
        if kind == 'restore':
            # Keep close/Quit blocked through the nested result-dialog event loop.
            self.restoring_selection.close()
            try:
                if state == 'done':
                    messagebox.showinfo(tr(self.app,'Restore complete'), tr(self.app,f'Saved data restored. Reopen SOSkúška to load it.\nSafety copy: {value}'), parent=self.modal)
                else:
                    messagebox.showerror(tr(self.app,'Restore failed'), tr(self.app,f'{tr(self.app,value)}\nThe app will close. Reopen to retry; any safety copy remains in the database’s backups folder.'), parent=self.modal)
            finally:
                self.busy = False
                self.app.data_restoring = False
                self.app.close()
            return
        self.busy = False
        for button in (self.create_button, self.restore_button, self.confirm_button, self.cancel_button):
            button.configure(state='normal')
        if state == 'error':
            self.status.configure(text=tr(self.app,'Could not complete the operation: ')+tr(self.app,value))
        elif kind == 'backup':
            self.status.configure(text=tr(self.app, 'Backup created: {v0}', v0=value))
        elif self.app.current_page != 'Settings' or self.validation_cancelled:
            self.status.configure(text=tr(self.app, 'Validation cancelled after navigation. Choose the backup again to restore.'))
        else:
            temp = self.validation_temp
            self.validation_temp = None
            def cleanup():
                try:temp.cleanup()
                except OSError:pass
            self.pending = SimpleNamespace(path=Path(temp.name)/'validated.sqlite3',source=self.selected_source,counts=value,close=cleanup)
            self.status.configure(text=tr(self.app, 'Validated {v0}: {v1} subjects, {v2} questions, {v3} focus sessions, {v4} cards. Confirm below to replace current data.', v0=self.pending.source.name, v1=value['subjects'], v2=value['questions'], v3=value['sessions'], v4=value['flashcards']))
            self.confirmation.grid()
        if self.validation_temp is not None:
            try:self.validation_temp.cleanup()
            except OSError:pass
            self.validation_temp = None

    def destroy(self):
        self.closed = True
        if self.process is not None and self.process.poll() is None:
            self.process.kill()
        self.cancel_pending()
        if self.output is not None:
            self.output.close()
            self.output = None
        if self.validation_temp is not None:
            try:self.validation_temp.cleanup()
            except OSError:pass
            self.validation_temp = None
        if getattr(self, 'poll_id', None):
            self.after_cancel(self.poll_id)
        super().destroy()
