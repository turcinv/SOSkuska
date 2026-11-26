# SOSkúška bright UI redesign plan

This is an internal implementation plan for the native Python/CustomTkinter app. The goal is to make the redesign visible in a semester presentation and help students identify their next action with less searching. The original Light theme used white cards and purple accents; Step 1 replaces the shared palette. The main visual change is a new dashboard layout, followed by clearer Practice Test and Flashcard review screens.

## New direction · 26 November 2026

The user requested substantially larger visual changes after finding the earlier result too incremental. The [study-studio Dashboard handoff](design/study-studio-dashboard/README.md) supersedes the next-step prompt below for design work. **Update:** the [cat brand redesign](design/cat-brand/README.md), released in v0.29.0, now defines the palette, logo and shell; use it as the current visual direction. Stage 1 replaces the Dashboard/navigation/shared palette with a working native preview. The user approved stage 1 for release in v0.27.0; remaining page compositions need their own implementation request. The Steps 1–5 records below remain historical; automated coverage is not visual approval.

## Session handoff

Read the plan from the documentation PR or from `main` once merged. Start implementation on a feature branch from current `main` and follow the repository's [development workflow](WORKFLOW.md). Read the [runtime](RUNTIME.md) and [study](STUDY.md) instructions before touching the corresponding screens. Use one step per agent session by default. Each step should leave the application runnable and end with a focused check and a commit on its implementation branch. Record the commit, checks run, any unchecked items, and next step in the session handoff or PR. When the next agent starts, have it inspect the branch and continue from the first incomplete step. Open a separate implementation PR for each independently reviewable milestone, or keep related steps on one PR when they depend on each other. Follow the repository's review and merge workflow.

Suggested first prompt for the next session:

> Read `docs/agents/BRIGHT_UI_REDESIGN.md` and the repository guidance. Inspect the implementation handoffs and branch first. After the Step 5 Settings/data portion is merged, continue with Step 6 regression checks and teacher demo only with disposable data and focused checks.

## Design direction

- Use a warm off-white workspace, white reading surfaces, deep navy text, a saturated blue for the primary action, and pale blue and mint for selected surfaces or progress. Reserve amber for deadlines and warnings and red for errors and destructive actions. Verify contrast when choosing final values. Carry the hierarchy into Dark mode with the existing paired colors.
- Make the primary action visually strongest. Use clear page titles, quieter secondary actions, and consistent spacing. Use text together with color for progress, warnings, results and selections.
- Work within `soskuska/`. The earlier `soskuska-local/` HTML is a visual reference. Preserve the saved Light/Dark/System choice, existing defaults, offline behavior, translations, and SQLite schema. Keep timers, navigation, drafts, history, scoring, scheduling, and CSV/backup workflows working through their existing entry points.

## Step 1 — Theme foundation

**Files:** `soskuska/theme.py`, shared style helpers in `soskuska/app.py`, and focused appearance checks if needed.

1. Capture baseline Dashboard, active Practice Test and Flashcard review screenshots in Light mode at 1440 × 900 using a disposable database with a subject, exam date, practice questions and a due deck. Reuse the same fixture for the final screenshots. Sketch the Dashboard and Practice Test with their primary actions in place.
2. Update paired theme colors and reuse the existing `font`, `label`, `frame` and `button` helpers for the few shared visual roles the new layouts need. Check primary and secondary buttons, selected items, placeholders, warnings and disabled states. Leave layout changes for later steps.
3. Run `tests/test_appearance.py` and `soskuska/check_appearance.py` through the appropriate test environment. Confirm that applying Light, Dark and System through the existing Save flow keeps active widgets and drafts intact. End the session once the palette and shared styles pass the focused checks.

### Step 1 handoff · 25 November 2026

Theme foundation merged through [PR #43](https://github.com/turcinv/SOSkuska/pull/43), commit `60a8082`. See [captures, sketches, reproduction commands and validation](design/bright-ui-step1/README.md). Shared palette and secondary hover role are applied; Statistics progress tracks reuse the shared surface. Light/Dark captures use the same disposable fixture. Local validation: 308 unit tests (two platform skips), 18 GUI scripts and 12 focused appearance tests passed; independent Sol medium re-review found no blockers. Published version remains v0.18.1, schema 10. Native platform/scaling checks are not claimed. Continue with **Step 2**, not the whole plan; repeat acceptance after layout work before v1.0.0.

## Step 2 — Dashboard and sidebar

**Files:** `soskuska/app.py`, `soskuska/check_dashboard.py`, and the localization catalogs if labels change.

1. Replace the greeting-led layout with a **Today's Study** panel that groups the subject picker, Start Studying action, timer controls, and daily-goal progress. Keep recovery and save-retry actions visible when needed. Keep the checklist accessible in the same section.
2. Put **My Subjects** and its search directly below Today's Study. Place upcoming exams and recent sessions beside the main column at the wide size and stack them below it at the minimum size. Move lifetime metrics into a compact summary. Give the sidebar a clear selected state and preserve collapse and navigation behavior.
3. Run `check_dashboard.py` and `check_focus_recovery.py`. Verify empty and populated dashboards, long subject names, sidebar collapse, recovery and the start/pause/resume/finish flow at 1440 × 900 and 1024 × 700. Check that a new user can find the first action if the database has no subjects. End after the dashboard is ready to show by itself.

### Step 2 handoff · 25 November 2026

Dashboard/sidebar merged through [PR #44](https://github.com/turcinv/SOSkuska/pull/44), commit `9ecc5dd`; both Steps 1–2 ship in v0.19.0. See [screenshots, validation, reproduction and next-session scope](design/bright-ui-step2/README.md). The study panel, subject/search ordering, compact summary and sidebar selection are in place. Width/wrapping now use logical viewport dimensions; four-language checks cover 100/150% startup scaling, long selected names and recovery/retry controls. Local full suite: 308 unit tests (two platform skips), all 18 GUI scripts passed. Sol medium re-review found no remaining blockers. Release labels align to v0.19.0/schema 10; native hardware/live-DPI claims are excluded. Continue with **Step 3 only** when requested.

## Step 3 — Practice Tests

**Files:** `soskuska/practice_page.py`, focused practice GUI checks, and localization catalogs if needed.

1. Give the running test a dedicated progress and timer header, full-width A–D answer rows, a clear selected state, and consistent Previous, Next and Finish positions. Allow long prompts and answers to wrap and remain scrollable at the minimum size.
2. Style setup, result and history with the same hierarchy. Maintain the visibility rules for correct answers, existing confirmations, deadline behavior, and resume/history paths.
3. Run `check_practice.py` and `check_practice_history.py`. Verify timed and untimed runs, selected answers after navigation or resume, and opening a completed result. End once the flow works from setup through review.

### Step 3 handoff · 25 November 2026

Practice redesign merged through [PR #46](https://github.com/turcinv/SOSkuska/pull/46), commit `a5bc578`, and released in v0.20.0. See [captures, reproduction, review and validation](design/bright-ui-step3/README.md). Progress/timer header, saved-choice row selection, common footer, grouped setup and result/history hierarchy are in place. Hidden row/label/radio events cannot save answers; failed writes restore the last saved choice and styling. Local validation: 308 unit tests (two platform skips), all 18 GUI scripts and 28 focused practice/history unit tests passed; Sol medium re-review found no blockers. All four languages at 100/150% startup scaling cover long content, rollback, hidden events, footer access and results. Release labels align to v0.20.0/schema 10. Continue with **Step 4 only** when requested.

## Step 4 — Flashcard review

**Files:** `soskuska/flashcard_page.py` and focused flashcard GUI checks.

1. Give prompt and revealed answer a spacious reading surface. Make Reveal the primary action before the answer appears, then show the existing rating choices in a consistent order and location. Keep long content scrollable and the rating actions reachable.
2. Align deck and card lists, editing controls, and empty states with the shared styles. Preserve the reveal-before-rating rule, review history and import preview state.
3. Run `check_flashcards.py` and `check_flashcard_import.py`. Verify reveal and rating, a deck with no due cards, and long text at compact size. If time is short, proceed to Step 6 for the teacher demo and schedule Step 5 later.

### Step 4 handoff · 25 November 2026

Flashcard review merged through [PR #48](https://github.com/turcinv/SOSkuska/pull/48), commit `0b370d0`, and ships in v0.21.0; see [captures, validation and next-session scope](design/bright-ui-step4/README.md). Prompt/answer reading surfaces, guarded Reveal/rating footer, responsive rating grid, deck actions and empty states are aligned. Failed-write feedback stays by the footer; a committed rating with failed next-card read disables old ratings and retries reads only. Scheduling, schema 10, immutable history and CSV/editor paths remain. Release labels align to v0.21.0/schema 10. All five feature PR CI jobs passed. Continue with the **Subjects and Question Bank portion of Step 5 only** after this step is merged and requested.

## Step 5 — Consistency pass

Split this into as many sessions as needed. In one session, align **Subjects and Question Bank**. In another, align **Statistics and AI Tutor**, then handle **Settings and shared backup/import panels** in a separate session if needed. Apply the shared style to typography, spacing, forms, statuses and empty states. Keep editors and in-progress operations intact. Run the existing GUI check for each touched screen, including its import, draft or streaming checks where relevant. Update English, Czech, Slovak and Russian catalogs together if text changes, and keep affected user guides aligned if screen navigation or documented behavior changes.

### Step 5 authoring handoff · 25 November 2026

Subjects and Question Bank merged through [PR #50](https://github.com/turcinv/SOSkuska/pull/50), commit `1bf6763`, and ship in v0.22.0; see [captures, validation and continuation scope](design/bright-ui-step5-authoring/README.md). Header/search/filter cards, two-row subject actions, responsive answer fields, readable authoring previews and empty states use shared styles. Resizing repositions existing subject cards without SQL reads; logical-unit wrapping and breakpoints preserve compact/scaled layouts. Existing editor widgets, snapshots, filters, topic identity, pagination and import paths remain. Release labels align to v0.22.0/schema 10. All five feature CI jobs passed; the bounded suite includes 19 GUI scripts. Continue only when requested with the **Statistics and AI Tutor portion of Step 5**, leaving Settings/data panels for another session.

### Step 5 Statistics/Tutor handoff · 25 November 2026

Statistics and AI Tutor merged through [PR #52](https://github.com/turcinv/SOSkuska/pull/52), commit `532d13a`, and ship in v0.23.0; see [captures, validation and continuation](design/bright-ui-step5-reports/README.md). Statistics groups period controls and responsive summary cards; Tutor groups connection/history and conversation/composer surfaces, with full-width model selection and recovery feedback beside its controls. Stable parent widths avoid uniform-column rounding loops. Existing calculations, snapshots, drafts, context ownership, streaming, Stop and persistence behavior remain. New four-language 100/150% startup layout/state probes run as a separate bounded GUI script. Release labels align to v0.23.0/schema 10. All five feature CI jobs passed; local validation passed 308 unit tests (two platform skips) and 20 GUI scripts. Next only when requested after merge: **Settings and shared backup/import panels**, then Step 6 acceptance/demo.

### Step 5 Settings/data handoff · 25 November 2026

Settings and shared data panels merged through [PR #54](https://github.com/turcinv/SOSkuska/pull/54), commit `c6d094a`, and ship in v0.24.0; see [captures, validation and continuation](design/bright-ui-step5-settings/README.md). Grouped Settings cards and mirrored save/reload feedback, shared backup/schedule/CSV surfaces, responsive action groups and visible restore warnings complete the implementation scope of Step 5. `panel_layout.py` contains only widget-local logical wrapping and guarded action reflow. Existing drafts, snapshots, previews, workers, timers and atomic data-transfer operations remain. Release labels align to v0.24.0/schema 10. All five feature CI jobs passed; local validation passed 308 unit tests (two platform skips) and 21 GUI scripts. Next after merge and user request: **Step 6 regression, platform acceptance and teacher demo**, with recorded evidence rather than assumed manual results.

## Step 6 — Regression checks and teacher demo

- Use disposable data for the container checks described in [Container tests](../CONTAINER_TESTS.md). Run the full suite after the screen work. Check Light, Dark and System, the four UI languages, contrast, keyboard navigation, and text wrapping and scrolling at 1440 × 900 and 1024 × 700. Record any manual Windows scaling results separately from automated checks, following [Windows acceptance](../WINDOWS_ACCEPTANCE.md).
- Capture matching before/after screenshots of Dashboard, active Practice Test and Flashcard review. In the live demo, select a subject, start a focus session, answer a practice question, and reveal and rate a flashcard. Use the new Light mode and the disposable dataset.
- If someone unfamiliar with SOSkúška is available, ask them to start a focus session and answer a practice question without hints. Record whether they found the right control on the first try and where they hesitated. Describe the design intent and any observed results separately in the presentation.
