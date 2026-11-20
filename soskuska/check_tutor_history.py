"""Real-window local history, offline reopen, persistence errors and close/restart."""
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
from app import Dashboard
from storage import Store
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from ollama_fixture import FakeOllama


def check(path,reopen=False):
    fixture=None if reopen else FakeOllama()
    app=Dashboard(path);page=app.tutor_page;errors=[];patcher=None;cid=None
    def guarded(callback):
        def run():
            try:callback()
            except Exception as exc:
                errors.append(str(exc));traceback.print_exc();app.destroy()
        return run
    def wait(predicate,callback,remaining=160):
        def poll():
            assert remaining>0,callback.__name__
            if predicate():callback()
            else:wait(predicate,callback,remaining-1)
        app.after(50,guarded(poll))
    def choose(cid):
        page.history_choice.set(next(k for k,v in page.history_rows.items() if v['id']==cid));page.open_button.invoke()
    def initial():
        nonlocal cid
        app.geometry('1024x700');app.navigate('AI Tutor');app.update_idletasks()
        if reopen:
            saved=app.store.tutor_conversations();assert len(saved)==2
            completed=next(v for v in saved if v['title']=='First question 日本語')
            choose(completed['id']);assert page.models==[] and page.connected_endpoint is None
            assert page.turns[-1]['status']=='interrupted' and page.turns[-1]['answer']=='Hello '
            assert 'First question 日本語' in page.transcript.get('1.0','end')
            pending=next(v for v in saved if v['id']!=completed['id'])
            choose(pending['id']);assert page.turns[-1]['status']=='pending'
            page.recover_button.invoke();assert page.turns[-1]['status']=='pending'
            page.recover_button.invoke();assert page.turns[-1]['status']=='interrupted'
            page.refresh_history();page.delete_button.invoke();page.delete_button.invoke()
            assert len(app.store.tutor_conversations())==1
            app.close();return
        assert fixture.requests==[] and page.history_rows=={}
        app.scroll._parent_canvas.yview_moveto(1);app.update_idletasks()
        assert app.scroll._parent_canvas.yview()[0]>0
        assert page.recover_button.winfo_rooty()+page.recover_button.winfo_height()<=app.winfo_rooty()+app.winfo_height()
        app.scroll._parent_canvas.yview_moveto(0)
        assert page.delete_button.winfo_rootx()+page.delete_button.winfo_width()<=app.winfo_rootx()+app.winfo_width()
        page.endpoint.delete(0,'end');page.endpoint.insert(0,fixture.url);page.connect()
        wait(lambda:page.task is None,connected)
    def connected():
        page.prompt.insert('1.0','First question 日本語');page.send()
        wait(lambda:page.task is None,first_done)
    def first_done():
        nonlocal cid
        cid=page.conversation_id
        assert not page.unsaved_reply and len(page.history_rows)==1
        assert app.store.tutor_conversation(cid)['turns'][0]['status']=='completed'
        page.new_chat();page.new_chat();assert page.turns==[] and len(app.store.tutor_conversations())==1
        before=len(fixture.requests)
        with patch.object(app.store,'tutor_conversations',side_effect=sqlite3.OperationalError('busy')):
            page.history_page(1)
        assert page.history_offset==0
        choose(cid)
        assert len(fixture.requests)==before and page.models==[] and page.model.get()=='study-model:latest'
        page.prompt.insert('1.0','Keep this draft');page.open_history();assert page.prompt.get('1.0','end-1c')=='Keep this draft'
        assert 'opened offline' in page.status.cget('text')
        page.prompt.delete('1.0','end');page.connect();wait(lambda:page.task is None,owner_check)
    def owner_check():
        nonlocal patcher
        page.models.append('other-model');page.model.set('other-model');page.prompt.insert('1.0','Continue')
        before=len(fixture.requests);page.send();assert page.task is None and len(fixture.requests)==before
        assert 'New chat' in page.status.cget('text')
        page.model.set('study-model:latest')
        with patch.object(app.store,'begin_tutor_turn',side_effect=sqlite3.OperationalError('full')):
            page.send()
        assert page.task is None and page.prompt.get('1.0','end-1c')=='Continue'
        assert len(fixture.requests)==before
        patcher=patch.object(app.store,'finish_tutor_turn',side_effect=sqlite3.OperationalError('full'));patcher.start()
        page.send();wait(lambda:page.task is None,failed_save)
    def failed_save():
        nonlocal patcher
        assert page.unsaved_reply and page.retry_button.cget('state')=='normal'
        assert page.open_button.cget('state')=='disabled'
        app.navigate("Dashboard");app.close();assert app.winfo_exists() and page.unsaved_reply
        assert app.current_page=="AI Tutor"
        patcher.stop();patcher=None
        page.retry_button.invoke();assert not page.unsaved_reply
        assert len(app.store.tutor_conversation(cid)['turns'])==2
        page.retry_button.invoke();assert len(app.store.tutor_conversation(cid)['turns'])==2
        sent=fixture.requests[-1][2]['messages'];assert any(m['content']=='First question 日本語' for m in sent)
        fixture.mode='slow';fixture.gate.clear();page.prompt.insert('1.0','Close during reply');page.send()
        wait(lambda:page.turns[-1]['answer']=='Hello ',closing)
    def closing():
        pending=app.store.begin_tutor_turn(None,fixture.url,'study-model:latest','Unfinished previous process','English')
        assert pending['id']!=cid
        task=page.task;app.close();task.thread.join(2);assert not task.thread.is_alive()
    def error(kind,value,tb):
        errors.append(str(value));traceback.print_exception(kind,value,tb);app.destroy()
    app.report_callback_exception=error
    app.after(700,guarded(initial))
    app.after(35000,guarded(lambda:(_ for _ in ()).throw(AssertionError('History check timed out'))))
    try:app.mainloop()
    finally:
        if patcher:patcher.stop()
        app.store.close()
        if fixture:fixture.close()
    assert not errors,errors


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reopen',type=Path);args=parser.parse_args()
    ctk.set_appearance_mode('dark')
    if args.reopen:check(args.reopen,True)
    else:
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'history.db';check(path)
            subprocess.run([sys.executable,'-X','faulthandler','-u',str(Path(__file__).resolve()),'--reopen',str(path)],check=True,timeout=20)
        print('PASS: local history, compact controls, offline opening, prompt retention, server/model ownership, initial/final save failures, idempotent retry, context continuation, interrupted close, fresh-process recovery and confirmed deletion',flush=True)
