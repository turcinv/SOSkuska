"""Regression tests from the independent backup/restore review."""
import os
import sqlite3
import tempfile
import unicodedata
import unittest
from contextlib import closing
from pathlib import Path

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'soskuska'))

from backup import PreparedBackup, create_backup, restore_backup
from storage import Store


class ReviewFindings(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)
        self.active = self.root / 'active.sqlite3'
        self.candidate = self.root / 'candidate.sqlite3'

    def write_subject(self, path, name, *, exam_date=None):
        with closing(Store(path)) as store:
            return store.create_subject(name, exam_date=exam_date or '')

    def test_backup_cannot_claim_case_variant_of_absent_active_journal(self):
        self.write_subject(self.active, 'Active')
        if not (self.root / self.active.name.upper()).exists():
            self.skipTest('case-sensitive filesystem')
        destination = self.root / (self.active.name.upper() + '-JOURNAL')
        self.assertFalse(destination.exists())
        with self.assertRaises(ValueError):
            create_backup(self.active, destination)
        self.assertFalse(destination.exists())

    def test_backup_cannot_claim_normalized_alias_of_absent_active_journal(self):
        self.active = self.root / 'caf\u00e9.sqlite3'
        self.write_subject(self.active, 'Active')
        alias = self.root / unicodedata.normalize('NFD', self.active.name)
        if not alias.exists():
            self.skipTest('normalization-sensitive filesystem')
        destination = alias.with_name(alias.name + '-journal')
        self.assertFalse(destination.exists())
        with self.assertRaises(ValueError):
            create_backup(self.active, destination)
        self.assertFalse(destination.exists())

    def test_hardlinked_active_database_is_not_opened_or_restored(self):
        self.write_subject(self.active, 'Active')
        self.write_subject(self.candidate, 'Restorable')
        alias = self.root / 'alias.sqlite3'
        try:
            os.link(self.active, alias)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f'hard links unavailable: {error}')
        with self.assertRaises((OSError, ValueError)):
            with closing(Store(alias)):
                self.fail('Opening a hard-linked database bypasses the active lease')
        with closing(PreparedBackup(self.candidate, self.active)) as prepared:
            with self.assertRaises((OSError, ValueError)):
                restore_backup(self.active, prepared)
        with closing(sqlite3.connect(self.active)) as db:
            self.assertEqual(db.execute('SELECT name FROM subjects').fetchall(), [('Active',)])

    def test_closed_wal_candidate_is_checked_without_creating_companions(self):
        self.write_subject(self.active, 'Active')
        with closing(Store(self.candidate)) as store:
            store.create_subject('Candidate')
            mode = store.db.execute('PRAGMA journal_mode=wal').fetchone()[0]
        if mode != 'wal':
            self.skipTest('SQLite WAL mode unavailable')
        companions = [Path(str(self.candidate) + suffix) for suffix in ('-wal', '-shm')]
        self.assertFalse(any(path.exists() for path in companions))
        original = self.candidate.read_bytes()
        with self.assertRaises(ValueError):
            with closing(PreparedBackup(self.candidate, self.active)):
                pass
        self.assertEqual(self.candidate.read_bytes(), original)
        self.assertFalse(any(path.exists() for path in companions))

    def test_export_wal_database_as_standalone_portable_snapshot(self):
        with closing(Store(self.active)) as store:
            mode = store.db.execute('PRAGMA journal_mode=wal').fetchone()[0]
            if mode != 'wal':
                self.skipTest('SQLite WAL mode unavailable')
            store.create_subject('Committed to the active WAL')
            create_backup(store.path, self.candidate)
        self.assertEqual(self.candidate.read_bytes()[18:20], b'\x01\x01')
        with closing(PreparedBackup(self.candidate, self.active)) as prepared:
            self.assertEqual(prepared.counts['subjects'], 1)
        self.assertFalse(Path(str(self.candidate) + '-wal').exists())
        self.assertFalse(Path(str(self.candidate) + '-shm').exists())

    def test_reject_backup_with_invalid_exam_date(self):
        self.write_subject(self.active, 'Active')
        self.write_subject(self.candidate, 'Invalid candidate')
        with closing(sqlite3.connect(self.candidate)) as db, db:
            db.execute("UPDATE subjects SET exam_date='zz-invalid'")
        with self.assertRaises(ValueError):
            with closing(PreparedBackup(self.candidate, self.active)):
                pass
        with closing(Store(self.active)) as store:
            self.assertEqual([subject['name'] for subject in store.subjects()], ['Active'])

    def test_reject_backup_with_fractional_session_seconds(self):
        self.write_subject(self.active, 'Active')
        self.write_subject(self.candidate, 'Invalid candidate')
        with closing(sqlite3.connect(self.candidate)) as db, db:
            db.execute("INSERT INTO sessions(day, seconds) VALUES ('2026-01-01', 1.5)")
        with self.assertRaises(ValueError):
            with closing(PreparedBackup(self.candidate, self.active)):
                pass

    def test_reject_active_database_trigger_that_silently_drops_questions(self):
        self.write_subject(self.active, 'Active')
        with closing(sqlite3.connect(self.active)) as db, db:
            db.execute('DROP TRIGGER questions_topic_insert')
            db.execute('CREATE TRIGGER questions_topic_insert BEFORE INSERT ON questions '
                       'BEGIN SELECT RAISE(IGNORE); END')
        with closing(Store(self.candidate)) as store:
            subject = store.create_subject('Candidate')
            store.create_question(subject, 'Which answer?', ['A', 'B', 'C', 'D'], 0, 'Easy')
        with closing(PreparedBackup(self.candidate, self.active)) as prepared:
            self.assertEqual(prepared.counts['questions'], 1)
            with self.assertRaises(ValueError):
                restore_backup(self.active, prepared)
        with closing(sqlite3.connect(self.active)) as db:
            self.assertEqual(db.execute('SELECT name FROM subjects').fetchall(), [('Active',)])

    def test_missing_active_database_is_not_created_by_restore(self):
        self.write_subject(self.candidate, 'Candidate')
        self.assertFalse(self.active.exists())
        with closing(PreparedBackup(self.candidate, self.active)) as prepared:
            with self.assertRaises((OSError, ValueError, sqlite3.Error)):
                restore_backup(self.active, prepared)
        self.assertFalse(self.active.exists())

    def test_reject_mixed_sqlite_header_without_creating_companions(self):
        self.write_subject(self.active, 'Active')
        self.write_subject(self.candidate, 'Candidate')
        with self.candidate.open('r+b') as db:
            db.seek(18)
            db.write(b'\x01\x02')
        with self.assertRaises(ValueError):
            with closing(PreparedBackup(self.candidate, self.active)):
                pass
        self.assertFalse(Path(str(self.candidate) + '-wal').exists())
        self.assertFalse(Path(str(self.candidate) + '-shm').exists())

    def test_reject_extra_trigger_named_like_sqlite_internal_object(self):
        self.write_subject(self.active, 'Active')
        self.write_subject(self.candidate, 'Candidate')
        with closing(sqlite3.connect(self.candidate)) as db, db:
            db.execute('CREATE TRIGGER sqliteXguard BEFORE INSERT ON subjects BEGIN SELECT 1; END')
        with self.assertRaises(ValueError):
            with closing(PreparedBackup(self.candidate, self.active)):
                pass

    def test_reject_index_with_different_predicate_string_literal(self):
        self.write_subject(self.active, 'Active')
        self.write_subject(self.candidate, 'Candidate')
        with closing(sqlite3.connect(self.active)) as db, db:
            db.execute('DROP INDEX practice_one_active')
            db.execute('CREATE UNIQUE INDEX practice_one_active ON practice_attempts(status) '
                       "WHERE status='IN_PROGRESS'")
        with closing(PreparedBackup(self.candidate, self.active)) as prepared:
            with self.assertRaises(ValueError):
                restore_backup(self.active, prepared)
