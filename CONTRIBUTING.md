# Contributing to SOSkúška

[English](CONTRIBUTING.md) · [Čeština](docs/cs/CONTRIBUTING.md) · [Slovenčina](docs/sk/CONTRIBUTING.md) · [Русский](docs/ru/CONTRIBUTING.md)

[Container tests](docs/CONTAINER_TESTS.md).

```sh
docker build -f Dockerfile.tests -t soskuska-tests .
docker run --rm --init --network none --cpus 2 --memory 2g soskuska-tests
```

## Before you start

Read the [README](README.md), [Git guide](docs/GIT_GUIDE.md), [development guide](docs/DEVELOPMENT.md) and [current architecture](docs/CURRENT_ARCHITECTURE.md). Development assistants must also follow [AGENTS.md](AGENTS.md).

Start a new branch from current `main`. Each change should solve one understandable problem. Dashboard, My Subjects, Question bank, Practice Tests, Flashcards, Statistics, AI Tutor and Settings exist; distinguish future proposals from implemented behavior. New databases must remain empty until the user enters data. Use `--data .local-data/dev.sqlite3` for isolated development.

## Before submitting

On the prepared Mac:

```sh
.venv-macos/bin/python -m compileall -q soskuska tests
.venv-macos/bin/python -m unittest discover -s tests -v
```

Use the container suite above for routine UI, timer and scrolling checks. Native GUI scripts open real windows and are only for required platform-specific/manual verification; arrange those visible runs with the user first. The complete list is `GUI_CHECKS` in `tools/run_checks.py`. On Windows/Linux, use the Python executable from your local environment, for example:

```sh
.venv-macos/bin/python soskuska/check_dashboard.py
.venv-macos/bin/python soskuska/check_note_generation.py
```

GUI checks open real windows and need a graphical session. Documentation-only changes normally need link, command and formatting checks rather than the entire UI suite.

Check `git diff --check` and review the staged changes. Never commit environments, databases, caches, tokens or `.env`. Preserve user data, UI stability and offline use. Keep English documentation and the Czech (`docs/cs/`), Slovak (`docs/sk/`) and Russian (`docs/ru/`) versions aligned. AGENTS.md remains English; the UI supports English, Czech, Slovak and Russian.

## Pull requests and issue reports

Push your branch and open a PR targeting `main`. Never commit or push directly to `main`; merge only after the user authorizes the PR and findings are resolved. Describe the problem, resulting behavior and actual validation, including OS/Python/Tk where relevant. Add a screenshot when it helps assess a UI change. Synthetic events do not prove physical trackpad behavior.

Use the issue templates to report reproduction steps, expected/actual behavior, environment and relevant complete logs. A feature request should explain the user's need and expected behavior. Do not attach private databases or credentials. Issues and PRs may use Czech, Slovak, English or Russian.

## Continuous integration

CI runs Python 3.12 unit tests on Ubuntu, Windows and macOS, the GUI scripts listed in `tools/run_checks.py` (26 at v0.30.1) on Ubuntu/Xvfb, and a Windows portable build check. [Workflow results](https://github.com/turcinv/SOSkuska/actions/workflows/ci.yml). Checks do not deploy or publish releases. See [Statistics rules](docs/STATISTICS.md) when changing reports; self-ratings must not be presented as measured mastery. AI prompt or schema changes should also be re-run with `tools/evaluate_ai.py` against a real local model (see [Development](docs/DEVELOPMENT.md)).

`tests/test_flashcard_csv_import.py`, `soskuska/check_flashcard_import.py`.
