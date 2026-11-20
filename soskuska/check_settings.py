"""Native Settings save/retry/conflict, timer safety and fresh-process persistence."""
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
from storage import Store, SCHEMA_VERSION
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from ollama_fixture import FakeOllama


def run_check(path,endpoint_url,reopen=False):
    app=Dashboard(path)
    page=app.settings_page
    tutor=app.tutor_page
    errors=[]

    def set_entry(key,value):
        entry=page.entries[key]
        entry.delete(0,'end')
        entry.insert(0,str(value))

    def guarded(callback):
        def run():
            try:callback()
            except Exception as exc:
                errors.append(str(exc));traceback.print_exc();app.destroy()
        return run

    def wait_for(predicate,callback,deadline=100):
        def poll():
            assert deadline>0,f'Timed out waiting for {callback.__name__}'
            if predicate():callback()
            else:wait_for(predicate,callback,deadline-1)
        app.after(50,guarded(poll))

    def initial():
        app.geometry('1024x700')
        app.navigate('Settings')
        app.update_idletasks()
        assert page.winfo_ismapped()
        right=app.winfo_rootx()+app.winfo_width()
        assert page.copy_button.winfo_rootx()+page.copy_button.winfo_width()<=right
        assert app.store.preferences()['focus_minutes']==15
        set_entry('focus_minutes','not a number')
        page.save_button.invoke()
        assert 'whole numbers' in page.status.cget('text')
        assert app.store.preferences()['revision']==0
        set_entry('focus_minutes',20)
        set_entry('daily_goal_minutes',120)
        set_entry('ollama_endpoint',endpoint_url)
        set_entry('ollama_model','study-model:latest')
        page.language.set('Russian')
        with patch('socket.create_connection',side_effect=AssertionError('Save must not connect')):
            page.save_button.invoke()
        assert app.preferences['focus_minutes']==20
        assert '/ 120 min' in app.goal.cget('text')
        assert tutor.connected_endpoint is None and tutor.task is None
        assert tutor.endpoint.get()==endpoint_url
        sid=app.store.create_subject('Settings — Математика')
        app.start_focus(sid)
        assert app.focus_target==1200 and app.session_open
        app.pause_focus()
        app.session_seconds=75
        app.navigate('Settings')
        set_entry('focus_minutes',25)
        set_entry('daily_goal_minutes',90)
        with patch.object(app.store,'summary',side_effect=sqlite3.OperationalError('locked')):
            page.save_button.invoke()  # No post-commit report read is needed.
        assert 'Settings saved' in page.status.cget('text')
        assert app.focus_target==1200 and app.session_open
        assert '/ 90 min' in app.goal.cget('text')
        assert app.finish_focus()
        assert app.store.seconds()==75
        app.start_focus(sid)
        assert app.focus_target==1500
        app.pause_focus()
        app.session_seconds=0
        app.finish_focus()
        app.navigate('Settings')
        set_entry('focus_minutes',35)
        with patch.object(app.store,'save_preferences',side_effect=sqlite3.OperationalError('disk full')):
            page.save_button.invoke()
        assert page.entries['focus_minutes'].get()=='35'
        assert app.preferences['focus_minutes']==25
        assert app.store.preferences()['focus_minutes']==25
        other=Store(path)
        try:
            fields={key:app.store.preferences()[key] for key in ['focus_minutes','daily_goal_minutes','ollama_endpoint','ollama_model','answer_language','ui_language']}
            fields['daily_goal_minutes']=100
            other.save_preferences(fields,expected_revision=app.store.preferences()['revision'])
        finally:other.close()
        page.save_button.invoke()
        assert 'another window' in page.status.cget('text')
        assert page.entries['focus_minutes'].get()=='35'
        page.reload_button.invoke()
        assert page.pending_reload and page.entries['focus_minutes'].get()=='35'
        app.navigate('Dashboard')
        app.query.set('keep dashboard search')
        app.navigate('Settings')
        assert not page.pending_reload and page.entries['focus_minutes'].get()=='35'
        app.focus_search();app.clear_search()
        assert app.query.get()=='keep dashboard search'
        page.reload_button.invoke();page.reload_button.invoke()
        assert page.entries['focus_minutes'].get()=='25'
        assert page.entries['daily_goal_minutes'].get()=='100'
        set_entry('daily_goal_minutes',90)
        page.save_button.invoke()
        app.navigate('AI Tutor')
        # A busy Tutor blocks AI changes while study-only preferences remain usable.
        tutor.task = object()
        set_entry('ollama_model','busy-change')
        page.save_button.invoke()
        assert 'Tutor request' in page.status.cget('text')
        assert app.store.preferences()['ollama_model']=='study-model:latest'
        set_entry('ollama_model','study-model:latest')
        set_entry('daily_goal_minutes',91)
        page.save_button.invoke()
        assert app.store.preferences()['daily_goal_minutes']==91
        tutor.task = None
        tutor.controls()
        set_entry('daily_goal_minutes',90)
        page.save_button.invoke()
        tutor.connect_button.invoke()
        wait_for(lambda:tutor.task is None,connected)

    def connected():
        assert tutor.model.get()=='study-model:latest'
        assert tutor.language.get()=='Russian'
        tutor.turns.append({'prompt':'keep this chat','answer':'saved only in memory','status':'completed'})
        app.navigate('Settings')
        set_entry('ollama_endpoint','http://127.0.0.1:1')
        page.save_button.invoke()
        assert 'New chat' in page.status.cget('text')
        assert app.store.preferences()['ollama_endpoint']==endpoint_url
        set_entry('ollama_endpoint',endpoint_url)
        set_entry('ollama_model','missing-model')
        page.save_button.invoke()
        assert app.store.preferences()['ollama_model']=='missing-model'
        assert tutor.model.get()==''
        app.navigate('AI Tutor')
        tutor.connect_button.invoke()
        wait_for(lambda:tutor.task is None,missing_model)

    def missing_model():
        assert 'Preferred model is unavailable' in tutor.status.cget('text')
        assert tutor.model.get()==''
        tutor.send()
        assert tutor.task is None
        tutor.model.set('study-model:latest')
        app.navigate('Settings')
        page.copy_button.invoke()
        assert page.entries['ollama_model'].get()=='study-model:latest'
        page.save_button.invoke()
        # Saved preferences do not replace an unchanged temporary Tutor URL/draft.
        tutor.prompt.insert('1.0','unsent question')
        set_entry('daily_goal_minutes',91)
        page.save_button.invoke()
        assert tutor.prompt.get('1.0','end-1c')=='unsent question'
        assert tutor.connected_endpoint==endpoint_url
        set_entry('daily_goal_minutes',90)
        page.save_button.invoke()
        assert app.store.db.execute('PRAGMA user_version').fetchone()[0]==SCHEMA_VERSION
        app.close()

    def resumed():
        assert app.preferences['focus_minutes']==25
        assert app.preferences['daily_goal_minutes']==90
        assert tutor.endpoint.get()==endpoint_url
        assert tutor.model.get()=='study-model:latest'
        assert tutor.language.get()=='Russian'
        assert tutor.task is None and tutor.connected_endpoint is None and tutor.turns==[]
        app.navigate('Settings')
        assert page.entries['focus_minutes'].get()=='25'
        assert app.store.seconds()==75
        app.close()

    def callback_error(kind,value,tb):
        errors.append(str(value));traceback.print_exception(kind,value,tb);app.destroy()
    app.report_callback_exception=callback_error
    app.after(900,guarded(resumed if reopen else initial))
    app.after(20000,guarded(lambda:(_ for _ in ()).throw(AssertionError('Settings check timed out'))))
    try:app.mainloop()
    finally:app.store.close()
    assert not errors,errors


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reopen',type=Path)
    parser.add_argument('--endpoint')
    args=parser.parse_args()
    ctk.set_appearance_mode('dark')
    if args.reopen:
        with patch('socket.create_connection',side_effect=AssertionError('Startup must not connect')):
            run_check(args.reopen,args.endpoint,reopen=True)
    else:
        fixture=FakeOllama()
        try:
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'settings.sqlite3'
                run_check(path,fixture.url)
                subprocess.run([sys.executable,'-u',str(Path(__file__).resolve()),'--reopen',str(path),'--endpoint',fixture.url],check=True,timeout=30)
        finally:fixture.close()
        print('PASS: preferences validation/save/retry, stale conflict/reload, kept drafts, active timer safety, preferred model/language, server guard, no auto-connection and fresh-process persistence',flush=True)
