"""Regression coverage for the four Astra 6.2 findings recorded in docs."""
import json
import subprocess
import sqlite3
import sys
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'soskuska'))
from storage import Store
from question_bank import QuestionBankPage
from scheduled_backups import ScheduledBackups


class ReviewStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        path=Path(self.temp.name)/'study.sqlite3'
        self.one=Store(path);self.two=Store(path)
        self.addCleanup(self.one.close);self.addCleanup(self.two.close)
        self.sid=self.one.create_subject('Subject','Original','2026-12-20')

    def test_subject_draft_does_not_overwrite_concurrent_description_or_exam(self):
        original=self.one.subject(self.sid)
        self.two.update_subject(self.sid,'Subject','Latest description','2026-12-21')
        # Same-second timestamps must not bypass actual-content checks.
        self.two.db.execute('UPDATE subjects SET updated_at=? WHERE id=?',(original['updated_at'],self.sid));self.two.db.commit()
        with self.assertRaisesRegex(ValueError,'changed in another window'):
            self.one.update_subject(self.sid,'My rename',original['description'],original['exam_date'],expected_state=original)
        current=self.two.subject(self.sid)
        self.assertEqual((current['name'],current['description'],current['exam_date']),('Subject','Latest description','2026-12-21'))
        self.one.update_subject(self.sid,'Merged rename',current['description'],current['exam_date'],expected_state=current)
        self.assertEqual(self.two.subject(self.sid)['name'],'Merged rename')

    def test_question_deletion_requires_reconfirmation_after_changed_answers(self):
        qid=self.one.create_question(self.sid,'Question',['a','b','c','d'],0)
        old=self.one.question(qid)
        self.two.update_question(qid,'Question',['one','two','three','four'],2,explanation='New explanation')
        self.assertFalse(self.one.delete_question(qid,expected_state=old))
        latest=self.two.question(qid)
        self.assertEqual(latest['explanation'],'New explanation')
        self.assertTrue(self.one.delete_question(qid,expected_state=latest))
        self.assertIsNone(self.two.question(qid))

    def test_topic_rename_invalidates_delete_warning_without_removing_questions(self):
        tid=self.one.create_topic(self.sid,'Original topic')
        qid=self.one.create_question(self.sid,'Question',['a','b','c','d'],0,topic_id=tid)
        old=self.one.topic(tid);self.two.update_topic(tid,'Updated topic')
        self.assertFalse(self.one.delete_topic(tid,expected_state=old))
        self.assertEqual(self.one.question(qid)['topic_id'],tid)
        self.assertTrue(self.one.delete_topic(tid,expected_state=self.one.topic(tid)))
        self.assertIsNone(self.two.question(qid)['topic_id'])

    def test_failed_delete_write_preserves_confirmed_content_for_retry(self):
        qid=self.one.create_question(self.sid,'Question',['a','b','c','d'],0)
        snapshot=self.one.question(qid)
        self.one.db.execute("CREATE TRIGGER no_delete BEFORE DELETE ON questions BEGIN SELECT RAISE(ABORT,'full'); END")
        with self.assertRaises(sqlite3.Error):self.one.delete_question(qid,expected_state=snapshot)
        self.assertIsNotNone(self.two.question(qid))
        self.one.db.execute('DROP TRIGGER no_delete')
        self.assertTrue(self.one.delete_question(qid,expected_state=snapshot))


class DeleteRearmTests(unittest.TestCase):
    def test_disappearing_record_clears_old_confirmation_and_does_not_retry_delete(self):
        page=QuestionBankPage.__new__(QuestionBankPage)
        page.pending_delete=('question',42,dict(id=42));page.subject_id=1
        page.app=SimpleNamespace(store=Mock())
        page.app.store.delete_question.return_value=False;page.app.store.question.return_value=None
        page.delete_panel=Mock();page.refresh=Mock();page.status=Mock()
        page.confirm_delete()
        self.assertIsNone(page.pending_delete);page.delete_panel.grid_remove.assert_called()
        page.confirm_delete();page.app.store.delete_question.assert_called_once()


class BackupReconciliationTests(unittest.TestCase):
    def panel(self):
        panel=ScheduledBackups.__new__(ScheduledBackups)
        panel.app=SimpleNamespace(store=SimpleNamespace(path='/tmp/unused'),data_restoring=False,
            settings_page=SimpleNamespace(backups=SimpleNamespace(busy=False,pending=None)),
            question_bank=SimpleNamespace(importer=SimpleNamespace(saving=False)),
            flashcard_page=SimpleNamespace(importer=SimpleNamespace(saving=False)),backup_notice=Mock())
        panel.closed=False;panel.process=None;panel.output=None;panel.next_check=0
        panel.waiting_elsewhere=False;panel.backup_failed=False
        panel.save_button=Mock();panel.retry_button=Mock();panel.last=Mock();panel.runtime=Mock()
        panel.after=Mock();panel.launch=Mock()
        return panel

    def test_external_success_clears_superseded_failure_without_another_write(self):
        panel=self.panel();panel.complete('error',None)
        self.assertTrue(panel.backup_failed)
        saved=dict(enabled=True,invalid=False,last_day=date.today().isoformat(),last_path='/tmp/success.sqlite3')
        panel.retry()
        with patch('scheduled_backups.load_config',return_value=saved):panel.poll()
        self.assertFalse(panel.backup_failed);panel.app.backup_notice.grid_remove.assert_called_once()
        self.assertIn('success.sqlite3',panel.last.configure.call_args.kwargs['text'])
        self.assertIn('Daily backup saved',panel.runtime.configure.call_args.kwargs['text'])
        panel.launch.assert_not_called()

    def test_real_external_worker_success_reconciles_failed_window(self):
        from automatic_backup import load_config,save_config
        with tempfile.TemporaryDirectory(prefix='soskuska-external-success-') as directory:
            path=Path(directory)/'study.sqlite3';store=Store(path)
            try:
                destination=Path(directory)/'backups';destination.mkdir()
                save_config(path,True,str(destination),load_config(path)['token'])
                panel=self.panel();panel.app.store.path=path;panel.complete('error',None)
                command=[sys.executable,str(Path(__file__).resolve().parents[1]/'soskuska/backup_worker.py'),'automatic',str(path)]
                with tempfile.TemporaryFile() as output:
                    subprocess.run(command,stdout=output,stderr=subprocess.DEVNULL,check=True,timeout=15)
                    output.seek(0);result=json.loads(output.read())
                self.assertEqual(result[0],'done');self.assertEqual(result[1]['state'],'created')
                panel.retry();panel.poll()
                self.assertFalse(panel.backup_failed);panel.launch.assert_not_called()
                self.assertEqual(len(list(destination.glob('*.sqlite3'))),1)
                panel.app.backup_notice.grid_remove.assert_called_once()
            finally:store.close()

    def test_older_or_invalid_receipt_does_not_clear_unresolved_failure(self):
        for saved in [dict(enabled=False,invalid=False,last_day=(date.today()-timedelta(days=1)).isoformat(),last_path='/tmp/old.sqlite3'),
                      dict(enabled=False,invalid=True,last_day=None,last_path='')]:
            with self.subTest(saved=saved):
                panel=self.panel();panel.complete('error',None);panel.retry()
                with patch('scheduled_backups.load_config',return_value=saved):panel.poll()
                self.assertTrue(panel.backup_failed);panel.app.backup_notice.grid_remove.assert_not_called()

    def test_read_failure_keeps_failure_notice_and_retries_without_duplicate_job(self):
        panel=self.panel();panel.complete('error',None);panel.retry()
        with patch('scheduled_backups.load_config',side_effect=OSError('read')):panel.poll()
        self.assertTrue(panel.backup_failed);panel.launch.assert_not_called()
        panel.app.backup_notice.grid_remove.assert_not_called();panel.after.assert_called_once()


if __name__=='__main__':unittest.main()
