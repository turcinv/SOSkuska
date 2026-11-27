# Semester report outline

Working draft, written against v0.31.1 (27 November 2026). Placeholders in `[[double brackets]]` must be filled in by the author; nothing here invents personal, course or grading details. Facts below were checked against the repository on that date; re-check numbers before submitting.

**Title page:** SOSkúška — an offline study planner with optional local AI · [[author name]] · [[course / subject code]] · [[school / class]] · [[teacher]] · [[submission date]] · report language: [[language]].

## 1. Introduction (½ page)

- Problem: students preparing for several exams lose track of what to revise; most study apps need an account and the cloud.
- Goal: a desktop app that works fully offline, keeps data in one local file, and uses AI only when the student explicitly asks.
- Scope of the semester project and what is out of scope (no mobile version, no accounts, no cloud sync).

## 2. Requirements (½–1 page)

- Functional: subjects with exam dates, topics and multiple-choice questions; practice tests with history; flashcards with spaced repetition; focus timer and daily goal; statistics; AI Tutor and AI drafts from notes; backup/restore and CSV import; four interface languages.
- Non-functional: offline by default; no data loss (transactions, focus checkpoints, safety copy before restore); 1440 × 900 target and 1024 × 700 minimum window; privacy (nothing sent without an explicit action).
- Sources for detail: `README.md`, `docs/HOW_IT_WORKS.md`.

## 3. Design and architecture (1–2 pages)

- Technology: Python 3.12, CustomTkinter 5.2.2, SQLite (schema version 10), optional Ollama for local AI, optional MCP SDK for the assistant integration.
- Module overview diagram: GUI pages → `storage.py` (all database access, migrations) → SQLite file; pure modules such as `content.py`, `practice.py`, `repetition.py`, `study_statistics.py`; AI path `tutor.py`/`ollama_client.py` on worker threads; CSV/backup jobs in separate processes. Source: `docs/CURRENT_ARCHITECTURE.md`.
- Data model figure: subjects, topics, questions, practice attempts/items (snapshots), decks, flashcards, review events, sessions, focus runs, preferences, Tutor conversations.
- Key decisions worth explaining:
  - Immutable practice and review snapshots, so history survives edits and deletions.
  - Stale-state checks under `BEGIN IMMEDIATE` so two windows cannot silently overwrite each other.
  - Database jobs in isolated processes, and garbage collection only on the Tk thread (v0.31.1), because Tk is not thread-safe.
- Screenshots: `screenshots/01-dashboard-light.png`, `02-dashboard-dark.png`, `03-dashboard-czech.png`.

## 4. Implementation highlights (2–3 pages)

1. **Study workflow:** subjects and question bank (`04`, `05`, `06`), practice tests (`08`, `09`, `10`), flashcards (`11`, `12`), statistics (`13`).
2. **AI with consent:** Tutor and question explanations (`14`); drafting questions/flashcards from notes (`07`). Real-model evaluation found wrong answer letters and prompt injection; fixes: the app places the correct answer, notes are fenced as data, weakly supported drafts start unticked. Source: `docs/agents/design/ai-note-generation/EVALUATION.md`.
3. **Data safety:** backup and restore with validation and safety copy (`16`), scheduled daily backups, CSV import with preview (`17`), focus-session recovery after a crash.
4. **Read-only MCP server (v0.31.0):** lets the student's own assistant read study data; read-only, answers hidden by default, stdio only. Source: `docs/MCP_SERVER.md`.
5. **Localisation:** English, Czech, Slovak and Russian UI and documentation.

## 5. Testing and quality (1 page)

- 382 unit tests (two platform skips on Linux; MCP tests need the optional package) and 26 GUI scripts under Xvfb in a Docker test container; CI on GitHub runs unit tests on Ubuntu, Windows and macOS, the GUI suite on Linux, and builds and checks the Windows portable ZIP. Sources: `docs/DEVELOPMENT.md`, `docs/CONTAINER_TESTS.md`.
- Techniques: disposable databases only, mutation checks (deliberately breaking a guarantee to prove a test fails), fresh-process startup budgets, independent code reviews on every feature PR.
- A debugging story worth telling: the flaky Tutor check that turned out to be a real 4-second stall caused by garbage collection in a worker thread (`docs/SESSION_LESSONS.md`, 27 November 2026).
- Honest limits: no recorded native macOS/Windows visual acceptance or real-assistant MCP run yet [[update if done]]; AI quality depends on the local model.

## 6. Process (½ page)

- Git with feature branches and pull requests, squash merges, tagged releases with a Windows ZIP and checksum. As of 27 November 2026: 77 merged pull requests and 41 release tags (v0.31.1 latest).
- AI-assisted development: [[describe honestly how you used AI coding assistants, what you decided and reviewed yourself, and what you learned]].

## 7. Conclusion and future work (½ page)

- What works, what you would do differently [[your reflection]].
- Future work: native acceptance, broader AI evaluation and optional assistant write access only through reviewed drafts (`docs/PLANNED_ARCHITECTURE.md`); ideas not yet planned there: Anki export/import or an FSRS-style scheduler.

## Appendices

- A: How to run (`README.md`, `docs/WINDOWS_FIRST_RUN.md`).
- B: Screenshot index (`README.md` in this folder).
- C: Demo script (`DEMO_SCRIPT.md`).
- References: CustomTkinter, SQLite, Ollama, Model Context Protocol documentation [[add citation style required by the course]].
