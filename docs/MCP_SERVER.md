# Read-only MCP server

[English](MCP_SERVER.md) · [Čeština](cs/MCP_SERVER.md) · [Slovenčina](sk/MCP_SERVER.md) · [Русский](ru/MCP_SERVER.md)

SOSkúška includes an optional [Model Context Protocol](https://modelcontextprotocol.io) server. With it, an AI assistant you already use (Claude Desktop, VS Code, Kiro or another MCP host) can **read** your study data: quiz you from your own questions, see which flashcards are due and plan revision from your real results. It cannot change anything.

## What it can and cannot do

- **Read only.** Subjects, topics, questions, decks and due cards, focus time, practice results and exam dates. There is no tool that writes, deletes or imports.
- **Answers stay hidden by default.** Correct options, explanations and flashcard backs are returned only when the assistant asks for them explicitly (for example to check your answer). Start the server with `--no-answers` to forbid them completely.
- **No network.** The assistant starts the server as a local program and talks to it over standard input/output. SOSkúška opens no port and connects nowhere.
- **Safe beside the app.** Each request opens the database read-only for a moment and closes it. The app can stay open, and a restore is never blocked by an idle assistant; a request made during a restore gets a "busy, retry" message.

**Privacy:** whatever the server returns goes to the model behind your assistant. If that is a cloud service, your study data reaches that service. Only connect assistants you are comfortable sharing your study data with.

## Install

The server needs a source checkout (see [Development](DEVELOPMENT.md)); the Windows portable ZIP does not include it. Install the optional dependency into the same environment you use for the app:

```sh
# macOS
.venv-macos/bin/python -m pip install -r soskuska/requirements-mcp.txt
# Windows
.venv\Scripts\python -m pip install -r soskuska\requirements-mcp.txt
```

Check it starts (press Ctrl+C to stop; it waits silently for an assistant):

```sh
.venv-macos/bin/python soskuska/mcp_server.py --data .local-data/dev.sqlite3
```

Without `--data` it reads the app's normal database. It never creates a database: open the app once first.

## Connect your assistant

Use **absolute paths** to the environment's Python and to `soskuska/mcp_server.py`. The examples use macOS paths; on Windows use paths such as `C:\\Users\\you\\SOSkuska\\.venv\\Scripts\\python.exe`.

**Claude Desktop** (`claude_desktop_config.json`) and **Kiro** (`~/.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "soskuska": {
      "command": "/Users/you/SOSkuska/.venv-macos/bin/python",
      "args": ["/Users/you/SOSkuska/soskuska/mcp_server.py"]
    }
  }
}
```

**VS Code** (`.vscode/mcp.json` or the user `mcp.json`):

```json
{
  "servers": {
    "soskuska": {
      "type": "stdio",
      "command": "/Users/you/SOSkuska/.venv-macos/bin/python",
      "args": ["/Users/you/SOSkuska/soskuska/mcp_server.py", "--no-answers"]
    }
  }
}
```

Add `"--data", "/path/to/file.sqlite3"` to `args` to use another database. Configuration file locations change between host versions; check your host's documentation if the file above does not exist.

## Tools and prompts

| Tool | Returns |
| --- | --- |
| `list_subjects` | Subjects, exam dates, days left, topic/question counts, focus time |
| `get_subject` | One subject's topics with question counts per difficulty |
| `search_questions` | Questions of a subject, optionally by text, topic, difficulty or one exact `question_id`; answers only with `include_answers` |
| `list_decks` / `due_flashcards` | Decks with due counts; due cards, backs only with `include_backs` |
| `study_statistics` | Focus time, weighted practice accuracy and flashcard self-ratings for Last 7 days, Last 30 days or All time |
| `practice_history` | Completed tests with per-topic scores, under the subject name they were taken with |
| `upcoming_exams` | Exams from today on |

Prompts: **Quiz me** (one question at a time, answer revealed after you reply) and **Weak topics study plan**. The resource `soskuska://subjects` gives a short Markdown overview.

Results are kept small for the model: lists stop at 50 items (exams at 20) and at about 20 KB, and long descriptions are shortened; both are marked `truncated`. Questions and cards are always returned whole.

## Troubleshooting

- **"needs the optional 'mcp' package"** — install `requirements-mcp.txt` into the Python named in your host configuration.
- **"no SOSkúška database"** — open the app once, or pass the right `--data` path.
- **"busy"** — a restore or another exclusive operation is running; retry in a moment.
- **"Open SOSkúška once to update it"** — the database belongs to another app version; open the app so it can update the database.

To remove it, delete the `soskuska` entry from your host configuration. Optionally uninstall the package with `python -m pip uninstall mcp`.

## Verification status

Automated tests (in-process client in both the current stateless protocol and the older handshake, and a real stdio subprocess) cover every tool, hidden answers, `--no-answers`, limits, busy/schema/missing-database errors and an unchanged database file. A recorded run with a real assistant is still pending.
