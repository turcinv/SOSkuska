"""Flashcard persistence, transactional scheduling and retained history."""
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "soskuska"))
from repetition import card_fields, deck_fields, next_review
from storage import SCHEMA_VERSION, Store

NOW = datetime(2026, 11, 16, 12, tzinfo=timezone.utc)


class FlashcardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "cards.sqlite3"
        self.store = Store(self.path)
        self.addCleanup(self.store.close)
        self.sid = self.store.create_subject("Математика")
        self.did = self.store.create_deck(self.sid, "Algebra", "Definitions")

    def add_card(self, front="Что такое производная?", back="Limit of a difference quotient."):
        with patch("storage.utc_now", return_value=NOW):
            return self.store.create_flashcard(self.did, front, back)

    def test_empty_new_database_contains_no_flashcard_demo(self):
        other = Store(Path(self.temp.name) / "empty.sqlite3")
        try:
            self.assertEqual(other.decks(), [])
            self.assertEqual(other.flashcard_history(), [])
        finally:
            other.close()

    def test_unicode_fields_and_due_counts_survive_reopening(self):
        cid = self.add_card("  Otázka\nпо-русски  ", "  Odpověď\nОтвет  ")
        reopened = Store(self.path)
        try:
            with patch("storage.utc_now", return_value=NOW):
                self.assertEqual(reopened.decks()[0]["due_count"], 1)
            self.assertEqual(reopened.flashcard(cid)["front"], "Otázka\nпо-русски")
            self.assertEqual(reopened.flashcard(cid)["back"], "Odpověď\nОтвет")
            self.assertEqual(len(reopened.flashcards(self.did, "ОТВЕТ")), 1)
        finally:
            reopened.close()

    def test_deck_names_are_global_unicode_unique(self):
        self.store.create_deck(self.sid, "Café")
        with self.assertRaises(ValueError):
            self.store.create_deck(self.sid, "Cafe\u0301")
        with self.assertRaises(ValueError):
            self.store.update_deck(self.did, "CAFÉ")
        self.assertEqual(self.store.deck(self.did)["name"], "Algebra")
        self.store.update_deck(self.did, "  New   deck  ", "New description")
        self.assertEqual(self.store.deck(self.did)["name"], "New deck")

    def test_invalid_fields_and_missing_subject_do_not_insert(self):
        for name in ["", " ", "x" * 121]:
            with self.assertRaises(ValueError):
                self.store.create_deck(self.sid, name)
        with self.assertRaises(ValueError):
            self.store.create_deck(self.sid, "Other", "x" * 1001)
        with self.assertRaises(ValueError):
            self.store.create_deck(99999, "Other")
        for front, back in [("", "a"), ("a", ""), ("x" * 2001, "a"), ("a", "x" * 4001)]:
            with self.assertRaises(ValueError):
                self.store.create_flashcard(self.did, front, back)
        with self.assertRaises(ValueError):
            self.store.create_flashcard(99999, "a", "b")
        self.assertEqual(self.store.flashcards(self.did), [])
        deck_fields("Valid", "Description")
        card_fields("Front", "Back")

    def test_schedule_rules_and_cap(self):
        for rating, delta, interval in [("Again", timedelta(minutes=10), 0), ("Hard", timedelta(hours=1), 0),
                                       ("Good", timedelta(days=1), 1), ("Easy", timedelta(days=4), 4)]:
            with self.subTest(rating=rating):
                due, days, _label = next_review(0, rating, NOW)
                self.assertEqual((due, days), (NOW + delta, interval))
        self.assertEqual(next_review(4, "Hard", NOW)[1], 5)
        self.assertEqual(next_review(4, "Good", NOW)[1], 10)
        self.assertEqual(next_review(4, "Easy", NOW)[1], 14)
        self.assertEqual(next_review(365, "Easy", NOW)[1], 365)
        self.assertEqual(next_review(100, "Again", NOW)[1], 0)
        for interval, rating in [(-1, "Good"), (True, "Good"), (366, "Good"), (0, "Invalid")]:
            with self.assertRaises(ValueError):
                next_review(interval, rating, NOW)

    def test_rating_records_snapshot_and_persists_schedule(self):
        cid = self.add_card()
        with patch("storage.utc_now", return_value=NOW):
            result = self.store.rate_flashcard(cid, "Good", 0)
            self.assertEqual(self.store.due_flashcards(self.did), [])
        self.assertEqual(result["due_at"], (NOW + timedelta(days=1)).isoformat())
        card = self.store.flashcard(cid)
        self.assertEqual((card["interval_days"], card["revision"], card["review_count"]), (1, 1, 1))
        event = self.store.flashcard_history()[0]
        self.assertEqual((event["rating"], event["front"], event["deck_name"]), ("Good", "Что такое производная?", "Algebra"))
        reopened = Store(self.path)
        try:
            self.assertEqual(reopened.flashcard(cid)["due_at"], card["due_at"])
            self.assertEqual(reopened.flashcard_history()[0], event)
        finally:
            reopened.close()

    def test_duplicate_stale_and_early_rating_are_rejected(self):
        cid = self.add_card()
        with patch("storage.utc_now", return_value=NOW):
            self.store.rate_flashcard(cid, "Again", 0)
            with self.assertRaises(ValueError):
                self.store.rate_flashcard(cid, "Good", 0)
            with self.assertRaisesRegex(ValueError, "not due"):
                self.store.rate_flashcard(cid, "Good", 1)
        self.assertEqual(len(self.store.flashcard_history()), 1)
        with patch("storage.utc_now", return_value=NOW + timedelta(minutes=10)):
            self.store.rate_flashcard(cid, "Good", 1)
        self.assertEqual(len(self.store.flashcard_history()), 2)

    def test_edit_resets_schedule_without_rewriting_history(self):
        cid = self.add_card()
        with patch("storage.utc_now", return_value=NOW):
            self.store.rate_flashcard(cid, "Easy", 0)
        event = self.store.flashcard_history()[0]
        future = NOW + timedelta(minutes=1)
        with patch("storage.utc_now", return_value=future):
            self.store.update_flashcard(cid, "New front", "New back", 1)
            self.assertEqual(self.store.due_flashcards(self.did)[0]["id"], cid)
        card = self.store.flashcard(cid)
        self.assertEqual((card["interval_days"], card["revision"], card["review_count"]), (0, 2, 1))
        self.assertEqual(self.store.flashcard_history()[0], event)

    def test_concurrent_edit_and_stale_delete_do_not_overwrite_new_content(self):
        cid = self.add_card()
        other = Store(self.path)
        try:
            other.update_flashcard(cid, "Changed", "New answer", 0)
            with self.assertRaises(ValueError):
                self.store.update_flashcard(cid, "Stale front", "Stale back", 0)
            self.assertFalse(self.store.delete_flashcard(cid, 0))
            self.assertEqual(self.store.flashcard(cid)["front"], "Changed")
        finally:
            other.close()

    def test_rating_failure_rolls_back_schedule_and_event(self):
        cid = self.add_card()
        before = self.store.flashcard(cid)
        self.store.db.execute("""CREATE TRIGGER fail_rating BEFORE UPDATE ON flashcards
            BEGIN SELECT RAISE(ABORT, 'test failure'); END""")
        with patch("storage.utc_now", return_value=NOW):
            with self.assertRaises(sqlite3.IntegrityError):
                self.store.rate_flashcard(cid, "Good", 0)
        self.assertEqual(self.store.flashcard(cid), before)
        self.assertEqual(self.store.flashcard_history(), [])

    def test_deck_deletion_reconfirms_changed_content_and_keeps_reviews(self):
        cid = self.add_card()
        state = self.store.deck_deletion_state(self.did)
        with patch("storage.utc_now", return_value=NOW):
            self.store.rate_flashcard(cid, "Good", 0)
        self.add_card("Extra", "Answer")
        self.assertFalse(self.store.delete_deck(self.did, state))
        self.assertTrue(self.store.delete_deck(self.did, self.store.deck_deletion_state(self.did)))
        self.assertIsNone(self.store.flashcard(cid))
        event = self.store.flashcard_history()[0]
        self.assertIsNone(event["deck_id"])
        self.assertIsNone(event["card_id"])
        self.assertEqual(event["deck_name"], "Algebra")

    def test_subject_and_card_deletion_keep_deck_or_history(self):
        cid = self.add_card()
        with patch("storage.utc_now", return_value=NOW):
            self.store.rate_flashcard(cid, "Good", 0)
        self.store.delete_subject(self.sid)
        self.assertIsNone(self.store.deck(self.did)["subject_id"])
        self.assertEqual(self.store.deck(self.did)["subject_name"], "Математика")
        self.assertIsNotNone(self.store.flashcard(cid))
        self.store.delete_flashcard(cid)
        self.assertEqual(self.store.flashcard_history()[0]["back"], "Limit of a difference quotient.")

    def test_missing_records_and_invalid_rating_are_reported(self):
        cid = self.add_card()
        with patch("storage.utc_now", return_value=NOW):
            with self.assertRaises(ValueError):
                self.store.rate_flashcard(cid, "Invalid", 0)
            with self.assertRaises(ValueError):
                self.store.rate_flashcard(99999, "Good", 0)
        for action in [lambda: self.store.update_deck(99999, "Missing"),
                       lambda: self.store.delete_deck(99999),
                       lambda: self.store.update_flashcard(99999, "Front", "Back", 0),
                       lambda: self.store.delete_flashcard(99999)]:
            with self.assertRaises(ValueError):
                action()
        self.assertEqual(self.store.flashcard_history(), [])
        self.assertEqual(self.store.flashcard(cid)["revision"], 0)

    def test_due_queue_is_isolated_and_bounded(self):
        for index in range(4):
            self.add_card(f"Front {index}", "Back")
        other = self.store.create_deck(self.sid, "Other")
        with patch("storage.utc_now", return_value=NOW):
            self.store.create_flashcard(other, "Other front", "Other back")
            due = self.store.due_flashcards(self.did, limit=2)
        self.assertEqual(len(due), 2)
        self.assertTrue(all(c["deck_id"] == self.did for c in due))


class FlashcardMigrationTests(unittest.TestCase):
    def test_schema_four_preserves_content_practice_and_study_history(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "schema4.sqlite3"
            db = sqlite3.connect(path)
            db.executescript((Path(__file__).parent / "fixtures/schema_v4.sql").read_text())
            db.executescript("""
                INSERT INTO subjects(id,name,name_key) VALUES(42,'Calculus','calculus');
                INSERT INTO topics VALUES(7,42,'Limits','limits');
                INSERT INTO questions(id,subject_id,topic_id,prompt,option_a,option_b,option_c,option_d,correct_option,difficulty,explanation)
                    VALUES(8,42,7,'Limit?','0','1','2','3',1,'Easy','Original explanation');
                INSERT INTO sessions VALUES(9,'2026-11-15',180,42,'Calculus');
                INSERT INTO tasks VALUES('2026-11-15','focus',1);
                INSERT INTO practice_attempts(id,subject_id,subject_name,topic_name,status,question_count,started_at,completed_at)
                    VALUES(10,42,'Calculus','All topics','completed',1,'2026-11-15T12:00:00+00:00','2026-11-15T12:01:00+00:00');
                INSERT INTO practice_items(attempt_id,position,question_id,prompt,option_a,option_b,option_c,option_d,correct_option,selected_option,explanation,difficulty)
                    VALUES(10,0,8,'Limit?','0','1','2','3',1,1,'Original explanation','Easy');
            """)
            db.close()
            store = Store(path)
            try:
                self.assertEqual(store.db.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
                self.assertEqual(store.question(8)["explanation"], "Original explanation")
                self.assertEqual(store.practice_attempt(10)["correct"], 1)
                self.assertEqual(store.seconds(), 180)
                self.assertEqual(tuple(store.db.execute("SELECT * FROM tasks").fetchone()), ("2026-11-15", "focus", 1))
                self.assertEqual(store.decks(), [])
                self.assertEqual(store.flashcard_history(), [])
                did = store.create_deck(42, "New deck")
                store.create_flashcard(did, "Front", "Back")
            finally:
                store.close()
            store = Store(path)
            try:
                self.assertEqual(len(store.decks()), 1)
                self.assertEqual(store.practice_attempt(10)["correct"], 1)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
