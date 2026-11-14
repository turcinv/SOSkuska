"""Question authoring, topic ownership and schema v2 upgrade regressions."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "soskuska"))
from storage import Store, SCHEMA_VERSION


class QuestionBankTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "study.sqlite3"
        self.store = Store(self.path)
        self.addCleanup(self.store.close)
        self.sid = self.store.create_subject("Математика")
        self.other = self.store.create_subject("Physics")
        self.tid = self.store.create_topic(self.sid, "Алгебра")

    def add_question(self, **kwargs):
        args = dict(subject_id=self.sid, prompt="Сколько будет 2 + 2?", options=["3", "4", "5", "6"],
                    correct_option=1, difficulty="Easy", topic_id=self.tid, explanation="Дважды два — четыре.")
        args.update(kwargs)
        return self.store.create_question(**args)

    def test_unicode_question_and_answers_survive_reopen(self):
        qid = self.add_question()
        other = Store(self.path)
        try:
            question = other.question(qid)
            self.assertEqual((question["prompt"], question["option_b"], question["correct_option"]), ("Сколько будет 2 + 2?", "4", 1))
            self.assertEqual(question["topic_id"], self.tid)
            self.assertEqual(question["explanation"], "Дважды два — четыре.")
        finally:
            other.close()

    def test_question_edit_retains_identity_and_subject(self):
        qid = self.add_question()
        self.store.update_question(qid, "What is 3 × 3?", ["3", "6", "9", "12"], 2, "Hard", None, "Three groups of three.")
        question = self.store.question(qid)
        self.assertEqual((question["id"], question["subject_id"], question["option_c"], question["correct_option"]), (qid, self.sid, "9", 2))
        self.assertIsNone(question["topic_id"])
        self.assertEqual(len(self.store.questions(self.sid)), 1)

    def test_topic_name_uniqueness_is_unicode_and_subject_scoped(self):
        with self.assertRaises(ValueError):
            self.store.create_topic(self.sid, "  АЛГЕБРА  ")
        self.store.create_topic(self.other, "Алгебра")
        tid = self.store.create_topic(self.sid, "Café")
        with self.assertRaises(ValueError):
            self.store.create_topic(self.sid, "Cafe\u0301")
        with self.assertRaises(ValueError):
            self.store.update_topic(tid, "Алгебра")
        self.assertEqual(self.store.topic(tid)["name"], "Café")

    def test_topic_rename_updates_question_listing(self):
        self.add_question()
        self.store.update_topic(self.tid, "Algebra")
        self.assertEqual(self.store.questions(self.sid)[0]["topic_name"], "Algebra")

    def test_topic_delete_keeps_questions_unassigned(self):
        qid = self.add_question()
        self.store.delete_topic(self.tid)
        self.assertIsNone(self.store.question(qid)["topic_id"])
        self.assertEqual(len(self.store.questions(self.sid)), 1)
        self.assertIsNone(self.store.questions(self.sid)[0]["topic_name"])

    def test_question_delete_only_removes_selected_question(self):
        qid = self.add_question()
        other_qid = self.add_question(prompt="Another question")
        self.store.delete_question(qid)
        self.assertIsNone(self.store.question(qid))
        self.assertEqual([q["id"] for q in self.store.questions(self.sid)], [other_qid])

    def test_subject_delete_cascades_content_but_keeps_time(self):
        qid = self.add_question()
        other_tid = self.store.create_topic(self.other, "Mechanics")
        other_qid = self.add_question(subject_id=self.other, topic_id=other_tid)
        self.store.add_session(90, self.sid)
        self.store.delete_subject(self.sid)
        self.assertIsNone(self.store.question(qid))
        self.assertIsNone(self.store.topic(self.tid))
        self.assertIsNotNone(self.store.question(other_qid))
        self.assertEqual(self.store.seconds(), 90)
        self.assertEqual(self.store.recent_sessions()[0]["subject_name"], "Математика")

    def test_topic_from_other_subject_is_rejected_in_api_and_sql(self):
        foreign_tid = self.store.create_topic(self.other, "Mechanics")
        with self.assertRaises(ValueError):
            self.add_question(topic_id=foreign_tid)
        qid = self.add_question()
        with self.assertRaises(ValueError):
            self.store.update_question(qid, "Question", ["1", "2", "3", "4"], 0, topic_id=foreign_tid)
        with self.assertRaises(sqlite3.IntegrityError), self.store.db:
            self.store.db.execute("UPDATE questions SET topic_id=? WHERE id=?", (foreign_tid, qid))
        self.assertEqual(self.store.question(qid)["topic_id"], self.tid)

    def test_validation_rejects_invalid_questions_without_inserting(self):
        cases = [dict(prompt=" "), dict(prompt="x" * 2001), dict(options=["1", "2", "3"]),
                 dict(options="abcd"), dict(options=["1", "", "3", "4"]),
                 dict(options=["A", " a ", "B", "C"]), dict(options=["Café", "Cafe\u0301", "B", "C"]),
                 dict(options=["x" * 501, "2", "3", "4"]), dict(correct_option=-1),
                 dict(correct_option=4), dict(correct_option=True), dict(difficulty="Impossible"),
                 dict(explanation="x" * 2001), dict(topic_id=99999), dict(subject_id=99999)]
        for fields in cases:
            with self.subTest(fields=str(fields)[:80]):
                with self.assertRaises(ValueError):
                    self.add_question(**fields)
        self.assertEqual(self.store.questions(self.sid), [])

    def test_invalid_edit_preserves_previous_answer(self):
        qid = self.add_question()
        with self.assertRaises(ValueError):
            self.store.update_question(qid, "Bad edit", ["1", "1", "2", "3"], 0)
        self.assertEqual(self.store.question(qid)["option_b"], "4")

    def test_topic_validation_and_missing_records(self):
        for name in ["", " ", "x" * 121]:
            with self.assertRaises(ValueError):
                self.store.create_topic(self.sid, name)
        with self.assertRaises(ValueError):
            self.store.create_topic(9999, "Missing")
        with self.assertRaises(ValueError):
            self.store.update_topic(9999, "Missing")
        with self.assertRaises(ValueError):
            self.store.delete_topic(9999)
        with self.assertRaises(ValueError):
            self.store.update_question(9999, "Missing", ["1", "2", "3", "4"], 0)
        with self.assertRaises(ValueError):
            self.store.delete_question(9999)

    def test_subject_counts_do_not_multiply_session_time(self):
        self.add_question()
        self.add_question(prompt="Second")
        self.store.create_topic(self.sid, "Geometry")
        self.store.add_session(90, self.sid)
        self.store.add_session(30, self.sid)
        subject = next(s for s in self.store.subjects() if s["id"] == self.sid)
        self.assertEqual((subject["topic_count"], subject["question_count"], subject["session_count"], subject["study_seconds"]), (2, 2, 2, 120))
        self.assertEqual(self.store.questions(self.other), [])


class QuestionMigrationTests(unittest.TestCase):
    def test_v2_database_keeps_subject_task_and_session_on_upgrade(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "v2.sqlite3"
            db = sqlite3.connect(path)
            db.executescript("""
                CREATE TABLE tasks(day TEXT NOT NULL,name TEXT NOT NULL,done INTEGER NOT NULL,PRIMARY KEY(day,name));
                CREATE TABLE subjects(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,name_key TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL DEFAULT '',exam_date TEXT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE sessions(id INTEGER PRIMARY KEY,day TEXT NOT NULL,seconds INTEGER NOT NULL CHECK(seconds>=0),
                    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,subject_name TEXT);
                CREATE INDEX sessions_subject ON sessions(subject_id);
                INSERT INTO subjects(id,name,name_key,description,exam_date) VALUES(42,'Mathematics','mathematics','Calculus','2026-12-12');
                INSERT INTO tasks VALUES('2026-11-11','focus',1);
                INSERT INTO sessions VALUES(7,'2026-11-11',95,42,'Mathematics');
                PRAGMA user_version=2;
            """)
            db.close()
            store = Store(path)
            try:
                self.assertEqual(store.db.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
                self.assertEqual(store.subject(42)["exam_date"], "2026-12-12")
                self.assertEqual(tuple(store.db.execute("SELECT * FROM tasks").fetchone()), ("2026-11-11", "focus", 1))
                self.assertEqual(store.recent_sessions()[0]["subject_id"], 42)
                self.assertEqual(store.seconds(), 95)
                self.assertEqual(store.topics(42), [])
                self.assertEqual(store.questions(42), [])
            finally:
                store.close()
            store = Store(path)
            self.assertEqual(store.seconds(), 95)
            store.close()


if __name__ == "__main__":
    unittest.main()
