"""Native four-language UI, canonical choices, opaque content and restart checks."""
import argparse
import sqlite3
import subprocess
import sys
import tempfile
import traceback
import tkinter
from pathlib import Path
from unittest.mock import patch

import customtkinter as ctk
from app import Dashboard
from storage import Store
from preferences import DEFAULTS
from theme import COLORS as C
from localization import Translator, LANGUAGE_CODES
from localization_widgets import LocalizedOptionMenu


def widgets(root):
    for child in root.winfo_children():
        yield child
        yield from widgets(child)


def dashboard_layout(app, scale):
    """Measure startup DPI in fresh processes, not live CTk scaling changes."""
    def visible(widget):
        app.update_idletasks()
        canvas = app.scroll._parent_canvas
        assert widget.winfo_ismapped()
        left, top = widget.winfo_rootx(), widget.winfo_rooty()
        right, bottom = left + widget.winfo_width(), top + widget.winfo_height()
        assert canvas.winfo_rootx() <= left and right <= canvas.winfo_rootx() + canvas.winfo_width(), (app.translator.language, widget, left, right, canvas.winfo_width())
        assert canvas.winfo_rooty() <= top and bottom <= canvas.winfo_rooty() + canvas.winfo_height(), (app.translator.language, widget, top, bottom, canvas.winfo_height())

    def settle():
        ready = ctk.BooleanVar(master=app, value=False)
        app.after(200, lambda: ready.set(True))
        app.wait_variable(ready)
        app.reflow(); app.update_idletasks()

    long_name = ('Длинный предмет ' + 'математика ' * 9).strip()
    sid = app.store.create_subject(long_name)
    app.refresh_data(); app.select_subject(long_name); app.refresh_data(); settle()
    assert app.layout_mode == 'compact'
    assert app.subject_selection.get() == long_name and app.selected_subject_id == sid
    app.scroll._parent_canvas.yview_moveto(0)
    for widget in (app.start_button, app.subject_picker, app.search, app.manage_subjects_button):
        app.scroll.scroll_to_widget(widget)
        visible(widget)
    card = next(card for name, card in app.subject_cards if name == long_name)
    title = next(w for w in card.winfo_children() if isinstance(w,ctk.CTkLabel) and w.cget('text') == long_name)
    assert title.cget('wraplength') <= card.winfo_width() / scale - 30
    assert title.winfo_height() > 28 * scale
    assert any(isinstance(w,ctk.CTkLabel) and w.cget('text')==app.translator.text("One thing at a time.") for w in widgets(app.study_panel))
    app.store.start_focus_checkpoint(sid, 900)
    app.store.release_focus(); app.refresh_focus_recovery(); settle()
    app.scroll.scroll_to_widget(app.recovery_panel)
    for widget in app.recover_focus_button.master.winfo_children():
        if isinstance(widget,ctk.CTkButton): visible(widget)
    visible(app.recovery_status)
    app.discard_focus(); app.update_idletasks(); visible(app.discard_focus_button)
    app.cancel_focus_discard(); app.recover_focus()
    assert app.session_open and app.running_since is None
    with patch.object(app.store,'add_session',side_effect=sqlite3.OperationalError('full')):
        assert not app.finish_focus()
    app.show_focus_retry(); app.update_idletasks()
    visible(app.finish_button); visible(app.focus_retry_label)
    assert app.focus_retry_label.cget('text')
    assert app.finish_focus()
    app.store.delete_subject(sid); app.refresh_data()


def practice_layout(app, scale):
    """Long-content running/setup/result/history in each language/startup DPI."""
    sid = app.store.create_subject(('Практика ' + 'предмет ' * 12).strip())
    prompt = ('Длинный вопрос для проверки переноса и прокрутки. ' * 18).strip()
    answers = [(letter + ' ' + 'Подробный вариант ответа. ' * 15).strip() for letter in 'ABCD']
    explanation = 'SNAPSHOT_EXPLANATION_ONLY_AFTER_FINISH'
    app.store.create_question(sid, prompt, answers, 2, explanation=explanation)
    aid = app.store.start_practice(sid, 1, minutes=5)
    app.navigate('Practice Tests'); page = app.practice_page
    app.update_idletasks()
    assert page.run.winfo_ismapped() and not page.results.winfo_ismapped()
    assert page.prompt.cget('wraplength') <= page.prompt.master.winfo_width() / scale - 30
    assert page.prompt.winfo_height() > 60 * scale
    assert page.answer_progress.get() == 0
    assert all(row.cget('fg_color') == C['card'] for row in page.answer_rows)
    assert not any(isinstance(w,ctk.CTkLabel) and explanation in w.cget('text') for w in widgets(page.run))
    for row, label in zip(page.answer_rows,page.answer_labels):
        assert label.cget('wraplength') <= row.winfo_width() / scale - 100
    def click_row(index):
        row = page.answer_rows[index]
        children = (row.nametowidget(name) for name in row.tk.call('winfo','children',str(row)))
        canvas = next(w for w in children if isinstance(w,tkinter.Canvas))
        canvas.event_generate('<Button-1>', x=4, y=4)
        app.update_idletasks()
    def selected(index):
        assert page.choice.get() == index
        assert app.store.practice_items(aid)[0]['selected_option'] == (None if index == -1 else index)
        assert [row.cget('fg_color') == C['selected'] for row in page.answer_rows] == [i == index for i in range(4)]
        assert page.answer_progress.get() == (0 if index == -1 else 1)
    click_row(1); selected(1)  # Highlight the choice, not the correct answer (C).
    text = next(w for w in page.answer_labels[3].winfo_children() if isinstance(w,tkinter.Label))
    text.event_generate('<Button-1>'); app.update_idletasks(); selected(3)
    with patch.object(app.store,'save_practice_answer',side_effect=sqlite3.OperationalError('full')):
        click_row(0)
    selected(3)
    page.clear_button.invoke(); selected(-1)
    page.show_config(); click_row(0); page.radios[2].invoke(); selected(-1)
    page.resume()  # Keep the run gridded to isolate the off-page guard too.
    app.navigate('Dashboard'); text.event_generate('<Button-1>'); page.radios[2].invoke(); selected(-1)
    app.navigate('Practice Tests'); app.update_idletasks(); selected(-1)
    click_row(1); selected(1)
    app.scroll._parent_canvas.yview_moveto(1); app.update_idletasks()
    canvas=app.scroll._parent_canvas
    for button in (page.previous_button,page.next_button,page.clear_button,page.finish_button):
        assert button.winfo_ismapped()
        assert button.winfo_rootx() >= canvas.winfo_rootx()
        assert button.winfo_rootx()+button.winfo_width() <= canvas.winfo_rootx()+canvas.winfo_width()
        assert button.winfo_rooty()+button.winfo_height() <= canvas.winfo_rooty()+canvas.winfo_height()
    page.finish_button.invoke(); page.confirm_button.invoke(); app.update_idletasks()
    assert page.results.winfo_ismapped() and app.store.practice_attempt(aid)['status']=='completed'
    assert any(isinstance(w,ctk.CTkLabel) and explanation in w.cget('text') for w in widgets(page.results))
    for label in (w for w in widgets(page.results) if isinstance(w,ctk.CTkLabel)):
        if label.cget('wraplength'):
            assert label.cget('wraplength') <= label.master.winfo_width()/scale - 30
    page.show_config(); app.update_idletasks()
    assert page.start_button.winfo_rootx()+page.start_button.winfo_width() <= canvas.winfo_rootx()+canvas.winfo_width()
    app.store.delete_subject(sid); app.refresh_data(); app.navigate('Dashboard')


def flashcard_layout(app, scale):
    """Long-content reveal/rating, retry and compact actions in all languages."""
    sid = app.store.create_subject('Карточки — проверка')
    did = app.store.create_deck(sid, 'Длинная колода — ' + 'тема ' * 15)
    front = ('Длинный вопрос для проверки чтения и переноса. ' * 45)[:1900].strip()
    back = ('Подробный ответ с объяснением и несколькими строками. ' * 70)[:3700].strip()
    cid = app.store.create_flashcard(did,front,back)
    app.store.create_flashcard(did,'Second prompt','Second answer')
    app.navigate('Flashcards');page=app.flashcard_page;page.open_deck(did);app.update_idletasks()
    canvas=app.scroll._parent_canvas
    for button in (page.new_card_button,page.study_button,page.csv_button):
        assert button.winfo_rootx()+button.winfo_width() <= canvas.winfo_rootx()+canvas.winfo_width()
    page.start_review(did);app.update_idletasks()
    assert page.current_card['id']==cid and not page.revealed
    assert page.answer.cget('text')=='' and page.answer_panel.winfo_manager()==''
    assert page.rating_actions.winfo_manager()==''
    assert all(b.cget('state')=='disabled' for b in page.rating_buttons.values())
    assert page.front_label.cget('text')==front and page.front_label.cget('justify')=='left'
    assert page.front_label.cget('wraplength') <= page.front_label.master.winfo_width()/scale-30
    before=len(app.store.flashcard_history())
    page.rate('Good',cid,page.current_card['revision'])
    assert len(app.store.flashcard_history())==before
    def footer_bounds(buttons):
        app.update_idletasks();canvas.yview_moveto(1);app.update_idletasks()
        for button in buttons:
            assert button.winfo_ismapped()
            assert button.winfo_rootx()>=canvas.winfo_rootx()
            assert button.winfo_rootx()+button.winfo_width()<=canvas.winfo_rootx()+canvas.winfo_width()
            assert button.winfo_rooty()>=canvas.winfo_rooty()
            assert button.winfo_rooty()+button.winfo_height()<=canvas.winfo_rooty()+canvas.winfo_height()
    footer_bounds([page.reveal_button])
    page.reveal_button.invoke();app.update_idletasks()
    assert page.revealed and page.answer.cget('text')==back
    assert page.answer_panel.winfo_ismapped() and not page.reveal_button.winfo_ismapped()
    assert page.answer.cget('justify')=='left'
    assert page.answer.cget('wraplength') <= page.answer.master.winfo_width()/scale-30
    assert list(page.rating_buttons)==['Again','Hard','Good','Easy']
    assert [int(b.grid_info()['row']) for b in page.rating_buttons.values()]==[1,1,2,2]
    footer_bounds(page.rating_buttons.values())
    with patch.object(app.store,'rate_flashcard',side_effect=sqlite3.OperationalError('full')):
        page.rating_buttons['Good'].invoke()
    assert page.revealed and page.current_card['id']==cid and page.answer.cget('text')==back
    assert page.review_notice.cget('text') and page.review_notice.winfo_manager()=='grid'
    assert len(app.store.flashcard_history())==before
    app.navigate('Dashboard');page.rating_buttons['Good'].invoke()
    assert len(app.store.flashcard_history())==before
    app.navigate('Flashcards');app.update_idletasks()
    assert not page.revealed and page.answer_panel.winfo_manager()==''
    page.reveal_button.invoke();app.update_idletasks()
    stale=dict(page.current_card)
    # The rating commits even if loading the next card fails; only Refresh may retry the read.
    read_card = app.store.flashcard
    def fail_next_read(card_id):
        if card_id != cid:
            raise sqlite3.OperationalError('read')
        return read_card(card_id)
    with patch.object(app.store,'flashcard',side_effect=fail_next_read):
        page.rating_buttons['Good'].invoke()
    assert len(app.store.flashcard_history())==before+1
    assert page.current_card is None and page.review_refresh_pending
    assert all(b.cget('state')=='disabled' for b in page.rating_buttons.values())
    assert app.translator.text('Review saved. Refresh card to continue; do not rate it again.') in page.review_notice.cget('text')
    footer_bounds([page.review_notice])
    page.rate('Good',stale['id'],stale['revision'])
    assert len(app.store.flashcard_history())==before+1
    page.show_review();assert not page.review_refresh_pending and not page.revealed
    page.reveal_button.invoke();page.rating_buttons['Good'].invoke()
    assert page.current_card is None
    page.show_deck(did);assert page.study_button.cget('state')=='disabled'
    page.show_history();app.update_idletasks()
    assert any(isinstance(w,ctk.CTkLabel) and w.cget('text')==back for w in widgets(page.body))
    app.store.delete_deck(did);app.store.delete_subject(sid)
    page.show_decks();app.navigate('Dashboard')


def check(path,language,reopen=False,scale=1.0):
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
        ctk.set_widget_scaling(scale); ctk.set_window_scaling(scale)
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
                dashboard_layout(app, scale)
                practice_layout(app, scale)
                flashcard_layout(app, scale)
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
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--language');parser.add_argument('--data',type=Path);parser.add_argument('--reopen',action='store_true');parser.add_argument('--scale',type=float,choices=(1.0,1.5),default=1.0);args=parser.parse_args()
    ctk.set_appearance_mode('dark')
    if args.language:check(args.data,args.language,args.reopen,args.scale)
    else:
        with tempfile.TemporaryDirectory() as folder:
            for language in LANGUAGE_CODES:
                path=Path(folder)/(language+'.db')
                for flags in ([],['--reopen']):
                    subprocess.run([sys.executable,'-X','faulthandler','-u',str(Path(__file__).resolve()),'--language',language,'--data',str(path),*flags],check=True,timeout=25)
                scaled=Path(folder)/(language+'-150.db')
                subprocess.run([sys.executable,'-X','faulthandler','-u',str(Path(__file__).resolve()),'--language',language,'--data',str(scaled),'--scale','1.5'],check=True,timeout=25)
        print('PASS: four translated interfaces, compact Dashboard at 100/150 percent including recovery/retry/long selected names, Practice selection/rollback/hidden events/long text/results/footer at both scales, Flashcard reveal/rating/long text/postcommit retry at both scales, canonical dropdowns, unchanged user content, independent answer language, draft retention, compact scrolling, trace cleanup and fresh-process language application',flush=True)
