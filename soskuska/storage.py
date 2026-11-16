"""Versioned local storage for subjects, topics, questions, focus sessions and daily tasks."""
import random
import sqlite3
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from content import question_fields, topic_fields
from practice import expired, practice_settings, utc_now
from repetition import card_fields, deck_fields, next_review

SCHEMA_VERSION = 5


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

    def complete_practice(self, attempt_id):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            attempt = self.practice_attempt(attempt_id)
            if attempt is None:
                raise ValueError("This test no longer exists.")
            if attempt["status"] == "in_progress":
                now = utc_now()
                finished = attempt["deadline_at"] if expired(attempt["deadline_at"], now) else now.isoformat()
                self.db.execute("UPDATE practice_attempts SET status='completed',completed_at=? WHERE id=?", (finished, attempt_id))
        return self.practice_attempt(attempt_id)

    def discard_practice(self, attempt_id):
        with self.db:
            cursor = self.db.execute("DELETE FROM practice_attempts WHERE id=? AND status='in_progress'", (attempt_id,))
            if cursor.rowcount == 0:
                raise ValueError("Only an in-progress test can be discarded.")

    def decks(self):
        return [dict(row) for row in self.db.execute("""SELECT d.*,s.name AS current_subject_name,
            (SELECT COUNT(*) FROM flashcards WHERE deck_id=d.id) AS card_count,
            (SELECT COUNT(*) FROM flashcards WHERE deck_id=d.id AND due_at<=?) AS due_count
            FROM decks d LEFT JOIN subjects s ON s.id=d.subject_id ORDER BY d.name_key,d.id""", (utc_now().isoformat(),))]

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

    def update_deck(self, deck_id, name, description=""):
        name, key, description = deck_fields(name, description)
        with self.db:
            try:
                cursor = self.db.execute("UPDATE decks SET name=?,name_key=?,description=? WHERE id=?", (name, key, description, deck_id))
            except sqlite3.IntegrityError:
                raise ValueError("A deck with this name already exists.") from None
            if cursor.rowcount == 0:
                raise ValueError("This deck no longer exists.")

    def deck_deletion_state(self, deck_id):
        row = self.db.execute("""SELECT name,(SELECT COUNT(*) FROM flashcards WHERE deck_id=decks.id)
            FROM decks WHERE id=?""", (deck_id,)).fetchone()
        return tuple(row) if row else None

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
        return [dict(row) for row in self.db.execute("SELECT * FROM flashcards WHERE deck_id=? AND due_at<=? ORDER BY due_at,id LIMIT ?",
                                                   (deck_id, utc_now().isoformat(), limit))]

    def rate_flashcard(self, card_id, rating, expected_revision):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            card = self.flashcard(card_id)
            if card is None:
                raise ValueError("This card no longer exists.")
            if type(expected_revision) is not int or card["revision"] != expected_revision:
                raise ValueError("This card changed. Reveal its current answer before rating it.")
            now = utc_now()
            if card["due_at"] > now.isoformat():
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
