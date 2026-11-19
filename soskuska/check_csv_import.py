"""Native CSV preview/import, retry/consumption, concurrency, 500-row paging and reopen."""
import argparse
import csv
import io
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from csv_import import COLUMNS, read_csv, template_text
from storage import Store, SCHEMA_VERSION


def contents(records):
    output=io.StringIO(newline='');writer=csv.writer(output);writer.writerow(COLUMNS)
    for row in records:writer.writerow(row)
    return output.getvalue()


def check(path,reopen=False):
    app=Dashboard(path);bank=app.question_bank;panel=bank.importer;errors=[];patcher=None
    source=path.parent/'вопросы.csv';template=path.parent/'template.csv'
    subject_name='--Биология 日本語';sid=None
    good=[['Cells','Что такое клетка, 日本語?\nSecond line','A','B','C','D','B','Easy','Explanation\nSecond line'],
          [' cells ','Second question','A','B','C','D','C','Hard','Because']]

    def guarded(callback):
        def run():
            try:callback()
            except Exception as exc:
                errors.append(str(exc));traceback.print_exc();app.destroy()
        return run

    def wait_for(predicate,callback,remaining=300):
        def poll():
            assert remaining>0,f'Timed out: {callback.__name__}'
            if predicate():callback()
            else:wait_for(predicate,callback,remaining-1)
        app.after(50,guarded(poll))

    def choose():
        with patch('csv_import_panel.filedialog.askopenfilename',return_value=str(source)):
            panel.choose_button.invoke()

    def initial():
        nonlocal sid
        if reopen:
            sid=next(s['id'] for s in app.store.subjects() if s['name']==subject_name)
            assert len(app.store.questions(sid))==503
            assert app.store.db.execute('PRAGMA user_version').fetchone()[0]==SCHEMA_VERSION
            assert len(app.store.subjects())==2
            app.open_question_bank(sid);assert len(bank.cards.winfo_children())==50
            app.close();return
        sid=app.store.create_subject(subject_name);app.store.create_subject('Other subject')
        app.geometry('1024x700');app.open_question_bank(sid)
        bank.show_topic_form();bank.topic_entry.insert(0,'Keep this topic draft')
        bank.csv_button.invoke();app.update_idletasks()
        assert panel.winfo_ismapped() and bank.topic_form.winfo_ismapped()
        assert panel.grid_info()['row']!=bank.topic_form.grid_info()['row']
        assert bank.topic_entry.get()=='Keep this topic draft'
        assert panel.template_button.winfo_rootx()+panel.template_button.winfo_width()<=app.winfo_rootx()+app.winfo_width()
        with patch('csv_import_panel.filedialog.asksaveasfilename',return_value=str(template)):
            panel.template_button.invoke()
        wait_for(lambda:panel.process is None,template_done)

    def template_done():
        assert template.read_text()==template_text()
        assert len(app.store.questions(sid))==0
        source.write_text(contents([good[0],['Cells','Invalid','A','A','C','D','B','Easy','']]),encoding='utf-8')
        choose();wait_for(lambda:panel.process is None,invalid_done)

    def invalid_done():
        assert panel.preview['errors'] and 'record 3' in panel.errors.get('1.0','end')
        assert panel.import_button.cget('state')=='disabled'
        assert len(app.store.questions(sid))==0
        source.write_text(contents(good),encoding='utf-8');choose()
        app.navigate('Dashboard');app.open_question_bank(sid);bank.csv_button.invoke()
        assert panel.preview is None
        choose();wait_for(lambda:panel.process is None,preview_done)

    def preview_done():
        assert not panel.preview['errors'] and len(panel.preview['rows'])==2
        assert 'Что такое клетка' in panel.details.get('1.0','end')
        panel.next_button.invoke();assert 'Second question' in panel.details.get('1.0','end')
        panel.previous_button.invoke();assert 'Second line' in panel.details.get('1.0','end')
        locked_source=path.parent/'locked-selection.csv'
        locked_source.write_text(contents([['','Selected under lock','A','B','C','D','A','Easy','']]),encoding='utf-8')
        locker=Store(path)
        try:
            locker.db.execute('BEGIN EXCLUSIVE')
            with patch('csv_import_panel.filedialog.askopenfilename',return_value=str(locked_source)):
                panel.choose_button.invoke()
            assert panel.preview is None and panel.import_button.cget('state')=='disabled'
            assert 'Reading and validating' in panel.status.cget('text')
            locker.db.rollback()
        finally:locker.close()
        wait_for(lambda:panel.process is None,locked_selection_done)

    def locked_selection_done():
        assert len(panel.preview['rows'])==1
        assert 'Selected under lock' in panel.details.get('1.0','end')
        choose();wait_for(lambda:panel.process is None,ready_for_failed_save)

    def ready_for_failed_save():
        assert len(panel.preview['rows'])==2
        source.write_text('Changed after preview',encoding='utf-8')
        app.store.db.execute("CREATE TRIGGER fail_csv BEFORE INSERT ON questions WHEN NEW.prompt='Second question' BEGIN SELECT RAISE(ABORT,'disk full'); END")
        panel.import_button.invoke()
        assert panel.saving
        app.close();assert app.winfo_exists()
        app.navigate('Dashboard');assert app.current_page=='Question Bank'
        app.open_question_bank(999);assert bank.subject_id==sid
        wait_for(lambda:panel.process is None,failed_save)

    def failed_save():
        nonlocal patcher
        assert 'Import not saved' in panel.status.cget('text')
        assert len(app.store.questions(sid))==0 and len(app.store.topics(sid))==0
        assert panel.preview and panel.import_button.cget('state')=='normal'
        app.store.db.execute('DROP TRIGGER fail_csv')
        patcher=patch.object(app.store,'topics',side_effect=sqlite3.OperationalError('injected report read failure'))
        patcher.start()
        panel.import_button.invoke();wait_for(lambda:panel.process is None,committed_read_failure)

    def committed_read_failure():
        nonlocal patcher
        patcher.stop();patcher=None
        assert panel.preview is None and panel.import_button.cget('state')=='disabled'
        assert len(app.store.questions(sid))==2
        assert 'Imported 2' in panel.status.cget('text') and 'Could not refresh' in panel.status.cget('text')
        panel.save();assert len(app.store.questions(sid))==2
        panel.refresh_button.invoke();assert 'Totals refreshed' in panel.status.cget('text')
        source.write_text(contents(good),encoding='utf-8');choose();wait_for(lambda:panel.process is None,duplicate_preview)

    def duplicate_preview():
        assert any('already exists' in e for e in panel.preview['errors'])
        source.write_text(contents([['Race','Concurrent question','A','B','C','D','A','Medium','']]),encoding='utf-8')
        choose();wait_for(lambda:panel.process is None,concurrent_save)

    def concurrent_save():
        assert not panel.preview['errors']
        other=Store(path)
        try:other.import_questions(sid,read_csv(source)['rows'],expected_subject_name=subject_name)
        finally:other.close()
        panel.import_button.invoke();wait_for(lambda:panel.process is None,concurrent_rejected)

    def concurrent_rejected():
        assert len(app.store.questions(sid))==3
        assert panel.preview['errors'] and panel.import_button.cget('state')=='disabled'
        source.write_text(contents([['Bulk',f'Bulk {i}','A','B','C','D','D','Easy',''] for i in range(500)]),encoding='utf-8')
        choose();wait_for(lambda:panel.process is None,bulk_preview)

    def bulk_preview():
        assert len(panel.preview['rows'])==500 and not panel.preview['errors']
        panel.move(499);assert 'Bulk 499' in panel.details.get('1.0','end')
        app.scroll._parent_canvas.yview_moveto(0.5);app.update_idletasks()
        panel.import_button.invoke();wait_for(lambda:panel.process is None,bulk_done)

    def bulk_done():
        assert len(app.store.questions(sid))==503
        assert len(bank.cards.winfo_children())==50
        bank.next_page.invoke();assert bank.question_page==1
        qid=app.store.questions(sid)[50]['id']
        bank.show_question_form(qid);assert bank.question_page==1
        bank.hide_question_form();assert bank.question_page==1
        bank.query.set('Bulk 499');assert bank.question_page==0 and len(bank.cards.winfo_children())==1
        bank.query.set('');assert len(bank.cards.winfo_children())==50
        assert panel.preview is None and panel.import_button.cget('state')=='disabled'
        app.close()

    def callback_error(kind,value,tb):
        errors.append(str(value));traceback.print_exception(kind,value,tb);app.destroy()
    app.report_callback_exception=callback_error
    app.after(800,guarded(initial))
    app.after(45000,guarded(lambda:(_ for _ in ()).throw(AssertionError('CSV native check timed out'))))
    try:app.mainloop()
    finally:
        if patcher:patcher.stop()
        app.store.close()
    assert not errors,errors


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reopen',type=Path);args=parser.parse_args()
    ctk.set_appearance_mode('dark')
    if args.reopen:check(args.reopen,reopen=True)
    else:
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'csv.sqlite3';check(path)
            subprocess.run([sys.executable,'-u',str(Path(__file__).resolve()),'--reopen',str(path)],check=True,timeout=20)
        print('PASS: template, Unicode/multiline preview, compact layout/draft separation, validation/cancel, atomic write retry, postcommit refresh, duplicate/concurrent rejection, 500-row import/pagination and process reopen',flush=True)
