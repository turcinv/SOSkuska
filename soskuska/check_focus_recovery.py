"""Disposable focus crash/reopen and recovery UI checks, under a virtual display."""
import argparse
import sqlite3
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path
from unittest.mock import patch
import customtkinter as ctk
from app import Dashboard, SAVE_RETRY_NOTICE
from storage import Store


def gui(path, mode, marker):
    ctk.set_default_color_theme('dark-blue')
    app=Dashboard(path);errors=[]
    def check():
        try:
            app.geometry('1024x700');app.update_idletasks()
            if mode=='crash':
                sid=app.store.subjects()[0]['id'];app.start_focus(sid)
                app.session_seconds=42;app.running_since=None
                assert app.checkpoint_focus()
                marker.write_text('ready')
                return  # Parent terminates this process without normal close.
            if mode=='verify':
                assert app.recovery_record is None and not app.session_open
                assert app.store.seconds()==52 and app.store.summary()['sessions']==2
                app.close();return
            assert app.recovery_record['elapsed_seconds']==42
            assert app.start_button.cget('state')=='disabled'
            app.discard_focus();assert app.pending_focus_discard
            with patch.object(app.store,'pending_focus',side_effect=sqlite3.OperationalError('locked')):
                app.refresh_focus_recovery()
            assert app.recovery_record is None and not app.pending_focus_discard
            assert app.recover_focus_button.cget('state')=='disabled'
            assert app.discard_focus_button.cget('state')=='disabled'
            app.refresh_focus_recovery();app.discard_focus();app.navigate('Statistics')
            assert not app.pending_focus_discard
            app.navigate('Dashboard');app.discard_focus()
            other=Store(path)
            try:
                row=other.pending_focus();other.claim_focus_checkpoint(row['id'],row['revision'])
                app.recover_focus();assert not app.session_open and not app.pending_focus_discard
            finally:other.close()
            app.refresh_focus_recovery()
            with patch.object(app.store,'subjects',side_effect=sqlite3.OperationalError('read')):
                app.recover_focus()
            app.update_idletasks()
            assert app.session_open and app.running_since is None and app.session_seconds==42
            assert app.timer_frame.winfo_manager()=='grid' and app.refresh_pending
            assert app.pause_button.cget('state')=='normal'
            assert app.focus_target==900 and app.preferences['focus_minutes']==1
            assert 'Original' in app.focus_subject_label.cget('text')
            assert app.store.seconds()==0
            app.refresh_data();app.refresh_pending=False
            app.navigate('Settings');app.toggle_sidebar();app.session_seconds=47;app.running_since=time.monotonic()
            with patch.object(app.store,'checkpoint_focus',side_effect=sqlite3.OperationalError('full')):
                app.last_checkpoint=time.monotonic()-6;app.tick()
            assert app.session_save_failed and app.running_since is None
            assert app.pause_button.cget('state')=='disabled'
            assert app.focus_alert.winfo_manager()=='grid' and app.focus_alert.cget('text')=='!'
            app.update_idletasks();assert app.focus_alert.winfo_ismapped()
            assert app.focus_retry_label.cget('text')==SAVE_RETRY_NOTICE
            assert app.current_page=='Settings' and app.store.pending_focus()['elapsed_seconds']==42
            with patch.object(app.store,'add_session',side_effect=sqlite3.OperationalError('full')):
                app.close()
            assert app.winfo_exists() and app.current_page=='Dashboard' and app.session_open
            assert app.finish_focus() and app.store.seconds()==47
            assert not app.session_open and not app.focus_alert.winfo_manager()
            sid=app.store.subjects()[0]['id']
            with patch.object(app.store,'subjects',side_effect=sqlite3.OperationalError('read')):
                app.start_focus(sid)
            assert app.session_open and app.timer_frame.winfo_manager()=='grid'
            assert app.refresh_pending and app.pause_button.cget('state')=='normal'
            app.running_since=None;app.session_seconds=17;app.checkpoint_focus()
            app.store.release_focus();app.session_open=False;app.focus_run_id=None
            app.timer_frame.grid_remove();app.refresh_focus_recovery()
            app.discard_focus();app.clear_search();assert not app.pending_focus_discard
            app.discard_focus();app.refresh_focus_recovery();assert not app.pending_focus_discard
            app.discard_focus();app.discard_focus();assert app.store.pending_focus() is None
            assert app.store.seconds()==47
            app.start_focus(sid);app.running_since=None;app.session_seconds=5
            app.close()  # Normal close saves exactly once.
        except Exception as exc:
            errors.append(exc);traceback.print_exc();app.destroy()
    app.report_callback_exception=lambda *args:(errors.append(args[1]),traceback.print_exception(*args),app.destroy())
    app.after(300,check)
    app.after(20000,lambda:(errors.append(AssertionError('GUI timeout')),app.destroy()))
    try:app.mainloop()
    finally:app.store.close()
    if errors:raise AssertionError(errors)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode');parser.add_argument('--data',type=Path);parser.add_argument('--marker',type=Path)
    args=parser.parse_args()
    if args.mode:gui(args.data,args.mode,args.marker);return
    with tempfile.TemporaryDirectory(prefix='soskuska-focus-') as folder:
        path=Path(folder)/'study.sqlite3';marker=Path(folder)/'ready'
        store=Store(path);store.create_subject('Original');store.close()
        command=[sys.executable,'-X','faulthandler','-u',__file__,'--data',str(path),'--marker',str(marker),'--mode']
        with (Path(folder)/'crash.log').open('w+') as log:
            child=subprocess.Popen([*command,'crash'],stdout=log,stderr=subprocess.STDOUT)
            try:
                deadline=time.monotonic()+15
                while not marker.exists() and time.monotonic()<deadline and child.poll() is None:time.sleep(.05)
                if not marker.exists():
                    log.seek(0);raise AssertionError(log.read() or 'No committed checkpoint')
            finally:
                if child.poll() is None:child.kill()
                child.wait(timeout=5)
        store=Store(path)
        try:
            row=store.pending_focus();assert row['elapsed_seconds']==42
            fields=store.preferences();fields['focus_minutes']=1
            store.save_preferences(fields,expected_revision=fields['revision'])
            store.update_subject(row['subject_id'],'Renamed')
        finally:store.close()
        for mode in ('recover','verify'):subprocess.run([*command,mode],check=True,timeout=25)
    print('PASS: abrupt GUI kill, fresh-process paused recovery, original target/snapshot, stale confirmation, failed reads, exclusive owner, off-page checkpoint failure, close retry, discard and normal-close persistence',flush=True)


if __name__=='__main__':main()
