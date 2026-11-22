# Settings (introduced in v0.8.0)

[English](SETTINGS.md) · [Čeština](cs/SETTINGS.md) · [Slovenčina](sk/SETTINGS.md) · [Русский](ru/SETTINGS.md)

Preferences use the same local database as study data.

In **Settings**, choose the next focus duration (1–180 minutes; default 15), daily goal (1–1,440 minutes; default 60), Ollama URL, preferred model and AI answer language. **Save settings** saves and applies the whole form. Drafts survive navigation but not closing the app. Active/paused sessions retain their original duration. Goals update immediately without rewriting history.

**Use Tutor choices** only copies the current AI Tutor choices into the form; Save settings is still required. Changes directly in AI Tutor are temporary. Startup, navigation and Save never create a network connection; choose Connect / refresh explicitly. An unavailable preferred model is not silently replaced. Answer language applies to AI replies, not the English UI.

Wait for or Stop an active AI request before changing AI preferences. Study preferences can still be saved. If an existing chat belongs to another server, detach it with New chat and confirmation first; saved history is kept. Saving the already-connected server preserves its chat. Conversations remain saved after app close.

Failed writes and conflicting edits from another window keep the draft. Copy it before Reload; replacing a changed form requires a second click. Changes from another window are not applied live: Save or restart applies them in this window. Save applies all loaded fields, including externally changed AI preferences, so the same guards can apply. Invalid stored preferences display safe defaults and repair only on explicit Save.

Preferences belong to the selected database (`--data`), without synchronization or encryption. Theme selection remains unimplemented.

Connecting to a different server resolves the model from the saved preference again. Refreshing the same server preserves an available manual selection.

## Backup and restore

Settings now includes manual local backup and validated restore, with a pre-restore safety copy. Current schema is 10. Restore closes the app; reopen it afterward. See [Backup and restore](BACKUP_RESTORE.md).

## Saved AI Tutor conversations

AI Tutor now saves conversations locally, including the original server/model and reply status. Open saved history without networking, reconnect explicitly to continue, or delete a selected conversation after confirmation. Released in v0.12.0 with schema 7, which migrates existing study data transactionally. [Saved AI Tutor conversations](TUTOR_HISTORY.md).

## Interface language

UI language selection is available in v0.13.0: English, Czech, Slovak and Russian, saved separately from AI answer language and applied after restart. Current schema is 10. [Interface language](UI_LANGUAGES.md).

## Appearance settings

v0.16.0 adds saved Light/Dark/System choices, applied on Save without rebuilding screens or losing active work. System follows Windows/macOS and uses Light on Linux. Current schema is 10. The user confirmed baseline testing complete and approved merging appearance PR #32 on 22 November 2026. [Appearance settings](APPEARANCE.md).

## Focus-session recovery

v0.17.0 adds focus-session crash recovery using schema **10**. Keep a backup before opening existing data: migration is transactional, but v0.16.0 cannot open a schema-10 database. [Focus-session recovery](FOCUS_RECOVERY.md).

## Scheduled local backups

Scheduled local backups are available in **v0.18.0**. SQLite schema remains **10**. Manual backup/restore continues to work independently. [Scheduled local backups](SCHEDULED_BACKUPS.md).
