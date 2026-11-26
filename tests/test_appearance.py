"""Appearance validation, schema-8 migration, atomic writes and readable paired colors."""
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'soskuska'))
from preferences import DEFAULTS, AI_KEYS, APPEARANCE_MODES, preference_fields
from storage import Store, SCHEMA_VERSION
from backup import PreparedBackup, create_backup, restore_backup
from theme import COLORS


def contrast(first,second):
    def luminance(value):
        rgb=[int(value[i:i+2],16)/255 for i in (1,3,5)]
        linear=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb]
        return sum(c*w for c,w in zip(linear,(.2126,.7152,.0722)))
    a,b=sorted((luminance(first),luminance(second)))
    return (b+.05)/(a+.05)


class AppearanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'appearance.db';self.store=Store(self.path);self.addCleanup(self.store.close)

    def test_default_dark_and_independent_canonical_modes(self):
        self.assertEqual(self.store.preferences()['appearance_mode'],'Dark')
        self.assertNotIn('appearance_mode',AI_KEYS)
        for revision,mode in enumerate(APPEARANCE_MODES):
            saved=self.store.save_preferences(dict(DEFAULTS,appearance_mode=mode,ui_language='Czech',answer_language='Russian'),expected_revision=revision)
            self.assertEqual((saved['appearance_mode'],saved['ui_language'],saved['answer_language']),(mode,'Czech','Russian'))
        other=Store(self.path)
        try:self.assertEqual(other.preferences()['appearance_mode'],'System')
        finally:other.close()

    def test_invalid_mode_and_failed_write_preserve_revision_and_all_fields(self):
        before=self.store.preferences()
        with self.assertRaises(ValueError):self.store.save_preferences(dict(DEFAULTS,appearance_mode='Sepia'),expected_revision=0)
        self.store.db.execute("CREATE TRIGGER no_save BEFORE UPDATE ON preferences BEGIN SELECT RAISE(ABORT,'full'); END")
        with self.assertRaises(sqlite3.Error):self.store.save_preferences(dict(DEFAULTS,appearance_mode='Light'),expected_revision=0)
        self.assertEqual(before,self.store.preferences())

    def test_stale_appearance_save_preserves_other_window_choice(self):
        other=Store(self.path)
        try:other.save_preferences(dict(DEFAULTS,appearance_mode='Light'),expected_revision=0)
        finally:other.close()
        with self.assertRaisesRegex(ValueError,'another window'):
            self.store.save_preferences(dict(DEFAULTS,appearance_mode='System'),expected_revision=0)
        self.assertEqual(self.store.preferences()['appearance_mode'],'Light')

    def test_invalid_stored_mode_falls_back_without_repair_until_save(self):
        self.store.db.execute('PRAGMA ignore_check_constraints=ON')
        self.store.db.execute("UPDATE preferences SET appearance_mode='unknown'");self.store.db.commit()
        saved=self.store.preferences();self.assertTrue(saved['invalid']);self.assertEqual(saved['appearance_mode'],'Dark')
        self.assertEqual(self.store.db.execute('SELECT appearance_mode FROM preferences').fetchone()[0],'unknown')
        self.store.save_preferences(dict(DEFAULTS),expected_revision=saved['revision'])
        self.assertFalse(self.store.preferences()['invalid'])

    def test_current_backup_roundtrip_restores_appearance_and_languages(self):
        self.store.save_preferences(dict(DEFAULTS,appearance_mode='System',ui_language='Russian'),expected_revision=0)
        target=Path(self.temp.name)/'copy.db';create_backup(self.path,target)
        prepared=PreparedBackup(target,self.path)
        try:
            self.store.save_preferences(dict(DEFAULTS,appearance_mode='Light'),expected_revision=1)
            self.store.close();restore_backup(self.path,prepared)
        finally:prepared.close()
        other=Store(self.path)
        try:
            self.assertEqual(other.preferences()['appearance_mode'],'System')
            self.assertEqual(other.preferences()['ui_language'],'Russian')
        finally:other.close()

    def schema8(self):
        self.store.close();self.path.unlink()
        with closing(sqlite3.connect(self.path)) as db:
            db.executescript((Path(__file__).parent/'fixtures/schema_v8.sql').read_text(encoding='utf-8'))
            db.execute("INSERT INTO subjects(name,name_key) VALUES('Keep','keep')")
            db.execute("UPDATE preferences SET focus_minutes=25,ui_language='Slovak',answer_language='Russian',revision=7")
            db.commit()

    def test_schema8_migration_preserves_existing_preferences_revision_and_data(self):
        self.schema8();migrated=Store(self.path)
        try:
            saved=migrated.preferences()
            self.assertEqual((saved['appearance_mode'],saved['focus_minutes'],saved['ui_language'],saved['answer_language'],saved['revision']),('Dark',25,'Slovak','Russian',7))
            self.assertEqual(migrated.subjects()[0]['name'],'Keep')
            self.assertEqual(migrated.db.execute('PRAGMA user_version').fetchone()[0],SCHEMA_VERSION)
        finally:migrated.close()

    def test_failed_schema8_migration_rolls_back_without_losing_rows(self):
        self.schema8();db=sqlite3.connect(self.path)
        db.set_authorizer(lambda action,*_:sqlite3.SQLITE_DENY if action==sqlite3.SQLITE_ALTER_TABLE else sqlite3.SQLITE_OK)
        with patch('storage.sqlite3.connect',return_value=db),self.assertRaises(sqlite3.Error):Store(self.path)
        with closing(sqlite3.connect(self.path)) as check:
            self.assertEqual(check.execute('PRAGMA user_version').fetchone()[0],8)
            self.assertNotIn('appearance_mode',[row[1] for row in check.execute('PRAGMA table_info(preferences)')])
            self.assertEqual(check.execute('SELECT name FROM subjects').fetchone()[0],'Keep')

    def test_primary_and_secondary_text_contrast_in_both_palettes(self):
        for mode in (0,1):
            for text in ('text','secondary','hover','green','warning'):
                for background in ('bg','card','raised'):
                    with self.subTest(mode=mode,text=text,background=background):
                        self.assertGreaterEqual(contrast(COLORS[text][mode],COLORS[background][mode]),4.5)
            for background in ('primary','primary_hover','danger','danger_hover'):
                self.assertGreaterEqual(contrast(COLORS['on_primary'][mode],COLORS[background][mode]),4.5)
            for background in ('primary','primary_hover'):
                self.assertGreaterEqual(contrast(COLORS['disabled_on_primary'][mode],COLORS[background][mode]),4.5)

    def test_selected_navigation_and_button_hover_states_remain_readable(self):
        # Covers actual shared helper roles rather than pinning particular hex values.
        pairs = [('hover', 'selected'), ('text', 'raised'),
                 ('text', 'secondary_hover'), ('secondary', 'raised'),
                 ('on_primary', 'primary_hover'), ('on_primary', 'danger_hover')]
        for mode in (0, 1):
            for foreground, background in pairs:
                with self.subTest(mode=mode, foreground=foreground, background=background):
                    self.assertGreaterEqual(contrast(COLORS[foreground][mode], COLORS[background][mode]), 4.5)

    def test_progress_and_dark_control_outlines_remain_distinguishable(self):
        for mode in (0, 1):
            self.assertGreaterEqual(contrast(COLORS['accent'][mode], COLORS['raised'][mode]), 3.0)
        # Disabled selector chevrons share the border fill; unchecked boxes use
        # that same border on cards. Both need to stay identifiable in Dark mode.
        for foreground, background in [('secondary', 'border'), ('border', 'card')]:
            self.assertGreaterEqual(contrast(COLORS[foreground][1], COLORS[background][1]), 3.0)

    def test_studio_navigation_and_focus_roles_are_readable(self):
        for mode in (0,1):
            for foreground,background in [('nav_text','nav_bg'),('nav_secondary','nav_bg'),
                    ('nav_accent','nav_selected'),('focus_text','focus_bg'),('focus_secondary','focus_bg')]:
                self.assertGreaterEqual(contrast(COLORS[foreground][mode],COLORS[background][mode]),4.5)
            for foreground,background in [('border','focus_bg'),('focus_accent','focus_track')]:
                self.assertGreaterEqual(contrast(COLORS[foreground][mode],COLORS[background][mode]),3)


class SystemFallbackTests(unittest.TestCase):
    def test_unsupported_system_mode_never_enables_ctk_os_command_polling(self):
        from appearance import apply_appearance
        with patch('appearance.SYSTEM_MODE_SUPPORTED',False),patch('appearance.ctk.set_appearance_mode') as apply:
            apply_appearance('System')
        apply.assert_called_once_with('Light')

    def test_native_system_and_explicit_modes_use_public_ctk_api(self):
        from appearance import apply_appearance
        with patch('appearance.SYSTEM_MODE_SUPPORTED',True),patch('appearance.ctk.set_appearance_mode') as apply:
            for mode in ('System','Light','Dark'):apply_appearance(mode)
        self.assertEqual([c.args[0] for c in apply.call_args_list],['System','Light','Dark'])


if __name__=='__main__':unittest.main()
