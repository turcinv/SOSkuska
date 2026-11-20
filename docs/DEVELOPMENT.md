# Development and setup

[English](DEVELOPMENT.md) · [Čeština](cs/DEVELOPMENT.md) · [Slovenčina](sk/DEVELOPMENT.md) · [Русский](ru/DEVELOPMENT.md)

Start with the [Git guide](GIT_GUIDE.md) if you do not have the project. Read [Contributing](../CONTRIBUTING.md) before changing it. Run commands from the repository root. The application currently uses scripts in `soskuska/`, not an installable package.

## Prepared Mac: fastest path

```sh
cd "$HOME/Documents/SOSkuska"
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

The development database is separate from ordinary user data. Its parent directory is created automatically; `.local-data/` is Git-ignored. Without `--data`, the app opens the normal user database instead. `soskuska/run-macos.command` accepts the same arguments.

## Requirements

The verified local environment is Python 3.12.13 / Tk 9.0 / CustomTkinter 5.2.2. Use Python 3.12 with Tk to reproduce it. macOS requires at least Tk 8.6; Python's version alone does not guarantee Tk support.

External dependencies are in `soskuska/requirements.txt`. There is no complete lockfile; pip resolves transitive versions. Installation needs internet, but normal study then works offline. Ollama is optional. GUI checks need a graphical desktop session.

## New macOS environment

```sh
python3.12 -c "import sys, tkinter; print(sys.executable); print(sys.version); print('Tk', tkinter.TkVersion)"
python3.12 -m venv .venv-macos
.venv-macos/bin/python -m pip install -r soskuska/requirements.txt
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

On the current developer's Mac, `/Users/turcinv/.local/bin/python3.12` is also suitable. `/usr/bin/python3` used old system Tk 8.5; Homebrew `python3` lacked `_tkinter` when checked. Silencing the warning with `TK_SILENCE_DEPRECATION` does not fix an empty window. Do not assume these machine-specific paths apply elsewhere.

If an existing environment uses another Python, create a new environment with a different name and adjust commands. Installing libraries does not replace its base interpreter. The Mac launcher specifically expects `.venv-macos`.

## Windows / PowerShell

With nothing installed, follow [Windows first run](WINDOWS_FIRST_RUN.md). This abbreviated procedure assumes Python 3.12, Tcl/Tk and the `py` launcher already work:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r soskuska/requirements.txt
.\.venv\Scripts\python.exe -c "import tkinter; print(tkinter.TkVersion)"
.\.venv\Scripts\python.exe soskuska/app.py --data .local-data/dev.sqlite3
```

No activation or execution-policy change is needed. Unit CI runs on Windows; the complete manual first-run/UI walkthrough remains unverified.

## Linux

Use Python with Tk and virtual-environment support. Common system package names are `python3-tk` and `python3-venv`; exact names depend on your distribution and must match the selected Python.

```sh
python3 -c "import sys, tkinter; print(sys.version); print('Tk', tkinter.TkVersion)"
python3 -m venv .venv
.venv/bin/python -m pip install -r soskuska/requirements.txt
.venv/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

A server without a graphical session cannot display the window. Linux GUI CI uses Xvfb; it does not replace manual desktop testing.

## Checks

Syntax and unit tests without opening the application window:

```sh
.venv-macos/bin/python -m compileall -q soskuska tests
.venv-macos/bin/python -m unittest discover -s tests -v
```

Native checks use disposable databases and open real windows:

```sh
.venv-macos/bin/python soskuska/check_dashboard.py
.venv-macos/bin/python soskuska/check_question_bank.py
.venv-macos/bin/python soskuska/check_review_fixes.py
.venv-macos/bin/python soskuska/check_practice.py
.venv-macos/bin/python soskuska/check_flashcards.py
.venv-macos/bin/python soskuska/check_statistics.py
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
.venv-macos/bin/python soskuska/check_settings.py
```

Use the corresponding environment executable on Windows/Linux. For example:

```powershell
.\.venv\Scripts\python.exe soskuska/check_settings.py
```

Checks print `PASS` and close their windows on success. They never use the normal user database. The Dashboard script has a 12-second Tk safeguard, not a hard process timeout if the event loop freezes; use Ctrl+C in that case. CI adds a 60-second external timeout per script.

Backup/restore validation on this branch passed 234 unit tests and fourteen native checks locally. Do not present old results as validation of untested code changes. Coverage includes:

| Check / tests | Main coverage |
| --- | --- |
| `check_dashboard.py`, `test_storage.py`, `test_subjects.py` | Empty database, real metrics, subject CRUD/Unicode/exam dates, session links/history, wide/compact columns, search, synthetic scrolling, timer retry, midnight checklist, concurrent migrations |
| `check_question_bank.py`, `test_questions.py` | Topic/question CRUD, combined filters, subject isolation, compact editor, retained history, schema 2 fixture migration |
| `check_review_fixes.py` | Stale deletion warnings, real SQLite locks, failed reads/writes, daily header/retry, no duplicate sessions, nested editor/scrollbar gestures; native macOS Quit in a bounded child process |
| `check_practice.py`, `test_practice.py` | Setup, answer save/retry, scoring, immutable snapshots, UTC deadlines, idempotent completion, fresh-process resume, no scroll/draft changes on another screen |
| `check_flashcards.py`, `test_flashcards.py` | Draft retention, repeated search, reveal/rating guard, stale revisions, write retry, scheduling/history, fresh process, frozen schema 4 migration |
| `check_statistics.py`, `test_statistics.py` | Empty state, local periods, weighted accuracy, full history, consistent read snapshot, retry, compact layout, scrolling and fresh process |
| `check_state_fixes.py` | Question conflicts/reload, refreshed deck-subject choices, expired-discard preservation, missing-attempt recovery and transient errors |
| `check_tutor.py`, `test_tutor.py` | Loopback fake Ollama, Unicode/stream errors, Stop/TLS cancellation, context bounds, navigation, clearing and close while generating |
| `check_settings.py`, `test_preferences.py`, `test_settings_ui.py` | Atomic/stale preference writes, migration/rollback from frozen schema 5, kept drafts, active timer target, fresh-process persistence, no auto-connection, per-server model choice |

After UI changes, manually check 1440 × 900 and 1024 × 700, access to lower content, actual scrolling gestures, sidebar, search, Ctrl+K / Cmd+K and Escape. For persistence changes, edit the checklist, finish a short session and restart to inspect saved data. There is no automatic code reload: restart the app.

## CI

`.github/workflows/ci.yml` runs on PRs targeting main, pushes to main and manual dispatch. Python 3.12 syntax, dependencies and unit tests run on Ubuntu, Windows and macOS; fourteen GUI checks run under Xvfb on Ubuntu. Each process has a 60-second timeout, each job 10 minutes. Newer runs cancel superseded runs for the same ref. Actions are pinned and the token can only read contents. CI does not deploy, publish releases or configure branch protection.

Read the first failing step in [Actions](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml), fix it and push to the same branch. Do not disable meaningful checks to get green results. Linux GUI checks do not establish native Aqua Quit or Tk 9 hardware trackpad behavior. Fake Ollama does not establish real-model quality or performance.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Empty window / system Tk warning | Check interpreter and Tk; use `.venv-macos` on the prepared Mac |
| `No module named _tkinter` | Choose Python built with Tk; installing CustomTkinter alone will not fix it |
| `No module named customtkinter` | Install requirements through the same interpreter used to launch |
| Trackpad does not scroll | Use current `scrolling.py` and restart; Tk 9 needs `TouchpadScroll` |
| SQLite write error | Select a writable `--data` path; check permissions and free space |
| Earlier data missing | Compare `--data` with the normal user database path |

## Data and further development

If no fresh `SOSkuska` database exists but legacy `ExamPrep/dashboard.sqlite3` does, the app uses that file without copying, moving or overwriting it. Explicit `--data` wins. Schema 7 migration preserves prior records; older apps refuse newer schemas. [Settings](SETTINGS.md) explains revision conflicts and explicit preference application.

`app.py` owns Dashboard/timer/navigation; `storage.py` owns SQL and migrations; `scrolling.py` owns scrolling compatibility. Other screens have their own modules. HTML under `soskuska-local/` is only a visual reference. See [planned architecture](PLANNED_ARCHITECTURE.md) for gradual restructuring, [Flashcards](FLASHCARDS.md), [Statistics](STATISTICS.md) and [AI Tutor](AI_TUTOR.md) for feature rules.

Keep environments, SQLite files, caches and local tool configuration out of Git. The repository [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska) remains private.

## Backup and restore

Settings now includes manual local backup and validated restore, with a pre-restore safety copy. Current schema is 8. Restore closes the app; reopen it afterward. See [Backup and restore](BACKUP_RESTORE.md).

`tests/test_backup.py`, `tests/test_backup_review.py`, `soskuska/check_backup.py`.

```sh
.venv-macos/bin/python soskuska/check_backup.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_backup.py
```

## Import questions from CSV

Question bank now supports UTF-8 CSV import into an existing subject, with a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records; question lists show 50 per page. Current schema is 8. [Question CSV import](QUESTION_CSV_IMPORT.md).

`tests/test_csv_import.py`, `soskuska/check_csv_import.py`.

```sh
.venv-macos/bin/python soskuska/check_csv_import.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_csv_import.py
```

## Import flashcards from CSV

Flashcards now supports UTF-8 CSV import into an existing deck: a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records. New cards are due immediately; existing schedules and review history are preserved. Current schema is 8. [Import flashcards from CSV](FLASHCARD_CSV_IMPORT.md).

`tests/test_flashcard_csv_import.py`, `soskuska/check_flashcard_import.py`.

```sh
.venv-macos/bin/python soskuska/check_flashcard_import.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_flashcard_import.py
```

## Saved AI Tutor conversations

AI Tutor now saves conversations locally, including the original server/model and reply status. Open saved history without networking, reconnect explicitly to continue, or delete a selected conversation after confirmation. Released in v0.12.0 with schema 7, which migrates existing study data transactionally. [Saved AI Tutor conversations](TUTOR_HISTORY.md).

`tests/test_tutor_history.py`, `soskuska/check_tutor_history.py`.

```sh
.venv-macos/bin/python soskuska/check_tutor_history.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_tutor_history.py
```

## Interface language

UI language selection is available in v0.13.0: English, Czech, Slovak and Russian, saved separately from AI answer language and applied after restart. Current schema is 8. [Interface language](UI_LANGUAGES.md).

`tests/test_localization.py`, `soskuska/check_ui_languages.py`.

```sh
.venv-macos/bin/python soskuska/check_ui_languages.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_ui_languages.py
```
