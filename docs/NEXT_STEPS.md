# Next steps · 26 November 2026

[English](NEXT_STEPS.md) · [Čeština](cs/NEXT_STEPS.md) · [Slovenčina](sk/NEXT_STEPS.md) · [Русский](ru/NEXT_STEPS.md)

Current release: **v0.26.0**, schema **10**. Bright UI implementation Steps 1–5 are complete through PRs #43, #44, #46, #48, #50, #52 and #54. Step 6 acceptance and demo preparation remain.

## Planned for today · 26 November 2026

Run a **full review of the current main branch with Astra**, using v0.26.0 as the published baseline. This is planned work, not a completed review or a request to start it automatically.

- Record the exact reviewed commit. Cover application behavior and architecture, SQLite migrations/data integrity, draft and concurrent-state safety, UI/navigation/scrolling, AI Tutor and study modes, backup/imports, CI/Windows packaging and documentation consistency.
- Use disposable data and container GUI checks; preserve the user's desktop and normal database. Real-model LLM testing remains deferred and is not part of this planned review.
- Save actionable findings in the repository with severity, file/line references, reproduction or evidence and resolution status. Fixes follow through a separate branch/PR; merge and release need their own authorization.

1. **Next: Step 6, regression checks and teacher demo.** Follow the [design plan](agents/BRIGHT_UI_REDESIGN.md) and [Settings/data handoff](agents/design/bright-ui-step5-settings/README.md). Use disposable data to verify the complete study flow, Light/Dark/System, four languages and compact/wide layouts; refresh the final screenshot/demo evidence. Make any fixes through a separate reviewed branch/PR. Do not infer manual hardware acceptance from automated checks.
2. **Complete release acceptance after the redesign.** Use the [Windows checklist](WINDOWS_ACCEPTANCE.md) with disposable data and recorded OS/build, hardware, scaling, version/hash and outcomes. Startup scaling checks are not native/live-DPI acceptance. Test a real Ollama model separately, recording server/model versions, hardware, streaming/Stop/reconnect/history and offline study.
3. **Finish the semester report and presentation separately.** Keep identity/course/language/deadline placeholders until supplied; add real screenshots, references and evaluation evidence. Follow the course instructions, refresh document fields and inspect final pagination.

Before v1.0.0, resolve acceptance findings through reviewed PRs and rerun the relevant checks. New work, merge and publication need their own authorization. No manual result is marked passed by this status update.
