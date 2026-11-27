"""Headless, read-only study queries used by the planned MCP server."""
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "soskuska"
sys.path.insert(0, str(SOURCE))
import storage
import study_queries as q
from storage import Store, user_database_path


class UserDatabasePathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"

    def resolve(self, platform, env):
        with patch.object(storage.sys, "platform", platform), \
             patch.dict(os.environ, env, clear=True), \
             patch.object(Path, "home", return_value=self.home):
            return user_database_path()

    def test_platform_bases_match_the_gui_rules(self):
        cases = [
            ("darwin", {}, self.home / "Library/Application Support"),
            ("win32", {}, self.home / "AppData/Local"),
            ("win32", {"LOCALAPPDATA": str(self.home / "Local")}, self.home / "Local"),
            ("linux", {}, self.home / ".local/share"),
            ("linux", {"XDG_DATA_HOME": str(self.home / "xdg")}, self.home / "xdg"),
        ]
        for platform, env, base in cases:
            with self.subTest(platform=platform, env=env):
                self.assertEqual(self.resolve(platform, env), base / "SOSkuska/dashboard.sqlite3")

    def test_legacy_database_is_still_preferred_when_it_is_the_only_one(self):
        legacy = self.home / ".local/share/ExamPrep/dashboard.sqlite3"
        legacy.parent.mkdir(parents=True)
        legacy.write_bytes(b"")
        self.assertEqual(self.resolve("linux", {}), legacy)

    def test_query_layer_imports_without_tk(self):
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import storage, study_queries; "
                "bad = [m for m in ('tkinter', 'customtkinter', 'app') if m in sys.modules]; "
                "sys.exit(1 if bad else 0)")
        result = subprocess.run([sys.executable, "-c", code, str(SOURCE)], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)


class StudyQueryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "study.sqlite3"
        self.store = Store(self.path)
        self.addCleanup(self.store.close)

    def populate(self):
        s = self.store
        exam = (date.today() + timedelta(days=10)).isoformat()
        self.bio = s.create_subject("Biology", "Cells and plants", exam)
        self.chem = s.create_subject("Chemistry")
        self.cells = s.create_topic(self.bio, "Cells")
        self.plants = s.create_topic(self.bio, "Plants")
        self.q1 = s.create_question(self.bio, "What powers the cell?", ["Mitochondria", "Ribosome", "Wall", "Golgi"], 0,
                                    "Easy", self.cells, "Mitochondria make ATP.")
        self.q2 = s.create_question(self.bio, "Where is chlorophyll?", ["Nucleus", "Chloroplast", "Vacuole", "Membrane"], 1,
                                    "Hard", self.plants, "Chloroplasts hold chlorophyll.")
        self.q3 = s.create_question(self.bio, "Cell theory author?", ["Schwann", "Darwin", "Mendel", "Hooke"], 0, "Medium")
        self.deck = s.create_deck(self.bio, "Bio cards")
        self.card = s.create_flashcard(self.deck, "ATP?", "Energy currency")
        s.create_flashcard(self.deck, "DNA?", "Genetic material")
        s.add_session(600, self.bio)
        attempt = s.start_practice(self.bio, 3)
        for item in s.practice_items(attempt):
            s.save_practice_answer(attempt, item["position"], item["correct_option"] if item["topic_name"] != "Plants" else None)
        s.complete_practice(attempt)
        self.attempt = attempt

    def test_empty_database_gives_empty_bounded_results(self):
        self.assertEqual(q.subjects_overview(self.store), {"items": [], "returned": 0, "truncated": False, "total": 0})
        self.assertEqual(q.decks_overview(self.store)["items"], [])
        self.assertEqual(q.practice_results(self.store)["items"], [])
        self.assertEqual(q.upcoming(self.store)["items"], [])
        report = q.study_report(self.store, "All time")
        self.assertIsNone(report["practice"]["accuracy_percent"])
        self.assertEqual(report["focus"]["minutes"], 0)
        self.assertEqual(report["active_days"], [])

    def test_overview_and_detail_counts(self):
        self.populate()
        overview = q.subjects_overview(self.store)
        bio = next(item for item in overview["items"] if item["id"] == self.bio)
        self.assertEqual((bio["topic_count"], bio["question_count"], bio["study_minutes"], bio["session_count"]), (2, 3, 10.0, 1))
        self.assertEqual(bio["days_until_exam"], 10)
        detail = q.subject_detail(self.store, self.bio)
        self.assertEqual([t["name"] for t in detail["topics"]], ["Cells", "Plants"])
        self.assertEqual(detail["topics"][0]["by_difficulty"], {"Easy": 1, "Medium": 0, "Hard": 0})
        self.assertEqual(detail["questions_without_topic"], {"question_count": 1, "by_difficulty": {"Easy": 0, "Medium": 1, "Hard": 0}})
        self.assertFalse(detail["truncated"])
        self.assertEqual(q.upcoming(self.store)["items"][0]["subject"], "Biology")

    def test_answers_and_backs_are_hidden_unless_requested(self):
        self.populate()
        hidden = q.find_questions(self.store, self.bio)
        text = json.dumps(hidden)
        self.assertNotIn("correct_option", text)
        self.assertNotIn("ATP.", text)
        self.assertEqual(hidden["items"][0]["options"]["A"], "Schwann")
        shown = q.find_questions(self.store, self.bio, query="CHLOROPHYLL", include_answers=True)
        self.assertEqual([(i["id"], i["correct_option"]) for i in shown["items"]], [(self.q2, "B")])
        cards = q.due_cards(self.store, self.deck)
        self.assertEqual(cards["total"], 2)
        self.assertNotIn("Energy currency", json.dumps(cards))
        self.assertIn("Energy currency", json.dumps(q.due_cards(self.store, self.deck, include_backs=True)))
        self.assertEqual(q.decks_overview(self.store)["items"][0]["due_count"], 2)

    def test_question_filters(self):
        self.populate()
        ids = lambda **kw: [i["id"] for i in q.find_questions(self.store, self.bio, **kw)["items"]]
        self.assertEqual(ids(topic_id=self.cells), [self.q1])
        self.assertEqual(ids(topic_id=None), [self.q3])
        self.assertEqual(ids(difficulty="Hard"), [self.q2])
        self.assertEqual(ids(query="ribosome"), [self.q1])
        self.assertEqual(ids(limit=1), [self.q3])
        self.assertEqual(q.find_questions(self.store, self.bio, limit=1)["total"], 3)

    def test_invalid_arguments_raise_clear_value_errors(self):
        self.populate()
        calls = [
            lambda: q.subject_detail(self.store, 999),
            lambda: q.subject_detail(self.store, "1"),
            lambda: q.subject_detail(self.store, True),
            lambda: q.find_questions(self.store, self.bio, topic_id=self.cells + 100),
            lambda: q.find_questions(self.store, self.chem, topic_id=self.cells),
            lambda: q.find_questions(self.store, self.bio, difficulty="Impossible"),
            lambda: q.find_questions(self.store, self.bio, include_answers="yes"),
            lambda: q.find_questions(self.store, self.bio, limit=0),
            lambda: q.find_questions(self.store, self.bio, query="x" * 201),
            lambda: q.due_cards(self.store, 999),
            lambda: q.study_report(self.store, "Forever"),
            lambda: q.practice_results(self.store, limit=-1),
        ]
        for index, call in enumerate(calls):
            with self.subTest(index=index), self.assertRaises(ValueError):
                call()

    def test_limits_are_clamped_and_long_text_is_truncated(self):
        sid = self.store.create_subject("Long")
        for n in range(60):
            self.store.create_question(sid, f"{n} " + "p" * 1990, [f"a{n}", f"b{n}", f"c{n}", f"d{n}"], 0,
                                       explanation="e" * 2000)
        result = q.find_questions(self.store, sid, limit=500, include_answers=True)
        self.assertEqual(result["total"], 60)
        self.assertTrue(result["truncated"])
        self.assertLessEqual(result["returned"], 50)
        self.assertLessEqual(len(json.dumps(result, ensure_ascii=False)), q.TEXT_BUDGET + 2000)
        first = result["items"][0]
        self.assertEqual(len(first["prompt"]), q.TEXT_LIMIT)
        self.assertTrue(first["prompt"].endswith("…"))
        short = q.find_questions(self.store, sid, query="59 ", limit=1)
        self.assertEqual(short["returned"], 1)

    def test_history_keeps_deleted_subject_snapshot_and_topic_scores(self):
        self.populate()
        self.store.delete_subject(self.bio)
        history = q.practice_results(self.store)
        attempt = history["items"][0]
        self.assertEqual((attempt["id"], attempt["subject"], attempt["subject_still_exists"]), (self.attempt, "Biology", False))
        self.assertEqual((attempt["correct"], attempt["question_count"], attempt["score_percent"]), (2, 3, 66.7))
        self.assertEqual({t["topic"]: (t["correct"], t["total"]) for t in attempt["by_topic"]},
                         {None: (1, 1), "Cells": (1, 1), "Plants": (0, 1)})
        self.assertEqual(q.practice_results(self.store, subject_name="Biology")["total"], 1)
        report = q.study_report(self.store, "All time")
        self.assertEqual((report["practice"]["correct"], report["practice"]["questions"], report["practice"]["accuracy_percent"]), (2, 3, 66.7))
        self.assertIn("self-assessment", report["flashcards"]["note"])

    def test_every_query_runs_read_only_and_leaves_the_file_unchanged(self):
        self.populate()
        self.store.close()
        before = (hashlib.sha256(self.path.read_bytes()).hexdigest(), self.path.stat().st_mtime_ns)
        readonly = Store.open_existing(self.path, readonly=True)
        try:
            q.subjects_overview(readonly)
            q.subject_detail(readonly, self.bio)
            q.find_questions(readonly, self.bio, include_answers=True)
            q.decks_overview(readonly)
            q.due_cards(readonly, self.deck, include_backs=True)
            for period in q.PERIODS:
                q.study_report(readonly, period)
            q.practice_results(readonly)
            q.upcoming(readonly)
            with self.assertRaises(sqlite3.OperationalError):
                readonly.db.execute("DELETE FROM subjects")
        finally:
            readonly.close()
        after = (hashlib.sha256(self.path.read_bytes()).hexdigest(), self.path.stat().st_mtime_ns)
        self.assertEqual(before, after)
        self.assertFalse(Path(str(self.path) + "-journal").exists())


if __name__ == "__main__":
    unittest.main()
