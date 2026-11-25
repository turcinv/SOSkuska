"""Conversation transactions, owner isolation, interruption, backup and migration."""
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'soskuska'))
from storage import Store, SCHEMA_VERSION
from backup import create_backup, PreparedBackup, restore_backup
from tutor import chat_messages


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'study.db';self.store=Store(self.path);self.addCleanup(self.store.close)

    def begin(self,cid=None,revision=0,prompt='Český, русский 日本語?',endpoint='http://127.0.0.1:11434',model='study'):
        return self.store.begin_tutor_turn(cid,endpoint,model,prompt,'Russian',expected_revision=revision)

    def finish(self,saved,answer='Answer',status='completed'):
        return self.store.finish_tutor_turn(saved['id'],saved['turn_id'],answer,status,expected_revision=saved['revision'])

    def test_new_empty_database_has_no_seeded_conversations(self):
        self.assertEqual(self.store.tutor_conversations(),[])
        self.assertEqual(self.store.db.execute('PRAGMA user_version').fetchone()[0],SCHEMA_VERSION)

    def test_completed_unicode_chat_reopens_with_same_owner_and_context(self):
        saved=self.begin();revision=self.finish(saved,'Ответ\nSecond line')
        other=Store(self.path)
        try:chat=other.tutor_conversation(saved['id'])
        finally:other.close()
        self.assertEqual(chat['revision'],revision);self.assertEqual(chat['model'],'study')
        self.assertEqual(chat['turns'][0]['answer'],'Ответ\nSecond line')
        messages=chat_messages(chat['turns'],'Continue')
        self.assertEqual([m['role'] for m in messages],['system','user','assistant','user'])

    def test_pending_survives_reopen_without_automatic_recovery(self):
        saved=self.begin();other=Store(self.path)
        try:self.assertEqual(other.tutor_conversation(saved['id'])['turns'][0]['status'],'pending')
        finally:other.close()
        with self.assertRaises(ValueError):self.begin(saved['id'],saved['revision'])
        self.assertEqual(chat_messages(self.store.tutor_conversation(saved['id'])['turns'],'Continue')[-1]['content'],'Continue')
        self.assertEqual(len(chat_messages(self.store.tutor_conversation(saved['id'])['turns'],'Continue')),2)

    def test_terminal_partial_statuses_are_saved_but_excluded_from_context(self):
        for status in ['stopped','failed','interrupted']:
            saved=self.begin();self.finish(saved,'Partial',status)
            turns=self.store.tutor_conversation(saved['id'])['turns']
            self.assertEqual(turns[0]['status'],status);self.assertEqual(turns[0]['answer'],'Partial')
            self.assertEqual(len(chat_messages(turns,'Next')),2)

    def test_retry_is_idempotent_and_owner_cannot_change(self):
        saved=self.begin();revision=self.finish(saved)
        self.assertEqual(self.finish(saved),revision)
        for owner in [dict(endpoint='http://127.0.0.1:11435'),dict(model='other')]:
            with self.subTest(owner=owner),self.assertRaises(ValueError):self.begin(saved['id'],revision,**owner)
        next_turn=self.begin(saved['id'],revision,prompt='Next')
        self.assertEqual(len(self.store.tutor_conversation(saved['id'])['turns']),2)
        self.assertEqual(next_turn['revision'],revision+1)

    def test_conflicting_window_cannot_overwrite_recovery_or_delete(self):
        saved=self.begin();other=Store(self.path)
        try:
            revision=other.finish_tutor_turn(saved['id'],saved['turn_id'],'','interrupted',expected_revision=saved['revision'])
            with self.assertRaises(ValueError):self.finish(saved)
            with self.assertRaises(ValueError):self.store.delete_tutor_conversation(saved['id'],expected_revision=saved['revision'])
            other.delete_tutor_conversation(saved['id'],expected_revision=revision)
        finally:other.close()
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM tutor_turns').fetchone()[0],0)
        with self.assertRaises(ValueError):self.finish(saved)
        with self.assertRaises(ValueError):self.store.tutor_conversation(saved['id'])

    def test_failed_initial_write_does_not_leave_empty_chat(self):
        self.store.db.execute("CREATE TRIGGER fail_turn BEFORE INSERT ON tutor_turns BEGIN SELECT RAISE(ABORT,'disk full'); END")
        with self.assertRaises(sqlite3.Error):self.begin()
        self.assertEqual(self.store.tutor_conversations(),[])
        self.store.db.execute('DROP TRIGGER fail_turn');self.begin()
        self.assertEqual(len(self.store.tutor_conversations()),1)

    def test_failed_terminal_write_is_atomic_and_retryable(self):
        saved=self.begin()
        self.store.db.execute("CREATE TRIGGER fail_finish BEFORE UPDATE ON tutor_conversations BEGIN SELECT RAISE(ABORT,'disk full'); END")
        with self.assertRaises(sqlite3.Error):self.finish(saved)
        chat=self.store.tutor_conversation(saved['id'])
        self.assertEqual(chat['revision'],saved['revision']);self.assertEqual(chat['turns'][0]['status'],'pending')
        self.assertEqual(chat['turns'][0]['answer'],'')
        self.store.db.execute('DROP TRIGGER fail_finish');self.finish(saved)

    def test_twelve_turn_limit_and_history_paging(self):
        saved=self.begin()
        for index in range(12):
            revision=self.finish(saved)
            if index<11:saved=self.begin(saved['id'],revision,prompt=str(index))
        with self.assertRaises(ValueError):self.begin(saved['id'],revision)
        for index in range(24):self.begin(prompt=str(index))
        first=self.store.tutor_conversations();second=self.store.tutor_conversations(20)
        self.assertEqual(len(first),21);self.assertEqual(len(second),5)
        self.assertFalse({r['id'] for r in first[:20]} & {r['id'] for r in second})

    def test_invalid_fields_do_not_write(self):
        for prompt in ['', 'x'*4001, 'bad\x00']:
            with self.assertRaises(ValueError):self.begin(prompt=prompt)
        self.assertEqual(self.store.tutor_conversations(),[])
        saved=self.begin()
        for answer,status in [('x'*16001,'completed'),('x','pending'),('\x00','failed')]:
            with self.assertRaises(ValueError):self.finish(saved,answer,status)
        self.assertEqual(self.store.tutor_conversation(saved['id'])['turns'][0]['status'],'pending')

    def test_backups_roundtrip_completed_and_pending_chats(self):
        saved=self.begin();self.finish(saved);pending=self.begin(prompt='Interrupted request')
        backup=self.path.with_name('backup.db');create_backup(self.path,backup)
        prepared=PreparedBackup(backup,self.path)
        try:
            self.store.delete_tutor_conversation(saved['id'],expected_revision=2)
            self.store.close();restore_backup(self.path,prepared)
        finally:prepared.close()
        reopened=Store(self.path)
        try:
            self.assertEqual(reopened.tutor_conversation(saved['id'])['turns'][0]['answer'],'Answer')
            self.assertEqual(reopened.tutor_conversation(pending['id'])['turns'][0]['status'],'pending')
        finally:reopened.close()

    def test_title_truncation_at_space_still_roundtrips_backup(self):
        saved=self.begin(prompt='a'*79+' b');self.finish(saved)
        self.assertEqual(self.store.tutor_conversation(saved['id'])['title'],'a'*79)
        backup=self.path.with_name('title.db');create_backup(self.path,backup)
        prepared=PreparedBackup(backup,self.path);prepared.close()

    def test_backup_rejects_malformed_chat_states(self):
        saved=self.begin();self.finish(saved)
        for sql in ["UPDATE tutor_conversations SET endpoint='http://user:secret@localhost'", "UPDATE tutor_conversations SET title=''", "UPDATE tutor_conversations SET revision=9223372036854775807", "UPDATE tutor_turns SET position=3", "UPDATE tutor_turns SET language='Other'", "UPDATE tutor_turns SET status='pending'"]:
            with self.subTest(sql=sql):
                backup=self.path.with_name('bad.db');backup.unlink(missing_ok=True);create_backup(self.path,backup)
                with closing(sqlite3.connect(backup)) as db,db:db.execute(sql)
                with self.assertRaises(ValueError):PreparedBackup(backup,self.path)


class MigrationTests(unittest.TestCase):
    def fixture(self,path):
        db=sqlite3.connect(path)
        db.executescript((Path(__file__).parent/'fixtures/schema_v6.sql').read_text())
        db.execute("INSERT INTO subjects(name,name_key) VALUES('Keep','keep')");db.commit();db.close()

    def test_schema_six_migration_preserves_saved_rows_and_preferences(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'old.db';self.fixture(path)
            store=Store(path)
            try:
                self.assertEqual(store.subjects()[0]['name'],'Keep');self.assertEqual(store.preferences()['focus_minutes'],15)
                self.assertEqual(store.tutor_conversations(),[])
                self.assertEqual(store.db.execute('PRAGMA user_version').fetchone()[0],SCHEMA_VERSION)
            finally:store.close()

    def test_failed_migration_rolls_back_schema_and_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'old.db';self.fixture(path)
            db=sqlite3.connect(path)
            db.set_authorizer(lambda action,name,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_CREATE_TABLE and name=='tutor_turns' else sqlite3.SQLITE_OK)
            with patch('storage.sqlite3.connect',return_value=db),self.assertRaises(sqlite3.Error):Store(path)
            with closing(sqlite3.connect(path)) as check:
                self.assertEqual(check.execute('PRAGMA user_version').fetchone()[0],6)
                self.assertIsNone(check.execute("SELECT name FROM sqlite_schema WHERE name='tutor_conversations'").fetchone())
                self.assertEqual(check.execute('SELECT name FROM subjects').fetchone()[0],'Keep')


class HistoryUiTests(unittest.TestCase):
    def page(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        from tutor_page import TutorPage
        page=TutorPage.__new__(TutorPage)
        page.app=SimpleNamespace(store=Mock());page.task=None;page.unsaved_reply=False
        page.history_offset=0;page.history_has_next=True
        page.history_rows={'1 · First':{'id':1,'revision':1}};page.pending_delete=None
        page.history_choice=Mock();page.history_choice.get.return_value='1 · First'
        page.history_menu=Mock();page.delete_button=Mock();page.status=Mock();page.feedback=Mock();page.controls=Mock()
        return page

    def test_failed_next_page_read_keeps_displayed_offset_and_rows(self):
        page=self.page();page.app.store.tutor_conversations.side_effect=sqlite3.OperationalError('busy')
        before=page.history_rows.copy();page.history_page(1)
        self.assertEqual(page.history_offset,0);self.assertEqual(page.history_rows,before)
        page.app.store.tutor_conversations.assert_called_once_with(20)

    def test_empty_deleted_last_page_returns_to_first_page(self):
        page=self.page();page.history_offset=20
        page.app.store.tutor_conversations.side_effect=[[],[{'id':1,'title':'First'}]]
        page.refresh_history()
        self.assertEqual(page.history_offset,0);self.assertFalse(page.history_has_next)
        self.assertEqual(list(page.history_rows),['1 · First'])

    def test_discard_unsaved_preserves_next_prompt_draft(self):
        from unittest.mock import Mock
        page=self.page();page.unsaved_reply=True;page.pending_discard=True
        page.prompt=Mock();page.prompt.get.return_value='Keep next question'
        page.new_chat=Mock();page.discard_button=Mock();page.turns=[{'answer':'Copy me'}]
        page.discard_unsaved()
        page.prompt.insert.assert_called_once_with('1.0','Keep next question')
        self.assertFalse(page.unsaved_reply);self.assertEqual(page.turns,[])
