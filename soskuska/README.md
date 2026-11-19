# SOSkúška desktop application

Entry point: `app.py`. Python and CustomTkinter create the UI; SQLite stores local study data and preferences. New databases start empty.

From the prepared Mac's repository root:

```sh
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Without `--data`, the normal user database is used. Native checks use disposable databases; see the complete [development guide](../docs/DEVELOPMENT.md) for all eleven commands.

Documentation: [English](../README.md) · [Čeština](../docs/cs/README.md) · [Slovenčina](../docs/sk/README.md) · [Русский](../docs/ru/README.md).

- [Windows first run](../docs/WINDOWS_FIRST_RUN.md)
- [How it works](../docs/HOW_IT_WORKS.md)
- [Current architecture](../docs/CURRENT_ARCHITECTURE.md)
- [Planned architecture](../docs/PLANNED_ARCHITECTURE.md)
- [Development instructions](../AGENTS.md)

Dashboard, My Subjects, Question bank, Practice Tests, Flashcards, Statistics, optional session-only AI Tutor and persisted Settings are implemented. Practice resumes after restart; cards retain schedules/review history. Settings persists study/AI choices without connecting automatically. AI conversations remain session-only. Normal study works offline.

[Backup and restore](../docs/BACKUP_RESTORE.md) is available from Settings.

[Question CSV import](../docs/QUESTION_CSV_IMPORT.md) is available in the question bank.
