"""Validated, atomic, isolated preferences and migration from frozen schema 5."""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'soskuska'))
from preferences import DEFAULTS, preference_fields
from storage import Store, SCHEMA_VERSION


class PreferencesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'prefs.sqlite3'
        self.store = Store(self.path)
        self.addCleanup(self.store.close)

    def fields(self, **changes):
        return dict(DEFAULTS, **changes)

    def test_defaults_do_not_seed_study_records_or_connect(self):
        with patch('socket.create_connection', side_effect=AssertionError('Unexpected network')):
            saved = self.store.preferences()
        self.assertEqual({k:saved[k] for k in DEFAULTS}, DEFAULTS)
        self.assertEqual(saved['revision'], 0)
        self.assertFalse(saved['invalid'])
        self.assertEqual(self.store.summary()['seconds'], 0)
        self.assertEqual(self.store.subjects(), [])
        self.assertEqual(self.store.practice_history(), [])
        self.assertEqual(self.store.decks(), [])

    def test_roundtrip_normalizes_endpoint_and_preserves_unicode_model(self):
        fields=self.fields(focus_minutes=25,daily_goal_minutes=120,ollama_endpoint=' HTTP://LOCALHOST:11434/ ',
                           ollama_model='  study-модель:latest  ',answer_language='Russian')
        saved=self.store.save_preferences(fields,expected_revision=0)
        self.assertEqual(saved['ollama_endpoint'],'http://localhost:11434')
        self.assertEqual(saved['ollama_model'],'study-модель:latest')
        other=Store(self.path)
        try:self.assertEqual(other.preferences(),saved)
        finally:other.close()

    def test_invalid_values_never_partially_write(self):
        before=self.store.preferences()
        cases=[dict(focus_minutes=n) for n in [0,181,True,15.5,'15']]
        cases += [dict(daily_goal_minutes=n) for n in [0,1441,True,1.5]]
        cases += [dict(ollama_endpoint=n) for n in ['ftp://host','http://u:p@host','http://host/path','http://host:0']]
        cases += [dict(ollama_model=n) for n in ['x'*201,'abc\ndef',chr(0xd800)]]
        cases += [dict(answer_language='French')]
        for change in cases:
            with self.subTest(change=repr(change)),self.assertRaises(ValueError):
                self.store.save_preferences(self.fields(**change),expected_revision=0)
            self.assertEqual(self.store.preferences(),before)

    def test_stale_window_cannot_replace_new_preferences(self):
        other=Store(self.path)
        try:
            stale=self.store.preferences()
            newer=other.save_preferences(self.fields(daily_goal_minutes=90),expected_revision=0)
            with self.assertRaisesRegex(ValueError,'changed in another window'):
                self.store.save_preferences(self.fields(focus_minutes=40),expected_revision=stale['revision'])
            self.assertEqual(self.store.preferences(),newer)
            saved=self.store.save_preferences(self.fields(focus_minutes=40,daily_goal_minutes=90),expected_revision=newer['revision'])
            self.assertEqual(saved['revision'],2)
        finally:other.close()

    def test_failed_write_rolls_back_all_fields_and_revision(self):
        self.store.db.execute("CREATE TRIGGER fail_pref BEFORE UPDATE ON preferences BEGIN SELECT RAISE(ABORT,'disk full'); END")
        with self.assertRaises(sqlite3.Error):
            self.store.save_preferences(self.fields(focus_minutes=30,daily_goal_minutes=120),expected_revision=0)
        self.assertEqual(self.store.preferences()['revision'],0)
        self.assertEqual(self.store.preferences()['focus_minutes'],15)
        self.store.db.execute('DROP TRIGGER fail_pref')
        self.assertEqual(self.store.save_preferences(self.fields(focus_minutes=30),expected_revision=0)['revision'],1)

    def test_return_does_not_require_postcommit_read(self):
        with patch.object(self.store,'preferences',side_effect=sqlite3.OperationalError('locked')):
            saved=self.store.save_preferences(self.fields(focus_minutes=20),expected_revision=0)
        self.assertEqual(saved,self.store.preferences())

    def test_invalid_saved_values_use_safe_defaults_without_automatic_rewrite(self):
        with self.store.db:
            self.store.db.execute("UPDATE preferences SET ollama_endpoint='http://user:secret@host',answer_language='Unknown'")
        changes=self.store.db.total_changes
        with patch('socket.create_connection',side_effect=AssertionError('Unexpected network')):
            saved=self.store.preferences()
        self.assertTrue(saved['invalid'])
        self.assertEqual(saved['ollama_endpoint'],DEFAULTS['ollama_endpoint'])
        self.assertEqual(self.store.db.total_changes,changes)
        repaired=self.store.save_preferences(self.fields(),expected_revision=saved['revision'])
        self.assertFalse(repaired['invalid'])
        self.assertFalse(self.store.preferences()['invalid'])

    def test_missing_preference_row_can_be_repaired_explicitly(self):
        with self.store.db:self.store.db.execute('DELETE FROM preferences')
        self.assertTrue(self.store.preferences()['invalid'])
        saved=self.store.save_preferences(self.fields(),expected_revision=0)
        self.assertEqual(self.store.preferences(),saved)

    def test_preferences_are_isolated_by_database_path(self):
        self.store.save_preferences(self.fields(daily_goal_minutes=100),expected_revision=0)
        other=Store(Path(self.temp.name)/'other.sqlite3')
        try:self.assertEqual(other.preferences()['daily_goal_minutes'],60)
        finally:other.close()

    def test_singleton_and_numeric_constraints(self):
        for sql in ['UPDATE preferences SET focus_minutes=0','UPDATE preferences SET daily_goal_minutes=1441',
                    'INSERT INTO preferences SELECT 2,focus_minutes,daily_goal_minutes,ollama_endpoint,ollama_model,answer_language,revision,ui_language FROM preferences']:
            with self.subTest(sql=sql),self.assertRaises(sqlite3.IntegrityError),self.store.db:
                self.store.db.execute(sql)

    def test_invalid_revision_is_rejected(self):
        for revision in [-1,True,None,'0']:
            with self.assertRaises(ValueError):self.store.save_preferences(self.fields(),expected_revision=revision)
        self.assertEqual(self.store.preferences()['revision'],0)


class PreferencesMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'v5.sqlite3'
        db=sqlite3.connect(self.path)
        db.executescript((Path(__file__).parent/'fixtures/schema_v5.sql').read_text())
        db.executescript("""
            INSERT INTO subjects(id,name,name_key) VALUES(1,'Biology','biology');
            INSERT INTO topics VALUES(1,1,'Cells','cells');
            INSERT INTO questions(id,subject_id,topic_id,prompt,option_a,option_b,option_c,option_d,correct_option,difficulty,explanation)
                VALUES(1,1,1,'Question?','A','B','C','D',1,'Easy','Explanation');
            INSERT INTO sessions VALUES(1,'2026-11-18',75,1,'Biology');
            INSERT INTO tasks VALUES('2026-11-18','focus',1);
            INSERT INTO practice_attempts(id,subject_id,subject_name,topic_name,question_count,status,started_at,completed_at)
                VALUES(1,1,'Biology','Cells',1,'completed','2026-11-18T12:00:00+00:00','2026-11-18T12:01:00+00:00');
            INSERT INTO practice_items(attempt_id,position,question_id,prompt,option_a,option_b,option_c,option_d,correct_option,selected_option,explanation,difficulty,topic_name)
                VALUES(1,0,1,'Question?','A','B','C','D',1,1,'Explanation','Easy','Cells');
            INSERT INTO decks(id,subject_id,subject_name,name,name_key) VALUES(1,1,'Biology','Cells','cells');
            INSERT INTO flashcards(id,deck_id,front,back,due_at) VALUES(1,1,'Front','Back','2026-11-18T12:00:00+00:00');
            INSERT INTO review_events(card_id,deck_id,card_revision,deck_name,subject_name,front,back,rating,reviewed_at,previous_due_at,due_at,interval_days)
                VALUES(1,1,0,'Cells','Biology','Front','Back','Good','2026-11-18T12:00:00+00:00','2026-11-18T12:00:00+00:00','2026-11-19T12:00:00+00:00',1);
        """)
        self.before={table:db.execute(f'SELECT * FROM {table}').fetchall() for table in ['subjects','topics','questions','tasks','sessions','practice_attempts','practice_items','decks','flashcards','review_events']}
        db.close()

    def test_schema_five_migration_keeps_all_content_and_history(self):
        store=Store(self.path)
        try:
            self.assertEqual(store.db.execute('PRAGMA user_version').fetchone()[0],SCHEMA_VERSION)
            for table,rows in self.before.items():
                self.assertEqual([tuple(r) for r in store.db.execute(f'SELECT * FROM {table}')],rows,table)
            self.assertEqual(store.preferences()['revision'],0)
            self.assertEqual(store.preferences()['focus_minutes'],15)
        finally:store.close()

    def test_failed_migration_leaves_original_schema_and_data(self):
        db=sqlite3.connect(self.path)
        db.set_authorizer(lambda action,name,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_CREATE_TABLE and name=='preferences' else sqlite3.SQLITE_OK)
        with patch('storage.sqlite3.connect',return_value=db),self.assertRaises(sqlite3.DatabaseError):
            Store(self.path)
        other=sqlite3.connect(self.path)
        try:
            self.assertEqual(other.execute('PRAGMA user_version').fetchone()[0],5)
            self.assertIsNone(other.execute("SELECT name FROM sqlite_master WHERE name='preferences'").fetchone())
            for table,rows in self.before.items():self.assertEqual(other.execute(f'SELECT * FROM {table}').fetchall(),rows)
        finally:other.close()


if __name__=='__main__':unittest.main()
