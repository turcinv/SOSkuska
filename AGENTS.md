# SOSkúška — instructions for development agents

These instructions apply to the entire standalone SOSkuska repository. Product name: **SOSkúška**. Repository, source folder and fresh-install data folder: **SOSkuska** / `soskuska`.

## Start here in a new session

1. Read this file, `README.md`, `docs/CURRENT_ARCHITECTURE.md`, and `docs/DEVELOPMENT.md` before changing the application. Equivalent Slovak and Russian documentation is available under `docs/sk/` and `docs/ru/`.
2. Distinguish implemented behavior from proposals in `docs/PLANNED_ARCHITECTURE.md`. A roadmap is not an instruction to implement every feature.
3. Check the user's latest message for their current language and requested scope. Do not assume access to other chats or decisions not recorded in this workspace.
4. For users with a clean Windows machine, use `docs/WINDOWS_FIRST_RUN.md` or its Slovak/Russian equivalent. These guides cover installing Python, obtaining/extracting sources, creating a Windows-local environment, installing dependencies, and launching the app. Never assume a Mac virtual environment can be copied to Windows or that the user has access to a private repository.

5. Read `CONTRIBUTING.md` for contribution checks and `docs/GIT_GUIDE.md` (or its Slovak/Russian version) for cloning and repository workflow. Keep the language versions aligned.

## Conversation languages

- The user may write instructions, answers, corrections, and follow-up messages in **Czech, Slovak, English, or Russian**, and may switch languages between messages. Treat all four languages as supported conversation languages.
- Respond in the language of the user's **most recent message**, unless they explicitly request a different response language. Do not force English merely because this file or the source code is in English.
- Do not translate or restate the user's messages in English unless asked. Ask a concise clarification only when meaning is genuinely ambiguous.
- Conversation language, application UI language, and documentation language are independent. The initial application UI remains **English**. Do not change UI labels just because the user writes in another language.
- Keep this AGENTS.md in **English**. Keep Slovak documentation separately in `docs/sk/` and Russian documentation in `docs/ru/`. Existing Czech documentation remains under `docs/` and the root README. Do not mix languages within localized documents; preserve code identifiers, commands, paths, and literal UI labels as needed.

## Scope and implementation

- This is a native Python/CustomTkinter desktop application. HTML in `soskuska-local/` is a visual reference, not its runtime implementation. Do not convert it into a website without an explicit request.
- Dashboard and My Subjects exist. Subject CRUD, optional exam dates and subject-linked focus sessions use real SQLite data. New databases start empty; no sample statistics are added. AI Tutor, questions, practice tests, flashcards and the Statistics/Settings screens remain unimplemented.
- Entry point: `soskuska/app.py`. Dashboard and timer logic live there; the subject-management screen is in `soskuska/subjects.py`; SQLite operations and transactional schema migrations (user_version 2) are in `soskuska/storage.py`; scroll compatibility is isolated in `soskuska/scrolling.py`. Storage regression tests live in `tests/test_storage.py` and run with `python -m unittest discover -s tests -v`.
- Keep sample data distinct from user records. Do not present sample metrics as actual user statistics or invent records in the user's database.

## Environment and data

Commands below are relative to the project root:

```sh
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
.venv-macos/bin/python -m compileall -q soskuska
.venv-macos/bin/python soskuska/check_dashboard.py
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
- Update current architecture, developer instructions, and known limitations with material changes. Keep Czech, Slovak, and Russian versions aligned; do not silently update only one language. Current code is the source of truth for implemented behavior.
- Preserve offline operation without mandatory cloud services or paid APIs. Ollama is a planned optional local integration.
- GitHub repository: `https://github.com/turcinv/SOSkuska`. Keep it private unless the user requests a visibility change. Use the code and checked Git state to report publication status.

## CodeGraph

If `.codegraph/` exists at the repository root, use `codegraph_explore` or `codegraph explore "<symbols or question>"` before searching or reading source to understand code. Without an index, skip CodeGraph; do not create an index unless requested by the user.

## Branch and pull-request policy

- For implementation work, create a feature branch and open a pull request for review.
- Never commit or push directly to `main`. Merge through a pull request only after the user explicitly authorizes merging that PR and its review findings are resolved and validated. Passing tests alone is not merge authorization.
- Keep review fixes on the existing feature branch. Start a new feature branch for subsequent work after a PR is merged.
