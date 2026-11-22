"""Daily schedule consent, atomic settings, concurrency, process and data safety."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'soskuska'))
from storage import Store
from automatic_backup import load_config,save_config,config_path,config_lease,perform_backup,due
from backup import PreparedBackup,create_backup,protect_path


class AutomaticBackupTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.path=self.root/'study.sqlite3'
        self.folder=self.root/'Сохранённые zálohy';self.folder.mkdir()
        self.store=Store(self.path);self.addCleanup(self.store.close)
        self.sid=self.store.create_subject('Keep content')
    def enable(self):return save_config(self.path,True,str(self.folder),load_config(self.path)['token'])
    def test_disabled_default_creates_no_config_or_backup(self):
        self.assertFalse(load_config(self.path)['enabled']);self.assertFalse(config_path(self.path).exists())
        self.assertEqual(perform_backup(self.path),dict(state='skipped'));self.assertEqual(list(self.folder.iterdir()),[])
    def test_daily_backup_roundtrip_and_one_receipt_per_day(self):
        self.enable();result=perform_backup(self.path)
        self.assertEqual(result['state'],'created');self.assertTrue(Path(result['path']).is_file())
        prepared=PreparedBackup(result['path'],self.path);prepared.close()
        self.assertEqual(perform_backup(self.path)['state'],'skipped')
        self.assertEqual(len(list(self.folder.iterdir())),1)
        self.assertEqual(load_config(self.path)['last_day'],date.today().isoformat())
    def test_stale_save_does_not_undo_other_window_or_success_receipt(self):
        old=load_config(self.path);self.enable()
        with self.assertRaisesRegex(ValueError,'changed'):save_config(self.path,False,'',old['token'])
        before=load_config(self.path);perform_backup(self.path)
        updated=save_config(self.path,False,str(self.folder),before['token'])
        self.assertFalse(updated['enabled']);self.assertEqual(updated['last_day'],date.today().isoformat())
    def test_schedule_changes_and_worker_respect_exclusive_lease(self):
        self.enable()
        with config_lease(self.path):
            self.assertEqual(perform_backup(self.path)['state'],'busy')
            with self.assertRaises(ValueError):save_config(self.path,False,'',load_config(self.path)['token'])
        self.assertEqual(list(self.folder.iterdir()),[])
    def test_unavailable_folder_failure_preserves_receipt_and_retry(self):
        self.enable();self.folder.rmdir()
        with self.assertRaisesRegex(ValueError,'unavailable'):perform_backup(self.path)
        self.assertIsNone(load_config(self.path)['last_day']);self.folder.mkdir()
        self.assertEqual(perform_backup(self.path)['state'],'created')
    def test_publish_failure_after_backup_never_deletes_published_file(self):
        self.enable()
        with patch('automatic_backup.publish_config',side_effect=OSError('full')):
            with self.assertRaises(OSError):perform_backup(self.path)
        files=list(self.folder.iterdir());self.assertEqual(len(files),1)
        self.assertIsNone(load_config(self.path)['last_day'])
        perform_backup(self.path);self.assertTrue(files[0].is_file());self.assertEqual(len(list(self.folder.iterdir())),2)
    def test_failed_config_replace_keeps_saved_policy(self):
        self.enable();before=config_path(self.path).read_bytes()
        with patch('automatic_backup.os.replace',side_effect=OSError('full')):
            with self.assertRaises(OSError):save_config(self.path,False,'',load_config(self.path)['token'])
        self.assertEqual(config_path(self.path).read_bytes(),before)
        self.assertFalse(list(self.root.glob('.soskuska-plan-*')))
    def test_invalid_settings_disable_automation_and_require_explicit_repair(self):
        config_path(self.path).write_text('{broken',encoding='utf-8')
        saved=load_config(self.path);self.assertTrue(saved['invalid']);self.assertFalse(saved['enabled'])
        self.assertEqual(perform_backup(self.path)['state'],'skipped')
        repaired=save_config(self.path,False,'',saved['token']);self.assertFalse(repaired['invalid'])
    def test_validation_rejects_relative_missing_and_control_paths(self):
        for enabled,directory in [(True,''),(True,'relative'),(False,'relative'),(True,str(self.folder)+'\n')]:
            with self.subTest(directory=directory),self.assertRaises(ValueError):save_config(self.path,enabled,directory,'missing')
        self.assertFalse(config_path(self.path).exists())
    def test_new_folder_and_disable_preserve_daily_receipt(self):
        self.enable();perform_backup(self.path);current=load_config(self.path)
        disabled=save_config(self.path,False,str(self.folder),current['token'])
        self.assertEqual(disabled['last_day'],current['last_day'])
        changed=save_config(self.path,True,str(self.root),disabled['token'])
        self.assertEqual(changed['last_day'],current['last_day']);self.assertFalse(due(changed,date.today()))
    def test_future_receipt_does_not_create_repeat_backups_after_clock_rollback(self):
        config=dict(enabled=True,invalid=False,last_day=(date.today()+timedelta(days=1)).isoformat())
        self.assertFalse(due(config,date.today()))
    def test_machine_plan_and_lock_cannot_be_used_as_export_outputs(self):
        for suffix in ('.backup-plan.json','.backup-plan.lock'):
            with self.assertRaises(ValueError):protect_path(Path(str(self.path)+suffix),self.path)
    def test_backups_do_not_transfer_machine_specific_opt_in(self):
        self.enable();result=perform_backup(self.path);copy=Path(result['path'])
        self.assertFalse(config_path(copy).exists());self.assertFalse(load_config(copy)['enabled'])
    def test_fresh_worker_and_two_processes_do_not_duplicate_backups(self):
        self.enable();command=[sys.executable,str(Path(__file__).resolve().parents[1]/'soskuska/backup_worker.py'),'automatic',str(self.path)]
        results=[]
        with tempfile.TemporaryFile() as one,tempfile.TemporaryFile() as two:
            children=[subprocess.Popen(command,stdout=out,stderr=subprocess.DEVNULL) for out in (one,two)]
            for child in children:self.assertEqual(child.wait(timeout=15),0)
            for out in (one,two):out.seek(0);results.append(json.loads(out.read()))
        self.assertEqual(len(list(self.folder.iterdir())),1)
        self.assertTrue(any(row[0]=='done' and row[1]['state']=='created' for row in results))
    def test_symlink_and_hardlinked_plan_are_rejected(self):
        if sys.platform=='win32':self.skipTest('Symlink permissions differ on hosted Windows')
        target=self.root/'unrelated';target.write_text('private')
        config_path(self.path).symlink_to(target)
        with self.assertRaises(ValueError):save_config(self.path,True,str(self.folder),'missing')
        self.assertEqual(target.read_text(),'private')

    def test_invalid_receipt_unicode_and_deep_json_disable_safely(self):
        self.enable();config=load_config(self.path)
        raw={key:config[key] for key in ('enabled','directory','last_day','last_path','plan_id')}
        raw['last_path']='/bad\ud800'
        config_path(self.path).write_text(json.dumps(raw),encoding='utf-8')
        self.assertTrue(load_config(self.path)['invalid'])
        config_path(self.path).write_text('['*6000+'0'+']'*6000,encoding='utf-8')
        self.assertTrue(load_config(self.path)['invalid'])

    def test_unicode_receipt_encoding_has_room_for_long_valid_paths(self):
        from automatic_backup import config_bytes,MAX_CONFIG_BYTES
        self.enable();config=load_config(self.path)
        directory='/'+'/'.join(['🌟'*35]*20)
        encoded=config_bytes(dict(config,directory=directory,last_path=directory+'/backup.sqlite3'))
        self.assertLess(len(encoded),MAX_CONFIG_BYTES)

    def test_resolved_control_character_folder_fails_before_publication(self):
        if sys.platform=='win32':self.skipTest('Windows forbids control characters in folder names')
        target=self.root/'bad\nfolder';target.mkdir()
        alias=self.root/'alias';alias.symlink_to(target,target_is_directory=True)
        save_config(self.path,True,str(alias),load_config(self.path)['token'])
        with self.assertRaises(ValueError):perform_backup(self.path)
        self.assertFalse(list(target.iterdir()));self.assertFalse(load_config(self.path)['invalid'])

if __name__=='__main__':unittest.main()
