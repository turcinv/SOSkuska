"""Versioned local storage for subjects, focus sessions and daily tasks."""
import sqlite3
import unicodedata
from datetime import date, timedelta
from pathlib import Path

SCHEMA_VERSION = 2


def default_database(base):
    base = Path(base)
    current = base / "SOSkuska" / "dashboard.sqlite3"
    legacy = base / "ExamPrep" / "dashboard.sqlite3"
    return legacy if not current.exists() and legacy.is_file() else current


def subject_fields(name, description="", exam_date=""):
    name = " ".join(name.split())
    description = description.strip()
    exam_date = exam_date.strip()
    if not name or len(name) > 120:
        raise ValueError("Enter a subject name between 1 and 120 characters.")
    if len(description) > 1000:
        raise ValueError("Keep the description within 1,000 characters.")
    if exam_date:
        try:
            parsed = date.fromisoformat(exam_date)
            if parsed.isoformat() != exam_date:
                raise ValueError
        except ValueError:
            raise ValueError("Use a valid exam date in YYYY-MM-DD format, or leave it empty.") from None
    key = unicodedata.normalize("NFKC", name).casefold()
    return name, key, description, exam_date or None


class Store:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        try:
            self._migrate()
        except Exception:
            self.db.close()
            raise

    def _migrate(self):
        # Avoid executescript: it commits implicitly and would split the migration.
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            # Another process may have migrated while this connection waited.
            version = self.db.execute("PRAGMA user_version").fetchone()[0]
            if version > SCHEMA_VERSION:
                raise ValueError("This database was created by a newer SOSkúška version.")
            if version < 1:
                self.db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                    day TEXT NOT NULL, name TEXT NOT NULL, done INTEGER NOT NULL,
                    PRIMARY KEY (day, name))""")
                self.db.execute("""CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY, day TEXT NOT NULL,
                    seconds INTEGER NOT NULL CHECK(seconds >= 0))""")
            if version < 2:
                self.db.execute("""CREATE TABLE subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL, name_key TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL DEFAULT '', exam_date TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
                self.db.execute("ALTER TABLE sessions ADD COLUMN subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL")
                self.db.execute("ALTER TABLE sessions ADD COLUMN subject_name TEXT")
                self.db.execute("CREATE INDEX sessions_subject ON sessions(subject_id)")
            self.db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    def task(self, name, default=False):
        row = self.db.execute("SELECT done FROM tasks WHERE day=? AND name=?",
                              (date.today().isoformat(), name)).fetchone()
        return bool(row[0]) if row else default

    def set_task(self, name, done):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO tasks VALUES (?, ?, ?)",
                            (date.today().isoformat(), name, int(done)))

    def subjects(self):
        return [dict(row) for row in self.db.execute("""
            SELECT s.*, COUNT(x.id) AS session_count,
                   COALESCE(SUM(x.seconds), 0) AS study_seconds
            FROM subjects s LEFT JOIN sessions x ON x.subject_id=s.id
            GROUP BY s.id ORDER BY s.name_key, s.id
        """)]

    def subject(self, subject_id):
        row = self.db.execute("SELECT * FROM subjects WHERE id=?", (subject_id,)).fetchone()
        return dict(row) if row else None

    def create_subject(self, name, description="", exam_date=""):
        fields = subject_fields(name, description, exam_date)
        try:
            with self.db:
                cursor = self.db.execute("INSERT INTO subjects(name,name_key,description,exam_date) VALUES (?,?,?,?)", fields)
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("A subject with this name already exists.") from None

    def update_subject(self, subject_id, name, description="", exam_date=""):
        fields = subject_fields(name, description, exam_date)
        try:
            with self.db:
                cursor = self.db.execute("""UPDATE subjects
                    SET name=?,name_key=?,description=?,exam_date=?,updated_at=CURRENT_TIMESTAMP
                    WHERE id=?""", (*fields, subject_id))
                if cursor.rowcount == 0:
                    raise ValueError("This subject no longer exists. Refresh the subject list.")
        except sqlite3.IntegrityError:
            raise ValueError("A subject with this name already exists.") from None

    def delete_subject(self, subject_id):
        with self.db:
            cursor = self.db.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
            if cursor.rowcount == 0:
                raise ValueError("This subject no longer exists.")

    def add_session(self, seconds, subject_id=None, subject_name=None):
        if not isinstance(seconds, int) or isinstance(seconds, bool) or seconds < 0:
            raise ValueError("Study time must be a non-negative whole number of seconds.")
        if seconds == 0:
            return
        with self.db:
            subject = self.subject(subject_id) if subject_id is not None else None
            if subject:
                subject_name = subject_name or subject["name"]
            else:
                subject_id = None
            self.db.execute("INSERT INTO sessions(day,seconds,subject_id,subject_name) VALUES (?,?,?,?)",
                            (date.today().isoformat(), seconds, subject_id, subject_name))

    def seconds(self, today=False):
        query = "SELECT COALESCE(SUM(seconds), 0) FROM sessions"
        if today:
            return self.db.execute(query + " WHERE day=?", (date.today().isoformat(),)).fetchone()[0]
        return self.db.execute(query).fetchone()[0]

    def summary(self):
        count = self.db.execute("SELECT COUNT(*) FROM sessions WHERE seconds>0").fetchone()[0]
        days = set()
        for row in self.db.execute("SELECT DISTINCT day FROM sessions WHERE seconds>0"):
            try:
                days.add(date.fromisoformat(row[0]))
            except ValueError:
                continue
        cursor = date.today()
        if cursor not in days:
            cursor -= timedelta(days=1)
        streak = 0
        while cursor in days:
            streak += 1
            cursor -= timedelta(days=1)
        return {"seconds": self.seconds(), "today_seconds": self.seconds(today=True),
                "sessions": count, "streak": streak,
                "subjects": self.db.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]}

    def upcoming_exams(self, limit=5):
        return [dict(row) for row in self.db.execute("""SELECT id,name,exam_date FROM subjects
            WHERE exam_date>=? ORDER BY exam_date,name_key LIMIT ?""", (date.today().isoformat(), limit))]

    def recent_sessions(self, limit=5):
        return [dict(row) for row in self.db.execute("""SELECT id,day,seconds,subject_id,subject_name
            FROM sessions WHERE seconds>0 ORDER BY id DESC LIMIT ?""", (limit,))]

    def close(self):
        self.db.close()
