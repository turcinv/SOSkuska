"""Consistent SQLite snapshots and validated, transactional local restore. No Tk."""
import os
import sqlite3
import tempfile
import time
import uuid
import re
import unicodedata
from contextlib import closing
from datetime import datetime
from pathlib import Path

from database_lock import DatabaseLease
from storage import SCHEMA_VERSION, Store
from backup_validation import validate_records

TABLES = ('tasks', 'subjects', 'sessions', 'topics', 'questions', 'practice_attempts',
          'practice_items', 'decks', 'flashcards', 'review_events', 'preferences', 'tutor_conversations', 'tutor_turns', 'sqlite_sequence')
TIMEOUT = 60


def readonly(path):
    return sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True, timeout=0.2)


def deadline():
    end = time.monotonic() + TIMEOUT
    def check(*args):
        if time.monotonic() > end:
            raise ValueError('Database operation timed out. Your current data is unchanged; retry with a local file.')
    return check


def protect_path(path, active):
    path, active = Path(path).resolve(), Path(active).resolve()
    protected = [active] + [Path(str(active) + suffix) for suffix in ('-wal', '-shm', '-journal', '.lock')]
    for item in protected:
        if unicodedata.normalize('NFC',str(path)).casefold() == unicodedata.normalize('NFC',str(item)).casefold() or (path.exists() and item.exists() and os.path.samefile(path, item)):
            raise ValueError('Choose a separate backup file, not the active database or its companion files.')
    return path


def snapshot(source, destination, *, check=None):
    """Never overwrite an existing file. Publish a complete SQLite snapshot."""
    destination = Path(destination).resolve()
    check = check or deadline()
    if destination.exists():
        raise FileExistsError('Choose an unused backup filename; existing files are never overwritten.')
    with tempfile.TemporaryDirectory(prefix='.soskuska-backup-', dir=destination.parent) as folder:
        staging = Path(folder) / 'snapshot.sqlite3'
        with closing(sqlite3.connect(staging)) as target:
            source.backup(target, pages=128, progress=check, sleep=0.02)
            target.execute('PRAGMA journal_mode=DELETE')
            target.set_progress_handler(lambda: (check(), 0)[1], 1000)
            if target.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                raise ValueError('The database snapshot failed its integrity check.')
        check()
        staging.chmod(0o600)
        # No reservation or overwrite: publish the completed file exclusively.
        if os.name == 'nt':
            os.rename(staging, destination)  # Windows refuses an existing destination.
        else:
            os.link(staging, destination)  # Atomic no-clobber publication on local filesystems.
            staging.unlink()
    return destination


def create_backup(active, destination):
    active = Path(active).resolve()
    destination = protect_path(destination, active)
    with DatabaseLease(active), closing(readonly(active)) as source:
        return snapshot(source, destination)


def schema_signature(db):
    objects = [(row[0],row[1],row[2], re.sub(r'\s+', ' ', row[3]).strip().rstrip(';') if row[3] else None) for row in db.execute("SELECT type,name,tbl_name,CASE WHEN type IN ('trigger','index') THEN sql ELSE NULL END FROM sqlite_schema WHERE name NOT GLOB 'sqlite_*' ORDER BY type,name")]
    columns = {name: [tuple(row) for row in db.execute(f'PRAGMA table_info("{name}")')] for name in TABLES}
    return objects, columns


class PreparedBackup:
    """Own the validated private copy until confirmation, cancellation or completion."""
    def __init__(self, source, active):
        self.source = protect_path(source, active)
        if not self.source.is_file():
            raise ValueError('Choose a regular local backup file.')
        with self.source.open('rb') as header:
            start = header.read(20)
        if start[:16] != b'SQLite format 3\x00' or start[18:20] != bytes([1,1]):
            raise ValueError('Choose a standalone backup made with Create backup, not a WAL-mode or invalid working database.')
        self.temp = tempfile.TemporaryDirectory(prefix='soskuska-restore-')
        self.path = Path(self.temp.name) / 'validated.sqlite3'
        check = deadline()
        try:
            raw = Path(self.temp.name) / 'input.sqlite3'
            with closing(readonly(self.source)) as db:
                snapshot(db, raw, check=check)
            clean = Store(self.path)
            try:
                with closing(readonly(raw)) as db:
                    db.set_progress_handler(lambda: (check(), 0)[1], 1000)
                    if db.execute('PRAGMA user_version').fetchone()[0] != SCHEMA_VERSION:
                        raise ValueError(f'Choose a SOSkúška schema {SCHEMA_VERSION} backup. Older/newer schemas cannot be restored by this version.')
                    if schema_signature(db) != schema_signature(clean.db):
                        raise ValueError('This file does not have the expected SOSkúška database structure.')
                    if db.execute('PRAGMA foreign_key_check').fetchone() is not None:
                        raise ValueError('The backup contains broken record references.')
                    clean.db.execute('PRAGMA defer_foreign_keys=ON')
                    with clean.db:
                        for name in reversed(TABLES):
                            clean.db.execute(f'DELETE FROM "{name}"')
                        for name in TABLES:
                            if name == 'sqlite_sequence':
                                clean.db.execute('DELETE FROM sqlite_sequence')
                            cursor = db.execute(f'SELECT * FROM "{name}"')
                            while rows := cursor.fetchmany(128):
                                check()
                                marks = ','.join('?' for _ in rows[0])
                                clean.db.executemany(f'INSERT INTO "{name}" VALUES ({marks})', rows)
                    validate_records(clean, TABLES, check)
                    self.counts = {name: clean.db.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
                                   for name in ('subjects', 'questions', 'sessions', 'flashcards')}
            finally:
                clean.close()
        except BaseException:
            self.close()
            raise

    def close(self):
        # Cleanup must never turn a committed restore into an apparent failure.
        try:
            self.temp.cleanup()
        except OSError:
            return False
        return True


def restore_backup(active, prepared):
    """App's Store must be closed first. Lock, snapshot old data, then commit once."""
    active = Path(active).resolve()
    check = deadline()
    safety = None
    with DatabaseLease(active, exclusive=True), closing(sqlite3.connect(active.as_uri() + '?mode=rw', uri=True, timeout=0.2)) as target:
        target.set_progress_handler(lambda: (check(), 0)[1], 1000)
        target.execute('PRAGMA foreign_keys=OFF')
        target.execute('ATTACH DATABASE ? AS restored', (prepared.path.as_uri() + '?mode=ro',))
        try:
            target.execute('BEGIN IMMEDIATE')
            with closing(readonly(prepared.path)) as validated:
                if target.execute('PRAGMA user_version').fetchone()[0] != SCHEMA_VERSION or schema_signature(target) != schema_signature(validated):
                    raise ValueError('The current database structure changed. Restore was not applied.')
            if target.execute("SELECT 1 FROM practice_attempts WHERE status='in_progress'").fetchone():
                raise ValueError('Finish or discard the current practice test before restoring.')
            folder = active.parent / 'backups'
            folder.mkdir(exist_ok=True)
            safety = folder / ('SOSkuska-before-restore-' + datetime.now().strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex + '.sqlite3')
            with closing(readonly(active)) as current:
                snapshot(current, safety, check=check)
            for name in reversed(TABLES):
                check()
                target.execute(f'DELETE FROM "{name}"')
            for name in TABLES:
                check()
                if name == 'sqlite_sequence':
                    target.execute('DELETE FROM sqlite_sequence')
                target.execute(f'INSERT INTO "{name}" SELECT * FROM restored."{name}"')
            if target.execute('PRAGMA foreign_key_check').fetchone() is not None:
                raise ValueError('Restored data failed its reference check.')
            for name in TABLES:
                check()
                if target.execute(f'SELECT COUNT(*) FROM main."{name}"').fetchone() != target.execute(f'SELECT COUNT(*) FROM restored."{name}"').fetchone():
                    raise ValueError('Restored row counts do not match the validated backup.')
                for left,right in (('main','restored'),('restored','main')):
                    if target.execute(f'SELECT * FROM {left}."{name}" EXCEPT SELECT * FROM {right}."{name}"').fetchone() is not None:
                        raise ValueError('Restored records do not match the validated backup.')
            check()
            target.commit()
        except BaseException:
            target.rollback()
            raise
    return safety
