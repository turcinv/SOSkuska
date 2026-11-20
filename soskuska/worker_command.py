"""Explicit source/frozen launch paths for isolated database helpers (no Tk)."""
import sys
from pathlib import Path

WORKERS = {'backup': 'backup_worker.py', 'questions': 'csv_import_worker.py', 'flashcards': 'flashcard_csv_import_worker.py'}


def worker_command(worker, *args):
    script = WORKERS[worker]
    if getattr(sys, 'frozen', False):
        suffix = '.exe' if sys.platform == 'win32' else ''
        command = [str(Path(sys.executable).with_name('SOSkuska-worker' + suffix)), worker]
    else:
        command = [sys.executable, '-u', str(Path(__file__).with_name(script))]
    return [*command, *(str(arg) for arg in args)]
