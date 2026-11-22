"""Durable focus checkpoints, crash ownership, atomic completion and schema migration."""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'soskuska'))
from storage import Store,SCHEMA_VERSION
from focus import FocusStateError
from backup import PreparedBackup,create_backup,restore_backup


class FocusTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'focus.sqlite3'
        self.store=Store(self.path);self.addCleanup(self.store.close)
        self.sid=self.store.create_subject('Математика – sústredenie')

    def start(self):return self.store.start_focus_checkpoint(self.sid,900)

    def test_one_pending_session_and_exclusive_live_owner(self):
        row=self.start();other=Store(self.path)
        try:
            self.assertEqual(other.pending_focus()['id'],row['id'])
            for action in [lambda:other.start_focus_checkpoint(self.sid,900),lambda:other.claim_focus_checkpoint(row['id'],0),lambda:other.discard_focus_checkpoint(row['id'],0)]:
                with self.assertRaises(ValueError):action()
        finally:other.close()
        self.assertEqual(self.store.seconds(),0)
        self.assertEqual(self.store.summary()['sessions'],0)

    def test_recovery_preserves_only_checkpoint_and_finalizes_once(self):
        row=self.start();self.store.checkpoint_focus(row['id'],17);self.store.close()
        recovered=Store(self.path)
        try:
            snapshot=recovered.pending_focus()
            loaded=recovered.claim_focus_checkpoint(snapshot['id'],snapshot['revision'])
            self.assertEqual(loaded['elapsed_seconds'],17)
            result=recovered.add_session(20,focus_run_id=row['id'])
            self.assertEqual(result['seconds'],20)
            self.assertEqual(recovered.add_session(800,focus_run_id=row['id']),result)
            self.assertEqual(recovered.seconds(),20);self.assertEqual(recovered.summary()['sessions'],1)
            self.assertIsNone(recovered.pending_focus())
        finally:recovered.close()

    def test_abrupt_process_exit_releases_lease_and_keeps_committed_checkpoint(self):
        code="""import os,sys
from storage import Store
s=Store(sys.argv[1]);r=s.start_focus_checkpoint(int(sys.argv[2]),900)
s.checkpoint_focus(r['id'],37)
os._exit(0)
"""
        subprocess.run([sys.executable,'-c',code,str(self.path),str(self.sid)],cwd=Path(__file__).resolve().parents[1]/'soskuska',check=True,timeout=10)
        row=self.store.pending_focus();self.assertEqual(row['elapsed_seconds'],37)
        recovered=self.store.claim_focus_checkpoint(row['id'],row['revision'])
        self.assertEqual(recovered['elapsed_seconds'],37);self.assertEqual(self.store.seconds(),0)

    def test_checkpoint_validation_does_not_move_time_backwards(self):
        row=self.start();self.store.checkpoint_focus(row['id'],10)
        for value in (9,-1,True,10.5,901):
            with self.subTest(value=value),self.assertRaises(ValueError):self.store.checkpoint_focus(row['id'],value)
        self.assertEqual(self.store.pending_focus()['elapsed_seconds'],10)

    def test_checkpoint_lock_failure_is_bounded_and_recoverable(self):
        row=self.start();previous=self.store.db.execute('PRAGMA busy_timeout').fetchone()[0]
        db=sqlite3.connect(self.path);db.execute('BEGIN IMMEDIATE')
        try:
            started=time.monotonic()
            with self.assertRaises(sqlite3.OperationalError):self.store.checkpoint_focus(row['id'],5)
            self.assertLess(time.monotonic()-started,1.0)
        finally:db.rollback();db.close()
        self.assertEqual(self.store.db.execute('PRAGMA busy_timeout').fetchone()[0],previous)
        self.assertEqual(self.store.pending_focus()['elapsed_seconds'],0)
        self.store.checkpoint_focus(row['id'],6)

    def test_failed_final_insert_keeps_checkpoint_and_retry_writes_once(self):
        row=self.start();self.store.checkpoint_focus(row['id'],15)
        self.store.db.execute("CREATE TRIGGER no_session BEFORE INSERT ON sessions BEGIN SELECT RAISE(ABORT,'full'); END")
        with self.assertRaises(sqlite3.Error):self.store.add_session(20,focus_run_id=row['id'])
        self.assertEqual(self.store.pending_focus()['elapsed_seconds'],15);self.assertEqual(self.store.seconds(),0)
        self.store.db.execute('DROP TRIGGER no_session')
        self.store.add_session(20,focus_run_id=row['id']);self.store.add_session(21,focus_run_id=row['id'])
        self.assertEqual(self.store.seconds(),20);self.assertEqual(self.store.summary()['sessions'],1)

    def test_stale_recovery_and_old_owner_cannot_mutate_new_claim(self):
        row=self.start();snapshot=self.store.pending_focus();self.store.release_focus()
        other=Store(self.path)
        try:
            loaded=other.claim_focus_checkpoint(row['id'],snapshot['revision'])
            with self.assertRaises(FocusStateError):self.store.checkpoint_focus(row['id'],5)
            other.release_focus()
            with self.assertRaises(FocusStateError):self.store.discard_focus_checkpoint(row['id'],snapshot['revision'])
            self.store.discard_focus_checkpoint(row['id'],loaded['revision'])
            self.assertIsNone(self.store.pending_focus());self.assertEqual(self.store.seconds(),0)
        finally:other.close()

    def test_zero_finish_has_no_invented_session_and_allows_new_run(self):
        row=self.start();result=self.store.add_session(0,focus_run_id=row['id'])
        self.assertIsNone(result['session_id']);self.assertEqual(self.store.summary()['sessions'],0)
        self.assertNotEqual(self.start()['id'],row['id'])

    def test_source_rename_and_deletion_keep_original_subject_snapshot(self):
        row=self.start();self.store.update_subject(self.sid,'Renamed');self.store.delete_subject(self.sid)
        self.store.add_session(12,focus_run_id=row['id'])
        saved=self.store.recent_sessions()[0]
        self.assertIsNone(saved['subject_id']);self.assertEqual(saved['subject_name'],'Математика – sústredenie')

    def test_backup_pending_recovery_and_restore_guard(self):
        row=self.start();self.store.checkpoint_focus(row['id'],13)
        target=Path(self.temp.name)/'backup.sqlite3';create_backup(self.path,target)
        prepared=PreparedBackup(target,self.path)
        try:
            self.store.close()
            with self.assertRaisesRegex(ValueError,'saved focus'):restore_backup(self.path,prepared)
            current=Store(self.path)
            try:
                pending=current.pending_focus();current.discard_focus_checkpoint(pending['id'],pending['revision'])
            finally:current.close()
            restore_backup(self.path,prepared)
        finally:prepared.close()
        recovered=Store(self.path)
        try:
            pending=recovered.pending_focus();self.assertEqual(pending['elapsed_seconds'],13)
            recovered.claim_focus_checkpoint(pending['id'],pending['revision'])
            recovered.add_session(13,focus_run_id=pending['id']);self.assertEqual(recovered.seconds(),13)
        finally:recovered.close()

    def test_backup_rejects_mismatched_completed_focus_and_protects_focus_lock(self):
        row=self.start()
        with self.assertRaises(ValueError):create_backup(self.path,Path(str(self.path)+'.focus.lock'))
        self.store.add_session(12,focus_run_id=row['id'])
        self.store.db.execute('UPDATE sessions SET seconds=13');self.store.db.commit()
        target=Path(self.temp.name)/'invalid.sqlite3';create_backup(self.path,target)
        with self.assertRaises(ValueError):PreparedBackup(target,self.path)

    def test_start_failure_rolls_back_and_releases_owner(self):
        self.store.db.execute("CREATE TRIGGER no_focus BEFORE INSERT ON focus_runs BEGIN SELECT RAISE(ABORT,'full'); END")
        with self.assertRaises(sqlite3.Error):self.start()
        self.assertIsNone(self.store.pending_focus())
        self.store.db.execute('DROP TRIGGER no_focus');self.start()

    def test_backup_accepts_original_valid_subject_name_domain(self):
        sid=self.store.create_subject('One\x7fTwo')
        row=self.store.start_focus_checkpoint(sid,900)
        self.store.checkpoint_focus(row['id'],13)
        target=Path(self.temp.name)/'control.sqlite3';create_backup(self.path,target)
        prepared=PreparedBackup(target,self.path);prepared.close()

    def test_backup_rejects_revision_overflow_before_restore(self):
        row=self.start();self.store.release_focus()
        self.store.db.execute('UPDATE focus_runs SET revision=?',(float(2**63),));self.store.db.commit()
        target=Path(self.temp.name)/'overflow.sqlite3';create_backup(self.path,target)
        with self.assertRaises(ValueError):PreparedBackup(target,self.path)

    def test_imported_boundary_revision_recovers_and_roundtrips(self):
        row=self.start();self.store.release_focus()
        maximum=2**63-1
        self.store.db.execute('UPDATE focus_runs SET revision=?',(maximum,));self.store.db.commit()
        target=Path(self.temp.name)/'boundary.sqlite3';create_backup(self.path,target)
        PreparedBackup(target,self.path).close()
        claimed=self.store.claim_focus_checkpoint(row['id'],maximum)
        self.assertEqual(claimed['revision'],0)
        self.store.checkpoint_focus(row['id'],13)
        self.store.add_session(13,focus_run_id=row['id'])
        output=Path(self.temp.name)/'boundary-after.sqlite3';create_backup(self.path,output)
        PreparedBackup(output,self.path).close()
        second=self.start();self.store.release_focus()
        self.store.db.execute("UPDATE focus_runs SET revision=? WHERE id=?",(maximum,second['id']));self.store.db.commit()
        self.store.discard_focus_checkpoint(second['id'],maximum)
        self.assertIsNone(self.store.pending_focus())

    def test_accepted_backup_subject_spacing_survives_focus_snapshot(self):
        self.store.db.execute("UPDATE subjects SET name='Subject  title',name_key='subject title' WHERE id=?",(self.sid,));self.store.db.commit()
        before=Path(self.temp.name)/'spacing-before.sqlite3';create_backup(self.path,before)
        PreparedBackup(before,self.path).close()
        row=self.start();self.store.add_session(13,focus_run_id=row['id'])
        after=Path(self.temp.name)/'spacing-after.sqlite3';create_backup(self.path,after)
        PreparedBackup(after,self.path).close()
        self.assertEqual(self.store.recent_sessions()[0]['subject_name'],'Subject  title')


class FocusMigrationTests(unittest.TestCase):
    def test_schema9_upgrade_preserves_rows_and_preferences(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'old.sqlite3'
            with closing(sqlite3.connect(path)) as db:
                db.executescript((Path(__file__).parent/'fixtures/schema_v9.sql').read_text(encoding='utf-8'))
                db.execute("INSERT INTO subjects(name,name_key) VALUES('Keep','keep')")
                db.execute("UPDATE preferences SET appearance_mode='Light',ui_language='Russian',revision=5");db.commit()
            store=Store(path)
            try:
                self.assertEqual(store.db.execute('PRAGMA user_version').fetchone()[0],SCHEMA_VERSION)
                self.assertEqual(store.preferences()['appearance_mode'],'Light');self.assertEqual(store.preferences()['revision'],5)
                self.assertEqual(store.subjects()[0]['name'],'Keep');self.assertIsNone(store.pending_focus())
            finally:store.close()

    def test_failed_upgrade_leaves_schema9_and_content(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'old.sqlite3'
            with closing(sqlite3.connect(path)) as db:db.executescript((Path(__file__).parent/'fixtures/schema_v9.sql').read_text(encoding='utf-8'))
            db=sqlite3.connect(path)
            db.set_authorizer(lambda action,arg,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_CREATE_TABLE and arg=='focus_runs' else sqlite3.SQLITE_OK)
            with patch('storage.sqlite3.connect',return_value=db),self.assertRaises(sqlite3.Error):Store(path)
            with closing(sqlite3.connect(path)) as check:
                self.assertEqual(check.execute('PRAGMA user_version').fetchone()[0],9)
                self.assertIsNone(check.execute("SELECT name FROM sqlite_schema WHERE name='focus_runs'").fetchone())


if __name__=='__main__':unittest.main()
