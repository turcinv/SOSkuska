# Appearance settings

[English](APPEARANCE.md) · [Čeština](cs/APPEARANCE.md) · [Slovenčina](sk/APPEARANCE.md) · [Русский](ru/APPEARANCE.md)

**v0.29.0 — cat brand:** Light uses a Cream workspace with white cards; Dark uses Charcoal surfaces. Both share lavender pill buttons, violet accents and an always-charcoal sidebar with a lavender selected item. Saved Light/Dark/System behaviour is unchanged. [Internal captures and handoff](agents/design/cat-brand/README.md).

**v0.19.0 — redesign Step 1:** the shared theme now uses blue actions/selection, mint progress, a warm off-white Light workspace and paired Dark surfaces. Secondary buttons have a separate hover surface; Statistics progress tracks match Dashboard. Layouts, saved mode/default, navigation, data and settings behaviour are unchanged. [Internal captures, sketches and handoff](agents/design/bright-ui-step1/README.md).

Appearance settings were released in **v0.16.0** after the user confirmed v0.15.0 baseline testing complete and approved merging PR #32 on 22 November 2026. Future changes still require their own review and merge/release authorization.

Open **Settings → Appearance (applies on Save)** and choose Light, Dark or System. Save settings to apply the choice immediately and remember it for this database. Merely selecting a mode is a draft; navigation keeps that draft, while Reload confirms replacing it. Failed or stale saves keep the current appearance and draft. Existing databases default to Dark. Saving the whole Settings form retains its existing validation and AI-change guards.

Appearance is independent of interface language and AI answer language. It updates existing widgets in place: it does not rebuild screens, discard editor/Tutor drafts, reset focus/practice timing, alter saved history or start networking. UI language still needs a restart. Other app windows pick up saved settings through their own Save/restart, not live synchronization.

System follows native Windows/macOS appearance and responds to OS changes while the app is running. On Linux and other unsupported systems it deliberately uses Light. This avoids repeatedly starting desktop-detection subprocesses on the Tk thread with the pinned dependencies. Choose explicit Light/Dark on Linux. System behavior is tested with simulated OS notifications; manual native OS/DPI checks remain separate.

`theme.py` provides paired colors shared by frames, text, controls, dropdowns, placeholders, disabled primary buttons and destructive controls. `appearance.py` uses the public CustomTkinter appearance API. Automated checks audit visible text/background contrast across screens, but do not establish complete accessibility or manual platform verification.

Schema **9** adds `preferences.appearance_mode` with allowed canonical values Light/Dark/System and a Dark default. Migration preserves existing content, conversation history, languages and revision; failed migrations roll back. Backups include the choice. This release accepts schema 9 standalone backups; opening an older trusted backup copy through startup migrates it, after which a new backup can be exported. Keep originals: v0.15.0 uses schema 8 and cannot reopen schema 9 data.

Status updated 22 November 2026: the user confirmed v0.15.0 baseline testing complete and approved appearance PR #32. This checklist now targets v0.32.0; item-by-item clean-machine/DPI results are not recorded here. Leave unchecked items unverified and record device-specific evidence when testing the new release. For new checks use `--data .local-data/appearance.sqlite3`. [Next steps · 22 November 2026](NEXT_STEPS.md).

Checks: `tests/test_appearance.py`, `soskuska/check_appearance.py`, live stream preservation in `check_tutor.py`, four-language controls and frozen Windows startup in all 12 language/mode combinations. Routine GUI checks run inside the [container](CONTAINER_TESTS.md). No new application dependency is required.
