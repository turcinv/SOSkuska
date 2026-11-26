"""Read-only statistics over saved history; no Tk or extra dependencies."""
from datetime import date, timedelta

PERIODS = {"Last 7 days": 7, "Last 30 days": 30, "All time": None}
RATINGS = ("Again", "Hard", "Good", "Easy")


def statistics_report(db, period="Last 7 days", *, today=None):
    """Return one consistent snapshot. UTC events are bucketed in system local time.

    Focus sessions already store a local save date. All ranges include today and
    exclude future calendar days. All-time totals keep full history; the daily
    chart contains at most the latest 30 days. This function never writes data.
    """
    if period not in PERIODS:
        raise ValueError("Choose Last 7 days, Last 30 days or All time.")
    today = today or date.today()
    days = PERIODS[period]
    start = today - timedelta(days=days - 1) if days else None
    end_text = today.isoformat()
    start_text = start.isoformat() if start else "0001-01-01"
    params = (start_text, end_text)
    # A deferred read transaction keeps all aggregates on the same SQLite
    # snapshot without taking a write lock or altering the database schema.
    with db:
        db.execute("BEGIN")
        focus = [dict(row) for row in db.execute("""
            SELECT day, SUM(seconds) AS seconds, COUNT(*) AS sessions
            FROM sessions WHERE seconds>0 AND day BETWEEN ? AND ?
            GROUP BY day ORDER BY day""", params)]
        practice = [dict(row) for row in db.execute("""
            SELECT study_local_day(a.completed_at) AS day,
                   COUNT(*) AS attempts, SUM(a.question_count) AS questions,
                   SUM(COALESCE(i.answered,0)) AS answered,
                   SUM(COALESCE(i.correct,0)) AS correct
            FROM practice_attempts a LEFT JOIN (
                SELECT attempt_id,
                    SUM(selected_option IS NOT NULL) AS answered,
                    SUM(CASE WHEN selected_option=correct_option THEN 1 ELSE 0 END) AS correct
                FROM practice_items GROUP BY attempt_id
            ) i ON i.attempt_id=a.id
            WHERE a.status='completed' AND study_local_day(a.completed_at) BETWEEN ? AND ?
            GROUP BY day ORDER BY day""", params)]
        reviews = [dict(row) for row in db.execute("""
            SELECT study_local_day(reviewed_at) AS day, rating, COUNT(*) AS count
            FROM review_events WHERE study_local_day(reviewed_at) BETWEEN ? AND ?
            GROUP BY day,rating ORDER BY day,rating""", params)]
        subjects = [dict(row) for row in db.execute("""
            SELECT s.subject_id,
                   CASE WHEN s.subject_id IS NOT NULL THEN p.name ELSE s.subject_name END AS name,
                   SUM(s.seconds) AS seconds, COUNT(*) AS sessions
            FROM sessions s LEFT JOIN subjects p ON p.id=s.subject_id
            WHERE s.seconds>0 AND s.day BETWEEN ? AND ?
            GROUP BY s.subject_id, CASE WHEN s.subject_id IS NULL THEN s.subject_name END
            ORDER BY seconds DESC, name COLLATE NOCASE""", params)]
    rating_counts = {rating: 0 for rating in RATINGS}
    for row in reviews:
        rating_counts[row["rating"]] += row["count"]
    chart_start = start or today - timedelta(days=29)
    by_day = {}
    for offset in range((today - chart_start).days + 1):
        day = (chart_start + timedelta(days=offset)).isoformat()
        by_day[day] = {"day": day, "seconds": 0, "practice": 0, "reviews": 0}
    for row in focus:
        if row["day"] in by_day:
            by_day[row["day"]]["seconds"] = row["seconds"]
    for row in practice:
        if row["day"] in by_day:
            by_day[row["day"]]["practice"] = row["attempts"]
    for row in reviews:
        if row["day"] in by_day:
            by_day[row["day"]]["reviews"] += row["count"]
    questions = sum(row["questions"] for row in practice)
    correct = sum(row["correct"] for row in practice)
    return {
        "period": period, "start_day": start.isoformat() if start else None,
        "end_day": end_text, "chart_start_day": chart_start.isoformat(),
        "focus_seconds": sum(row["seconds"] for row in focus),
        "sessions": sum(row["sessions"] for row in focus), "focus_days": len(focus),
        "practice_completed": sum(row["attempts"] for row in practice),
        "practice_questions": questions, "practice_correct": correct,
        "practice_answered": sum(row["answered"] for row in practice),
        "practice_accuracy": correct / questions * 100 if questions else None,
        "reviews": sum(rating_counts.values()), "rating_counts": rating_counts,
        "focus_by_subject": subjects, "daily": list(by_day.values()),
    }


def duration(seconds):
    """Keep sub-minute saved sessions visible instead of rounding to zero."""
    hours, rest = divmod(seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"
