# Next steps · 25 November 2026

[English](NEXT_STEPS.md) · [Čeština](cs/NEXT_STEPS.md) · [Slovenčina](sk/NEXT_STEPS.md) · [Русский](ru/NEXT_STEPS.md)

Current release: **v0.19.0**, schema **10**. Bright UI Steps 1–2 are implemented through PRs #43 and #44: the shared theme and Dashboard/sidebar. All four earlier Astra findings remain resolved. This release is not a declaration of v1.0.0 acceptance.

1. **Next implementation milestone: Step 3, Practice Tests.** Follow the [design plan](agents/BRIGHT_UI_REDESIGN.md) and [Step 2 handoff](agents/design/bright-ui-step2/README.md). Use a new branch, preserve answer/deadline/history rules, run appropriate container checks and obtain independent Sol review at medium effort. Do not implement the remaining design steps all at once. New work, merge and release need their own authorization.
2. **Repeat real acceptance after the redesign.** Use the current [Windows package](WINDOWS_PORTABLE.md) and [manual checklist](WINDOWS_ACCEPTANCE.md), with disposable data and OS/build, hardware, resolution/scaling, version/hash and results. Container startup-scale checks at 100/150% are not native Windows or live monitor-DPI evidence. Existing CTk live-scaling limitations remain documented in the handoff.
3. **Test a real Ollama model.** Record model/server versions, hardware, endpoint without credentials, date and Connect/stream/Stop/reconnect/saved-chat outcomes. Confirm offline study with the server stopped. Fake-server CI does not establish real-model quality or performance.
4. **Finish the semester report and presentation separately.** Keep student/course/language/deadline fields as placeholders until supplied. Complete real screenshots, references and actual evaluation evidence; update generated fields and inspect final pagination. Follow the supplied course instructions. Do not infer an exact deadline or submission compliance from passing app tests.

Before v1.0.0, complete acceptance, resolve findings in reviewed PRs, rerun checks and publish only with user approval. No manual checklist is marked passed by this status update. The historical v0.15.0 confirmation does not verify the redesigned release.
