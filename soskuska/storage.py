"""Versioned local storage for subjects, topics, questions, focus sessions and daily tasks."""
import hashlib
import json
import os
import random
import sqlite3
import sys
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from content import question_fields, topic_fields
from practice import MissingPracticeError, PracticeChangedError, expired, practice_settings, utc_now
from repetition import card_fields, deck_fields, next_review
from study_statistics import statistics_report
from study_time import register_sql_functions, utc_key
from preferences import DEFAULTS, preference_fields
from database_lock import DatabaseLease
from csv_import import ImportValidationError, validate_rows, signature

SCHEMA_VERSION = 10


def _fingerprint(rows):
    """Short digest of child rows; compared under the write lock, never stored."""
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False).encode('utf-8')).hexdigest()[:24]


def default_database(base):
    base = Path(base)
    current = base / "SOSkuska" / "dashboard.sqlite3"
    legacy = base / "ExamPrep" / "dashboard.sqlite3"
    return legacy if not current.exists() and legacy.is_file() else current


def _env_base(name, default):
    # An empty or relative value would make the database depend on the current
    # directory (XDG treats such values as unset); an MCP host may start
    # headless tools anywhere, so fall back to the per-user default instead.
    value = os.environ.get(name, "")
    return Path(value) if value and Path(value).is_absolute() else default


def user_database_path():
    """The normal per-user database the GUI opens without --data.

    Lives here, not in app.py, so headless tools can find it without importing Tk.
    """
    if sys.platform == "win32":
        base = _env_base("LOCALAPPDATA", Path.home() / "AppData/Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Application Support"
    else:
        base = _env_base("XDG_DATA_HOME", Path.home() / ".local/share")
    return default_database(base)


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


from focus import FocusStoreMixin


class Store(FocusStoreMixin):
    def __init__(self, path):
        path = Path(path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.lease = DatabaseLease(path)
        try:
            self.db = sqlite3.connect(str(path))
            self.db.row_factory = sqlite3.Row
            register_sql_functions(self.db)
            self.db.execute("PRAGMA foreign_keys = ON")
            self._migrate()
        except Exception:
            if hasattr(self, 'db'):
                self.db.close()
            self.lease.close()
            raise

    @classmethod
    def open_existing(cls, path, *, readonly=False):
        """Job connection: never create or migrate a database during import preview/save."""
        path=Path(path).resolve()
        if not path.is_file():
            raise ValueError('The active database file is missing. Reopen the app before importing.')
        store=cls.__new__(cls)
        store.path=path
        store.lease=DatabaseLease(path)
        try:
            store.db=sqlite3.connect(path.as_uri()+('?mode=ro' if readonly else '?mode=rw'),uri=True)
            store.db.row_factory=sqlite3.Row
            register_sql_functions(store.db)
            store.db.execute('PRAGMA foreign_keys=ON')
            if store.db.execute('PRAGMA user_version').fetchone()[0]!=SCHEMA_VERSION:
                raise ValueError('The database version changed. Reopen the app before importing.')
        except Exception:
            if hasattr(store,'db'):store.db.close()
            store.lease.close()
            raise
        return store

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
            if version < 4:
                self.db.execute("""CREATE TABLE practice_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
                    subject_name TEXT NOT NULL,
                    topic_name TEXT NOT NULL, difficulty TEXT,
                    status TEXT NOT NULL DEFAULT 'in_progress' CHECK(status IN ('in_progress','completed')),
                    question_count INTEGER NOT NULL CHECK(question_count BETWEEN 1 AND 100),
                    current_index INTEGER NOT NULL DEFAULT 0 CHECK(current_index >= 0 AND current_index < question_count),
                    time_limit_minutes INTEGER CHECK(time_limit_minutes BETWEEN 1 AND 180),
                    started_at TEXT NOT NULL, deadline_at TEXT, completed_at TEXT)""")
                self.db.execute("""CREATE UNIQUE INDEX practice_one_active
                    ON practice_attempts(status) WHERE status='in_progress'""")
                self.db.execute("""CREATE TABLE practice_items (
                    attempt_id INTEGER NOT NULL REFERENCES practice_attempts(id) ON DELETE CASCADE,
                    position INTEGER NOT NULL CHECK(position >= 0),
                    question_id INTEGER REFERENCES questions(id) ON DELETE SET NULL,
                    prompt TEXT NOT NULL, option_a TEXT NOT NULL, option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL, option_d TEXT NOT NULL,
                    correct_option INTEGER NOT NULL CHECK(correct_option BETWEEN 0 AND 3),
                    selected_option INTEGER CHECK(selected_option BETWEEN 0 AND 3),
                    explanation TEXT NOT NULL, difficulty TEXT NOT NULL, topic_name TEXT,
                    PRIMARY KEY(attempt_id, position))""")
                self.db.execute("CREATE INDEX practice_items_question ON practice_items(question_id)")
            if version < 5:
                self.db.execute("""CREATE TABLE decks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
                    subject_name TEXT NOT NULL, name TEXT NOT NULL,
                    name_key TEXT NOT NULL UNIQUE, description TEXT NOT NULL DEFAULT '')""")
                self.db.execute("""CREATE TABLE flashcards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    deck_id INTEGER NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
                    front TEXT NOT NULL, back TEXT NOT NULL, due_at TEXT NOT NULL,
                    interval_days INTEGER NOT NULL DEFAULT 0 CHECK(interval_days BETWEEN 0 AND 365),
                    revision INTEGER NOT NULL DEFAULT 0 CHECK(revision >= 0),
                    review_count INTEGER NOT NULL DEFAULT 0 CHECK(review_count >= 0))""")
                self.db.execute("CREATE INDEX flashcards_due ON flashcards(deck_id,due_at,id)")
                self.db.execute("""CREATE TABLE review_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER REFERENCES flashcards(id) ON DELETE SET NULL,
                    deck_id INTEGER REFERENCES decks(id) ON DELETE SET NULL,
                    card_revision INTEGER NOT NULL,
                    deck_name TEXT NOT NULL, subject_name TEXT NOT NULL,
                    front TEXT NOT NULL, back TEXT NOT NULL,
                    rating TEXT NOT NULL CHECK(rating IN ('Again','Hard','Good','Easy')),
                    reviewed_at TEXT NOT NULL, previous_due_at TEXT NOT NULL,
                    due_at TEXT NOT NULL, interval_days INTEGER NOT NULL,
                    UNIQUE(card_id,card_revision))""")
                self.db.execute("CREATE INDEX review_events_deck ON review_events(deck_id,id)")
            if version < 6:
                self.db.execute("""CREATE TABLE preferences (
                    id INTEGER PRIMARY KEY CHECK(id=1),
                    focus_minutes INTEGER NOT NULL CHECK(focus_minutes BETWEEN 1 AND 180),
                    daily_goal_minutes INTEGER NOT NULL CHECK(daily_goal_minutes BETWEEN 1 AND 1440),
                    ollama_endpoint TEXT NOT NULL, ollama_model TEXT NOT NULL,
                    answer_language TEXT NOT NULL,
                    revision INTEGER NOT NULL DEFAULT 0 CHECK(revision>=0))""")
                self.db.execute("INSERT INTO preferences VALUES (1,?,?,?,?,?,0)", tuple(DEFAULTS[key] for key in ('focus_minutes','daily_goal_minutes','ollama_endpoint','ollama_model','answer_language')))
            if version < 7:
                self.db.execute("""CREATE TABLE tutor_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
                    endpoint TEXT NOT NULL, model TEXT NOT NULL,
                    revision INTEGER NOT NULL DEFAULT 0 CHECK(revision>=0),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
                self.db.execute("""CREATE TABLE tutor_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL REFERENCES tutor_conversations(id) ON DELETE CASCADE,
                    position INTEGER NOT NULL CHECK(position BETWEEN 0 AND 11),
                    prompt TEXT NOT NULL, answer TEXT NOT NULL DEFAULT '', language TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('pending','completed','stopped','failed','interrupted')),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    UNIQUE(conversation_id,position))""")
                self.db.execute('CREATE INDEX tutor_history_recent ON tutor_conversations(updated_at DESC,id DESC)')
            if version < 8:
                self.db.execute("ALTER TABLE preferences ADD COLUMN ui_language TEXT NOT NULL DEFAULT 'English' CHECK(ui_language IN ('English','Czech','Slovak','Russian'))")
            if version < 9:
                self.db.execute("ALTER TABLE preferences ADD COLUMN appearance_mode TEXT NOT NULL DEFAULT 'Dark' CHECK(appearance_mode IN ('Light','Dark','System'))")
            if version < 10:
                self.db.execute("""CREATE TABLE focus_runs (
                    id TEXT NOT NULL PRIMARY KEY CHECK(length(id)=32), singleton INTEGER NOT NULL DEFAULT 1 CHECK(singleton=1),
                    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL, subject_name TEXT NOT NULL,
                    target_seconds INTEGER NOT NULL CHECK(target_seconds BETWEEN 1 AND 10800),
                    elapsed_seconds INTEGER NOT NULL CHECK(elapsed_seconds BETWEEN 0 AND target_seconds),
                    status TEXT NOT NULL CHECK(status IN ('pending','completed','discarded')),
                    revision INTEGER NOT NULL CHECK(revision>=0), started_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    completed_at TEXT, session_id INTEGER UNIQUE REFERENCES sessions(id),
                    CHECK((status='pending' AND completed_at IS NULL) OR (status!='pending' AND completed_at IS NOT NULL)),
                    CHECK((status='completed' AND ((elapsed_seconds=0 AND session_id IS NULL) OR (elapsed_seconds>0 AND session_id IS NOT NULL))) OR (status!='completed' AND session_id IS NULL)))""")
                self.db.execute("CREATE UNIQUE INDEX focus_pending ON focus_runs(singleton) WHERE status='pending'")
            self.db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    def tutor_conversations(self, offset=0):
        if type(offset) is not int or offset < 0:
            raise ValueError('Invalid conversation page.')
        return [dict(row) for row in self.db.execute(
            'SELECT * FROM tutor_conversations ORDER BY updated_at DESC,id DESC LIMIT 21 OFFSET ?', (offset,))]

    def tutor_conversation(self, conversation_id):
        with self.db:
            self.db.execute('BEGIN')
            row = self.db.execute('SELECT * FROM tutor_conversations WHERE id=?', (conversation_id,)).fetchone()
            if row is None:
                raise ValueError('This conversation was deleted. Start a New chat or refresh history.')
            result = dict(row)
            result['turns'] = [dict(r) for r in self.db.execute(
                'SELECT * FROM tutor_turns WHERE conversation_id=? ORDER BY position', (conversation_id,))]
        return result

    def begin_tutor_turn(self, conversation_id, endpoint, model, prompt, language, *, expected_revision=0):
        from tutor_history import owner_fields, turn_fields
        endpoint, model = owner_fields(endpoint, model)
        prompt, _, language, _ = turn_fields(prompt, '', language, 'pending')
        now = utc_now().isoformat()
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            if conversation_id is None:
                title = ' '.join(prompt.split())[:80].rstrip()
                conversation_id = self.db.execute(
                    'INSERT INTO tutor_conversations(title,endpoint,model,created_at,updated_at) VALUES (?,?,?,?,?)',
                    (title, endpoint, model, now, now)).lastrowid
                revision = 0
            else:
                row = self.db.execute('SELECT * FROM tutor_conversations WHERE id=?', (conversation_id,)).fetchone()
                if row is None or row['revision'] != expected_revision:
                    raise ValueError('This conversation changed. Reopen it before sending; your prompt is kept.')
                if (row['endpoint'], row['model']) != (endpoint, model):
                    raise ValueError('Start a New chat before changing this conversation’s server or model.')
                revision = row['revision']; title = row['title']
            turns = self.db.execute('SELECT status FROM tutor_turns WHERE conversation_id=? ORDER BY position', (conversation_id,)).fetchall()
            if len(turns) >= 12:
                raise ValueError('This conversation has 12 turns. Start a New chat to continue.')
            if any(row['status']=='pending' for row in turns):
                raise ValueError('This conversation has an unfinished reply. Mark it interrupted before continuing.')
            turn_id = self.db.execute(
                'INSERT INTO tutor_turns(conversation_id,position,prompt,language,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)',
                (conversation_id,len(turns),prompt,language,'pending',now,now)).lastrowid
            self.db.execute('UPDATE tutor_conversations SET revision=?,updated_at=? WHERE id=?', (revision+1,now,conversation_id))
        return {'id':conversation_id,'turn_id':turn_id,'revision':revision+1,'title':title,'endpoint':endpoint,'model':model}

    def finish_tutor_turn(self, conversation_id, turn_id, answer, status, *, expected_revision):
        from tutor_history import TERMINAL
        from csv_import import safe_text
        answer = safe_text(answer)
        if len(answer)>16000 or status not in TERMINAL:
            raise ValueError('Invalid saved reply.')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT revision FROM tutor_conversations WHERE id=?', (conversation_id,)).fetchone()
            turn = self.db.execute('SELECT * FROM tutor_turns WHERE id=? AND conversation_id=?', (turn_id,conversation_id)).fetchone()
            # A retry after a known terminal save cannot append or change another reply.
            if row and turn and row['revision']==expected_revision+1 and turn['answer']==answer and turn['status']==status:
                return row['revision']
            if row is None or turn is None or row['revision']!=expected_revision or turn['status']!='pending':
                raise ValueError('This conversation changed or was deleted. Copy the unsaved reply, then Discard unsaved and reopen history.')
            now = utc_now().isoformat()
            self.db.execute('UPDATE tutor_turns SET answer=?,status=?,updated_at=? WHERE id=?', (answer,status,now,turn_id))
            self.db.execute('UPDATE tutor_conversations SET revision=revision+1,updated_at=? WHERE id=?', (now,conversation_id))
        return expected_revision+1

    def delete_tutor_conversation(self, conversation_id, *, expected_revision):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT revision FROM tutor_conversations WHERE id=?', (conversation_id,)).fetchone()
            if row is None or row['revision']!=expected_revision:
                raise ValueError('This conversation changed or was deleted. Refresh history and confirm again.')
            self.db.execute('DELETE FROM tutor_conversations WHERE id=?', (conversation_id,))

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

    def update_subject(self, subject_id, name, description="", exam_date="", *, expected_state=None):
        fields = subject_fields(name, description, exam_date)
        try:
            with self.db:
                self.db.execute("BEGIN IMMEDIATE")
                current = self.subject(subject_id)
                if current is None:
                    raise ValueError("This subject no longer exists. Refresh the subject list.")
                if expected_state is not None and any(current[key] != expected_state[key] for key in ("id", "name", "description", "exam_date")):
                    raise ValueError("This subject changed in another window. Your draft is kept. Reopen Edit to load the latest version before saving.")
                cursor = self.db.execute("""UPDATE subjects
                    SET name=?,name_key=?,description=?,exam_date=?,updated_at=CURRENT_TIMESTAMP
                    WHERE id=?""", (*fields, subject_id))
                if cursor.rowcount == 0:
                    raise ValueError("This subject no longer exists. Refresh the subject list.")
        except sqlite3.IntegrityError:
            raise ValueError("A subject with this name already exists.") from None

    def subject_deletion_state(self, subject_id):
        """Name and counts for the warning plus a fingerprint of the content it deletes.

        The fingerprint covers topic and question identities and editable fields, so a
        same-count replacement or edit in another window invalidates the confirmation.
        """
        row = self.db.execute("""SELECT name,
            (SELECT COUNT(*) FROM topics WHERE subject_id=subjects.id),
            (SELECT COUNT(*) FROM questions WHERE subject_id=subjects.id)
            FROM subjects WHERE id=?""", (subject_id,)).fetchone()
        if row is None:
            return None
        content = [tuple(r) for r in self.db.execute(
            "SELECT 't',id,name,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL FROM topics WHERE subject_id=? "
            "UNION ALL SELECT 'q',id,prompt,topic_id,option_a,option_b,option_c,option_d,correct_option,difficulty,explanation "
            "FROM questions WHERE subject_id=? ORDER BY 1,2", (subject_id, subject_id))]
        return (*tuple(row), _fingerprint(content))

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

    def update_topic(self, topic_id, name, *, expected_state=None):
        name, key = topic_fields(name)
        try:
            with self.db:
                self.db.execute("BEGIN IMMEDIATE")
                current = self.topic(topic_id)
                if current is None:
                    raise ValueError("This topic no longer exists.")
                if expected_state is not None and any(current[key] != expected_state[key]
                        for key in ("id", "subject_id", "name")):
                    raise ValueError("This topic changed in another window. Your draft is kept; copy your changes, then reopen Rename topic to reload.")
                cursor = self.db.execute("UPDATE topics SET name=?,name_key=? WHERE id=?", (name, key, topic_id))
                if cursor.rowcount == 0:
                    raise ValueError("This topic no longer exists.")
        except sqlite3.IntegrityError:
            raise ValueError("A topic with this name already exists in this subject.") from None

    def delete_topic(self, topic_id, *, expected_state=None):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            current = self.topic(topic_id)
            if current is None:
                raise ValueError("This topic no longer exists.")
            if expected_state is not None and any(current[key] != expected_state[key] for key in ("id", "subject_id", "name")):
                return False
            self.db.execute("DELETE FROM topics WHERE id=?", (topic_id,))
        return True

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

    def _check_question_import(self, subject_id, rows, expected_subject_name):
        normalized,errors=validate_rows(rows)
        subject=self.subject(subject_id)
        if subject is None:
            raise ImportValidationError(['The selected subject no longer exists. Choose another subject and CSV.'])
        if subject['name'] != expected_subject_name:
            raise ImportValidationError(['The selected subject was renamed. Reload its question bank and choose the CSV again.'])
        wanted={signature(row):row['record'] for row in normalized}
        prompts=list({row['fields'][0] for row in normalized})
        if prompts:
            marks=','.join('?' for _ in prompts)
            existing=self.db.execute(f"""SELECT q.*,t.name_key AS import_topic_key FROM questions q
                LEFT JOIN topics t ON t.id=q.topic_id
                WHERE q.subject_id=? AND q.prompt IN ({marks})""",(subject_id,*prompts))
            reported=set()
            for row in existing:
                key=(row['import_topic_key'] or '',*[row[k] for k in
                     ('prompt','option_a','option_b','option_c','option_d','correct_option','difficulty','explanation')])
                if key in wanted and key not in reported:
                    errors.append(f'CSV record {wanted[key]}: This exact question already exists in this subject.')
                    reported.add(key)
        return normalized,errors

    def check_question_import(self, subject_id, rows, *, expected_subject_name):
        with self.db:
            self.db.execute('BEGIN')
            return self._check_question_import(subject_id,rows,expected_subject_name)[1]

    def import_questions(self, subject_id, rows, *, expected_subject_name):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            normalized,errors=self._check_question_import(subject_id,rows,expected_subject_name)
            if errors:
                raise ImportValidationError(errors)
            topics={r['name_key']:r['id'] for r in self.db.execute('SELECT id,name_key FROM topics WHERE subject_id=?',(subject_id,))}
            created=0
            for row in normalized:
                topic_id=None
                if row['topic']:
                    name,key=topic_fields(row['topic'])
                    if key not in topics:
                        topics[key]=self.db.execute('INSERT INTO topics(subject_id,name,name_key) VALUES (?,?,?)',(subject_id,name,key)).lastrowid
                        created+=1
                    topic_id=topics[key]
                self.db.execute("""INSERT INTO questions(subject_id,topic_id,prompt,option_a,option_b,option_c,option_d,correct_option,difficulty,explanation)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",(subject_id,topic_id,*row['fields']))
        return {'questions':len(normalized),'topics':created,'subject':expected_subject_name}

    def update_question(self, question_id, prompt, options, correct_option, difficulty="Medium", topic_id=None, explanation="", *, expected_state=None):
        fields = question_fields(prompt, options, correct_option, difficulty, explanation)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            question = self.question(question_id)
            if question is None:
                raise ValueError("This question no longer exists.")
            if expected_state is not None:
                # Compare actual content, not updated_at's one-second precision.
                keys = ("id", "subject_id", "topic_id", "prompt", "option_a", "option_b",
                        "option_c", "option_d", "correct_option", "difficulty", "explanation")
                if any(question[key] != expected_state[key] for key in keys):
                    raise ValueError("This question changed in another window. Your draft is kept. Reopen Edit to load the latest version before saving.")
            self._validate_question_topic(question["subject_id"], topic_id)
            cursor = self.db.execute("""UPDATE questions SET topic_id=?,prompt=?,option_a=?,option_b=?,
                option_c=?,option_d=?,correct_option=?,difficulty=?,explanation=?,updated_at=CURRENT_TIMESTAMP
                WHERE id=?""", (topic_id, *fields, question_id))
            if cursor.rowcount == 0:
                raise ValueError("This question no longer exists.")

    def delete_question(self, question_id, *, expected_state=None):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            current = self.question(question_id)
            if current is None:
                raise ValueError("This question no longer exists.")
            keys = ("id", "subject_id", "topic_id", "prompt", "option_a", "option_b",
                    "option_c", "option_d", "correct_option", "difficulty", "explanation")
            if expected_state is not None and any(current[key] != expected_state[key] for key in keys):
                return False
            self.db.execute("DELETE FROM questions WHERE id=?", (question_id,))
        return True

    def practice_pool(self, subject_id, topic="all", difficulty=None):
        practice_settings(1, None, difficulty)
        if self.subject(subject_id) is None:
            raise ValueError("Choose an existing subject.")
        if topic != "all" and topic is not None:
            if type(topic) is not int:
                raise ValueError("Choose a topic from this subject.")
            self._validate_question_topic(subject_id, topic)
        return [q for q in self.questions(subject_id)
                if (topic == "all" or q["topic_id"] == topic)
                and (difficulty is None or q["difficulty"] == difficulty)]

    def start_practice(self, subject_id, count, topic="all", difficulty=None, minutes=None):
        practice_settings(count, minutes, difficulty)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if self.active_practice() is not None:
                raise ValueError("Finish or discard the current test before starting another.")
            pool = self.practice_pool(subject_id, topic, difficulty)
            if count > len(pool):
                raise ValueError(f"Only {len(pool)} questions match these settings. Choose fewer questions.")
            subject = self.subject(subject_id)
            topic_name = "All topics" if topic == "all" else ("No topic" if topic is None else self.topic(topic)["name"])
            now = utc_now()
            deadline = (now + timedelta(minutes=minutes)).isoformat() if minutes is not None else None
            cursor = self.db.execute("""INSERT INTO practice_attempts(
                subject_id,subject_name,topic_name,difficulty,question_count,time_limit_minutes,started_at,deadline_at)
                VALUES (?,?,?,?,?,?,?,?)""", (subject_id, subject["name"], topic_name, difficulty, count, minutes, now.isoformat(), deadline))
            attempt_id = cursor.lastrowid
            for position, question in enumerate(random.sample(pool, count)):
                self.db.execute("""INSERT INTO practice_items(
                    attempt_id,position,question_id,prompt,option_a,option_b,option_c,option_d,correct_option,explanation,difficulty,topic_name)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", (attempt_id, position, question["id"],
                    *(question[key] for key in ["prompt", "option_a", "option_b", "option_c", "option_d", "correct_option", "explanation", "difficulty", "topic_name"])))
        return attempt_id

    def practice_attempt(self, attempt_id):
        row = self.db.execute("""SELECT a.*,
            (SELECT COUNT(*) FROM practice_items WHERE attempt_id=a.id AND selected_option IS NOT NULL) AS answered,
            (SELECT COUNT(*) FROM practice_items WHERE attempt_id=a.id AND selected_option=correct_option) AS correct
            FROM practice_attempts a WHERE a.id=?""", (attempt_id,)).fetchone()
        return dict(row) if row else None

    def active_practice(self):
        row = self.db.execute("SELECT id FROM practice_attempts WHERE status='in_progress'").fetchone()
        return self.practice_attempt(row[0]) if row else None

    def practice_items(self, attempt_id):
        return [dict(row) for row in self.db.execute(
            "SELECT * FROM practice_items WHERE attempt_id=? ORDER BY position", (attempt_id,))]

    def practice_history(self, limit=20):
        ids = self.db.execute("SELECT id FROM practice_attempts WHERE status='completed' ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [self.practice_attempt(row[0]) for row in ids]

    def practice_history_page(self, *, subject_name=None, date_from='', date_to='', page=0, page_size=20):
        """Read one consistent, bounded page using historical names and local completion dates."""
        if type(page) is not int or page < 0 or type(page_size) is not int or not 1 <= page_size <= 100:
            raise ValueError("Choose a valid history page.")
        if subject_name is not None and (not isinstance(subject_name, str) or not 1 <= len(subject_name) <= 120):
            raise ValueError("Choose a subject from practice history.")
        bounds = []
        for value in (date_from, date_to):
            try:
                if not isinstance(value, str) or (value and date.fromisoformat(value).isoformat() != value):
                    raise ValueError
            except ValueError:
                raise ValueError("Use valid history dates in YYYY-MM-DD format, or leave them empty.") from None
            bounds.append(value)
        if all(bounds) and date_from > date_to:
            raise ValueError("History start date must not be after the end date.")
        # Use the same parser as result display/backup validation, including
        # accepted ISO offsets and fractional seconds SQLite date() cannot parse.
        where = ["status='completed'"]
        params = []
        if subject_name is not None:
            where.append('subject_name=?'); params.append(subject_name)
        if date_from:
            where.append("study_local_day(completed_at)>=?"); params.append(date_from)
        if date_to:
            where.append("study_local_day(completed_at)<=?"); params.append(date_to)
        clause = ' AND '.join(where)
        with self.db:
            self.db.execute('BEGIN')
            names = [row[0] for row in self.db.execute(
                "SELECT DISTINCT subject_name FROM practice_attempts WHERE status='completed' ORDER BY subject_name COLLATE NOCASE,subject_name")]
            total = self.db.execute('SELECT COUNT(*) FROM practice_attempts WHERE '+clause, params).fetchone()[0]
            pages = max(1, (total + page_size - 1) // page_size)
            page = min(page, pages - 1)
            rows = self.db.execute("""SELECT a.*,
                (SELECT COUNT(*) FROM practice_items WHERE attempt_id=a.id AND selected_option IS NOT NULL) AS answered,
                (SELECT COUNT(*) FROM practice_items WHERE attempt_id=a.id AND selected_option=correct_option) AS correct
                FROM practice_attempts a WHERE """+clause+" ORDER BY study_utc_key(completed_at) DESC,id DESC LIMIT ? OFFSET ?",
                [*params,page_size,page*page_size]).fetchall()
        return dict(rows=[dict(row) for row in rows], total=total, page=page, pages=pages, subjects=names)

    def _editable_practice(self, attempt_id):
        attempt = self.practice_attempt(attempt_id)
        if attempt is None or attempt["status"] != "in_progress":
            raise ValueError("This test is no longer in progress.")
        if expired(attempt["deadline_at"], utc_now()):
            raise ValueError("Time is up. Finish the test to view your results.")
        return attempt

    def save_practice_answer(self, attempt_id, position, selected):
        if type(position) is not int or position < 0:
            raise ValueError("Choose an existing question.")
        if selected is not None and (type(selected) is not int or selected not in range(4)):
            raise ValueError("Choose answer A, B, C or D.")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            self._editable_practice(attempt_id)
            cursor = self.db.execute("UPDATE practice_items SET selected_option=? WHERE attempt_id=? AND position=?", (selected, attempt_id, position))
            if cursor.rowcount == 0:
                raise ValueError("This question does not belong to this test.")

    def set_practice_position(self, attempt_id, position):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            attempt = self._editable_practice(attempt_id)
            if type(position) is not int or not 0 <= position < attempt["question_count"]:
                raise ValueError("Choose an existing question.")
            self.db.execute("UPDATE practice_attempts SET current_index=? WHERE id=?", (position, attempt_id))

    def practice_answers(self, attempt_id):
        """The saved selections in position order, as shown on a confirmation."""
        return tuple(row[0] for row in self.db.execute(
            "SELECT selected_option FROM practice_items WHERE attempt_id=? ORDER BY position", (attempt_id,)))

    def _check_practice_answers(self, attempt_id, expected_answers):
        if expected_answers is not None and self.practice_answers(attempt_id) != tuple(expected_answers):
            raise PracticeChangedError("This test changed in another window. Its current answers are shown; confirm again to continue.")

    def complete_practice(self, attempt_id, *, expected_answers=None):
        """Submit an attempt. With `expected_answers` (from a confirmation), refuse if
        another window changed an answer since; an expired attempt is saved anyway."""
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            attempt = self.practice_attempt(attempt_id)
            if attempt is None:
                raise MissingPracticeError("This test no longer exists.")
            if attempt["status"] == "in_progress":
                now = utc_now()
                if expired(attempt["deadline_at"], now):
                    finished = attempt["deadline_at"]
                else:
                    self._check_practice_answers(attempt_id, expected_answers)
                    finished = now.isoformat()
                self.db.execute("UPDATE practice_attempts SET status='completed',completed_at=? WHERE id=?", (finished, attempt_id))
        return self.practice_attempt(attempt_id)

    def discard_practice(self, attempt_id, *, expected_answers=None):
        """Return True if discarded, False if expiry saved the result instead."""
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            attempt = self.practice_attempt(attempt_id)
            if attempt is None:
                raise MissingPracticeError("This test no longer exists.")
            if attempt["status"] != "in_progress":
                raise ValueError("Only an in-progress test can be discarded.")
            # Check the clock after waiting for any competing writer. Expired
            # answers belong to history even if the UI timer has not run yet.
            if expired(attempt["deadline_at"], utc_now()):
                self.db.execute("UPDATE practice_attempts SET status='completed',completed_at=? WHERE id=?",
                                (attempt["deadline_at"], attempt_id))
                return False
            # Never delete answers another window saved after this confirmation opened.
            self._check_practice_answers(attempt_id, expected_answers)
            self.db.execute("DELETE FROM practice_attempts WHERE id=?", (attempt_id,))
        return True

    def decks(self):
        return [dict(row) for row in self.db.execute("""SELECT d.*,s.name AS current_subject_name,
            (SELECT COUNT(*) FROM flashcards WHERE deck_id=d.id) AS card_count,
            (SELECT COUNT(*) FROM flashcards WHERE deck_id=d.id AND study_utc_key(due_at)<=?) AS due_count
            FROM decks d LEFT JOIN subjects s ON s.id=d.subject_id ORDER BY d.name_key,d.id""", (utc_key(utc_now().isoformat()),))]

    def deck(self, deck_id):
        row = self.db.execute("""SELECT d.*,s.name AS current_subject_name FROM decks d
            LEFT JOIN subjects s ON s.id=d.subject_id WHERE d.id=?""", (deck_id,)).fetchone()
        return dict(row) if row else None

    def create_deck(self, subject_id, name, description=""):
        name, key, description = deck_fields(name, description)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            subject = self.subject(subject_id)
            if subject is None:
                raise ValueError("Choose an existing subject.")
            try:
                cursor = self.db.execute("INSERT INTO decks(subject_id,subject_name,name,name_key,description) VALUES (?,?,?,?,?)",
                                         (subject_id, subject["name"], name, key, description))
            except sqlite3.IntegrityError:
                raise ValueError("A deck with this name already exists.") from None
        return cursor.lastrowid

    def update_deck(self, deck_id, name, description="", *, expected_state=None):
        name, key, description = deck_fields(name, description)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            current = self.deck(deck_id)
            if current is None:
                raise ValueError("This deck no longer exists.")
            if expected_state is not None and any(current[key] != expected_state[key]
                    for key in ("id", "name", "description")):
                raise ValueError("This deck changed in another window. Your draft is kept; copy your changes, then reopen Edit deck to reload.")
            try:
                cursor = self.db.execute("UPDATE decks SET name=?,name_key=?,description=? WHERE id=?", (name, key, description, deck_id))
            except sqlite3.IntegrityError:
                raise ValueError("A deck with this name already exists.") from None
            if cursor.rowcount == 0:
                raise ValueError("This deck no longer exists.")

    def deck_deletion_state(self, deck_id):
        """Name and card count for the warning plus a fingerprint of the cards it deletes."""
        row = self.db.execute("""SELECT name,(SELECT COUNT(*) FROM flashcards WHERE deck_id=decks.id)
            FROM decks WHERE id=?""", (deck_id,)).fetchone()
        if row is None:
            return None
        cards = [tuple(r) for r in self.db.execute(
            "SELECT id,front,back FROM flashcards WHERE deck_id=? ORDER BY id", (deck_id,))]
        return (*tuple(row), _fingerprint(cards))

    def delete_deck(self, deck_id, expected_state=None):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            state = self.deck_deletion_state(deck_id)
            if state is None:
                raise ValueError("This deck no longer exists.")
            if expected_state is not None and state != expected_state:
                return False
            self.db.execute("DELETE FROM decks WHERE id=?", (deck_id,))
        return True

    def flashcards(self, deck_id, query=""):
        key = unicodedata.normalize("NFKC", query.strip()).casefold()
        rows = self.db.execute("SELECT * FROM flashcards WHERE deck_id=? ORDER BY id", (deck_id,))
        return [dict(row) for row in rows if not key or key in unicodedata.normalize("NFKC", row["front"] + "\n" + row["back"]).casefold()]

    def flashcard(self, card_id):
        row = self.db.execute("SELECT * FROM flashcards WHERE id=?", (card_id,)).fetchone()
        return dict(row) if row else None

    def _check_flashcard_import(self, deck_id, rows, expected_deck_name):
        from flashcard_csv_import import validate_rows
        normalized, errors = validate_rows(rows)
        deck = self.deck(deck_id)
        if deck is None or deck['name'] != expected_deck_name:
            errors.append('The deck was renamed or deleted. Reopen it and choose the CSV again.')
            return normalized, errors
        signatures = {tuple(row['fields']): row['record'] for row in normalized}
        fronts = list(dict.fromkeys(row['fields'][0] for row in normalized))
        if fronts:
            marks = ','.join('?' for _ in fronts)
            for card in self.db.execute(f'SELECT front,back FROM flashcards WHERE deck_id=? AND front IN ({marks})', [deck_id, *fronts]):
                key = (card['front'], card['back'])
                if key in signatures:
                    errors.append(f'CSV record {signatures[key]}: This front and back already exist in the deck.')
        return normalized, errors

    def check_flashcard_import(self, deck_id, rows, *, expected_deck_name):
        with self.db:
            self.db.execute('BEGIN')
            return self._check_flashcard_import(deck_id, rows, expected_deck_name)[1]

    def import_flashcards(self, deck_id, rows, *, expected_deck_name):
        from csv_import import ImportValidationError
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            normalized, errors = self._check_flashcard_import(deck_id, rows, expected_deck_name)
            if errors:
                raise ImportValidationError(errors)
            due = utc_now().isoformat()
            self.db.executemany('INSERT INTO flashcards(deck_id,front,back,due_at) VALUES (?,?,?,?)',
                                [(deck_id, *row['fields'], due) for row in normalized])
        return {'cards': len(normalized), 'deck': expected_deck_name}

    def create_flashcard(self, deck_id, front, back):
        front, back = card_fields(front, back)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if self.deck(deck_id) is None:
                raise ValueError("This deck no longer exists.")
            cursor = self.db.execute("INSERT INTO flashcards(deck_id,front,back,due_at) VALUES (?,?,?,?)", (deck_id, front, back, utc_now().isoformat()))
        return cursor.lastrowid

    def update_flashcard(self, card_id, front, back, expected_revision):
        front, back = card_fields(front, back)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            card = self.flashcard(card_id)
            if card is None:
                raise ValueError("This card no longer exists.")
            if type(expected_revision) is not int or card["revision"] != expected_revision:
                raise ValueError("This card changed. Reopen it before editing; your draft has been kept.")
            self.db.execute("""UPDATE flashcards SET front=?,back=?,due_at=?,interval_days=0,revision=revision+1
                WHERE id=?""", (front, back, utc_now().isoformat(), card_id))

    def delete_flashcard(self, card_id, expected_revision=None):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            card = self.flashcard(card_id)
            if card is None:
                raise ValueError("This card no longer exists.")
            if expected_revision is not None and card["revision"] != expected_revision:
                return False
            self.db.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
        return True

    def due_flashcards(self, deck_id, limit=100):
        return [dict(row) for row in self.db.execute("SELECT * FROM flashcards WHERE deck_id=? AND study_utc_key(due_at)<=? ORDER BY study_utc_key(due_at),id LIMIT ?",
                                                   (deck_id, utc_key(utc_now().isoformat()), limit))]

    def rate_flashcard(self, card_id, rating, expected_revision):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            card = self.flashcard(card_id)
            if card is None:
                raise ValueError("This card no longer exists.")
            if type(expected_revision) is not int or card["revision"] != expected_revision:
                raise ValueError("This card changed. Reveal its current answer before rating it.")
            now = utc_now()
            if datetime.fromisoformat(card["due_at"]) > now:
                raise ValueError("This card is not due yet.")
            due, interval, _label = next_review(card["interval_days"], rating, now)
            deck = self.deck(card["deck_id"])
            subject_name = deck["current_subject_name"] or deck["subject_name"]
            cursor = self.db.execute("""INSERT INTO review_events(
                card_id,deck_id,card_revision,deck_name,subject_name,front,back,rating,reviewed_at,previous_due_at,due_at,interval_days)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", (card_id, card["deck_id"], card["revision"], deck["name"], subject_name,
                    card["front"], card["back"], rating, now.isoformat(), card["due_at"], due.isoformat(), interval))
            self.db.execute("""UPDATE flashcards SET due_at=?,interval_days=?,revision=revision+1,review_count=review_count+1
                WHERE id=?""", (due.isoformat(), interval, card_id))
            result = {"id": cursor.lastrowid, "due_at": due.isoformat(), "interval_days": interval}
        # No post-commit read: a failed UI refresh must not repeat this rating.
        return result

    def flashcard_history(self, deck_id=None, limit=20):
        query = "SELECT * FROM review_events"
        parameters = []
        if deck_id is not None:
            query += " WHERE deck_id=?"
            parameters.append(deck_id)
        return [dict(row) for row in self.db.execute(query + " ORDER BY id DESC LIMIT ?", (*parameters, limit))]

    def add_session(self, seconds, subject_id=None, subject_name=None, *, focus_run_id=None):
        if focus_run_id is not None:
            return self.finish_focus_checkpoint(focus_run_id,seconds)
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

    def statistics(self, period="Last 7 days", *, today=None):
        return statistics_report(self.db, period, today=today)

    def preferences(self):
        row = self.db.execute("SELECT * FROM preferences WHERE id=1").fetchone()
        if row is None:
            return dict(DEFAULTS, revision=0, invalid=True)
        try:
            fields = preference_fields(*(row[key] for key in DEFAULTS))
        except (ValueError, TypeError, AttributeError):
            return dict(DEFAULTS, revision=row["revision"], invalid=True)
        return dict(fields, revision=row["revision"], invalid=False)

    def save_preferences(self, fields, *, expected_revision):
        normalized = preference_fields(*(fields[key] for key in DEFAULTS))
        if type(expected_revision) is not int or expected_revision < 0:
            raise ValueError("Reload settings before saving.")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            row = self.db.execute("SELECT revision FROM preferences WHERE id=1").fetchone()
            revision = row[0] if row else 0
            if revision != expected_revision:
                raise ValueError("Settings changed in another window. Your draft is kept; copy it before using Reload to combine changes.")
            self.db.execute("""INSERT INTO preferences(id,focus_minutes,daily_goal_minutes,ollama_endpoint,ollama_model,answer_language,ui_language,appearance_mode,revision) VALUES (1,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET focus_minutes=excluded.focus_minutes,
                daily_goal_minutes=excluded.daily_goal_minutes,ollama_endpoint=excluded.ollama_endpoint,
                ollama_model=excluded.ollama_model,answer_language=excluded.answer_language,
                ui_language=excluded.ui_language,appearance_mode=excluded.appearance_mode,revision=excluded.revision""", (*normalized.values(), revision+1))
        return dict(normalized, revision=revision+1, invalid=False)

    def close(self):
        try:
            try:self.release_focus()
            finally:self.db.close()
        finally:
            self.lease.close()
