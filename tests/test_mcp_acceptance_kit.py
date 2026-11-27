"""Sample database tool for MCP host acceptance never touches existing or normal databases."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "soskuska"))
from storage import Store

spec = importlib.util.spec_from_file_location("make_mcp_acceptance_db", ROOT / "tools" / "make_mcp_acceptance_db.py")
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


class AcceptanceKitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "kit" / "study.sqlite3"

    def test_creates_labelled_sample_data(self):
        kit.create(self.path)
        store = Store.open_existing(self.path, readonly=True)
        try:
            subjects = store.subjects()
            self.assertEqual([s["name"] for s in subjects], ["Sample Biology", "Sample History"])
            self.assertTrue(all(s["exam_date"] for s in subjects))
            self.assertEqual(sum(s["question_count"] for s in subjects), 7)
            self.assertEqual(store.decks()[0]["due_count"], 4)
            history = store.practice_history_page()
            self.assertEqual((history["total"], history["rows"][0]["correct"]), (1, 2))
        finally:
            store.close()

    def test_refuses_existing_file_and_normal_database(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b"keep")
        with self.assertRaises(SystemExit):
            kit.create(self.path)
        self.assertEqual(self.path.read_bytes(), b"keep")
        other = Path(self.temp.name) / "normal.sqlite3"
        with patch.object(kit, "user_database_path", return_value=other), self.assertRaises(SystemExit):
            kit.create(other)
        self.assertFalse(other.exists())


if __name__ == "__main__":
    unittest.main()
