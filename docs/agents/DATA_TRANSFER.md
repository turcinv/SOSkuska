# Backup, restore and CSV safeguards

English instructions for development agents, referenced by [AGENTS.md](../../AGENTS.md). Read this file when its routing rule applies. Paths and commands in this file are relative to the repository root.

## Backup and restore safeguards

- Schema remains 6. Backup snapshots use SQLite backup(), include committed WAL data and export standalone DELETE-mode files. Never overwrite existing outputs or active database/companion aliases; reject hard-linked active databases. POSIX publication uses atomic hard links, Windows uses no-overwrite rename.
- Only regular standalone schema 6 files are accepted. Validate a private copy for integrity, canonical structure/constraints, types/dates/aware timestamps, practice consistency, preferences and references. Never execute source DDL against the live database. Keep the private selection stable through confirmation.
- Store holds a shared database lease; restore requires an exclusive lease (POSIX flock / Windows LockFileEx). Close other current app instances; external tools/old versions must be closed manually. Keep the .lock file persistent; never unlink it while a lease may exist.
- Actual restore requires idle focus/Tutor and no target unfinished practice test; recheck on confirmation and under the write lock where applicable. Close Store, pause periodic callbacks and block editing. Create a safety snapshot under the write lock before replacing rows. Compare final rows and sequences; commit once, rollback pre-commit failures. Restore success or failure closes the app for a fresh launch.
- Database jobs run in isolated backup_worker.py processes. Do not move validation into Python threads: cyclic GC can finalize Tk objects there and crash macOS. Poll child state on Tk; use a temporary output file, never undrained pipes. Enforce the process timeout without waiting on the UI thread. Keep Quit blocked through result dialogs. Cleanup failure must not mask a committed restore.
- Tests use disposable databases. Run test_backup.py, test_backup_review.py and check_backup.py, plus affected/full checks. CI includes the tenth GUI script. Keep docs/BACKUP_RESTORE.md and cs/sk/ru versions aligned. No automatic/cloud backup, encryption or power-loss durability guarantee.

- Local backup/restore was released in v0.9.0. Schema remains 6; standalone schema 6 backups are required.

## Question CSV import safeguards

- Schema remains 6. csv_import.py validates UTF-8/BOM, comma CSV, known unique headers, 2 MiB / 500 nonblank records and existing content rules. Correct answer is A–D; difficulty is Easy/Medium/Hard. Optional topic/explanation may be omitted. Template is header-only, never sample user records.
- Preview uses Store.open_existing(mode=ro) with a shared lease and no creation/migration; save uses mode=rw. Worker argument values must handle leading-hyphen subject names. Use isolated processes and temporary output files, no Tk worker threads or undrained pipes.
- Exact duplicates include canonical question fields plus normalized topic name, both within the batch and existing subject. Never overwrite or silently skip records. Store.import_questions obtains BEGIN IMMEDIATE, rechecks subject identity/name and duplicates, reuses/creates current topics, and saves everything in one transaction. No nested CRUD commits.
- Preview is an immutable private batch; original-file edits need re-selection. Any issue disables Import all. Navigation/cancel discards reads; actual save blocks close/Quit/navigation. Consume a successful or uncertain batch before report reads. Failed report reads retry refresh only; unknown helper results may have committed and require inspection. Cleanup errors must not mask a known commit.
- Keep CSV panel separate from hidden topic/question forms and preserve drafts. Question bank filters the full subject then renders 50 cards/page; CRUD/refresh preserves/clamps the page, explicit filter/subject changes reset it.
- Template publication is atomic/no-clobber and protects database/companion paths. POSIX requires hard-link support; Windows uses no-overwrite rename.
- Run test_csv_import.py and check_csv_import.py with disposable data. CI includes the eleventh GUI check. Maintain QUESTION_CSV_IMPORT.md in all four languages. Update/merge and semicolon/legacy-encoding formats remain outside this feature.

- CSV selection must clear/disable the old batch immediately after a new filename is chosen. Capture the subject snapshot already displayed by the bank; do not make synchronous subject reads on Tk during CSV open/choose. The helper rechecks identity/name and reports read failures.

- CSV question import and 50-question bank pagination were released in v0.10.0. Schema stays 6; published version labels must match in the footer and all four README/changelog versions.

## Flashcard CSV import safeguards

- Schema stays 6. `flashcard_csv_import.py` uses existing card rules, UTF-8/BOM comma CSV with exactly front/back, 2 MiB / 500 nonblank records. Templates are header-only. Front/back retain internal whitespace and case; duplicates compare both trimmed fields exactly, within the file and full destination deck.
- `Store.import_flashcards` takes BEGIN IMMEDIATE, rechecks displayed deck identity/name and duplicates, then inserts everything once. New cards are due now with default schedule; existing schedules and immutable review events are untouched. Subject deletion does not invalidate a retained deck.
- Share the process-based CSV panel/template publication safeguards with question import. Never move database jobs to Python threads. Opening/selecting uses displayed deck snapshots without synchronous Tk SQL. The persistent importer sits outside the recreated deck body. Navigation discards previews; actual save blocks navigation/Quit. Postcommit refresh failures retry reads only; uncertain batches are consumed before inspection.
- Run `tests/test_flashcard_csv_import.py` and `soskuska/check_flashcard_import.py`, plus shared question import/full regression checks. CI has twelve native scripts. Maintain FLASHCARD_CSV_IMPORT.md and related guides in all four languages. Flashcard CSV import was released in v0.11.0. Keep the footer, README versions and release headings aligned in all four languages.
