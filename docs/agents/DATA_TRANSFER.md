# Backup, restore and CSV safeguards

English instructions for development agents, referenced by [AGENTS.md](../../AGENTS.md). Read this file when its routing rule applies. Paths and commands in this file are relative to the repository root.

## Backup and restore safeguards

- Current schema is 10. Backup snapshots use SQLite backup(), include committed WAL data and export standalone DELETE-mode files. Never overwrite existing outputs or active database/companion aliases; reject hard-linked active databases. POSIX publication uses atomic hard links, Windows uses no-overwrite rename.
- Only regular standalone schema 10 files are accepted. Validate a private copy for integrity, canonical structure/constraints, types/dates/aware timestamps, practice consistency, preferences and references. Never execute source DDL against the live database. Keep the private selection stable through confirmation.
- Store holds a shared database lease; restore requires an exclusive lease (POSIX flock / Windows LockFileEx). Close other current app instances; external tools/old versions must be closed manually. Keep the .lock file persistent; never unlink it while a lease may exist.
- Actual restore requires idle focus/Tutor and no target unfinished practice test; recheck on confirmation and under the write lock where applicable. Close Store, pause periodic callbacks and block editing. Create a safety snapshot under the write lock before replacing rows. Compare final rows and sequences; commit once, rollback pre-commit failures. Restore success or failure closes the app for a fresh launch.
- Database jobs run in isolated backup_worker.py processes. Do not move validation into Python threads: cyclic GC can finalize Tk objects there and crash macOS. Poll child state on Tk; use a temporary output file, never undrained pipes. Enforce the process timeout without waiting on the UI thread. Keep Quit blocked through result dialogs. Cleanup failure must not mask a committed restore.
- Tests use disposable databases. Run test_backup.py, test_backup_review.py and check_backup.py, plus affected/full checks. CI includes the tenth GUI script. Keep docs/BACKUP_RESTORE.md and cs/sk/ru versions aligned. No cloud backup, encryption or power-loss durability guarantee. Opt-in local scheduling is available in v0.18.0.

- Local backup/restore was released in v0.9.0. Current schema is 10; standalone schema 10 backups are required.

## Question CSV import safeguards

- Current schema is 10. csv_import.py validates UTF-8/BOM, comma CSV, known unique headers, 2 MiB / 500 nonblank records and existing content rules. Correct answer is A–D; difficulty is Easy/Medium/Hard. Optional topic/explanation may be omitted. Template is header-only, never sample user records.
- Preview uses Store.open_existing(mode=ro) with a shared lease and no creation/migration; save uses mode=rw. Worker argument values must handle leading-hyphen subject names. Use isolated processes and temporary output files, no Tk worker threads or undrained pipes.
- Exact duplicates include canonical question fields plus normalized topic name, both within the batch and existing subject. Never overwrite or silently skip records. Store.import_questions obtains BEGIN IMMEDIATE, rechecks subject identity/name and duplicates, reuses/creates current topics, and saves everything in one transaction. No nested CRUD commits.
- Preview is an immutable private batch; original-file edits need re-selection. Any issue disables Import all. Navigation/cancel discards reads; actual save blocks close/Quit/navigation. Consume a successful or uncertain batch before report reads. Failed report reads retry refresh only; unknown helper results may have committed and require inspection. Cleanup errors must not mask a known commit.
- Keep CSV panel separate from hidden topic/question forms and preserve drafts. Question bank filters the full subject then renders 50 cards/page; CRUD/refresh preserves/clamps the page, explicit filter/subject changes reset it.
- Template publication is atomic/no-clobber and protects database/companion paths. POSIX requires hard-link support; Windows uses no-overwrite rename.
- Run test_csv_import.py and check_csv_import.py with disposable data. CI includes the eleventh GUI check. Maintain QUESTION_CSV_IMPORT.md in all four languages. Update/merge and semicolon/legacy-encoding formats remain outside this feature.

- CSV selection must clear/disable the old batch immediately after a new filename is chosen. Capture the subject snapshot already displayed by the bank; do not make synchronous subject reads on Tk during CSV open/choose. The helper rechecks identity/name and reports read failures.

- CSV question import and 50-question bank pagination were released in v0.10.0. Current schema is 10; published version labels must match in the footer and all four README/changelog versions.

## Flashcard CSV import safeguards

- Current schema is 10. `flashcard_csv_import.py` uses existing card rules, UTF-8/BOM comma CSV with exactly front/back, 2 MiB / 500 nonblank records. Templates are header-only. Front/back retain internal whitespace and case; duplicates compare both trimmed fields exactly, within the file and full destination deck.
- `Store.import_flashcards` takes BEGIN IMMEDIATE, rechecks displayed deck identity/name and duplicates, then inserts everything once. New cards are due now with default schedule; existing schedules and immutable review events are untouched. Subject deletion does not invalidate a retained deck.
- Share the process-based CSV panel/template publication safeguards with question import. Never move database jobs to Python threads. Opening/selecting uses displayed deck snapshots without synchronous Tk SQL. The persistent importer sits outside the recreated deck body. Navigation discards previews; actual save blocks navigation/Quit. Postcommit refresh failures retry reads only; uncertain batches are consumed before inspection.
- Run `tests/test_flashcard_csv_import.py` and `soskuska/check_flashcard_import.py`, plus shared question import/full regression checks. CI has fourteen native scripts. Maintain FLASHCARD_CSV_IMPORT.md and related guides in all four languages. Flashcard CSV import was released in v0.11.0. Keep the footer, README versions and release headings aligned in all four languages.

## Frozen Windows helpers

Use worker_command.worker_command for both source and frozen launches. A frozen GUI executable is not a Python interpreter: never call it with a worker script path. The bundled sibling SOSkuska-worker.exe is a console application with stdout redirected to the existing temporary file and CREATE_NO_WINDOW; it dispatches only backup/questions/flashcards and imports no Tk. Preserve canonical CLI argument boundaries, including Unicode/spaces and leading-hyphen names. All helper resources must ship with the entire portable folder.

## Focus checkpoint safeguards (released in v0.17.0)

Schema 10 adds focus_runs. Preserve the exclusive persistent `.focus.lock`, five-second/on-Pause checkpointing, bounded 200 ms write contention and explicit paused recovery/discard. Never credit closed-process time or finalize twice. Completion keeps the local save-day policy; do not introduce midnight splitting. Configure visible controls before fallible reads; clear stale recovery actions on read failure and cancel discard on navigation/other recovery actions. A save failure must remain visible off-Dashboard, disable ineffective Resume and keep Close on Dashboard until Finish succeeds. Backups include committed focus records, validate the original subject-name domain and bounded integer revisions, and refuse restore over target pending focus. Run test_focus.py and check_focus_recovery.py. See [Focus recovery](../FOCUS_RECOVERY.md).

## Daily local schedules (v0.18.0)

Keep machine-specific consent/destination out of SQLite exports. automatic_backup.py owns atomic .backup-plan.json + persistent exclusive .backup-plan.lock, strict bounded validation, plan-ID compare-and-swap and daily receipt. Only explicit plan saves change plan_id; helper receipts must preserve it and the newest last_day/path. Hold the lease throughout snapshot and receipt publication. Another live helper is temporary busy, not folder failure. Preflight canonical UTF-8/control-safe destination and receipt size before writing a snapshot. Never overwrite/delete backups or lock files. Postpublication receipt failures may leave an extra valid copy on retry. Keep schedules opt-in and use existing standalone SQLite snapshots with shared DB leases. ScheduledBackups polls isolated file-backed processes on Tk, with bounded timeouts; errors persist across navigation and Close shows a visible root notice without consuming previews/drafts. Restore/manual jobs defer scheduling. Preserve independent form drafts and confirm Reload; do not accept another plan's CAS token under stale controls. Run test_automatic_backup.py/check_scheduled_backups.py and the full suite; Windows CI checks frozen helper automatic mode. Schema remains 10.

Reconcile a valid current-day success receipt read from another window against an older local failure: update the last path, clear the superseded runtime/root notice and do not launch another job. Invalid/older receipts and failed reads must not falsely clear an unresolved failure. Cover both callback behavior and a real external automatic helper in test_review_findings.py, plus check_scheduled_backups.py.
