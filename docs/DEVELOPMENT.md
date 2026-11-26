# Development and setup

[English](DEVELOPMENT.md) · [Čeština](cs/DEVELOPMENT.md) · [Slovenčina](sk/DEVELOPMENT.md) · [Русский](ru/DEVELOPMENT.md)

[Container tests](CONTAINER_TESTS.md).

```sh
docker build -f Dockerfile.tests -t soskuska-tests .
docker run --rm --init --network none --cpus 2 --memory 2g soskuska-tests
```

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
.venv-macos/bin/python soskuska/check_practice_history.py
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

Backup/restore validation on this branch passed 244 unit tests and fifteen native checks locally. Do not present old results as validation of untested code changes. Coverage includes:

| Check / tests | Main coverage |
| --- | --- |
| `check_dashboard.py`, `test_storage.py`, `test_subjects.py` | Empty database, real metrics, subject CRUD/Unicode/exam dates, session links/history, wide/compact columns, search, synthetic scrolling, timer retry, midnight checklist, concurrent migrations |
| `check_focus_recovery.py`, `test_focus.py` | Process crash/reopen, paused recovery, exclusive ownership, bounded failures, atomic completion/discard and schema-9 migration |
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

`.github/workflows/ci.yml` runs on PRs targeting main, pushes to main and manual dispatch. Python 3.12 syntax, dependencies and unit tests run on Ubuntu, Windows and macOS; fifteen GUI checks run under Xvfb on Ubuntu. Each process has a 60-second timeout, each job 10 minutes. Newer runs cancel superseded runs for the same ref. Actions are pinned and the token can only read contents. CI does not deploy, publish releases or configure branch protection.

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

If no fresh `SOSkuska` database exists but legacy `ExamPrep/dashboard.sqlite3` does, the app uses that file without copying, moving or overwriting it. Explicit `--data` wins. Schema 10 migration preserves prior records; older apps refuse newer schemas. [Settings](SETTINGS.md) explains revision conflicts and explicit preference application.

`app.py` owns Dashboard/timer/navigation; `storage.py` owns SQL and migrations; `scrolling.py` owns scrolling compatibility. Other screens have their own modules. HTML under `soskuska-local/` is only a visual reference. See [planned architecture](PLANNED_ARCHITECTURE.md) for gradual restructuring, [Flashcards](FLASHCARDS.md), [Statistics](STATISTICS.md) and [AI Tutor](AI_TUTOR.md) for feature rules.

Keep environments, SQLite files, caches and local tool configuration out of Git. The repository [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska) remains private.

## Backup and restore

Settings now includes manual local backup and validated restore, with a pre-restore safety copy. Current schema is 10. Restore closes the app; reopen it afterward. See [Backup and restore](BACKUP_RESTORE.md).

`tests/test_backup.py`, `tests/test_backup_review.py`, `soskuska/check_backup.py`.

```sh
.venv-macos/bin/python soskuska/check_backup.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_backup.py
```

## Import questions from CSV

Question bank now supports UTF-8 CSV import into an existing subject, with a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records; question lists show 50 per page. Current schema is 10. [Question CSV import](QUESTION_CSV_IMPORT.md).

`tests/test_csv_import.py`, `soskuska/check_csv_import.py`.

```sh
.venv-macos/bin/python soskuska/check_csv_import.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_csv_import.py
```

## Import flashcards from CSV

Flashcards now supports UTF-8 CSV import into an existing deck: a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records. New cards are due immediately; existing schedules and review history are preserved. Current schema is 10. [Import flashcards from CSV](FLASHCARD_CSV_IMPORT.md).

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

UI language selection is available in v0.13.0: English, Czech, Slovak and Russian, saved separately from AI answer language and applied after restart. Current schema is 10. [Interface language](UI_LANGUAGES.md).

`tests/test_localization.py`, `soskuska/check_ui_languages.py`.

```sh
.venv-macos/bin/python soskuska/check_ui_languages.py
```

```powershell
.\.venv\Scripts\python.exe soskuska/check_ui_languages.py
```

## Practice history

Practice history now supports pages of 20 across all completed attempts, historical subject-name and inclusive local-date filters, and reopening saved answer reviews. Filter drafts and the applied page survive navigation; failed reads keep prior results. Schema remains 8. [Practice history](PRACTICE_HISTORY.md).

```sh
python soskuska/check_practice_history.py
```

## Windows portable build and acceptance

v0.15.0 adds an unsigned Windows x64 portable ZIP, built and checked by a fifth CI job. Bundled helper executables preserve isolated CSV/backup jobs; Python is not required on the target machine. Automated hosted Windows checks and the manual clean-machine checklist are separate; manual acceptance is not yet completed. Published version is v0.18.1, schema 10. [Windows portable build and acceptance](WINDOWS_PORTABLE.md) · [Checklist](WINDOWS_ACCEPTANCE.md).

Current packaging work: 251 unit tests passed locally. The Linux container passed all 15 GUI scripts (250 unit tests at that source snapshot, two filesystem-specific skips). No native Mac GUI suite was run for this branch. Hosted Windows build evidence is recorded separately; manual acceptance remains NOT RUN.

## Appearance settings

v0.16.0 adds saved Light/Dark/System choices, applied on Save without rebuilding screens or losing active work. System follows Windows/macOS and uses Light on Linux. Current schema is 10. The user confirmed baseline testing complete and approved merging appearance PR #32 on 22 November 2026. [Appearance settings](APPEARANCE.md).

```sh
python soskuska/check_appearance.py
```

## Focus-session recovery

v0.17.0 adds focus-session crash recovery using schema **10**. Keep a backup before opening existing data: migration is transactional, but v0.16.0 cannot open a schema-10 database. [Focus-session recovery](FOCUS_RECOVERY.md).

## Scheduled local backups

Scheduled local backups are available in **v0.18.0**. SQLite schema remains **10**. Manual backup/restore continues to work independently. [Scheduled local backups](SCHEDULED_BACKUPS.md).

## Main-branch review fixes

Fixes released in v0.18.1 through PR #38, tracked in [Astra review findings](REVIEW_FINDINGS.md). Schema remains 10 and the published version is v0.18.1. Subject edits compare their original content under the write lock; a conflict keeps your draft. Copy any changes you need before reopening Edit to load the latest version. Question/topic deletions recheck their displayed snapshot and require a refreshed confirmation after changes. Returning to the same subject preserves the active question/topic editor, filters and original editing identity, including read retries; a removed selected topic stays unavailable until you explicitly choose a replacement or No topic. Opening a different subject still resets the editor. A newer successful daily-backup receipt clears the old failure notice without another backup write.


## Question explanations · v0.25.0

Completed Practice results, including reopened history, offer **Explain this question**. Open the local preview, then choose **Prepare in Tutor**. It uses the saved question snapshot (all four choices, selected answer or Unanswered, stored answer key and explanation), even after the original question/subject is deleted. Nothing connects or sends during preview/preparation. In Tutor, review the server, model and answer language, explicitly Connect if needed, then Send. The draft is editable and uses ordinary local chat history, Stop and save-retry paths.

Tutor must be an idle, clean New chat with an empty prompt and no pending confirmation or unsaved reply. Existing work is preserved; finish it or explicitly use the confirmed New chat action before retrying. A complete generated prompt above 4,000 characters is rejected with its measured length; nothing is truncated. The saved answer key and AI explanation may be wrong; scores and source content never change. Automatic asks for the supplied question language; explicit answer language overrides it. Prompt instructions stay in English and user content stays unchanged. No schema change (10), released version is v0.30.0.

Implementation: `question_explanation.py` builds/validates the bounded snapshot prompt; `practice_page.py` owns preview and stale-result checks; `tutor_page.py` guards draft insertion. Existing Send persists the prompt before HTTP. Automated checks use disposable data and loopback FakeOllama; real-model quality and native platform/DPI acceptance remain manual.


## AI study modes · v0.26.0

In a completed result, open **Explain this question**, then choose **Study mode** before **Prepare in Tutor**. **Explain answer** keeps the existing explanation; **Explain simply** requests short beginner-friendly steps and an example; **Give me a hint** requests one conceptual hint and omits your selected answer, stored key and explanation from the prompt; **Quiz me** asks one new follow-up at a time, waiting for your response before feedback. This is informal practice and never writes a scored attempt or changes source content.

Changing mode regenerates the exact local preview and invalidates its previous Prepare action. Nothing connects, sends or creates a conversation until the existing explicit controls are used. The sent prompt is saved in ordinary local chat history, with the existing language, 4,000-character bound, clean-chat guard, Stop and save-retry rules. Hint mode still includes all four choices: a model may infer/reveal the answer, and text already visible in completed results remains visible. Mode following and explanation quality require later real-model testing, explicitly deferred by the user. Automated checks use loopback FakeOllama. Released version is v0.30.0 / schema 10.


## Astra review fixes · v0.26.1

Deck and topic editors now compare the original editable snapshot under the write lock. A conflict keeps the draft and shows a warning; copy needed changes before reopening Edit deck or Rename topic to load the current record. Deck warnings also appear beside Save. Once a deck save commits, a failed display refresh changes Save to Refresh deck and retries only the read, without repeating or overwriting the save.

Flashcard due counts, ordered queues, rating and review checks compare timezone-aware instants, including restored offsets and microseconds. Statistics and history share local-day parsing for accepted ISO timestamps, including offsets with seconds. No stored timestamps are rewritten. Exact integer UTC keys cover the full accepted date range; if the host cannot convert an extreme date to local time, reports use its UTC day clamped to the supported calendar. Restore requires standalone schema 10; migration descriptions remain historical. Released version is v0.30.0 / schema 10. Real-model testing remains deferred.


## Study studio redesign · v0.27.0

A new Dashboard composition replaces the earlier incremental bright UI layout: four summary tiles, a large focus room with a live circular clock, monogram-led subject cards and a saved-date month agenda. The persistent sidebar uses locally drawn icons and separate dark navigation colors; shared card surfaces and paired Dark/Light styling update across the app. This stage implements the Dashboard and shared shell; remaining page compositions follow visual feedback. [Design evidence and scope](agents/design/study-studio-dashboard/README.md).

The clock uses actual remaining time and the active session's original target. Calendar marks use the complete subject snapshot, while the upcoming list keeps exact saved dates and its top-five limit. Keyboard search, focus-save retry and pending recovery reveal their controls in compact windows; deferred reveals cancel on navigation/search. Reflow performs no I/O. Schema remains 10 and the released version is v0.30.0. Container/synthetic scaling coverage is separate from native platform acceptance; real-model testing remains deferred.


## Brand assets

Run `python tools/build_brand_assets.py` with the project environment to rebuild the committed SVG, PNG, ICO and ICNS files in `soskuska/assets/brand/`. The generator needs only Pillow; restart the app afterward. Windows CI verifies bundled assets, executable icon presence and frozen startup. Native platform/DPI visual acceptance remains manual.
