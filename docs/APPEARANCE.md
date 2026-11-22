# Appearance settings

[English](APPEARANCE.md) · [Čeština](cs/APPEARANCE.md) · [Slovenčina](sk/APPEARANCE.md) · [Русский](ru/APPEARANCE.md)

This feature is implemented on the appearance branch and is **not part of released v0.15.0**. Keep the feature PR unmerged until the user confirms v0.15.0 testing is complete and explicitly approves merging. Baseline defects go through separate fix PRs.

Open **Settings → Appearance (applies on Save)** and choose Light, Dark or System. Save settings to apply the choice immediately and remember it for this database. Merely selecting a mode is a draft; navigation keeps that draft, while Reload confirms replacing it. Failed or stale saves keep the current appearance and draft. Existing databases default to Dark. Saving the whole Settings form retains its existing validation and AI-change guards.

Appearance is independent of interface language and AI answer language. It updates existing widgets in place: it does not rebuild screens, discard editor/Tutor drafts, reset focus/practice timing, alter saved history or start networking. UI language still needs a restart. Other app windows pick up saved settings through their own Save/restart, not live synchronization.

System follows native Windows/macOS appearance and responds to OS changes while the app is running. On Linux and other unsupported systems it deliberately uses Light. This avoids repeatedly starting desktop-detection subprocesses on the Tk thread with the pinned dependencies. Choose explicit Light/Dark on Linux. System behavior is tested with simulated OS notifications; manual native OS/DPI checks remain separate.

`theme.py` provides paired colors shared by frames, text, controls, dropdowns, placeholders, disabled primary buttons and destructive controls. `appearance.py` uses the public CustomTkinter appearance API. Automated checks audit visible text/background contrast across screens, but do not establish complete accessibility or manual platform verification.

Schema **9** adds `preferences.appearance_mode` with allowed canonical values Light/Dark/System and a Dark default. Migration preserves existing content, conversation history, languages and revision; failed migrations roll back. Backups include the choice. This branch accepts schema 9 standalone backups; opening an older trusted backup copy through startup migrates it, after which a new backup can be exported. Keep originals: v0.15.0 uses schema 8 and cannot reopen schema 9 data.

To test this branch while keeping v0.15.0 acceptance separate, use a new disposable `--data .local-data/appearance.sqlite3` database or a separate copy. Do not open the baseline test database with the feature build. The [Windows acceptance checklist](WINDOWS_ACCEPTANCE.md) remains about the released baseline.

Checks: `tests/test_appearance.py`, `soskuska/check_appearance.py`, live stream preservation in `check_tutor.py`, four-language controls and frozen Windows startup in all 12 language/mode combinations. Routine GUI checks run inside the [container](CONTAINER_TESTS.md). No new application dependency is required.
