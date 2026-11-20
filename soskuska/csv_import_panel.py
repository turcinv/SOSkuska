"""Shared question/flashcard CSV preview and isolated jobs, owned by Tk."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk


class CsvImportPanel(ctk.CTkFrame):
    cards = False
    noun = "questions"
    def __init__(self,parent,app,bank,*,cards=False):
        super().__init__(parent,fg_color='transparent')
        self.cards=cards;self.noun="flashcards" if cards else "questions"
        self.app=app;self.bank=bank;self.process=None;self.output=None;self.payload=None
        self.preview=None;self.position=0;self.kind=None;self.subject_id=None;self.subject_name='';self.closed=False;self.abandoned=[];self.saved_message=None
        self.grid_columnconfigure(0,weight=1)
        self.heading=app.label(self,f'Import {self.noun} from CSV',20,bold=True,wraplength=600)
        self.heading.grid(row=0,column=0,sticky='ew',pady=(0,8))
        self.status=app.label(self,f'Choose a UTF-8 comma-separated CSV. Maximum 2 MiB / 500 {self.noun}. Nothing is saved until Import all is confirmed.',12,'secondary',wraplength=600)
        self.status.grid(row=1,column=0,sticky='ew',pady=(0,10))
        actions=app.frame(self);actions.grid(row=2,column=0,sticky='w',pady=(0,10))
        self.choose_button=app.button(actions,'Choose CSV…',self.choose,primary=True,width=125);self.choose_button.pack(side='left',padx=(0,8))
        self.template_button=app.button(actions,'Save CSV template',self.save_template,width=155);self.template_button.pack(side='left',padx=(0,8))
        self.cancel_button=app.button(actions,'Close import',self.cancel,width=115);self.cancel_button.pack(side='left')
        self.errors=ctk.CTkTextbox(self,height=95,font=app.font(),wrap='word',state='disabled')
        self.errors.grid(row=3,column=0,sticky='ew',pady=(0,10));self.errors.grid_remove()
        self.record_label=app.label(self,'',13,'secondary');self.record_label.grid(row=4,column=0,sticky='w')
        self.details=ctk.CTkTextbox(self,height=215,font=app.font(),wrap='word',state='disabled')
        self.details.grid(row=5,column=0,sticky='ew',pady=(4,10))
        pages=app.frame(self);pages.grid(row=6,column=0,sticky='w',pady=(0,10))
        self.previous_button=app.button(pages,'Previous',lambda:self.move(-1),width=100);self.previous_button.pack(side='left',padx=(0,8))
        self.next_button=app.button(pages,'Next',lambda:self.move(1),width=90);self.next_button.pack(side='left')
        save=app.frame(self);save.grid(row=7,column=0,sticky='w')
        self.import_button=app.button(save,'Import all',self.save,primary=True,width=135);self.import_button.pack(side='left',padx=(0,8))
        self.refresh_button=app.button(save,'Refresh totals',self.refresh_totals,width=145);self.refresh_button.pack(side='left')
        self.buttons=(self.choose_button,self.template_button,self.cancel_button,self.import_button,self.previous_button,self.next_button,self.refresh_button)
        self.bind('<Configure>',lambda event:[label.configure(wraplength=max(250,event.width-12)) for label in (self.heading,self.status)],add='+')
        self.controls();self.poll_id=self.after(50,self.poll)

    @property
    def saving(self):
        return self.kind=='save'

    def text(self,widget,value):
        widget.configure(state='normal');widget.delete('1.0','end');widget.insert('1.0',value);widget.configure(state='disabled')

    def controls(self):
        busy=self.process is not None
        for button in self.buttons:button.configure(state='disabled' if busy else 'normal')
        self.cancel_button.configure(state='disabled' if self.saving else 'normal')
        rows=self.preview['rows'] if self.preview else []
        self.import_button.configure(state='normal' if rows and not self.preview['errors'] and not busy else 'disabled')
        self.previous_button.configure(state='normal' if rows and self.position>0 and not busy else 'disabled')
        self.next_button.configure(state='normal' if rows and self.position+1<len(rows) and not busy else 'disabled')

    def open(self):
        if self.saving:return
        self.cancel()
        subject=self.bank.deck_snapshot if self.cards else self.bank.subject_snapshot
        if subject is None:
            self.bank.status.configure(text='This deck no longer exists.' if self.cards else 'This subject no longer exists.');return
        self.subject_id=subject['id'];self.subject_name=subject['name']
        self.heading.configure(text=f'Import into {self.subject_name}')
        self.status.configure(text=f'Save the header-only template, fill it in, then Choose CSV. Preview every record before Import all. Exact duplicates are rejected; existing {self.noun} are never changed.')
        self.grid();self.app.scroll._parent_canvas.yview_moveto(0)

    def cancel(self):
        if self.saving:return
        if self.process is not None:
            self.process.kill()
            # poll() reaps it later; cancelled results cannot resurrect the preview.
            self.abandoned.append((self.process,self.output));self.process=None;self.output=None
        self.preview=None;self.kind=None;self.position=0;self.saved_message=None
        self.text(self.details,'');self.text(self.errors,'');self.errors.grid_remove();self.record_label.configure(text='')
        self.controls();self.grid_remove()

    def launch(self,kind,selected):
        self.kind=kind
        self.status.configure(text=f'Importing all {self.noun}… Wait for completion before closing.' if kind=='save' else 'Reading and validating… You can cancel or navigate away.')
        try:
            command=[sys.executable,'-u',str(Path(__file__).with_name('flashcard_csv_import_worker.py' if self.cards else 'csv_import_worker.py')),kind,str(self.app.store.path),str(selected),
                     '--deck-id' if self.cards else '--subject-id',str(self.subject_id),f'--{"deck" if self.cards else "subject"}-name={self.subject_name}']
            self.output=tempfile.TemporaryFile();self.started=time.monotonic()
            self.process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=self.output,stderr=subprocess.DEVNULL,
                                         creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
        except OSError as exc:
            if self.output is not None:self.output.close();self.output=None
            self.process=None;self.complete({'state':'error','value':str(exc)})
        self.controls()

    def choose(self):
        if self.process is not None:return
        selected=filedialog.askopenfilename(parent=self.app,title=f'Choose {self.noun} CSV',filetypes=[('CSV file','*.csv'),('All files','*')])
        if not selected:return
        # A new selection always invalidates the old batch before any fallible work.
        self.preview=None;self.position=0;self.saved_message=None
        self.text(self.details,'');self.text(self.errors,'');self.errors.grid_remove()
        self.record_label.configure(text='');self.controls()
        # Capture the target already displayed by the host. The read-only helper
        # rechecks identity/name; a locked database must not block the Tk callback.
        subject=self.bank.deck_snapshot if self.cards else self.bank.subject_snapshot
        if subject is None or subject['id']!=(self.bank.deck_id if self.cards else self.bank.subject_id):
            self.status.configure(text='Reopen the deck before choosing another CSV.' if self.cards else 'Reload the question bank before choosing another CSV.');return
        self.subject_id=subject['id'];self.subject_name=subject['name']
        self.heading.configure(text=f'Import into {self.subject_name}')
        self.launch('parse',selected)

    def save_template(self):
        if self.process is not None:return
        selected=filedialog.asksaveasfilename(parent=self.app,title='Save header-only CSV template',initialfile='flashcards-template.csv' if self.cards else 'questions-template.csv',
                     defaultextension='.csv',filetypes=[('CSV file','*.csv')])
        if selected:self.launch('template',selected)

    def show_record(self):
        rows=self.preview['rows'] if self.preview else []
        if not rows:
            self.text(self.details,'');self.record_label.configure(text='No valid records to preview.');self.controls();return
        row=rows[self.position];fields=row['fields']
        self.record_label.configure(text=f'Preview {self.position+1} / {len(rows)} · CSV record {row["record"]}')
        if self.cards:
            lines=['Front',fields[0],'','Back',fields[1]]
        else:
            lines=[f'Topic: {row["topic"] or "No topic"}',f'Difficulty: {fields[6]}','',fields[0],'']
            lines += [f'{letter}. {value}' for letter,value in zip('ABCD',fields[1:5])]
            lines += ['',f'Correct answer: {"ABCD"[fields[5]]}','',f'Explanation: {fields[7] or "—"}']
        self.text(self.details,'\n'.join(lines));self.controls()

    def move(self,offset):
        if self.process is not None or not self.preview:return
        self.position=max(0,min(len(self.preview['rows'])-1,self.position+offset));self.show_record()

    def save(self):
        if self.process is not None or not self.preview or self.preview['errors'] or not self.preview['rows']:return
        try:
            self.payload=tempfile.TemporaryDirectory(prefix='soskuska-csv-')
            selected=Path(self.payload.name)/'preview.json'
            selected.write_text(json.dumps(self.preview['rows'],ensure_ascii=False),encoding='utf-8')
        except OSError as exc:
            self.status.configure(text=f'Could not stage the import: {exc}');return
        self.kind='save'
        self.modal=ctk.CTkToplevel(self.app);self.modal.title(f'Importing {self.noun}');self.modal.geometry('420x150')
        self.app.label(self.modal,'Importing… Please wait. All records save together.',14,wraplength=370).pack(padx=20,pady=35)
        self.modal.protocol('WM_DELETE_WINDOW',lambda:None);self.modal.grab_set()
        self.launch('save',selected)

    def refresh_totals(self):
        try:
            (self.bank.refresh_csv_totals() if self.cards else self.bank.refresh());self.app.refresh_data()
        except (sqlite3.Error,ValueError):
            self.status.configure(text='Could not refresh totals. Retry Refresh totals; this does not import again.');return False
        if self.saved_message:self.status.configure(text=self.saved_message+' Totals refreshed.')
        return True

    def complete(self,result):
        kind=self.kind;self.kind=None
        if kind=='save':
            self.modal.grab_release();self.modal.destroy()
            if self.payload is not None:
                try:self.payload.cleanup()
                except OSError:pass
                self.payload=None
        state=result.get('state');value=result.get('value','')
        if kind=='parse' and state=='done':
            self.preview=value;self.position=0
            self.text(self.errors,'\n'.join(value['errors']))
            self.errors.grid() if value['errors'] else self.errors.grid_remove()
            self.status.configure(text=f'{value["total"]} CSV records; {len(value["rows"])} valid records to preview; {len(value["errors"])} issues. No rows saved. Fix all issues before Import all.')
            self.show_record()
        elif kind=='save' and state=='done':
            # Consume the batch before any report read; retries must only refresh.
            self.preview=None;self.text(self.details,'');self.errors.grid_remove();self.record_label.configure(text='')
            message=(f'Imported {value["cards"]} flashcards into {value["deck"]}. New cards are due now.' if self.cards else f'Imported {value["questions"]} questions and created {value["topics"]} topics in {value["subject"]}.')
            self.saved_message=message
            self.status.configure(text=message)
            if not self.refresh_totals():self.status.configure(text=message+' Could not refresh totals. Retry Refresh totals; do not import again.')
        elif kind=='save' and state=='unknown':
            self.preview=None;self.text(self.details,'');self.errors.grid_remove();self.record_label.configure(text='')
            self.status.configure(text='The helper stopped before confirming the result. Import may have completed. Refresh totals before choosing the CSV again.')
        elif state=='invalid':
            if self.preview is not None:self.preview['errors']=result['errors']
            self.text(self.errors,'\n'.join(result['errors']));self.errors.grid()
            self.status.configure(text='Import not saved. The target or content changed. Resolve the listed issues and choose the CSV again.')
        elif state=='error':
            self.status.configure(text=('Import not saved. Preview is kept; retry or choose CSV again. ' if kind=='save' else 'Could not complete CSV operation: ')+str(value))
        elif kind=='template' and state=='done':self.status.configure(text=f'Header-only template saved: {value}')
        else:self.status.configure(text='CSV helper stopped unexpectedly. Choose the file again.')
        self.controls()

    def poll(self):
        if self.closed:return
        for process,output in self.abandoned[:]:
            if process.poll() is not None:
                output.close();self.abandoned.remove((process,output))
        process=self.process
        if process is not None:
            if process.poll() is not None:
                self.output.seek(0);output=self.output.read(16*1024*1024);self.output.close()
                self.output=None;self.process=None
                try:result=json.loads(output)
                except (ValueError,UnicodeError):result={'state':'unknown'}
                self.complete(result)
            elif time.monotonic()-self.started>60:process.kill()
        self.poll_id=self.after(50,self.poll)

    def destroy(self):
        self.closed=True
        if self.process is not None:
            if self.process.poll() is None:self.process.kill()
            self.output.close()
        for process,output in self.abandoned:
            if process.poll() is None:process.kill()
            process.poll();output.close()
        if self.payload is not None:
            try:self.payload.cleanup()
            except OSError:pass
        self.after_cancel(self.poll_id)
        super().destroy()
