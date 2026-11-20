# Container tests

[English](CONTAINER_TESTS.md) · [Čeština](cs/CONTAINER_TESTS.md) · [Slovenčina](sk/CONTAINER_TESTS.md) · [Русский](ru/CONTAINER_TESTS.md)

Use container checks by default to avoid GUI windows interrupting desktop work. Docker must be installed and its engine running; this project does not install or launch Docker Desktop automatically. From the repository root:

```sh
docker build -f Dockerfile.tests -t soskuska-tests .
docker run --rm --init --network none --cpus 2 --memory 2g soskuska-tests
```

Keep `--init`: it lets the virtual-display wrapper receive its startup signal correctly and reaps child processes.

The build downloads Python, system libraries and Python dependencies, so it requires internet. Rebuild after source changes; sources are copied into the image, not mounted live. Later builds reuse cached dependencies. The run needs only loopback for fake Ollama tests, so external networking is disabled. CPU/memory limits reduce interference with other work; adjust them if necessary. No display socket, host data directory or port is mounted/exposed. `.dockerignore` permits only test sources; environments, databases, secrets and Git history stay outside the build context. The disposable container is removed afterward; the image/cache remain for later runs.

The image runs as a non-root user. Xvfb supplies an internal virtual screen for all 15 GUI scripts, so no application windows appear on the host. The shared `tools/run_checks.py` runs dependency checks, syntax, 251 unit tests and the GUI scripts, with a timeout for each process. The full suite takes a few minutes; failures return a nonzero exit code. CI uses the same GUI script list with `--gui-only` after its separate unit jobs.

Linux container checks do not verify native macOS Quit/Tk 9 trackpad behavior or Windows UI. Run native Mac checks only when a relevant platform change needs them, and arrange that visible run with the user first. Do not replace a meaningful failing platform check with a passing container check.
