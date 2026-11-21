"""Live appearance and state-preservation checks, intended for Xvfb/container runs."""
import argparse
import os
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
from preferences import DEFAULTS
from storage import Store
from theme import COLORS as C


def run(path, reopen=False, screenshots=None):
    errors=[]
    with patch('socket.create_connection',side_effect=AssertionError('Appearance must not connect')), patch('darkdetect.theme',return_value='Dark') as detector, patch('appearance.SYSTEM_MODE_SUPPORTED',True):
        ctk.set_default_color_theme('dark-blue')
        app=Dashboard(path);settings=app.settings_page
        def guard(callback):
            def wrapped():
                try:callback()
                except Exception as exc:errors.append(str(exc));traceback.print_exc();app.destroy()
            return wrapped
        def save(mode):
            app.navigate('Settings');settings.appearance_mode.set(mode);settings.save_button.invoke();app.update_idletasks()
            assert app.preferences['appearance_mode']==mode and app.store.preferences()['appearance_mode']==mode
        def resolved(mode):
            assert ctk.get_appearance_mode()==mode
            assert tkinter.Tk.cget(app,'background')==C['bg'][0 if mode=='Light' else 1]
        def contrast_audit():
            sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
            from test_appearance import contrast
            index=0 if ctk.get_appearance_mode()=='Light' else 1
            def color(value,widget):
                if isinstance(value,(list,tuple)):value=value[index]
                rgb=widget.winfo_rgb(value)
                return '#'+''.join(f'{channel//257:02x}' for channel in rgb)
            def background(widget,own=True):
                current=widget if own else widget.master
                while current is not None:
                    try:value=current.cget('fg_color')
                    except (ValueError,tkinter.TclError):value=None
                    if value and value!='transparent':return color(value,widget)
                    current=current.master
                raise AssertionError('No visible background found')
            def visit(parent):
                for widget in parent.winfo_children():
                    if widget.winfo_ismapped() and isinstance(widget,(ctk.CTkLabel,ctk.CTkButton,ctk.CTkCheckBox,ctk.CTkEntry,ctk.CTkOptionMenu,ctk.CTkRadioButton)):
                        own=not isinstance(widget,(ctk.CTkCheckBox,ctk.CTkRadioButton))
                        text=widget.cget('text_color')
                        if isinstance(widget,(ctk.CTkButton,ctk.CTkOptionMenu)) and widget.cget('state')=='disabled':
                            text=widget.cget('text_color_disabled')
                        bg=background(widget,own)
                        assert contrast(color(text,widget),bg)>=4.5,(type(widget).__name__,text,bg)
                        if isinstance(widget,ctk.CTkEntry) and widget.cget('placeholder_text'):
                            assert contrast(color(widget.cget('placeholder_text_color'),widget),bg)>=4.5
                    visit(widget)
            visit(app)
        def image(mode):
            if screenshots:
                from PIL import ImageGrab
                screenshots.mkdir(parents=True,exist_ok=True)
                app.geometry('1440x900');app.navigate('Dashboard');app.update_idletasks();app.update()
                ImageGrab.grab(xdisplay=os.environ.get('DISPLAY')).save(screenshots/(mode+'.png'))
                app.geometry('1024x700');app.update_idletasks()
        def initial():
            app.geometry('1024x700');app.update_idletasks();resolved('Dark')
            sid=app.store.create_subject('Light русский');app.store.create_question(sid,'Original?', ['a','b','c','d'],1)
            app.store.create_deck(sid,'Dark')
            aid=app.store.start_practice(sid,1);app.store.save_practice_answer(aid,0,1)
            app.practice_page.load();app.start_focus(sid)
            app.open_question_bank(sid);bank=app.question_bank;bank.show_question_form()
            bank.prompt_entry.insert('1.0','Unsaved question draft');original=bank.prompt_entry
            app.tutor_page.prompt.insert('1.0','Unsent Tutor draft')
            target=app.focus_target;started=app.running_since
            app.navigate('Settings');settings.appearance_mode.set('Light')
            app.navigate('Dashboard');app.navigate('Settings')
            assert settings.appearance_mode.get()=='Light';resolved('Dark')
            with patch.object(app.store,'save_preferences',side_effect=sqlite3.OperationalError('full')):
                settings.save_button.invoke()
            resolved('Dark');assert settings.appearance_mode.get()=='Light'
            save('Light');resolved('Light')
            assert app.focus_target==target and app.running_since==started and app.session_open
            assert bank.prompt_entry is original and original.get('1.0','end-1c')=='Unsaved question draft'
            assert app.store.active_practice()['id']==aid and app.store.active_practice()['answered']==1
            assert app.tutor_page.prompt.get('1.0','end-1c')=='Unsent Tutor draft'
            # Another window's committed settings cannot be overwritten or visually applied by a stale Save.
            other=Store(path)
            try:other.save_preferences(dict(DEFAULTS,appearance_mode='Dark'),expected_revision=app.store.preferences()['revision'])
            finally:other.close()
            settings.appearance_mode.set('System');settings.save_button.invoke()
            resolved('Light');assert settings.appearance_mode.get()=='System'
            assert 'another window' in settings.status.cget('text')
            settings.reload_button.invoke();settings.reload_button.invoke()
            assert settings.appearance_mode.get()=='Dark';resolved('Light')
            for mode in ('Dark','Light'):
                save(mode);resolved(mode)
                for screen in ('Dashboard','My Subjects','Flashcards','Practice Tests','AI Tutor','Statistics','Settings'):
                    app.navigate(screen);app.update_idletasks();resolved(mode);contrast_audit()
                image(mode)
            app.open_question_bank(sid);assert bank.prompt_entry is original
            assert original.get('1.0','end-1c')=='Unsaved question draft'
            app.pause_focus();save('System')
            app.after(250,guard(system_dark))
        def system_dark():
            resolved('Dark');assert app.store.preferences()['appearance_mode']=='System'
            detector.return_value='Light';app.after(250,guard(system_light))
        def system_light():
            resolved('Light')
            assert settings.appearance_mode.get()=='System'
            save('Dark');detector.return_value='Light';app.after(250,guard(explicit_mode))
        def explicit_mode():
            resolved('Dark')
            with patch('appearance.SYSTEM_MODE_SUPPORTED',False):
                save('System');resolved('Light')
            save('Light')
            app.update_idletasks();right=app.winfo_rootx()+app.winfo_width()
            for widget in (settings.save_button,settings.reload_button,settings.copy_button,settings.appearance_menu):
                assert widget.winfo_rootx()+widget.winfo_width()<=right
            app.scroll._parent_canvas.yview_moveto(1);app.update_idletasks();assert app.scroll._parent_canvas.yview()[0]>0
            app.close()
        def resumed():
            assert app.preferences['appearance_mode']=='Light';resolved('Light')
            assert app.store.subjects()[0]['name']=='Light русский'
            assert app.store.active_practice()['answered']==1
            app.close()
        def callback_error(kind,value,tb):
            errors.append(str(value));traceback.print_exception(kind,value,tb);app.destroy()
        app.report_callback_exception=callback_error
        app.after(700,guard(resumed if reopen else initial))
        app.after(22000,lambda:(errors.append('Appearance check timed out'),app.destroy()))
        try:app.mainloop()
        finally:app.store.close()
    assert not errors,errors


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reopen',type=Path);parser.add_argument('--screenshots',type=Path);args=parser.parse_args()
    if args.reopen:run(args.reopen,True)
    else:
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'appearance.db';run(path,screenshots=args.screenshots)
            subprocess.run([sys.executable,'-X','faulthandler','-u',str(Path(__file__).resolve()),'--reopen',str(path)],check=True,timeout=30)
        print('PASS: explicit Save/live palette, failed/stale writes, untouched drafts/focus/practice/Tutor prompt, all screens, OS-mode notifications, compact scrolling and fresh-process appearance',flush=True)
