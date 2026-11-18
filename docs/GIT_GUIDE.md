# Cloning and Git basics

[English](GIT_GUIDE.md) · [Čeština](cs/GIT_GUIDE.md) · [Slovenčina](sk/GIT_GUIDE.md) · [Русский](ru/GIT_GUIDE.md)

Git stores change history locally. GitHub hosts a remote copy and supports collaboration. A ZIP is enough to run the app; use a clone to develop and submit changes.

## 1. Get access and Git

[turcinv/SOSkuska](https://github.com/turcinv/SOSkuska) is **private**. Open it in a browser using an account with access first. A 404 may mean missing permission.

```sh
git --version
```

If Git is missing, follow its [official installation guide](https://git-scm.com/downloads/). On Windows, use Git for Windows and retain Git Credential Manager; reopen PowerShell afterward. macOS may offer Apple Command Line Tools; Linux users can use their distribution's package.

HTTPS cloning may open browser login through Git Credential Manager. Use an authorized account. Browser login alone does not necessarily authenticate Git. Never put an account password in the repository URL. See [GitHub credential guidance](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git). Existing GitHub CLI users can use `gh auth login` and `gh auth setup-git`.

## 2. Clone

Open a terminal in the parent directory where you want the project:

```sh
git clone https://github.com/turcinv/SOSkuska.git
cd SOSkuska
git status
```

This creates `SOSkuska` with `.git` history. Expect branch `main` and no local changes. Do not clone over an existing folder; choose another parent directory. Update an existing real clone with `git pull --ff-only`.

## 3. Prepare Python and launch

The clone contains neither an environment nor a database. Create a local environment on each computer. With no Python installed on Windows, follow [Windows first run](WINDOWS_FIRST_RUN.md), skipping the ZIP download steps.

Windows / PowerShell with Python 3.12 already installed:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r soskuska/requirements.txt
.\.venv\Scripts\python.exe soskuska/app.py --data .local-data/dev.sqlite3
```

macOS with Python 3.12 and Tk:

```sh
python3.12 -m venv .venv-macos
.venv-macos/bin/python -m pip install -r soskuska/requirements.txt
.venv-macos/bin/python soskuska/app.py --data .local-data/dev.sqlite3
```

Linux setup, Tk prerequisites and troubleshooting are in [Development](DEVELOPMENT.md).

## 4. Set the author for this clone

Replace both example values with your own before your first commit. GitHub also provides a private `noreply` address in email settings.

```sh
git config user.name "Your name"
git config user.email "your-address@example.com"
```

Without `--global`, these commands affect only this repository. Commit authorship and GitHub authentication are separate.

## 5. Normal workflow

Start from clean current `main`:

```sh
git switch main
git pull --ff-only
git switch -c feature/my-change
```

Edit files and run relevant [contribution checks](../CONTRIBUTING.md). Review and save your work:

```sh
git status
git diff
git add README.md
git diff --cached
git commit -m "docs: clarify setup instructions"
git push -u origin feature/my-change
```

The filename, branch and message are examples; stage the actual files you reviewed. Commit records locally; push sends history to GitHub and requires write access. Never commit or push directly to main.

On GitHub, select **Compare & pull request**, choose base `main`, explain the change and actual checks. Merge only with the user's authorization for that PR. After merging, return to main and update it. This workflow does not authorize access/visibility changes.

## 6. Update an existing clone

```sh
git status
git switch main
git pull --ff-only
```

Resolve your own local changes first. If `--ff-only` reports diverging history, inspect it; do not blindly force-push or discard work with `reset --hard`.

Reinstall requirements through your environment's Python after dependency changes. Restart after code changes. Git does not synchronize databases or environments.

## Command reference

| Command | Meaning |
| --- | --- |
| `git status` | Branch and modified files |
| `git diff` | Unstaged changes |
| `git diff --cached` | Contents of the next commit |
| `git log --oneline -5` | Latest five commits |
| `git remote -v` | Remote repository URLs |
| `git pull --ff-only` | Download updates without an automatic merge commit |

Commit sources and documentation. Environments, `.local-data/`, SQLite databases and `.env` are ignored. A downloaded ZIP has no `.git`; start Git work with a clone in another folder.
