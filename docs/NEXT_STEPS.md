# Next steps · 26 November 2026

[English](NEXT_STEPS.md) · [Čeština](cs/NEXT_STEPS.md) · [Slovenčina](sk/NEXT_STEPS.md) · [Русский](ru/NEXT_STEPS.md)

Current release: **v0.27.0**, schema **10**. Bright UI implementation Steps 1–5 are complete through PRs #43, #44, #46, #48, #50, #52 and #54. Step 6 acceptance and demo preparation remain.

## Full Astra review completed · 26 November 2026

The requested full **Astra 6.2 medium** review of main/v0.26.0 is complete. Reviewed commit: `db38e08802058480bbed250c16eeffc23bad143b`. **All five findings are released in v0.26.1** in [Review findings](REVIEW_FINDINGS.md), IDs A62-05–A62-09. Fixes should use a separate branch/PR; merge and release require their own authorization. Existing automated checks passed; targeted checks used disposable data and Docker/Xvfb. Real-model LLM testing remains deferred.

1. **Next: Step 6, regression checks and teacher demo.** Follow the [design plan](agents/BRIGHT_UI_REDESIGN.md) and [Settings/data handoff](agents/design/bright-ui-step5-settings/README.md). Use disposable data to verify the complete study flow, Light/Dark/System, four languages and compact/wide layouts; refresh the final screenshot/demo evidence. Make any fixes through a separate reviewed branch/PR. Do not infer manual hardware acceptance from automated checks.
2. **Complete release acceptance after the redesign.** Use the [Windows checklist](WINDOWS_ACCEPTANCE.md) with disposable data and recorded OS/build, hardware, scaling, version/hash and outcomes. Startup scaling checks are not native/live-DPI acceptance. Test a real Ollama model separately, recording server/model versions, hardware, streaming/Stop/reconnect/history and offline study.
3. **Finish the semester report and presentation separately.** Keep identity/course/language/deadline placeholders until supplied; add real screenshots, references and evaluation evidence. Follow the course instructions, refresh document fields and inspect final pagination.

Before v1.0.0, resolve acceptance findings through reviewed PRs and rerun the relevant checks. New work, merge and publication need their own authorization. No manual result is marked passed by this status update.
