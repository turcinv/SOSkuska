"""Bounded history pages, historical subject names and inclusive local date filters."""
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'soskuska'))
from storage import Store, SCHEMA_VERSION


class PracticeHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'history.db'
        self.store = Store(self.path); self.addCleanup(self.store.close)
        self.sid = self.store.create_subject('Settings')
        self.qid = self.store.create_question(self.sid, 'Original?', ['A','B','C','D'], 1, explanation='Original explanation')

    def completed(self, stamp=None, sid=None):
        aid = self.store.start_practice(self.sid if sid is None else sid, 1)
        self.store.save_practice_answer(aid, 0, 1)
        self.store.complete_practice(aid)
        if stamp:
            self.store.db.execute('UPDATE practice_attempts SET completed_at=? WHERE id=?', (stamp,aid)); self.store.db.commit()
        return aid

    def test_all_pages_have_stable_order_no_gaps_and_bounded_rows(self):
        ids = [self.completed('2026-11-10T12:00:00+00:00') for _ in range(45)]
        pages = [self.store.practice_history_page(page=i) for i in range(3)]
        self.assertEqual([len(p['rows']) for p in pages], [20,20,5])
        self.assertEqual([row['id'] for p in pages for row in p['rows']], ids[::-1])
        self.assertTrue(all(p['total']==45 and p['pages']==3 for p in pages))
        self.assertEqual(self.store.practice_history_page(page=99)['page'],2)
        self.assertEqual(self.store.db.execute('PRAGMA user_version').fetchone()[0],SCHEMA_VERSION)

    def test_local_date_bounds_are_inclusive_and_combine_with_subject(self):
        stamps = [datetime(2026,11,10,0),datetime(2026,11,10,23,59,59),datetime(2026,11,11,0)]
        ids = [self.completed(stamp.astimezone(timezone.utc).isoformat()) for stamp in stamps]
        other = self.store.create_subject('Other'); self.store.create_question(other,'Other?',['a','b','c','d'],0)
        self.completed(stamps[0].astimezone(timezone.utc).isoformat(),other)
        report = self.store.practice_history_page(subject_name='Settings', date_from='2026-11-10',date_to='2026-11-10')
        self.assertEqual([r['id'] for r in report['rows']],ids[:2][::-1])
        self.assertEqual(self.store.practice_history_page(date_from='2026-11-11')['total'],1)
        self.assertEqual(self.store.practice_history_page(date_to='2026-11-10')['total'],3)

    def test_renamed_deleted_and_recreated_subjects_use_saved_names(self):
        old = self.completed(); self.store.update_subject(self.sid,'Renamed'); newer=self.completed()
        self.store.delete_subject(self.sid)
        replacement=self.store.create_subject('Settings'); self.store.create_question(replacement,'New?',['a','b','c','d'],0)
        recent=self.completed(sid=replacement)
        report=self.store.practice_history_page(subject_name='Settings')
        self.assertEqual([r['id'] for r in report['rows']],[recent,old])
        self.assertEqual(report['subjects'],['Renamed','Settings'])
        self.assertEqual(self.store.practice_history_page(subject_name='Renamed')['rows'][0]['id'],newer)
        self.assertEqual(self.store.practice_items(old)[0]['explanation'],'Original explanation')

    def test_backup_accepted_iso_timestamp_matches_display_local_date(self):
        stamp='2026-11-10T12:00:00+00:00:00'
        aid=self.completed(stamp)
        local_day=datetime.fromisoformat(stamp).astimezone().date().isoformat()
        report=self.store.practice_history_page(date_from=local_day,date_to=local_day)
        self.assertEqual([row['id'] for row in report['rows']],[aid])

    def test_chronological_order_normalizes_offsets_and_fractional_precision(self):
        later=self.completed('2026-11-10T10:00:00+00:00')
        earlier=self.completed('2026-11-10T12:00:00+03:00')
        latest=self.completed('2026-11-10T10:00:00.000001+00:00')
        self.assertEqual([r['id'] for r in self.store.practice_history_page()['rows']],[latest,later,earlier])

    def test_empty_and_no_match_are_single_empty_page(self):
        report=self.store.practice_history_page(page=100)
        self.assertEqual((report['rows'],report['total'],report['page'],report['pages']),([],0,0,1))
        self.completed()
        report=self.store.practice_history_page(subject_name="' OR 1=1 --")
        self.assertEqual(report['total'],0)
        self.assertEqual(report['subjects'],['Settings'])

    def test_in_progress_and_discarded_attempts_are_excluded(self):
        aid=self.store.start_practice(self.sid,1)
        self.assertEqual(self.store.practice_history_page()['subjects'],[])
        self.store.discard_practice(aid)
        self.assertEqual(self.store.practice_history_page()['total'],0)

    def test_invalid_filters_do_not_mutate_or_leave_transaction(self):
        aid=self.completed()
        for kwargs in [dict(page=True),dict(page=-1),dict(page_size=0),dict(page_size=101),dict(page_size=True),
                       dict(subject_name=42),dict(subject_name=''),dict(date_from='2026-02-30'),
                       dict(date_from='20261110'),dict(date_to=None),dict(date_from='2026-11-12',date_to='2026-11-10')]:
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError): self.store.practice_history_page(**kwargs)
            self.assertFalse(self.store.db.in_transaction)
        self.assertEqual(self.store.practice_history_page()['rows'][0]['id'],aid)

    def test_read_failure_rolls_back_and_can_retry_without_writes(self):
        self.completed(); before=self.store.db.total_changes
        def denied(action,arg1,arg2,db,trigger):
            return sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_READ and arg1=='practice_items' else sqlite3.SQLITE_OK
        self.store.db.set_authorizer(denied)
        with self.assertRaises(sqlite3.Error): self.store.practice_history_page()
        self.store.db.set_authorizer(None)
        self.assertFalse(self.store.db.in_transaction)
        self.assertEqual(self.store.practice_history_page()['total'],1)
        self.assertEqual(self.store.db.total_changes,before)

    def test_count_rows_and_subjects_share_read_snapshot(self):
        self.completed(); self.store.db.execute('PRAGMA journal_mode=WAL')
        other=Store(self.path)
        try:
            sid=other.create_subject('Concurrent'); other.create_question(sid,'New?',['a','b','c','d'],0)
            fired=[]
            def trace(sql):
                if 'SELECT a.*' in sql and not fired:
                    fired.append(True); aid=other.start_practice(sid,1); other.complete_practice(aid)
            self.store.db.set_trace_callback(trace)
            report=self.store.practice_history_page()
            self.store.db.set_trace_callback(None)
            self.assertEqual(report['total'],1);self.assertEqual(len(report['rows']),1)
            self.assertEqual(report['subjects'],['Settings']);self.assertTrue(fired)
            self.assertEqual(self.store.practice_history_page()['total'],2)
        finally:
            self.store.db.set_trace_callback(None);other.close()


if __name__=='__main__': unittest.main()
