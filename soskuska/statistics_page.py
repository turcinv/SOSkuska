"""Statistics screen for saved focus, test results and self-assessed reviews."""
from theme import COLORS as C
from localization_widgets import LocalizedOptionMenu
from localization import tr, duration_text
import sqlite3

import customtkinter as ctk
from study_statistics import PERIODS, RATINGS, duration


class StatisticsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.app = app
        self.report = None
        self.summary_cards = []
        self.summary_columns = None
        self.grid_columnconfigure(0, weight=1)
        header = app.frame(self, card=True)
        header.grid(row=0,column=0,sticky="ew",pady=(0,18))
        header.grid_columnconfigure(0,weight=1)
        app.label(header,tr(app,'Statistics'),28,bold=True).grid(row=0,column=0,sticky="w",padx=18,pady=(16,6))
        self.status=app.label(header,tr(app,'Saved activity only. Choose a period or refresh the report.'),13,'secondary',wraplength=600,justify='left')
        self.status.grid(row=1,column=0,sticky='ew',padx=18,pady=(0,12))
        toolbar=app.frame(header)
        toolbar.grid(row=2,column=0,sticky='ew',padx=18,pady=(0,16))
        toolbar.grid_columnconfigure(0,weight=1)
        self.period=ctk.StringVar(value='Last 7 days')
        self.period_picker=LocalizedOptionMenu(toolbar,owner=app,variable=self.period,values=list(PERIODS),
            command=lambda _:self.load(),dynamic_resizing=False,font=app.font(),height=38,width=190)
        self.period_picker.grid(row=0,column=0,sticky='w',padx=(0,12))
        self.refresh_button=app.button(toolbar,tr(app,'Refresh'),self.load,width=95)
        self.refresh_button.grid(row=0,column=1)
        def wrap_status(event):
            width=max(220,app.scroll.logical_pixels(event.width)-36)
            if self.status.cget('wraplength')!=width:
                self.status.configure(wraplength=width)
        header.bind('<Configure>',wrap_status,add='+')
        self.body = app.frame(self)
        self.body.grid(row=3, column=0, sticky="ew")
        self.body.grid_columnconfigure(0, weight=1)
        self.bind("<Configure>", self.resize, add="+")

    def resize(self, event):
        self.layout_summary()

    def load(self):
        try:
            report = self.app.store.statistics(self.period.get())
        except (sqlite3.Error, ValueError):
            self.status.configure(text=tr(self.app, 'Could not refresh statistics. Previous report, if any, is unchanged. Press Refresh to retry.'))
            return
        # Replace the visible snapshot only after every query succeeds.
        self.report = report
        self.summary_cards = []
        self.summary_columns = None
        for child in self.body.winfo_children():
            child.destroy()
        start = report["start_day"] or tr(self.app,"First saved activity")
        self.status.configure(text=tr(self.app, '{v0} → {v1} · Local calendar days · Refresh or reopen to update', v0=start, v1=report['end_day']))
        self.render(report)
        if self.app.current_page == "Statistics":
            self.app.scroll.scroll_to_top()

    def card(self, title, row, parent=None):
        card = self.app.frame(parent or self.body, card=True)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)
        self.text(card, title, 0, 18, True)
        return card

    def text(self, parent, text, row, size=14, bold=False):
        label = self.app.label(parent, text, size, bold=bold, wraplength=600, justify="left")
        label.grid(row=row, column=0, sticky="ew", padx=18, pady=(10, 10))
        def resize(event):
            if parent.master is getattr(self,"summary",None):
                available=self.app.scroll.logical_pixels(self.summary.winfo_width())
                columns=3 if available>=950 else 1
                # Common parent width avoids one-pixel uniform-grid/wrap oscillation.
                width=max(160,int(available/columns)-(12 if columns==3 else 0)-40)
            else:
                width=max(160,self.app.scroll.logical_pixels(event.width)-36)
            if label.cget("wraplength")!=width:
                label.configure(wraplength=width)
        parent.bind("<Configure>",resize,add="+")
        return label

    def layout_summary(self, event=None):
        if not self.summary_cards:
            return
        columns=3 if self.app.scroll.logical_pixels(self.summary.winfo_width())>=950 else 1
        if columns==self.summary_columns:
            return
        self.summary_columns=columns
        for col in range(3):
            self.summary.grid_columnconfigure(col,weight=1 if col<columns else 0,uniform='metrics' if col<columns else '')
        for index,card in enumerate(self.summary_cards):
            card.grid(row=index//columns,column=index%columns,sticky='nsew',padx=(0,12) if columns==3 and index<2 else 0,pady=(0,16))

    def render(self, report):
        self.summary=self.app.frame(self.body)
        self.summary.grid(row=0,column=0,sticky='ew')
        self.summary.bind('<Configure>',self.layout_summary,add='+')
        focus = self.card(tr(self.app, 'Saved focus time'), 0, self.summary)
        self.text(focus, duration_text(self.app,duration(report["focus_seconds"])), 1, 26, True)
        self.text(focus, tr(self.app, '{v0} sessions · {v1} days with saved focus', v0=report['sessions'], v1=report['focus_days']), 2)
        self.text(focus, tr(self.app, 'Only saved timer sessions count. Running or unsaved time is excluded.'), 3, 12)
        practice = self.card(tr(self.app, 'Practice Tests'), 1, self.summary)
        accuracy = tr(self.app,"No completed tests") if report["practice_accuracy"] is None else tr(self.app,'{v0:.1f}% accuracy',v0=report['practice_accuracy'])
        self.text(practice, accuracy, 1, 26, True)
        self.text(practice, tr(self.app, '{v0} completed tests · {v1}/{v2} correct · {v3} answered', v0=report['practice_completed'], v1=report['practice_correct'], v2=report['practice_questions'], v3=report['practice_answered']), 2)
        self.text(practice, tr(self.app, 'Each question has equal weight. Unanswered questions count as incorrect. In-progress tests are excluded.'), 3, 12)
        reviews = self.card(tr(self.app, 'Flashcard reviews'), 2, self.summary)
        self.text(reviews, tr(self.app, '{v0} saved ratings', v0=report['reviews']), 1, 26, True)
        self.text(reviews, " · ".join(f'{tr(self.app,rating)}: {report["rating_counts"][rating]}' for rating in RATINGS), 2)
        self.text(reviews, tr(self.app, 'Self-assessments, not measured accuracy or mastery. Repeated reviews count separately.'), 3, 12)
        self.summary_cards=[focus,practice,reviews]
        self.layout_summary()
        subjects = self.card(tr(self.app, 'Focus by subject'), 1)
        self.subject_bars = []
        if not report["focus_by_subject"]:
            self.text(subjects, tr(self.app, 'No saved focus sessions in this period.'), 1)
        maximum = max((row["seconds"] for row in report["focus_by_subject"]), default=1)
        # Limit rendered rows, not totals. All rows remain in the report.
        for index, row in enumerate(report["focus_by_subject"][:50]):
            name = row["name"] or tr(self.app,"Unassigned sessions")
            if row["subject_id"] is None and row["name"]:
                name += tr(self.app," (subject deleted / unavailable)")
            self.text(subjects, tr(self.app, '{v0}\n{v1} · {v2} sessions', v0=name, v1=duration(row['seconds']), v2=row['sessions']), index * 2 + 1)
            bar = ctk.CTkProgressBar(subjects, height=8, fg_color=C["raised"], progress_color=C["accent"])
            bar.grid(row=index * 2 + 2, column=0, sticky="ew", padx=18, pady=(0, 12))
            bar.set(row["seconds"] / maximum)
            self.subject_bars.append(bar)
        if len(report["focus_by_subject"]) > 50:
            self.text(subjects, tr(self.app, 'Showing the 50 subjects with the most focus time. Totals include all subjects.'), 102, 12)
        daily = self.card(tr(self.app, 'Daily activity'), 2)
        self.text(daily, tr(self.app, 'Chart: {v0} → {v1}. Bars compare saved focus time; counts show completed tests and reviews.', v0=report['chart_start_day'], v1=report['end_day']), 1, 12)
        self.daily_bars = []
        maximum = max((row["seconds"] for row in report["daily"]), default=0) or 1
        for index, row in enumerate(reversed(report["daily"])):
            self.text(daily, tr(self.app, '{v0} · {v1} · {v2} tests · {v3} reviews', v0=row['day'], v1=duration(row['seconds']), v2=row['practice'], v3=row['reviews']), index * 2 + 2, 13)
            bar = ctk.CTkProgressBar(daily, height=8, fg_color=C["raised"], progress_color=C["accent"])
            bar.grid(row=index * 2 + 3, column=0, sticky="ew", padx=18, pady=(0, 12))
            bar.set(row["seconds"] / maximum)
            self.daily_bars.append(bar)
        footer = self.app.frame(self.body)
        footer.grid(row=3, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        self.text(footer, tr(self.app, 'Saved history survives source edits/deletions. Focus uses its saved date; tests use completion time and reviews use rating time in the system time zone. No study time is inferred from tests or flashcards.'), 0, 12)
