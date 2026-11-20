"""Flashcard CSV boundaries, transactions, concurrency and read-only workers."""
import csv
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'soskuska'))
from csv_import import MAX_BYTES, MAX_ROWS, ImportValidationError
from flashcard_csv_import import parse_csv, read_csv, template_text, validate_rows
from flashcard_csv_import_worker import run
from storage import Store, SCHEMA_VERSION


def contents(rows, header=('front', 'back')):
    output = io.StringIO(newline='')
    writer = csv.writer(output); writer.writerow(header); writer.writerows(rows)
    return output.getvalue()


class FormatTests(unittest.TestCase):
    def test_template_and_headers(self):
        self.assertEqual((Path(__file__).resolve().parents[1] / 'docs/examples/flashcards-template.csv').read_text(), template_text())
        self.assertTrue(parse_csv(template_text())['errors'])
        result = parse_csv(contents([[' Answer ', ' Question ']], [' BACK ', 'FRONT']))
        self.assertEqual(result['rows'][0]['fields'], ['Question', 'Answer'])
        for header in ['', 'front;back', 'front,front', 'front', 'front,back,extra', 'front,']:
            with self.subTest(header=header), self.assertRaises(ValueError): parse_csv(header)

    def test_unicode_multiline_bom_and_encoding(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'карточки.csv'
            path.write_bytes(b'\xef\xbb\xbf' + contents([['Český, русский\n日本語', 'Answer\nsecond line']]).encode())
            self.assertEqual(read_csv(path)['rows'][0]['fields'][0], 'Český, русский\n日本語')
            for data in [b'\xff', b'x' * (MAX_BYTES + 1)]:
                path.write_bytes(data)
                with self.assertRaises(ValueError): read_csv(path)
            with self.assertRaises(ValueError): read_csv(Path(folder))

    def test_lengths_controls_and_bad_rows(self):
        for front, back in [('', 'b'), ('a', ''), ('a'*2001, 'b'), ('a', 'b'*4001)]:
            result = parse_csv(contents([['valid', 'back'], [front, back]]))
            self.assertEqual(len(result['rows']), 1); self.assertIn('record 3', result['errors'][0])
        for value in ['\x00', '\x1b', '\x7f', '\ud800']:
            with self.assertRaises((ValueError, UnicodeError)): parse_csv(contents([[value, 'back']]))
        self.assertIn('Expected 2', parse_csv('front,back\na,b,c\n')['errors'][0])
        self.assertIn('Invalid CSV', parse_csv('front,back\n"unfinished')['errors'][0])
        self.assertFalse(parse_csv(contents([['a'*2000, 'b'*4000]]))['errors'])

    def test_duplicates_and_blank_rows(self):
        result = parse_csv(contents([['a', 'b'], [' a ', ' b '], ['A', 'b'], ['a', 'other'], ['', '']]))
        self.assertEqual(result['total'], 4); self.assertEqual(len(result['errors']), 1)
        self.assertIn('Duplicate of record 2', result['errors'][0])

    def test_limits_and_untrusted_payload(self):
        for count in [MAX_ROWS, MAX_ROWS + 1]:
            result = parse_csv(contents([[str(i), 'b'] for i in range(count)]))
            self.assertEqual(bool(result['errors']), count > MAX_ROWS)
        with self.assertRaises(ValueError): parse_csv('x'*(MAX_BYTES+1))
        for value in [None, [], 'abc', [{}]*501]:
            with self.assertRaises(ImportValidationError): validate_rows(value)
        for value in [None, {}, {'record':1,'fields':['a','b']}, {'record':2,'fields':['a',1]}]:
            self.assertTrue(validate_rows([value])[1])

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX-only input type')
    def test_fifo_not_opened(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'fifo'; os.mkfifo(path)
            with self.assertRaises(ValueError): read_csv(path)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'db.sqlite3'; self.store = Store(self.path); self.addCleanup(self.store.close)
        self.sid = self.store.create_subject('Subject'); self.did = self.store.create_deck(self.sid, '--Русский 日本語')
        self.name = self.store.deck(self.did)['name']
        self.source = self.path.with_name('cards.csv'); self.source.write_text(contents([['a','b'],['c','d']]), encoding='utf-8')
        self.rows = read_csv(self.source)['rows']

    def save(self, rows=None):
        return self.store.import_flashcards(self.did, self.rows if rows is None else rows, expected_deck_name=self.name)

    def test_bulk_due_and_reopen(self):
        rows = parse_csv(contents([[str(i),'back'] for i in range(500)]))['rows']
        result = self.save(rows); self.assertEqual(result, {'cards':500, 'deck':self.name})
        self.assertEqual(len(self.store.flashcards(self.did)), 500)
        self.assertEqual(len(self.store.due_flashcards(self.did)), 100)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM review_events').fetchone()[0], 0)
        self.assertEqual(self.store.db.execute('PRAGMA user_version').fetchone()[0], SCHEMA_VERSION)
        other = Store(self.path)
        try: self.assertEqual(len(other.flashcards(self.did)), 500)
        finally: other.close()

    def test_atomic_rollback_and_retry(self):
        self.store.db.execute("CREATE TRIGGER fail_import BEFORE INSERT ON flashcards WHEN NEW.front='c' BEGIN SELECT RAISE(ABORT,'full'); END")
        with self.assertRaises(sqlite3.Error): self.save()
        self.assertEqual(self.store.flashcards(self.did), [])
        self.store.db.execute('DROP TRIGGER fail_import'); self.save()
        self.assertEqual(len(self.store.flashcards(self.did)), 2)

    def test_duplicate_recheck_across_connections_and_beyond_ui_limit(self):
        for index in range(101):
            self.store.create_flashcard(self.did, f'Earlier {index}', 'Existing answer')
        other = Store(self.path)
        try: other.import_flashcards(self.did, self.rows[:1], expected_deck_name=self.name)
        finally: other.close()
        with self.assertRaises(ImportValidationError): self.save()
        self.assertEqual(len(self.store.flashcards(self.did)), 102)
        another = self.store.create_deck(self.sid, 'Other')
        self.store.import_flashcards(another, self.rows, expected_deck_name='Other')
        self.assertEqual(len(self.store.flashcards(another)), 2)
        with self.assertRaises(ImportValidationError): self.save([self.rows[1], self.rows[1]])

    def test_renamed_deleted_target_and_deleted_subject(self):
        self.store.update_deck(self.did, 'Renamed')
        with self.assertRaises(ImportValidationError): self.save()
        self.store.update_deck(self.did, self.name)
        self.store.delete_subject(self.sid)
        self.save(); self.assertEqual(len(self.store.flashcards(self.did)), 2)
        self.store.delete_deck(self.did)
        with self.assertRaises(ImportValidationError): self.save()

    def test_existing_schedule_and_history_preserved(self):
        cid = self.store.create_flashcard(self.did, 'old', 'answer')
        card = self.store.flashcard(cid)
        self.store.rate_flashcard(cid, 'Easy', card['revision'])
        before = self.store.flashcard(cid)
        history = [tuple(r) for r in self.store.db.execute('SELECT * FROM review_events')]
        self.save()
        self.assertEqual(before, self.store.flashcard(cid))
        self.assertEqual(history, [tuple(r) for r in self.store.db.execute('SELECT * FROM review_events')])

    def test_preview_is_readonly_and_missing_database_not_created(self):
        before = self.path.read_bytes()
        result = run('parse', self.path, self.source, self.did, self.name)
        self.assertFalse(result['errors']); self.assertEqual(self.path.read_bytes(), before)
        missing = self.path.with_name('missing.db')
        with self.assertRaises(ValueError): run('parse', missing, self.source, self.did, self.name)
        self.assertFalse(missing.exists())
        with patch.object(Store, '_migrate', side_effect=AssertionError('must not migrate')):
            self.assertFalse(run('parse', self.path, self.source, self.did, self.name)['errors'])

    def test_template_no_overwrite_and_protected_paths(self):
        out = self.path.with_name('template.csv'); run('template', self.path, out, self.did, self.name)
        self.assertEqual(out.read_text(), template_text())
        for path in [out, self.path, Path(str(self.path)+'-wal'), Path(str(self.path)+'.lock')]:
            with self.subTest(path=path), self.assertRaises((ValueError, FileExistsError)):
                run('template', self.path, path, self.did, self.name)
        self.assertEqual(out.read_text(), template_text())

    def test_worker_cli_and_known_commit_cleanup(self):
        worker = Path(__file__).resolve().parents[1]/'soskuska/flashcard_csv_import_worker.py'
        result = subprocess.run([sys.executable,str(worker),'parse',str(self.path),str(self.source),'--deck-id',str(self.did),f'--deck-name={self.name}'], capture_output=True, check=True, timeout=20)
        self.assertFalse(json.loads(result.stdout)['value']['errors'])
        payload = self.path.with_name('payload.json'); payload.write_text(json.dumps(self.rows), encoding='utf-8')
        original = Store.close
        def close_then_fail(store):
            original(store); raise OSError('cleanup failure')
        with patch.object(Store, 'close', close_then_fail):
            self.assertEqual(run('save',self.path,payload,self.did,self.name)['cards'], 2)
        self.assertEqual(len(self.store.flashcards(self.did)), 2)
