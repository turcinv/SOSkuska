# AI Tutor and Settings safeguards

English instructions for development agents, referenced by [AGENTS.md](../../AGENTS.md). Read this file when its routing rule applies. Paths and commands in this file are relative to the repository root.

## AI Tutor safeguards

- tutor_page.py owns session-only chat; tutor.py builds bounded context and runs daemon jobs; ollama_client.py uses direct standard-library HTTP/HTTPS. No SQLite chat persistence or schema changes. Make session loss on app close explicit.
- No request on startup/navigation. Connect loads /api/tags; Send streams /api/chat to the visible endpoint. Never automatically attach database records/files or fall back to a cloud service. Endpoint changes require clearing the prior chat. Backend/model processing is determined by the selected server.
- Workers must never call Tk or SQLite; queue events are handled by the main-thread after poll. Hidden updates must not scroll shared pages or alter another screen's draft. Shutdown cancels networking without joining a worker on the UI thread; failed focus saves must still keep the window open.
- Stop sets a cancellation event; nonblocking reads/writes/TLS handshakes poll it at most every100ms. Only the worker may mutate or close sockets/TLS state. Preserve partial text but exclude stopped/failed turns from future context. Keep one task active until its terminal event; do not consume events from an old task as a new answer. System DNS/TCP setup can delay cancellation.
- Prompt max4000 chars, answer max16000, session max12 turns; context max6 complete pairs/24000 chars. Socket timeout30s and wall-clock timer180s. Bound streamed JSON lines and model lists; reject malformed/truncated responses instead of treating them as complete.
- HTTPS verification stays enabled; reject URL credentials, paths, queries and fragments. Do not follow redirects or use environment HTTP proxies. No authenticated servers or automatic model downloads.
- Tests use loopback FakeOllama, not real downloads/cloud services. Run test_tutor.py and check_tutor.py plus the full suite; model quality/hardware performance is not established by the fixture. CI includes the eighth GUI check. AI Tutor was released in v0.7.0.

## Settings safeguards

- preferences.py validates focus 1–180 minutes, daily goal 1–1440, Ollama URL/model and AI answer language. settings_page.py saves explicitly through Store; schema 6 adds the singleton preferences row and revision. Migration is transactional and must preserve schema 5 content/history; use the frozen schema_v5.sql fixture.
- Never connect on startup, navigation or Settings Save. Use Tutor choices copies into a draft; only Save persists it. UI remains English; answer language only changes AI replies. Chat remains session-only.
- Active/paused/unsaved focus sessions retain their original target; next session uses saved duration. Goal changes immediately without changing history. Applying committed settings must not depend on another SQLite read.
- Reject stale revision under the write lock. Failed Save/Reload and navigation preserve drafts, including a failed initial load. Reload needs confirmation when dirty. Invalid saved preferences fall back safely and repair only on explicit Save.
- AI preference changes wait for an idle Tutor. Different servers require New chat when chat exists. Remembering the already-connected server must retain its connection identity and chat isolation. Prefer the saved model when available; never silently substitute an unavailable preferred model. Study-only saves preserve temporary Tutor choices when persisted AI fields are unchanged.
- Changes from another window apply in this window on Save/restart, not live; Save applies the whole loaded form, so AI guards can also apply after reloading another window's changes.
- Run test_preferences.py and check_settings.py with disposable databases; CI includes the ninth native check. English Settings guide lives under docs/; translations are under docs/cs/, docs/sk/, docs/ru/.

- Persistent Settings was released in v0.8.0. Switching servers resolves the saved model preference afresh; a same-server refresh preserves an available manual model choice.

- English-primary documentation with Czech/Slovak/Russian translations was introduced in v0.8.1. Keep published version labels aligned across the app footer, root README, all localized READMEs and changelogs.

