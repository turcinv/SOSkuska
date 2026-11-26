"""Flashcard authoring and saved self-assessment reviews."""
from theme import COLORS as C
from localization_widgets import LocalizedOptionMenu
from localization import tr, duration_text
import sqlite3
from datetime import datetime
from functools import wraps

import customtkinter as ctk
from study_time import display_time
from practice import utc_now
from repetition import RATINGS, next_review
from csv_import_panel import CsvImportPanel
from ai_generation_panel import NoteGenerationPanel
from panel_layout import wrap_labels


def safe(method):
    @wraps(method)
    def call(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (ValueError, sqlite3.Error) as exc:
            message = tr(self.app,str(exc)) if isinstance(exc,ValueError) else tr(self.app,'Could not access flashcard data. Please retry.')
            if self.review_refresh_pending:
                message += ' ' + tr(self.app,'Review saved. Refresh card to continue; do not rate it again.')
            if self.deck_refresh_pending is not None:
                message += ' ' + tr(self.app, 'Deck saved. Refresh deck to load saved content; do not save it again.')
            self.status.configure(text=message)
            form_notice = getattr(self, 'deck_form_notice', None)
            if self.view == 'deck_form' and form_notice is not None and form_notice.winfo_exists():
                form_notice.configure(text=message)
            notice = getattr(self,'review_notice',None)
            if self.view == 'review' and notice is not None and notice.winfo_exists():
                notice.configure(text=message)
                notice.grid()
    return call


class FlashcardPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.app = app
        self.view = "decks"
        self.deck_id = None
        self.deck_snapshot = None
        self.editing_deck = None
        self.editing_deck_snapshot = None
        self.deck_refresh_pending = None
        self.editing_card = None
        self.editing_revision = None
        self.pending_delete = None
        self.queue = []
        self.current_card = None
        self.revealed = False
        self.review_refresh_pending = False
        self.rated = {rating: 0 for rating in RATINGS}
        self.review_deck_name = ""
        self.query = ctk.StringVar()
        self.grid_columnconfigure(0, weight=1)
        app.label(self, tr(self.app, 'Flashcards'), 28, bold=True).grid(row=0, column=0, sticky="w")
        self.status = app.label(self, tr(self.app, 'Create cards, reveal the answer, then rate how well you recalled it.'), 13, "secondary", wraplength=650)
        self.status.grid(row=1, column=0, sticky="ew", pady=(6, 14))
        toolbar = app.frame(self)
        toolbar.grid(row=2, column=0, sticky="w", pady=(0, 18))
        app.button(toolbar, tr(self.app, 'All decks'), self.show_decks, width=110).pack(side="left", padx=(0, 8))
        app.button(toolbar, tr(self.app, 'Review history'), self.show_history, width=140).pack(side="left", padx=(0, 8))
        app.button(toolbar, tr(self.app, 'Refresh'), self.refresh, width=90).pack(side="left")
        self.importer = CsvImportPanel(self, app, self, cards=True)
        self.importer.grid(row=3, column=0, sticky="ew", pady=(0,18));self.importer.grid_remove()
        self._generator = None  # Built on first use to keep startup light.
        self.body = app.frame(self)
        self.body.grid(row=5, column=0, sticky="ew")
        self.body.grid_columnconfigure(0, weight=1)

    @property
    def generator(self):
        if self._generator is None:
            self._generator = NoteGenerationPanel(self, self.app, self, cards=True)
            self._generator.grid(row=4, column=0, sticky="ew", pady=(0,18));self._generator.grid_remove()
        return self._generator

    def open_generator(self):
        self.generator.open()

    def clear(self, view, *, preserve_import=False):
        if self.importer.saving:
            raise ValueError("Wait for the flashcard import to finish.")
        if not preserve_import:
            self.importer.cancel()
        # AI drafts belong to one deck: keep them (and a running request) only
        # while that same deck stays open, e.g. across search or refresh.
        if self._generator is not None and not (view == "deck" and self._generator.target_id == self.deck_id):
            self._generator.close(notify=True)
        if view != "deck":
            self.deck_snapshot = None
        for child in self.body.winfo_children():
            child.destroy()
        self.view = view
        if view != 'deck_form':
            self.deck_refresh_pending = None
        self.pending_delete = None
        if view != "review":
            self.review_refresh_pending = False
            self.current_card = None
            self.revealed = False
        if self.app.current_page == "Flashcards":
            self.app.scroll.scroll_to_top()

    def label(self, parent, text, row, size=14, bold=False):
        label = self.app.label(parent, text, size, bold=bold, wraplength=600, justify='left')
        label.grid(row=row, column=0, sticky="ew", padx=18, pady=(12, 10))
        parent.bind("<Configure>", lambda event, label=label: label.configure(wraplength=max(200, self.app.scroll.logical_pixels(event.width)-36)), add="+")
        return label

    @staticmethod
    def local_time(value):
        return display_time(value)

    def subject_text(self, deck):
        return deck["current_subject_name"] or tr(self.app,'{v0} (subject deleted)',v0=deck['subject_name'])

    @safe
    def load(self):
        if self.deck_refresh_pending is not None:
            self.retry_deck_refresh()
            return
        if self.view in ("deck_form", "card_form"):
            if self.view == "deck_form" and self.editing_deck is None:
                self.refresh_deck_subjects()
            return  # Navigation does not discard an unfinished authoring draft.
        if self.view == "review" and self.queue:
            self.show_review()
        elif self.view == "deck" and self.deck_id is not None:
            self.show_deck(self.deck_id)
        elif self.view == "history":
            self.show_history()
        else:
            self.show_decks()

    @safe
    def refresh(self):
        if self.deck_refresh_pending is not None:
            self.retry_deck_refresh()
            return
        if self.view == "deck_form" and self.editing_deck is None:
            self.refresh_deck_subjects()
            self.status.configure(text=tr(self.app, 'Subject list refreshed. Your draft is kept.'))
        elif self.view in ("deck_form", "card_form"):
            self.status.configure(text=tr(self.app, 'Save or cancel the current draft before refreshing.'))
        else:
            self.load()

    @safe
    def show_decks(self):
        decks = self.app.store.decks()
        self.clear("decks")
        self.queue = []
        self.current_card = None
        self.new_deck_button = self.app.button(self.body, tr(self.app, '+ New deck'), self.deck_form, primary=True, width=140)
        self.new_deck_button.grid(row=0, column=0, sticky="w", pady=(0, 16))
        if not decks:
            empty = self.app.frame(self.body, card=True)
            empty.grid(row=1,column=0,sticky='ew')
            empty.grid_columnconfigure(0,weight=1)
            self.label(empty,tr(self.app,'No decks yet. Create a subject in My Subjects, then add your first deck.'),0)
        for row, deck in enumerate(decks, 1):
            card = self.app.frame(self.body, card=True)
            card.grid(row=row, column=0, sticky="ew", pady=(0, 14))
            card.grid_columnconfigure(0, weight=1)
            self.label(card, deck["name"], 0, 18, True)
            self.label(card, tr(self.app, '{v0} · {v1} cards · {v2} due', v0=self.subject_text(deck), v1=deck['card_count'], v2=deck['due_count']), 1)
            actions = self.app.frame(card)
            actions.grid(row=2, column=0, sticky="w", padx=18, pady=(0, 16))
            self.app.button(actions, tr(self.app, 'Open deck'), lambda did=deck["id"]: self.open_deck(did), width=120).pack(side="left", padx=(0, 8))
            button = self.app.button(actions, tr(self.app, 'Study due'), lambda did=deck["id"]: self.start_review(did), primary=True, width=120)
            button.pack(side="left")
            button.configure(state="normal" if deck["due_count"] else "disabled")

    def open_deck(self, deck_id):
        self.query.set("")
        self.show_deck(deck_id)

    @safe
    def show_deck(self, deck_id):
        self._show_deck(deck_id)

    def refresh_csv_totals(self):
        self._show_deck(self.deck_id, preserve_import=True)

    def _show_deck(self, deck_id, *, preserve_import=False):
        search_draft = self.search.get() if preserve_import and self.view == "deck" else self.query.get()
        deck = self.app.store.deck(deck_id)
        if deck is None:
            if not preserve_import:
                self.show_decks()
            raise ValueError("This deck no longer exists.")
        cards = self.app.store.flashcards(deck_id, self.query.get())
        due = self.app.store.due_flashcards(deck_id)
        self.deck_id = deck_id
        self.clear("deck", preserve_import=preserve_import)
        self.deck_snapshot = dict(deck)
        if self._generator is not None:
            self._generator.sync_target()
        self.queue = []
        self.current_card = None
        head = self.app.frame(self.body, card=True)
        head.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        head.grid_columnconfigure(0, weight=1)
        self.label(head, deck["name"], 0, 22, True)
        self.label(head, self.subject_text(deck), 1)
        if deck["description"]:
            self.label(head, deck["description"], 2)
        actions = self.app.frame(self.body)
        actions.grid(row=1, column=0, sticky="w", pady=(0, 16))
        self.new_card_button = self.app.button(actions, tr(self.app, '+ New card'), self.card_form,
                                                primary=not due, width=125)
        self.new_card_button.grid(row=0, column=0, padx=(0, 8), pady=(0, 8), sticky="w")
        self.study_button = self.app.button(actions, tr(self.app, 'Study due ({v0})', v0=len(due)),
            lambda: self.start_review(deck_id), primary=bool(due), width=155)
        self.study_button.grid(row=0, column=1, padx=(0, 8), pady=(0, 8), sticky="w")
        self.study_button.configure(state="normal" if due else "disabled")
        self.csv_button = self.app.button(actions, tr(self.app, 'Import CSV'), self.importer.open, width=110)
        self.csv_button.grid(row=0, column=2, pady=(0, 8), sticky="w")
        self.app.button(actions, tr(self.app, 'Edit deck'), lambda: self.deck_form(deck_id), width=100).grid(
            row=1, column=0, padx=(0, 8), sticky="w")
        self.app.button(actions, tr(self.app, 'Delete deck'), lambda: self.ask_delete("deck", deck_id), width=115).grid(
            row=1, column=1, padx=(0, 8), sticky="w")
        self.generate_button = self.app.button(actions, tr(self.app, 'Generate with AI'), self.open_generator, width=150)
        self.generate_button.grid(row=1, column=2, sticky="w")
        search = self.app.frame(self.body)
        search.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        search.grid_columnconfigure(0, weight=1)
        self.search = ctk.CTkEntry(search, height=38, placeholder_text=tr(self.app, 'Search front or back…'), font=self.app.font(), placeholder_text_color=C["secondary"])
        self.app.label(search, tr(self.app, 'Search front or back…'), 11, 'secondary').grid(row=0, column=0, sticky='w', pady=(0,4))
        self.search.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        self.search.insert(0, search_draft)
        self.app.button(search, tr(self.app, 'Search'), self.search_cards, width=90).grid(row=1, column=1)
        self.app.label(self.body, tr(self.app, '{v0} matching cards · showing up to 100. Narrow the search for more.', v0=len(cards)), 13, "secondary", wraplength=650).grid(row=3, column=0, sticky="ew", pady=(0, 12))
        if not cards:
            empty = self.app.frame(self.body, card=True)
            empty.grid(row=4,column=0,sticky='ew')
            empty.grid_columnconfigure(0,weight=1)
            self.label(empty,tr(self.app,'No matching cards. Add a card or change the search.'),0)
        for row, item in enumerate(cards[:100], 4):
            card = self.app.frame(self.body, card=True)
            card.grid(row=row, column=0, sticky="ew", pady=(0, 14))
            card.grid_columnconfigure(0, weight=1)
            self.label(card, item["front"][:240] + ("…" if len(item["front"]) > 240 else ""), 0, 16, True)
            self.label(card, item["back"][:240] + ("…" if len(item["back"]) > 240 else ""), 1)
            self.label(card, tr(self.app, 'Due {v0} · {v1} saved reviews', v0=self.local_time(item['due_at']), v1=item['review_count']), 2)
            actions = self.app.frame(card)
            actions.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 14))
            self.app.button(actions, tr(self.app, 'Edit'), lambda cid=item["id"]: self.card_form(cid), width=85).pack(side="left", padx=(0, 8))
            self.app.button(actions, tr(self.app, 'Delete'), lambda cid=item["id"]: self.ask_delete("card", cid), width=85).pack(side="left")

    def search_cards(self):
        # Keep the query outside the recreated CTkEntry: its textvariable trace
        # would otherwise outlive a destroyed entry in CustomTkinter 5.2.2.
        self.query.set(self.search.get())
        self.show_deck(self.deck_id)

    @safe
    def deck_form(self, deck_id=None):
        deck = self.app.store.deck(deck_id) if deck_id is not None else None
        if deck_id is not None and deck is None:
            raise ValueError("This deck no longer exists.")
        subjects = self.app.store.subjects()
        self.subject_ids = {f'Subject: {s["name"]}': s["id"] for s in subjects}
        self.editing_deck = deck_id
        self.editing_deck_snapshot = deck
        self.clear("deck_form")
        self.deck_refresh_pending = None
        self.app.label(self.body, tr(self.app, 'Edit deck') if deck else tr(self.app, 'New deck'), 22, bold=True).grid(row=0, column=0, sticky="w", pady=(0, 16))
        self.app.label(self.body, tr(self.app, 'Name (1–120 characters; unique across decks)'), 13, "secondary").grid(row=1, column=0, sticky="w")
        self.name_entry = ctk.CTkEntry(self.body, height=38, font=self.app.font(), placeholder_text_color=C["secondary"])
        self.name_entry.grid(row=2, column=0, sticky="ew", pady=(4, 14))
        self.name_entry.insert(0, deck["name"] if deck else "")
        self.subject_choice_id = next(iter(self.subject_ids.values()), None)
        self.subject_requires_choice = False
        self.subject = ctk.StringVar(value=next(iter(self.subject_ids), "Add a subject first"))
        if not deck:
            self.app.label(self.body, tr(self.app, 'Subject'), 13, "secondary").grid(row=3, column=0, sticky="w")
            self.subject_menu = LocalizedOptionMenu(self.body,owner=self.app,translate_values=True, variable=self.subject, values=list(self.subject_ids) or ["Add a subject first"], command=self.select_deck_subject, dynamic_resizing=False, height=38)
            self.subject_menu.grid(row=4, column=0, sticky="ew", pady=(4, 14))
        self.app.label(self.body, tr(self.app, 'Description (optional, up to 1,000 characters)'), 13, "secondary").grid(row=5, column=0, sticky="w")
        self.description = ctk.CTkTextbox(self.body, height=90, font=self.app.font(), wrap="word")
        self.description.grid(row=6, column=0, sticky="ew", pady=(4, 14))
        self.description.insert("1.0", deck["description"] if deck else "")
        footer = self.app.frame(self.body)
        footer.grid(row=7, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        actions = self.app.frame(footer)
        actions.grid(row=0, column=0, sticky="w")
        self.save_button = self.app.button(actions, tr(self.app, 'Save deck'), self.save_deck, primary=True, width=125)
        self.save_button.pack(side="left", padx=(0, 8))
        self.app.button(actions, tr(self.app, 'Cancel'), self.show_decks, width=85).pack(side="left")
        self.deck_form_notice = self.app.label(footer, "", 13, wraplength=500)
        self.deck_form_notice.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        wrap_labels(footer, self.app, inset=0)

    def select_deck_subject(self, label):
        self.subject_choice_id = self.subject_ids.get(label)
        self.subject_requires_choice = self.subject_choice_id is None
        self.subject.set(label)

    def refresh_deck_subjects(self):
        """Refresh choices without deriving identity from display/sentinel text."""
        subjects = self.app.store.subjects()  # Read first; failure keeps draft intact.
        subject_ids = {f'Subject: {item["name"]}': item["id"] for item in subjects}
        selected_id = self.subject_choice_id
        if selected_id is not None and selected_id not in subject_ids.values():
            # Keep this requirement across an empty list and later creations.
            self.subject_requires_choice = True
            selected_id = None
        if not subject_ids:
            selected = "Add a subject first"
        elif self.subject_requires_choice:
            selected = "Choose a subject"
        else:
            if selected_id is None:
                selected_id = next(iter(subject_ids.values()))
            selected = next(label for label, sid in subject_ids.items() if sid == selected_id)
        self.subject_menu.configure(values=list(subject_ids) or ["Add a subject first"])
        self.subject_ids = subject_ids
        self.subject_choice_id = selected_id
        self.subject.set(selected)

    def retry_deck_refresh(self):
        if self.deck_refresh_pending is not None:
            self.status.configure(text=tr(self.app, 'Deck saved on this device.'))
            self.show_deck(self.deck_refresh_pending)

    @safe
    def save_deck(self):
        if self.deck_refresh_pending is not None:
            self.retry_deck_refresh()
            return
        values = (self.name_entry.get(), self.description.get("1.0", "end-1c"))
        if self.editing_deck is None:
            self.refresh_deck_subjects()
            self.editing_deck = self.app.store.create_deck(self.subject_choice_id, *values)
        else:
            self.app.store.update_deck(self.editing_deck, *values, expected_state=self.editing_deck_snapshot)
        self.deck_refresh_pending = self.editing_deck
        self.save_button.configure(text=tr(self.app, 'Refresh deck'))
        self.name_entry.configure(state='disabled')
        self.description.configure(state='disabled')
        if self.editing_deck_snapshot is None:
            self.subject_menu.configure(state='disabled')
        self.status.configure(text=tr(self.app, 'Deck saved on this device.'))
        self.show_deck(self.editing_deck)

    @safe
    def card_form(self, card_id=None):
        card = self.app.store.flashcard(card_id) if card_id is not None else None
        if card_id is not None and (card is None or card["deck_id"] != self.deck_id):
            raise ValueError("This card no longer exists in this deck.")
        self.editing_card = card_id
        self.editing_revision = card["revision"] if card else None
        self.clear("card_form")
        self.app.label(self.body, tr(self.app, 'Edit card') if card else tr(self.app, 'New card'), 22, bold=True).grid(row=0, column=0, sticky="w", pady=(0, 14))
        self.app.label(self.body, tr(self.app, 'Front (1–2,000 characters)'), 13, "secondary").grid(row=1, column=0, sticky="w")
        self.front_entry = ctk.CTkTextbox(self.body, height=120, font=self.app.font(), wrap="word")
        self.front_entry.grid(row=2, column=0, sticky="ew", pady=(4, 14))
        self.front_entry.insert("1.0", card["front"] if card else "")
        self.app.label(self.body, tr(self.app, 'Back (1–4,000 characters)'), 13, "secondary").grid(row=3, column=0, sticky="w")
        self.back_entry = ctk.CTkTextbox(self.body, height=150, font=self.app.font(), wrap="word")
        self.back_entry.grid(row=4, column=0, sticky="ew", pady=(4, 14))
        self.back_entry.insert("1.0", card["back"] if card else "")
        self.app.label(self.body, tr(self.app, "Editing restarts this card's schedule. Past review records are kept."), 13, "secondary", wraplength=650).grid(row=5, column=0, sticky="ew", pady=(0, 14))
        actions = self.app.frame(self.body)
        actions.grid(row=6, column=0, sticky="w")
        self.save_button = self.app.button(actions, tr(self.app, 'Save card'), self.save_card, primary=True, width=125)
        self.save_button.pack(side="left", padx=(0, 8))
        self.app.button(actions, tr(self.app, 'Cancel'), lambda: self.show_deck(self.deck_id), width=85).pack(side="left")

    @safe
    def save_card(self):
        front, back = self.front_entry.get("1.0", "end-1c"), self.back_entry.get("1.0", "end-1c")
        if self.editing_card is None:
            self.editing_card = self.app.store.create_flashcard(self.deck_id, front, back)
            self.editing_revision = 0
        else:
            self.app.store.update_flashcard(self.editing_card, front, back, self.editing_revision)
            self.editing_revision += 1
        self.status.configure(text=tr(self.app, 'Card saved on this device.'))
        self.show_deck(self.deck_id)

    @safe
    def ask_delete(self, kind, record_id):
        if kind == "deck":
            state = self.app.store.deck_deletion_state(record_id)
            if state is None:
                raise ValueError("This deck no longer exists.")
            text = f'Delete “{state[0]}” and its {state[1]} cards? Review history will be kept.'
        else:
            card = self.app.store.flashcard(record_id)
            if card is None or card["deck_id"] != self.deck_id:
                raise ValueError("This card no longer exists in this deck.")
            state = card["revision"]
            text = f'Delete this card permanently? {card["front"][:160]} · Review history will be kept.'
        self.clear("confirm")
        self.pending_delete = (kind, record_id, state)
        self.app.label(self.body, tr(self.app,text), 16, wraplength=650).grid(row=0, column=0, sticky="ew", pady=(0, 18))
        actions = self.app.frame(self.body)
        actions.grid(row=1, column=0, sticky="w")
        self.confirm_button = self.app.button(actions, tr(self.app, 'Confirm deletion'), self.confirm_delete, width=160)
        self.confirm_button.pack(side="left", padx=(0, 8))
        self.app.button(actions, tr(self.app, 'Cancel'), lambda: self.show_deck(self.deck_id) if self.deck_id is not None else self.show_decks(), width=85).pack(side="left")

    @safe
    def confirm_delete(self):
        if self.pending_delete is None:
            return
        kind, record_id, state = self.pending_delete
        deleted = self.app.store.delete_deck(record_id, state) if kind == "deck" else self.app.store.delete_flashcard(record_id, state)
        if not deleted:
            self.ask_delete(kind, record_id)
            self.status.configure(text=tr(self.app, 'The content changed. Review the updated warning before deleting.'))
            return
        self.pending_delete = None
        self.status.configure(text=tr(self.app, 'Deleted. Saved review history was kept.'))
        if kind == "deck":
            self.deck_id = None
            self.show_decks()
        else:
            self.show_deck(self.deck_id)

    @safe
    def start_review(self, deck_id):
        deck = self.app.store.deck(deck_id)
        if deck is None:
            raise ValueError("This deck no longer exists.")
        cards = self.app.store.due_flashcards(deck_id)
        self.deck_id = deck_id
        self.review_deck_name = deck["name"]
        self.queue = [card["id"] for card in cards]
        self.rated = {rating: 0 for rating in RATINGS}
        self.show_review()

    @safe
    def show_review(self):
        card = None
        while self.queue:
            candidate = self.app.store.flashcard(self.queue[0])
            if candidate and candidate["deck_id"] == self.deck_id and datetime.fromisoformat(candidate["due_at"]) <= utc_now():
                card = candidate
                break
            self.queue.pop(0)
        self.clear("review")
        self.review_refresh_pending = False
        self.current_card = card
        self.revealed = False
        header = self.app.frame(self.body, card=True)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)
        self.label(header, self.review_deck_name, 0, 22, True)
        if card is None:
            done = sum(self.rated.values())
            self.label(header, tr(self.app, 'No more due cards in this batch. {v0} reviews saved.', v0=done), 1, 18)
            self.label(header, " · ".join(f"{tr(self.app,key)}: {value}" for key, value in self.rated.items()), 2, 13)
            self.app.button(header, tr(self.app, 'Back to deck'), lambda: self.show_deck(self.deck_id), primary=True, width=150).grid(
                row=3, column=0, sticky="w", padx=18, pady=(0,16))
            return
        self.label(header, tr(self.app, '{v0} cards left · {v1} reviews saved this batch',
                             v0=len(self.queue), v1=sum(self.rated.values())), 1, 13)
        panel = self.app.frame(self.body, card=True)
        panel.grid(row=1, column=0, sticky="ew", pady=(0,16))
        panel.grid_columnconfigure(0, weight=1)
        self.app.label(panel, tr(self.app, 'Prompt'), 12, 'secondary').grid(
            row=0, column=0, sticky='w', padx=18, pady=(16,0))
        self.front_label = self.label(panel, card["front"], 1, 22, True)
        self.front_label.grid(pady=(8,22))
        self.answer_panel = self.app.frame(panel, card=True)
        self.answer_panel.configure(fg_color=C['raised'], border_width=0)
        self.answer_panel.grid(row=2,column=0,sticky='ew',padx=18,pady=(0,18))
        self.answer_panel.grid_columnconfigure(0,weight=1)
        self.app.label(self.answer_panel,tr(self.app,'Answer'),12,'secondary').grid(
            row=0,column=0,sticky='w',padx=18,pady=(12,0))
        self.answer = self.label(self.answer_panel, "", 1, 17)
        self.answer_panel.grid_remove()
        self.review_footer = self.app.frame(self.body)
        self.review_footer.grid(row=2,column=0,sticky='ew',pady=(0,16))
        self.review_footer.grid_columnconfigure(0,weight=1)
        self.reveal_button = self.app.button(self.review_footer, tr(self.app, 'Reveal answer'),
                                              self.reveal, primary=True, width=165)
        self.reveal_button.grid(row=0,column=0,sticky='w')
        self.rating_actions = self.app.frame(self.review_footer)
        self.rating_actions.grid(row=0,column=0,sticky='ew')
        self.app.label(self.rating_actions,tr(self.app,'Rate your recall'),13,'secondary').grid(
            row=0,column=0,columnspan=4,sticky='w',pady=(0,8))
        self.rating_buttons = {}
        for rating in RATINGS:
            _due, _interval, label = next_review(card["interval_days"], rating, utc_now())
            button = self.app.button(self.rating_actions, tr(self.app, '{v0} · {v1}',
                v0=tr(self.app,rating), v1=duration_text(self.app,label)),
                lambda r=rating, cid=card["id"], rev=card["revision"]: self.rate(r, cid, rev), width=138)
            button.configure(state="disabled")
            self.rating_buttons[rating] = button
        self.rating_actions.bind('<Configure>', self.layout_ratings, add='+')
        self.layout_ratings()
        self.rating_actions.grid_remove()
        self.review_notice = self.app.label(self.review_footer,'',12,'hover',wraplength=650,justify='left')
        self.review_notice.grid(row=1,column=0,sticky='ew',pady=(8,0))
        self.review_notice.grid_remove()
        self.review_footer.bind('<Configure>',lambda event:self.review_notice.configure(
            wraplength=max(200,self.app.scroll.logical_pixels(event.width))),add='+')
        self.app.button(self.body, tr(self.app, 'Refresh card'), self.show_review, width=140).grid(
            row=3,column=0,sticky='w')
        self.status.configure(text=tr(self.app, 'Ratings are self-assessments, not test scores. Unrated cards remain due after closing.'))

    def layout_ratings(self, event=None):
        width = (self.app.scroll.logical_pixels(event.width) if event is not None
                 else self.app.scroll.viewport_width() - 56)
        columns = 4 if width >= 850 else 2
        for index in range(4):
            self.rating_actions.grid_columnconfigure(index,weight=1 if index < columns else 0,
                                                      uniform='rating' if index < columns else '')
        for index, rating in enumerate(RATINGS):
            self.rating_buttons[rating].grid(row=1+index//columns,column=index%columns,sticky='ew',
                padx=(0 if index%columns == 0 else 4, 0 if index%columns == columns-1 else 4),
                pady=(0,8))

    def reveal(self):
        if self.app.current_page != "Flashcards" or self.view != "review" or self.current_card is None:
            return
        self.revealed = True
        self.answer.configure(text=self.current_card["back"])
        self.answer_panel.grid()
        self.reveal_button.configure(state="disabled")
        self.reveal_button.grid_remove()
        self.rating_actions.grid()
        for button in self.rating_buttons.values():
            button.configure(state="normal")

    @safe
    def rate(self, rating, card_id, revision):
        if self.app.current_page != "Flashcards" or self.view != "review" or not self.revealed or self.current_card is None or (self.current_card["id"], self.current_card["revision"]) != (card_id, revision):
            return
        try:
            self.app.store.rate_flashcard(card_id, rating, revision)
        except ValueError as exc:
            self.current_card = None
            self.revealed = False
            self.show_review()
            self.status.configure(text=tr(self.app, str(exc)))
            return
        self.queue.pop(0)
        self.rated[rating] += 1
        self.current_card = None
        self.revealed = False
        self.review_refresh_pending = True
        for button in self.rating_buttons.values():
            button.configure(state='disabled')
        self.show_review()

    @safe
    def show_history(self):
        history = self.app.store.flashcard_history()
        self.clear("history")
        self.app.label(self.body, tr(self.app, 'Review history · latest 20'), 22, bold=True).grid(row=0, column=0, sticky="w", pady=(0, 16))
        if not history:
            self.app.label(self.body, tr(self.app, 'No saved reviews yet.'), 14, "secondary").grid(row=1, column=0, sticky="w")
        for row, event in enumerate(history, 1):
            card = self.app.frame(self.body, card=True)
            card.grid(row=row, column=0, sticky="ew", pady=(0, 14))
            card.grid_columnconfigure(0, weight=1)
            for index, text in enumerate([f'{event["deck_name"]} · {event["subject_name"]}',
                    tr(self.app,'{v0} · {v1} · {v2}',v0=tr(self.app,event['rating']),v1=self.local_time(event['reviewed_at']),v2=self.local_time(event['due_at'])), event["front"], event["back"]]):
                self.label(card, text, index, 14, index == 0)
