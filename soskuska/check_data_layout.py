"""Bounded four-language Settings/data geometry checks using isolated worker previews."""
import argparse
import csv
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
from preferences import DEFAULTS
from localization import LANGUAGE_CODES
from storage import Store


def data_layout(app,scale):
    canvas=app.scroll._parent_canvas
    def horizontal(items):
        app.update_idletasks()
        for w in items:
            assert w.winfo_rootx()>=canvas.winfo_rootx(),(w,app.translator.language)
            assert w.winfo_rootx()+w.winfo_width()<=canvas.winfo_rootx()+canvas.winfo_width(),(w,scale,app.translator.language)
    def show(target,items):
        app.update_idletasks();canvas.yview_moveto(0);app.update_idletasks()
        height=canvas.bbox('all')[3]
        offset=target.winfo_rooty()-canvas.winfo_rooty()
        canvas.yview_moveto(max(0,(offset-8)/height));app.update_idletasks()
        horizontal(items)
        for w in items:
            assert w.winfo_ismapped()
            assert w.winfo_rooty()>=canvas.winfo_rooty()-1,(w,scale)
            assert w.winfo_rooty()+w.winfo_height()<=canvas.winfo_rooty()+canvas.winfo_height(),(w,scale)
    def wait_for(predicate):
        if predicate():return
        done=ctk.BooleanVar(master=app,value=False)
        deadline=time.monotonic()+6
        def poll():
            if predicate() or time.monotonic()>deadline:done.set(True)
            else:app.after(30,poll)
        app.after(30,poll);app.wait_variable(done)
        assert predicate(),"Data preview did not finish"
    sid=app.store.create_subject('Настройки — '+ 'предмет '*10)
    did=app.store.create_deck(sid,'Preview destination')
    app.start_focus(sid);target=app.focus_target
    app.navigate('Settings');page=app.settings_page;app.update_idletasks()
    page.entries['focus_minutes'].delete(0,'end');page.entries['focus_minutes'].insert(0,'27')
    snapshot=page.snapshot;entries=tuple(page.entries.values())
    assert page.preference_columns==1
    with patch.object(app.store,'preferences',side_effect=AssertionError('Resize read preferences')):
        app.geometry('1440x900');app.update_idletasks();assert page.preference_columns==2
        app.geometry('1024x700');app.update_idletasks();assert page.preference_columns==1
    assert page.snapshot is snapshot and tuple(page.entries.values())==entries
    assert page.entries['focus_minutes'].get()=='27' and app.focus_target==target and app.session_open
    horizontal([*entries,page.ui_language_menu,page.appearance_menu,page.language_menu])
    with patch.object(app.store,'save_preferences',side_effect=sqlite3.OperationalError('full')):
        page.save_button.invoke()
    assert page.snapshot is snapshot and page.entries['focus_minutes'].get()=='27'
    assert page.feedback.cget('text')==page.status.cget('text')==app.translator.text('Could not save settings. Your draft is kept; retry Save.')
    show(page.feedback.master,[page.save_button,page.reload_button,page.copy_button,page.feedback])
    page.reload_button.invoke();assert page.pending_reload
    assert page.feedback.cget('text')==app.translator.text('Click Confirm reload again to replace this draft with saved settings.')
    schedule=page.schedule;schedule.directory.insert(0,str(app.store.path.parent/('папка '*18)))
    schedule.enabled.set(True);draft=schedule.values();schedule_snapshot=schedule.snapshot
    app.navigate('Dashboard');app.navigate('Settings');app.update_idletasks()
    assert not page.pending_reload and page.entries['focus_minutes'].get()=='27'
    assert schedule.values()==draft and schedule.snapshot==schedule_snapshot
    horizontal([schedule.directory,schedule.choose_button,schedule.save_button,schedule.reload_button,schedule.retry_button])
    assert app.finish_focus()
    backup=app.store.path.parent/'preview.sqlite3'
    with sqlite3.connect(backup) as dest:app.store.db.backup(dest)
    panel=page.backups
    with patch('backup_panel.filedialog.askopenfilename',return_value=str(backup)):
        panel.restore_button.invoke()
    wait_for(lambda:not panel.busy);app.update_idletasks()
    assert panel.pending is not None,panel.status.cget("text")
    assert panel.confirmation.winfo_ismapped()
    assert 0<panel.warning.cget('wraplength')<=panel.confirmation.winfo_width()/scale-24
    show(panel.confirmation,[panel.warning,panel.confirm_button,panel.cancel_button])
    panel.cancel_button.invoke();assert panel.pending is None and not panel.confirmation.winfo_ismapped()
    assert page.entries['focus_minutes'].get()=='27' and schedule.values()==draft
    for cards in (False,True):
        file=app.store.path.parent/('cards.csv' if cards else 'questions.csv')
        with file.open('w',encoding='utf-8',newline='') as out:
            writer=csv.writer(out)
            if cards:writer.writerow(['front','back']);writer.writerow(['Вопрос '+ 'текст '*80,'Ответ '+ 'чтение '*100])
            else:writer.writerow(['prompt','option_a','option_b','option_c','option_d','correct_option','difficulty']);writer.writerow(['Вопрос '+ 'текст '*80,'A','B','C','D','A','Easy'])
        if cards:
            app.navigate('Flashcards');bank=app.flashcard_page;bank.open_deck(did);bank.search.insert(0,'Kept card search')
            draft_widget=bank.search
        else:
            app.open_question_bank(sid);bank=app.question_bank;bank.show_question_form();bank.prompt_entry.insert('1.0','Kept question draft');draft_widget=bank.prompt_entry
        importer=bank.importer;importer.open()
        with patch('csv_import_panel.filedialog.askopenfilename',return_value=str(file)):
            importer.choose_button.invoke()
        wait_for(lambda:importer.process is None)
        assert importer.preview and not importer.preview['errors']
        preview=importer.preview;details=importer.details.get('1.0','end-1c')
        assert importer.import_button.cget('state')=='normal' and 'Вопрос' in details
        with patch.object(app.store,'preferences',side_effect=AssertionError('Resize read preferences')):
            app.geometry('1440x900');app.update_idletasks();app.geometry('1024x700');app.update_idletasks()
        assert importer.preview is preview and importer.details.get('1.0','end-1c')==details
        horizontal(importer.buttons)
        assert (draft_widget.get() if cards else draft_widget.get('1.0','end-1c'))==('Kept card search' if cards else 'Kept question draft')
        show(importer.previous_button.master,[importer.previous_button,importer.next_button,importer.import_button,importer.refresh_button])
        importer.cancel_button.invoke();assert importer.preview is None
        assert app.store.flashcards(did)==[] if cards else app.store.questions(sid)==[]


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
                data_layout(app,scale)
                app.close()
            except Exception as exc:
                errors.append(repr(exc));traceback.print_exc();app.destroy()
        app.report_callback_exception=lambda kind,value,tb:(errors.append(repr(value)),traceback.print_exception(kind,value,tb),app.destroy())
        app.after(500,run)
        app.after(15000,lambda:(errors.append('Settings/data check timed out'),app.destroy()))
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
        print('PASS: four-language Settings/data panels at 100/150 percent, resize without reads, draft/snapshot/active-timer retention, save/reload feedback, schedule draft, validated restore/cancel, both real CSV previews and stable controls',flush=True)
