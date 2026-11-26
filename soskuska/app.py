"""SOSkúška native Dashboard. Run: python soskuska/app.py."""
from localization_widgets import LocalizedOptionMenu
from localization import tr, Translator
import argparse
import os
import platform
import sqlite3
import sys
import time
from datetime import date
from pathlib import Path

import tkinter

# Apple's bundled Tk 8.5 can display an empty window on recent macOS.
# Fail before creating the root so the user gets an actionable error instead.
if sys.platform == "darwin" and tkinter.TkVersion < 8.6:
    raise SystemExit(
        "SOSkúška cannot use macOS system Tk 8.5.\n"
        "From the project directory, run: .venv-macos/bin/python soskuska/app.py\n"
        "Alternatively use Python with Tk 8.6 or newer."
    )

import customtkinter as ctk
from storage import Store, default_database
from scrolling import DashboardScrollFrame
from subjects import SubjectPage
from question_bank import QuestionBankPage
from practice_page import PracticePage
from flashcard_page import FlashcardPage
from statistics_page import StatisticsPage
from tutor_page import TutorPage
from settings_page import SettingsPage
from preferences import AI_KEYS
from startup_errors import report_startup_error
from appearance import apply_appearance
from studio_widgets import (FocusClock, MonthAgenda, MONTHS, nav_icon, paw_icon, stat_icon,
                            cat_avatar, study_scene, sidebar_decor)
from panel_layout import wrap_labels
from branding import sidebar_logo, install_window_icon
from ai_generation_panel import generation_busy, shutdown_generators

APP_VERSION = '0.30.1'

from theme import COLORS as C

SAVE_RETRY_NOTICE = "This session could not be saved. Press Finish to retry saving it."
REFRESH_RETRY_NOTICE = "Could not refresh the Dashboard. Retrying automatically."

NAV = [("Dashboard", "▦"), ("My Subjects", "▤"), ("Flashcards", "▱"),
       ("Practice Tests", "☑"), ("AI Tutor", "◇"), ("Statistics", "▥")]


def data_path():
    if sys.platform == "win32":
        base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Application Support"
    else:
        base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share"))
    return default_database(base)


class Dashboard(ctk.CTk):
    def __init__(self, database=None):
        ctk.set_appearance_mode("Dark")  # Disable implicit OS polling before constructing Tk.
        super().__init__()
        self.title(tr(self, 'SOSkúška'))
        install_window_icon(self)
        self.geometry("1440x900")
        self.minsize(1024, 700)
        self.configure(fg_color=C["bg"])
        self.family = "Segoe UI" if platform.system() == "Windows" else "Helvetica" if sys.platform == "darwin" else "Noto Sans"
        # Editorial serif for the wordmark only; Tk falls back if it is missing.
        self.serif_family = "Georgia" if sys.platform in ("darwin", "win32") else "DejaVu Serif"
        self.store = Store(database or data_path())
        self.preferences = self.store.preferences()
        apply_appearance(self.preferences["appearance_mode"])
        self.translator = Translator(self.preferences["ui_language"])
        self.saved_today_seconds = 0
        self.data_restoring = False
        self.running_since = None
        self.session_seconds = 0.0
        self.focus_run_id = None
        self.last_checkpoint = 0.0
        self.recovery_record = None
        self.pending_focus_discard = False
        self.session_open = False
        self.session_save_failed = False
        self.refresh_pending = False
        self.session_subject_id = None
        self.session_subject_name = None
        self.current_page = "Dashboard"
        self.selected_subject_id = None
        self.active_day = date.today()
        self.focus_target = self.preferences["focus_minutes"] * 60
        self.collapsed = False
        self.layout_mode = None
        self.resize_job = None
        self.notice_job = None
        self.focus_reveal_job = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.build_sidebar()
        self.build_content()
        self.backup_notice=self.label(self,'',12,'hover',wraplength=900)
        self.subject_page = SubjectPage(self.scroll, self)
        self.subject_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.subject_page.grid_remove()
        self.question_bank = QuestionBankPage(self.scroll, self)
        self.question_bank.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.question_bank.grid_remove()
        self.practice_page = PracticePage(self.scroll, self)
        self.practice_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.practice_page.grid_remove()
        self.flashcard_page = FlashcardPage(self.scroll, self)
        self.flashcard_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.flashcard_page.grid_remove()
        self.statistics_page = StatisticsPage(self.scroll, self)
        self.statistics_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.statistics_page.grid_remove()
        self.tutor_page = TutorPage(self.scroll, self)
        self.tutor_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.tutor_page.grid_remove()
        self.settings_page = SettingsPage(self.scroll, self)
        self.settings_page.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        self.settings_page.grid_remove()
        self.bind("<Configure>", self.on_resize)
        self.bind("<Control-k>", self.focus_search)
        self.bind("<Command-k>", self.focus_search)
        self.bind("<Escape>", self.clear_search)
        self.protocol("WM_DELETE_WINDOW", self.close)
        if self.tk.call("tk", "windowingsystem") == "aqua":
            # The native application-menu Quit does not send WM_DELETE_WINDOW.
            self.createcommand("::tk::mac::Quit", self.close)
        self.refresh_data()
        self.refresh_focus_recovery()
        self.after(100, self.reflow)
        self.after(250, self.tick)

    def display_date(self, day):
        if self.translator.language=='English':return day.strftime('%A, %B %d, %Y')
        return day.strftime('%d.%m.%Y')

    def font(self, size=14, bold=False):
        return ctk.CTkFont(family=self.family, size=size, weight="bold" if bold else "normal")

    def label(self, parent, text, size=14, color="text", bold=False, **kwargs):
        return ctk.CTkLabel(parent, text=text, font=self.font(size, bold),
                            text_color=C[color], anchor="w", **kwargs)

    def frame(self, parent, card=False, **kwargs):
        return ctk.CTkFrame(parent, fg_color=C["card"] if card else "transparent",
                            corner_radius=16 if card else 0,
                            border_width=0, border_color=C["border"], **kwargs)

    def button(self, parent, text, command, primary=False, **kwargs):
        if self.translator.language!='English' and 'width' in kwargs:
            kwargs['width']=max(kwargs['width'],self.font(14,primary).measure(text)+24)
        # Pill-shaped controls: deep-lavender primary, outlined soft-violet secondary.
        return ctk.CTkButton(parent, text=text, command=command, height=38,
                             corner_radius=18, font=self.font(14, primary),
                             fg_color=C["primary"] if primary else C["raised"],
                             hover_color=C["primary_hover"] if primary else C["secondary_hover"],
                             text_color=C["on_primary"] if primary else C["text"],
                             text_color_disabled=C["disabled_on_primary"] if primary else C["secondary"], border_width=0 if primary else 1,
                             border_color=C["outline"], **kwargs)

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=216, corner_radius=0, fg_color=C['nav_bg'])
        self.sidebar.grid(row=0,column=0,sticky='nsew')
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0,weight=1)
        self.sidebar.grid_rowconfigure(3,weight=1)
        brand=self.frame(self.sidebar)
        brand.grid(row=0,column=0,padx=18,pady=(28,36),sticky='ew')
        brand.grid_columnconfigure(1,weight=1)
        self.brand_logo = sidebar_logo()
        self.brand_tile = ctk.CTkLabel(brand, text='', image=self.brand_logo,
                                     width=40, height=40, fg_color='transparent', text_color=C['nav_text'])
        self.brand_tile.grid(row=0,column=0,padx=(0,10))
        self.brand=ctk.CTkLabel(brand,text='SOSkúška',font=ctk.CTkFont(family=self.serif_family,size=17,weight='bold'),
                                text_color=C['nav_text'],anchor='w')
        self.brand.grid(row=0,column=1,sticky='w')
        self.collapse_btn=ctk.CTkButton(brand,text='‹',width=24,height=30,corner_radius=8,
            fg_color='transparent',hover_color=C['nav_hover'],text_color=C['nav_secondary'],command=self.toggle_sidebar)
        self.collapse_btn.grid(row=0,column=2)
        nav=self.frame(self.sidebar)
        nav.grid(row=1,column=0,padx=12,sticky='ew')
        self.nav_buttons=[]
        self.nav_icons={(name,active):nav_icon(name,active) for name,_ in [*NAV,('Settings','')] for active in (False,True)}
        for index,(name,_) in enumerate(NAV):
            button=ctk.CTkButton(nav,text=tr(self,name),image=self.nav_icons[name,index==0],compound='left',
                anchor='w',height=44,corner_radius=14,font=self.font(13,index==0),border_width=0,
                fg_color=C['nav_selected'] if index==0 else 'transparent',hover_color=C['nav_hover'],
                text_color=C['nav_accent'] if index==0 else C['nav_secondary'],command=lambda name=name:self.navigate(name))
            button.pack(fill='x',pady=4)
            self.nav_buttons.append(button)
        self.settings_btn=ctk.CTkButton(self.sidebar,text=tr(self,'Settings'),image=self.nav_icons['Settings',False],
            compound='left',anchor='w',height=44,corner_radius=14,font=self.font(13),
            fg_color='transparent',hover_color=C['nav_hover'],text_color=C['nav_secondary'],command=lambda:self.navigate('Settings'))
        self.settings_btn.grid(row=4,column=0,padx=12,pady=(12,20),sticky='ew')
        self.sidebar_art=sidebar_decor()
        self.sidebar_decor=ctk.CTkLabel(self.sidebar,text='',image=self.sidebar_art,fg_color='transparent',text_color=C['nav_text'])
        self.sidebar_decor.grid(row=3,column=0,sticky='s',padx=12,pady=(12,0))
        # Purely decorative: show it only when the flexible row can hold it whole.
        self.sidebar.bind('<Configure>',lambda _e:self.after_idle(self.fit_sidebar_decor),add='+')
        self.footer=self.frame(self.sidebar)
        self.footer.grid(row=5,column=0,sticky='ew',padx=22,pady=(8,24))
        self.label(self.footer,tr(self,'LOCAL WORKSPACE'),10,'nav_secondary').pack(anchor='w',pady=(0,10))
        self.label(self.footer,tr(self,'Local student'),13,'nav_text',bold=True).pack(anchor='w')
        self.label(self.footer,tr(self,'Offline · Stored on this device'),11,'nav_secondary',wraplength=170).pack(anchor='w',pady=(3,18))
        self.ai_status=self.label(self.footer,tr(self,'○  AI not connected'),11,'nav_secondary',wraplength=170)
        self.ai_status.pack(anchor='w')
        self.label(self.footer,tr(self,'Study workspace · {v0}',v0=f'v{APP_VERSION}'),10,'nav_secondary').pack(anchor='w',pady=(8,0))
        self.focus_alert=self.button(self.sidebar,tr(self,'Focus needs saving'),self.show_focus_retry,width=40)

    def build_content(self):
        self.scroll=DashboardScrollFrame(self,fg_color=C['bg'],corner_radius=0,
            scrollbar_button_color=C['border'],scrollbar_button_hover_color=C['secondary'])
        self.scroll.grid(row=0,column=1,sticky='nsew')
        self.scroll.grid_columnconfigure(0,weight=1)
        self.content=self.frame(self.scroll)
        self.content.grid(row=0,column=0,sticky='ew',padx=28,pady=28)
        self.content.grid_columnconfigure(0,weight=1)
        head=self.frame(self.content)
        head.grid(row=0,column=0,sticky='ew',pady=(0,24))
        head.grid_columnconfigure(0,weight=1)
        greeting=self.frame(head)
        greeting.grid(row=0,column=0,sticky='ew')
        greeting.grid_columnconfigure(1,weight=1)
        self.greeting_paw=paw_icon(24)
        self.dashboard_title=self.label(greeting,tr(self,'Good to see you back!'),30,bold=True,wraplength=1000)
        self.dashboard_title.grid(row=0,column=0,sticky='w')
        self.greeting_paw_label=ctk.CTkLabel(greeting,text='',image=self.greeting_paw,fg_color='transparent',text_color=C['text'])
        self.greeting_paw_label.grid(row=0,column=1,sticky='w',padx=(10,0))
        self.dashboard_subtitle=self.label(greeting,tr(self,'Ready for another study session?'),14,'secondary',wraplength=1000)
        self.dashboard_subtitle.grid(row=1,column=0,columnspan=2,sticky='ew',pady=(4,0))
        profile=self.frame(head)
        profile.grid(row=0,column=1,sticky='ne',padx=(16,0))
        self.avatar_image=cat_avatar(46)
        self.avatar=ctk.CTkLabel(profile,text='',image=self.avatar_image,fg_color='transparent',text_color=C['text'])
        self.avatar.grid(row=0,column=1,rowspan=2,padx=(12,0))
        self.label(profile,tr(self,'YOUR STUDY SPACE'),10,'secondary',bold=True).grid(row=0,column=0,sticky='e')
        self.date_label=self.label(profile,self.display_date(date.today()),11,'secondary')
        self.date_label.grid(row=1,column=0,sticky='e')
        self.metrics=self.frame(self.content)
        self.metrics.grid(row=1,column=0,sticky='ew',pady=(0,24))
        self.metric_cards,self.metric_values=[],[]
        self.metric_icons=[]
        for kind,name,val in [('time','Total study time','0h 00m'),('sessions','Study sessions','0'),
                              ('streak','Current streak','0 days'),('subjects','Subjects','0')]:
            card=self.frame(self.metrics,card=True)
            card.grid_columnconfigure(1,weight=1)
            icon_image=stat_icon(kind);self.metric_icons.append(icon_image)
            ctk.CTkLabel(card,text='',image=icon_image,fg_color='transparent',text_color=C['text']).grid(
                row=0,column=0,rowspan=2,padx=(16,12),pady=12)
            value=self.label(card,val,22,bold=True)
            value.grid(row=0,column=1,sticky='sw',padx=(0,14),pady=(10,0))
            caption=self.label(card,tr(self,name),11,'secondary',wraplength=150)
            caption.grid(row=1,column=1,sticky='nw',padx=(0,14),pady=(0,10))
            self.metric_cards.append(card);self.metric_values.append(value)
        self.columns=self.frame(self.content)
        self.columns.grid(row=2,column=0,sticky='ew')
        self.columns.grid_columnconfigure(0,weight=1)
        self.main=self.frame(self.columns);self.main.grid_columnconfigure(0,weight=1)
        self.rail=self.frame(self.columns);self.rail.grid_columnconfigure(0,weight=1)
        self.build_focus();self.build_subjects();self.build_rail()
        self.notice=self.label(self.content,tr(self,'Your subjects and study time are stored on this device.'),11,'secondary',wraplength=650)
        self.notice.grid(row=3,column=0,sticky='ew',pady=(20,0))

    def build_focus(self):
        self.study_panel=ctk.CTkFrame(self.main,fg_color=C['focus_bg'],corner_radius=24)
        self.study_panel.grid(row=0,column=0,sticky='ew')
        self.study_panel.grid_columnconfigure(0,weight=1)
        # Banner: copy on the left, illustrated window scene fading in on the right.
        self.focus_hero=ctk.CTkFrame(self.study_panel,fg_color='transparent')
        self.focus_hero.grid(row=0,column=0,columnspan=2,sticky='ew',padx=(24,10),pady=(8,0))
        self.focus_hero.grid_columnconfigure(0,weight=1)
        hero_copy=self.frame(self.focus_hero)
        hero_copy.grid(row=0,column=0,sticky='ew',pady=(12,0))
        hero_copy.grid_columnconfigure(0,weight=1)
        self.label(hero_copy,tr(self,'FOCUS ROOM'),10,'focus_secondary',bold=True).grid(row=0,column=0,sticky='w',pady=(0,6))
        self.hero_title=self.label(hero_copy,tr(self,'Continue studying'),25,'focus_text',bold=True,wraplength=360)
        self.hero_title.grid(row=1,column=0,sticky='ew')
        self.hero_subject=self.label(hero_copy,'',12,'focus_secondary',wraplength=360)
        self.hero_subject.grid(row=2,column=0,sticky='ew',pady=(6,0))
        self.scene_image=study_scene('focus_bg')
        self.focus_scene=ctk.CTkLabel(self.focus_hero,text='',image=self.scene_image,fg_color='transparent',text_color=C['focus_text'])
        self.focus_scene.grid(row=0,column=1,sticky='e')
        self.scene_visible=True
        self.focus_controller=self.frame(self.study_panel)
        self.focus_controller.grid(row=1,column=0,sticky='new',padx=24,pady=(12,24))
        focus=self.focus_controller
        focus.grid_columnconfigure(0,weight=1)
        self.label(focus,tr(self,'Choose a subject'),11,'focus_secondary').grid(row=2,column=0,sticky='w',pady=(0,6))
        self.study_actions=self.frame(focus)
        self.study_actions.grid(row=3,column=0,sticky='ew')
        self.study_actions.grid_columnconfigure(0,weight=1)
        self.subject_selection=ctk.StringVar(value='Add a subject first')
        self.subject_picker=LocalizedOptionMenu(self.study_actions,owner=self,translate_values=False,
            empty_text='Add a subject first',variable=self.subject_selection,values=[],command=self.select_subject,
            font=self.font(13),height=38,width=180,dynamic_resizing=False)
        self.subject_picker.grid(row=0,column=0,sticky='ew',pady=(0,10))
        self.start_button=self.button(self.study_actions,tr(self,'Start Studying  →'),self.start_focus,primary=True,width=160)
        self.start_button.grid(row=1,column=0,sticky='ew')
        self.study_hint=self.label(focus,tr(self,'Focus sessions are saved against the selected subject.'),11,'focus_secondary',wraplength=400)
        self.study_hint.grid(row=4,column=0,sticky='ew',pady=(8,12))
        self.timer_frame=self.frame(focus)
        self.timer_frame.grid(row=5,column=0,sticky='ew',pady=(0,12))
        self.timer_frame.grid_columnconfigure(1,weight=1)
        self.pause_button=self.button(self.timer_frame,tr(self,'Pause'),self.pause_focus,width=90)
        self.pause_button.grid(row=0,column=0,sticky='ew',padx=(0,8))
        self.finish_button=self.button(self.timer_frame,tr(self,'Finish'),self.finish_focus,primary=True,width=100)
        self.finish_button.grid(row=0,column=1,sticky='ew')
        self.focus_subject_label=self.label(self.timer_frame,'',11,'focus_secondary',wraplength=350)
        self.focus_subject_label.grid(row=1,column=0,columnspan=2,sticky='ew',pady=(6,0))
        self.focus_retry_label=self.label(self.timer_frame,'',12,'warning',wraplength=350)
        self.focus_retry_label.grid(row=2,column=0,columnspan=2,sticky='ew',pady=(6,0))
        self.timer_frame.grid_remove()
        self.recovery_panel=self.frame(focus)
        self.recovery_panel.grid(row=6,column=0,sticky='ew',pady=(0,14))
        self.recovery_panel.grid_columnconfigure(0,weight=1)
        self.label(self.recovery_panel,tr(self,'Saved focus session'),15,'focus_text',bold=True).grid(row=0,column=0,sticky='ew',pady=(0,6))
        self.recovery_status=self.label(self.recovery_panel,'',12,'focus_secondary',wraplength=350)
        self.recovery_status.grid(row=1,column=0,sticky='ew',pady=(0,10))
        recovery_actions=self.frame(self.recovery_panel)
        recovery_actions.grid(row=2,column=0,sticky='ew');recovery_actions.grid_columnconfigure(0,weight=1)
        self.recover_focus_button=self.button(recovery_actions,tr(self,'Recover paused'),self.recover_focus,primary=True,width=155)
        self.recover_focus_button.grid(row=0,column=0,sticky='ew',pady=(0,8))
        self.discard_focus_button=self.button(recovery_actions,tr(self,'Discard checkpoint'),self.discard_focus,width=175)
        self.discard_focus_button.grid(row=1,column=0,sticky='ew',pady=(0,8))
        self.button(recovery_actions,tr(self,'Refresh'),self.refresh_focus_recovery,width=110).grid(row=2,column=0,sticky='ew')
        self.recovery_panel.grid_remove()
        goal_row=self.frame(focus)
        goal_row.grid(row=7,column=0,sticky='ew',pady=(0,6));goal_row.grid_columnconfigure(0,weight=1)
        self.label(goal_row,tr(self,'Daily goal'),11,'focus_secondary').grid(row=0,column=0,sticky='w')
        self.goal=self.label(goal_row,tr(self,'0 / 60 min'),12,'focus_text',bold=True)
        self.goal.grid(row=0,column=1,sticky='e')
        self.goal_bar=ctk.CTkProgressBar(focus,height=5,fg_color=C['focus_track'],progress_color=C['focus_accent'])
        self.goal_bar.grid(row=8,column=0,sticky='ew',pady=(0,14))
        self.task_vars={}
        for row,(key,text,default) in enumerate([('review_subject','Review a subject',False),('focus','Complete a focus session',False)],9):
            var=ctk.BooleanVar(value=self.store.task(key,default));self.task_vars[key]=var
            check=ctk.CTkCheckBox(focus,text=tr(self,text),variable=var,font=self.font(11),
                text_color=C['focus_text'],checkmark_color=C['on_primary'],fg_color=C['primary'],
                hover_color=C['primary_hover'],border_color=C['border'],checkbox_width=16,checkbox_height=16,
                command=lambda k=key,v=var:self.save_task(k,v.get()))
            check.grid(row=row,column=0,sticky='w',pady=(0,9))
        self.focus_clock=FocusClock(self.study_panel,self)
        self.focus_clock.grid(row=1,column=1,sticky='n',padx=(0,24),pady=(30,16))
        self.timer_label=self.focus_clock.time_label
        self.focus_clock.set(self.focus_target,self.focus_target,tr(self,'Focus session'))
        self.focus_layout=None
        for parent in (hero_copy,focus,self.timer_frame,self.recovery_panel):wrap_labels(parent,self,inset=0)

    def build_subjects(self):
        self.subject_header=self.frame(self.main)
        header=self.subject_header
        header.grid(row=1,column=0,sticky='ew',pady=(24,14));header.grid_columnconfigure(0,weight=1)
        self.subject_heading=self.label(header,tr(self,'My subjects'),20,bold=True)
        self.subject_heading.grid(row=0,column=0,rowspan=2,sticky='w')
        self.subject_search_label=self.label(header,tr(self,'Search subjects…'),10,'secondary')
        self.subject_search_label.grid(row=0,column=1,sticky='w',padx=(12,10))
        self.query=ctk.StringVar();self.query.trace_add('write',lambda *_:self.filter_subjects())
        self.search=ctk.CTkEntry(header,placeholder_text=tr(self,'Search subjects…'),width=180,height=36,corner_radius=18,
            textvariable=self.query,fg_color=C['card'],border_width=1,border_color=C['outline'],text_color=C['text'],font=self.font(12),placeholder_text_color=C['secondary'])
        self.search.grid(row=1,column=1,padx=(12,10))
        self.manage_subjects_button=self.button(header,tr(self,'Manage subjects'),lambda:self.navigate('My Subjects'),width=140)
        self.manage_subjects_button.grid(row=0,column=2,rowspan=2)
        self.subject_grid=self.frame(self.main);self.subject_grid.grid(row=2,column=0,sticky='ew')
        self.subject_grid.grid_columnconfigure((0,1),weight=1,uniform='subject')
        self.subject_cards=[]
        self.add_subject_card=None
        self.empty=self.label(self.subject_grid,'',14,'secondary',wraplength=650,height=100)

    def build_rail(self):
        self.agenda=MonthAgenda(self.rail,self)
        self.agenda.grid(row=0,column=0,sticky='ew',pady=(0,22))
        self.label(self.rail,tr(self,'Upcoming exams'),16,bold=True).grid(row=1,column=0,sticky='w',pady=(0,12))
        self.exams=self.frame(self.rail)
        self.exams.grid(row=2,column=0,sticky='ew');self.exams.grid_columnconfigure(0,weight=1)
        self.label(self.rail,tr(self,'Recent study sessions'),16,bold=True).grid(row=3,column=0,sticky='w',pady=(22,12))
        self.activity=self.frame(self.rail,card=True)
        self.activity.grid(row=4,column=0,sticky='ew');self.activity.grid_columnconfigure(0,weight=1)

    def refresh_rail(self):
        today=date.today()
        exams=self.store.upcoming_exams();sessions=self.store.recent_sessions()
        for panel in (self.exams,self.activity):
            for widget in panel.winfo_children():widget.destroy()
        self.agenda.show(today,self.dashboard_subjects)
        if not exams:
            self.label(self.exams,tr(self,'No upcoming exams. Add a date in My Subjects.'),12,'secondary',wraplength=250).grid(row=0,column=0,sticky='ew',padx=8,pady=14)
        for index,exam in enumerate(exams):
            row=self.frame(self.exams,card=True);row.grid(row=index,column=0,sticky='ew',pady=(0,8));row.grid_columnconfigure(1,weight=1)
            day=date.fromisoformat(exam['exam_date']);days=(day-today).days
            badge=ctk.CTkLabel(row,text=f'{day.day:02d}\n{tr(self,MONTHS[day.month-1])[:3].upper()}',font=self.font(14,True),width=46,height=56,
                corner_radius=10,fg_color=C['selected'],text_color=C['hover'])
            badge.grid(row=0,column=0,rowspan=2,padx=(12,10),pady=12)
            title=self.label(row,exam['name'],13,bold=True,wraplength=180)
            title.grid(row=0,column=1,sticky='ew',padx=(0,12),pady=(13,0))
            when=tr(self,'Today') if days==0 else tr(self,'In {v0} days',v0=days)
            note=self.label(row,tr(self,'{v0} · {v1}',v0=exam['exam_date'],v1=when),11,'warning' if days<=7 else 'secondary',wraplength=180)
            note.grid(row=1,column=1,sticky='ew',padx=(0,12),pady=(0,12))
            row.bind('<Configure>',lambda event,labels=(title,note):[label.configure(
                wraplength=max(120,self.scroll.logical_pixels(event.width)-90)) for label in labels],add='+')
        if not sessions:
            self.label(self.activity,tr(self,'No saved sessions yet. Start with a short focus session.'),12,'secondary',wraplength=250).grid(row=0,column=0,sticky='ew',padx=16,pady=16)
        for index,session in enumerate(sessions):
            title=self.label(self.activity,session['subject_name'] or tr(self,'Unassigned session'),13,wraplength=250)
            title.grid(row=index*2,column=0,sticky='ew',padx=16,pady=(14,2))
            seconds=session['seconds']
            self.label(self.activity,tr(self,'{v0} · {v1}m {v2:02d}s',v0=session['day'],v1=seconds//60,v2=seconds%60),11,'secondary').grid(row=index*2+1,column=0,sticky='ew',padx=16,pady=(0,12))

    def on_resize(self, event):
        if event.widget is self or self.scroll.is_viewport(event.widget):
            if self.resize_job:
                self.after_cancel(self.resize_job)
            self.resize_job = self.after(120, self.reflow)

    def reflow(self):
        self.resize_job=None
        available=self.scroll.viewport_width()
        wide=available>=1100
        mode='wide' if wide else 'compact'
        main_width=available-56-(324 if wide else 0)
        self.dashboard_title.configure(wraplength=max(250,available-56-260))
        self.dashboard_subtitle.configure(wraplength=max(250,available-56-260))
        self.empty.configure(wraplength=max(200,main_width-32))
        show_scene=wide and main_width>=720
        if show_scene!=self.scene_visible:
            self.scene_visible=show_scene
            self.focus_scene.grid() if show_scene else self.focus_scene.grid_remove()
        horizontal=main_width>=650
        if horizontal!=self.focus_layout:
            self.focus_layout=horizontal
            self.study_panel.grid_columnconfigure(1,minsize=272 if horizontal else 0)
            self.focus_controller.grid(row=1,column=0,columnspan=1,sticky='new',padx=24,pady=(12,24))
            self.focus_clock.grid(row=1 if horizontal else 2,column=1 if horizontal else 0,
                sticky='n',padx=(0,24) if horizontal else 24,pady=(30,16) if horizontal else (0,20))
        compact_header=main_width<650
        if compact_header:
            self.subject_heading.grid(row=0,column=0,rowspan=1,sticky='w')
            self.manage_subjects_button.grid(row=0,column=1,rowspan=1,sticky='e')
            self.subject_search_label.grid(row=1,column=0,columnspan=2,sticky='w',padx=0,pady=(10,4))
            self.search.grid(row=2,column=0,columnspan=2,sticky='ew',padx=0)
        else:
            self.subject_heading.grid(row=0,column=0,rowspan=2,sticky='w')
            self.subject_search_label.grid(row=0,column=1,columnspan=1,sticky='w',padx=(12,10),pady=0)
            self.search.grid(row=1,column=1,columnspan=1,sticky='ew',padx=(12,10))
            self.manage_subjects_button.grid(row=0,column=2,rowspan=2,sticky='e')
        if mode==self.layout_mode:return
        self.layout_mode=mode
        self.columns.grid_columnconfigure(1,weight=0,minsize=300 if wide else 0)
        self.main.grid(row=0,column=0,sticky='nsew',padx=(0,24 if wide else 0))
        self.rail.grid(row=0 if wide else 1,column=1 if wide else 0,sticky='new',pady=(0 if wide else 24,0))
        for index in range(4):self.metrics.grid_columnconfigure(index,weight=1 if wide or index<2 else 0,uniform='metric' if wide or index<2 else '')
        for index,card in enumerate(self.metric_cards):
            col,row=(index,0) if wide else (index%2,index//2)
            card.grid(row=row,column=col,sticky='ew',padx=(0,12) if col<(3 if wide else 1) else 0,pady=(0,0 if wide else 12))
        self.layout_subject_cards()

    def layout_subject_cards(self):
        columns = 1 if self.layout_mode == "compact" else 2
        self.subject_grid.grid_columnconfigure(1, weight=0 if columns == 1 else 1,
                                               uniform="" if columns == 1 else "subject")
        for i, (_, card) in enumerate(self.subject_cards):
            col = i % columns
            card.grid(row=i//columns, column=col, sticky="nsew",
                      padx=(0, 6) if columns == 2 and col == 0 else (6, 0) if columns == 2 else 0,
                      pady=(0, 12))
        if self.add_subject_card is not None:
            i = len(self.subject_cards); col = i % columns
            self.add_subject_card.grid(row=i//columns, column=col, sticky="nsew",
                padx=(0, 6) if columns == 2 and col == 0 else (6, 0) if columns == 2 else 0, pady=(0, 12))

    def open_new_subject(self):
        self.navigate("My Subjects")
        # Never replace an open subject editor draft; only open an empty form.
        if self.current_page == "My Subjects" and not self.subject_page.form.winfo_manager():
            self.subject_page.show_form()

    def update_sidebar_selection(self,name):
        for button,(item,_) in zip([*self.nav_buttons,self.settings_btn],[*NAV,('Settings','')]):
            active=item==name
            button.configure(fg_color=C['nav_selected'] if active else 'transparent',
                text_color=C['nav_accent'] if active else C['nav_secondary'],
                image=self.nav_icons[item,active],font=self.font(13,active))

    def fit_sidebar_decor(self):
        """Grid the tail/paw art only if the weighted spacer row has room for all of it."""
        self.sidebar.update_idletasks()
        # The weighted row receives exactly the slack (or shrinks to it) whether or not
        # the decoration is gridded, so its bbox height is the free space either way.
        free = self.sidebar.grid_bbox(0, 3)[3]
        height = self.sidebar_decor.winfo_reqheight()
        needed = height + round(height * 12 / 70)  # art is 70 logical px with 12 px top padding
        fits = not self.collapsed and free >= needed
        if fits != bool(self.sidebar_decor.winfo_manager()):
            self.sidebar_decor.grid() if fits else self.sidebar_decor.grid_remove()

    def toggle_sidebar(self):
        self.collapsed=not self.collapsed
        self.sidebar.configure(width=76 if self.collapsed else 216)
        if self.collapsed:
            self.brand_tile.grid_remove();self.brand.grid_remove();self.collapse_btn.grid(column=0)
        else:
            self.brand_tile.grid();self.brand.grid();self.collapse_btn.grid(column=2)
        self.collapse_btn.configure(text='›' if self.collapsed else '‹')
        for button,(name,_) in zip([*self.nav_buttons,self.settings_btn],[*NAV,('Settings','')]):
            button.configure(text='' if self.collapsed else tr(self,name),anchor='center' if self.collapsed else 'w')
        self.footer.grid_remove() if self.collapsed else self.footer.grid()
        self.fit_sidebar_decor()
        self.focus_alert.configure(text='!' if self.collapsed else tr(self,'Focus needs saving'))
        self.after_idle(self.reflow)

    def navigate(self, name):
        if self.question_bank.importer.saving or self.flashcard_page.importer.saving:
            (self.flashcard_page.importer if self.flashcard_page.importer.saving else self.question_bank.importer).status.configure(text=tr(self, 'Wait for the CSV import to finish before navigating.'))
            return
        self.question_bank.importer.cancel()
        self.flashcard_page.importer.cancel()
        if name not in ("Dashboard", "My Subjects", "Practice Tests", "Flashcards", "Statistics", "AI Tutor", "Settings"):
            self.show_notice(tr(self, '{v0} will be available in a later version.', v0=name))
            return
        self.practice_page.cancel_explanation()
        self.cancel_focus_reveal()
        self.cancel_focus_discard()
        self.subject_page.cancel_delete()
        self.settings_page.backups.cancel_pending()
        self.current_page = name
        self.question_bank.grid_remove()
        self.practice_page.grid_remove()
        self.flashcard_page.grid_remove()
        self.statistics_page.grid_remove()
        self.tutor_page.grid_remove()
        self.settings_page.grid_remove()
        if name == "Settings":
            self.content.grid_remove()
            self.subject_page.grid_remove()
            self.settings_page.load()
            self.settings_page.grid()
        elif name == "AI Tutor":
            self.content.grid_remove()
            self.subject_page.grid_remove()
            self.tutor_page.load()
            self.tutor_page.grid()
        elif name == "Statistics":
            self.content.grid_remove()
            self.subject_page.grid_remove()
            self.statistics_page.load()
            self.statistics_page.grid()
        elif name == "Flashcards":
            self.content.grid_remove()
            self.subject_page.grid_remove()
            self.flashcard_page.load()
            self.flashcard_page.grid()
        elif name == "Practice Tests":
            self.content.grid_remove()
            self.subject_page.grid_remove()
            self.practice_page.load()
            self.practice_page.grid()
        elif name == "My Subjects":
            self.content.grid_remove()
            self.subject_page.grid()
            self.subject_page.render()
        else:
            self.subject_page.grid_remove()
            self.content.grid()
            self.refresh_data()
        self.scroll._parent_canvas.yview_moveto(0)
        self.update_sidebar_selection(name)

    def open_question_bank(self, subject_id):
        if self.question_bank.importer.saving or self.flashcard_page.importer.saving:
            return
        self.flashcard_page.importer.cancel()
        self.cancel_focus_discard()
        try:
            subject = self.store.subject(subject_id)
        except sqlite3.Error:
            if self.question_bank.subject_id != subject_id:
                self.show_notice(tr(self, 'Could not refresh the question bank. Your draft is kept; reopen Questions to retry.'))
                return
            # Reopen the retained editor; load_subject owns the read retry notice.
            subject = True
        if subject is None:
            self.navigate("My Subjects")
            self.show_notice(tr(self, 'This subject no longer exists.'))
            return
        self.subject_page.cancel_delete()
        self.content.grid_remove()
        self.subject_page.grid_remove()
        self.practice_page.grid_remove()
        self.flashcard_page.grid_remove()
        self.statistics_page.grid_remove()
        self.tutor_page.grid_remove()
        self.settings_page.grid_remove()
        self.question_bank.load_subject(subject_id)
        self.question_bank.grid()
        self.current_page = "Question Bank"
        self.update_sidebar_selection("My Subjects")
        self.scroll._parent_canvas.yview_moveto(0)

    def show_notice(self, text):
        self.notice.configure(text=tr(self,text), text_color=C["hover"])
        if hasattr(self, "subject_page"):
            self.subject_page.status.configure(text=tr(self,text))
        if hasattr(self, "question_bank"):
            self.question_bank.status.configure(text=tr(self,text))

    def save_task(self, key, value):
        try:
            self.store.set_task(key, value)
        except sqlite3.Error:
            self.task_vars[key].set(not value)
            self.show_notice(tr(self, 'Could not save the checklist. Please try again.'))
            return
        self.show_notice(tr(self, 'Checklist saved on this device.'))

    def filter_subjects(self):
        for _, card in self.subject_cards:
            card.destroy()
        self.subject_cards = []
        if self.add_subject_card is not None:
            self.add_subject_card.destroy()
            self.add_subject_card = None
        query = self.query.get().strip().casefold()
        subjects = self.store.subjects()
        visible = [s for s in subjects if query in s["name"].casefold()]
        self.empty.grid_remove()
        for i,subject in enumerate(visible):
            card=ctk.CTkFrame(self.subject_grid,fg_color=C['card'],corner_radius=18)
            card.grid_columnconfigure(1,weight=1)
            badge=ctk.CTkLabel(card,text=subject['name'][0].upper(),width=42,height=44,
                corner_radius=12,fg_color=C['selected'],text_color=C['hover'],font=self.font(21,True))
            badge.grid(row=0,column=0,rowspan=2,sticky='n',padx=(18,12),pady=(18,0))
            title=self.label(card,subject['name'],18,bold=True,wraplength=250)
            title.grid(row=0,column=1,sticky='ew',padx=(0,18),pady=(18,3))
            topics=tr(self,'{v0} topic' if subject['topic_count']==1 else '{v0} topics',v0=subject['topic_count'])
            questions=tr(self,'{v0} question' if subject['question_count']==1 else '{v0} questions',v0=subject['question_count'])
            meta=self.label(card,tr(self,'{v0} · {v1}',v0=topics,v1=questions),11,'secondary',wraplength=250)
            meta.grid(row=1,column=1,sticky='ew',padx=(0,18),pady=(0,12))
            card.bind('<Configure>',lambda event,labels=(title,meta):[label.configure(
                wraplength=max(120,self.scroll.logical_pixels(event.width)-100)) for label in labels],add='+')
            self.label(card,tr(self,'{v0} session · {v1} min' if subject['session_count']==1 else '{v0} sessions · {v1} min',
                v0=subject['session_count'],v1=subject['study_seconds']//60),12,'secondary').grid(row=2,column=0,columnspan=2,sticky='w',padx=18,pady=(3,14))
            actions=self.frame(card)
            actions.grid(row=3,column=0,columnspan=2,sticky='ew',padx=18,pady=(0,18))
            self.button(actions,tr(self,'Study'),lambda sid=subject['id']:self.start_focus(sid),primary=True,width=85).pack(side='left',padx=(0,8))
            self.button(actions,tr(self,'Questions'),lambda sid=subject['id']:self.open_question_bank(sid),width=95).pack(side='left')
            self.subject_cards.append((subject['name'],card))
        if visible and not query:
            # Outlined shortcut card, as in the brand concept; opens the real subject form.
            self.add_subject_card=ctk.CTkButton(self.subject_grid,text='+\n'+tr(self,'Add subject'),
                command=self.open_new_subject,height=150,corner_radius=18,font=self.font(14,True),
                fg_color='transparent',hover_color=C['selected'],text_color=C['hover'],
                border_width=2,border_color=C['outline'])
        self.layout_subject_cards()
        if not visible:
            self.empty.configure(text=tr(self,tr(self, 'No matching subjects. Try another name.') if subjects else tr(self, 'No subjects yet. Open My Subjects to create your first one.')))
            self.empty.grid(row=0, column=0, columnspan=2, sticky="w", pady=20)

    def refresh_data(self):
        subjects = self.store.subjects()
        self.dashboard_subjects = subjects
        self.subject_ids = {s["name"]: s["id"] for s in subjects}
        selected = next((s for s in subjects if s["id"] == self.selected_subject_id), None)
        selected = selected or (subjects[0] if subjects else None)
        self.selected_subject_id = selected["id"] if selected else None
        self.subject_picker.configure(values=list(self.subject_ids),
                                      state="disabled" if self.session_open or not subjects else "normal")
        self.subject_selection.set(selected["name"] if selected else "Add a subject first")
        self.start_button.configure(text=tr(self, 'Start Studying  →' if subjects else 'Create your first subject'))
        self.update_hero()
        self.update_metrics()
        self.filter_subjects()
        self.refresh_rail()
        if hasattr(self, "subject_page"):
            self.subject_page.render()

    def select_subject(self, name):
        self.selected_subject_id = self.subject_ids.get(name)
        self.update_hero()

    def update_hero(self):
        """Show which saved subject the banner's next focus session belongs to."""
        name = self.session_subject_name if self.session_open else next(
            (s["name"] for s in getattr(self, "dashboard_subjects", []) if s["id"] == self.selected_subject_id), None)
        self.hero_subject.configure(text=tr(self, '{v0} · {v1}', v0=name, v1=tr(self, 'Focus session'))
                                    if name else tr(self, 'Pick a subject to begin.'))

    def focus_search(self, _event=None):
        self.cancel_focus_reveal()
        if self.current_page in ("Practice Tests", "Flashcards", "Statistics", "AI Tutor", "Settings"):
            return "break"
        if self.current_page == "Question Bank":
            self.question_bank.search.focus_set()
        else:
            (self.subject_page.search if self.current_page == "My Subjects" else self.search).focus_set()
            if self.current_page=='Dashboard':
                self.scroll.reveal_if_outside(self.subject_header)
        return "break"

    def clear_search(self, _event=None):
        if self.pending_focus_discard:
            self.cancel_focus_discard()
            return "break"
        if self.current_page in ("Practice Tests", "Flashcards", "Statistics", "AI Tutor", "Settings"):
            return
        if self.current_page == "Question Bank":
            self.question_bank.query.set("")
        else:
            (self.subject_page.query if self.current_page == "My Subjects" else self.query).set("")

    def elapsed(self):
        return self.session_seconds + (time.monotonic() - self.running_since if self.running_since is not None else 0)

    def focus_error(self,exc):
        return tr(self,'Could not access saved focus. Retry the action or Refresh recovery.') if isinstance(exc,(sqlite3.Error,OSError)) else tr(self,str(exc))

    def start_focus(self, subject_id=None):
        if self.session_open:
            self.navigate("Dashboard")
            self.show_notice(tr(self, 'A focus session is already open. Use Pause, Resume or Finish.'))
            return
        subject_id = subject_id if subject_id is not None else self.selected_subject_id
        if subject_id is None:
            self.navigate("My Subjects")
            self.subject_page.show_form()
            self.show_notice(tr(self, 'Create a subject before starting your first focus session.'))
            return
        try:
            row=self.store.start_focus_checkpoint(subject_id,self.preferences['focus_minutes']*60)
        except (sqlite3.Error,ValueError,OSError) as exc:
            self.refresh_focus_recovery()
            self.show_notice(self.focus_error(exc))
            return
        self.activate_focus(row,recovered=False)
        if self.refresh_pending:return
        self.show_notice(tr(self, 'Focus session started · {v0}',v0=row['subject_name']))

    def activate_focus(self,row,*,recovered):
        self.focus_run_id=row['id']
        self.session_subject_id=row['subject_id'];self.session_subject_name=row['subject_name']
        if row['subject_id'] is not None:self.selected_subject_id=row['subject_id']
        self.focus_target=row['target_seconds'];self.session_seconds=float(row['elapsed_seconds'])
        self.running_since=None if recovered else time.monotonic()
        self.last_checkpoint=time.monotonic();self.session_open=True;self.session_save_failed=False
        self.recovery_record=None;self.pending_focus_discard=False;self.recovery_panel.grid_remove()
        self.focus_retry_label.configure(text='')
        self.focus_alert.grid_remove()
        self.focus_subject_label.configure(text=tr(self,'Focus subject: {v0}',v0=row['subject_name']))
        self.update_hero()
        remaining=max(0,self.focus_target-int(self.elapsed()))
        self.focus_clock.set(remaining,self.focus_target,tr(self,'Paused' if recovered else 'Focus'))
        self.pause_button.configure(text=tr(self,'Resume' if recovered else 'Pause'),state='normal')
        self.timer_frame.grid();self.start_button.configure(state='disabled');self.subject_picker.configure(state='disabled')
        try:self.navigate('Dashboard')
        except sqlite3.Error:self.defer_refresh()

    def cancel_focus_discard(self):
        self.pending_focus_discard=False
        self.discard_focus_button.configure(text=tr(self,'Discard checkpoint'))
        if self.recovery_record is not None:
            row=self.recovery_record
            self.recovery_status.configure(text=tr(self,'{v0} · saved {v1}s of {v2}s. Recover paused or discard. Time while closed is not counted; another window may still own this session.',v0=row['subject_name'],v1=row['elapsed_seconds'],v2=row['target_seconds']))

    def refresh_focus_recovery(self):
        if self.session_open:return
        self.cancel_focus_discard()
        self.recovery_record=None
        self.recover_focus_button.configure(state='disabled')
        self.discard_focus_button.configure(state='disabled')
        self.start_button.configure(state='disabled')
        try:row=self.store.pending_focus()
        except sqlite3.Error:
            self.recovery_status.configure(text=tr(self,'Could not read saved focus. Retry Refresh; no checkpoint was discarded.'))
            self.recovery_panel.grid();self.schedule_focus_reveal(self.recovery_panel);return
        self.recovery_record=row
        if row is None:
            self.recovery_panel.grid_remove();self.start_button.configure(state='normal');return
        self.recover_focus_button.configure(state='normal')
        self.discard_focus_button.configure(state='normal')
        self.cancel_focus_discard()
        self.recovery_panel.grid()
        self.schedule_focus_reveal(self.recovery_panel)

    def recover_focus(self):
        if self.session_open:return
        self.cancel_focus_discard()
        if self.recovery_record is None:self.refresh_focus_recovery();return
        try:row=self.store.claim_focus_checkpoint(self.recovery_record['id'],self.recovery_record['revision'])
        except (sqlite3.Error,ValueError,OSError) as exc:
            self.recovery_status.configure(text=self.focus_error(exc));return
        self.activate_focus(row,recovered=True)
        if self.refresh_pending:return
        self.show_notice(tr(self,'Focus recovered paused. Resume or Finish when ready; app downtime was not counted.'))

    def discard_focus(self):
        if self.session_open:return
        if self.recovery_record is None:self.refresh_focus_recovery();return
        if not self.pending_focus_discard:
            self.pending_focus_discard=True
            self.discard_focus_button.configure(text=tr(self,'Confirm discard'))
            self.recovery_status.configure(text=tr(self,'Discard this saved focus checkpoint? Its uncompleted time will not enter Statistics. Click Confirm discard, or Refresh to cancel.'))
            return
        try:self.store.discard_focus_checkpoint(self.recovery_record['id'],self.recovery_record['revision'])
        except (sqlite3.Error,ValueError,OSError) as exc:
            self.pending_focus_discard=False;self.discard_focus_button.configure(text=tr(self,'Discard checkpoint'))
            self.recovery_status.configure(text=self.focus_error(exc));return
        self.recovery_record=None;self.refresh_focus_recovery()
        self.show_notice(tr(self,'Focus checkpoint discarded. Completed study history is unchanged.'))

    def show_focus_retry(self):
        try:self.navigate('Dashboard')
        except sqlite3.Error:self.defer_refresh()
        self.show_notice(SAVE_RETRY_NOTICE)
        self.schedule_focus_reveal(self.timer_frame,idle=True)

    def cancel_focus_reveal(self):
        if self.focus_reveal_job is not None:
            self.after_cancel(self.focus_reveal_job)
            self.focus_reveal_job=None

    def schedule_focus_reveal(self,panel,*,idle=False):
        self.cancel_focus_reveal()
        def reveal():
            self.focus_reveal_job=None
            self.reveal_focus_controls(panel)
        self.focus_reveal_job=self.after_idle(reveal) if idle else self.after(160,reveal)

    def reveal_focus_controls(self,panel):
        if self.current_page=='Dashboard' and panel.winfo_ismapped():
            self.scroll.scroll_to_widget(panel)

    def focus_save_failure(self):
        self.pause_button.configure(state='disabled')
        self.focus_retry_label.configure(text=tr(self,SAVE_RETRY_NOTICE))
        self.focus_alert.configure(text='!' if self.collapsed else tr(self,'Focus needs saving'))
        self.focus_alert.grid(row=2,column=0,sticky='ew',padx=12,pady=(8,0))
        self.fit_sidebar_decor()
        self.show_notice(SAVE_RETRY_NOTICE)

    def checkpoint_focus(self):
        elapsed=min(int(self.elapsed()),self.focus_target)
        try:self.store.checkpoint_focus(self.focus_run_id,elapsed)
        except (sqlite3.Error,ValueError):
            self.session_seconds=self.elapsed();self.running_since=None;self.session_save_failed=True
            self.focus_save_failure()
            return False
        self.last_checkpoint=time.monotonic();return True

    def pause_focus(self):
        if self.running_since is not None:
            self.session_seconds=self.elapsed();self.running_since=None
            self.pause_button.configure(text=tr(self,'Resume'))
            self.checkpoint_focus()
        elif self.session_save_failed:
            self.show_notice(SAVE_RETRY_NOTICE)
        elif self.session_open:
            if int(self.session_seconds)>=self.focus_target:self.finish_focus();return
            self.running_since=time.monotonic();self.last_checkpoint=time.monotonic()
            self.pause_button.configure(text=tr(self,'Pause'))

    def finish_focus(self):
        if not self.session_open:
            return False
        elapsed = min(int(self.elapsed()), self.focus_target)
        try:
            result=self.store.add_session(elapsed, self.session_subject_id, self.session_subject_name,focus_run_id=self.focus_run_id)
            elapsed=result["seconds"]
        except (sqlite3.Error,ValueError):
            self.session_seconds = self.elapsed()
            self.running_since = None
            self.session_save_failed = True
            self.focus_save_failure()
            return False
        self.focus_run_id = None
        self.running_since = None
        self.session_seconds = 0.0
        self.session_open = False
        self.session_save_failed = False
        self.session_subject_id = None
        self.session_subject_name = None
        self.timer_frame.grid_remove()
        self.focus_clock.set(self.preferences['focus_minutes']*60,self.preferences['focus_minutes']*60,tr(self,'Focus session'))
        self.focus_alert.grid_remove()
        self.focus_retry_label.configure(text="")
        self.start_button.configure(state="normal")
        if elapsed:
            try:
                self.store.set_task("focus", True)
                self.task_vars["focus"].set(True)
            except sqlite3.Error:
                pass  # The session itself has already been committed successfully.
        self.show_notice(tr(self, 'Session saved · {v0}m {v1:02d}s of focused study.', v0=elapsed // 60, v1=elapsed % 60))
        try:
            self.refresh_data()
        except sqlite3.Error:
            self.defer_refresh()
        else:
            self.refresh_pending = False
        return True

    def defer_refresh(self):
        self.refresh_pending = True
        # A refresh retry must never obscure an unsaved session's required action.
        self.show_notice(SAVE_RETRY_NOTICE if self.session_save_failed else REFRESH_RETRY_NOTICE)

    def update_metrics(self):
        summary = self.store.summary()
        minutes = summary["seconds"] // 60
        values = [tr(self,'{v0}h {v1:02d}m',v0=minutes//60,v1=minutes%60), str(summary["sessions"]),
                  tr(self,'{v0} day' if summary['streak']==1 else '{v0} days',v0=summary['streak']), str(summary["subjects"])]
        for label, value in zip(self.metric_values, values):
            label.configure(text=value)
        self.saved_today_seconds = summary["today_seconds"]
        self.update_goal()

    def update_goal(self):
        goal = self.preferences["daily_goal_minutes"]
        self.goal.configure(text=tr(self, '{v0} / {v1} min', v0=self.saved_today_seconds // 60, v1=goal))
        self.goal_bar.set(min(self.saved_today_seconds / (goal * 60), 1))

    def validate_preferences_change(self, fields):
        tutor = self.tutor_page
        if any(fields[key] != self.preferences[key] for key in AI_KEYS) and tutor.task is not None:
            raise ValueError("Wait for or stop the Tutor request before changing AI preferences.")
        if any(fields[key] != self.preferences[key] for key in AI_KEYS) and generation_busy(self):
            raise ValueError("Wait for or stop AI generation before changing AI preferences.")
        if (fields["ollama_endpoint"] != self.preferences["ollama_endpoint"] and tutor.turns
                and fields["ollama_endpoint"] != (tutor.conversation_endpoint or tutor.connected_endpoint)):
            raise ValueError("Start a New chat in AI Tutor before saving a different server.")

    def apply_preferences(self, saved):
        previous = self.preferences
        self.preferences = dict(saved)
        if not self.session_open:
            self.focus_target = saved["focus_minutes"] * 60
            self.focus_clock.set(self.focus_target,self.focus_target,tr(self,'Focus session'))
        self.update_goal()
        self.tutor_page.apply_preferences(saved, previous)
        if saved["appearance_mode"] != previous["appearance_mode"]:
            apply_appearance(saved["appearance_mode"])

    def tick(self):
        try:
            if self.data_restoring:
                return
            if self.session_open:
                remaining = max(0, self.focus_target - int(self.elapsed()))
                self.focus_clock.set(remaining,self.focus_target,tr(self,'Paused' if self.running_since is None else 'Focus'))
                if remaining == 0 and self.running_since is not None:
                    self.finish_focus()
                elif self.running_since is not None and time.monotonic()-self.last_checkpoint>=5:
                    self.checkpoint_focus()
            today = date.today()
            day_changed = today != self.active_day
            if day_changed or self.refresh_pending:
                # Daily state changes only after successful reads. Post-save refresh
                # retries are independent of the date and never repeat the write.
                retrying = self.refresh_pending
                tasks = {key: self.store.task(key) for key in self.task_vars} if day_changed else {}
                self.refresh_data()
                for key, value in tasks.items():
                    self.task_vars[key].set(value)
                self.date_label.configure(text=self.display_date(today))
                self.active_day = today
                self.refresh_pending = False
                if retrying and not self.session_save_failed:
                    self.show_notice(tr(self, 'Dashboard refreshed.'))
        except sqlite3.Error:
            self.defer_refresh()
        finally:
            self.after(250, self.tick)

    def close(self):
        if self.settings_page.schedule.busy:
            self.backup_notice.configure(text=tr(self,'Daily backup is running. Please wait before closing.'))
            self.backup_notice.grid(row=1,column=0,columnspan=2,sticky='ew',padx=12,pady=6)
            return
        if self.question_bank.importer.saving or self.flashcard_page.importer.saving:
            (self.flashcard_page.importer if self.flashcard_page.importer.saving else self.question_bank.importer).status.configure(text=tr(self, 'Wait for the CSV import to finish before closing.'))
            return
        if self.settings_page.backups.busy:
            self.settings_page.backups.status.configure(text=tr(self, 'Wait for the database operation to finish before closing.'))
            return
        self.settings_page.backups.cancel_pending()
        if self.session_open and not self.finish_focus():
            self.show_focus_retry()
            return
        if not self.tutor_page.prepare_close():
            self.navigate("AI Tutor")
            return
        self.tutor_page.shutdown()
        # Cancel AI drafting without joining its worker on the Tk thread.
        shutdown_generators(self)
        self.store.close()
        self.destroy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SOSkúška native desktop Dashboard")
    parser.add_argument("--data", type=Path, help="Override the local SQLite database path")
    args = parser.parse_args()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    try:
        Dashboard(args.data).mainloop()
    except (sqlite3.Error, ValueError) as exc:
        report_startup_error(exc)
        raise SystemExit(1) from None
