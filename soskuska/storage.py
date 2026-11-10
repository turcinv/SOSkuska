"""Local Dashboard state, independent of the graphical interface."""
import sqlite3
from datetime import date
from pathlib import Path


def default_database(base):
    """Prefer the new namespace; reuse an existing legacy DB without moving it."""
    base = Path(base)
    current = base / "SOSkuska" / "dashboard.sqlite3"
    legacy = base / "ExamPrep" / "dashboard.sqlite3"
    if not current.exists() and legacy.is_file():
        return legacy
    return current


class Store:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                day TEXT NOT NULL, name TEXT NOT NULL, done INTEGER NOT NULL,
                PRIMARY KEY (day, name)
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY, day TEXT NOT NULL,
                seconds INTEGER NOT NULL CHECK(seconds >= 0)
            );
        """)

    def task(self, name, default=False):
        row = self.db.execute("SELECT done FROM tasks WHERE day=? AND name=?",
                              (date.today().isoformat(), name)).fetchone()
        return bool(row[0]) if row else default

    def set_task(self, name, done):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO tasks VALUES (?, ?, ?)",
                            (date.today().isoformat(), name, int(done)))

    def add_session(self, seconds):
        if seconds > 0:
            with self.db:
                self.db.execute("INSERT INTO sessions(day, seconds) VALUES (?, ?)",
                                (date.today().isoformat(), seconds))

    def seconds(self, today=False):
        query = "SELECT COALESCE(SUM(seconds), 0) FROM sessions"
        if today:
            return self.db.execute(query + " WHERE day=?", (date.today().isoformat(),)).fetchone()[0]
        return self.db.execute(query).fetchone()[0]

    def close(self):
        self.db.close()
