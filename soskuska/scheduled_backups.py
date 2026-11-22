"""Main-thread schedule controls and file-backed automatic-backup subprocess."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import date
from tkinter import filedialog
import customtkinter as ctk
from automatic_backup import load_config,save_config,due
from localization import tr
from theme import COLORS as C
from worker_command import worker_command


class ScheduledBackups(ctk.CTkFrame):
    def __init__(self,parent,app):
        super().__init__(parent,fg_color='transparent');self.app=app
        self.snapshot=None;self.baseline=None;self.busy=False;self.closed=False
        self.process=None;self.output=None;self.next_check=0;self.pending_reload=False;self.waiting_elsewhere=False
        self.grid_columnconfigure(0,weight=1)
        app.label(self,tr(app,'Daily local backups'),20,bold=True).grid(row=0,column=0,sticky='w',pady=(12,8))
        self.info=app.label(self,tr(app,'Opt in to one backup per local day while the app is open. Only saved data is copied. Existing backups are never deleted. This folder setting stays on this machine.'),12,'secondary',wraplength=600)
        self.info.grid(row=1,column=0,sticky='ew',pady=(0,10))
        self.enabled=ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self,text=tr(app,'Enable daily backups'),variable=self.enabled,font=app.font(),text_color=C['text']).grid(row=2,column=0,sticky='w',pady=(0,10))
        self.directory=ctk.CTkEntry(self,height=38,font=app.font())
        self.directory.grid(row=3,column=0,sticky='ew',pady=(0,10))
        self.choose_button=app.button(self,tr(app,'Choose backup folder…'),self.choose,width=190)
        self.choose_button.grid(row=4,column=0,sticky='w',pady=(0,10))
        actions=app.frame(self);actions.grid(row=5,column=0,sticky='w')
        self.save_button=app.button(actions,tr(app,'Save backup schedule'),self.save,width=185,primary=True);self.save_button.pack(side='left',padx=(0,8))
        self.reload_button=app.button(actions,tr(app,'Reload'),self.reload,width=100);self.reload_button.pack(side='left',padx=(0,8))
        self.retry_button=app.button(actions,tr(app,'Retry backup'),self.retry,width=120);self.retry_button.pack(side='left')
        self.status=app.label(self,'',12,'secondary',wraplength=600);self.status.grid(row=6,column=0,sticky='ew',pady=(10,4))
        self.runtime=app.label(self,'',12,'secondary',wraplength=600);self.runtime.grid(row=8,column=0,sticky='ew',pady=(6,0))
        self.last=app.label(self,'',12,'secondary',wraplength=600);self.last.grid(row=7,column=0,sticky='ew')
        self.load(force=True)
        self.bind('<Configure>',lambda e:[label.configure(wraplength=max(250,e.width-12)) for label in (self.info,self.status,self.last,self.runtime)],add='+')
        self.poll_id=self.after(1000,self.poll)

    def values(self):return (self.enabled.get(),self.directory.get())
    def dirty(self):return self.values()!=self.baseline
    def message(self,key,**values):self.status.configure(text=tr(self.app,key,**values))
    def runtime_message(self,key):self.runtime.configure(text=tr(self.app,key))
    def cancel_reload(self):
        self.pending_reload=False;self.reload_button.configure(text=tr(self.app,'Reload'))
    def load(self,force=False):
        self.cancel_reload()
        if not force and self.dirty():return
        try:saved=load_config(self.app.store.path)
        except (ValueError,OSError):
            self.message('Could not read backup settings. Your draft is kept; retry Reload.');return
        self.snapshot=saved;self.enabled.set(saved['enabled']);self.directory.delete(0,'end');self.directory.insert(0,saved['directory']);self.baseline=self.values()
        self.message('Invalid backup settings were disabled. Save to repair them.' if saved['invalid'] else 'Daily backups run only after you enable and save this schedule.')
        self.last.configure(text=tr(self.app,'Last automatic backup: {v0}',v0=saved['last_path']) if saved['last_path'] else tr(self.app,'No automatic backup recorded.'))
    def reload(self):
        if self.dirty() and not self.pending_reload:
            self.pending_reload=True;self.reload_button.configure(text=tr(self.app,'Confirm reload'));self.message('Click Confirm reload again to replace this draft with saved settings.');return
        self.load(force=True)
    def choose(self):
        self.cancel_reload()
        folder=filedialog.askdirectory(parent=self.app,title=tr(self.app,'Choose backup folder…'),mustexist=True)
        if folder:self.directory.delete(0,'end');self.directory.insert(0,folder)
    def save(self):
        self.cancel_reload()
        if self.busy:return
        if self.snapshot is None:
            self.message('Reload backup settings successfully before saving.');return
        try:saved=save_config(self.app.store.path,self.enabled.get(),self.directory.get(),self.snapshot['token'])
        except (ValueError,OSError) as exc:
            self.message(str(exc) if isinstance(exc,ValueError) else 'Could not save the backup schedule. Your draft is kept; retry Save.');return
        self.snapshot=saved;self.baseline=self.values();self.next_check=0
        self.message('Backup schedule saved. The next check runs while the app is open.')
        if not saved['enabled']:self.app.backup_notice.grid_remove()
    def retry(self):self.next_check=0
    def launch(self):
        self.busy=True;self.started=time.monotonic();self.runtime_message('Creating the daily backup. Wait before closing.')
        self.save_button.configure(state='disabled');self.retry_button.configure(state='disabled')
        try:
            self.output=tempfile.TemporaryFile()
            self.process=subprocess.Popen(worker_command('backup','automatic',self.app.store.path),stdin=subprocess.DEVNULL,stdout=self.output,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
        except OSError:self.complete('error',None)
    def complete(self,state,value):
        self.busy=False;self.process=None
        if self.output is not None:
            try:self.output.close()
            except OSError:pass
            self.output=None
        self.save_button.configure(state='normal');self.retry_button.configure(state='normal')
        if state!='done':
            self.next_check=time.monotonic()+900;self.runtime_message('Daily backup failed. Check the folder and free space, then Retry backup.')
            self.app.backup_notice.configure(text=tr(self.app,'Daily backup failed. Open Settings to retry.'));self.app.backup_notice.grid(row=1,column=0,columnspan=2,sticky='ew',padx=12,pady=6)
            return
        self.next_check=time.monotonic()+60
        self.app.backup_notice.grid_remove()
        self.waiting_elsewhere=value['state']=='busy'
        if value['state']=='busy':self.runtime_message('Another window is backing up. Retry after it finishes.')
        elif value['state']=='skipped':self.runtime_message('No daily backup needed now; the schedule will be checked again.')
        elif value['state']=='created':
            self.last.configure(text=tr(self.app,'Last automatic backup: {v0}',v0=value['path']))
            self.runtime_message('Daily backup saved. Existing backup files were kept.')
    def poll(self):
        if self.closed:return
        try:
            if self.process is not None:
                if self.process.poll() is not None:
                    try:
                        self.output.seek(0)
                        state,value=json.loads(self.output.read(1024*1024))
                        if state not in ('done','error') or (state=='done' and (not isinstance(value,dict) or value.get('state') not in ('created','skipped','busy'))):raise ValueError()
                    except (ValueError,UnicodeError,OSError):state,value='error',None
                    self.complete(state,value)
                elif time.monotonic()-self.started>90:self.process.kill()
            elif time.monotonic()>=self.next_check:
                self.next_check=time.monotonic()+60
                manual=self.app.settings_page.backups
                if self.app.data_restoring or manual.busy or manual.pending is not None or self.app.question_bank.importer.saving or self.app.flashcard_page.importer.saving:return
                saved=load_config(self.app.store.path)
                if due(saved,date.today()):self.launch()
                else:
                    if saved['last_path']:self.last.configure(text=tr(self.app,'Last automatic backup: {v0}',v0=saved['last_path']))
                    if self.waiting_elsewhere:
                        self.waiting_elsewhere=False;self.runtime_message('No daily backup needed now; the schedule will be checked again.')
        except (OSError,ValueError,sqlite3.Error):
            self.next_check=time.monotonic()+900;self.runtime_message('Could not read backup settings. Your draft is kept; retry Reload.')
        finally:
            if not self.closed:self.poll_id=self.after(250,self.poll)
    def destroy(self):
        self.closed=True
        if self.process is not None and self.process.poll() is None:self.process.kill()
        if self.output is not None:self.output.close()
        if getattr(self,'poll_id',None):self.after_cancel(self.poll_id)
        super().destroy()
