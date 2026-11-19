"""CSV format/limits, read-only preview and all-or-nothing question import."""
import csv
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch, Mock
from types import SimpleNamespace

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'soskuska'))
from csv_import import COLUMNS, MAX_BYTES, MAX_ROWS, ImportValidationError, parse_csv, read_csv, template_text
from csv_import_worker import run
from csv_import_panel import CsvImportPanel
from storage import Store, SCHEMA_VERSION


def csv_text(records,header=COLUMNS):
    output=io.StringIO(newline='');writer=csv.writer(output);writer.writerow(header)
    for record in records:writer.writerow([record.get(key,'') for key in header])
    return output.getvalue()


def question(**changes):
    values=dict(topic='Cells',prompt='What is a cell?',option_a='A',option_b='B',option_c='C',option_d='D',correct_option='B',difficulty='Medium',explanation='Because')
    values.update(changes);return values


class CsvFormatTests(unittest.TestCase):
    def test_template_is_header_only_and_has_no_sample_records(self):
        self.assertEqual(next(csv.reader(io.StringIO(template_text()))),list(COLUMNS))
        preview=parse_csv(template_text());self.assertFalse(preview['rows']);self.assertTrue(preview['errors'])
        self.assertEqual((Path(__file__).resolve().parents[1]/'docs/examples/questions-template.csv').read_text(),template_text())

    def test_unicode_bom_quoted_comma_and_multiline_text(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'日本語.csv'
            path.write_bytes(b'\xef\xbb\xbf'+csv_text([question(prompt='Český, русский\n第二行',explanation='Two\nlines')]).encode())
            preview=read_csv(path)
        self.assertFalse(preview['errors']);self.assertEqual(preview['rows'][0]['fields'][0],'Český, русский\n第二行')
        self.assertEqual(preview['rows'][0]['fields'][-1],'Two\nlines')

    def test_reordered_headers_optional_columns_and_case_normalization(self):
        header=['DIFFICULTY',' CORRECT_OPTION ',*['OPTION_'+k for k in 'DCBA'],'PROMPT']
        row=['easy',' b ','D','C','B','A','Question']
        output=io.StringIO();writer=csv.writer(output);writer.writerow(header);writer.writerow(row)
        preview=parse_csv(output.getvalue());self.assertFalse(preview['errors'])
        self.assertEqual(preview['rows'][0]['topic'],'');self.assertEqual(preview['rows'][0]['fields'][-3:],[1,'Easy',''])

    def test_invalid_headers_are_rejected(self):
        for text in ['', 'prompt,prompt\nx,y\n',';'.join(COLUMNS)+'\n','\n',','.join(COLUMNS)+',extra\n',','.join(COLUMNS[:-2])+'\n']:
            with self.subTest(text=text),self.assertRaises(ValueError):parse_csv(text)

    def test_bad_values_produce_record_errors_without_hiding_other_valid_rows(self):
        for changes in [dict(prompt=''),dict(prompt='x'*2001),dict(option_a=' b '),dict(correct_option='1'),dict(difficulty='Unknown'),dict(topic='x'*121),dict(explanation='x'*2001)]:
            preview=parse_csv(csv_text([question(),question(**changes)]))
            with self.subTest(changes=changes):
                self.assertTrue(any('record 3' in e for e in preview['errors']))
                self.assertTrue(preview['rows'])

    def test_wrong_cell_count_and_malformed_quotes_are_errors(self):
        preview=parse_csv(template_text()+'Cells,Question\n')
        self.assertIn('Expected',preview['errors'][0])
        preview=parse_csv(template_text()+'"unterminated')
        self.assertIn('Invalid CSV',preview['errors'][0])

    def test_control_characters_and_invalid_unicode_are_rejected(self):
        for text in ['\x00','\x1b','\ud800']:
            with self.assertRaises((ValueError,UnicodeError)):parse_csv(csv_text([question(prompt='Bad'+text)]))

    def test_blank_lines_ignored_and_row_limit_enforced(self):
        preview=parse_csv(template_text()+'\n,,,,,,,,\n'+csv_text([question()]).split('\n',1)[1]);self.assertEqual(preview['total'],1)
        preview=parse_csv(csv_text([question(prompt=f'Question {i}') for i in range(MAX_ROWS)]));self.assertEqual(len(preview['rows']),MAX_ROWS);self.assertFalse(preview['errors'])
        preview=parse_csv(csv_text([question(prompt=f'Question {i}') for i in range(MAX_ROWS+1)]));self.assertTrue(preview['errors'])

    def test_file_limit_and_non_utf8_input(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'file.csv'
            for content in [b'\xff',b'x'*(MAX_BYTES+1)]:
                p.write_bytes(content)
                with self.assertRaises(ValueError):read_csv(p)
            with self.assertRaises(ValueError):read_csv(Path(folder))

    @unittest.skipUnless(hasattr(os,'mkfifo'),'POSIX-only input type')
    def test_named_pipe_is_rejected_without_opening_it(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'pipe';os.mkfifo(p)
            with self.assertRaises(ValueError):read_csv(p)

    def test_within_file_duplicates_use_normalized_options_and_topic(self):
        preview=parse_csv(csv_text([question(topic='Ｃｅｌｌｓ'),question(topic=' cells ',option_a=' A ')]))
        self.assertTrue(any('Duplicate of record 2' in e for e in preview['errors']))
        preview=parse_csv(csv_text([question(),question(explanation='Different explanation')]))
        self.assertFalse(preview['errors'])


class CsvStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'db.sqlite3';self.store=Store(self.path);self.addCleanup(self.store.close)
        self.sid=self.store.create_subject('--Biology')
        self.rows=parse_csv(csv_text([question(),question(prompt='Second',topic='Other')]))['rows']

    def save(self,rows=None):
        return self.store.import_questions(self.sid,self.rows if rows is None else rows,expected_subject_name='--Biology')

    def counts(self):
        return tuple(self.store.db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ['subjects','topics','questions'])

    def test_atomic_import_reuses_subject_topics_and_preserves_history(self):
        tid=self.store.create_topic(self.sid,'Ｃｅｌｌｓ');self.store.add_session(45,self.sid,'--Biology')
        result=self.save();self.assertEqual(result['questions'],2);self.assertEqual(result['topics'],1)
        self.assertEqual(self.counts(),(1,2,2));self.assertEqual(self.store.seconds(),45)
        self.assertEqual(self.store.questions(self.sid)[0]['subject_id'],self.sid)
        self.assertEqual(self.store.db.execute("SELECT topic_id FROM questions WHERE prompt='What is a cell?'").fetchone()[0],tid)
        self.assertEqual(self.store.db.execute('PRAGMA user_version').fetchone()[0],SCHEMA_VERSION)

    def test_no_topic_does_not_create_a_placeholder_topic(self):
        rows=parse_csv(csv_text([question(topic='')]))['rows'];self.save(rows)
        self.assertEqual(self.counts(),(1,0,1));self.assertIsNone(self.store.questions(self.sid)[0]['topic_id'])

    def test_preflight_is_read_only_even_with_reserved_writer_lock(self):
        changes=self.store.db.total_changes;other=Store(self.path);before=self.path.read_bytes()
        try:
            other.db.execute('BEGIN IMMEDIATE')
            reader=Store.open_existing(self.path,readonly=True)
            try:self.assertFalse(reader.check_question_import(self.sid,self.rows,expected_subject_name='--Biology'))
            finally:reader.close()
            other.db.rollback()
        finally:other.close()
        self.assertEqual(self.store.db.total_changes,changes);self.assertEqual(self.path.read_bytes(),before)

    def test_preview_worker_does_not_modify_database_bytes(self):
        selected=Path(self.temp.name)/'questions.csv';selected.write_text(csv_text([question()]))
        before=self.path.read_bytes();mtime=self.path.stat().st_mtime_ns
        self.assertFalse(run('parse',self.path,selected,self.sid,'--Biology')['errors'])
        self.assertEqual(self.path.read_bytes(),before);self.assertEqual(self.path.stat().st_mtime_ns,mtime)

    def test_bad_api_rows_and_in_file_duplicates_never_partially_insert(self):
        for rows in [[],[self.rows[0],self.rows[0]],[self.rows[0],dict(self.rows[1],fields=['bad'])]]:
            with self.assertRaises(ImportValidationError):self.save(rows)
            self.assertEqual(self.counts(),(1,0,0))

    def test_existing_duplicate_rejects_entire_batch_and_reimport(self):
        self.save([self.rows[0]])
        with self.assertRaises(ImportValidationError) as exc:self.save()
        self.assertIn('already exists',' '.join(exc.exception.errors));self.assertEqual(self.counts(),(1,1,1))

    def test_concurrent_duplicate_after_preview_is_detected_under_write_lock(self):
        self.assertFalse(self.store.check_question_import(self.sid,self.rows,expected_subject_name='--Biology'))
        other=Store(self.path)
        try:other.import_questions(self.sid,[self.rows[1]],expected_subject_name='--Biology')
        finally:other.close()
        with self.assertRaises(ImportValidationError):self.save()
        self.assertEqual(self.counts(),(1,1,1))

    def test_renamed_and_deleted_subject_are_not_retargeted(self):
        with self.store.db:self.store.db.execute("UPDATE subjects SET name='Renamed',name_key='renamed' WHERE id=?",(self.sid,))
        with self.assertRaises(ImportValidationError):self.save()
        with self.store.db:self.store.db.execute('DELETE FROM subjects WHERE id=?',(self.sid,))
        with self.assertRaises(ImportValidationError):self.save()
        self.assertEqual(self.counts(),(0,0,0))

    def test_late_write_failure_rolls_back_questions_topics_and_sequences(self):
        before=list(self.store.db.execute('SELECT * FROM sqlite_sequence'))
        self.store.db.execute("CREATE TRIGGER fail_import BEFORE INSERT ON questions WHEN NEW.prompt='Second' BEGIN SELECT RAISE(ABORT,'disk full'); END")
        with self.assertRaises(sqlite3.Error):self.save()
        self.assertEqual(self.counts(),(1,0,0));self.assertEqual(list(self.store.db.execute('SELECT * FROM sqlite_sequence')),before)
        self.store.db.execute('DROP TRIGGER fail_import');self.assertEqual(self.save()['questions'],2)

    def test_snapshot_rows_do_not_depend_on_source_file_after_preview(self):
        source=Path(self.temp.name)/'questions.csv';source.write_text(csv_text([question()]))
        preview=read_csv(source);source.write_text('not CSV')
        self.assertEqual(self.save(preview['rows'])['questions'],1)

    def test_new_topic_uses_current_names_after_topic_rename(self):
        self.store.create_topic(self.sid,'Cells')
        with self.store.db:self.store.db.execute("UPDATE topics SET name='Renamed',name_key='renamed'")
        self.save([self.rows[0]]);self.assertEqual(self.counts(),(1,2,1))

    def test_different_explanation_or_topic_is_not_an_exact_duplicate(self):
        self.save([self.rows[0]])
        rows=parse_csv(csv_text([question(explanation='Different'),question(topic='Different')]))['rows']
        self.assertEqual(self.save(rows)['questions'],2)

    def test_existing_only_connections_never_create_or_migrate_a_database(self):
        path=Path(self.temp.name)/'missing.sqlite3'
        with self.assertRaises(ValueError):Store.open_existing(path)
        self.assertFalse(path.exists())
        with closing(sqlite3.connect(path)) as db:db.execute('PRAGMA user_version=5')
        before=path.read_bytes()
        for readonly in [False,True]:
            with self.assertRaises(ValueError):Store.open_existing(path,readonly=readonly)
        self.assertEqual(path.read_bytes(),before)

    def test_template_never_overwrites_existing_or_database_companion_files(self):
        target=Path(self.temp.name)/'template.csv'
        run('template',self.path,target,self.sid,'--Biology');self.assertEqual(target.read_text(),template_text())
        with self.assertRaises(FileExistsError):run('template',self.path,target,self.sid,'--Biology')
        for suffix in ['', '-journal','-wal','-shm','.lock']:
            with self.assertRaises(ValueError):run('template',self.path,Path(str(self.path)+suffix),self.sid,'--Biology')

    def test_template_write_failure_never_publishes_partial_file(self):
        target=Path(self.temp.name)/'template.csv'
        with patch('pathlib.Path.write_bytes',side_effect=OSError('disk full')),self.assertRaises(OSError):
            run('template',self.path,target,self.sid,'--Biology')
        self.assertFalse(target.exists())

    def test_maximum_batch_imports_every_record(self):
        rows=parse_csv(csv_text([question(prompt=f'Question {i}') for i in range(MAX_ROWS)]))['rows']
        self.assertEqual(self.save(rows)['questions'],MAX_ROWS)
        self.assertEqual(self.counts(),(1,1,MAX_ROWS))

    def test_committed_result_survives_connection_cleanup_error(self):
        payload=Path(self.temp.name)/'payload.json';payload.write_text(json.dumps(self.rows))
        real_close=self.store.close
        def fail_close():
            real_close();raise OSError('cleanup failed after commit')
        with patch('csv_import_worker.Store.open_existing',return_value=self.store),patch.object(self.store,'close',side_effect=fail_close):
            self.assertEqual(run('save',self.path,payload,self.sid,'--Biology')['questions'],2)
        with closing(sqlite3.connect(self.path)) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM questions').fetchone()[0],2)

    def test_concurrent_save_helpers_commit_once(self):
        payload=Path(self.temp.name)/'payload.json';payload.write_text(json.dumps(self.rows))
        worker=Path(__file__).resolve().parents[1]/'soskuska/csv_import_worker.py'
        command=[sys.executable,str(worker),'save',str(self.path),str(payload),'--subject-id',str(self.sid),'--subject-name=--Biology']
        processes=[subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for _ in range(2)]
        try:
            states=[json.loads(p.communicate(timeout=20)[0])['state'] for p in processes]
        finally:
            for p in processes:
                if p.poll() is None:p.kill()
                p.communicate(timeout=10)
        self.assertEqual(sorted(states),['done','invalid']);self.assertEqual(self.counts(),(1,2,2))

    def test_worker_cli_supports_subject_names_starting_with_dash(self):
        source=Path(self.temp.name)/'questions.csv';source.write_text(csv_text([question()]))
        worker=Path(__file__).resolve().parents[1]/'soskuska/csv_import_worker.py'
        base=[sys.executable,str(worker)]
        args=[str(self.path),str(source),'--subject-id',str(self.sid),'--subject-name=--Biology']
        result=subprocess.run([*base,'parse',*args],capture_output=True,check=True,timeout=15)
        preview=json.loads(result.stdout)['value'];self.assertFalse(preview['errors'])
        payload=Path(self.temp.name)/'payload.json';payload.write_text(json.dumps(preview['rows']))
        args[1]=str(payload)
        result=subprocess.run([*base,'save',*args],capture_output=True,check=True,timeout=15)
        self.assertEqual(json.loads(result.stdout)['value']['questions'],1)


class CsvSelectionTests(unittest.TestCase):
    def panel(self):
        panel=CsvImportPanel.__new__(CsvImportPanel)
        panel.process=None;panel.kind=None;panel.preview={'rows':[{'old':'batch'}],'errors':[]}
        panel.app=SimpleNamespace(store=Mock(),scroll=SimpleNamespace(_parent_canvas=Mock()))
        panel.app.store.subject.side_effect=sqlite3.OperationalError('database is locked')
        panel.bank=SimpleNamespace(subject_id=1,subject_snapshot={'id':1,'name':'Biology'},status=Mock())
        for field in ('details','errors','record_label','heading','status'):
            setattr(panel,field,Mock())
        panel.text=Mock();panel.controls=Mock();panel.launch=Mock()
        return panel

    def test_new_selection_consumes_old_preview_without_tk_database_read(self):
        panel=self.panel()
        with patch('csv_import_panel.filedialog.askopenfilename',return_value='/tmp/new.csv'):
            panel.choose()
        self.assertIsNone(panel.preview)
        panel.controls.assert_called_once()
        panel.launch.assert_called_once_with('parse','/tmp/new.csv')
        panel.app.store.subject.assert_not_called()
        panel.record_label.configure.assert_called_with(text='')
        panel.launch.reset_mock()
        panel.preview={'rows':[{'old':'batch'}],'errors':[]};panel.bank.subject_snapshot=None
        with patch('csv_import_panel.filedialog.askopenfilename',return_value='/tmp/new.csv'):
            panel.choose()
        self.assertIsNone(panel.preview);panel.launch.assert_not_called()
        self.assertIn('Reload',panel.status.configure.call_args.kwargs['text'])

    def test_open_captures_displayed_subject_without_tk_database_read(self):
        panel=self.panel();panel.cancel=Mock();panel.grid=Mock()
        panel.open()
        self.assertEqual(panel.subject_id,1);self.assertEqual(panel.subject_name,'Biology')
        panel.app.store.subject.assert_not_called()


if __name__=='__main__':unittest.main()
