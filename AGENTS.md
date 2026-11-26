# SOSkúška — development instructions

Applies to the whole repository. Product: **SOSkúška**; repository/source/data names: `SOSkuska` / `soskuska`. This is a native Python/CustomTkinter/SQLite semester project. `soskuska-local/` is a visual reference.

## Start with the relevant context

Read [@docs/agents/WORKFLOW.md](docs/agents/WORKFLOW.md) before changing files and [@docs/SESSION_LESSONS.md](docs/SESSION_LESSONS.md) at the start of a new session. Before application changes also read [@README.md](README.md), [@docs/CURRENT_ARCHITECTURE.md](docs/CURRENT_ARCHITECTURE.md) and [@docs/DEVELOPMENT.md](docs/DEVELOPMENT.md). Use [@docs/PLANNED_ARCHITECTURE.md](docs/PLANNED_ARCHITECTURE.md) to choose future work; implement only the requested scope.

The `@path` references are repository-relative reading instructions. Open the linked files with the available file tools; do not assume an `@` line automatically inserts its contents. Load only the topic files required below. They retain the detailed safeguards previously held here and apply to the relevant work.

| Work being changed or reviewed | Read before editing |
| --- | --- |
| Application runtime, database access, timer, navigation, Tk, scrolling or concurrent state | [@docs/agents/RUNTIME.md](docs/agents/RUNTIME.md) |
| Subjects/questions, practice, flashcards or statistics | [@docs/agents/STUDY.md](docs/agents/STUDY.md) **and** Runtime |
| AI Tutor, Ollama or Settings/preferences | [@docs/agents/AI_SETTINGS.md](docs/agents/AI_SETTINGS.md) **and** Runtime |
| Backup, restore or CSV imports, including shared panel/worker changes | [@docs/agents/DATA_TRANSFER.md](docs/agents/DATA_TRANSFER.md) **and** Runtime; also the affected Study or AI/Settings rules |
| Branches, PRs, reviews, CI, documentation or releases | [@docs/agents/WORKFLOW.md](docs/agents/WORKFLOW.md) |
| Read-only MCP server (planned) | [@docs/agents/MCP_SERVER_PLAN.md](docs/agents/MCP_SERVER_PLAN.md) **and** Runtime, Study, Data transfer |

## Essential rules

- Respond in the user's latest language: Czech, Slovak, English or Russian. UI defaults to English with saved Czech/Slovak/Russian choices; agent instructions stay English. User documentation is English-primary with separate aligned translations in `docs/cs/`, `docs/sk/`, `docs/ru/`; preserve matching-page language links. Files in `docs/agents/` are English internal agent instructions.
- Use a new branch and PR for changes. Never commit/push directly to main. Keep review fixes on the same branch; merge/release only with user authorization. Feature work gets independent Sol review at medium effort and appropriate local/CI checks.
- Preserve offline study, real user data and editing drafts. Never seed normal databases with samples. Use disposable databases or explicit `--data .local-data/dev.sqlite3` for checks. Never commit databases, environments, caches or secrets. Keep the GitHub repository private.
- Use `.venv-macos` on the prepared Mac; `.venv-desktop` uses Apple Tk 8.5 and produced a blank window. See Development for setup on each OS; use Windows first-run guides for a machine with nothing installed.
- Default to container GUI checks to avoid interrupting the user’s desktop; arrange native visible runs only for necessary platform verification. See [@docs/CONTAINER_TESTS.md](docs/CONTAINER_TESTS.md).
- Keep Tk on its main thread. CSV/backup database jobs run in isolated processes with file-backed output; Python thread garbage collection previously crashed macOS Tk. Never share Store connections across workers or use undrained output pipes.
- Preserve transaction boundaries, stale-state checks and immutable history. A committed or uncertain import must be consumed before refresh; retrying reads must never repeat writes. Apply schema changes transactionally and document them.
- Preserve the 1440 × 900 target, 1024 × 700 minimum, nested scrolling and Tk 9 trackpad support. Do not equate syntax/synthetic tests with manual platform or hardware verification.
- If `.codegraph/` exists, use CodeGraph before locating/reading code. Otherwise skip it; do not create an index without a request.

Keep this entry point short. Update the relevant topic file and dated lessons when a review uncovers a reusable safeguard; keep release/version history in changelogs.
