# SOSkúška

[English](README.md) · [Čeština](docs/cs/README.md) · [Slovenčina](docs/sk/README.md) · [Русский](docs/ru/README.md)

**Release: [v0.30.1](https://github.com/turcinv/SOSkuska/releases/tag/v0.30.1)** — source code and a Windows x64 portable ZIP. See the [changelog](CHANGELOG.md). An installer is not included.

SOSkúška is a local desktop study assistant built with Python, CustomTkinter and SQLite for a semester project. The product name uses accents; repository, source and data-folder names use `SOSkuska` / `soskuska`.

The app stores your subjects, questions, focus sessions, practice tests, flashcards and preferences on your device. New databases start empty. Normal study works offline without a cloud account, paid API, Superdesign or Ollama. Optional AI Tutor connects to your chosen Ollama server only after an explicit action.

## Clone and install

The repository is private: you need Git and a GitHub account with access.

```sh
git clone https://github.com/turcinv/SOSkuska.git
cd SOSkuska
```

A clone contains neither a Python environment nor your database. Follow [development and setup](docs/DEVELOPMENT.md) for your system. [Git basics](docs/GIT_GUIDE.md) covers Git installation, authentication, updates and branches.

**Starting with nothing installed on Windows?** Use [Windows first run](docs/WINDOWS_FIRST_RUN.md). It walks from Python installation through extracting the project and launching it; Git and an editor are optional.

## Quick start on the prepared Mac

From the project root:

```sh
.venv-macos/bin/python soskuska/app.py
```

You can also open `soskuska/run-macos.command`. This environment uses Python 3.12.13 / Tk 9.0. The old `.venv-desktop` showed an empty window on this Mac; use `.venv-macos` instead.

For development, keep test data separate:

```sh
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

## Implemented features

| Screen | What it does |
| --- | --- |
| Dashboard / My Subjects | Create, edit and delete subjects; optional exam dates; search; daily checklist; subject-linked focus sessions and real stored totals |
| Question bank | Subject-specific topics and questions with four distinct answers, one correct answer, difficulty and optional explanation |
| Practice Tests | Randomized tests, optional deadlines, saved answers and resume, immutable results and answer review |
| Flashcards | Deck/card editing, reveal-before-rating, deterministic review scheduling and retained review history |
| Statistics | Stored focus time, weighted practice accuracy, flashcard self-ratings and daily activity |
| AI Tutor | Optional streamed Ollama chat, model discovery, answer language and cancellation; chat is saved locally and can be reopened |
| Settings | Persist focus duration, daily goal, Ollama URL/model and AI answer language; explicit Save without automatic connection |

Open **My Subjects → Questions** to author questions. Questions require four different answers A–D, exactly one correct answer, Easy/Medium/Hard difficulty and optional topic/explanation. Search combines text, topic and difficulty. Deleting a topic keeps its questions unassigned. Deleting a subject warns before removing its questions/topics and retains study history.

For **Practice Tests**, create a subject and questions first. Choose a topic, difficulty and 1–100 questions. Time limits are 5, 10, 15, 30 or 60 minutes, or Untimed. Answers and position save as you go. Only one attempt may be unfinished. Resume survives restart; deadlines keep running while away. Finish confirms submission; unanswered questions count incorrect. Correct answers appear only after completion. Discard confirms removal of an unfinished attempt. History provides all completed results in pages of 20, with saved subject-name and local-date filters. Content is snapshotted at start, so later edits/deletions do not change results. Practice does not add invented focus time.

Feature guides: [Flashcards](docs/FLASHCARDS.md) · [Statistics](docs/STATISTICS.md) · [AI Tutor](docs/AI_TUTOR.md) · [Settings](docs/SETTINGS.md).

## Documentation

English is the primary documentation language. Czech, Slovak and Russian are maintained in separate folders; the application UI defaults to English and supports Czech, Slovak and Russian after restart. Conversation with development assistants may use any of these four languages.

| Document | Contents |
| --- | --- |
| [How it works](docs/HOW_IT_WORKS.md) | A simple explanation of opening, using and saving in the app |
| [Current architecture](docs/CURRENT_ARCHITECTURE.md) | Implemented modules, data flow, schema and limitations |
| [Planned architecture](docs/PLANNED_ARCHITECTURE.md) | Future structure and development stages, distinct from implemented features |
| [Development and setup](docs/DEVELOPMENT.md) | Installation, commands, checks and troubleshooting |
| [Windows first run](docs/WINDOWS_FIRST_RUN.md) | Step-by-step setup on a clean Windows computer |
| [Git basics](docs/GIT_GUIDE.md) | Clone, authenticate, branch, commit and update |
| [Contributing](CONTRIBUTING.md) | Checks, pull requests and issue reports |
| [Changelog](CHANGELOG.md) | Release history |
| [Session lessons and project handoff](docs/SESSION_LESSONS.md) | Dated project context and lessons for future development sessions |
| [Agent instructions](AGENTS.md) | English instructions for future development sessions |

## Repository layout and limitations

```text
soskuska/          Native application and GUI check scripts
tests/            Unit tests and frozen migration fixtures
soskuska-local/    Earlier standalone HTML visual reference
docs/             English guides; cs/, sk/, ru/ contain translations
```

Windows/Linux are primary target platforms; macOS is also the current development environment. Unit CI runs on all three systems; GUI CI runs on Ubuntu/Xvfb, with native checks also run locally on macOS. This does not replace manual Windows/Linux UI or physical scrolling-gesture testing. There is no installer or synchronization yet.

## Backup and restore

Settings now includes manual local backup and validated restore, with a pre-restore safety copy. Current schema is 10. Restore closes the app; reopen it afterward. See [Backup and restore](docs/BACKUP_RESTORE.md).

## Import questions from CSV

Question bank now supports UTF-8 CSV import into an existing subject, with a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records; question lists show 50 per page. Current schema is 10. [Question CSV import](docs/QUESTION_CSV_IMPORT.md).

## Import flashcards from CSV

Flashcards now supports UTF-8 CSV import into an existing deck: a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records. New cards are due immediately; existing schedules and review history are preserved. Current schema is 10. [Import flashcards from CSV](docs/FLASHCARD_CSV_IMPORT.md).

## Saved AI Tutor conversations

AI Tutor now saves conversations locally, including the original server/model and reply status. Open saved history without networking, reconnect explicitly to continue, or delete a selected conversation after confirmation. Released in v0.12.0 with schema 7, which migrates existing study data transactionally. [Saved AI Tutor conversations](docs/TUTOR_HISTORY.md).

## AI drafts from notes

In a flashcard deck or a subject's question bank, choose **Generate with AI**, paste your notes and press Generate. The saved Ollama model drafts flashcards or multiple-choice questions; review them, untick anything wrong and save the selection in one step. Notes are sent only when you press Generate and are not stored. Released in v0.30.0; schema remains 10. [Generate flashcards and questions from notes](docs/AI_NOTE_GENERATION.md).

## Interface language

UI language selection is available in v0.13.0: English, Czech, Slovak and Russian, saved separately from AI answer language and applied after restart. Current schema is 10. [Interface language](docs/UI_LANGUAGES.md).

## Practice history

Practice history now supports pages of 20 across all completed attempts, historical subject-name and inclusive local-date filters, and reopening saved answer reviews. Filter drafts and the applied page survive navigation; failed reads keep prior results. Schema remains 8. [Practice history](docs/PRACTICE_HISTORY.md).

## Windows portable build and acceptance

v0.15.0 adds an unsigned Windows x64 portable ZIP, built and checked by a fifth CI job. Bundled helper executables preserve isolated CSV/backup jobs; Python is not required on the target machine. Automated hosted Windows checks and the manual clean-machine checklist are separate; manual acceptance is not yet completed. Published version is v0.30.1, schema 10. [Windows portable build and acceptance](docs/WINDOWS_PORTABLE.md) · [Checklist](docs/WINDOWS_ACCEPTANCE.md).

## Appearance settings

v0.16.0 adds saved Light/Dark/System choices, applied on Save without rebuilding screens or losing active work. System follows Windows/macOS and uses Light on Linux. Current schema is 10. The user confirmed baseline testing complete and approved merging appearance PR #32 on 22 November 2026. [Appearance settings](docs/APPEARANCE.md).

## Next steps · 22 November 2026

Status updated 22 November 2026: the user confirmed v0.15.0 baseline testing complete and approved appearance PR #32. This checklist now targets v0.30.1; item-by-item clean-machine/DPI results are not recorded here. Leave unchecked items unverified and record device-specific evidence when testing the new release. [Next steps · 22 November 2026](docs/NEXT_STEPS.md).

## Focus-session recovery

v0.17.0 adds focus-session crash recovery using schema **10**. Keep a backup before opening existing data: migration is transactional, but v0.16.0 cannot open a schema-10 database. [Focus-session recovery](docs/FOCUS_RECOVERY.md).

## Scheduled local backups

Scheduled local backups are available in **v0.18.0**. SQLite schema remains **10**. Manual backup/restore continues to work independently. [Scheduled local backups](docs/SCHEDULED_BACKUPS.md).

[Main-branch review fixes](docs/REVIEW_FINDINGS.md).
