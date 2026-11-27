"""Bounded, read-only study-data queries for headless integrations.

Every function takes an open `Store` (normally `Store.open_existing(path,
readonly=True)`) and returns plain JSON-compatible dicts. Nothing here imports
Tk or MCP, and nothing writes: multi-statement reads share one deferred SQLite
read transaction so their counts agree with each other (see `practice_results`
for the one documented exception).

Results are bounded for language-model context. Limits are clamped to a
maximum, long text is shortened with a trailing ellipsis, and lists stop once
about TEXT_BUDGET characters of JSON have been collected. Whenever any text was
shortened or rows were left out by the budget, the result has `truncated: True`;
`total` versus `returned` shows rows left out by the requested limit.

Answer keys and flashcard backs are omitted unless the caller asks for them.
Stored text is the student's data: callers must treat it as data, never as
instructions.
"""
import json
import unicodedata
from contextlib import contextmanager
from datetime import date

from content import DIFFICULTIES
from study_statistics import PERIODS, RATINGS

LETTERS = "ABCD"
TEXT_BUDGET = 20_000
# Field limits equal the authoring maxima, so a question or card is never shown
# partially (four options differing after a cut would look identical). Only the
# per-result budget and free-text descriptions shorten output.
TEXT_LIMIT = 2000
OPTION_LIMIT = 500
BACK_LIMIT = 4000
DESCRIPTION_LIMIT = 400
QUERY_LIMIT = 200
RATING_NOTE = "Flashcard ratings are the student's own self-assessment, not measured mastery."
ACCURACY_NOTE = "Accuracy is correct answers divided by all questions in completed tests; unanswered questions count as wrong."


class _Clip:
    """Shortens text fields and remembers whether anything was shortened."""

    def __init__(self):
        self.truncated = False

    def __call__(self, value, limit=TEXT_LIMIT):
        if value is None:
            return None
        if len(value) <= limit:
            return value
        self.truncated = True
        return value[:limit - 1].rstrip() + "…"


def _bounded(items, clip, **extra):
    """Keep whole items until the JSON budget is spent; always keep the first one."""
    kept, used = [], 0
    for item in items:
        size = len(json.dumps(item, ensure_ascii=False))
        if kept and used + size > TEXT_BUDGET:
            clip.truncated = True
            break
        kept.append(item)
        used += size
    return {"items": kept, "returned": len(kept), "truncated": clip.truncated, **extra}


def _limit(value, default, maximum):
    if value is None:
        return default
    if type(value) is not int or value < 1:
        raise ValueError(f"Choose a limit between 1 and {maximum}.")
    return min(value, maximum)


def _record_id(value, what):
    if type(value) is not int or value < 1:
        raise ValueError(f"Use a {what} id from the list (a positive whole number).")
    return value


def _flag(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} must be true or false.")
    return value


@contextmanager
def _snapshot(store):
    # A deferred transaction takes no write lock and works on mode=ro connections.
    with store.db:
        store.db.execute("BEGIN")
        yield store.db


def _days_until(exam_date):
    if not exam_date:
        return None
    try:
        return (date.fromisoformat(exam_date) - date.today()).days
    except ValueError:
        return None


def _minutes(seconds):
    return round((seconds or 0) / 60, 1)


def _subject_summary(row, clip):
    return {
        "id": row["id"], "name": row["name"],
        "description": clip(row["description"], DESCRIPTION_LIMIT),
        "exam_date": row["exam_date"], "days_until_exam": _days_until(row["exam_date"]),
        "topic_count": row["topic_count"], "question_count": row["question_count"],
        "study_minutes": _minutes(row["study_seconds"]), "session_count": row["session_count"],
    }


def subjects_overview(store):
    """All subjects with exam dates, content counts and saved focus time."""
    clip = _Clip()
    rows = store.subjects()
    return _bounded([_subject_summary(row, clip) for row in rows], clip, total=len(rows))


def subject_detail(store, subject_id):
    """One subject plus its topics, each with question counts per difficulty."""
    _record_id(subject_id, "subject")
    clip = _Clip()
    with _snapshot(store) as db:
        row = next((row for row in store.subjects() if row["id"] == subject_id), None)
        if row is None:
            raise ValueError(f"Subject {subject_id} does not exist. List subjects to see current ids.")
        topics = [dict(t) for t in db.execute(
            "SELECT id,name FROM topics WHERE subject_id=? ORDER BY name_key,id", (subject_id,))]
        counts = db.execute("""SELECT topic_id,difficulty,COUNT(*) AS n FROM questions
            WHERE subject_id=? GROUP BY topic_id,difficulty""", (subject_id,)).fetchall()
    by_topic = {}
    for count in counts:
        by_topic.setdefault(count["topic_id"], dict.fromkeys(DIFFICULTIES, 0))[count["difficulty"]] = count["n"]
    empty = dict.fromkeys(DIFFICULTIES, 0)
    items = [{"id": t["id"], "name": t["name"], "question_count": sum(by_topic.get(t["id"], empty).values()),
              "by_difficulty": by_topic.get(t["id"], dict(empty))} for t in topics]
    unassigned = by_topic.get(None, dict(empty))
    result = _bounded(items, clip, total=len(items))
    topics_part = {"topics": result.pop("items"), "topics_returned": result.pop("returned")}
    return {**_subject_summary(row, clip), **topics_part, "topics_total": result["total"],
            "questions_without_topic": {"question_count": sum(unassigned.values()), "by_difficulty": unassigned},
            "truncated": clip.truncated}


def _fold(text):
    return unicodedata.normalize("NFKC", text).casefold()


def find_questions(store, subject_id, *, query="", topic_id="all", difficulty=None, limit=20,
                   include_answers=False, question_id=None):
    """Search a subject's question bank, newest first.

    `topic_id` is "all", None (questions without a topic) or a topic id of this
    subject. `question_id` selects exactly one question, so a host can check an
    answer to the very item it asked. The correct option and explanation are
    included only when `include_answers` is true.
    """
    _record_id(subject_id, "subject")
    limit = _limit(limit, 20, 50)
    _flag(include_answers, "include_answers")
    if not isinstance(query, str) or len(query) > QUERY_LIMIT:
        raise ValueError(f"Use a search text of at most {QUERY_LIMIT} characters.")
    if difficulty is not None and difficulty not in DIFFICULTIES:
        raise ValueError("Choose difficulty Easy, Medium or Hard, or leave it empty.")
    if topic_id not in ("all", None):
        _record_id(topic_id, "topic")
    if question_id is not None:
        _record_id(question_id, "question")
    key = _fold(query.strip())
    clip = _Clip()
    with _snapshot(store) as db:
        if store.subject(subject_id) is None:
            raise ValueError(f"Subject {subject_id} does not exist. List subjects to see current ids.")
        if topic_id not in ("all", None) and db.execute(
                "SELECT 1 FROM topics WHERE id=? AND subject_id=?", (topic_id, subject_id)).fetchone() is None:
            raise ValueError(f"Topic {topic_id} does not belong to subject {subject_id}.")
        rows = store.questions(subject_id)
    if question_id is not None and not any(q["id"] == question_id for q in rows):
        raise ValueError(f"Question {question_id} does not belong to subject {subject_id}.")
    matches = [q for q in rows
               if (question_id is None or q["id"] == question_id)
               and (topic_id == "all" or q["topic_id"] == topic_id)
               and (difficulty is None or q["difficulty"] == difficulty)
               and (not key or key in _fold("\n".join([q["prompt"], q["topic_name"] or "",
                                                         *(q["option_" + c] for c in "abcd")])))]
    items = []
    for q in matches[:limit]:
        item = {"id": q["id"], "prompt": clip(q["prompt"]),
                "options": {letter: clip(q["option_" + letter.lower()], OPTION_LIMIT) for letter in LETTERS},
                "topic_id": q["topic_id"], "topic": q["topic_name"], "difficulty": q["difficulty"]}
        if include_answers:
            item["correct_option"] = LETTERS[q["correct_option"]]
            item["explanation"] = clip(q["explanation"])
        items.append(item)
    return _bounded(items, clip, total=len(matches), answers_included=include_answers)


def decks_overview(store):
    """All flashcard decks with their subject, card count and cards due now."""
    clip = _Clip()
    rows = store.decks()
    items = [{"id": d["id"], "name": d["name"], "description": clip(d["description"], DESCRIPTION_LIMIT),
              "subject_id": d["subject_id"], "subject": d["current_subject_name"] or d["subject_name"],
              "card_count": d["card_count"], "due_count": d["due_count"]} for d in rows]
    return _bounded(items, clip, total=len(items))


def due_cards(store, deck_id, *, limit=20, include_backs=False):
    """Cards due now in one deck, in the same order as the Flashcards page."""
    _record_id(deck_id, "deck")
    limit = _limit(limit, 20, 50)
    _flag(include_backs, "include_backs")
    clip = _Clip()
    with _snapshot(store):
        deck = store.deck(deck_id)
        if deck is None:
            raise ValueError(f"Deck {deck_id} does not exist. List decks to see current ids.")
        cards = store.due_flashcards(deck_id, limit)
        total = next(d["due_count"] for d in store.decks() if d["id"] == deck_id)
    items = []
    for card in cards:
        item = {"id": card["id"], "front": clip(card["front"]), "due_at": card["due_at"],
                "review_count": card["review_count"], "interval_days": card["interval_days"]}
        if include_backs:
            item["back"] = clip(card["back"], BACK_LIMIT)
        items.append(item)
    return _bounded(items, clip, total=total, deck={"id": deck["id"], "name": deck["name"]},
                    backs_included=include_backs)


def study_report(store, period="Last 7 days", *, today=None):
    """Aggregates from the Statistics page for one period, without per-item content."""
    if period not in PERIODS:
        raise ValueError("Choose period Last 7 days, Last 30 days or All time.")
    report = store.statistics(period, today=today)
    accuracy = report["practice_accuracy"]
    return {
        "period": period, "start_day": report["start_day"], "end_day": report["end_day"],
        "focus": {"minutes": _minutes(report["focus_seconds"]), "sessions": report["sessions"],
                  "active_days": report["focus_days"],
                  "by_subject": [{"subject": row["name"], "subject_id": row["subject_id"],
                                  "minutes": _minutes(row["seconds"]), "sessions": row["sessions"]}
                                 for row in report["focus_by_subject"][:50]]},
        "practice": {"completed_tests": report["practice_completed"], "questions": report["practice_questions"],
                     "answered": report["practice_answered"], "correct": report["practice_correct"],
                     "accuracy_percent": None if accuracy is None else round(accuracy, 1), "note": ACCURACY_NOTE},
        "flashcards": {"reviews": report["reviews"],
                       "self_ratings": {rating: report["rating_counts"][rating] for rating in RATINGS},
                       "note": RATING_NOTE},
        "active_days": [{"day": day["day"], "focus_minutes": _minutes(day["seconds"]),
                         "practice_tests": day["practice"], "reviews": day["reviews"]}
                        for day in report["daily"] if day["seconds"] or day["practice"] or day["reviews"]],
    }


def practice_results(store, *, subject_name=None, limit=10):
    """Completed practice tests, newest first, scored from their saved snapshots.

    Subject names are the names saved with each attempt, so tests of deleted or
    renamed subjects keep the name they were taken under.

    `practice_history_page` opens its own read transaction, so the per-topic
    scores are read just after it. They still agree with the page: items of a
    completed attempt never change, completed attempts are never deleted, and
    restore cannot replace the file while this store holds its shared lease.
    """
    limit = _limit(limit, 10, 50)
    page = store.practice_history_page(subject_name=subject_name, page=0, page_size=limit)
    ids = [row["id"] for row in page["rows"]]
    by_attempt = {}
    if ids:
        marks = ",".join("?" for _ in ids)
        for row in store.db.execute(f"""SELECT attempt_id,topic_name,COUNT(*) AS total,
                SUM(CASE WHEN selected_option=correct_option THEN 1 ELSE 0 END) AS correct
                FROM practice_items WHERE attempt_id IN ({marks})
                GROUP BY attempt_id,topic_name ORDER BY attempt_id,topic_name""", ids):
            by_attempt.setdefault(row["attempt_id"], []).append(
                {"topic": row["topic_name"], "correct": row["correct"], "total": row["total"]})
    clip = _Clip()
    items = [{"id": a["id"], "subject": a["subject_name"], "subject_still_exists": a["subject_id"] is not None,
              "topic_filter": a["topic_name"], "difficulty_filter": a["difficulty"],
              "completed_at": a["completed_at"], "question_count": a["question_count"],
              "answered": a["answered"], "correct": a["correct"],
              "score_percent": round(a["correct"] / a["question_count"] * 100, 1),
              "time_limit_minutes": a["time_limit_minutes"], "by_topic": by_attempt.get(a["id"], [])}
             for a in page["rows"]]
    return _bounded(items, clip, total=page["total"], subjects_with_history=page["subjects"][:100])


def upcoming(store, limit=5):
    """Subjects with an exam today or later, soonest first."""
    limit = _limit(limit, 5, 20)
    clip = _Clip()
    items = [{"subject_id": row["id"], "subject": row["name"], "exam_date": row["exam_date"],
              "days_until_exam": _days_until(row["exam_date"])} for row in store.upcoming_exams(limit)]
    return _bounded(items, clip)
