# Bright UI Step 4 evidence and handoff

Internal implementation record, **25 November 2026**, branch `feature/bright-ui-flashcards`. Implements [Step 4](../../BRIGHT_UI_REDESIGN.md) only. Published labels remain **v0.20.0 / schema 10**; this feature is unreleased pending its PR merge authorization.

## Implemented

A deck header groups remaining cards and saved-review counts. Prompt and revealed answer have separate, left-aligned reading surfaces; long content wraps in logical CTk dimensions and scrolls to the controls. Reveal is the primary action before the answer appears. Existing Again / Hard / Good / Easy choices replace it in the same footer in a four-column wide or two-column compact grid. Ratings stay disabled and hidden before Reveal. Deck actions wrap into two rows; Study due is primary when cards are due, otherwise New card is primary. Search labels, deck/card/history surfaces and empty states share the existing theme.

Write errors preserve the revealed card and show retry feedback beside the footer. After a committed rating, the old card is invalidated and its ratings disabled before reading the next card. If that read fails, a localized notice identifies Refresh card; refresh retries only the read. The pending flag is UI state, not a database migration. Scheduling rules, snapshots, stale-rating guards, editor drafts and CSV preview entry points remain unchanged.

## Screenshots and reproduction

The [Step 1 before-reveal](../bright-ui-step1/after-light/flashcard.png) and [revealed](../bright-ui-step1/after-light/flashcard-revealed.png) captures show the previous layout. These captures reuse its disposable fixture and frozen clock: 25 November 2026, 12:00 UTC. Two Good ratings demonstrate saved review history and a completed batch; they are synthetic self-assessments, not measured learning outcomes.

| View | 1440×900 Light | 1440×900 Dark | 1024×700 Russian Light |
| --- | --- | --- | --- |
| Deck list | [Light](wide-light/decks.png) | [Dark](wide-dark/decks.png) | [Russian](compact-russian/decks.png) |
| Open deck | [Light](wide-light/deck.png) | [Dark](wide-dark/deck.png) | [Russian](compact-russian/deck.png) |
| Before Reveal | [Light](wide-light/flashcard.png) | [Dark](wide-dark/flashcard.png) | [Russian](compact-russian/flashcard.png) |
| Revealed answer | [Light](wide-light/flashcard-revealed.png) | [Dark](wide-dark/flashcard-revealed.png) | [Russian](compact-russian/flashcard-revealed.png) |
| Batch complete | [Light](wide-light/flashcard-complete.png) | [Dark](wide-dark/flashcard-complete.png) | [Russian](compact-russian/flashcard-complete.png) |
| No due cards | [Light](wide-light/deck-no-due.png) | [Dark](wide-dark/deck-no-due.png) | [Russian](compact-russian/deck-no-due.png) |
| Saved history | [Light](wide-light/flashcard-history.png) | [Dark](wide-dark/flashcard-history.png) | [Russian](compact-russian/flashcard-history.png) |

Use the [Step 1 Docker capture command](../bright-ui-step1/README.md#reproduce-captures-without-host-windows), adding `--flashcard-views` after the output argument. Add `--mode Dark`, or `--size compact --language Russian` for the other variants. Choose only one of Flashcard views, Practice views or Dashboard-only. Use unique container/output names; create the destination and copy `container:/tmp/design-capture/.` into it to avoid nested folders. The utility asserts four/two-column rating order and follows real deck/reveal/rating/history entry points. Metadata records runtime and options. No host display/data mounts or retained database.

## Validation and review

- Full Linux Docker/Xvfb suite: **308 unit tests**, **two platform skips**, **all 18 GUI scripts passed**. Focused flashcard unit tests: **29 passed**.
- Flashcard checks preserve CRUD, reveal-before-rating, stale revisions, retry, scheduling, retained history, deletion and fresh-process reopening. CSV checks cover preview/draft retention, atomic retry, duplicates, pagination and reopening.
- Four-language checks at 100/150% startup scaling cover 1,900-character prompts, 3,700-character answers, deck-action and footer bounds, hidden ratings, failed-write retry, off-page guards, next-card read failure after commit without duplicate ratings, refresh and a completed batch. Actual wide captures assert four rating columns; compact captures assert two.
- Independent Sol medium review: left alignment, scaled grid padding and local retry feedback addressed. Final review found no application/capture blockers; localized retry button names corrected. The reviewed missing Slovak architecture section and capture README are included in the final documentation.
- All **21 captures** visually inspected. Syntax, changed Markdown/artifact references, catalog parity and `git diff --check` checked before commit. Hosted CI is reported separately on the PR.

These are Linux/Xvfb checks, not native Windows/macOS hardware acceptance. Startup scaling does not establish live monitor-scaling support; the existing CTk limitation is unchanged. Continue only when requested with the **Subjects and Question Bank portion of Step 5**; Statistics/Tutor and Settings/data panels are separate later sessions.
