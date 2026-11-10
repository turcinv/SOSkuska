"""Storage and legacy-name compatibility; runs without a graphical session."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "soskuska"))
from storage import Store, default_database


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def test_new_install_uses_ascii_product_folder(self):
        self.assertEqual(default_database(self.base), self.base / "SOSkuska/dashboard.sqlite3")

    def test_existing_legacy_records_remain_available(self):
        legacy = self.base / "ExamPrep/dashboard.sqlite3"
        store = Store(legacy)
        store.set_task("test", True)
        store.add_session(95)
        store.close()
        selected = default_database(self.base)
        self.assertEqual(selected, legacy)
        store = Store(selected)
        self.addCleanup(store.close)
        self.assertTrue(store.task("test"))
        self.assertEqual(store.seconds(), 95)
        self.assertFalse((self.base / "SOSkuska").exists())

    def test_new_database_is_never_replaced_by_legacy(self):
        for folder, seconds in [("ExamPrep", 95), ("SOSkuska", 42)]:
            store = Store(self.base / folder / "dashboard.sqlite3")
            store.add_session(seconds)
            store.close()
        selected = default_database(self.base)
        store = Store(selected)
        self.addCleanup(store.close)
        self.assertEqual(selected.parent.name, "SOSkuska")
        self.assertEqual(store.seconds(), 42)

    def test_tasks_and_session_totals_survive_reopening(self):
        path = default_database(self.base)
        store = Store(path)
        self.assertFalse(store.task("test"))
        store.set_task("test", True)
        store.add_session(65)
        store.add_session(30)
        store.add_session(0)
        store.close()
        store = Store(path)
        self.addCleanup(store.close)
        self.assertTrue(store.task("test"))
        self.assertEqual(store.seconds(), 95)
        self.assertEqual(store.seconds(today=True), 95)


if __name__ == "__main__":
    unittest.main()
