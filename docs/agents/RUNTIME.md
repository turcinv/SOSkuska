# Runtime and lifecycle safeguards

English instructions for development agents, referenced by [AGENTS.md](../../AGENTS.md). Read this file when its routing rule applies. Paths and commands in this file are relative to the repository root.

## Scope and implementation

- This is a native Python/CustomTkinter desktop application. HTML in `soskuska-local/` is a visual reference, not its runtime implementation. Do not convert it into a website without an explicit request.
- Dashboard, My Subjects, Question bank, Practice Tests, Flashcards and Statistics exist. Subject/topic/question CRUD, optional exam dates and subject-linked focus sessions use real SQLite data. New databases start empty; no sample statistics are added. AI Tutor has optional Ollama chat with local history; Settings persists study and AI preferences with explicit Save.
- Entry point: `soskuska/app.py`. Dashboard and timer logic live there; the subject-management screen is in `soskuska/subjects.py`; SQLite operations and transactional schema migrations (user_version 10) are in `soskuska/storage.py`; question authoring lives in `soskuska/question_bank.py` with pure validation in `soskuska/content.py`; scroll compatibility is isolated in `soskuska/scrolling.py`. Storage regression tests live in `tests/test_storage.py` and run with `python -m unittest discover -s tests -v`.
- Keep sample data distinct from user records. Do not present sample metrics as actual user statistics or invent records in the user's database.

## Environment and data

Commands below are relative to the project root:

```sh
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
.venv-macos/bin/python -m compileall -q soskuska
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
.venv-macos/bin/python soskuska/check_backup.py
.venv-macos/bin/python soskuska/check_csv_import.py
.venv-macos/bin/python soskuska/check_flashcard_import.py
```

- On this Mac use `.venv-macos`, verified with Python 3.12.13 / Tk 9.0. `.venv-desktop` uses Apple Tk 8.5, which produced an empty window. Suppressing its warning is not a fix. The default Homebrew Python also lacked `_tkinter` when checked.
- Prefer project-local environments over global installation changes. Never commit environments, caches, or local databases.
- Use temporary databases in automated checks. Use `--data` for isolated development; without it, the app opens the normal user database.
- Fresh installations use a `SOSkuska` data folder. If it does not contain a database but the legacy `ExamPrep` database exists, continue using the legacy file without copying, moving or overwriting it. Document this compatibility behavior.
- Preserve user data. Version migrations through `PRAGMA user_version` and keep changes transactional. Deleting a subject must retain historical session time and its stored name snapshot. Legacy sessions remain unassigned; never infer a subject for them.
- Operate Tk widgets only on the main thread. Future network and long-running work must not block the UI event loop. Do not share SQLite connections between threads without an explicit design.

## UI and compatibility

- Preserve the established dark palette, spacing, typography, and desktop navigation unless a redesign is requested. Current colors and dimensions are in `soskuska/app.py`.
- Maintain the 1440 × 900 target and 1024 × 700 minimum. Check compact layout, focus, and access to lower content after relevant changes.
- Keep private CustomTkinter access inside `scrolling.py`. Verify `_parent_canvas`, `_scrollbar`, and `_shift_pressed` when upgrading the library. Do not modify installed dependency files in virtual environments.
- Tk 9 trackpads use `TouchpadScroll` with packed signed X/Y deltas. Do not replace this support with a MouseWheel-only handler.
- Use local design references. Do not start paid Superdesign generation for routine implementation work: the user switched to local development to avoid additional design credits.

## CodeGraph

If `.codegraph/` exists at the repository root, use `codegraph_explore` or `codegraph explore "<symbols or question>"` before searching or reading source to understand code. Without an index, skip CodeGraph; do not create an index unless requested by the user.

## Reviewed lifecycle safeguards

- Keep Aqua `::tk::mac::Quit` routed to the same save/retry handler as window close. Native application-menu Quit must preserve an unsaved session when saving fails.
- Dismiss subject deletion confirmations on navigation. Compare the displayed name/content counts under the SQLite write lock before deleting; changed content requires a refreshed warning and a second confirmation.
- Retry pending Dashboard reads independently of date rollover, including reads that fail after a session commit; retries must never duplicate the session. Preserve the manual Finish instruction while a session is unsaved. Clear refresh-retry notices after recovery. Always re-arm the timer tick after SQLite refresh errors. Commit `active_day` and update the header only after a successful daily refresh, so a failed refresh can retry.
- Contain scrolling in scrollable text editors, including at their boundaries; short editors still allow outer-page scrolling. Forward Tk 9 touchpad gestures from editor scrollbar/border canvases to the native Text widget exactly once. Use public Text/CTkTextbox APIs in the scrolling adapter.
- `check_review_fixes.py` verifies these failures with disposable databases; the native macOS Quit probe runs in a bounded child process. Existing storage unit tests now include stale deletion protection.

## Concurrent-state review fixes

- discard_practice obtains BEGIN IMMEDIATE before reading the clock. It returns True for deletion of an unfinished attempt, False when an expired attempt was completed and kept instead. Failed writes roll back. Never delete an expired attempt before the UI timer gets a turn.
- MissingPracticeError is terminal. Clear the stale active/finishing state and show usable setup; do not retry missing attempts every tick. SQLite failures still retain completion retry. A setup read failure can be retried with Refresh subjects or navigation.
- Question forms pass their original content snapshot as expected_state to update_question. Compare all editable content/identity under the write lock; updated_at has insufficient precision. Preserve drafts on conflict; require reloading current content before another save. These fixes introduced no schema change (5 in v0.6.2; current schema is 10).
- New-deck draft subject choices refresh in place on load, Refresh and Save. Keep selected subject by ID across rename. If it was deleted, require an explicit replacement; preserve title/description on every refresh/read failure.
- Run check_state_fixes.py and the complete unit/native suite with temporary databases. CI includes this seventh native check. These fixes were released in v0.6.2.


## Uninterrupted desktop testing

The user prefers GUI checks inside the Linux test container because native windows interrupt their work. Default to `docker build -f Dockerfile.tests -t soskuska-tests .` followed by `docker run --rm --init --network none --cpus 2 --memory 2g soskuska-tests`. No host display/data mounts; use disposable databases. Rebuild after source changes. See [Container tests](../CONTAINER_TESTS.md). Run native Mac UI checks only for required Aqua/Tk9/platform coverage and arrange the visible run with the user first. Container coverage is Linux only. CI shares the bounded GUI script list in `tools/run_checks.py`; keep new checks in that list.

## Focus checkpoint safeguards (released in v0.17.0)

Schema 10 adds focus_runs. Preserve the exclusive persistent `.focus.lock`, five-second/on-Pause checkpointing, bounded 200 ms write contention and explicit paused recovery/discard. Never credit closed-process time or finalize twice. Completion keeps the local save-day policy; do not introduce midnight splitting. Configure visible controls before fallible reads; clear stale recovery actions on read failure and cancel discard on navigation/other recovery actions. A save failure must remain visible off-Dashboard, disable ineffective Resume and keep Close on Dashboard until Finish succeeds. Backups include committed focus records, validate the original subject-name domain and bounded integer revisions, and refuse restore over target pending focus. Run test_focus.py and check_focus_recovery.py. See [Focus recovery](../FOCUS_RECOVERY.md).

## Dashboard responsive geometry

The scrolling adapter converts actual canvas/event widths into CTk logical units, excluding the scrollbar. Use that conversion for breakpoints and label wrapping; never feed native event widths directly into scaled wraplength. Reflow on viewport width changes as well as root resize and preserve hidden panels/drafts. Compact bounds checks must measure against the actual viewport with recovery/retry visible and long selected names. Simulate startup DPI in fresh processes with scaling set before widget creation; CTk 5.2.2 scaling callbacks can re-grid hidden widgets if invoked on a live app. Native/live-monitor DPI remains separate acceptance evidence.

## Equal-column wrapping

Derive label wrap lengths in uniform responsive columns from their shared container width, with gutter/inset/rounding allowance, not each child card's rounded width. The Czech Statistics resize probe exposed alternating one-pixel allocations that rewrapped indefinitely. Only re-grid on column-mode changes and avoid configuring unchanged wrap lengths. Keep these callbacks local to destroyed-with-report containers; resizing must not reread data or replace live editors/jobs.
