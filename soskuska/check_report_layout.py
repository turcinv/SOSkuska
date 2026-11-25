"""Bounded Statistics/Tutor layout and state probes using disposable data, no live model."""
import argparse
import queue
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from check_ui_languages import widgets
from preferences import DEFAULTS
from localization import LANGUAGE_CODES
from storage import Store


def report_layout(app,scale):
    canvas=app.scroll._parent_canvas
    def horizontal(items):
        app.update_idletasks()
        for w in items:
            assert w.winfo_rootx()>=canvas.winfo_rootx(),(w,app.translator.language)
            assert w.winfo_rootx()+w.winfo_width()<=canvas.winfo_rootx()+canvas.winfo_width(),(w,app.translator.language,scale)
    def footer(items):
        app.update_idletasks();canvas.yview_moveto(1);app.update_idletasks()
        horizontal(items)
        for w in items:
            assert w.winfo_ismapped()
            assert w.winfo_rooty()>=canvas.winfo_rooty(),(w,scale)
            assert w.winfo_rooty()+w.winfo_height()<=canvas.winfo_rooty()+canvas.winfo_height(),(w,scale)
    app.navigate('Statistics');stats=app.statistics_page;app.update_idletasks()
    assert stats.report['focus_seconds']==0 and stats.report['practice_accuracy'] is None
    assert [int(c.grid_info()['column']) for c in stats.summary_cards]==[0,0,0]
    sid=app.store.create_subject(('Длинный предмет ' + 'математика '*9).strip())
    app.store.add_session(1500,sid)
    stats.load();snapshot=stats.report;cards=tuple(stats.summary_cards);bars=tuple(stats.subject_bars)
    with patch.object(app.store,'statistics',side_effect=AssertionError('Geometry queried statistics')):
        app.geometry('1440x900');app.update_idletasks()
        assert [int(c.grid_info()['column']) for c in stats.summary_cards]==[0,1,2]
        assert stats.report is snapshot and tuple(stats.summary_cards)==cards and tuple(stats.subject_bars)==bars
        app.geometry('1024x700');app.update_idletasks()
    horizontal([stats.period_picker,stats.refresh_button,*stats.summary_cards,*stats.subject_bars])
    for label in widgets(stats.body):
        if isinstance(label,ctk.CTkLabel):
            assert label.cget('justify')=='left' and 0<label.cget('wraplength')<=label.master.winfo_width()/scale-30
    with patch.object(app.store,'statistics',side_effect=sqlite3.OperationalError('locked')):
        stats.load()
    assert stats.report is snapshot and tuple(stats.summary_cards)==cards
    assert app.translator.text('Could not refresh statistics. Previous report, if any, is unchanged. Press Refresh to retry.')==stats.status.cget('text')
    stats.load();assert stats.report['focus_seconds']==1500

    saved=app.store.begin_tutor_turn(None,'http://127.0.0.1:11434','study-model:latest','Длинная история '+ 'вопрос '*30,'Russian')
    answer='Подробный ответ для проверки чтения. '*100
    app.store.finish_tutor_turn(saved['id'],saved['turn_id'],answer,'completed',expected_revision=saved['revision'])
    app.navigate('AI Tutor');page=app.tutor_page;app.update_idletasks()
    horizontal([page.endpoint,page.connect_button,page.model_menu,page.language_menu,page.history_menu,page.open_button,page.history_refresh_button,page.delete_button,page.history_previous,page.history_next])
    assert page.task is None and page.connected_endpoint is None
    # Near the side-by-side breakpoint, a normal localized model instruction must fit.
    app.geometry('1270x900');app.update_idletasks()
    assert page.setup_cards[0].grid_info()['row']==page.setup_cards[1].grid_info()['row']==0
    font=page.model_menu.cget('font')
    instruction=app.translator.text('Connect to load models')
    assert font.measure(instruction)+45<=page.model_menu.winfo_width()/scale,(instruction,page.model_menu.winfo_width()/scale)
    page.open_button.invoke();app.update_idletasks()
    assert page.conversation_id==saved['id'] and answer in page.transcript.get('1.0','end-1c')
    assert page.task is None and page.connected_endpoint is None and page.model.get()=='study-model:latest'
    draft='Следующий вопрос — '+ 'сохранить черновик '*120
    page.prompt.insert('1.0',draft)
    transcript=page.transcript;prompt=page.prompt;turns=page.turns;history=page.history_choice.get()
    class BusyTask:
        def __init__(self):self.events=queue.Queue();self.cancelled=False
        def cancel(self):self.cancelled=True
    task=BusyTask();page.task=task;page.controls()
    assert page.stop_button.cget('state')=='normal' and page.send_button.cget('state')=='disabled'
    with patch.object(app.store,'tutor_conversations',side_effect=AssertionError('Resize read history')):
        app.geometry('1440x900');app.update_idletasks()
        app.geometry('1024x700');app.update_idletasks()
    assert page.task is task and page.transcript is transcript and page.prompt is prompt and page.turns is turns
    assert page.history_choice.get()==history and page.prompt.get('1.0','end-1c')==draft
    assert page.stop_button.cget('state')=='normal'
    footer([page.send_button,page.stop_button,page.clear_button,page.feedback])
    app.navigate('Statistics');app.update_idletasks();canvas.yview_moveto(.4);app.update_idletasks();scroll=canvas.yview()
    task.events.put(('text','HIDDEN_STREAM_TEXT'))
    page.after_cancel(page.poll_job);page.poll();app.update_idletasks()
    assert 'HIDDEN_STREAM_TEXT' in transcript.get('1.0','end-1c')
    assert canvas.yview()==scroll and page.prompt.get('1.0','end-1c')==draft
    page.stop();assert task.cancelled
    page.task=None;page.controls();app.navigate('AI Tutor');app.update_idletasks()
    assert page.prompt.get('1.0','end-1c')==draft and page.conversation_id==saved['id']
    page.unsaved_reply=True;page.controls();page.discard_unsaved();app.update_idletasks()
    assert page.pending_discard and page.feedback.cget('text')==page.status.cget('text')
    assert page.feedback.cget('text')==app.translator.text('Copy the unsaved reply first. Click Confirm discard to clear it; saved history (possibly unfinished) is kept.')
    footer([page.retry_button,page.discard_button,page.recover_button,page.feedback])
    page.unsaved_reply=False;page.pending_discard=False;page.controls()
    assert app.store.tutor_conversation(saved['id'])['turns'][0]['answer']==answer


def check(path, language, scale):
    store=Store(path)
    try:
        store.save_preferences(dict(DEFAULTS,ui_language=language),expected_revision=0)
    finally:
        store.close()
    ctk.set_widget_scaling(scale)
    ctk.set_window_scaling(scale)
    errors=[]
    with patch('socket.create_connection',side_effect=AssertionError('Unexpected network')):
        app=Dashboard(path)
        def run():
            try:
                app.geometry('1024x700');app.update_idletasks()
                report_layout(app,scale)
                app.close()
            except Exception as exc:
                errors.append(repr(exc));traceback.print_exc();app.destroy()
        app.report_callback_exception=lambda kind,value,tb:(errors.append(repr(value)),traceback.print_exception(kind,value,tb),app.destroy())
        app.after(500,run)
        app.after(15000,lambda:(errors.append('Report/Tutor check timed out'),app.destroy()))
        try:
            app.mainloop()
        finally:
            app.store.close()
    assert not errors,errors


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language');parser.add_argument('--data',type=Path)
    parser.add_argument('--scale',type=float,choices=(1.0,1.5),default=1.0)
    args=parser.parse_args()
    if args.language:
        check(args.data,args.language,args.scale)
    else:
        with tempfile.TemporaryDirectory() as folder:
            for language in LANGUAGE_CODES:
                for scale in (1.0,1.5):
                    subprocess.run([sys.executable,'-X','faulthandler','-u',str(Path(__file__).resolve()),
                        '--language',language,'--data',str(Path(folder)/(language+str(scale)+'.db')),
                        '--scale',str(scale)],check=True,timeout=20)
        print('PASS: four-language Statistics/Tutor at 100/150 percent, report retry, geometry without reads, model instruction, offline history, busy controls, hidden stream, draft retention and recovery feedback',flush=True)
