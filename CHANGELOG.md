# Changelog

[English](CHANGELOG.md) · [Čeština](docs/cs/CHANGELOG.md) · [Slovenčina](docs/sk/CHANGELOG.md) · [Русский](docs/ru/CHANGELOG.md)

## Unreleased

UI language selection is implemented on this branch: English, Czech, Slovak and Russian, saved separately from AI answer language and applied after restart. Current schema is 8; the published release remains v0.12.0 until release authorization. [Interface language](docs/UI_LANGUAGES.md).

## 0.12.0 — 2026-11-20

AI Tutor now saves conversations locally, including the original server/model and reply status. Open saved history without networking, reconnect explicitly to continue, or delete a selected conversation after confirmation. Released in v0.12.0 with schema 7, which migrates existing study data transactionally. [Saved AI Tutor conversations](docs/TUTOR_HISTORY.md).

## 0.11.1 — 2026-11-20

Root AGENTS.md is about 86% smaller (27.4 KB to 3.9 KB), with explicit `@` file references and a routing table. All 20 previous instruction sections are preserved across five focused English agent guides. References instruct the agent to read the files; they do not rely on automatic transclusion.

Dated session lessons record project preferences, review/release flow and safeguards for imports, Tk processes and unfinished drafts. English, Czech, Slovak and Russian versions are linked from their READMEs. The v0.11.0 handoff remains a historical baseline. Application study behavior and schema 6 are unchanged.

Validation: documentation review found no blocking issues; all original sections, local links/fences, `@` targets and language navigation were checked. All four documentation PR CI jobs passed. Release-label changes passed version, syntax and documentation checks.

## 0.11.0 — 2026-11-20

Flashcards now supports UTF-8 CSV import into an existing deck: a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records. New cards are due immediately; existing schedules and review history are preserved. Schema stays 6. [Import flashcards from CSV](docs/FLASHCARD_CSV_IMPORT.md).

Validation: 202 unit tests and all twelve native GUI checks passed locally on macOS. Independent Sol review findings were fixed and re-reviewed. All four feature PR CI jobs passed: unit tests on Linux, Windows and macOS, plus all twelve GUI checks on Ubuntu/Xvfb.

## 0.10.0 — 2026-11-19

Question bank now supports UTF-8 CSV import into an existing subject, with a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records; question lists show 50 per page. Schema stays 6. [Question CSV import](docs/QUESTION_CSV_IMPORT.md).

csv_import.py validates bounded canonical records; csv_import_worker.py runs isolated parse/read-only preflight/save/template jobs with file-backed output. Store.open_existing uses mode=ro/rw without creation or migration. Store.import_questions revalidates under BEGIN IMMEDIATE and inserts topics/questions in one transaction. A successful batch is consumed before UI report reads; refresh retry never imports again. Question-bank pagination applies filtering before selecting 50 visible cards.

Final review fixed a stale-preview risk: choosing a new file immediately clears the old batch, and subject validation stays off the Tk thread. Validation: 188 unit tests, eleven native checks across implementation and affected-fix retests, independent Sol review/re-review, and all four feature-PR CI jobs passed.

## 0.9.0 — 2026-11-19

Settings now includes manual local backup and validated restore, with a pre-restore safety copy. Schema stays 6. Restore closes the app; reopen it afterward. See [Backup and restore](docs/BACKUP_RESTORE.md).

backup.py and backup_validation.py validate private standalone snapshots and application domains, then replace rows in one write transaction without copying source DDL. database_lock.py provides shared Store leases and exclusive restore leases (flock / Windows LockFileEx). backup_worker.py runs in an isolated process; backup_panel.py polls a temporary output file on Tk, avoiding pipe deadlocks and worker-thread Tk finalization. The current Store is closed and periodic callbacks pause for actual restore. The safety copy is taken while the write lock is held; final rows and ID sequences must match before commit.

Validation: 156 unit tests and ten native macOS checks passed with disposable databases. Feature PR CI passed unit tests on Ubuntu, Windows and macOS and all ten GUI checks on Ubuntu/Xvfb. Independent Sol review findings were fixed and rechecked.

## 0.8.1 — 2026-11-18

English is now the primary documentation language in the repository root and `docs/`. Existing Czech documentation is preserved under `docs/cs/`, alongside Slovak and Russian versions. Matching-page language links and English agent instructions describe the four-language structure. Documentation-only change; the application and database schema are unchanged.

## 0.8.0 — 2026-11-18

Persistent Settings uses the study database. Schema 6 adds a singleton preferences row and revision-checked writes; transactional migration preserves all schema 5 tables/data. Older applications refuse the newer schema.

Configure the next focus duration (1–180 minutes, default 15), daily goal (1–1,440 minutes, default 60), Ollama URL, preferred model and AI answer language. Save settings explicitly persists/applies the whole form. Drafts survive navigation but not closing. Current/paused sessions retain their duration; goals update immediately without rewriting history.

Use Tutor choices copies temporary Tutor choices into the form; Save is still required. Startup, navigation and Save never connect. Missing preferred models require explicit selection. Changing servers resolves the preference afresh; refreshing the same server retains a manual choice. Answer language affects AI replies, not UI. Active AI requests block AI preference changes; study-only changes remain usable. Existing chats require New chat before moving servers. Saving the already-connected server preserves its chat; closing still loses chat.

Failed reads/writes and stale-window conflicts retain drafts. Reload confirms before replacing edits. Other-window changes apply on Save/restart, not live; Save applies all loaded fields, including AI preferences and their safeguards. Invalid saved values show safe defaults and repair only on explicit Save. Preferences are per database (`--data`), without synchronization/encryption. Themes, UI translations, backups and saved AI conversations remain future work.

Validation: 126 unit tests and nine native checks with temporary data; feature-PR CI passed on three systems and GUI on Ubuntu. Independent Sol review and re-review found no remaining issues. [Settings guide](docs/SETTINGS.md).

## 0.7.0 — 2026-11-18

Optional Ollama AI Tutor adds explicit connection/model discovery, answer-language selection, streamed replies and Stop. Other screens remain usable during generation/offline. Chat lasts only for the app session and is not saved to SQLite.

`tutor_page.py` owns chat/widgets; `tutor.py` bounds context and runs daemon workers with queue events polled by Tk every 50 ms. `ollama_client.py` uses standard http.client/ssl, GET /api/tags and streaming POST /api/chat. Workers call neither Tk nor SQLite. Shutdown cancels without waiting in the UI; failed focus saves still prevent closing. Schema remained 5; no new external dependencies.

23 new tests plus check_tutor.py use loopback FakeOllama and disposable data. They cover Unicode/protocol errors, stream/TLS cancellation, limits/context, navigation and close while generating. Total: 107 unit tests and eight GUI checks. Real-model quality/hardware requirements were not established.

## 0.6.2 — 2026-11-17

Discard obtains the write lock before checking the deadline. Expired tests are completed/retained rather than deleted; failed writes preserve state for retry. A missing attempt from another instance is terminal: Finish clears stale state and restores setup instead of retrying forever. SQLite errors remain retryable; Refresh subjects/navigation recovers setup reads.

Question forms compare an original content snapshot under the write lock, covering text/options/correct answer/difficulty/topic/explanation instead of relying on coarse timestamps. Conflicts retain drafts for copying and combining after reload. Schema remained 5.

New deck refreshes subject choices on navigation, Refresh and Save without losing title/description. Renamed subjects stay selected by ID; deletion requires an explicit replacement rather than silently choosing another subject.

Eight new unit tests and check_state_fixes.py cover lock/deadline timing, rollback, stale edits/reload, expired-discard retention, subject refresh and missing-attempt recovery. Total: 84 unit tests and seven native checks using temporary data.

## 0.6.0 — 2026-11-17

Statistics adds Last 7 days / Last 30 days / All time reports of saved time/sessions, question-weighted completed-test accuracy, card self-ratings, subject time and daily activity. Refresh/reopening loads a snapshot; this is not measured mastery.

StatisticsPage calls Store.statistics(); study_statistics.py reads sessions, completed practice snapshots and review_events in one consistent read transaction. No schema/data changes (schema 5). Read errors retain the report, Configure bindings live with widgets, and search shortcuts leave hidden drafts alone.

16 new tests cover local periods, weighting, full history/deletion retention, read-only behavior, concurrent snapshots and retry. Native checks cover empty states, filters, navigation, compact layout, scrolling and process reopen. Total: 76 unit tests and six native checks using disposable data. [Statistics guide](docs/STATISTICS.md).

## 0.5.1 — 2026-11-16

Aligned the app version, current release links, changelogs and Czech/Slovak/Russian flashcard guides with v0.5.0. Study behavior/schema unchanged; source release without installer.

## 0.5.0 — 2026-11-16

Flashcards adds deck/card CRUD, front/back search, reveal and Again / Hard / Good / Easy self-ratings. Custom deterministic scheduling is not SM-2/FSRS. Editing resets due status and retains history. Subject deletion retains decks/cards; deleting cards/decks retains review snapshots. Drafts and failed writes can be retried.

`flashcard_page.py` owns UI; `repetition.py` owns pure validation/scheduling. Schema 5 adds decks, flashcards and review_events; schedules live on cards. Revision/due checks occur under the write lock; rating, content snapshot and next due commit together. One revision cannot be rated twice. History foreign keys use SET NULL, deck-subject uses SET NULL and card-deck uses CASCADE. Migration preserves earlier content and practice results.

60 unit tests passed on Ubuntu/Windows/macOS CI; five GUI checks passed on Ubuntu/Xvfb and locally on macOS. Separate Czech/Slovak/Russian documentation; source release without installer. [Flashcard rules](docs/FLASHCARDS.md).

## 0.4.1 — 2026-11-15

Added CI with Python 3.12 syntax/dependency checks and 45 unit tests on Ubuntu/Windows/macOS, plus four GUI checks on Ubuntu/Xvfb (Tk 8.6). The first hosted run passed all jobs. Pinned actions, read-only token, timeouts and superseded-run cancellation. Added documentation in Czech/Slovak/Russian. Study features and schema unchanged from v0.4.0; no installer release. [Workflow](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml).

## 0.4.0 — 2026-11-15

Practice Tests uses subject questions with topic/difficulty filters, 1–100 random questions without repetition and optional 5/10/15/30/60-minute limits or Untimed. Answers and position save immediately; Clear answer and Previous/Next are available. One attempt may be unfinished; Resume survives restart and Discard requires confirmation.

Finish confirms submission; unanswered questions count incorrect. Correct answers/explanations appear afterward. Deadlines continue while closed/away and expired tests finish on return. Questions/options/answers are start-time snapshots, unaffected by later source edits/deletions. History shows 20 results while older rows remain stored. Practice never adds invented focus time. AI, flashcards, import and aggregate statistics were still planned at this release.

Schema 4 migration preserves subjects/questions/study history. Validation: 45 tests and four native checks on macOS; independent Sol medium review confirmed the fix preventing background completion from scrolling another screen. Manual Windows/Linux UI and physical gestures were unverified. Source-only release.

## 0.3.0 — 2026-11-14

First source release published on GitHub, combining subjects, question bank and fixes from PRs #1–#3. Version 0.2.0 was not separately released at that time. Working desktop prototype without installer.

### Features

- Native CustomTkinter Dashboard, collapsible navigation, search, daily checklist and local persistence without cloud login.
- Subject CRUD, descriptions, optional exam dates and Unicode validation.
- Per-subject topics/questions, four distinct answers, one correct choice, difficulty, optional explanation and combined text/topic/difficulty filters.
- Actual content/session counts, saved time, streaks, upcoming exams and recent activity; empty new databases.
- Subject-linked focus timer with pause/finish and retained subject-name history.
- Transactional SQLite migrations through schema 3, preserving legacy tasks/sessions and ExamPrep data-folder compatibility.
- Czech/Slovak/Russian setup, clean-Windows, cloning/Git, contribution and architecture guides; English AGENTS.md.

### Fixes

- Window close and native macOS Quit save sessions; failures retain paused time and Press Finish retry instructions.
- Navigation cancels stale deletion confirmations; changed names/content counts require renewed warning under the SQLite lock. History is retained.
- Read failures do not stop timer scheduling. Daily refresh retries and updates the header only after success.
- Same-day post-save reads retry metrics/subject choices without duplicate sessions; unsaved-session instructions stay visible.
- A gesture does not scroll both a long editor and page. Tk 9 editor scrollbar/border gestures forward to Text; short editors permit outer scrolling.
- Concurrent migrations, responsive subject columns and compact-content access fixed.

32 tests and all three native checks passed on macOS, Python 3.12.13 / Tk 9.0 / CustomTkinter 5.2.2, using temporary databases, real SQLite locks, native Quit and synthetic gestures. Manual Windows/Linux and physical trackpad behavior remained unverified. Authoring showed correct answers; practice, cards, AI, import and installers were still planned. Normal use was offline without paid services.

## 0.1.0 — 2026-11-10

Initial prototype version label, not an announcement of an installer or GitHub release at that time.

- Python/CustomTkinter Dashboard, resizable window and collapsible navigation.
- Subject search, daily checklist, 15-minute timer and SQLite storage.
- Scrolling including Tk 9 trackpad and legacy ExamPrep database compatibility.
- Storage/native checks on macOS; Windows/Linux unverified.
- Czech/Slovak/Russian documentation including clean-Windows setup; English AGENTS.md.
- Private `turcinv/SOSkuska` repository. Sample metrics and other screens remained at the stage described by that version's documentation.
