# Bright UI Step 2 evidence and handoff

Internal implementation record, **25 November 2026**, branch `feature/bright-ui-dashboard`. Scope: [Step 2](../../BRIGHT_UI_REDESIGN.md) only. Published labels remain v0.18.1/schema 10. No release or merge is authorized by this record.

## Implemented

Today's Study groups the subject picker, Start Studying, active timer/Pause/Finish, recovery/retry actions, daily goal and checklist. An empty workspace offers Create your first subject through the existing subject form. Subjects and labelled search follow the study panel. Exams/recent sessions sit alongside at wide size and below subjects at compact size; stored metrics move to a smaller summary below the columns. Dashboard cards use two columns at wide size and one at compact size.

Sidebar selection uses fill, outline and bold text, including Settings; Question Bank selects My Subjects. Collapse preserves selection and drafts. Width decisions use the visible viewport in logical CTk units, excluding the scrollbar; long card titles use the same conversion. No scoring, timer accounting, schema, data model, network or preference-save rules changed. Four new labels are translated in all four catalogs.

## Screenshots

Baseline is [Step 1 Light Dashboard](../bright-ui-step1/after-light/dashboard.png) / [Dark Dashboard](../bright-ui-step1/after-dark/dashboard.png), now merged through PR #43. The populated fixture, date and 100% capture scale are the same as Step 1. Empty captures are deliberately empty. Each folder includes metadata; images are Linux/Xvfb captures, not native Windows acceptance.

| State | Screenshot |
| --- | --- |
| 1440×900 English Light | [Dashboard](wide-light/dashboard.png) |
| 1440×900 English Dark | [Dashboard](wide-dark/dashboard.png) |
| 1024×700 English Light | [Dashboard](compact-light/dashboard.png) |
| 1024×700 Russian Dark | [Dashboard](compact-russian-dark/dashboard.png) |
| 1024×700 empty English Light | [First action](empty-light/dashboard.png) |
| 1024×700 empty Russian Light | [First action](empty-russian/dashboard.png) |

Use the [Step 1 container command](../bright-ui-step1/README.md#reproduce-captures-without-host-windows), passing `--dashboard-only`. Add `--size compact`, `--language Russian`, `--mode Dark` or `--empty` as needed; empty captures require Dashboard-only. Use unique container/output names. The script creates temporary data, refuses native Windows/macOS execution and validates the full display bounds before saving. Default wide/full capture behaviour remains available for the Step 6 comparison.

## Validation

- Final full Docker/Xvfb suite: **308 unit tests**, **two platform skips**, all **18 GUI scripts** passed.
- Dashboard check: empty first action, wide/compact placement, long Cyrillic content, sidebar Settings selection/collapse, retained search, timer save/retry, midnight refresh, deletion/history and reopen.
- Focus recovery check: abrupt GUI termination, fresh-process paused recovery, failed reads, stale discard confirmation, exclusive owner, off-page failure and retry on close.
- Four-language check: compact Dashboard at **100% and 150% startup widget/window scaling**, with a long selected Cyrillic subject, wrapped card title, recovery/discard controls and failed-save Finish/retry text. Bounds are checked against the visible canvas, not only the parent frame. Existing language, appearance, draft, history and restart checks also pass.
- Independent Sol review at medium effort: viewport/scaling and long-title findings addressed; final re-review found no remaining blockers. All six captures were visually inspected.
- CI must be checked on the PR; local success does not predeclare hosted results. The capture utility's new flags were exercised by the six actual capture runs.

## Limits and next session

Startup DPI is simulated in fresh processes. Calling CustomTkinter 5.2.2 scaling setters after constructing the UI can re-grid hidden pages/panels; this existing toolkit behaviour is not fixed here or claimed as live monitor-DPI support. Native Windows scaling, macOS trackpad/Quit and real Ollama checks remain separate.

After the PR is merged, continue with **Step 3 only: Practice Tests**. The practice layout sketch from Step 1 remains a concept, not an implemented Step 2 feature. Keep explicit review/merge authorization and repeat release acceptance after the final redesign before v1.0.0.
