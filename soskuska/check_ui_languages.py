"""Native four-language UI, canonical choices, opaque content and restart checks."""
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
from storage import Store
from preferences import DEFAULTS
from localization import Translator, LANGUAGE_CODES
from localization_widgets import LocalizedOptionMenu


def widgets(root):
    for child in root.winfo_children():
        yield child
        yield from widgets(child)


def check(path,language,reopen=False):
    next_language=list(LANGUAGE_CODES)[(list(LANGUAGE_CODES).index(language)+1)%4]
    if not reopen:
        store=Store(path)
        try:
            store.save_preferences(dict(DEFAULTS,ui_language=language,answer_language='Russian'),expected_revision=0)
            sid=store.create_subject('Settings');topic=store.create_topic(sid,'Hard')
            store.create_question(sid,'Statistics',['Easy','Medium','Hard','Good'],1,topic_id=topic)
            deck=store.create_deck(sid,'Delete');store.create_flashcard(deck,'Cancel','Settings')
            turn=store.begin_tutor_turn(None,'http://127.0.0.1:11434','Hard','Settings','Russian')
            store.finish_tutor_turn(turn['id'],turn['turn_id'],'Delete','completed',expected_revision=turn['revision'])
        finally:store.close()
    errors=[]
    with patch('socket.create_connection',side_effect=AssertionError('Unexpected network')):
        app=Dashboard(path)
        def run():
            try:
                app.geometry('1024x700');app.update_idletasks()
                if reopen:
                    assert app.translator.language==next_language
                    assert app.preferences['answer_language']=='Russian'
                    app.navigate('Settings');assert app.settings_page.ui_language.get()==next_language
                    app.close();return
                tr=app.translator.text
                assert tr('Dashboard') in app.nav_buttons[0].cget('text')
                assert tr('Settings') in app.settings_btn.cget('text')
                sid=app.store.subjects()[0]['id'];deck=app.store.decks()[0]['id'];qid=app.store.questions(sid)[0]['id']
                app.navigate('My Subjects');app.update_idletasks()
                assert any(isinstance(w,ctk.CTkLabel) and w.cget('text')=='Settings' for w in widgets(app.subject_page))
                app.open_question_bank(sid);bank=app.question_bank;bank.show_question_form(qid)
                assert bank.prompt_entry.get('1.0','end-1c')=='Statistics'
                assert bank.option_entries[0].get()=='Easy'
                assert bank.difficulty.get()=='Medium'
                assert tr('Medium') in next(w for w in widgets(bank.question_form) if isinstance(w,LocalizedOptionMenu) and w.canonical is bank.difficulty).cget('values')
                bank.option_entries[0].delete(0,'end');bank.option_entries[0].insert(0,'Keep draft')
                app.navigate('Practice Tests');page=app.practice_page
                difficulty=next(w for w in widgets(page.setup) if isinstance(w,LocalizedOptionMenu) and w.canonical is page.difficulty)
                difficulty.selected(tr('Hard'));assert page.difficulty.get()=='Hard'
                difficulty.selected(tr('Medium'));assert page.difficulty.get()=='Medium'
                assert page.subject.get()=='Settings'
                assert page.subject_menu.display_variable.get()=='Settings'
                assert app.settings_page.appearance_menu.cget('values')==[tr(mode) for mode in ('Light','Dark','System')]
                assert any(isinstance(w,ctk.CTkLabel) and w.cget('text')==tr('System follows Windows/macOS appearance; on Linux it uses Light.') for w in widgets(app.settings_page))
                assert page.history_apply.cget('text')==tr('Apply filters')
                assert page.history_subject_menu.display_variable.get()==tr('All subjects')
                app.update_idletasks()
                for button in (page.history_apply,page.history_reset):
                    assert button.winfo_rootx()+button.winfo_width()<=app.winfo_rootx()+app.winfo_width()
                app.navigate('Flashcards');cards=app.flashcard_page;cards.open_deck(deck);cards.start_review(deck)
                assert cards.current_card['front']=='Cancel';cards.reveal()
                assert cards.answer.cget('text')=='Settings'
                assert tr('Again') in cards.rating_buttons['Again'].cget('text')
                app.navigate('Statistics');app.statistics_page.period_picker.selected(tr('Last 30 days'))
                assert app.statistics_page.period.get()=='Last 30 days'
                assert app.statistics_page.report['period']=='Last 30 days'
                app.navigate('AI Tutor');tutor=app.tutor_page
                tutor.history_choice.set(next(iter(tutor.history_rows)));tutor.open_history()
                assert 'Settings' in tutor.transcript.get('1.0','end') and 'Delete' in tutor.transcript.get('1.0','end')
                assert tutor.model.get()=='Hard' and tutor.models==[]
                assert tutor.model_menu.display_variable.get()=='Hard'
                assert tutor.language.get()=='Russian'
                app.navigate('Settings');settings=app.settings_page
                for mode in ('Light','Dark'):
                    settings.appearance_menu.selected(tr(mode));assert settings.appearance_mode.get()==mode
                    settings.save();app.update_idletasks();assert ctk.get_appearance_mode()==mode
                    assert app.store.preferences()['ui_language']==language
                    for button in (settings.save_button,settings.reload_button,settings.copy_button):
                        assert button.winfo_rootx()+button.winfo_width()<=app.winfo_rootx()+app.winfo_width()
                settings.ui_language.set(next_language)
                settings.entries['focus_minutes'].delete(0,'end');settings.entries['focus_minutes'].insert(0,'27')
                app.navigate('Dashboard');app.navigate('Settings')
                assert settings.entries['focus_minutes'].get()=='27' and settings.ui_language.get()==next_language
                settings.save();assert app.store.preferences()['ui_language']==next_language
                assert app.translator.language==language and app.preferences['answer_language']=='Russian'
                assert settings.status.cget('text')==tr('Settings saved. Appearance applied. Restart the app to apply an interface language change. Active focus duration is unchanged; Ollama connects only after Connect.')
                app.update_idletasks();right=app.winfo_rootx()+app.winfo_width()
                for button in (settings.save_button,settings.reload_button,settings.copy_button):
                    assert button.winfo_rootx()+button.winfo_width()<=right
                app.scroll._parent_canvas.yview_moveto(1);app.update_idletasks()
                assert app.scroll._parent_canvas.yview()[0]>0
                # Recreated option menus remove their trace from a persistent variable.
                variable=ctk.StringVar(master=app,value='Hard');before=len(variable.trace_info())
                for _ in range(12):
                    menu=LocalizedOptionMenu(settings,owner=app,variable=variable,values=['Hard','Easy'])
                    menu.selected(tr('Easy'));assert variable.get()=='Easy';menu.destroy();variable.set('Hard')
                assert len(variable.trace_info())==before
                menu=LocalizedOptionMenu(settings,owner=app,variable=variable,values=['Deleted record'],translate_values=False,empty_text='Add a subject first')
                menu.configure(values=[]);variable.set('Add a subject first')
                assert menu.cget('values')==[] and menu.display_variable.get()==tr('Add a subject first')
                before=variable.get();menu.selected('Deleted record');assert variable.get()==before
                menu.destroy()
                for model_name in ['Connect to load models','No models installed']:
                    variable.set(model_name)
                    menu=LocalizedOptionMenu(settings,owner=app,variable=variable,values=[],translate_values=False)
                    assert menu.display_variable.get()==model_name;menu.destroy()
                app.open_question_bank(sid);assert bank.option_entries[0].get()=='Keep draft'
                assert app.store.question(qid)['option_a']=='Easy'
                assert app.store.subject(sid)['name']=='Settings'
                app.close()
            except Exception as exc:
                errors.append(str(exc));traceback.print_exc();app.destroy()
        def callback_error(kind,value,tb):
            errors.append(str(value));traceback.print_exception(kind,value,tb);app.destroy()
        app.report_callback_exception=callback_error;app.after(700,run)
        app.after(18000,lambda:(errors.append('Language check timed out'),app.destroy()))
        try:app.mainloop()
        finally:app.store.close()
    assert not errors,errors


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--language');parser.add_argument('--data',type=Path);parser.add_argument('--reopen',action='store_true');args=parser.parse_args()
    ctk.set_appearance_mode('dark')
    if args.language:check(args.data,args.language,args.reopen)
    else:
        with tempfile.TemporaryDirectory() as folder:
            for language in LANGUAGE_CODES:
                path=Path(folder)/(language+'.db')
                for flags in ([],['--reopen']):
                    subprocess.run([sys.executable,'-X','faulthandler','-u',str(Path(__file__).resolve()),'--language',language,'--data',str(path),*flags],check=True,timeout=25)
        print('PASS: four translated interfaces, canonical dropdowns, unchanged user content, independent answer language, draft retention, compact scrolling, trace cleanup and fresh-process language application',flush=True)
