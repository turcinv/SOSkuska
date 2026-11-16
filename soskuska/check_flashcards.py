"""Native flashcard workflow; uses disposable data and a fresh-process reopen."""
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


def run_check(path, reopen=False):
    app = Dashboard(path)
    page = app.flashcard_page
    errors = []

    def guarded(callback):
        def run():
            try:
                callback()
            except Exception as exc:
                errors.append(str(exc))
                traceback.print_exc()
                app.destroy()
        return run

    def later(callback):
        app.after(250, guarded(callback))

    def initial():
        app.geometry("1024x700")
        app.navigate("Flashcards")
        assert app.store.decks() == []
        app.store.create_subject("Математика")
        app.refresh_data()
        page.new_deck_button.invoke()
        page.save_button.invoke()
        assert page.view == "deck_form" and app.store.decks() == []
        page.name_entry.insert(0, "Algebra – skúška")
        page.description.insert("1.0", "Definitions and recall")
        page.save_button.invoke()
        did = app.store.decks()[0]["id"]
        assert page.view == "deck"
        page.new_card_button.invoke()
        page.save_button.invoke()
        assert page.view == "card_form" and app.store.flashcards(did) == []
        page.front_entry.insert("1.0", "Что такое производная?")
        page.back_entry.insert("1.0", "Предел отношения приращений.")
        # Navigating away preserves an unfinished authoring draft.
        app.navigate("Dashboard")
        app.navigate("Flashcards")
        assert page.front_entry.get("1.0", "end-1c") == "Что такое производная?"
        page.save_button.invoke()
        page.new_card_button.invoke()
        page.front_entry.insert("1.0", "Second card?")
        page.back_entry.insert("1.0", "Second answer.")
        page.save_button.invoke()
        page.deck_form(did)
        page.name_entry.delete(0, "end")
        page.name_entry.insert(0, "Algebra – edited")
        page.save_button.invoke()
        cid = app.store.flashcards(did)[0]["id"]
        page.card_form(cid)
        page.front_entry.insert("end", " Updated.")
        page.save_button.invoke()
        page.search.insert(0, "ВТОРОЙ НЕТ")
        page.search_cards()
        assert "No matching cards" in " ".join(texts(page.body))
        page.search.delete(0, "end")
        page.search_cards()
        page.study_button.invoke()
        assert page.current_card["id"] == app.store.due_flashcards(did)[0]["id"]
        assert not page.revealed
        assert all(b.cget("state") == "disabled" for b in page.rating_buttons.values())
        page.rate("Good", cid, page.current_card["revision"])
        assert app.store.flashcard_history() == []
        page.reveal_button.invoke()
        assert page.answer.cget("text") == page.current_card["back"]
        later(rating)

    def texts(widget):
        result = []
        for child in widget.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                result.append(child.cget("text"))
            result.extend(texts(child))
        return result

    def rating():
        assert page.answer.winfo_ismapped()
        stale = dict(page.current_card)
        other = Store(path)
        try:
            other.update_flashcard(stale["id"], stale["front"] + " Changed elsewhere.", stale["back"], stale["revision"])
        finally:
            other.close()
        page.rating_buttons["Good"].invoke()
        assert not page.revealed and app.store.flashcard_history() == []
        page.reveal_button.invoke()
        app.update_idletasks()
        right = app.winfo_rootx() + app.winfo_width()
        assert all(button.winfo_rootx() + button.winfo_width() <= right for button in page.rating_buttons.values())
        first = dict(page.current_card)
        with patch.object(app.store, "rate_flashcard", side_effect=sqlite3.OperationalError("disk full")):
            page.rating_buttons["Good"].invoke()
        assert page.revealed and page.current_card["id"] == first["id"]
        assert app.store.flashcard_history() == []
        page.rating_buttons["Good"].invoke()
        assert len(app.store.flashcard_history()) == 1
        page.rate("Good", first["id"], first["revision"])
        assert len(app.store.flashcard_history()) == 1  # Stale button cannot rate the next card.
        app.navigate("Dashboard")
        app.navigate("Flashcards")
        assert page.view == "review" and not page.revealed
        page.reveal_button.invoke()
        page.rating_buttons["Again"].invoke()
        assert page.current_card is None
        assert len(app.store.flashcard_history()) == 2
        did = app.store.decks()[0]["id"]
        page.show_deck(did)
        assert page.study_button.cget("state") == "disabled"
        assert app.store.decks()[0]["due_count"] == 0
        sid = app.store.deck(did)["subject_id"]
        app.store.delete_subject(sid)
        app.refresh_data()
        page.show_deck(did)
        assert "subject deleted" in " ".join(texts(page.body))
        page.show_history()
        assert "Предел отношения приращений." in " ".join(texts(page.body))
        page.show_deck(did)
        page.ask_delete("card", first["id"])
        page.show_deck(did)  # Cancel.
        assert app.store.flashcard(first["id"])
        page.ask_delete("card", first["id"])
        page.confirm_button.invoke()
        assert app.store.flashcard(first["id"]) is None
        assert len(app.store.flashcard_history()) == 2
        page.ask_delete("deck", did)
        app.store.create_flashcard(did, "Fresh front", "Fresh back")
        page.confirm_button.invoke()
        assert app.store.deck(did) and page.pending_delete
        assert "changed" in page.status.cget("text")
        page.show_deck(did)
        app.close()

    def resumed():
        app.geometry("1024x700")
        app.navigate("Flashcards")
        deck = app.store.decks()[0]
        assert deck["subject_id"] is None and deck["due_count"] == 1
        assert len(app.store.flashcard_history()) == 2
        page.open_deck(deck["id"])
        page.study_button.invoke()
        assert page.current_card["front"] == "Fresh front"
        page.reveal_button.invoke()
        assert page.answer.cget("text") == "Fresh back"
        page.rating_buttons["Good"].invoke()
        assert len(app.store.flashcard_history()) == 3
        page.show_deck(deck["id"])
        page.ask_delete("deck", deck["id"])
        page.confirm_button.invoke()
        assert app.store.decks() == []
        history = app.store.flashcard_history()
        assert len(history) == 3 and all(e["deck_id"] is None and e["card_id"] is None for e in history)
        page.show_history()
        assert "Fresh back" in " ".join(texts(page.body))
        assert app.store.seconds() == 0
        app.close()

    def callback_error(kind, value, tb):
        errors.append(str(value))
        traceback.print_exception(kind, value, tb)
        app.destroy()

    def timeout():
        errors.append("Flashcard UI check timed out")
        app.destroy()

    app.report_callback_exception = callback_error
    app.after(900, guarded(resumed if reopen else initial))
    app.after(15000, timeout)
    try:
        app.mainloop()
    finally:
        app.store.close()
    assert not errors, errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reopen", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    ctk.set_appearance_mode("dark")
    if args.reopen:
        run_check(args.reopen, reopen=True)
    else:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "flashcards.sqlite3"
            run_check(path)
            reopened = Store(path)
            try:
                assert reopened.decks()[0]["due_count"] == 1
                assert len(reopened.flashcard_history()) == 2
            finally:
                reopened.close()
            subprocess.run([sys.executable, "-u", str(Path(__file__).resolve()), "--reopen", str(path)], check=True, timeout=25)
            print("PASS: deck/card CRUD, validation, draft navigation, reveal/rating guard, write failure/retry, scheduling, retained review snapshots, deletion reconfirmation, compact layout and fresh-process reopen", flush=True)
