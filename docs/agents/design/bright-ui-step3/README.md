# Bright UI Step 3 evidence and handoff

Internal implementation record, **25 November 2026**, branch `feature/bright-ui-practice`. Implements [Step 3](../../BRIGHT_UI_REDESIGN.md) only. Published labels remain v0.19.0/schema 10. No merge or release is authorized by this record.

## Implemented

A dedicated running-test card groups subject/question/answered counts, timed or untimed status and an answered-count progress bar. The bar represents saved answers, not correctness or the current question index. The prompt has its own reading surface. Full-width A–D rows highlight only the committed choice with a filled radio, outline and bold text; row backgrounds and answer text are clickable. Previous/Next/Clear remain on the left and Finish on the right of one footer. Long content wraps in logical CTk units and scrolls to the footer.

Setup selectors share a two-column card with a full-width time-limit field. Results share a summary card, and history cards have a stronger title. Existing setup/history paths, filters, pagination, confirmations, snapshots, scoring, deadline rules, resume and save/retry semantics remain. Correct answers and explanations remain hidden until completion. No new labels, dependencies, migrations or network operations.

## Screenshots and reproduction

The [Step 1 practice capture](../bright-ui-step1/after-light/practice.png) is the previous layout. These captures reuse its disposable subject, exam, questions, session, due cards and selected answer. The clock is frozen to 25 November 2026, 12:00 UTC; the timed variant starts with five minutes. The intentionally incorrect B choice demonstrates selection styling independently of correctness; the completed fixture scores 0/2 with one unanswered question. These are synthetic study records, not real user progress or learning evidence.

| View | 1440×900 Light | 1440×900 timed Dark | 1024×700 Russian Light |
| --- | --- | --- | --- |
| Running | [Light](wide-light/practice.png) | [Dark](wide-dark-timed/practice.png) | [Russian](compact-russian/practice.png) |
| Setup/resume | [Light](wide-light/practice-setup.png) | [Dark](wide-dark-timed/practice-setup.png) | [Russian](compact-russian/practice-setup.png) |
| Submit confirmation | [Light](wide-light/practice-confirm.png) | [Dark](wide-dark-timed/practice-confirm.png) | [Russian](compact-russian/practice-confirm.png) |
| Saved result | [Light](wide-light/practice-result.png) | [Dark](wide-dark-timed/practice-result.png) | [Russian](compact-russian/practice-result.png) |
| History after scrolling | [Light](wide-light/practice-history.png) | [Dark](wide-dark-timed/practice-history.png) | [Russian](compact-russian/practice-history.png) |

Use the [Step 1 Docker command](../bright-ui-step1/README.md#reproduce-captures-without-host-windows) with `--practice-views` after the output argument. Add `--timed-practice --mode Dark` for the timed variant, or `--size compact --language Russian` for compact localization. Do not combine Practice views with Dashboard-only/empty captures. Use unique container/output names. The five views are captured through real setup/resume/confirmation/completion/history entry points; history waits for the scrolled content to paint. Metadata in each folder records the options and runtime. Defaults still capture the original Dashboard/practice/card sequence. No database is retained or host display/data mounted.

## Validation and review

- Full Linux Docker/Xvfb suite: **308 unit tests**, **two platform skips**, **all 18 GUI scripts passed**. Focused practice/history unit tests: **28 passed**.
- Existing Practice GUI checks also assert saved row selection and answered progress through navigation, failed answer writes and fresh-process resume. Timed completion/retry and background completion without changing another screen's scroll/draft continue to pass.
- Four-language checks at 100/150% startup scaling exercise long prompts/options, actual row-canvas and text-label clicks, choosing a wrong answer, clearing, save rollback, hidden setup/off-page events without writes, footer access and completed result visibility. A final focused Russian 150% run also isolates the page guard while the running panel stays gridded inside the hidden page.
- Actual appearance audits cover radio checked/hover/border contrast and progress tracks in addition to text.
- Independent Sol medium review: CTk canvas Configure routing, stale hidden callbacks and Dark radio contrast findings addressed. Re-review found no remaining blockers. No correctness information is used to style running choices.
- All 15 final captures were visually inspected. Syntax, Markdown/artifact references and diff checks are recorded on the PR. CI must be inspected separately; local results do not predeclare hosted success.

Native hardware/Windows DPI and live monitor scaling remain separate from simulated startup scaling. The existing CTk live-scaling limitation from Step 2 is unchanged. This work does not validate real Ollama answer quality. After merge, continue with **Step 4 only: Flashcard review**, when requested.
