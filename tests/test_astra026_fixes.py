"""Concurrent study edits and timezone-aware data restored from a backup."""
import sys
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "soskuska"))
from backup import PreparedBackup, create_backup, restore_backup
from storage import SCHEMA_VERSION, Store

NOW = datetime(2026, 11, 26, 18, 45, 10, 123456, tzinfo=timezone.utc)
POSITIVE_OFFSET = timezone(timedelta(hours=10))
NEGATIVE_OFFSET = timezone(timedelta(hours=-10))
SECOND_OFFSET = timezone(timedelta(hours=3, seconds=7))
MICROSECOND = timedelta(microseconds=1)


class StudyStoreTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.path = self.folder / "study.sqlite3"
        self.store = Store(self.path)
        self.addCleanup(self.store.close)
        self.sid = self.store.create_subject("Physics")
        self.did = self.store.create_deck(self.sid, "Motion", "Original description")

    def test_stale_deck_edit_preserves_new_description_until_reload(self):
        original = self.store.deck(self.did)
        with closing(Store(self.path)) as other:
            other.update_deck(self.did, "Motion", "New description")
            latest = other.deck(self.did)
            changes = self.store.db.total_changes
            with self.assertRaisesRegex(ValueError, "changed"):
                self.store.update_deck(
                    self.did, "Draft title", original["description"], expected_state=original
                )
            self.assertEqual(other.deck(self.did), latest)
            self.assertEqual(self.store.db.total_changes, changes)
            self.assertFalse(self.store.db.in_transaction)
            reloaded = self.store.deck(self.did)
            self.store.update_deck(
                self.did, "Draft title", reloaded["description"], expected_state=reloaded
            )
            saved = other.deck(self.did)
            self.assertEqual((saved["name"], saved["description"]), ("Draft title", "New description"))

    def test_stale_topic_rename_preserves_new_name_until_reload(self):
        tid = self.store.create_topic(self.sid, "Kinematics")
        original = self.store.topic(tid)
        with closing(Store(self.path)) as other:
            other.update_topic(tid, "Mechanics")
            latest = other.topic(tid)
            changes = self.store.db.total_changes
            with self.assertRaisesRegex(ValueError, "changed"):
                self.store.update_topic(tid, "Draft name", expected_state=original)
            self.assertEqual(other.topic(tid), latest)
            self.assertEqual(self.store.db.total_changes, changes)
            self.assertFalse(self.store.db.in_transaction)
            self.store.update_topic(tid, "Draft name", expected_state=self.store.topic(tid))
            self.assertEqual(other.topic(tid)["name"], "Draft name")

    def test_deck_edit_only_compares_editable_fields_and_identity(self):
        original = self.store.deck(self.did)
        with closing(Store(self.path)) as other:
            other.update_subject(self.sid, "Classical physics")
            other.create_flashcard(self.did, "Speed?", "Distance per unit time")
        self.store.update_deck(self.did, "Velocity", "Original description", expected_state=original)
        self.assertEqual(self.store.deck(self.did)["name"], "Velocity")
        self.assertEqual(self.store.deck(self.did)["current_subject_name"], "Classical physics")

    def test_deleted_edit_records_fail_without_recreating_rows(self):
        tid = self.store.create_topic(self.sid, "Kinematics")
        original_deck = self.store.deck(self.did)
        original_topic = self.store.topic(tid)
        with closing(Store(self.path)) as other:
            other.delete_deck(self.did)
            other.delete_topic(tid)
            changes = self.store.db.total_changes
            with self.assertRaisesRegex(ValueError, "no longer exists"):
                self.store.update_deck(self.did, "Draft title", expected_state=original_deck)
            with self.assertRaisesRegex(ValueError, "no longer exists"):
                self.store.update_topic(tid, "Draft name", expected_state=original_topic)
            self.assertIsNone(other.deck(self.did))
            self.assertIsNone(other.topic(tid))
            self.assertEqual(self.store.db.total_changes, changes)
            self.assertFalse(self.store.db.in_transaction)

    def card_due_at(self, front, timestamp):
        cid = self.store.create_flashcard(self.did, front, "Answer")
        with self.store.db:
            self.store.db.execute("UPDATE flashcards SET due_at=? WHERE id=?", (timestamp, cid))
        return cid

    def test_due_uses_instant_order_with_microseconds_and_id_tiebreak(self):
        equal_high = self.card_due_at("Due with positive offset", NOW.astimezone(POSITIVE_OFFSET).isoformat())
        equal_low = self.card_due_at("Due with negative offset", NOW.astimezone(NEGATIVE_OFFSET).isoformat())
        older = self.card_due_at("Earlier by one microsecond", (NOW - MICROSECOND).isoformat())
        future = self.card_due_at(
            "Later by one microsecond", (NOW + MICROSECOND).astimezone(NEGATIVE_OFFSET).isoformat()
        )
        changes = self.store.db.total_changes
        with patch("storage.utc_now", return_value=NOW):
            self.assertEqual(self.store.decks()[0]["due_count"], 3)
            self.assertEqual(
                [card["id"] for card in self.store.due_flashcards(self.did)], [older, equal_high, equal_low]
            )
            self.assertEqual(
                [card["id"] for card in self.store.due_flashcards(self.did, limit=2)], [older, equal_high]
            )
            with self.assertRaisesRegex(ValueError, "not due"):
                self.store.rate_flashcard(future, "Good", 0)
            self.assertEqual(self.store.flashcard_history(), [])
            self.assertEqual(self.store.flashcard(future)["revision"], 0)
            self.assertEqual(self.store.db.total_changes, changes)
            self.assertFalse(self.store.db.in_transaction)
            self.store.rate_flashcard(equal_high, "Good", 0)

    def test_due_checks_accept_offsets_crossing_the_utc_calendar_range(self):
        early = self.card_due_at("Before UTC year 1", "0001-01-01T00:00:00+01:00")
        late = self.card_due_at("After UTC year 9999", "9999-12-31T23:59:59-01:00")
        with patch("storage.utc_now", return_value=NOW):
            self.assertEqual(self.store.decks()[0]["due_count"], 1)
            self.assertEqual([card["id"] for card in self.store.due_flashcards(self.did)], [early])
            with self.assertRaisesRegex(ValueError, "not due"):
                self.store.rate_flashcard(late, "Good", 0)
            self.store.rate_flashcard(early, "Good", 0)
        self.assertEqual(self.store.flashcard_history()[0]["card_id"], early)

    def test_statistics_leaves_an_open_read_cursor_usable(self):
        self.store.create_subject("Mathematics")
        with closing(self.store.db.execute("SELECT name FROM subjects ORDER BY id")) as cursor:
            self.assertEqual(cursor.fetchone()[0], "Physics")
            self.assertEqual(self.store.statistics()["practice_completed"], 0)
            self.assertEqual(cursor.fetchone()[0], "Mathematics")
        self.assertFalse(self.store.db.in_transaction)

    def test_restored_offsets_work_in_readonly_reports_and_writable_rating(self):
        # Use an event just before local midnight to check the actual calendar day.
        instant = datetime(2026, 11, 25, 23, 59, 58).astimezone(timezone.utc)
        event_day = instant.astimezone().date()
        event_timestamp = instant.astimezone(SECOND_OFFSET).isoformat()
        due_timestamp = (NOW - timedelta(minutes=5)).astimezone(POSITIVE_OFFSET).isoformat()
        self.store.create_question(self.sid, "Speed?", ["scalar", "vector", "angle", "force"], 0)
        with patch("storage.utc_now", return_value=instant):
            aid = self.store.start_practice(self.sid, 1)
            self.store.save_practice_answer(aid, 0, 0)
            self.store.complete_practice(aid)
            reviewed = self.store.create_flashcard(self.did, "Reviewed", "Answer")
            event_id = self.store.rate_flashcard(reviewed, "Good", 0)["id"]
        due = self.card_due_at("Ready to review", due_timestamp)
        with self.store.db:
            self.store.db.execute(
                "UPDATE practice_attempts SET completed_at=? WHERE id=?", (event_timestamp, aid)
            )
            self.store.db.execute(
                "UPDATE review_events SET reviewed_at=? WHERE id=?", (event_timestamp, event_id)
            )

        backup = self.folder / "backup.sqlite3"
        target = self.folder / "target.sqlite3"
        create_backup(self.path, backup)
        Store(target).close()
        with closing(PreparedBackup(backup, target)) as prepared:
            restore_backup(target, prepared)

        with closing(Store.open_existing(target, readonly=True)) as restored:
            with patch("storage.utc_now", return_value=NOW):
                queue = restored.due_flashcards(self.did)
                self.assertIn(due, [card["id"] for card in queue])
                self.assertEqual(restored.decks()[0]["due_count"], len(queue))
            self.assertEqual(restored.flashcard(due)["due_at"], due_timestamp)
            self.assertEqual(restored.practice_attempt(aid)["completed_at"], event_timestamp)
            self.assertEqual(restored.flashcard_history()[0]["reviewed_at"], event_timestamp)
            history = restored.practice_history_page(
                date_from=event_day.isoformat(), date_to=event_day.isoformat()
            )
            self.assertEqual([row["id"] for row in history["rows"]], [aid])
            report = restored.statistics("All time", today=event_day)
            self.assertEqual(report["practice_completed"], 1)
            self.assertEqual(report["practice_accuracy"], 100)
            self.assertEqual(report["reviews"], 1)
            self.assertEqual(report["rating_counts"]["Good"], 1)
            self.assertEqual(
                report["daily"][-1],
                {"day": event_day.isoformat(), "seconds": 0, "practice": 1, "reviews": 1},
            )
            self.assertEqual(restored.db.total_changes, 0)
            self.assertEqual(restored.db.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
            self.assertFalse(restored.db.in_transaction)

        with closing(Store(target)) as restored, patch("storage.utc_now", return_value=NOW):
            rated = restored.rate_flashcard(due, "Good", 0)
            self.assertEqual(restored.flashcard_history()[0]["previous_due_at"], due_timestamp)
            self.assertEqual(rated["due_at"], (NOW + timedelta(days=1)).isoformat())


if __name__ == "__main__":
    unittest.main()
