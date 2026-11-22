# Planned architecture

[English](PLANNED_ARCHITECTURE.md) · [Čeština](cs/PLANNED_ARCHITECTURE.md) · [Slovenčina](sk/PLANNED_ARCHITECTURE.md) · [Русский](ru/PLANNED_ARCHITECTURE.md)

**Future design, not a description of everything implemented today.** Proposed files/tables exist only where confirmed by [current architecture](CURRENT_ARCHITECTURE.md). A roadmap does not authorize implementing every feature at once.

Published baseline is v0.16.0, with interface languages, saved AI conversations and schema 9. The history guide below describes the implemented behavior. Settings Save does not start networking.

## Direction

Keep Python + CustomTkinter, local SQLite and optional Ollama. Windows/Linux remain primary targets with working macOS development. Ordinary study must not require a cloud account, paid API or running AI. Evolve the current Dashboard's visual style. Separate UI, study rules and persistence gradually as features need it; avoid introducing another UI framework or web backend.

## Proposed layers

```mermaid
flowchart TD
    UI[Screens and components] --> Services[Study services and screen state]
    Services --> Domain[Models and study rules]
    Services --> Repos[Repositories and migrations]
    Repos --> DB[(SQLite)]
    Services --> Jobs[Background jobs]
    Jobs --> Ollama[Local Ollama / HTTP]
    Jobs --> Files[Import and export]
    Jobs --> Queue[Result queue]
    Queue --> Main[Tk after / main thread]
    Main --> UI
```

| Layer | Responsibility |
| --- | --- |
| UI | Widgets, navigation, focus and state display; no SQL or blocking HTTP |
| Services | Study start, ratings, reports and AI context; no widget manipulation |
| Domain | Subjects, questions, answers and repetition rules independent of Tk |
| Persistence | Queries, transactions, mapping and migrations |
| Integrations | Ollama and file formats |

Screen state can remain a simple data structure; a large MVVM framework is unnecessary.

## Proposed files

```text
pyproject.toml
src/soskuska/
    __main__.py
    bootstrap.py
    domain/             models.py, repetition.py
    services/           dashboard.py, study.py, practice.py, tutor.py
    persistence/        database.py, migrations/, repositories/
    integrations/       ollama.py, import_export.py
    ui/
        app.py, theme.py, navigation.py
        components/
        screens/        dashboard, subjects, flashcards, practice,
                        tutor, statistics, settings
    i18n/               en.json, cs.json, sk.json, ru.json
tests/
docs/
```

Move incrementally in working steps. Until packaging exists, `python soskuska/app.py` remains the entry point; future `python -m soskuska` does not work yet.

## Proposed data model

| Area | Possible tables |
| --- | --- |
| Content | `subjects`, `topics`, `questions`, `answer_options` |
| Cards | `decks`, `flashcards`, `review_events`, `card_schedule` |
| Tests | `test_attempts`, `attempt_answers` |
| Study | `study_sessions` with subject and timing |
| Planning/settings | `exams`, `daily_tasks`, `settings` |
| AI | `conversations`, `messages`, attached-context references |
| Maintenance | Schema version / migration history |

These are proposed names, not replacements already performed. Define foreign keys, deletion rules, indexes and transactions. Preserve current tasks/sessions; never invent subjects for old time. A local profile should not need a server account.

Focus crash recovery is implemented on this unreleased branch; see [Focus recovery](FOCUS_RECOVERY.md). Midnight splitting remains future work. Completion currently assigns all time to its local completion day.

## Feature areas

- **Subjects/Dashboard:** subject/topic/question management, exams and actual session totals are implemented. New databases are empty; practice results and aggregate statistics already exist.
- **Flashcards:** decks, editing, reveal/rating, saved schedules and history exist. Rules in repetition.py are custom, not SM-2/FSRS. CSV import is implemented; advanced scheduling remains future work.
- **Practice:** filters, counts, timing, saved attempts, score and answer review exist. Question CSV import is implemented; paged history with subject/date filters is implemented.
- **AI Tutor:** bounded Ollama HTTP client, discovered models, streaming and cancellation exist. Keep default local connection, visible configurable URL and no automatic cloud fallback. Distinguish unavailable service, no models, loading/ready/generating/stopped, memory error and missing model; connection failure alone cannot prove Ollama is not installed.
- **AI execution:** keep long operations off the Tk thread, results through queue/after, and no worker widget calls. Do not share SQLite connections without a design; short writes may stay on the main thread and future jobs should get their own connections.
- **Text/languages:** start with plain text, code blocks and Unicode math; advanced HTML/LaTeX is optional future work. Separate UI from AI answer language. UI translations should support English/Czech/Slovak/Russian, long text and Cyrillic; AI already supports these plus Automatic and manual override.
- **Statistics/settings/data:** basic reports and study/AI preferences exist. Future work includes richer charts (Matplotlib only if needed), data management, import validation and scheduled backups. Manual backup/restore is now implemented.  The current manual restore closes the connection and creates a safety copy.

## Stages and completion criteria

| Stage | Scope | Completion evidence |
| --- | --- | --- |
| 1. Stabilize | Theme/UI separation, storage errors, migrations | Dashboard works and existing data survives |
| 2. Subjects | Subjects/topics/exams and actual reports | New subject survives restart; empty data is truthful |
| 3. Content/cards | Editor/import, decks, repetition | Rating creates history and next schedule |
| 4. Tests | Setup, execution, results and errors | Result can be reopened/recomputed from answers |
| 5. AI | Ollama client/chat | UI stays responsive; Stop works; offline state is clear |
| 6. Finish | Reports, languages, theme, backups, packaging | Verified installations on target systems |

Some stages are partly or substantially complete; use current architecture for status. Iterate with feedback against the semester assignment. This plan does not demand an immediate rewrite of Dashboard.

## Backup and restore

Settings now includes manual local backup and validated restore, with a pre-restore safety copy. Current branch schema is 10. Restore closes the app; reopen it afterward. See [Backup and restore](BACKUP_RESTORE.md).

## Import questions from CSV

Question bank now supports UTF-8 CSV import into an existing subject, with a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records; question lists show 50 per page. Current branch schema is 10. [Question CSV import](QUESTION_CSV_IMPORT.md).

## Import flashcards from CSV

Flashcards now supports UTF-8 CSV import into an existing deck: a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records. New cards are due immediately; existing schedules and review history are preserved. Current branch schema is 10. [Import flashcards from CSV](FLASHCARD_CSV_IMPORT.md).

## Saved AI Tutor conversations

AI Tutor now saves conversations locally, including the original server/model and reply status. Open saved history without networking, reconnect explicitly to continue, or delete a selected conversation after confirmation. Released in v0.12.0 with schema 7, which migrates existing study data transactionally. [Saved AI Tutor conversations](TUTOR_HISTORY.md).

## Interface language

UI language selection is available in v0.13.0: English, Czech, Slovak and Russian, saved separately from AI answer language and applied after restart. Current branch schema is 10. [Interface language](UI_LANGUAGES.md).

## Practice history

Practice history now supports pages of 20 across all completed attempts, historical subject-name and inclusive local-date filters, and reopening saved answer reviews. Filter drafts and the applied page survive navigation; failed reads keep prior results. Schema remains 8. [Practice history](PRACTICE_HISTORY.md).

## Windows portable build and acceptance

v0.15.0 adds an unsigned Windows x64 portable ZIP, built and checked by a fifth CI job. Bundled helper executables preserve isolated CSV/backup jobs; Python is not required on the target machine. Automated hosted Windows checks and the manual clean-machine checklist are separate; manual acceptance is not yet completed. Published version is v0.16.0, schema 9. [Windows portable build and acceptance](WINDOWS_PORTABLE.md) · [Checklist](WINDOWS_ACCEPTANCE.md).

## Appearance settings

v0.16.0 adds saved Light/Dark/System choices, applied on Save without rebuilding screens or losing active work. System follows Windows/macOS and uses Light on Linux. Current branch schema is 10. The user confirmed baseline testing complete and approved merging appearance PR #32 on 22 November 2026. [Appearance settings](APPEARANCE.md).

## Next steps · 22 November 2026

Status updated 22 November 2026: the user confirmed v0.15.0 baseline testing complete and approved appearance PR #32. This checklist now targets v0.16.0; item-by-item clean-machine/DPI results are not recorded here. Leave unchecked items unverified and record device-specific evidence when testing the new release. [Next steps · 22 November 2026](NEXT_STEPS.md).

## Focus-session recovery

This branch adds focus recovery to the published v0.16.0 baseline. It is unreleased and uses schema **10**. Keep a backup before opening existing data: migration is transactional, but v0.16.0 cannot open a schema-10 database. [Focus-session recovery](FOCUS_RECOVERY.md).
