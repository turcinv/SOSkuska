# Bright UI Step 5 Statistics/Tutor evidence and handoff

Internal implementation record, **25 November 2026**, branch `feature/bright-ui-statistics-tutor`. Implements the **Statistics and AI Tutor portion of [Step 5](../../BRIGHT_UI_REDESIGN.md)** only. Merged through [PR #52](https://github.com/turcinv/SOSkuska/pull/52), commit `532d13a`, and released in **v0.23.0 / schema 10**. Captures retain implementation-time version labels.

## Implemented

Statistics groups title/status/period/Refresh in a header and places three summary cards side by side at 950 logical pixels, otherwise stacked. The period picker keeps a fixed readable width. Subject and daily bars remain below; all totals, weighted accuracy, date periods and self-rating definitions remain unchanged. Labels are left aligned and wrapped. Failed reads preserve the displayed report; resizing only repositions existing cards and does not read data.

Tutor groups server/model/language choices and local history controls into separate cards, side by side at 950 logical pixels and stacked below. Model has a full-width row for translated connection instructions. Ownership, bordered transcript, prompt, Send/Stop/New chat and recovery controls share a card. Recovery controls use three columns at 850 logical pixels or two below. `set_status` repeats existing status text in the header and beside recovery actions, including copy-before-discard and other-window interruption confirmations. No new messages or translation keys.

Existing request, Stop, task queue, context, ownership, save/retry, pending/interrupted recovery, offline history and prompt-preservation paths remain. No automatic connection, database/schema or dependency change. Reflow changes existing widget geometry only. Stable shared-container widths with gutter/inset/rounding allowance avoid a confirmed one-pixel loop when Czech summary text wraps; same-mode and unchanged-width callbacks do no layout work.

## Captures and reproduction

The fixture uses the same frozen 25 November 2026, 12:00 UTC clock and disposable Computer Science data as earlier captures. For these views, the two-question practice attempt completes at 0/2 (one incorrect saved answer and one unanswered); focus time is 25 minutes. A saved Tutor conversation is seeded explicitly with a documented synthetic answer, opened offline, and given an unsent prompt. No real model response or student performance is claimed. A forced read failure demonstrates retained Statistics feedback.

The baseline uses the retained v0.21.0 container; Statistics/Tutor source is identical between that runtime and v0.22.0. Its footer shows v0.21.0. New captures show the current v0.22.0 label. No real user data is used.

| View | Previous Light | New Light | New Dark | Compact Russian |
| --- | --- | --- | --- | --- |
| Statistics summary | [Before](before-light/statistics.png) | [Light](wide-light/statistics.png) | [Dark](wide-dark/statistics.png) | [Russian](compact-russian/statistics.png) |
| Daily activity after scrolling | [Before](before-light/statistics-daily.png) | [Light](wide-light/statistics-daily.png) | [Dark](wide-dark/statistics-daily.png) | [Russian](compact-russian/statistics-daily.png) |
| Failed refresh, prior report kept | [Before](before-light/statistics-retry.png) | [Light](wide-light/statistics-retry.png) | [Dark](wide-dark/statistics-retry.png) | [Russian](compact-russian/statistics-retry.png) |
| Tutor setup and offline history | [Before](before-light/tutor.png) | [Light](wide-light/tutor.png) | [Dark](wide-dark/tutor.png) | [Russian](compact-russian/tutor.png) |
| Opened conversation | [Before](before-light/tutor-conversation.png) | [Light](wide-light/tutor-conversation.png) | [Dark](wide-dark/tutor-conversation.png) | [Russian](compact-russian/tutor-conversation.png) |
| Prompt, actions and feedback | [Before](before-light/tutor-footer.png) | [Light](wide-light/tutor-footer.png) | [Dark](wide-dark/tutor-footer.png) | [Russian](compact-russian/tutor-footer.png) |

Use the [Step 1 Docker capture command](../bright-ui-step1/README.md#reproduce-captures-without-host-windows), adding `--report-views` after the output argument. Add `--mode Dark`, or `--size compact --language Russian` for the other variants. Capture modes are mutually exclusive. Use unique container/output names; copy `container:/tmp/design-capture/.` into an already created destination. Metadata records options/runtime. Current captures follow the checked-out source; historical baseline requires its prior runtime. No host display/data mount or retained database.

## Validation and review

- Full Linux Docker/Xvfb suite passed: **308 unit tests**, **two platform skips**, **all 20 GUI scripts**. All five feature CI jobs passed in run `45633577816`; release assets are built separately from the final main/tag commit. Existing Statistics/Tutor/history checks cover empty data, all periods, weighted retained history, read retry, explicit connection, real loopback streaming/Stop, UTF-8, navigation, write failures, offline history, interruption, close/restart and persisted ownership.
- New `check_report_layout.py` is a separate bounded script in the shared runner, for **20 GUI scripts** total. It tests four languages at 100/150% startup scaling, empty/populated Statistics, report identity across failed reads, geometry without SQL, exact Czech compact/wide resize, long labels, localized model instruction at the wide threshold, offline history, existing transcript/prompt widgets during busy resizing, hidden stream consumption/scroll isolation, Stop and visible discard warning.
- The simulated busy queue is UI/state coverage; existing loopback tests establish the network event path. No model downloads or cloud calls. Each script retains its 60-second bound; new child probes retain bounded execution.
- Independent Sol medium review addressed clipped Russian model instructions and distant recovery warnings. Additional resize investigation identified the shared-width rounding safeguard; the resulting four-language probes pass.
- All **24 captures** visually inspected. Syntax, Markdown/artifact links, catalog parity, baseline source equivalence and diff checks are checked before commit. CI results must be read separately, not inferred from local runs.

Native hardware/live-monitor DPI and real Ollama answer quality remain separate acceptance work. Next only when requested after merge: **Settings and shared backup/import panels**, then Step 6 regression/demo and manual release acceptance.
