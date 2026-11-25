# Next steps · 25 November 2026

[English](NEXT_STEPS.md) · [Čeština](cs/NEXT_STEPS.md) · [Slovenčina](sk/NEXT_STEPS.md) · [Русский](ru/NEXT_STEPS.md)

Current release: **v0.20.0**, schema **10**. Bright UI Steps 1–3 are implemented through PRs #43, #44 and #46: theme, Dashboard/sidebar and Practice Tests.

1. **Next: Step 4, Flashcard review.** Follow the [design plan](agents/BRIGHT_UI_REDESIGN.md) and [Step 3 handoff](agents/design/bright-ui-step3/README.md), on a separate branch with independent Sol medium review and container checks. Preserve reveal-before-rating, scheduling, retained review history and import drafts. Do not implement all remaining steps at once.
2. **Complete release acceptance after the redesign.** Use the [Windows checklist](WINDOWS_ACCEPTANCE.md) with disposable data and recorded OS/build, hardware, scaling, version/hash and outcomes. Startup scaling checks are not native/live-DPI acceptance. Test a real Ollama model separately, recording server/model versions, hardware, streaming/Stop/reconnect/history and offline study.
3. **Finish the semester report and presentation separately.** Keep identity/course/language/deadline placeholders until supplied; add real screenshots, references and evaluation evidence. Follow the course instructions, refresh document fields and inspect final pagination.

Before v1.0.0, resolve acceptance findings through reviewed PRs and rerun the relevant checks. New work, merge and publication need their own authorization. No manual result is marked passed by this status update.
