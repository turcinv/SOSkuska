"""Bounded four-language Subjects/Question Bank layout checks, separate from other pages."""
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
from check_ui_languages import widgets
from preferences import DEFAULTS
from localization import LANGUAGE_CODES
from storage import Store


def authoring_layout(app, scale):
    """Compact translated authoring and pure reflow with retained drafts."""
    name=('Длинный предмет ' + 'математика ' * 9).strip()
    sid=app.store.create_subject(name,'Описание ' * 100)
    topic=app.store.create_topic(sid,('Длинная тема ' * 8).strip())
    prompt=('Подробный вопрос для проверки переноса. ' * 45).strip()
    qid=app.store.create_question(sid,prompt,['А ' + 'ответ ' * 70,'B','C','D'],0,topic_id=topic)
    app.refresh_data();app.navigate('My Subjects');page=app.subject_page;app.update_idletasks()
    canvas=app.scroll._parent_canvas
    def horizontal(items):
        app.update_idletasks()
        for w in items:
            assert w.winfo_rootx()>=canvas.winfo_rootx(), (w,app.translator.language)
            assert w.winfo_rootx()+w.winfo_width()<=canvas.winfo_rootx()+canvas.winfo_width(), (w,app.translator.language,scale)
    assert page.card_columns==1
    horizontal([page.add_button,page.search,*[w for w in widgets(page.cards) if isinstance(w,ctk.CTkButton)]])
    labels=[w for w in widgets(page.cards) if isinstance(w,ctk.CTkLabel) and w.cget('text')==name]
    assert labels and labels[0].cget('justify')=='left'
    assert 0<labels[0].cget('wraplength')<=labels[0].master.winfo_width()/scale-30
    page.show_form(sid);page.name_entry.delete(0,'end');page.name_entry.insert(0,'Subject draft')
    snapshot=page.editing_snapshot
    # A real resize must not read subjects or recreate cards/form controls.
    old_cards=tuple(page.subject_cards)
    with patch.object(app.store,'subjects',side_effect=AssertionError('Resize queried SQLite')):
        app.geometry('1440x900');app.update_idletasks()
        assert page.card_columns==2
        assert tuple(page.subject_cards)==old_cards
        assert page.name_entry.get()=='Subject draft' and page.editing_snapshot is snapshot
        app.geometry('1024x700');app.update_idletasks()
        assert page.card_columns==1
    app.open_question_bank(sid);bank=app.question_bank;app.update_idletasks()
    horizontal([bank.heading,bank.count_label,bank.add_question_button,bank.add_topic_button,bank.csv_button,
        bank.topic_filter_menu,bank.edit_topic_button,bank.delete_topic_button,bank.search,bank.page_label])
    card=bank.cards.winfo_children()[0]
    long_label=next(w for w in card.winfo_children() if isinstance(w,ctk.CTkLabel) and w.cget('text')==prompt)
    assert 0<long_label.cget('wraplength')<=card.winfo_width()/scale-30
    bank.show_question_form(qid);app.update_idletasks()
    assert [field.grid_info()['column'] for field in bank.answer_fields]==[0,0,0,0]
    bank.option_entries[1].delete(0,'end');bank.option_entries[1].insert(0,'Kept authoring draft')
    original=bank.question_snapshot
    app.geometry('1440x900');app.update_idletasks()
    assert [field.grid_info()['column'] for field in bank.answer_fields]==[0,1,0,1]
    app.geometry('1024x700');app.update_idletasks()
    horizontal([bank.prompt_entry,*bank.option_entries,bank.question_topic_menu,bank.save_question_button])
    app.navigate('Dashboard');app.open_question_bank(sid);app.update_idletasks()
    assert bank.option_entries[1].get()=='Kept authoring draft' and bank.question_snapshot==original
    assert app.store.question(qid)['option_b']=='B'
    with patch.object(app.store,'update_question',side_effect=sqlite3.OperationalError('full')):
        bank.save_question_button.invoke()
    assert bank.question_error.cget('text') and bank.option_entries[1].get()=='Kept authoring draft'
    # Leave only the editor on screen, then reach its save/error footer by scrolling.
    bank.query.set('no matching fixture');app.update_idletasks();canvas.yview_moveto(1);app.update_idletasks()
    assert bank.save_question_button.winfo_rooty()>=canvas.winfo_rooty()
    assert bank.save_question_button.winfo_rooty()+bank.save_question_button.winfo_height()<=canvas.winfo_rooty()+canvas.winfo_height()
    app.navigate('My Subjects');assert page.name_entry.get()=='Subject draft'
    page.hide_form();app.store.delete_subject(sid);app.refresh_data();app.navigate('Dashboard')


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
                authoring_layout(app,scale)
                app.close()
            except Exception as exc:
                errors.append(repr(exc));traceback.print_exc();app.destroy()
        app.report_callback_exception=lambda kind,value,tb:(errors.append(repr(value)),traceback.print_exception(kind,value,tb),app.destroy())
        app.after(500,run)
        app.after(15000,lambda:(errors.append('Authoring check timed out'),app.destroy()))
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
        print('PASS: four-language Subjects/Question Bank at 100/150 percent, long content, bounds, geometry without reads, stable widgets/snapshots, retained drafts, write failure and footer access',flush=True)
