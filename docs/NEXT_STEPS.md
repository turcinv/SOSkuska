# Next steps · 25 November 2026

[English](NEXT_STEPS.md) · [Čeština](cs/NEXT_STEPS.md) · [Slovenčina](sk/NEXT_STEPS.md) · [Русский](ru/NEXT_STEPS.md)

Current release: **v0.24.0**, schema **10**. Bright UI implementation Steps 1–5 are complete through PRs #43, #44, #46, #48, #50, #52 and #54. Step 6 acceptance and demo preparation remain.

1. **Next: Step 6, regression checks and teacher demo.** Follow the [design plan](agents/BRIGHT_UI_REDESIGN.md) and [Settings/data handoff](agents/design/bright-ui-step5-settings/README.md). Use disposable data to verify the complete study flow, Light/Dark/System, four languages and compact/wide layouts; refresh the final screenshot/demo evidence. Make any fixes through a separate reviewed branch/PR. Do not infer manual hardware acceptance from automated checks.
2. **Complete release acceptance after the redesign.** Use the [Windows checklist](WINDOWS_ACCEPTANCE.md) with disposable data and recorded OS/build, hardware, scaling, version/hash and outcomes. Startup scaling checks are not native/live-DPI acceptance. Test a real Ollama model separately, recording server/model versions, hardware, streaming/Stop/reconnect/history and offline study.
3. **Finish the semester report and presentation separately.** Keep identity/course/language/deadline placeholders until supplied; add real screenshots, references and evaluation evidence. Follow the course instructions, refresh document fields and inspect final pagination.

Before v1.0.0, resolve acceptance findings through reviewed PRs and rerun the relevant checks. New work, merge and publication need their own authorization. No manual result is marked passed by this status update.

## AI improvement plan · 26 November 2026

A separate [stepped AI plan](AI_IMPROVEMENTS.md) proposes Explain this question for completed Practice results first. It is planning only; implementation, merge and release need separate decisions. The existing final acceptance/demo work remains outstanding.
