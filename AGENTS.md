# SOSkúška — instructions for development agents

These instructions apply to the entire standalone SOSkuska repository. Product name: **SOSkúška**. Repository, source folder and fresh-install data folder: **SOSkuska** / `soskuska`.

## Start here in a new session

1. Read this file, `README.md`, `docs/CURRENT_ARCHITECTURE.md`, and `docs/DEVELOPMENT.md` before changing the application. English is primary; Czech, Slovak and Russian translations are under `docs/cs/`, `docs/sk/` and `docs/ru/`.
2. Distinguish implemented behavior from proposals in `docs/PLANNED_ARCHITECTURE.md`. A roadmap is not an instruction to implement every feature.
3. Check the user's latest message for their current language and requested scope. Do not assume access to other chats or decisions not recorded in this workspace.
4. For users with a clean Windows machine, use `docs/WINDOWS_FIRST_RUN.md` or its Czech/Slovak/Russian equivalent. These guides cover installing Python, obtaining/extracting sources, creating a Windows-local environment, installing dependencies, and launching the app. Never assume a Mac virtual environment can be copied to Windows or that the user has access to a private repository.

5. Read `CONTRIBUTING.md` for contribution checks and `docs/GIT_GUIDE.md` (or its Czech/Slovak/Russian version) for cloning and repository workflow. Keep the language versions aligned.

## Conversation languages

- The user may write instructions, answers, corrections, and follow-up messages in **Czech, Slovak, English, or Russian**, and may switch languages between messages. Treat all four languages as supported conversation languages.
- Respond in the language of the user's **most recent message**, unless they explicitly request a different response language. Do not force English merely because this file or the source code is in English.
- Do not translate or restate the user's messages in English unless asked. Ask a concise clarification only when meaning is genuinely ambiguous.
- Conversation language, application UI language, and documentation language are independent. The initial application UI remains **English**. Do not change UI labels just because the user writes in another language.
- Keep this AGENTS.md in **English**. English is the primary documentation language: root README.md, CONTRIBUTING.md, CHANGELOG.md and guides in `docs/`. Keep Czech translations in `docs/cs/`, Slovak in `docs/sk/` and Russian in `docs/ru/`. Keep matching-page language links on all guides and all four versions aligned. Do not mix languages within localized documents; preserve code identifiers, commands, paths, and literal UI labels as needed.

## Scope and implementation

- This is a native Python/CustomTkinter desktop application. HTML in `soskuska-local/` is a visual reference, not its runtime implementation. Do not convert it into a website without an explicit request.
- Dashboard, My Subjects, Question bank, Practice Tests, Flashcards and Statistics exist. Subject/topic/question CRUD, optional exam dates and subject-linked focus sessions use real SQLite data. New databases start empty; no sample statistics are added. AI Tutor has optional session-only Ollama chat; Settings persists study and AI preferences with explicit Save.
- Entry point: `soskuska/app.py`. Dashboard and timer logic live there; the subject-management screen is in `soskuska/subjects.py`; SQLite operations and transactional schema migrations (user_version 6) are in `soskuska/storage.py`; question authoring lives in `soskuska/question_bank.py` with pure validation in `soskuska/content.py`; scroll compatibility is isolated in `soskuska/scrolling.py`. Storage regression tests live in `tests/test_storage.py` and run with `python -m unittest discover -s tests -v`.
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
.venv-macos/bin/python soskuska/check_flashcards.py
.venv-macos/bin/python soskuska/check_statistics.py
.venv-macos/bin/python soskuska/check_state_fixes.py
.venv-macos/bin/python soskuska/check_tutor.py
.venv-macos/bin/python soskuska/check_settings.py
.venv-macos/bin/python soskuska/check_backup.py
.venv-macos/bin/python soskuska/check_csv_import.py
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

## Verification and documentation

- The native smoke check opens a real window and requires a graphical session. It uses a temporary database and must not modify normal user data.
- Add focused checks for persistence, timer, and scrolling changes. Avoid tests that merely duplicate static style values.
- Report what was actually verified. Syntax checking is not UI testing; synthetic events are not a manual hardware test; macOS checks do not establish Windows/Linux compatibility.
- Update current architecture, developer instructions, and known limitations with material changes. Keep English, Czech, Slovak, and Russian versions aligned; do not silently update only one language. Current code is the source of truth for implemented behavior.
- Preserve offline operation without mandatory cloud services or paid APIs. Ollama is optional and connects only after an explicit Connect/Send.
- GitHub repository: `https://github.com/turcinv/SOSkuska`. Keep it private unless the user requests a visibility change. Use the code and checked Git state to report publication status.

## CodeGraph

If `.codegraph/` exists at the repository root, use `codegraph_explore` or `codegraph explore "<symbols or question>"` before searching or reading source to understand code. Without an index, skip CodeGraph; do not create an index unless requested by the user.

## Branch and pull-request policy

- For implementation work, create a feature branch and open a pull request for review.
- Never commit or push directly to `main`. Merge through a pull request only after the user explicitly authorizes merging that PR and its review findings are resolved and validated. Passing tests alone is not merge authorization.
- Keep review fixes on the existing feature branch. Start a new feature branch for subsequent work after a PR is merged.

## Question bank

Open Questions from a subject card. Questions have four distinct answers, one correct answer (0–3), difficulty and optional explanation/topic. Topics are unique within a subject. Deleting a topic keeps its questions unassigned; deleting a subject explicitly warns and cascades its content while retaining session history. Schema 3 migrates existing data transactionally. Use `tests/test_questions.py` and `check_question_bank.py` for verification; all automated checks use disposable data. Practice execution, saved answers, resume, deadlines and snapshot scoring are implemented in `practice_page.py`, `practice.py` and Store; flashcards are implemented in flashcard_page.py with pure rules in repetition.py; session-only AI Tutor is implemented.

## Reviewed lifecycle safeguards

- Keep Aqua `::tk::mac::Quit` routed to the same save/retry handler as window close. Native application-menu Quit must preserve an unsaved session when saving fails.
- Dismiss subject deletion confirmations on navigation. Compare the displayed name/content counts under the SQLite write lock before deleting; changed content requires a refreshed warning and a second confirmation.
- Retry pending Dashboard reads independently of date rollover, including reads that fail after a session commit; retries must never duplicate the session. Preserve the manual Finish instruction while a session is unsaved. Clear refresh-retry notices after recovery. Always re-arm the timer tick after SQLite refresh errors. Commit `active_day` and update the header only after a successful daily refresh, so a failed refresh can retry.
- Contain scrolling in scrollable text editors, including at their boundaries; short editors still allow outer-page scrolling. Forward Tk 9 touchpad gestures from editor scrollbar/border canvases to the native Text widget exactly once. Use public Text/CTkTextbox APIs in the scrolling adapter.
- `check_review_fixes.py` verifies these failures with disposable databases; the native macOS Quit probe runs in a bounded child process. Existing storage unit tests now include stale deletion protection.

## Practice safeguards

- One in-progress practice attempt globally, enforced by a partial unique SQLite index. Configure subject/topic/difficulty, 1–100 questions, and optional time limit. Never seed user content.
- Snapshot questions/options/correct answers/explanations on start. History and unfinished attempts survive source edits/deletions; completed results are read-only through the API. Never expose correct answers in the running test UI.
- Save each answer and navigation position transactionally. On failed answer writes restore the last saved choice. Deadline checks occur after obtaining the write lock. Completion is idempotent; failed result reads may retry without creating another result.
- UTC deadlines continue while away or closed. On reopening, expired tests complete and reject late answers. System-clock changes can affect remaining time. Discard requires confirmation and applies only to an unfinished attempt.
- Practice results do not count as focus-session time. History shows the latest 20 results; older rows remain stored. Schema 4 migration preserves all existing content/history.
- Run `tests/test_practice.py` and `check_practice.py` with temporary data. The native check covers fresh-process resume, write errors and timed completion, in addition to the existing native checks.

- Background practice completion must not reset the shared scroll canvas or affect another screen's editing draft. Only reset practice scrolling when Practice Tests is active.

## Continuous integration

- `.github/workflows/ci.yml` runs for PRs targeting main, pushes to main and manual dispatch. Python 3.12 unit tests/syntax/dependency checks run on Linux, Windows and macOS; eleven GUI checks run under Xvfb on Ubuntu.
- Keep action references pinned to verified release commit SHAs, contents permission read-only, and process/job timeouts. CI does not publish releases or deploy. Avoid duplicate feature-branch push and PR runs.
- CI results are automated coverage, not manual platform or hardware verification. Native Aqua Quit and Tk 9 trackpad behavior still require the Mac checks. Do not claim those are tested by the Linux GUI job.
- Read failed job logs, fix the cause and keep fixes on the same PR branch. Do not disable a meaningful failing check to obtain a green status. Branch protection is not configured by this workflow.

## Flashcard safeguards

- Schema 5 adds decks, flashcards and immutable review_events. Deck names are globally Unicode-normalized unique. Subject deletion keeps decks/cards, card/deck deletion keeps review snapshots; communicate this in confirmation text.
- Custom deterministic scheduling in repetition.py: Again 10m/reset, new Hard 1h, new Good 1d, new Easy 4d; mature Hard/Good/Easy multiply days by 1.2/2.5/3.5 and round up, capped365d. Do not label it SM-2/FSRS or claim measured mastery. Ratings are self-assessments.
- Reveal before enabling rating. Compare card revision and due time under the write lock, commit schedule and review snapshot together. Advance UI only after commit. A stale callback cannot rate the next card or a hidden page. Failed writes keep revealed content/drafts for retry.
- Editing resets due/interval but keeps historical reviews. Study at most100 due cards per batch; history shows20, older rows remain stored. UTC system-clock changes can affect due status.
- Avoid binding a persistent StringVar to repeatedly recreated CTkEntry widgets in CTk5.2.2; destroyed entries retain traces. Flashcard search copies text through public entry APIs instead.
- Run tests/test_flashcards.py (including historical schema4 fixture) and check_flashcards.py. CI includes the fifth native check. Flashcards were released in v0.5.0.

## Statistics safeguards

- StatisticsPage uses Store.statistics() / study_statistics.py. Keep all four read aggregates in one deferred SQLite transaction; no writes or migration. Statistics introduced no schema change (schema 5 in v0.6.0; current schema is 6).
- Last 7/30 days includes today and previous 6/29 local calendar days; all-time totals exclude future days and chart only the latest 30 days. Focus uses stored local day; UTC completion/review times use SQLite localtime. Time-zone changes can rebucket events.
- Practice accuracy is total correct / total questions from completed snapshots; unanswered questions count incorrect, unfinished/discarded tests excluded. Include full retained history beyond the other screens' 20-row display limits.
- Flashcard ratings are self-assessments, not accuracy/mastery. Never infer focus time from tests/reviews. Empty history has zero counts and no percentage. Keep deleted/unassigned focus history visible and document name-based grouping after deletion.
- Refresh or reopening loads a new snapshot. Read failure preserves the previous report with a retry notice. Resize bindings must die with their labels; do not accumulate Configure callbacks on persistent report containers. Statistics shortcuts must not modify hidden search drafts.
- Run tests/test_statistics.py and check_statistics.py with disposable data. CI includes the sixth native check. Statistics was released in v0.6.0.

## Concurrent-state review fixes

- discard_practice obtains BEGIN IMMEDIATE before reading the clock. It returns True for deletion of an unfinished attempt, False when an expired attempt was completed and kept instead. Failed writes roll back. Never delete an expired attempt before the UI timer gets a turn.
- MissingPracticeError is terminal. Clear the stale active/finishing state and show usable setup; do not retry missing attempts every tick. SQLite failures still retain completion retry. A setup read failure can be retried with Refresh subjects or navigation.
- Question forms pass their original content snapshot as expected_state to update_question. Compare all editable content/identity under the write lock; updated_at has insufficient precision. Preserve drafts on conflict; require reloading current content before another save. These fixes introduced no schema change (5 in v0.6.2; current schema is 6).
- New-deck draft subject choices refresh in place on load, Refresh and Save. Keep selected subject by ID across rename. If it was deleted, require an explicit replacement; preserve title/description on every refresh/read failure.
- Run check_state_fixes.py and the complete unit/native suite with temporary databases. CI includes this seventh native check. These fixes were released in v0.6.2.

## AI Tutor safeguards

- tutor_page.py owns session-only chat; tutor.py builds bounded context and runs daemon jobs; ollama_client.py uses direct standard-library HTTP/HTTPS. No SQLite chat persistence or schema changes. Make session loss on app close explicit.
- No request on startup/navigation. Connect loads /api/tags; Send streams /api/chat to the visible endpoint. Never automatically attach database records/files or fall back to a cloud service. Endpoint changes require clearing the prior chat. Backend/model processing is determined by the selected server.
- Workers must never call Tk or SQLite; queue events are handled by the main-thread after poll. Hidden updates must not scroll shared pages or alter another screen's draft. Shutdown cancels networking without joining a worker on the UI thread; failed focus saves must still keep the window open.
- Stop sets a cancellation event; nonblocking reads/writes/TLS handshakes poll it at most every100ms. Only the worker may mutate or close sockets/TLS state. Preserve partial text but exclude stopped/failed turns from future context. Keep one task active until its terminal event; do not consume events from an old task as a new answer. System DNS/TCP setup can delay cancellation.
- Prompt max4000 chars, answer max16000, session max12 turns; context max6 complete pairs/24000 chars. Socket timeout30s and wall-clock timer180s. Bound streamed JSON lines and model lists; reject malformed/truncated responses instead of treating them as complete.
- HTTPS verification stays enabled; reject URL credentials, paths, queries and fragments. Do not follow redirects or use environment HTTP proxies. No authenticated servers or automatic model downloads.
- Tests use loopback FakeOllama, not real downloads/cloud services. Run test_tutor.py and check_tutor.py plus the full suite; model quality/hardware performance is not established by the fixture. CI includes the eighth GUI check. AI Tutor was released in v0.7.0.

## Settings safeguards

- preferences.py validates focus 1–180 minutes, daily goal 1–1440, Ollama URL/model and AI answer language. settings_page.py saves explicitly through Store; schema 6 adds the singleton preferences row and revision. Migration is transactional and must preserve schema 5 content/history; use the frozen schema_v5.sql fixture.
- Never connect on startup, navigation or Settings Save. Use Tutor choices copies into a draft; only Save persists it. UI remains English; answer language only changes AI replies. Chat remains session-only.
- Active/paused/unsaved focus sessions retain their original target; next session uses saved duration. Goal changes immediately without changing history. Applying committed settings must not depend on another SQLite read.
- Reject stale revision under the write lock. Failed Save/Reload and navigation preserve drafts, including a failed initial load. Reload needs confirmation when dirty. Invalid saved preferences fall back safely and repair only on explicit Save.
- AI preference changes wait for an idle Tutor. Different servers require New chat when chat exists. Remembering the already-connected server must retain its connection identity and chat isolation. Prefer the saved model when available; never silently substitute an unavailable preferred model. Study-only saves preserve temporary Tutor choices when persisted AI fields are unchanged.
- Changes from another window apply in this window on Save/restart, not live; Save applies the whole loaded form, so AI guards can also apply after reloading another window's changes.
- Run test_preferences.py and check_settings.py with disposable databases; CI includes the ninth native check. English Settings guide lives under docs/; translations are under docs/cs/, docs/sk/, docs/ru/.

- Persistent Settings was released in v0.8.0. Switching servers resolves the saved model preference afresh; a same-server refresh preserves an available manual model choice.

- English-primary documentation with Czech/Slovak/Russian translations was introduced in v0.8.1. Keep published version labels aligned across the app footer, root README, all localized READMEs and changelogs.

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
- Run test_csv_import.py and check_csv_import.py with disposable data. CI includes the eleventh GUI check. Maintain QUESTION_CSV_IMPORT.md in all four languages. Flashcard import, update/merge and semicolon/legacy-encoding formats remain outside this feature.

- CSV selection must clear/disable the old batch immediately after a new filename is chosen. Capture the subject snapshot already displayed by the bank; do not make synchronous subject reads on Tk during CSV open/choose. The helper rechecks identity/name and reports read failures.
