# Windows from zero: first launch

[English](WINDOWS_FIRST_RUN.md) · [Čeština](cs/WINDOWS_FIRST_RUN.md) · [Slovenčina](sk/WINDOWS_FIRST_RUN.md) · [Русский](ru/WINDOWS_FIRST_RUN.md)

For Windows 10/11 users without Python or development tools. You need internet for initial installation and the SOSkuska source files. Git, VS Code, Node.js, Ollama and paid services are not required for normal study.

This guide follows the project's setup instructions; the complete manual Windows walkthrough has not yet been verified. The app has no `.exe` installer. Automated Windows unit checks do not replace a manual first run.

## 1. Install the Python manager

1. Open the [official Python downloads for Windows](https://www.python.org/downloads/windows/).
2. Choose **Python install manager** and download its installer. The manager itself is not the Python version needed by this app; add that next.
3. Open the download and select **Install**. If offered, use **Launch** to finish initial setup.
4. Close old terminal windows afterward.

Do not select the embeddable package or Python source archive. This guide uses ordinary Python through the manager; see [Python's Windows instructions](https://docs.python.org/3/using/windows.html).

## 2. Open PowerShell and add Python 3.12

Open Start, search `PowerShell`, then open Windows PowerShell or Terminal with a PowerShell profile. Administrator mode is not needed. Copy one command at a time and press Enter; do not copy prompt markers such as `PS>` or Markdown fences.

```powershell
py install 3.12
```

Wait for download/installation, then check:

```powershell
py -3.12 --version
```

Expect `Python 3.12.x`; the final number may differ. Use the 3.12 series deliberately rather than automatically selecting the newest Python.

If `py install` tries to open a file named `install`, an older launcher is probably handling the command. Use the manager's unambiguous command:

```powershell
pymanager install 3.12
```

If neither command is recognized, reopen the terminal and check the manager installation. Do not continue until the version check works.

## 3. Check window support

```powershell
py -3.12 -m tkinter
```

A small Tk demonstration window should open. Close it and return to PowerShell. Installing CustomTkinter alone cannot repair a missing `_tkinter` module.

## 4. Obtain and extract the project

Sign into an account with access to the private [turcinv/SOSkuska](https://github.com/turcinv/SOSkuska) repository and choose **Code → Download ZIP**. Without access, ask the author for a **SOSkuska-source.zip** archive. Git is optional. GitHub's ZIP usually contains `SOSkuska-main`; rename the extracted project folder to `SOSkuska`.

1. Right-click the ZIP and choose **Extract All**.
2. Locate the folder directly containing `README.md`, `docs` and the `soskuska` source subfolder.
3. Move it into your user directory, such as `C:\Users\your-name\SOSkuska`.
4. Confirm that `SOSkuska\soskuska` contains `app.py` and `requirements.txt`; avoid accidental double nesting like `SOSkuska\SOSkuska\soskuska`.

Extract the files rather than running inside the archive. Do not copy a Mac virtual environment; create a Windows-local one.

## 5. Enter the project directory

```powershell
cd "$HOME\SOSkuska"
Test-Path .\soskuska\app.py
Test-Path .\soskuska\requirements.txt
```

Both checks should print `True`. `$HOME` is your user directory; no username replacement is needed. If you saved the project elsewhere, change the quoted `cd` path. Resolve any `False` result before continuing.

## 6. Create the environment and install libraries

```powershell
py -3.12 -m venv .venv
```

This creates `.venv`; no output without an error is normal. Then run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r soskuska/requirements.txt
```

Wait for successful installation. Packages stay inside this project. You do not need to activate the environment or change PowerShell execution policy. If installation fails, retain the full error instead of continuing blindly.

## 7. Launch

```powershell
.\.venv\Scripts\python.exe soskuska/app.py
```

Expect a dark **SOSkúška** window with Dashboard and sidebar navigation. Keep PowerShell open; its prompt returns when the app exits. Normally close the application using its window's close button.

Create your first subject. New databases are empty and show your actual saved data. Dashboard, My Subjects, Question bank, Practice Tests, Flashcards, Statistics, optional AI Tutor and Settings are implemented. AI Tutor requires your own Ollama setup; other study features do not.

## 8. Launch next time

Do not repeat Python installation or environment creation. Open PowerShell:

```powershell
cd "$HOME\SOSkuska"
.\.venv\Scripts\python.exe soskuska/app.py
```

Normal study works offline after installation. Data is stored at `%LOCALAPPDATA%\SOSkuska\dashboard.sqlite3`. Open `%LOCALAPPDATA%\SOSkuska` in File Explorer's address bar to locate it; deleting it removes saved data. If no new database exists but legacy `ExamPrep/dashboard.sqlite3` does, the app uses the legacy file without copying/moving/overwriting it. Explicit `--data` always wins.

## 9. Optional: development and checks

Use a separate database for experiments:

```powershell
.\.venv\Scripts\python.exe soskuska/app.py --data .local-data/dev.sqlite3
```

This check briefly opens a window with its own temporary database:

```powershell
.\.venv\Scripts\python.exe soskuska/check_dashboard.py
```

It prints `PASS` and closes the window on success. If launch or a check fails, include the complete output in a report, not just its last line.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| `py` not recognized | Finish installing the manager, reopen PowerShell and check `pymanager` too |
| `No suitable Python runtime found` | Run `py install 3.12`, or `pymanager install 3.12` for a launcher conflict |
| File checks print `False` | Find the correct directory or extract the ZIP correctly |
| Path with spaces fails | Keep the full `cd` path inside double quotes |
| `No module named customtkinter` | Reinstall requirements through `.\.venv\Scripts\python.exe` |
| Missing `_tkinter` | Use a full Python with Tk and repeat step 3; a pip-only install is insufficient |
| `Activate.ps1` blocked | Skip activation; commands above invoke the environment's Python directly |
| Double-click window closes immediately | Launch from PowerShell so the error remains visible |
| Dependency download fails | Check internet or organizational proxy settings; do not disable certificate verification |

Continue with [Development](DEVELOPMENT.md) and [How it works](HOW_IT_WORKS.md). Feature guides: [Flashcards](FLASHCARDS.md), [Statistics](STATISTICS.md), [AI Tutor](AI_TUTOR.md) and [Settings](SETTINGS.md). Questions are authored through My Subjects → Questions; Practice Tests uses those questions and keeps saved snapshots/results. Question and flashcard CSV imports are available in their respective screens; images are not implemented.

## Backup and restore

Settings now includes manual local backup and validated restore, with a pre-restore safety copy. Current schema is 8. Restore closes the app; reopen it afterward. See [Backup and restore](BACKUP_RESTORE.md).

## Import questions from CSV

Question bank now supports UTF-8 CSV import into an existing subject, with a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records; question lists show 50 per page. Current schema is 8. [Question CSV import](QUESTION_CSV_IMPORT.md).

## Import flashcards from CSV

Flashcards now supports UTF-8 CSV import into an existing deck: a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records. New cards are due immediately; existing schedules and review history are preserved. Current schema is 8. [Import flashcards from CSV](FLASHCARD_CSV_IMPORT.md).

## Saved AI Tutor conversations

AI Tutor now saves conversations locally, including the original server/model and reply status. Open saved history without networking, reconnect explicitly to continue, or delete a selected conversation after confirmation. Released in v0.12.0 with schema 7, which migrates existing study data transactionally. [Saved AI Tutor conversations](TUTOR_HISTORY.md).

## Interface language

UI language selection is implemented on this branch: English, Czech, Slovak and Russian, saved separately from AI answer language and applied after restart. Current schema is 8; the published release remains v0.12.0 until release authorization. [Interface language](UI_LANGUAGES.md).
