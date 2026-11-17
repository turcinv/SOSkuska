"""Flashcard authoring and saved self-assessment reviews."""
import sqlite3
from datetime import datetime
from functools import wraps

import customtkinter as ctk
from practice import utc_now
from repetition import RATINGS, next_review


def safe(method):
    @wraps(method)
    def call(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (ValueError, sqlite3.Error) as exc:
            self.status.configure(text=str(exc) if isinstance(exc, ValueError) else "Could not access flashcard data. Please retry.")
    return call


class FlashcardPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent", corner_radius=0)
        self.app = app
        self.view = "decks"
        self.deck_id = None
        self.editing_deck = None
        self.editing_card = None
        self.editing_revision = None
        self.pending_delete = None
        self.queue = []
        self.current_card = None
        self.revealed = False
        self.rated = {rating: 0 for rating in RATINGS}
        self.review_deck_name = ""
        self.query = ctk.StringVar()
        self.grid_columnconfigure(0, weight=1)
        app.label(self, "Flashcards", 28, bold=True).grid(row=0, column=0, sticky="w")
        self.status = app.label(self, "Create cards, reveal the answer, then rate how well you recalled it.", 13, "secondary", wraplength=650)
        self.status.grid(row=1, column=0, sticky="ew", pady=(6, 14))
        toolbar = app.frame(self)
        toolbar.grid(row=2, column=0, sticky="w", pady=(0, 18))
        app.button(toolbar, "All decks", self.show_decks, width=110).pack(side="left", padx=(0, 8))
        app.button(toolbar, "Review history", self.show_history, width=140).pack(side="left", padx=(0, 8))
        app.button(toolbar, "Refresh", self.refresh, width=90).pack(side="left")
        self.body = app.frame(self)
        self.body.grid(row=3, column=0, sticky="ew")
        self.body.grid_columnconfigure(0, weight=1)

    def clear(self, view):
        for child in self.body.winfo_children():
            child.destroy()
        self.view = view
        self.pending_delete = None
        if view != "review":
            self.current_card = None
            self.revealed = False
        if self.app.current_page == "Flashcards":
            self.app.scroll.scroll_to_top()

    def label(self, parent, text, row, size=14, bold=False):
        label = self.app.label(parent, text, size, bold=bold, wraplength=600)
        label.grid(row=row, column=0, sticky="ew", padx=18, pady=(12, 10))
        parent.bind("<Configure>", lambda event, label=label: label.configure(wraplength=max(250, event.width-36)), add="+")
        return label

    @staticmethod
    def local_time(value):
        return datetime.fromisoformat(value).astimezone().strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def subject_text(deck):
        return deck["current_subject_name"] or f'{deck["subject_name"]} (subject deleted)'

    @safe
    def load(self):
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
        if self.view == "deck_form" and self.editing_deck is None:
            self.refresh_deck_subjects()
            self.status.configure(text="Subject list refreshed. Your draft is kept.")
        elif self.view in ("deck_form", "card_form"):
            self.status.configure(text="Save or cancel the current draft before refreshing.")
        else:
            self.load()

    @safe
    def show_decks(self):
        decks = self.app.store.decks()
        self.clear("decks")
        self.queue = []
        self.current_card = None
        self.new_deck_button = self.app.button(self.body, "+ New deck", self.deck_form, primary=True, width=140)
        self.new_deck_button.grid(row=0, column=0, sticky="w", pady=(0, 16))
        if not decks:
            self.app.label(self.body, "No decks yet. Create a subject in My Subjects, then add your first deck.", 14, "secondary", wraplength=650).grid(row=1, column=0, sticky="ew")
        for row, deck in enumerate(decks, 1):
            card = self.app.frame(self.body, card=True)
            card.grid(row=row, column=0, sticky="ew", pady=(0, 14))
            card.grid_columnconfigure(0, weight=1)
            self.label(card, deck["name"], 0, 18, True)
            self.label(card, f'{self.subject_text(deck)} · {deck["card_count"]} cards · {deck["due_count"]} due', 1)
            actions = self.app.frame(card)
            actions.grid(row=2, column=0, sticky="w", padx=18, pady=(0, 16))
            self.app.button(actions, "Open deck", lambda did=deck["id"]: self.open_deck(did), width=120).pack(side="left", padx=(0, 8))
            button = self.app.button(actions, "Study due", lambda did=deck["id"]: self.start_review(did), primary=True, width=120)
            button.pack(side="left")
            button.configure(state="normal" if deck["due_count"] else "disabled")

    def open_deck(self, deck_id):
        self.query.set("")
        self.show_deck(deck_id)

    @safe
    def show_deck(self, deck_id):
        deck = self.app.store.deck(deck_id)
        if deck is None:
            self.show_decks()
            raise ValueError("This deck no longer exists.")
        cards = self.app.store.flashcards(deck_id, self.query.get())
        due = self.app.store.due_flashcards(deck_id)
        self.deck_id = deck_id
        self.clear("deck")
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
        self.new_card_button = self.app.button(actions, "+ New card", self.card_form, primary=True, width=125)
        self.new_card_button.pack(side="left", padx=(0, 8))
        self.study_button = self.app.button(actions, f"Study due ({len(due)})", lambda: self.start_review(deck_id), width=155)
        self.study_button.pack(side="left", padx=(0, 8))
        self.study_button.configure(state="normal" if due else "disabled")
        self.app.button(actions, "Edit deck", lambda: self.deck_form(deck_id), width=100).pack(side="left", padx=(0, 8))
        self.app.button(actions, "Delete deck", lambda: self.ask_delete("deck", deck_id), width=115).pack(side="left")
        search = self.app.frame(self.body)
        search.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        search.grid_columnconfigure(0, weight=1)
        self.search = ctk.CTkEntry(search, height=38, placeholder_text="Search front or back…", font=self.app.font())
        self.search.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.search.insert(0, self.query.get())
        self.app.button(search, "Search", self.search_cards, width=90).grid(row=0, column=1)
        self.app.label(self.body, f"{len(cards)} matching cards · showing up to 100. Narrow the search for more.", 13, "secondary", wraplength=650).grid(row=3, column=0, sticky="ew", pady=(0, 12))
        if not cards:
            self.app.label(self.body, "No matching cards. Add a card or change the search.", 14, "secondary").grid(row=4, column=0, sticky="w")
        for row, item in enumerate(cards[:100], 4):
            card = self.app.frame(self.body, card=True)
            card.grid(row=row, column=0, sticky="ew", pady=(0, 14))
            card.grid_columnconfigure(0, weight=1)
            self.label(card, item["front"][:240] + ("…" if len(item["front"]) > 240 else ""), 0, 16, True)
            self.label(card, item["back"][:240] + ("…" if len(item["back"]) > 240 else ""), 1)
            self.label(card, f'Due {self.local_time(item["due_at"])} · {item["review_count"]} saved reviews', 2)
            actions = self.app.frame(card)
            actions.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 14))
            self.app.button(actions, "Edit", lambda cid=item["id"]: self.card_form(cid), width=85).pack(side="left", padx=(0, 8))
            self.app.button(actions, "Delete", lambda cid=item["id"]: self.ask_delete("card", cid), width=85).pack(side="left")

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
        self.subject_ids = {s["name"]: s["id"] for s in subjects}
        self.editing_deck = deck_id
        self.clear("deck_form")
        self.app.label(self.body, "Edit deck" if deck else "New deck", 22, bold=True).grid(row=0, column=0, sticky="w", pady=(0, 16))
        self.app.label(self.body, "Name (1–120 characters; unique across decks)", 13, "secondary").grid(row=1, column=0, sticky="w")
        self.name_entry = ctk.CTkEntry(self.body, height=38, font=self.app.font())
        self.name_entry.grid(row=2, column=0, sticky="ew", pady=(4, 14))
        self.name_entry.insert(0, deck["name"] if deck else "")
        self.subject = ctk.StringVar(value=next(iter(self.subject_ids), "Add a subject first"))
        if not deck:
            self.app.label(self.body, "Subject", 13, "secondary").grid(row=3, column=0, sticky="w")
            self.subject_menu = ctk.CTkOptionMenu(self.body, variable=self.subject, values=list(self.subject_ids) or ["Add a subject first"], dynamic_resizing=False, height=38)
            self.subject_menu.grid(row=4, column=0, sticky="ew", pady=(4, 14))
        self.app.label(self.body, "Description (optional, up to 1,000 characters)", 13, "secondary").grid(row=5, column=0, sticky="w")
        self.description = ctk.CTkTextbox(self.body, height=90, font=self.app.font(), wrap="word")
        self.description.grid(row=6, column=0, sticky="ew", pady=(4, 14))
        self.description.insert("1.0", deck["description"] if deck else "")
        actions = self.app.frame(self.body)
        actions.grid(row=7, column=0, sticky="w")
        self.save_button = self.app.button(actions, "Save deck", self.save_deck, primary=True, width=125)
        self.save_button.pack(side="left", padx=(0, 8))
        self.app.button(actions, "Cancel", self.show_decks, width=85).pack(side="left")

    def refresh_deck_subjects(self):
        """Refresh choices in place without replacing name/description widgets."""
        selected_name = self.subject.get()
        selected_id = self.subject_ids.get(selected_name)
        subjects = self.app.store.subjects()  # Read first; failure keeps draft intact.
        subject_ids = {item["name"]: item["id"] for item in subjects}
        if not subject_ids:
            selected = "Add a subject first"
        elif selected_id is not None:
            selected = next((name for name, sid in subject_ids.items() if sid == selected_id), "Choose a subject")
        elif selected_name == "Add a subject first":
            selected = next(iter(subject_ids))
        else:
            selected = "Choose a subject"
        self.subject_menu.configure(values=list(subject_ids) or ["Add a subject first"])
        self.subject_ids = subject_ids
        self.subject.set(selected)

    @safe
    def save_deck(self):
        values = (self.name_entry.get(), self.description.get("1.0", "end-1c"))
        if self.editing_deck is None:
            self.refresh_deck_subjects()
            self.editing_deck = self.app.store.create_deck(self.subject_ids.get(self.subject.get()), *values)
        else:
            self.app.store.update_deck(self.editing_deck, *values)
        self.status.configure(text="Deck saved on this device.")
        self.show_deck(self.editing_deck)

    @safe
    def card_form(self, card_id=None):
        card = self.app.store.flashcard(card_id) if card_id is not None else None
        if card_id is not None and (card is None or card["deck_id"] != self.deck_id):
            raise ValueError("This card no longer exists in this deck.")
        self.editing_card = card_id
        self.editing_revision = card["revision"] if card else None
        self.clear("card_form")
        self.app.label(self.body, "Edit card" if card else "New card", 22, bold=True).grid(row=0, column=0, sticky="w", pady=(0, 14))
        self.app.label(self.body, "Front (1–2,000 characters)", 13, "secondary").grid(row=1, column=0, sticky="w")
        self.front_entry = ctk.CTkTextbox(self.body, height=120, font=self.app.font(), wrap="word")
        self.front_entry.grid(row=2, column=0, sticky="ew", pady=(4, 14))
        self.front_entry.insert("1.0", card["front"] if card else "")
        self.app.label(self.body, "Back (1–4,000 characters)", 13, "secondary").grid(row=3, column=0, sticky="w")
        self.back_entry = ctk.CTkTextbox(self.body, height=150, font=self.app.font(), wrap="word")
        self.back_entry.grid(row=4, column=0, sticky="ew", pady=(4, 14))
        self.back_entry.insert("1.0", card["back"] if card else "")
        self.app.label(self.body, "Editing restarts this card's schedule. Past review records are kept.", 13, "secondary", wraplength=650).grid(row=5, column=0, sticky="ew", pady=(0, 14))
        actions = self.app.frame(self.body)
        actions.grid(row=6, column=0, sticky="w")
        self.save_button = self.app.button(actions, "Save card", self.save_card, primary=True, width=125)
        self.save_button.pack(side="left", padx=(0, 8))
        self.app.button(actions, "Cancel", lambda: self.show_deck(self.deck_id), width=85).pack(side="left")

    @safe
    def save_card(self):
        front, back = self.front_entry.get("1.0", "end-1c"), self.back_entry.get("1.0", "end-1c")
        if self.editing_card is None:
            self.editing_card = self.app.store.create_flashcard(self.deck_id, front, back)
            self.editing_revision = 0
        else:
            self.app.store.update_flashcard(self.editing_card, front, back, self.editing_revision)
            self.editing_revision += 1
        self.status.configure(text="Card saved on this device.")
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
        self.app.label(self.body, text, 16, wraplength=650).grid(row=0, column=0, sticky="ew", pady=(0, 18))
        actions = self.app.frame(self.body)
        actions.grid(row=1, column=0, sticky="w")
        self.confirm_button = self.app.button(actions, "Confirm deletion", self.confirm_delete, width=160)
        self.confirm_button.pack(side="left", padx=(0, 8))
        self.app.button(actions, "Cancel", lambda: self.show_deck(self.deck_id) if self.deck_id is not None else self.show_decks(), width=85).pack(side="left")

    @safe
    def confirm_delete(self):
        if self.pending_delete is None:
            return
        kind, record_id, state = self.pending_delete
        deleted = self.app.store.delete_deck(record_id, state) if kind == "deck" else self.app.store.delete_flashcard(record_id, state)
        if not deleted:
            self.ask_delete(kind, record_id)
            self.status.configure(text="The content changed. Review the updated warning before deleting.")
            return
        self.pending_delete = None
        self.status.configure(text="Deleted. Saved review history was kept.")
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
            if candidate and candidate["deck_id"] == self.deck_id and candidate["due_at"] <= utc_now().isoformat():
                card = candidate
                break
            self.queue.pop(0)
        self.clear("review")
        self.current_card = card
        self.revealed = False
        self.app.label(self.body, self.review_deck_name, 22, bold=True, wraplength=650).grid(row=0, column=0, sticky="ew", pady=(0, 14))
        if card is None:
            done = sum(self.rated.values())
            self.app.label(self.body, f"No more due cards in this batch. {done} reviews saved.", 18, wraplength=650).grid(row=1, column=0, sticky="ew", pady=(0, 12))
            self.app.label(self.body, " · ".join(f"{key}: {value}" for key, value in self.rated.items()), 13, "secondary", wraplength=650).grid(row=2, column=0, sticky="ew", pady=(0, 16))
            self.app.button(self.body, "Back to deck", lambda: self.show_deck(self.deck_id), width=150).grid(row=3, column=0, sticky="w")
            return
        self.app.label(self.body, f'{len(self.queue)} cards left · {sum(self.rated.values())} reviews saved this batch', 13, "secondary", wraplength=650).grid(row=1, column=0, sticky="ew", pady=(0, 16))
        panel = self.app.frame(self.body, card=True)
        panel.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        panel.grid_columnconfigure(0, weight=1)
        self.label(panel, card["front"], 0, 21, True)
        self.answer = self.label(panel, "", 1, 17)
        self.answer.grid_remove()
        self.reveal_button = self.app.button(self.body, "Reveal answer", self.reveal, primary=True, width=165)
        self.reveal_button.grid(row=3, column=0, sticky="w", pady=(0, 16))
        actions = self.app.frame(self.body)
        actions.grid(row=4, column=0, sticky="w", pady=(0, 16))
        self.rating_buttons = {}
        for rating in RATINGS:
            _due, _interval, label = next_review(card["interval_days"], rating, utc_now())
            button = self.app.button(actions, f"{rating} · {label}", lambda r=rating, cid=card["id"], rev=card["revision"]: self.rate(r, cid, rev), width=138)
            button.pack(side="left", padx=(0, 6))
            button.configure(state="disabled")
            self.rating_buttons[rating] = button
        self.app.button(self.body, "Refresh card", self.show_review, width=140).grid(row=5, column=0, sticky="w")
        self.status.configure(text="Ratings are self-assessments, not test scores. Unrated cards remain due after closing.")

    def reveal(self):
        if self.app.current_page != "Flashcards" or self.view != "review" or self.current_card is None:
            return
        self.revealed = True
        self.answer.configure(text=self.current_card["back"])
        self.answer.grid()
        self.reveal_button.configure(state="disabled")
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
            self.status.configure(text=str(exc))
            return
        self.queue.pop(0)
        self.rated[rating] += 1
        self.current_card = None
        self.revealed = False
        self.show_review()

    @safe
    def show_history(self):
        history = self.app.store.flashcard_history()
        self.clear("history")
        self.app.label(self.body, "Review history · latest 20", 22, bold=True).grid(row=0, column=0, sticky="w", pady=(0, 16))
        if not history:
            self.app.label(self.body, "No saved reviews yet.", 14, "secondary").grid(row=1, column=0, sticky="w")
        for row, event in enumerate(history, 1):
            card = self.app.frame(self.body, card=True)
            card.grid(row=row, column=0, sticky="ew", pady=(0, 14))
            card.grid_columnconfigure(0, weight=1)
            for index, text in enumerate([f'{event["deck_name"]} · {event["subject_name"]}',
                    f'{event["rating"]} · {self.local_time(event["reviewed_at"])} · next {self.local_time(event["due_at"])}', event["front"], event["back"]]):
                self.label(card, text, index, 14, index == 0)
