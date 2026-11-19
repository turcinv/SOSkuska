"""Native backup validation/confirmation/guards, recovery and fresh-process restore."""
import argparse
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from backup import create_backup
from storage import Store


def check(path,source,mode):
    app=Dashboard(path);panel=app.settings_page.backups;errors=[];notices=[];other_stores=[]

    def guarded(callback):
        def run():
            try:callback()
            except Exception as exc:
                errors.append(str(exc));traceback.print_exc();app.destroy()
        return run

    def wait_for(predicate,callback,remaining=160):
        def poll():
            assert remaining>0,f'Timed out: {callback.__name__}'
            if predicate():callback()
            else:wait_for(predicate,callback,remaining-1)
        app.after(50,guarded(poll))

    def choose():
        with patch('backup_panel.filedialog.askopenfilename',return_value=str(source)):
            panel.restore_button.invoke()

    def initial():
        if mode=='reopen':
            assert [s['name'] for s in app.store.subjects()]==['Backup subject']
            assert app.preferences['focus_minutes']==15
            assert app.tutor_page.task is None and app.tutor_page.connected_endpoint is None
            copies=list((path.parent/'backups').glob('*.sqlite3'))
            assert len(copies)==1
            safety=Store(copies[0])
            try:assert 'Current subject' in [s['name'] for s in safety.subjects()]
            finally:safety.close()
            app.close();return
        app.geometry('1024x700');app.navigate('Settings');app.update_idletasks()
        app.scroll._parent_canvas.yview_moveto(1);app.update_idletasks()
        assert panel.create_button.winfo_ismapped()
        assert panel.create_button.winfo_rooty()+panel.create_button.winfo_height()<=app.winfo_rooty()+app.winfo_height()
        if mode=='success':
            choose();wait_for(lambda:panel.pending is not None,confirm_success);return
        output=path.parent/'native-backup.sqlite3'
        with patch('backup_panel.filedialog.asksaveasfilename',return_value=str(output)):
            panel.create_button.invoke()
        assert panel.busy
        app.close();assert app.winfo_exists()
        wait_for(lambda:not panel.busy,backup_done)

    def backup_done():
        assert (path.parent/'native-backup.sqlite3').is_file()
        assert 'Backup created' in panel.status.cget('text')
        long_path=path.parent/('界'*1000)
        with patch('backup_panel.filedialog.asksaveasfilename',return_value=str(long_path)):
            panel.create_button.invoke()
        wait_for(lambda:not panel.busy,long_error_done)

    def long_error_done():
        assert 'Could not complete' in panel.status.cget('text')
        sid=app.store.subjects()[0]['id']
        app.start_focus(sid);app.navigate('Settings');choose()
        assert 'focus session' in panel.status.cget('text') and not panel.busy
        app.pause_focus();app.session_seconds=0;app.finish_focus()
        app.tutor_page.task=object();choose()
        assert 'Tutor request' in panel.status.cget('text') and not panel.busy
        app.tutor_page.task=None
        app.store.create_question(sid,'Native question',['A','B','C','D'],0)
        attempt=app.store.start_practice(sid,1);choose()
        assert 'practice test' in panel.status.cget('text') and not panel.busy
        app.store.discard_practice(attempt)
        choose();wait_for(lambda:panel.pending is not None,cancel)

    def cancel():
        staged=panel.pending.path
        assert 'Validated' in panel.status.cget('text')
        panel.cancel_button.invoke()
        assert panel.pending is None and not staged.exists()
        assert len(app.store.subjects())==2
        choose()
        app.navigate('Dashboard');app.navigate('Settings')
        wait_for(lambda:not panel.busy,inflight_cancelled)

    def inflight_cancelled():
        assert panel.pending is None and 'cancelled' in panel.status.cget('text')
        choose();wait_for(lambda:panel.pending is not None,navigation)

    def navigation():
        app.navigate('Dashboard');assert panel.pending is None
        app.navigate('Settings');choose();wait_for(lambda:panel.pending is not None,confirm_failure)

    def confirm_failure():
        app.tutor_page.task=object();panel.confirm_button.invoke()
        assert panel.pending is not None and 'Tutor request' in panel.status.cget('text')
        app.tutor_page.task=None
        other_stores.append(Store(path))  # A real second window lease must block restore.
        panel.confirm_button.invoke()
        assert app.data_restoring
        app.tick();app.practice_page.tick()  # Closed Store is not read by periodic callbacks.

    def confirm_success():
        panel.confirm_button.invoke()
        assert app.data_restoring

    def message(*args,**kwargs):
        notices.append(args)
        app.close()  # Quit remains blocked even while the result dialog is open.
        assert app.winfo_exists()
        while other_stores:other_stores.pop().close()
    def callback_error(kind,value,tb):
        errors.append(str(value));traceback.print_exception(kind,value,tb);app.destroy()
    app.report_callback_exception=callback_error
    app.after(800,guarded(initial))
    app.after(20000,guarded(lambda:(_ for _ in ()).throw(AssertionError('Backup native check timed out'))))
    try:
        with patch('backup_panel.messagebox.showerror',side_effect=message),patch('backup_panel.messagebox.showinfo',side_effect=message):
            app.mainloop()
    finally:
        while other_stores:other_stores.pop().close()
        app.store.close()
    assert not errors,errors
    if mode=='fail':
        assert notices and 'other SOSkúška windows' in notices[-1][1]
        store=Store(path)
        try:assert len(store.subjects())==2
        finally:store.close()
    elif mode=='success':assert notices and 'Safety copy:' in notices[-1][1]


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path',type=Path);parser.add_argument('--source',type=Path)
    parser.add_argument('--mode',choices=['fail','success','reopen'])
    args=parser.parse_args();ctk.set_appearance_mode('dark')
    if args.mode:check(args.path,args.source,args.mode)
    else:
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'active.sqlite3';source=Path(folder)/'selected.sqlite3'
            store=Store(path)
            try:
                store.create_subject('Backup subject');create_backup(path,source);store.create_subject('Current subject')
            finally:store.close()
            for mode in ['fail','success','reopen']:
                subprocess.run([sys.executable,'-u',str(Path(__file__).resolve()),'--path',str(path),'--source',str(source),'--mode',mode],check=True,timeout=30)
        print('PASS: backup file dialogs/jobs, compact scrolling, focus/AI/practice guards, preview/cancel/navigation, failed restore closure, successful restore/safety copy and fresh-process reopen',flush=True)
