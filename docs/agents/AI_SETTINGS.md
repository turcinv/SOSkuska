# AI Tutor and Settings safeguards

English instructions for development agents, referenced by [AGENTS.md](../../AGENTS.md). Read this file when its routing rule applies. Paths and commands in this file are relative to the repository root.

## AI Tutor safeguards

- tutor_page.py owns locally saved chat; tutor.py builds bounded context and runs daemon jobs; ollama_client.py uses direct standard-library HTTP/HTTPS. Schema 7 persists local conversation/turn snapshots on the Tk thread. Keep explicit server/model ownership and interruption/save-retry states.
- No request on startup/navigation. Connect loads /api/tags; Send streams /api/chat to the visible endpoint. Never automatically attach database records/files or fall back to a cloud service. Endpoint changes require clearing the prior chat. Backend/model processing is determined by the selected server.
- Workers must never call Tk or SQLite; queue events are handled by the main-thread after poll. Hidden updates must not scroll shared pages or alter another screen's draft. Shutdown cancels networking without joining a worker on the UI thread; failed focus saves must still keep the window open.
- Stop sets a cancellation event; nonblocking reads/writes/TLS handshakes poll it at most every100ms. Only the worker may mutate or close sockets/TLS state. Preserve partial text but exclude stopped/failed turns from future context. Keep one task active until its terminal event; do not consume events from an old task as a new answer. System DNS/TCP setup can delay cancellation.
- Prompt max4000 chars, answer max16000, session max12 turns; context max6 complete pairs/24000 chars. Socket timeout30s and wall-clock timer180s. Bound streamed JSON lines and model lists; reject malformed/truncated responses instead of treating them as complete.
- HTTPS verification stays enabled; reject URL credentials, paths, queries and fragments. Do not follow redirects or use environment HTTP proxies. No authenticated servers or automatic model downloads.
- Tests use loopback FakeOllama, not real downloads/cloud services. Run test_tutor.py and check_tutor.py plus the full suite; model quality/hardware performance is not established by the fixture. CI includes the eighth GUI check. AI Tutor was released in v0.7.0.

## Settings safeguards

- preferences.py validates focus 1–180 minutes, daily goal 1–1440, Ollama URL/model and AI answer language. settings_page.py saves explicitly through Store; schema 6 adds the singleton preferences row and revision. Migration is transactional and must preserve schema 5 content/history; use the frozen schema_v5.sql fixture.
- Never connect on startup, navigation or Settings Save. Use Tutor choices copies into a draft; only Save persists it. UI language applies after restart; AI answer language remains independent. Conversations save separately in the local database.
- Active/paused/unsaved focus sessions retain their original target; next session uses saved duration. Goal changes immediately without changing history. Applying committed settings must not depend on another SQLite read.
- Reject stale revision under the write lock. Failed Save/Reload and navigation preserve drafts, including a failed initial load. Reload needs confirmation when dirty. Invalid saved preferences fall back safely and repair only on explicit Save.
- AI preference changes wait for an idle Tutor. Different servers require New chat when chat exists. Remembering the already-connected server must retain its connection identity and chat isolation. Prefer the saved model when available; never silently substitute an unavailable preferred model. Study-only saves preserve temporary Tutor choices when persisted AI fields are unchanged.
- Changes from another window apply in this window on Save/restart, not live; Save applies the whole loaded form, so AI guards can also apply after reloading another window's changes.
- Run test_preferences.py and check_settings.py with disposable databases; CI includes the ninth native check. English Settings guide lives under docs/; translations are under docs/cs/, docs/sk/, docs/ru/.

- Persistent Settings was released in v0.8.0. Switching servers resolves the saved model preference afresh; a same-server refresh preserves an available manual model choice.

- English-primary documentation with Czech/Slovak/Russian translations was introduced in v0.8.1. Keep published version labels aligned across the app footer, root README, all localized READMEs and changelogs.


## Local history safeguards (v0.12.0)

- Schema 7 adds tutor_conversations/tutor_turns. A chat's endpoint/model are immutable; new owner requires New chat. Opening history never connects. Use the displayed saved owner even before a connection exists. Send stores a pending question before starting HTTP, then terminal reply saves atomically with a conversation revision check. No worker SQLite/Tk calls.
- New chat keeps history; delete confirms and checks revision. Keep drafts on failed writes/reads and same-conversation reload. A terminal save failure retains reply text, blocks Send/history changes and normal Quit until Retry save reply or confirmed Discard unsaved. Discard keeps the next prompt. Quit brings hidden save errors to AI Tutor.
- Normal close saves visible partial text as interrupted. Abrupt crashes can leave pending questions and lose uncheckpointed stream text. Recovery is explicit, confirms that another window may be active and invalidates late writers. Never feed pending/stopped/failed/interrupted text into model context. Validate chunks before enqueue so unsupported controls cannot create an unsaveable reply.
- Titles trim after truncation. Backup validation includes text, exact ordered 1–12 turns, pending-only-last/empty-answer and revision = 2*turn_count - pending_last. Preserve both new tables and sequences on backup/restore. Restore accepts current schema 10 only; migrate a separate copy of an older trusted backup via startup before exporting a current backup.
- Run test_tutor_history.py, check_tutor_history.py and affected Tutor/Settings/backup checks. CI includes fourteen native scripts. Keep TUTOR_HISTORY.md and related user guides aligned in all four languages; Local Tutor history was released in v0.12.0; keep published labels aligned.

## Interface language safeguards (v0.13.0)

- Schema 8 adds preferences.ui_language; preserve answer_language, prior revision and all study/chat rows. Frozen schema_v7.sql verifies migration/rollback. Schema-6 initialization must insert only its original columns before the later ALTER; preference saves name columns explicitly.
- Translator is fixed for the process at launch. Settings Save persists the choice but never rebuilds screens, replaces drafts, interrupts a task, changes the global locale or starts networking. UI and AI answer languages are independent. English is the migration/default fallback.
- LocalizedOptionMenu owns a display variable and traces the canonical variable. Translate only known domain choices. Raw subject/history/model names remain opaque; sentinels are explicit empty_text, never inferred from user text. Empty lists remain empty; unknown stale dropdown callbacks are ignored. Remove traces on destroy.
- Use explicit tr boundaries for UI copy, keeping fields such as question/card text, user names, models, paths and CSV headers unmodified. Keep all four catalogs' keys and placeholder format contracts aligned. Unknown technical errors fall back to their original text; do not run machine translation at runtime.
- Run test_localization.py/check_ui_languages.py and full regression checks. CI includes fourteen GUI scripts. Cover all four languages at 1024×700, draft retention, independent answer language, restart persistence, domain IDs, raw sentinel-like names and dropdown trace cleanup. Maintain UI_LANGUAGES.md in all four documentation languages.

## Appearance safeguards (v0.16.0)

Schema 9 adds appearance_mode Light/Dark/System with Dark default. Keep migration/revisions atomic; preserve language/history. Save applies to existing paired-color widgets through appearance.apply_appearance, never by screen reconstruction or I/O. Theme changes must not reset drafts, focus/practice, or an active Tutor request. Linux System deliberately resolves to Light: pinned darkdetect otherwise starts gsettings synchronously at CTk's 30ms polling cadence. Windows/macOS System uses native detection; use only public CTk APIs. Caption/checkmark/disabled-on-primary/placeholder colors have distinct roles; audit contrast on real widget backgrounds. Maintain all four catalogs/guides, frozen startup checks and schema-8 migration fixture. The baseline-testing gate was satisfied by the user on 22 November 2026 and PR #32 merged; retain normal per-PR merge/release authorization for future work.

## Tutor feedback placement

Tutor `set_status` updates both the header and the feedback beside recovery controls. Keep copy-before-discard and other-window interruption warnings visible near their confirmation buttons after scrolling. The model selector needs a full-width row for localized instructions; preserve its canonical value and explicit connection semantics. Geometry changes only reposition existing setup/recovery widgets.

## Completed-question explanation safeguards

Only completed result snapshots may prepare a Tutor draft, identified by `(attempt_id, position)`. Preview and prepare perform no HTTP or chat writes; Send retains the normal persist-before-request path. Reject complete prompts over 4,000 characters without truncation. Capture the exact preview identity in consent callbacks, invalidate it on navigation, and revalidate the completed snapshot before handoff. Require an idle, clean New chat with a literally empty prompt, no unsaved reply and no pending confirmation; preserve all existing work. Reveal the draft only while Tutor still owns that exact content and the shared viewport. `test_question_explanation.py` and `check_question_explanation.py` cover the shortcut; real-model explanation quality remains manual.


Study modes retain the exact v0.25 default prompt for Explain answer, including its length budget. Other modes add explicit prompt instructions. Hint shares only question/choices and omits selected answer, answer key and saved explanation; never attach these via another automatic context path. Mode changes replace the preview and invalidate old Prepare and dropdown callbacks. Mode labels are localized but their values remain canonical. Mode following is model-dependent, not automatic grading; real-model evaluation was deferred by the user on 26 November 2026.
