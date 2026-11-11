"""Real subject CRUD, migrations and truthful Dashboard aggregates."""
import sqlite3
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "soskuska"))
from storage import SCHEMA_VERSION, Store


class SubjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "study.sqlite3"
        self.store = Store(self.path)
        self.addCleanup(lambda: self.store.close())

    def test_new_database_is_empty_and_versioned(self):
        self.assertEqual(self.store.db.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
        self.assertEqual(self.store.subjects(), [])
        self.assertEqual(self.store.summary(), {"seconds": 0, "today_seconds": 0, "sessions": 0, "streak": 0, "subjects": 0})

    def test_unicode_create_edit_and_reopen(self):
        sid = self.store.create_subject("  Математика   skúška  ", "  Derivatives  ", "2026-12-12")
        self.assertEqual(self.store.subject(sid)["name"], "Математика skúška")
        self.store.update_subject(sid, "Fyzika", "Mechanics", "2026-12-14")
        other = Store(self.path)
        try:
            subject = other.subject(sid)
            self.assertEqual((subject["name"], subject["description"], subject["exam_date"]), ("Fyzika", "Mechanics", "2026-12-14"))
        finally:
            other.close()

    def test_duplicate_names_include_case_and_unicode_normalization(self):
        sid = self.store.create_subject("МАТЕМАТИКА")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.store.create_subject("математика")
        other = self.store.create_subject("English")
        with self.assertRaises(ValueError):
            self.store.update_subject(other, "Математика")
        self.assertEqual(self.store.subject(other)["name"], "English")
        self.store.update_subject(sid, "Математика")
        self.store.create_subject("Café")
        with self.assertRaises(ValueError):
            self.store.create_subject("Cafe\u0301")

    def test_invalid_fields_do_not_create_records(self):
        for name, description, exam in [(" ", "", ""), ("x" * 121, "", ""),
                                        ("Math", "x" * 1001, ""),
                                        ("Math", "", "2026-02-30"),
                                        ("Math", "", "20261212")]:
            with self.subTest(name=name[:20], exam=exam):
                with self.assertRaises(ValueError):
                    self.store.create_subject(name, description, exam)
        self.assertEqual(self.store.subjects(), [])

    def test_delete_keeps_history_and_name_snapshot(self):
        sid = self.store.create_subject("Mathematics")
        self.store.add_session(95, sid)
        self.store.update_subject(sid, "Calculus")
        self.store.delete_subject(sid)
        self.assertIsNone(self.store.subject(sid))
        self.assertEqual(self.store.seconds(), 95)
        session = self.store.recent_sessions()[0]
        self.assertIsNone(session["subject_id"])
        self.assertEqual(session["subject_name"], "Mathematics")
        # IDs must not be reused to attach old sessions to a new subject.
        other = self.store.create_subject("Physics")
        self.assertNotEqual(sid, other)
        self.assertEqual(self.store.subjects()[0]["study_seconds"], 0)

    def test_explicit_session_snapshot_survives_external_delete(self):
        sid = self.store.create_subject("History")
        self.store.delete_subject(sid)
        self.store.add_session(30, sid, "History")
        session = self.store.recent_sessions()[0]
        self.assertIsNone(session["subject_id"])
        self.assertEqual(session["subject_name"], "History")

    def test_missing_updates_and_deletes_are_reported(self):
        with self.assertRaises(ValueError):
            self.store.update_subject(100, "Missing")
        with self.assertRaises(ValueError):
            self.store.delete_subject(100)

    def test_real_subject_totals_and_streak(self):
        sid = self.store.create_subject("Mathematics")
        self.store.add_session(90, sid)
        self.store.add_session(30, sid)
        for days in [1, 2, 8]:
            self.store.db.execute("INSERT INTO sessions(day,seconds) VALUES (?,?)", ((date.today() - timedelta(days=days)).isoformat(), 60))
        self.store.db.commit()
        summary = self.store.summary()
        self.assertEqual(summary["seconds"], 300)
        self.assertEqual(summary["today_seconds"], 120)
        self.assertEqual(summary["sessions"], 5)
        self.assertEqual(summary["streak"], 3)
        subject = self.store.subjects()[0]
        self.assertEqual((subject["study_seconds"], subject["session_count"]), (120, 2))

    def test_exams_are_saved_and_sorted_without_past_dates(self):
        today = date.today()
        self.store.create_subject("Later", exam_date=(today + timedelta(days=4)).isoformat())
        self.store.create_subject("Today", exam_date=today.isoformat())
        self.store.create_subject("Past", exam_date=(today - timedelta(days=1)).isoformat())
        self.store.create_subject("No date")
        self.assertEqual([s["name"] for s in self.store.upcoming_exams()], ["Today", "Later"])

    def test_invalid_time_is_rejected_without_writes(self):
        for seconds in [-1, 1.5, True]:
            with self.assertRaises(ValueError):
                self.store.add_session(seconds)
        self.assertEqual(self.store.recent_sessions(), [])


class MigrationTests(unittest.TestCase):
    def test_unversioned_original_database_preserves_all_records(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "old.sqlite3"
            db = sqlite3.connect(path)
            db.executescript("""
                CREATE TABLE tasks(day TEXT NOT NULL,name TEXT NOT NULL,done INTEGER NOT NULL,PRIMARY KEY(day,name));
                CREATE TABLE sessions(id INTEGER PRIMARY KEY,day TEXT NOT NULL,seconds INTEGER NOT NULL CHECK(seconds>=0));
                INSERT INTO tasks VALUES ('2026-11-10','cards',1);
                INSERT INTO sessions VALUES (7,'2026-11-10',95);
            """)
            db.close()
            store = Store(path)
            self.assertEqual(tuple(store.db.execute("SELECT * FROM tasks").fetchone()), ("2026-11-10", "cards", 1))
            old = store.recent_sessions()[0]
            self.assertEqual((old["id"], old["day"], old["seconds"], old["subject_id"], old["subject_name"]), (7, "2026-11-10", 95, None, None))
            self.assertEqual(store.subjects(), [])
            store.close()
            store = Store(path)
            self.assertEqual(store.seconds(), 95)
            self.assertEqual(store.db.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
            store.close()

    def test_newer_database_is_not_downgraded(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "new.sqlite3"
            db = sqlite3.connect(path)
            db.execute("PRAGMA user_version=99")
            db.close()
            with self.assertRaisesRegex(ValueError, "newer"):
                Store(path)
            db = sqlite3.connect(path)
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 99)
            db.close()


if __name__ == "__main__":
    unittest.main()
