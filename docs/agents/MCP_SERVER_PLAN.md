# Read-only MCP server · implementation plan

Internal plan, 27 November 2026, written against v0.30.1 (schema 10). Phase 1 is merged into `main` (PR #76, `556ddab`); Phase 2 (the stdio server) is implemented on `feature/mcp-server`; neither is released. Phase 2 manual acceptance with a real host and Phase 3 are not done. Start each phase on its own branch from current `main` and follow [WORKFLOW.md](WORKFLOW.md). Read [RUNTIME.md](RUNTIME.md), [STUDY.md](STUDY.md) and [DATA_TRANSFER.md](DATA_TRANSFER.md) before touching storage or leases.

## Goal

Let a student's own AI assistant (Claude Desktop, Kiro, VS Code, any MCP host) read their SOSkúška study data. With it the assistant can quiz from real questions, see which cards are due and explain weak topics from real statistics. The app's local-first, explicit-consent model must stay intact.

Out of scope for this plan:

- Any write to the database.
- Network listeners or remote access.
- Running AI inside the server.
- Changes to the GUI.

Draft-proposal writes are a possible later phase, described at the end.

## Key decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Transport | **stdio only** | The MCP host launches the server as a child process, so there is no port, no authentication and no listener. Streamable HTTP is out of scope. |
| Library | Official Python SDK **`mcp==2.3.0`**, `from mcp.server import MCPServer` (Python ≥ 3.10; the project uses 3.12) | Hand-rolling JSON-RPC would need to track spec changes: 2026-07-28 is stateless with no `initialize` handshake, while older clients still handshake. The SDK negotiates both. Verify version negotiation with an older-client fixture during Phase 2. |
| Dependency scope | **Optional**: new `soskuska/requirements-mcp.txt`, not `requirements.txt` | The SDK pulls in pydantic, starlette, uvicorn, httpx2 and more. The desktop app and the Windows portable ZIP must not grow or break because of it. If `mcp` is missing, the entry point exits with an install hint. |
| Process | Separate entry point `soskuska/mcp_server.py`; never started by the GUI | The user opts in by adding it to their MCP host's configuration. The GUI is not involved, and Tk is never imported. |
| Database access | `Store.open_existing(path, readonly=True)` **per tool call**, closed before returning | Uses `mode=ro`, never creates or migrates, rejects other schema versions, and takes the shared lease only for the duration of a call. Keeping it open would block restore, which needs the exclusive lease. |
| Answer keys | Hidden unless the tool call passes `include_answers=true`; a server flag `--no-answers` forbids them entirely | Assistants often quiz the student. The answer key should not leak into a hint by default. |
| Output | Bounded, structured results (pydantic or TypedDict return types → `structured_content`) plus short text | Limits on rows and characters keep replies within model context. Structured output lets hosts render or filter results. |

## Phase 1 — Headless data path and query layer (no new dependency)

One PR, reviewable on its own.

1. **Move the default database location out of `app.py`.** `data_path()` lives in `app.py`, which imports Tk. Move it to `storage.py` as `user_database_path()` next to `default_database()`, keeping the macOS/Windows/Linux rules and the legacy `ExamPrep` fallback unchanged. `app.py` imports it. Add a unit test for the three platform bases (patched `sys.platform`/env) so behaviour cannot drift.
2. **New `soskuska/study_queries.py`** with pure functions `(store, …) -> dict`: no Tk, no MCP, no writes. Each validates its arguments, clamps limits and truncates long text with an explicit `truncated` flag.
   - `subjects_overview(store)`: id, name, exam date, days until exam, topic/question counts, study minutes, session count.
   - `subject_detail(store, subject_id)`: the overview fields plus topics with question counts per difficulty.
   - `find_questions(store, subject_id, *, query='', topic_id='all', difficulty=None, limit=20, include_answers=False)`: prompt, options and topic. The correct letter and explanation are included only with `include_answers`. `limit` is at most 50.
   - `decks_overview(store)`: id, name, subject, card count, due count.
   - `due_cards(store, deck_id, *, limit=20, include_backs=False)`: front, due time and review count; the back only with `include_backs`. Same ordering as `Store.due_flashcards`.
   - `study_report(store, period)`: `Store.statistics()` reduced to the documented aggregates. Keep weighted practice accuracy, label flashcard ratings as self-assessments, never present mastery.
   - `practice_results(store, *, subject_name=None, limit=10)`: completed attempts only, from `practice_history_page`. Scores and per-topic correct/total come from snapshots.
   - `upcoming(store, limit=5)`: exams from `upcoming_exams`.
3. **Tests (`tests/test_study_queries.py`)** on disposable databases:
   - Results on an empty database and a populated one.
   - Limits and truncation.
   - Answer and back hiding.
   - Deleted-subject snapshots in history.
   - Invalid IDs give a clear `ValueError`, not tracebacks.
   - Every function works on a `readonly=True` store and leaves the file's bytes and mtime unchanged.
4. Docs: a short note in `CURRENT_ARCHITECTURE.md` (four languages) only if the data-path move changes documented behaviour; otherwise a code comment is enough.

### Phase 1 as built (PR #76)

Phase 2 should wrap these contracts rather than re-derive them:

- `storage.user_database_path()` treats an empty or relative `LOCALAPPDATA`/`XDG_DATA_HOME` as unset, so the path never depends on the host's working directory.
- Function names match the list above. Every list result has `items`, `returned`, `total` (where countable) and `truncated`; `truncated` means text was shortened or rows were left out by the ~20 KB JSON budget, while `total > returned` means the limit cut rows. Limits are clamped (`find_questions`/`due_cards`/`practice_results` ≤ 50, `upcoming` ≤ 20).
- Invalid arguments, unknown ids and bool-as-int raise `ValueError` with a message suitable for a tool error.
- `find_questions` search never matches explanation text, so hidden answers cannot leak through search.
- `practice_results` reads per-topic scores just after `practice_history_page` (which opens its own transaction); the docstring explains why they agree.
- `tests/test_study_queries.py` proves a full sweep on `Store.open_existing(readonly=True)` leaves the file's hash and mtime unchanged.

The hosted-CI startup flake seen while merging Phase 1 is fixed: `check_studio_layout.py` now budgets startup CPU and wall time separately from its functional steps (see [WORKFLOW.md](WORKFLOW.md)).

## Phase 2 — MCP server (optional dependency)

One PR, after Phase 1 is merged.

1. **`soskuska/requirements-mcp.txt`:** `mcp==2.3.0`. Document that transitive versions are resolved by pip, as with the main requirements file. Never add it to `requirements.txt` or the PyInstaller spec in this phase.
2. **`soskuska/mcp_server.py`:**
   - **Command line:** `python soskuska/mcp_server.py [--data PATH] [--no-answers]`. The default path is `user_database_path()`. A missing file is an error; the server never creates a database.
   - **Server:** `MCPServer("SOSkúška", instructions=…)`. The instructions say that the data belongs to the student, that it is read-only, and that answer keys should stay hidden while quizzing unless the student asks.
   - **Tools** wrap Phase 1 one-to-one:
     - `list_subjects`, `get_subject`, `search_questions`
     - `list_decks`, `due_flashcards`
     - `study_statistics` (`period`: `Last 7 days` | `Last 30 days` | `All time`)
     - `practice_history`, `upcoming_exams`
   - **Annotations on every tool:** `readOnlyHint=True`, `destructiveHint=False`, `idempotentHint=True`, `openWorldHint=False`.
   - **Resource:** `soskuska://subjects`, a markdown overview for hosts that prefer resources.
   - **Prompt templates:**
     - `quiz_me(subject_id, count=5)` asks one question at a time from `search_questions` and reveals the answer only after the student replies.
     - `weak_topics(period)` builds a study plan from `study_statistics` and `practice_history`.
   - **Per call:** open → query → close with a `try/finally`.
   - **Errors:**
     - A lease or lock conflict (restore in progress, `sqlite3.OperationalError: database is locked`) becomes a tool error: "SOSkúška database is busy (for example a restore); retry shortly."
     - Schema mismatch: "Open SOSkúška once to update the database, then retry."
     - Nothing is retried in a loop.
   - **Logging:** stdout is reserved for the protocol; all diagnostics go to stderr. Never log study content or note text.
   - Never import `app`, `customtkinter` or `tkinter` (guard with a test).
3. **Concurrency with the app:**
   - SQLite `mode=ro` plus the shared lease coexist with the running GUI, which also holds a shared lease.
   - Restore takes the exclusive lease, so it will wait for or reject a call in flight. Calls are short, and the server holds no lease between calls.
   - Focus checkpoints and practice writes in the GUI are visible to the next call; no caching.
4. **Tests:**
   - **`tests/test_mcp_server.py`:** skipped with a clear reason when `mcp` is not installed.
     - In-process client (SDK `Client` over an in-memory or stdio transport): `tools/list` names and annotations, each tool on a fixture database, answer hiding and `--no-answers`, bounded outputs, busy-lease error (hold an exclusive `DatabaseLease` in the test), schema-mismatch error, a missing database is never created.
     - The database file hash is unchanged after a full tool sweep.
     - The `tkinter`/`customtkinter` import guard.
   - **Subprocess stdio smoke test:** launch `python soskuska/mcp_server.py --data <fixture>`, exchange initialize (or a stateless request) plus `tools/list` plus one call, and assert that stdout contains only protocol lines.
   - **CI:** add a step to the Ubuntu unit job that installs `requirements-mcp.txt` and runs these tests. Windows and macOS unit jobs may skip them in the first PR; keep job time within the 10-minute bound. Add the same install to `Dockerfile.tests` so the container suite covers it.
5. **Docs:**
   - **New user guide `docs/MCP_SERVER.md` in all four languages:**
     - What it is and why it is read-only.
     - Installation: `pip install -r soskuska/requirements-mcp.txt` in the project environment.
     - Host configuration examples (JSON `command`/`args` with absolute paths) for Claude Desktop, VS Code and Kiro.
     - Privacy: your study data goes to the assistant's model, which may be a cloud service you chose; SOSkúška itself never connects anywhere.
     - `--no-answers`, troubleshooting (busy, schema, missing database), and how to remove it.
   - Changelog Unreleased entry in four languages, `CURRENT_ARCHITECTURE.md` section, `PLANNED_ARCHITECTURE.md` "Integrations" bullet updated, an agent-safeguards section in `AI_SETTINGS.md` (or a new `docs/agents/MCP.md` routed from AGENTS.md).
6. **Manual acceptance (recorded, not assumed):**
   - Connect a real MCP host on macOS to a disposable database. List subjects, run `quiz_me`, and confirm that answers stay hidden.
   - Run a restore in the GUI while the host is idle and confirm it succeeds.
   - Record the host name, versions and results in the PR.

## Phase 3 (optional, later) — Packaging

- Ship a separate console helper `SOSkuska-mcp.exe` in the Windows portable ZIP only if Phase 2 proves useful. Use a separate PyInstaller target so the GUI build stays unchanged.
- The Windows acceptance job runs the stdio smoke test against the frozen helper.
- Measure the ZIP size increase and record it.

## Possible later phase — Draft proposals (not part of this plan)

If assistants should add study material, they must not write directly. A `propose_flashcards` or `propose_questions` tool could write a pending draft file in a dedicated drafts folder. The app would then show it in the existing review panel (the same flow as Generate with AI) and save it with `Store.import_*` only after the student ticks and saves. That needs its own design, a review of locking and file safety, and explicit user approval before work starts.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Study data reaches a cloud model | Opt-in by configuration only; the privacy section in the guide; read-only; answers hidden by default; `--no-answers`. |
| Blocking restore or app writes | Open and close per call; shared lease only; `mode=ro`; busy errors instead of waiting. |
| SDK churn (spec 2026-07-28 is stateless; older hosts handshake) | Pin `mcp==2.3.0`; test both an older-style handshake and a stateless request; isolate SDK use in one module. |
| Dependency weight and supply chain | Optional requirements file; exact pin; not in the GUI build; review `pip install` output in CI. |
| Prompt injection from stored content (question text is user data) | Tool results are data; server instructions tell hosts so; no tool can write or execute anything. |
| Large outputs | Clamped limits, truncated fields with flags, at most about 20 KB of text per call. |

## Definition of done (Phase 1 + 2)

- Unit tests and the existing GUI suite pass in the container. The new MCP tests pass with `mcp` installed and are skipped cleanly without it. All five CI jobs pass.
- Independent review at medium effort with findings resolved.
- Manual acceptance with one real MCP host recorded in the PR.
- Docs in four languages, and a release-label PR when the user authorizes a release.
