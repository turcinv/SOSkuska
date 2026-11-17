"""Statistics screen for saved focus, test results and self-assessed reviews."""
import sqlite3

import customtkinter as ctk
from study_statistics import PERIODS, RATINGS, duration


class StatisticsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.app = app
        self.report = None
        self.grid_columnconfigure(0, weight=1)
        app.label(self, "Statistics", 28, bold=True).grid(row=0, column=0, sticky="w")
        self.status = app.label(self, "Saved activity only. Choose a period or refresh the report.", 13, "secondary", wraplength=600)
        self.status.grid(row=1, column=0, sticky="ew", pady=(6, 14))
        toolbar = app.frame(self)
        toolbar.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        toolbar.grid_columnconfigure(0, weight=1)
        self.period = ctk.StringVar(value="Last 7 days")
        self.period_picker = ctk.CTkOptionMenu(toolbar, variable=self.period, values=list(PERIODS),
                                              command=lambda _: self.load(), dynamic_resizing=False,
                                              font=app.font(), height=38)
        self.period_picker.grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.refresh_button = app.button(toolbar, "Refresh", self.load, width=95)
        self.refresh_button.grid(row=0, column=1)
        self.body = app.frame(self)
        self.body.grid(row=3, column=0, sticky="ew")
        self.body.grid_columnconfigure(0, weight=1)
        self.bind("<Configure>", self.resize, add="+")

    def resize(self, event):
        self.status.configure(wraplength=max(250, event.width - 12))

    def load(self):
        try:
            report = self.app.store.statistics(self.period.get())
        except (sqlite3.Error, ValueError):
            self.status.configure(text="Could not refresh statistics. Previous report, if any, is unchanged. Press Refresh to retry.")
            return
        # Replace the visible snapshot only after every query succeeds.
        self.report = report
        for child in self.body.winfo_children():
            child.destroy()
        start = report["start_day"] or "First saved activity"
        self.status.configure(text=f'{start} → {report["end_day"]} · Local calendar days · Refresh or reopen to update')
        self.render(report)
        if self.app.current_page == "Statistics":
            self.app.scroll.scroll_to_top()

    def card(self, title, row):
        card = self.app.frame(self.body, card=True)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)
        self.text(card, title, 0, 18, True)
        return card

    def text(self, parent, text, row, size=14, bold=False):
        label = self.app.label(parent, text, size, bold=bold, wraplength=600)
        label.grid(row=row, column=0, sticky="ew", padx=18, pady=(10, 10))
        parent.bind("<Configure>", lambda event: label.configure(wraplength=max(220, event.width - 36)), add="+")
        return label

    def render(self, report):
        focus = self.card("Saved focus time", 0)
        self.text(focus, duration(report["focus_seconds"]), 1, 26, True)
        self.text(focus, f'{report["sessions"]} sessions · {report["focus_days"]} days with saved focus', 2)
        self.text(focus, "Only saved timer sessions count. Running or unsaved time is excluded.", 3, 12)
        practice = self.card("Practice Tests", 1)
        accuracy = "No completed tests" if report["practice_accuracy"] is None else f'{report["practice_accuracy"]:.1f}% accuracy'
        self.text(practice, accuracy, 1, 26, True)
        self.text(practice, f'{report["practice_completed"]} completed tests · {report["practice_correct"]}/{report["practice_questions"]} correct · {report["practice_answered"]} answered', 2)
        self.text(practice, "Each question has equal weight. Unanswered questions count as incorrect. In-progress tests are excluded.", 3, 12)
        reviews = self.card("Flashcard reviews", 2)
        self.text(reviews, f'{report["reviews"]} saved ratings', 1, 26, True)
        self.text(reviews, " · ".join(f'{rating}: {report["rating_counts"][rating]}' for rating in RATINGS), 2)
        self.text(reviews, "Self-assessments, not measured accuracy or mastery. Repeated reviews count separately.", 3, 12)
        subjects = self.card("Focus by subject", 3)
        self.subject_bars = []
        if not report["focus_by_subject"]:
            self.text(subjects, "No saved focus sessions in this period.", 1)
        maximum = max((row["seconds"] for row in report["focus_by_subject"]), default=1)
        # Limit rendered rows, not totals. All rows remain in the report.
        for index, row in enumerate(report["focus_by_subject"][:50]):
            name = row["name"] or "Unassigned sessions"
            if row["subject_id"] is None and row["name"]:
                name += " (subject deleted / unavailable)"
            self.text(subjects, f'{name}\n{duration(row["seconds"])} · {row["sessions"]} sessions', index * 2 + 1)
            bar = ctk.CTkProgressBar(subjects, height=8, progress_color="#8B5CF6")
            bar.grid(row=index * 2 + 2, column=0, sticky="ew", padx=18, pady=(0, 12))
            bar.set(row["seconds"] / maximum)
            self.subject_bars.append(bar)
        if len(report["focus_by_subject"]) > 50:
            self.text(subjects, "Showing the 50 subjects with the most focus time. Totals include all subjects.", 102, 12)
        daily = self.card("Daily activity", 4)
        self.text(daily, f'Chart: {report["chart_start_day"]} → {report["end_day"]}. Bars compare saved focus time; counts show completed tests and reviews.', 1, 12)
        self.daily_bars = []
        maximum = max((row["seconds"] for row in report["daily"]), default=0) or 1
        for index, row in enumerate(reversed(report["daily"])):
            self.text(daily, f'{row["day"]} · {duration(row["seconds"])} · {row["practice"]} tests · {row["reviews"]} reviews', index * 2 + 2, 13)
            bar = ctk.CTkProgressBar(daily, height=8, progress_color="#8B5CF6")
            bar.grid(row=index * 2 + 3, column=0, sticky="ew", padx=18, pady=(0, 12))
            bar.set(row["seconds"] / maximum)
            self.daily_bars.append(bar)
        footer = self.app.frame(self.body)
        footer.grid(row=5, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        self.text(footer, "Saved history survives source edits/deletions. Focus uses its saved date; tests use completion time and reviews use rating time in the system time zone. No study time is inferred from tests or flashcards.", 0, 12)
