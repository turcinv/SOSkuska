"""Main-thread garbage collection policy; no display needed."""
import gc
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "soskuska"))
import main_thread_gc


class MainThreadGcTests(unittest.TestCase):
    def setUp(self):
        enabled, threshold = gc.isenabled(), gc.get_threshold()
        self.addCleanup(lambda: (gc.enable() if enabled else gc.disable(), gc.set_threshold(*threshold)))
        gc.disable()
        gc.collect()

    def test_collects_only_when_cpython_would(self):
        gc.set_threshold(50, 10, 10)
        self.assertIsNone(main_thread_gc.collect_due())
        kept = [[] for _ in range(200)]
        self.assertEqual(main_thread_gc.collect_due(), 0)
        self.assertIsNone(main_thread_gc.collect_due())
        self.assertTrue(kept)

    def test_older_generations_follow_their_thresholds(self):
        gc.set_threshold(1, 1, 1)
        with patch.object(gc, "get_count", return_value=(5, 2, 0)), patch.object(gc, "collect") as collect:
            self.assertEqual(main_thread_gc.collect_due(), 1)
            collect.assert_called_once_with(1)
        with patch.object(gc, "get_count", return_value=(5, 2, 2)), patch.object(gc, "collect") as collect:
            self.assertEqual(main_thread_gc.collect_due(), 2)

    def test_threshold_zero_means_never(self):
        gc.set_threshold(0)
        kept = [[] for _ in range(200)]
        self.assertIsNone(main_thread_gc.collect_due())
        self.assertTrue(kept)

    def test_install_disables_automatic_collection_and_reschedules(self):
        gc.enable()
        scheduled = []

        class Root:
            def after(self, delay, callback):
                scheduled.append((delay, callback))
        main_thread_gc.install(Root(), interval_ms=123)
        self.assertFalse(gc.isenabled())
        self.assertEqual(scheduled[0][0], 123)
        scheduled.pop()[1]()
        self.assertEqual(len(scheduled), 1, "the timer must reschedule itself")


if __name__ == "__main__":
    unittest.main()
