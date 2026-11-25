# Study feature safeguards

English instructions for development agents, referenced by [AGENTS.md](../../AGENTS.md). Read this file when its routing rule applies. Paths and commands in this file are relative to the repository root.

## Question bank

Open Questions from a subject card. Questions have four distinct answers, one correct answer (0–3), difficulty and optional explanation/topic. Topics are unique within a subject. Deleting a topic keeps its questions unassigned; deleting a subject explicitly warns and cascades its content while retaining session history. Schema 3 migrates existing data transactionally. Use `tests/test_questions.py` and `check_question_bank.py` for verification; all automated checks use disposable data. Practice execution, saved answers, resume, deadlines and snapshot scoring are implemented in `practice_page.py`, `practice.py` and Store; flashcards are implemented in flashcard_page.py with pure rules in repetition.py; AI Tutor with local history is implemented.

## Practice safeguards

- One in-progress practice attempt globally, enforced by a partial unique SQLite index. Configure subject/topic/difficulty, 1–100 questions, and optional time limit. Never seed user content.
- Snapshot questions/options/correct answers/explanations on start. History and unfinished attempts survive source edits/deletions; completed results are read-only through the API. Never expose correct answers in the running test UI.
- Save each answer and navigation position transactionally. On failed answer writes restore the last saved choice. Deadline checks occur after obtaining the write lock. Completion is idempotent; failed result reads may retry without creating another result.
- UTC deadlines continue while away or closed. On reopening, expired tests complete and reject late answers. System-clock changes can affect remaining time. Discard requires confirmation and applies only to an unfinished attempt.
- Practice results do not count as focus-session time. History exposes all completed results in pages of 20, using saved subject names and inclusive local completion dates. Apply filters explicitly; preserve drafts, prior rows and applied page on read failure. Query names/count/rows in one deferred read transaction. No schema change (8). Schema 4 migration preserves all existing content/history.
- Run `tests/test_practice.py`, `tests/test_practice_history.py`, `check_practice.py` and `check_practice_history.py` with temporary data. The native check covers fresh-process resume, write errors and timed completion, in addition to the existing native checks.

- History filters/sorting must parse the same timezone-aware ISO timestamps as result display and backup validation. Normalize chronology to UTC including microseconds; use local calendar days for date bounds. Raw SQLite date()/text ordering misses accepted offset variants. Initialize retry controls before the first read; do not require a prior successful load.

- Background practice completion must not reset the shared scroll canvas or affect another screen's editing draft. Only reset practice scrolling when Practice Tests is active.

## Flashcard safeguards

- Schema 5 adds decks, flashcards and immutable review_events. Deck names are globally Unicode-normalized unique. Subject deletion keeps decks/cards, card/deck deletion keeps review snapshots; communicate this in confirmation text.
- Custom deterministic scheduling in repetition.py: Again 10m/reset, new Hard 1h, new Good 1d, new Easy 4d; mature Hard/Good/Easy multiply days by 1.2/2.5/3.5 and round up, capped365d. Do not label it SM-2/FSRS or claim measured mastery. Ratings are self-assessments.
- Reveal before enabling rating. Compare card revision and due time under the write lock, commit schedule and review snapshot together. Advance UI only after commit. A stale callback cannot rate the next card or a hidden page. Failed writes keep revealed content/drafts for retry.
- Editing resets due/interval but keeps historical reviews. Study at most100 due cards per batch; history shows20, older rows remain stored. UTC system-clock changes can affect due status.
- Avoid binding a persistent StringVar to repeatedly recreated CTkEntry widgets in CTk5.2.2; destroyed entries retain traces. Flashcard search copies text through public entry APIs instead.
- Run tests/test_flashcards.py (including historical schema4 fixture) and check_flashcards.py. CI includes the fifth native check. Flashcards were released in v0.5.0.

## Statistics safeguards

- StatisticsPage uses Store.statistics() / study_statistics.py. Keep all four read aggregates in one deferred SQLite transaction; no writes or migration. Statistics introduced no schema change (schema 5 in v0.6.0; current schema is 9).
- Last 7/30 days includes today and previous 6/29 local calendar days; all-time totals exclude future days and chart only the latest 30 days. Focus uses stored local day; UTC completion/review times use SQLite localtime. Time-zone changes can rebucket events.
- Practice accuracy is total correct / total questions from completed snapshots; unanswered questions count incorrect, unfinished/discarded tests excluded. Include full retained history beyond Flashcards’ 20-row review-history display limit.
- Flashcard ratings are self-assessments, not accuracy/mastery. Never infer focus time from tests/reviews. Empty history has zero counts and no percentage. Keep deleted/unassigned focus history visible and document name-based grouping after deletion.
- Refresh or reopening loads a new snapshot. Read failure preserves the previous report with a retry notice. Resize bindings must die with their labels; do not accumulate Configure callbacks on persistent report containers. Statistics shortcuts must not modify hidden search drafts.
- Run tests/test_statistics.py and check_statistics.py with disposable data. CI includes the sixth native check. Statistics was released in v0.6.0.


## Main review findings (v0.18.1)

SubjectPage passes its original editable subject snapshot to update_subject; compare actual values under BEGIN IMMEDIATE, never only updated_at. Conflicts keep the form/draft. Question/topic delete callbacks retain the displayed snapshot and recheck atomically; stale data returns False, clears the old confirmation and displays a changed warning beside Confirm with a fresh snapshot. Missing records clear pending state. Reopening the same subject must retain the question/topic editor, original edit snapshot, filters and text. Preserve selected topic IDs through rename; deleted choices remain unavailable and block Save until explicit replacement, including when a new topic reuses the old name. Entry-point and refresh errors must reopen the retained editor with a retry notice. New subject navigation may reset the single-subject editor. Run test_review_findings.py/check_state_fixes.py and affected checks. Track status and evidence in docs/REVIEW_FINDINGS.md.

## Practice UI review safeguards

Show saved answer selection independently of correctness and restore both radio value and row style after a failed write. Guard every answer callback with the active Practice page and gridded run panel; a hidden but still-enabled radio must not mutate the attempt. Count committed answers in progress. CTkFrame.bind delivers canvas Configure events, so widget-local width handlers must accept them and convert native widths to logical CTk units. Audit checked/hover indicators against selected surfaces. GUI checks exercise row canvas/text events, off-page events with run still gridded, rollback, navigation/resume and long-text footer reachability at startup scaling in four languages.

### Flashcard review footer and refresh

Keep reveal/rating controls in the same footer; order is Again, Hard, Good, Easy. Hidden ratings remain disabled until Reveal. Treat `review_refresh_pending` as UI-only committed-write state: invalidate the old card and disable its ratings before reading the next card, then clear the flag only after that read succeeds. A failed write retains the revealed card for retry. Surface errors beside the footer as well as the page status; localize referenced action names. Test the next-card read separately from precommit Store validation.
