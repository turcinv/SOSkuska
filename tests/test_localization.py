"""Translation coverage, canonical formatting, migration and preference isolation."""
import ast
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from string import Formatter
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'soskuska'))
from localization import Translator, tr, LANGUAGE_CODES
from preferences import DEFAULTS
from storage import Store, SCHEMA_VERSION
from backup import PreparedBackup, create_backup, restore_backup

ROOT=Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def test_catalogs_have_identical_keys_and_format_contracts(self):
        base=Translator().catalog
        for language in LANGUAGE_CODES:
            catalog=Translator(language).catalog;self.assertEqual(set(catalog),set(base))
            for key,value in catalog.items():
                with self.subTest(language=language,key=key):
                    self.assertIsInstance(value,str);self.assertTrue(value)
                    shape=lambda text:[(name,spec,conversion) for _,name,spec,conversion in Formatter().parse(text) if name is not None]
                    self.assertCountEqual(shape(key),shape(value))
                    self.assertFalse(any(ord(c)<32 and c not in '\n\t\r' for c in value))

    def test_explicit_literal_ui_keys_have_catalog_entries(self):
        keys=Translator().catalog
        for path in (ROOT/'soskuska').glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='tr' and len(node.args)>1:
                    if isinstance(node.args[1],ast.Constant) and isinstance(node.args[1].value,str) and node.args[1].value:
                        self.assertIn(node.args[1].value,keys,(path,node.lineno))

    def test_formats_preserve_opaque_user_text_and_unknown_errors(self):
        for language in LANGUAGE_CODES:
            translator=Translator(language)
            name='Settings {v1} русский 日本語'
            text=translator.text('Topic: {v0}',v0=name)
            self.assertIn(name,text)
            source='Imported 3 flashcards into '+name+'. New cards are due now.'
            self.assertIn(name,translator.text(source))
            self.assertEqual(translator.text('Unknown OS error: /tmp/Settings'), 'Unknown OS error: /tmp/Settings')
            self.assertIn('03:02',translator.text('Time left · {v0:02d}:{v1:02d}',v0=3,v1=2))

    def test_unknown_language_and_headless_helpers_fall_back_to_english(self):
        self.assertEqual(Translator('French').language,'English')
        self.assertEqual(tr(SimpleNamespace(),'Page {v0} / {v1} · up to 50 questions per page',v0=1,v1=2),'Page 1 / 2 · up to 50 questions per page')
        self.assertEqual(tr(SimpleNamespace(translator=Translator('Russian')),'Settings'),'Настройки')

    def test_rendering_does_not_change_process_locale_or_network(self):
        import locale
        original=locale.setlocale(locale.LC_ALL)
        with patch('socket.create_connection',side_effect=AssertionError('Unexpected network')):
            for language in LANGUAGE_CODES:Translator(language).text('Settings')
        self.assertEqual(locale.setlocale(locale.LC_ALL),original)


class ChoiceLabelTests(unittest.TestCase):
    def test_user_model_and_subject_names_never_translate_as_ui_copy(self):
        from localization_widgets import LocalizedOptionMenu
        for language in LANGUAGE_CODES:
            menu=LocalizedOptionMenu.__new__(LocalizedOptionMenu)
            menu.owner=SimpleNamespace(translator=Translator(language));menu.translate_values=False
            for value in ['Settings','Hard','Connect to load models','No models installed']:
                self.assertEqual(menu.label(value),value)
            menu.translate_values=True
            self.assertEqual(menu.label('Settings'),menu.owner.translator.text('Settings'))


class LanguageStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'languages.db';self.store=Store(self.path);self.addCleanup(self.store.close)

    def test_ui_language_is_saved_independently_of_answer_language(self):
        for index,language in enumerate(LANGUAGE_CODES):
            saved=self.store.save_preferences(dict(DEFAULTS,ui_language=language,answer_language='Russian'),expected_revision=index)
            self.assertEqual(saved['ui_language'],language);self.assertEqual(saved['answer_language'],'Russian')
        other=Store(self.path)
        try:self.assertEqual(other.preferences()['ui_language'],'Russian')
        finally:other.close()

    def test_invalid_choice_and_failed_write_preserve_previous_preferences(self):
        before=self.store.preferences()
        with self.assertRaises(ValueError):self.store.save_preferences(dict(DEFAULTS,ui_language='French'),expected_revision=0)
        self.store.db.execute("CREATE TRIGGER fail_language BEFORE UPDATE ON preferences BEGIN SELECT RAISE(ABORT,'full'); END")
        with self.assertRaises(sqlite3.Error):self.store.save_preferences(dict(DEFAULTS,ui_language='Czech'),expected_revision=0)
        self.assertEqual(self.store.preferences(),before)

    def test_backup_roundtrip_preserves_interface_and_answer_language(self):
        self.store.save_preferences(dict(DEFAULTS,ui_language='Slovak',answer_language='Russian'),expected_revision=0)
        path=self.path.with_name('backup.db');create_backup(self.path,path);prepared=PreparedBackup(path,self.path)
        try:
            self.store.save_preferences(dict(DEFAULTS),expected_revision=1)
            self.store.close();restore_backup(self.path,prepared)
        finally:prepared.close()
        other=Store(self.path)
        try:
            self.assertEqual(other.preferences()['ui_language'],'Slovak');self.assertEqual(other.preferences()['answer_language'],'Russian')
        finally:other.close()

    def test_schema_seven_migration_preserves_chat_study_and_preferences(self):
        self.store.close();self.path.unlink()
        with closing(sqlite3.connect(self.path)) as db:
            db.executescript((ROOT/'tests/fixtures/schema_v7.sql').read_text(encoding='utf-8'))
            db.execute("INSERT INTO subjects(name,name_key) VALUES('Keep','keep')")
            db.execute("UPDATE preferences SET focus_minutes=30,answer_language='Russian',revision=4")
            now='2026-11-20T12:00:00+00:00'
            db.execute('INSERT INTO tutor_conversations(title,endpoint,model,revision,created_at,updated_at) VALUES (?,?,?,?,?,?)',('Keep chat','http://127.0.0.1:11434','Hard',2,now,now))
            db.execute('INSERT INTO tutor_turns(conversation_id,position,prompt,answer,language,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)',(1,0,'Settings','Delete','Russian','completed',now,now))
            db.commit()
        migrated=Store(self.path)
        try:
            saved=migrated.preferences();self.assertEqual(saved['ui_language'],'English')
            self.assertEqual(saved['answer_language'],'Russian');self.assertEqual(saved['focus_minutes'],30);self.assertEqual(saved['revision'],4)
            self.assertEqual(migrated.subjects()[0]['name'],'Keep')
            chat=migrated.tutor_conversation(1);self.assertEqual(chat['revision'],2)
            self.assertEqual(chat['model'],'Hard');self.assertEqual(chat['turns'][0]['answer'],'Delete')
            self.assertEqual(migrated.db.execute('PRAGMA user_version').fetchone()[0],SCHEMA_VERSION)
        finally:migrated.close()

    def test_failed_language_migration_rolls_back_original_schema(self):
        self.store.close();self.path.unlink()
        with closing(sqlite3.connect(self.path)) as db:db.executescript((ROOT/'tests/fixtures/schema_v7.sql').read_text(encoding='utf-8'))
        db=sqlite3.connect(self.path)
        db.set_authorizer(lambda action,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_ALTER_TABLE else sqlite3.SQLITE_OK)
        with patch('storage.sqlite3.connect',return_value=db),self.assertRaises(sqlite3.Error):Store(self.path)
        with closing(sqlite3.connect(self.path)) as check:
            self.assertEqual(check.execute('PRAGMA user_version').fetchone()[0],7)
            self.assertNotIn('ui_language',[r[1] for r in check.execute('PRAGMA table_info(preferences)')])


class DiagnosticTranslationTests(unittest.TestCase):
    def test_csv_record_prefix_and_known_validation_detail_translate_together(self):
        for language in ['Czech','Slovak','Russian']:
            result=Translator(language).text('CSV record 3: Expected 2 cells, found 1.')
            self.assertIn('3',result);self.assertNotIn('Expected',result);self.assertNotIn('CSV record',result)

    def test_formatted_technical_values_are_not_reinterpreted(self):
        result=Translator('Russian').text('Invalid text in tutor_turns.answer.')
        self.assertIn('tutor_turns.answer',result);self.assertNotIn('Invalid text',result)
