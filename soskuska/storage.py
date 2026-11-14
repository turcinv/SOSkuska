"""Versioned local storage for subjects, topics, questions, focus sessions and daily tasks."""
import sqlite3
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from content import question_fields, topic_fields

SCHEMA_VERSION = 3


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
            if version < 3:
                self.db.execute("""CREATE TABLE topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
                    name TEXT NOT NULL, name_key TEXT NOT NULL,
                    UNIQUE(subject_id, name_key))""")
                self.db.execute("""CREATE TABLE questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
                    topic_id INTEGER REFERENCES topics(id) ON DELETE SET NULL,
                    prompt TEXT NOT NULL, option_a TEXT NOT NULL, option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL, option_d TEXT NOT NULL,
                    correct_option INTEGER NOT NULL CHECK(correct_option BETWEEN 0 AND 3),
                    difficulty TEXT NOT NULL CHECK(difficulty IN ('Easy','Medium','Hard')),
                    explanation TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
                self.db.execute("CREATE INDEX questions_subject ON questions(subject_id)")
                self.db.execute("CREATE INDEX questions_topic ON questions(topic_id)")
                # Enforce topic ownership even for direct SQL writes.
                for operation in ("INSERT", "UPDATE OF topic_id, subject_id"):
                    suffix = "insert" if operation == "INSERT" else "update"
                    self.db.execute(f"""CREATE TRIGGER questions_topic_{suffix}
                        BEFORE {operation} ON questions
                        WHEN NEW.topic_id IS NOT NULL AND NOT EXISTS (
                            SELECT 1 FROM topics WHERE id=NEW.topic_id AND subject_id=NEW.subject_id)
                        BEGIN SELECT RAISE(ABORT, 'Topic must belong to the question subject'); END""")
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
                   COALESCE(SUM(x.seconds), 0) AS study_seconds,
                   (SELECT COUNT(*) FROM topics t WHERE t.subject_id=s.id) AS topic_count,
                   (SELECT COUNT(*) FROM questions q WHERE q.subject_id=s.id) AS question_count
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

    def subject_deletion_state(self, subject_id):
        """The name and content counts shown in the destructive-action warning."""
        row = self.db.execute("""SELECT name,
            (SELECT COUNT(*) FROM topics WHERE subject_id=subjects.id),
            (SELECT COUNT(*) FROM questions WHERE subject_id=subjects.id)
            FROM subjects WHERE id=?""", (subject_id,)).fetchone()
        return tuple(row) if row else None

    def delete_subject(self, subject_id, expected_state=None):
        """Return False when the confirmation is stale; delete atomically otherwise."""
        with self.db:
            if expected_state is not None:
                # Keep other connections from changing content between check/delete.
                self.db.execute("BEGIN IMMEDIATE")
                current = self.subject_deletion_state(subject_id)
                if current is not None and current != expected_state:
                    return False
            cursor = self.db.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
            if cursor.rowcount == 0:
                raise ValueError("This subject no longer exists.")
        return True

    def topics(self, subject_id):
        return [dict(row) for row in self.db.execute("""SELECT t.*, COUNT(q.id) AS question_count
            FROM topics t LEFT JOIN questions q ON q.topic_id=t.id
            WHERE t.subject_id=? GROUP BY t.id ORDER BY t.name_key,t.id""", (subject_id,))]

    def topic(self, topic_id):
        row = self.db.execute("SELECT * FROM topics WHERE id=?", (topic_id,)).fetchone()
        return dict(row) if row else None

    def create_topic(self, subject_id, name):
        name, key = topic_fields(name)
        if self.subject(subject_id) is None:
            raise ValueError("This subject no longer exists.")
        try:
            with self.db:
                cursor = self.db.execute("INSERT INTO topics(subject_id,name,name_key) VALUES (?,?,?)", (subject_id, name, key))
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("A topic with this name already exists in this subject.") from None

    def update_topic(self, topic_id, name):
        name, key = topic_fields(name)
        try:
            with self.db:
                cursor = self.db.execute("UPDATE topics SET name=?,name_key=? WHERE id=?", (name, key, topic_id))
                if cursor.rowcount == 0:
                    raise ValueError("This topic no longer exists.")
        except sqlite3.IntegrityError:
            raise ValueError("A topic with this name already exists in this subject.") from None

    def delete_topic(self, topic_id):
        with self.db:
            cursor = self.db.execute("DELETE FROM topics WHERE id=?", (topic_id,))
            if cursor.rowcount == 0:
                raise ValueError("This topic no longer exists.")

    def questions(self, subject_id):
        return [dict(row) for row in self.db.execute("""SELECT q.*, t.name AS topic_name
            FROM questions q LEFT JOIN topics t ON t.id=q.topic_id
            WHERE q.subject_id=? ORDER BY q.id DESC""", (subject_id,))]

    def question(self, question_id):
        row = self.db.execute("SELECT * FROM questions WHERE id=?", (question_id,)).fetchone()
        return dict(row) if row else None

    def _validate_question_topic(self, subject_id, topic_id):
        if self.subject(subject_id) is None:
            raise ValueError("This subject no longer exists.")
        if topic_id is not None:
            topic = self.topic(topic_id)
            if topic is None or topic["subject_id"] != subject_id:
                raise ValueError("Choose a topic belonging to this subject.")

    def create_question(self, subject_id, prompt, options, correct_option, difficulty="Medium", topic_id=None, explanation=""):
        fields = question_fields(prompt, options, correct_option, difficulty, explanation)
        self._validate_question_topic(subject_id, topic_id)
        with self.db:
            cursor = self.db.execute("""INSERT INTO questions(
                subject_id,topic_id,prompt,option_a,option_b,option_c,option_d,correct_option,difficulty,explanation)
                VALUES (?,?,?,?,?,?,?,?,?,?)""", (subject_id, topic_id, *fields))
        return cursor.lastrowid

    def update_question(self, question_id, prompt, options, correct_option, difficulty="Medium", topic_id=None, explanation=""):
        fields = question_fields(prompt, options, correct_option, difficulty, explanation)
        question = self.question(question_id)
        if question is None:
            raise ValueError("This question no longer exists.")
        self._validate_question_topic(question["subject_id"], topic_id)
        with self.db:
            cursor = self.db.execute("""UPDATE questions SET topic_id=?,prompt=?,option_a=?,option_b=?,
                option_c=?,option_d=?,correct_option=?,difficulty=?,explanation=?,updated_at=CURRENT_TIMESTAMP
                WHERE id=?""", (topic_id, *fields, question_id))
            if cursor.rowcount == 0:
                raise ValueError("This question no longer exists.")

    def delete_question(self, question_id):
        with self.db:
            cursor = self.db.execute("DELETE FROM questions WHERE id=?", (question_id,))
            if cursor.rowcount == 0:
                raise ValueError("This question no longer exists.")

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
