# Settings (introduced in v0.8.0)

[English](SETTINGS.md) · [Čeština](cs/SETTINGS.md) · [Slovenčina](sk/SETTINGS.md) · [Русский](ru/SETTINGS.md)

Preferences use the same local database as study data.

In **Settings**, choose the next focus duration (1–180 minutes; default 15), daily goal (1–1,440 minutes; default 60), Ollama URL, preferred model and AI answer language. **Save settings** saves and applies the whole form. Drafts survive navigation but not closing the app. Active/paused sessions retain their original duration. Goals update immediately without rewriting history.

**Use Tutor choices** only copies the current AI Tutor choices into the form; Save settings is still required. Changes directly in AI Tutor are temporary. Startup, navigation and Save never create a network connection; choose Connect / refresh explicitly. An unavailable preferred model is not silently replaced. Answer language applies to AI replies, not the English UI.

Wait for or Stop an active AI request before changing AI preferences. Study preferences can still be saved. If an existing chat belongs to another server, clear it with New chat and confirmation first. Saving the already-connected server preserves its chat. Chat is still lost on app close.

Failed writes and conflicting edits from another window keep the draft. Copy it before Reload; replacing a changed form requires a second click. Changes from another window are not applied live: Save or restart applies them in this window. Save applies all loaded fields, including externally changed AI preferences, so the same guards can apply. Invalid stored preferences display safe defaults and repair only on explicit Save.

Preferences belong to the selected database (`--data`), without synchronization or encryption. Themes, UI translations, backups and saved AI conversations remain unimplemented.

Connecting to a different server resolves the model from the saved preference again. Refreshing the same server preserves an available manual selection.
