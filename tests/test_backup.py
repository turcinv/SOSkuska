"""Database round trips, failure atomicity, WAL snapshots and process leases."""
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'soskuska'))
import backup
from backup import TABLES, PreparedBackup, create_backup, restore_backup
from database_lock import DatabaseLease
from preferences import DEFAULTS
from storage import Store, SCHEMA_VERSION


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name);self.active=self.folder/'active.sqlite3';self.copy=self.folder/'backup.sqlite3'
        self.store=Store(self.active);self.addCleanup(self.store.close)

    def populate(self):
        s=self.store
        sid=s.create_subject('Математика — 数学',exam_date='2030-12-01')
        tid=s.create_topic(sid,'Limits')
        s.create_question(sid,'Question?',['A','B','C','D'],1,topic_id=tid,explanation='Because')
        s.set_task('focus',True);s.add_session(75,sid,'Математика — 数学')
        attempt=s.start_practice(sid,1);s.save_practice_answer(attempt,0,1);s.complete_practice(attempt)
        deck=s.create_deck(sid,'Deck');card=s.create_flashcard(deck,'Front','Back');s.rate_flashcard(card,'Good',0)
        s.save_preferences(dict(DEFAULTS,focus_minutes=25,answer_language='Russian'),expected_revision=0)
        return sid

    def rows(self,path):
        with closing(sqlite3.connect(path)) as db:
            return {t:db.execute(f'SELECT * FROM "{t}" ORDER BY rowid').fetchall() for t in TABLES}

    def prepare(self):
        create_backup(self.active,self.copy)
        prepared=PreparedBackup(self.copy,self.active);self.addCleanup(prepared.close);return prepared

    def test_full_roundtrip_and_safety_copy_preserve_all_tables_and_preferences(self):
        self.populate();before=self.rows(self.active);prepared=self.prepare()
        self.store.create_subject('Only in safety copy');current=self.rows(self.active)
        self.store.close();safety=restore_backup(self.active,prepared)
        self.assertEqual(self.rows(self.active),before);self.assertEqual(self.rows(safety),current)
        reopened=Store(self.active)
        try:
            self.assertEqual(reopened.preferences()['focus_minutes'],25)
            self.assertEqual(len(reopened.practice_history()),1)
            self.assertEqual(reopened.statistics()['period'],'Last 7 days')
        finally:reopened.close()

    def test_snapshot_is_independent_and_does_not_include_uncommitted_writes(self):
        self.store.create_subject('Committed')
        self.store.db.execute("INSERT INTO subjects(name,name_key) VALUES('Pending','pending')")
        create_backup(self.active,self.copy)
        with closing(sqlite3.connect(self.copy)) as db:
            self.assertEqual(db.execute('SELECT name FROM subjects').fetchall(),[('Committed',)])
        self.store.db.rollback()

    def test_existing_output_is_never_overwritten(self):
        self.copy.write_bytes(b'keep me')
        with self.assertRaises(FileExistsError):create_backup(self.active,self.copy)
        self.assertEqual(self.copy.read_bytes(),b'keep me')

    def test_racing_output_creation_is_not_clobbered(self):
        publish=os.rename if os.name=='nt' else os.link
        def racing(source,destination):
            Path(destination).write_bytes(b'other writer')
            return publish(source,destination)
        with patch('backup.os.rename' if os.name=='nt' else 'backup.os.link',side_effect=racing):
            with self.assertRaises(FileExistsError):create_backup(self.active,self.copy)
        self.assertEqual(self.copy.read_bytes(),b'other writer')

    def test_snapshot_failure_leaves_no_published_file(self):
        def fail(*args):raise ValueError('injected failure')
        with closing(backup.readonly(self.active)) as db:
            with self.assertRaises(ValueError):backup.snapshot(db,self.copy,check=fail)
        self.assertFalse(self.copy.exists())

    def test_active_database_and_companions_are_protected(self):
        before=self.rows(self.active)
        for suffix in ['','-wal','-shm','-journal','.lock']:
            with self.subTest(suffix=suffix),self.assertRaises(ValueError):
                create_backup(self.active,Path(str(self.active)+suffix))
        self.assertEqual(self.rows(self.active),before)

    def test_private_snapshot_survives_changes_to_selected_file(self):
        self.store.create_subject('Selected');prepared=self.prepare()
        with closing(sqlite3.connect(self.copy)) as db, db:db.execute("UPDATE subjects SET name='Changed',name_key='changed'")
        self.store.close();restore_backup(self.active,prepared)
        self.assertEqual(self.rows(self.active)['subjects'][0][1],'Selected')

    def test_other_store_blocks_restore_until_closed(self):
        prepared=self.prepare();self.store.close();other=Store(self.active)
        try:
            with self.assertRaisesRegex(ValueError,'other SOSkúška'):restore_backup(self.active,prepared)
        finally:other.close()
        self.assertTrue(restore_backup(self.active,prepared).exists())

    def test_exclusive_lease_blocks_other_process_and_releases_after_close(self):
        self.store.close()
        code="import sys;from database_lock import DatabaseLease;lease=DatabaseLease(sys.argv[1]);lease.close()"
        env=dict(os.environ,PYTHONPATH=str(Path(__file__).resolve().parents[1]/'soskuska'))
        with DatabaseLease(self.active,exclusive=True):
            result=subprocess.run([sys.executable,'-c',code,str(self.active)],env=env,capture_output=True,timeout=10)
            self.assertNotEqual(result.returncode,0)
        result=subprocess.run([sys.executable,'-c',code,str(self.active)],env=env,capture_output=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_restore_rejects_current_unfinished_test(self):
        sid=self.populate();prepared=self.prepare();self.store.start_practice(sid,1)
        before=self.rows(self.active);self.store.close()
        with self.assertRaisesRegex(ValueError,'practice test'):restore_backup(self.active,prepared)
        self.assertEqual(self.rows(self.active),before)

    def test_backup_can_restore_an_unfinished_test_for_resume(self):
        sid=self.populate();attempt=self.store.start_practice(sid,1);prepared=self.prepare()
        self.store.discard_practice(attempt);self.store.close();restore_backup(self.active,prepared)
        reopened=Store(self.active)
        try:self.assertEqual(reopened.active_practice()['id'],attempt)
        finally:reopened.close()

    def test_failed_safety_copy_preserves_current_database(self):
        prepared=self.prepare();self.store.create_subject('Keep');before=self.rows(self.active);self.store.close()
        with patch('backup.snapshot',side_effect=OSError('disk full')),self.assertRaises(OSError):
            restore_backup(self.active,prepared)
        self.assertEqual(self.rows(self.active),before)

    def test_mid_restore_failure_rolls_back_and_keeps_safety_copy(self):
        self.populate();prepared=self.prepare();self.store.create_subject('Keep');before=self.rows(self.active);self.store.close()
        real_connect=sqlite3.connect
        class FailingConnection(sqlite3.Connection):
            def execute(self,sql,*args,**kwargs):
                if sql.startswith('INSERT INTO "questions" SELECT'):raise sqlite3.OperationalError('injected write error')
                return super().execute(sql,*args,**kwargs)
        def connect(path,*args,**kwargs):
            if str(path)==self.active.resolve().as_uri()+'?mode=rw':kwargs['factory']=FailingConnection
            return real_connect(path,*args,**kwargs)
        with patch('backup.sqlite3.connect',side_effect=connect),self.assertRaises(sqlite3.OperationalError):restore_backup(self.active,prepared)
        self.assertEqual(self.rows(self.active),before)
        safety=list((self.folder/'backups').glob('*.sqlite3'))
        self.assertEqual(len(safety),1);self.assertEqual(self.rows(safety[0]),before)

    def test_old_future_and_unrelated_backups_are_rejected_without_changing_current(self):
        before=self.rows(self.active)
        for version in [SCHEMA_VERSION-1,SCHEMA_VERSION+1]:
            path=self.folder/f'v{version}.sqlite3';s=Store(path);s.close()
            with closing(sqlite3.connect(path)) as db, db:db.execute(f'PRAGMA user_version={version}')
            with self.assertRaises(ValueError):PreparedBackup(path,self.active)
        unrelated=self.folder/'other.sqlite3'
        with closing(sqlite3.connect(unrelated)) as db, db:db.execute('CREATE TABLE other(id)');db.execute('PRAGMA user_version=6')
        with self.assertRaises(ValueError):PreparedBackup(unrelated,self.active)
        self.assertEqual(self.rows(self.active),before)

    def test_invalid_types_dates_timestamps_and_attempt_items_are_rejected(self):
        self.populate();create_backup(self.active,self.copy)
        changes=["UPDATE subjects SET exam_date='zz-invalid'","UPDATE sessions SET seconds=1.5",
                 "UPDATE practice_attempts SET current_index=0.5","UPDATE practice_attempts SET started_at='2026-01-01T00:00:00'",
                 "DELETE FROM practice_items","UPDATE flashcards SET due_at='garbage'",
                 "UPDATE questions SET option_b=option_a","UPDATE preferences SET answer_language='Unknown'",
                 "UPDATE subjects SET name=zeroblob(4)"]
        for index,sql in enumerate(changes):
            path=self.folder/f'bad{index}.sqlite3'
            with closing(sqlite3.connect(self.copy)) as src,closing(sqlite3.connect(path)) as dst:src.backup(dst)
            with closing(sqlite3.connect(path)) as db, db:db.execute(sql)
            with self.subTest(sql=sql),self.assertRaises((ValueError,sqlite3.Error)):PreparedBackup(path,self.active)

    @unittest.skipUnless(hasattr(os,'mkfifo'),'Named pipes are POSIX-only')
    def test_named_pipe_is_rejected_before_open(self):
        path=self.folder/'pipe';os.mkfifo(path)
        with self.assertRaisesRegex(ValueError,'regular local'):PreparedBackup(path,self.active)

    def test_cleanup_failure_does_not_change_committed_outcome(self):
        prepared=self.prepare()
        with patch.object(prepared.temp,'cleanup',side_effect=OSError('file busy')):
            self.assertFalse(prepared.close())
        prepared.close()

    def test_id_sequence_high_watermark_survives_restore(self):
        sid=self.store.create_subject('Subject')
        with self.store.db:self.store.db.execute("UPDATE sqlite_sequence SET seq=500 WHERE name='subjects'")
        prepared=self.prepare();self.store.close();restore_backup(self.active,prepared)
        reopened=Store(self.active)
        try:self.assertEqual(reopened.create_subject('Next'),501)
        finally:reopened.close()


if __name__=='__main__':unittest.main()
