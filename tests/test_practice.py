"""Practice scoring, snapshot history, resume/deadlines and schema-3 migration."""
import sqlite3
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "soskuska"))
from practice import MissingPracticeError, expired, practice_settings, seconds_left
from storage import SCHEMA_VERSION, Store

NOW = datetime(2026, 11, 15, 12, tzinfo=timezone.utc)


class PracticeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.sqlite3"
        self.store = Store(self.path)
        self.addCleanup(self.store.close)
        self.sid = self.store.create_subject("Математика – skúška")
        self.tid = self.store.create_topic(self.sid, "Algebra")
        self.qids = [self.store.create_question(self.sid, f"Question {i}?", ["one", "two", "three", "four"],
                      i % 4, ["Easy", "Medium", "Hard"][i % 3], self.tid if i < 3 else None,
                      f"Explanation {i}") for i in range(4)]

    def test_filters_and_random_selection_have_no_repeats(self):
        self.assertEqual(len(self.store.practice_pool(self.sid, self.tid)), 3)
        self.assertEqual(len(self.store.practice_pool(self.sid, None)), 1)
        self.assertEqual(len(self.store.practice_pool(self.sid, difficulty="Easy")), 2)
        aid = self.store.start_practice(self.sid, 3, topic=self.tid)
        items = self.store.practice_items(aid)
        self.assertEqual(len({i["question_id"] for i in items}), 3)
        self.assertTrue(all(i["topic_name"] == "Algebra" for i in items))

    def test_answer_and_current_position_survive_reopen(self):
        aid = self.store.start_practice(self.sid, 4)
        self.store.save_practice_answer(aid, 1, 2)
        self.store.set_practice_position(aid, 1)
        other = Store(self.path)
        try:
            self.assertEqual(other.active_practice()["id"], aid)
            self.assertEqual(other.active_practice()["current_index"], 1)
            self.assertEqual(other.active_practice()["answered"], 1)
            self.assertEqual(other.practice_items(aid)[1]["selected_option"], 2)
        finally:
            other.close()

    def test_completed_score_is_recomputable_and_idempotent(self):
        aid = self.store.start_practice(self.sid, 4)
        items = self.store.practice_items(aid)
        self.store.save_practice_answer(aid, 0, items[0]["correct_option"])
        self.store.save_practice_answer(aid, 1, (items[1]["correct_option"] + 1) % 4)
        self.store.save_practice_answer(aid, 2, items[2]["correct_option"])
        self.store.save_practice_answer(aid, 2, None)
        result = self.store.complete_practice(aid)
        self.assertEqual((result["correct"], result["answered"], result["question_count"]), (1, 2, 4))
        again = self.store.complete_practice(aid)
        self.assertEqual(result, again)
        self.assertIsNone(self.store.active_practice())
        self.assertEqual(len(self.store.practice_history()), 1)
        with self.assertRaises(ValueError):
            self.store.save_practice_answer(aid, 0, 1)
        with self.assertRaises(ValueError):
            self.store.set_practice_position(aid, 1)
        with self.assertRaises(ValueError):
            self.store.discard_practice(aid)

    def test_history_uses_snapshots_after_edit_and_delete(self):
        aid = self.store.start_practice(self.sid, 4)
        before = self.store.practice_items(aid)
        self.store.save_practice_answer(aid, 0, before[0]["correct_option"])
        self.store.complete_practice(aid)
        self.store.update_subject(self.sid, "Renamed")
        self.store.update_question(before[0]["question_id"], "Replaced?", ["a", "b", "c", "d"], 3)
        self.store.delete_subject(self.sid)
        result = self.store.practice_attempt(aid)
        after = self.store.practice_items(aid)
        self.assertEqual(result["subject_name"], "Математика – skúška")
        self.assertIsNone(result["subject_id"])
        self.assertEqual(result["correct"], 1)
        for old, new in zip(before, after):
            for field in ["prompt", "option_a", "option_b", "option_c", "option_d", "correct_option", "explanation", "topic_name"]:
                self.assertEqual(old[field], new[field])
            self.assertIsNone(new["question_id"])

    def test_unfinished_test_survives_deleting_source_content(self):
        aid = self.store.start_practice(self.sid, 4)
        self.store.delete_subject(self.sid)
        self.store.save_practice_answer(aid, 0, 0)
        self.assertEqual(self.store.complete_practice(aid)["question_count"], 4)

    def test_deadline_persists_and_late_answers_are_rejected(self):
        with patch("storage.utc_now", return_value=NOW):
            aid = self.store.start_practice(self.sid, 2, minutes=5)
        deadline = (NOW + timedelta(minutes=5)).isoformat()
        self.assertEqual(self.store.practice_attempt(aid)["deadline_at"], deadline)
        with patch("storage.utc_now", return_value=NOW + timedelta(minutes=4)):
            self.store.save_practice_answer(aid, 0, 1)
        with patch("storage.utc_now", return_value=NOW + timedelta(minutes=5)):
            with self.assertRaisesRegex(ValueError, "Time is up"):
                self.store.save_practice_answer(aid, 1, 2)
            with self.assertRaises(ValueError):
                self.store.set_practice_position(aid, 1)
            result = self.store.complete_practice(aid)
        self.assertEqual(result["answered"], 1)
        self.assertEqual(result["completed_at"], deadline)

    def test_only_one_unfinished_test_across_connections(self):
        aid = self.store.start_practice(self.sid, 2)
        other = Store(self.path)
        try:
            with self.assertRaisesRegex(ValueError, "Finish or discard"):
                other.start_practice(self.sid, 1)
            other.discard_practice(aid)
            self.assertEqual(other.practice_items(aid), [])
            self.assertNotEqual(self.store.start_practice(self.sid, 1), aid)
        finally:
            other.close()

    def test_invalid_settings_make_no_attempt(self):
        for kwargs in [dict(count=0), dict(count=101), dict(count=True), dict(count=1.5),
                       dict(count=5), dict(count=1, minutes=0), dict(count=1, minutes=181),
                       dict(count=1, minutes=True), dict(count=1, difficulty="Impossible"),
                       dict(count=1, topic=99999), dict(count=1, topic=True)]:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    self.store.start_practice(self.sid, **kwargs)
            self.assertIsNone(self.store.active_practice())
            self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM practice_items").fetchone()[0], 0)
        other_sid = self.store.create_subject("Other")
        foreign = self.store.create_topic(other_sid, "Other topic")
        with self.assertRaises(ValueError):
            self.store.start_practice(self.sid, 1, topic=foreign)
        with self.assertRaises(ValueError):
            self.store.start_practice(99999, 1)
        with self.assertRaises(ValueError):
            self.store.start_practice(other_sid, 1)

    def test_invalid_answer_or_position_does_not_change_saved_answer(self):
        aid = self.store.start_practice(self.sid, 1)
        self.store.save_practice_answer(aid, 0, 2)
        for selected in [4, -1, True, "A"]:
            with self.assertRaises(ValueError):
                self.store.save_practice_answer(aid, 0, selected)
        with self.assertRaises(ValueError):
            self.store.save_practice_answer(aid, 5, 1)
        with self.assertRaises(ValueError):
            self.store.set_practice_position(aid, 1)
        self.assertEqual(self.store.practice_items(aid)[0]["selected_option"], 2)

    def test_start_rolls_back_if_snapshot_insert_fails(self):
        self.store.db.execute("""CREATE TRIGGER fail_practice BEFORE INSERT ON practice_items
            BEGIN SELECT RAISE(ABORT, 'test insert failure'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.start_practice(self.sid, 2)
        self.assertIsNone(self.store.active_practice())
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM practice_items").fetchone()[0], 0)

    def test_failed_completion_keeps_answers_for_retry(self):
        aid = self.store.start_practice(self.sid, 1)
        self.store.save_practice_answer(aid, 0, 2)
        self.store.db.execute("""CREATE TRIGGER fail_finish BEFORE UPDATE OF status ON practice_attempts
            BEGIN SELECT RAISE(ABORT, 'test update failure'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.complete_practice(aid)
        self.assertEqual(self.store.active_practice()["answered"], 1)
        self.store.db.execute("DROP TRIGGER fail_finish")
        self.assertEqual(self.store.complete_practice(aid)["answered"], 1)

    def test_missing_attempt_is_terminal_and_does_not_finish_a_new_attempt(self):
        aid = self.store.start_practice(self.sid, 1)
        other = Store(self.path)
        try:
            other.discard_practice(aid)
            new_id = other.start_practice(self.sid, 1)
            with self.assertRaises(MissingPracticeError):
                self.store.complete_practice(aid)
            with self.assertRaises(MissingPracticeError):
                self.store.discard_practice(aid)
            self.assertEqual(self.store.active_practice()["id"], new_id)
            self.assertEqual(self.store.practice_attempt(new_id)["status"], "in_progress")
        finally:
            other.close()

    def test_deadline_rounding_and_untimed_rules(self):
        deadline = (NOW + timedelta(seconds=1, microseconds=1)).isoformat()
        self.assertEqual(seconds_left(deadline, NOW), 2)
        self.assertFalse(expired(deadline, NOW))
        self.assertTrue(expired(deadline, NOW + timedelta(seconds=2)))
        self.assertEqual(seconds_left(deadline, NOW + timedelta(seconds=2)), 0)
        self.assertIsNone(seconds_left(None, NOW))
        self.assertFalse(expired(None, NOW))
        practice_settings(100, 180, "Hard")


    def test_discard_at_deadline_keeps_answers_and_completed_history(self):
        with patch("storage.utc_now", return_value=NOW):
            aid = self.store.start_practice(self.sid, 1, minutes=5)
            answer = self.store.practice_items(aid)[0]["correct_option"]
            self.store.save_practice_answer(aid, 0, answer)
        with patch("storage.utc_now", return_value=NOW + timedelta(minutes=5)):
            self.assertFalse(self.store.discard_practice(aid))
        result = self.store.practice_attempt(aid)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["completed_at"], (NOW + timedelta(minutes=5)).isoformat())
        self.assertEqual(result["correct"], 1)
        self.assertEqual(self.store.practice_items(aid)[0]["selected_option"], answer)
        self.assertEqual(len(self.store.practice_history()), 1)
        reopened = Store(self.path)
        try:
            self.assertEqual(reopened.practice_history()[0]["id"], aid)
        finally:
            reopened.close()

    def test_discard_before_deadline_removes_only_unfinished_attempt(self):
        with patch("storage.utc_now", return_value=NOW):
            aid = self.store.start_practice(self.sid, 1, minutes=5)
        with patch("storage.utc_now", return_value=NOW + timedelta(minutes=4, seconds=59)):
            self.assertTrue(self.store.discard_practice(aid))
        self.assertIsNone(self.store.practice_attempt(aid))
        self.assertEqual(self.store.practice_items(aid), [])
        self.assertEqual(self.store.practice_history(), [])

    def test_discard_rechecks_deadline_after_waiting_for_write_lock(self):
        with patch("storage.utc_now", return_value=NOW):
            aid = self.store.start_practice(self.sid, 1, minutes=5)
        locked = threading.Event()
        released = threading.Event()
        failures = []
        def writer():
            try:
                db = sqlite3.connect(self.path)
                db.execute("BEGIN IMMEDIATE")
                locked.set()
                # Release in a bounded interval while the main connection waits.
                released.wait(0.2)
                released.set()
                db.commit()
                db.close()
            except Exception as exc:
                failures.append(exc)
                locked.set()
        thread = threading.Thread(target=writer)
        thread.start()
        self.assertTrue(locked.wait(2))
        def after_lock():
            self.assertTrue(released.is_set(), "Clock read before acquiring write lock")
            return NOW + timedelta(minutes=5, seconds=1)
        try:
            with patch("storage.utc_now", side_effect=after_lock):
                self.assertFalse(self.store.discard_practice(aid))
        finally:
            thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(failures, [])
        self.assertEqual(self.store.practice_attempt(aid)["status"], "completed")

    def test_expiry_save_failure_preserves_attempt_for_retry(self):
        with patch("storage.utc_now", return_value=NOW):
            aid = self.store.start_practice(self.sid, 1, minutes=5)
            self.store.save_practice_answer(aid, 0, 1)
        self.store.db.execute("CREATE TRIGGER fail_expiry BEFORE UPDATE ON practice_attempts BEGIN SELECT RAISE(ABORT,'disk full'); END")
        with patch("storage.utc_now", return_value=NOW + timedelta(minutes=6)):
            with self.assertRaises(sqlite3.Error):
                self.store.discard_practice(aid)
        self.assertEqual(self.store.practice_attempt(aid)["status"], "in_progress")
        self.assertEqual(self.store.practice_items(aid)[0]["selected_option"], 1)
        self.store.db.execute("DROP TRIGGER fail_expiry")
        with patch("storage.utc_now", return_value=NOW + timedelta(minutes=6)):
            self.assertFalse(self.store.discard_practice(aid))


class PracticeMigrationTests(unittest.TestCase):
    def test_schema_three_content_and_history_survive_upgrade(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "schema3.sqlite3"
            db = sqlite3.connect(path)
            db.executescript("""
                CREATE TABLE tasks(day TEXT NOT NULL,name TEXT NOT NULL,done INTEGER NOT NULL,PRIMARY KEY(day,name));
                CREATE TABLE subjects(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,name_key TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL DEFAULT '',exam_date TEXT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE sessions(id INTEGER PRIMARY KEY,day TEXT NOT NULL,seconds INTEGER NOT NULL CHECK(seconds>=0),
                    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,subject_name TEXT);
                CREATE TABLE topics(id INTEGER PRIMARY KEY AUTOINCREMENT,subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,name_key TEXT NOT NULL,UNIQUE(subject_id,name_key));
                CREATE TABLE questions(id INTEGER PRIMARY KEY AUTOINCREMENT,subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
                    topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,prompt TEXT NOT NULL,option_a TEXT NOT NULL,option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL,option_d TEXT NOT NULL,correct_option INTEGER NOT NULL,difficulty TEXT NOT NULL,
                    explanation TEXT NOT NULL DEFAULT '',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
                INSERT INTO subjects(id,name,name_key) VALUES(42,'Calculus','calculus');
                INSERT INTO topics VALUES(7,42,'Limits','limits');
                INSERT INTO questions(id,subject_id,topic_id,prompt,option_a,option_b,option_c,option_d,correct_option,difficulty,explanation)
                    VALUES(8,42,7,'Limit?','0','1','2','3',1,'Easy','Original explanation');
                INSERT INTO sessions VALUES(9,'2026-11-14',180,42,'Calculus');
                INSERT INTO tasks VALUES('2026-11-14','focus',1);
                PRAGMA user_version=3;
            """)
            db.close()
            store = Store(path)
            try:
                self.assertEqual(store.db.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
                self.assertEqual(store.question(8)["explanation"], "Original explanation")
                self.assertEqual(store.topic(7)["name"], "Limits")
                self.assertEqual(store.seconds(), 180)
                self.assertEqual(tuple(store.db.execute("SELECT * FROM tasks").fetchone()), ("2026-11-14", "focus", 1))
                self.assertEqual(store.practice_history(), [])
                self.assertIsNone(store.active_practice())
                store.start_practice(42, 1)
            finally:
                store.close()
            store = Store(path)
            try:
                self.assertEqual(store.active_practice()["question_count"], 1)
                self.assertEqual(store.seconds(), 180)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
