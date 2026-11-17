"""Statistics date boundaries, weighting, retention and consistent read snapshots."""
import sqlite3
import sys
import tempfile
import unittest
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "soskuska"))
from storage import SCHEMA_VERSION, Store
from study_statistics import duration

TODAY = date(2026, 11, 17)


def local_noon(day):
    return datetime.combine(day, time(12)).astimezone(timezone.utc)


class StatisticsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "stats.sqlite3"
        self.store = Store(self.path)
        self.addCleanup(self.store.close)
        self.sid = self.store.create_subject("Математика")
        self.did = self.store.create_deck(self.sid, "Algebra")
        for i in range(5):
            self.store.create_question(self.sid, f"Question {i}?", ["yes", "no", "maybe", "never"], 0)

    def focus(self, day, seconds=60, sid=None, name="Математика"):
        with self.store.db:
            self.store.db.execute("INSERT INTO sessions(day,seconds,subject_id,subject_name) VALUES (?,?,?,?)",
                                  (day.isoformat(), seconds, sid or self.sid, name))

    def practice(self, day, count=1, correct=1, answered=None):
        now = local_noon(day)
        answered = count if answered is None else answered
        with patch("storage.utc_now", return_value=now):
            aid = self.store.start_practice(self.sid, count)
            for index in range(answered):
                self.store.save_practice_answer(aid, index, 0 if index < correct else 1)
            self.store.complete_practice(aid)
        return aid

    def review(self, day, rating="Good"):
        with patch("storage.utc_now", return_value=local_noon(day)):
            cid = self.store.create_flashcard(self.did, "Front?", "Back")
            self.store.rate_flashcard(cid, rating, 0)
        return cid

    def report(self, period="Last 7 days"):
        return self.store.statistics(period, today=TODAY)

    def test_empty_is_zero_without_invented_accuracy_or_activity(self):
        report = self.report()
        self.assertEqual(report["focus_seconds"], 0)
        self.assertEqual(report["sessions"], 0)
        self.assertEqual(report["practice_completed"], 0)
        self.assertIsNone(report["practice_accuracy"])
        self.assertEqual(report["reviews"], 0)
        self.assertEqual(report["focus_by_subject"], [])
        self.assertEqual(len(report["daily"]), 7)
        self.assertTrue(all(row["seconds"] == row["practice"] == row["reviews"] == 0 for row in report["daily"]))

    def test_seven_day_range_includes_today_and_six_days_ago(self):
        for days, seconds in [(0, 10), (6, 20), (7, 40), (-1, 80)]:
            self.focus(TODAY - timedelta(days=days), seconds)
            self.practice(TODAY - timedelta(days=days))
            self.review(TODAY - timedelta(days=days))
        report = self.report()
        self.assertEqual(report["focus_seconds"], 30)
        self.assertEqual(report["focus_days"], 2)
        self.assertEqual(report["practice_completed"], 2)
        self.assertEqual(report["reviews"], 2)
        self.assertEqual(report["daily"][0]["day"], "2026-11-11")
        self.assertEqual(report["daily"][-1]["day"], "2026-11-17")

    def test_thirty_day_and_all_time_ranges_with_chart_limit(self):
        for days in [0, 29, 30, 400]:
            self.focus(TODAY - timedelta(days=days))
        self.assertEqual(self.report("Last 30 days")["sessions"], 2)
        report = self.report("All time")
        self.assertEqual(report["sessions"], 4)
        self.assertEqual(report["focus_seconds"], 240)
        self.assertEqual(sum(row["seconds"] for row in report["daily"]), 120)
        self.assertEqual(len(report["daily"]), 30)
        self.assertIsNone(report["start_day"])

    def test_accuracy_weights_questions_not_attempt_percentages(self):
        self.practice(TODAY, 1, 1)
        self.practice(TODAY, 4, 0, answered=2)
        report = self.report()
        self.assertEqual(report["practice_completed"], 2)
        self.assertEqual(report["practice_questions"], 5)
        self.assertEqual(report["practice_answered"], 3)
        self.assertEqual(report["practice_correct"], 1)
        self.assertEqual(report["practice_accuracy"], 20)

    def test_in_progress_and_discarded_attempts_are_not_results(self):
        aid = self.store.start_practice(self.sid, 1)
        self.store.save_practice_answer(aid, 0, 0)
        self.assertEqual(self.report()["practice_completed"], 0)
        self.store.discard_practice(aid)
        self.assertEqual(self.report()["practice_completed"], 0)

    def test_each_rating_counted_without_inventing_focus_or_accuracy(self):
        for rating in ["Again", "Again", "Hard", "Good", "Easy"]:
            self.review(TODAY, rating)
        report = self.report()
        self.assertEqual(report["rating_counts"], {"Again": 2, "Hard": 1, "Good": 1, "Easy": 1})
        self.assertEqual(report["reviews"], 5)
        self.assertEqual(report["focus_seconds"], 0)
        self.assertIsNone(report["practice_accuracy"])

    def test_full_history_is_counted_beyond_ui_history_limit(self):
        for _ in range(23):
            self.review(TODAY)
            self.practice(TODAY)
        self.assertEqual(len(self.store.flashcard_history()), 20)
        self.assertEqual(len(self.store.practice_history()), 20)
        self.assertEqual(self.report()["reviews"], 23)
        self.assertEqual(self.report()["practice_completed"], 23)

    def test_deleting_sources_keeps_historical_totals(self):
        self.focus(TODAY, 75)
        self.practice(TODAY)
        cid = self.review(TODAY)
        self.store.delete_flashcard(cid, 1)
        self.store.delete_deck(self.did)
        self.store.delete_subject(self.sid)
        report = self.report()
        self.assertEqual((report["focus_seconds"], report["practice_correct"], report["reviews"]), (75, 1, 1))
        self.assertIsNone(report["focus_by_subject"][0]["subject_id"])
        self.assertEqual(report["focus_by_subject"][0]["name"], "Математика")

    def test_focus_subjects_use_live_identity_and_keep_legacy_unassigned(self):
        self.focus(TODAY)
        self.store.update_subject(self.sid, "Renamed")
        self.focus(TODAY, name="Renamed")
        with self.store.db:
            self.store.db.execute("INSERT INTO sessions(day,seconds) VALUES (?,?)", (TODAY.isoformat(), 10))
        rows = self.report()["focus_by_subject"]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "Renamed")
        self.assertEqual(rows[0]["seconds"], 120)
        self.assertIsNone(rows[1]["name"])
        self.assertEqual(sum(row["seconds"] for row in rows), 130)

    def test_zero_length_sessions_are_not_active_days(self):
        self.focus(TODAY, 0)
        self.assertEqual(self.report()["sessions"], 0)
        self.assertEqual(self.report()["focus_days"], 0)

    def test_utc_events_use_local_calendar_day(self):
        # Choose a UTC instant near midnight; derive the expected local date so
        # this exercises the system time zone on Linux, Windows and macOS.
        instant = datetime(2026, 11, 17, 0, 15, tzinfo=timezone.utc)
        expected = instant.astimezone().date()
        with patch("storage.utc_now", return_value=instant):
            cid = self.store.create_flashcard(self.did, "F", "B")
            self.store.rate_flashcard(cid, "Good", 0)
        report = self.report("Last 30 days")
        matching = [row for row in report["daily"] if row["reviews"]]
        self.assertEqual([row["day"] for row in matching], [expected.isoformat()])

    def test_practice_bucket_uses_completion_not_start(self):
        aid = self.practice(TODAY)
        with self.store.db:
            self.store.db.execute("UPDATE practice_attempts SET started_at=? WHERE id=?",
                                  (local_noon(TODAY - timedelta(days=60)).isoformat(), aid))
        self.assertEqual(self.report()["practice_completed"], 1)

    def test_report_is_read_only_and_schema_unchanged(self):
        self.review(TODAY)
        changes = self.store.db.total_changes
        for period in ["Last 7 days", "Last 30 days", "All time"]:
            self.report(period)
        self.assertEqual(changes, self.store.db.total_changes)
        self.assertEqual(self.store.db.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
        self.assertFalse(self.store.db.in_transaction)
        with self.assertRaises(ValueError):
            self.report("Last 8 days")

    def test_snapshot_is_consistent_during_concurrent_write(self):
        self.store.db.execute("PRAGMA journal_mode=WAL")
        self.focus(TODAY)
        other = Store(self.path)
        self.addCleanup(other.close)
        fired = []
        def trace(sql):
            if "SELECT date(a.completed_at" in sql and not fired:
                fired.append(True)
                with other.db:
                    other.db.execute("INSERT INTO sessions(day,seconds) VALUES (?,?)", (TODAY.isoformat(), 90))
        self.store.db.set_trace_callback(trace)
        try:
            report = self.report()
        finally:
            self.store.db.set_trace_callback(None)
        self.assertTrue(fired)
        self.assertEqual(report["focus_seconds"], 60)
        self.assertEqual(sum(row["seconds"] for row in report["focus_by_subject"]), 60)
        self.assertEqual(self.report()["focus_seconds"], 150)

    def test_query_failure_rolls_back_read_transaction_and_can_retry(self):
        self.store.db.set_authorizer(lambda action, *_: sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_READ else sqlite3.SQLITE_OK)
        try:
            with self.assertRaises(sqlite3.DatabaseError):
                self.report()
        finally:
            self.store.db.set_authorizer(None)
        self.assertFalse(self.store.db.in_transaction)
        self.assertEqual(self.report()["sessions"], 0)

    def test_duration_keeps_seconds(self):
        self.assertEqual(duration(5), "0m 5s")
        self.assertEqual(duration(3665), "1h 1m 5s")


if __name__ == "__main__":
    unittest.main()
