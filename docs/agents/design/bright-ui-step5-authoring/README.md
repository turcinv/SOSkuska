# Bright UI Step 5 authoring evidence and handoff

Internal implementation record, **25 November 2026**, branch `feature/bright-ui-subjects-questions`. Implements the **Subjects and Question Bank portion of [Step 5](../../BRIGHT_UI_REDESIGN.md)** only. Published version remains **v0.21.0 / schema 10**; this work is unreleased pending its PR and merge authorization.

## Implemented

Subjects groups its title, explanation and New subject action in a header card, with labelled search on a separate surface. Questions is the subject card's primary action; Study, Edit and Delete stay available in a two-row group. Cards use two columns from 950 logical page pixels, otherwise one. Resizing repositions the existing cards and does not read SQLite or recreate the subject editor. Multiline editor fields have theme borders so their bounds remain visible on white cards. Titles, descriptions, counts and form/confirmation notices wrap in logical CTk units with left alignment.

Question Bank groups its heading/count/actions, labelled topic/difficulty filters, topic actions and search into shared surfaces. Previous/Next page controls and the page label occupy separate rows. The editor keeps the same A–D entry widgets, with two columns from 850 logical answer-panel pixels and one below; widget creation/tab order stays A–D. Fixed-width menus keep long topic names inside the selectors. Correct-answer previews have an inset surface in the authoring list; running Practice Tests are unchanged. Empty states use the existing card style.

Callbacks, editing snapshots, stale-data guards, question/topic identity, filters, 50-question pagination, deletion confirmations and CSV preview/save paths remain. No Store, validation, schema, dependency or localization changes. Editors retain their existing behavior: reopening the same subject keeps a question draft, while switching subjects resets it.

## Captures and reproduction

The disposable fixture and clock match earlier redesign captures: Computer Science plus a second Mathematics subject, two questions, one topic and 25 November 2026 at 12:00 UTC. Baseline captures use the retained v0.20.0 container; Subjects/Question Bank source is identical between that runtime and v0.21.0. Its footer therefore shows v0.20.0. New captures show v0.21.0. The comparison is synthetic UI evidence, not student outcomes or native platform acceptance.

| View | Previous Light | New Light | New Dark | Compact Russian |
| --- | --- | --- | --- | --- |
| Subjects | [Before](before-light/subjects.png) | [Light](wide-light/subjects.png) | [Dark](wide-dark/subjects.png) | [Russian](compact-russian/subjects.png) |
| Subject editor | [Before](before-light/subject-editor.png) | [Light](wide-light/subject-editor.png) | [Dark](wide-dark/subject-editor.png) | [Russian](compact-russian/subject-editor.png) |
| Question Bank | [Before](before-light/question-bank.png) | [Light](wide-light/question-bank.png) | [Dark](wide-dark/question-bank.png) | [Russian](compact-russian/question-bank.png) |
| Question editor | [Before](before-light/question-editor.png) | [Light](wide-light/question-editor.png) | [Dark](wide-dark/question-editor.png) | [Russian](compact-russian/question-editor.png) |
| Editor footer after scrolling | [Before](before-light/question-editor-footer.png) | [Light](wide-light/question-editor-footer.png) | [Dark](wide-dark/question-editor-footer.png) | [Russian](compact-russian/question-editor-footer.png) |
| Topic editor | [Before](before-light/topic-editor.png) | [Light](wide-light/topic-editor.png) | [Dark](wide-dark/topic-editor.png) | [Russian](compact-russian/topic-editor.png) |
| No matching questions | [Before](before-light/question-empty.png) | [Light](wide-light/question-empty.png) | [Dark](wide-dark/question-empty.png) | [Russian](compact-russian/question-empty.png) |

Use the [Step 1 Docker capture command](../bright-ui-step1/README.md#reproduce-captures-without-host-windows), adding `--authoring-views` after the output argument. Add `--mode Dark`, or `--size compact --language Russian`. Capture modes are mutually exclusive. Use unique container/output names and copy `container:/tmp/design-capture/.` into an already created destination. The script uses real Subjects, question/topic editor and filter entry points; it scrolls before capturing the save footer. Metadata records options and runtime. New captures reflect the checked-out code; reproducing the baseline requires its historical runtime. No host display/data mount or retained database.

## Validation and continuation

- Focused `check_question_bank.py` passed: CRUD, validation, filters, compact editor scrolling, subject isolation, deletion and reopening.
- Full Docker/Xvfb suite: **308 unit tests**, **two platform skips**, **all 18 GUI scripts passed**. Hosted CI is recorded separately on the PR. Four-language authoring checks at 100/150% startup scaling passed: long names/topic/prompt/answer, viewport bounds, real compact/wide resizing with an open subject draft and SQL reads forbidden, stable card widgets and edit snapshots, answer-grid reflow, retained question draft after navigation, failed-write retention and save-footer access.
- All **28 captures** visually inspected. Syntax, changed Markdown/artifact links, catalog parity and diff checks are checked before commit.
- Independent Sol medium review found no code blocker. Its outdated-breakpoint finding was addressed in all four architecture guides and the Dashboard layout check; final follow-up covers the added probes and capture helper.

Native Windows/macOS hardware and live-monitor scaling acceptance remain separate. Startup scaling is simulated before widget construction, preserving the known CTk live-scaling limitation. Next, only when requested after this portion is merged: **Statistics and AI Tutor portion of Step 5**. Settings and shared data panels remain a later session.
