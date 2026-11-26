# Windows portable app

[English](WINDOWS_PORTABLE.md) · [Čeština](cs/WINDOWS_PORTABLE.md) · [Slovenčina](sk/WINDOWS_PORTABLE.md) · [Русский](ru/WINDOWS_PORTABLE.md)

v0.25.0 includes an **unsigned Windows x64 portable ZIP**, not an installer. End users do not need Python or administrator rights.

1. Download `SOSkuska-windows-x64.zip` and its `.sha256` file from [v0.25.0](https://github.com/turcinv/SOSkuska/releases/tag/v0.25.0). GitHub sign-in and repository access are required for this private repository. Choose the named Windows ZIP, not GitHub’s source-code archive.
2. Extract the ZIP fully into a writable folder. Keep the entire `SOSkuska` folder together, including `_internal` and `SOSkuska-worker.exe`.
3. Open `SOSkuska.exe`. Do not run it inside the ZIP, move just the EXE, or launch the helper directly. Existing study data remains in `%LOCALAPPDATA%\SOSkuska\dashboard.sqlite3` (legacy ExamPrep fallback still applies), independently of the portable app folder.
4. An unsigned build may be blocked by Windows security or organization policy. Verify its source/commit and SHA-256; do not disable protection. Ask your administrator if policy prevents it.

For an isolated check, open PowerShell in the extracted folder and run `./SOSkuska.exe --data "$env:TEMP/SOSkuska-check.sqlite3"`. Use a new unused path to avoid changing previous test data. Normal study is offline; Ollama remains optional and separate. Moving/removing the application folder does not delete the data folder. Keep backups before updates; older binaries refuse a newer database schema.

The artifact includes a SHA-256 file. Compare it with `Get-FileHash .\SOSkuska-windows-x64.zip -Algorithm SHA256` before extracting the inner ZIP. A matching checksum checks integrity, not publisher identity. The archive contains the app, console helper, Python/Tk/CustomTkinter resources, four translation catalogs and these guides. It contains no user database or virtual environment.

## Build and check on Windows

Use 64-bit Python 3.12 on Windows, from the repository root. PyInstaller is a build-only dependency pinned separately from app requirements. It must run on Windows to produce this Windows app:

```powershell
py -3.12 -m venv .venv-build
.\.venv-build\Scripts\python.exe -m pip install -r soskuska/requirements.txt -r packaging/requirements-build.txt
.\.venv-build\Scripts\python.exe tools/build_windows.py
.\.venv-build\Scripts\python.exe tools/check_windows_bundle.py dist/SOSkuska-windows-x64.zip --report dist/windows-acceptance.json
```

Output: `dist/SOSkuska/`, ZIP, `.sha256` and the check report. The spec builds a windowed GUI plus a console helper, whose hidden child processes keep the file-backed JSON worker protocol available. Source execution still launches Python worker scripts. The build uses no installer, registry installation, signing certificate or automatic updater.

CI extracts the actual ZIP into a Unicode/spaced temporary path and launches it from another working directory without Python on PATH. It checks a visible main window and normal close, an empty database, all four language startups, both CSV helper imports, backup/validation/restore and retained records. This automated hosted Windows evidence does **not** complete [manual acceptance](WINDOWS_ACCEPTANCE.md) on a clean Windows desktop. macOS/Linux packaging and ARM64 Windows remain out of scope.

Build approach follows the [PyInstaller spec-file documentation](https://pyinstaller.org/en/stable/spec-files.html) and [CustomTkinter packaging guidance](https://customtkinter.tomschimansky.com/documentation/packaging/).
