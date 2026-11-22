"""Daily backup GUI/worker integration, disposable data and fresh-process reopening."""
import argparse
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import date,timedelta
from pathlib import Path
from unittest.mock import patch
import customtkinter as ctk
from app import Dashboard
from automatic_backup import load_config,save_config,publish_config,config_lease
from backup import PreparedBackup


def run(path,folder,reopen=False):
    ctk.set_default_color_theme('dark-blue');app=Dashboard(path);panel=app.settings_page.schedule;errors=[]
    def guarded(callback):
        def call():
            try:callback()
            except Exception as exc:errors.append(exc);traceback.print_exc();app.destroy()
        return call
    def poll_now():
        panel.after_cancel(panel.poll_id)
        panel.poll()
    def wait(callback,remaining=120):
        def step():
            assert remaining>0,'Backup worker timed out'
            if not panel.busy:callback()
            else:wait(callback,remaining-1)
        app.after(50,guarded(step))
    def entry(value):panel.directory.delete(0,'end');panel.directory.insert(0,str(value))
    def start():
        if reopen:
            assert load_config(path)['enabled'] and panel.enabled.get()
            assert panel.directory.get()==str(folder)
            panel.next_check=0;poll_now()
            assert not panel.busy and len(list(folder.glob('*.sqlite3')))==2
            panel.enabled.set(False);panel.save();app.close();return
        app.geometry('1024x700');app.navigate('Settings');app.update_idletasks()
        assert not panel.enabled.get() and not load_config(path)['enabled']
        app.store.create_subject('Saved data');app.refresh_data()
        with patch('scheduled_backups.filedialog.askdirectory',return_value=str(folder)):
            panel.choose_button.invoke()
        panel.enabled.set(True)
        app.navigate('Dashboard');app.navigate('Settings');assert panel.directory.get()==str(folder)
        with patch('scheduled_backups.save_config',side_effect=OSError('full')):panel.save()
        assert panel.dirty() and not load_config(path)['enabled']
        panel.save();panel.next_check=0;poll_now();assert panel.busy
        app.open_question_bank(app.store.subjects()[0]['id']);app.question_bank.show_topic_form()
        app.close();assert app.current_page=='Question Bank' and app.winfo_exists()
        app.update_idletasks();assert app.backup_notice.winfo_ismapped()
        wait(first_done)
    def first_done():
        assert len(list(folder.glob('*.sqlite3')))==1
        assert 'saved' in panel.runtime.cget('text')
        PreparedBackup(next(folder.glob('*.sqlite3')),path).close()
        app.navigate('Settings');assert 'saved' in panel.runtime.cget('text')
        panel.next_check=0;poll_now();assert not panel.busy
        # Background completion must not authorize a Save of stale controls.
        prior=panel.snapshot
        other=save_config(path,False,str(folder),load_config(path)['token'])
        panel.complete('done',dict(state='skipped'))
        assert panel.snapshot['token']==prior['token']
        panel.save();assert 'another window' in panel.status.cget('text')
        panel.load(force=True);panel.enabled.set(True);panel.save()
        # A failed Reload keeps edited values protected on later navigation.
        entry(folder/'draft')
        panel.reload()
        with patch('scheduled_backups.load_config',side_effect=OSError('read')):panel.reload()
        app.navigate('Dashboard');app.navigate('Settings');assert panel.directory.get()==str(folder/'draft')
        panel.load(force=True)
        config=load_config(path);publish_config(path,dict(config,last_day=(date.today()-timedelta(days=1)).isoformat()))
        missing=folder/'missing';entry(missing);panel.save()
        panel.next_check=0;poll_now();assert panel.busy;wait(failed)
    def failed():
        assert 'failed' in panel.runtime.cget('text')
        app.navigate('Dashboard');app.navigate('Settings');assert 'failed' in panel.runtime.cget('text')
        assert app.backup_notice.winfo_manager()=='grid'
        missing=folder/'missing';missing.mkdir();entry(folder);panel.save()
        panel.next_check=0;poll_now();wait(second_done)
    def second_done():
        assert len(list(folder.glob('*.sqlite3')))==2
        assert panel.runtime.cget('text')=='Daily backup saved. Existing backup files were kept.'
        app.scroll._parent_canvas.yview_moveto(1);app.update_idletasks()
        assert app.scroll._parent_canvas.yview()[0]>0
        right=app.winfo_rootx()+app.winfo_width()
        for button in (panel.save_button,panel.reload_button,panel.retry_button):
            assert button.winfo_rootx()+button.winfo_width()<=right
        app.close()
    app.after(250,guarded(start));app.after(20000,guarded(lambda:(_ for _ in ()).throw(AssertionError('GUI timeout'))))
    app.report_callback_exception=lambda *args:(errors.append(args[1]),traceback.print_exception(*args),app.destroy())
    try:app.mainloop()
    finally:app.store.close()
    assert not errors,errors


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path);parser.add_argument('--folder',type=Path);parser.add_argument('--reopen',action='store_true');args=parser.parse_args()
    if args.data:run(args.data,args.folder,args.reopen);return
    with tempfile.TemporaryDirectory(prefix='soskuska-daily-') as directory:
        path=Path(directory)/'study.sqlite3';folder=Path(directory)/'Сохранённые zálohy';folder.mkdir()
        command=[sys.executable,'-X','faulthandler','-u',__file__,'--data',str(path),'--folder',str(folder)]
        subprocess.run(command,check=True,timeout=25)
        subprocess.run([*command,'--reopen'],check=True,timeout=25)
    print('PASS: opt-in schedule, draft/failure/reload preservation, stale-window rejection, isolated backup worker, close banner, daily retry, compact scrolling and fresh-process policy/receipt',flush=True)

if __name__=='__main__':main()
