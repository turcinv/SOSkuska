# MCP server safeguards

English instructions for development agents, referenced by [AGENTS.md](../../AGENTS.md). Read with [RUNTIME.md](RUNTIME.md), [STUDY.md](STUDY.md) and [DATA_TRANSFER.md](DATA_TRANSFER.md). Design history: [MCP_SERVER_PLAN.md](MCP_SERVER_PLAN.md). User guide: [MCP_SERVER.md](../MCP_SERVER.md).

## Boundaries

- `soskuska/mcp_server.py` is stdio only. Do not add Streamable HTTP, SSE or any listener without an explicit request and a security design (authentication, origin checks, bind address).
- Read only. No tool may write, import, delete, migrate or create a database. Writes, if ever requested, go through reviewed drafts that the student saves in the app (see the plan's draft-proposal section); never call `Store` write methods from the server.
- Never import `app`, `customtkinter` or `tkinter` from the server or `study_queries.py`; tests guard this. Keep the SDK isolated to `mcp_server.py`.
- `mcp` stays optional: only in `soskuska/requirements-mcp.txt`, exact pin, never in `requirements.txt` or `packaging/windows.spec`. CI installs it on the Ubuntu unit job and fails if `tests/test_mcp_server.py` is skipped there.

## Data access

- Open `Store.open_existing(path, readonly=True)` per call and close it in `finally`. Never cache a Store, connection or lease between calls: restore needs the exclusive lease. `test_busy_schema_and_missing_database_errors` tracks every opened store.
- Map expected failures to `ToolError` (busy lease or lock, schema mismatch, missing file, unreadable database, `ValueError` from queries). Never retry in a loop.
- New tools wrap a pure function in `study_queries.py` with limits, truncation and the `truncated` flag. Question and card fields use the authoring maxima, so items are never shown partially (S27-05); only the response budget and descriptions shorten output. `search_questions(question_id=…)` returns one exact question for grading, with a per-process keyed `version`; never expose an unkeyed hash that includes the answer key. Keep answer keys, explanations and card backs behind an explicit flag that `--no-answers` rejects, and keep them out of search matching.
- Use `StrictInt`/`StrictBool`/`StrictStr` tool parameters; lax validation turns `true` into `1`. Prompt arguments arrive as strings, so prompts use plain `int`.

## Output and logging

- stdout carries only protocol messages: no `print` in server code paths. Diagnostics go to stderr through `logging` and must not contain study content or paths beyond the configured database.
- Stored text is user data. Server instructions say so; never let content select tools or arguments inside the server.

## Testing

- Run `tests/test_mcp_server.py` in an environment with `requirements-mcp.txt` (see Development). It covers both protocol modes (`mode="legacy"` handshake and the stateless default) and a real stdio subprocess. In raw stdio tests keep stdin open until the last reply: the SDK stops on EOF without finishing in-flight requests. Use a file for the child's stderr, never an undrained pipe.
- Automated tests are not a host acceptance pass. Record real host runs (host, versions, steps, results) in the plan before calling it verified.

## Manual host acceptance

`tools/make_mcp_acceptance_db.py <new path>` creates a disposable database with labelled sample data (two subjects with exams, seven questions, four due cards, focus time, one 2-of-4 practice test). It refuses existing files and the normal user database. Give the user absolute host-configuration paths to a Python environment with `requirements-mcp.txt` and that database, and check: tool list; subjects and exams; due cards without backs; Quiz me hides the answer until the student replies; practice results; a write request is refused; a restore in the app succeeds while the host is idle and the host still answers afterwards; `--no-answers` refuses answers. Record host, version, model and per-step results in the plan.
