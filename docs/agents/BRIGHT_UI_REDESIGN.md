# SOSkúška bright UI redesign plan

This is an internal implementation plan for the native Python/CustomTkinter app. The goal is to make the redesign visible in a semester presentation and help students identify their next action with less searching. The existing Light theme already uses white cards and purple accents. The main visual change is a new dashboard layout, followed by clearer Practice Test and Flashcard review screens.

## Session handoff

Read the plan from the documentation PR or from `main` once merged. Start implementation on a feature branch from current `main` and follow the repository's [development workflow](WORKFLOW.md). Read the [runtime](RUNTIME.md) and [study](STUDY.md) instructions before touching the corresponding screens. Use one step per agent session by default. Each step should leave the application runnable and end with a focused check and a commit on its implementation branch. Record the commit, checks run, any unchecked items, and next step in the session handoff or PR. When the next agent starts, have it inspect the branch and continue from the first incomplete step. Open a separate implementation PR for each independently reviewable milestone, or keep related steps on one PR when they depend on each other. Follow the repository's review and merge workflow.

Suggested first prompt for the next session:

> Read `docs/agents/BRIGHT_UI_REDESIGN.md` and the repository guidance. Implement Step 1 only. Use disposable data, run its focused checks, and report what is ready for Step 2.

## Design direction

- Use a warm off-white workspace, white reading surfaces, deep navy text, a saturated blue for the primary action, and pale blue and mint for selected surfaces or progress. Reserve amber for deadlines and warnings and red for errors and destructive actions. Verify contrast when choosing final values. Carry the hierarchy into Dark mode with the existing paired colors.
- Make the primary action visually strongest. Use clear page titles, quieter secondary actions, and consistent spacing. Use text together with color for progress, warnings, results and selections.
- Work within `soskuska/`. The earlier `soskuska-local/` HTML is a visual reference. Preserve the saved Light/Dark/System choice, existing defaults, offline behavior, translations, and SQLite schema. Keep timers, navigation, drafts, history, scoring, scheduling, and CSV/backup workflows working through their existing entry points.

## Step 1 — Theme foundation

**Files:** `soskuska/theme.py`, shared style helpers in `soskuska/app.py`, and focused appearance checks if needed.

1. Capture baseline Dashboard, active Practice Test and Flashcard review screenshots in Light mode at 1440 × 900 using a disposable database with a subject, exam date, practice questions and a due deck. Reuse the same fixture for the final screenshots. Sketch the Dashboard and Practice Test with their primary actions in place.
2. Update paired theme colors and reuse the existing `font`, `label`, `frame` and `button` helpers for the few shared visual roles the new layouts need. Check primary and secondary buttons, selected items, placeholders, warnings and disabled states. Leave layout changes for later steps.
3. Run `tests/test_appearance.py` and `soskuska/check_appearance.py` through the appropriate test environment. Confirm that applying Light, Dark and System through the existing Save flow keeps active widgets and drafts intact. End the session once the palette and shared styles pass the focused checks.

## Step 2 — Dashboard and sidebar

**Files:** `soskuska/app.py`, `soskuska/check_dashboard.py`, and the localization catalogs if labels change.

1. Replace the greeting-led layout with a **Today's Study** panel that groups the subject picker, Start Studying action, timer controls, and daily-goal progress. Keep recovery and save-retry actions visible when needed. Keep the checklist accessible in the same section.
2. Put **My Subjects** and its search directly below Today's Study. Place upcoming exams and recent sessions beside the main column at the wide size and stack them below it at the minimum size. Move lifetime metrics into a compact summary. Give the sidebar a clear selected state and preserve collapse and navigation behavior.
3. Run `check_dashboard.py` and `check_focus_recovery.py`. Verify empty and populated dashboards, long subject names, sidebar collapse, recovery and the start/pause/resume/finish flow at 1440 × 900 and 1024 × 700. Check that a new user can find the first action if the database has no subjects. End after the dashboard is ready to show by itself.

## Step 3 — Practice Tests

**Files:** `soskuska/practice_page.py`, focused practice GUI checks, and localization catalogs if needed.

1. Give the running test a dedicated progress and timer header, full-width A–D answer rows, a clear selected state, and consistent Previous, Next and Finish positions. Allow long prompts and answers to wrap and remain scrollable at the minimum size.
2. Style setup, result and history with the same hierarchy. Maintain the visibility rules for correct answers, existing confirmations, deadline behavior, and resume/history paths.
3. Run `check_practice.py` and `check_practice_history.py`. Verify timed and untimed runs, selected answers after navigation or resume, and opening a completed result. End once the flow works from setup through review.

## Step 4 — Flashcard review

**Files:** `soskuska/flashcard_page.py` and focused flashcard GUI checks.

1. Give prompt and revealed answer a spacious reading surface. Make Reveal the primary action before the answer appears, then show the existing rating choices in a consistent order and location. Keep long content scrollable and the rating actions reachable.
2. Align deck and card lists, editing controls, and empty states with the shared styles. Preserve the reveal-before-rating rule, review history and import preview state.
3. Run `check_flashcards.py` and `check_flashcard_import.py`. Verify reveal and rating, a deck with no due cards, and long text at compact size. If time is short, proceed to Step 6 for the teacher demo and schedule Step 5 later.

## Step 5 — Consistency pass

Split this into as many sessions as needed. In one session, align **Subjects and Question Bank**. In another, align **Statistics and AI Tutor**, then handle **Settings and shared backup/import panels** in a separate session if needed. Apply the shared style to typography, spacing, forms, statuses and empty states. Keep editors and in-progress operations intact. Run the existing GUI check for each touched screen, including its import, draft or streaming checks where relevant. Update English, Czech, Slovak and Russian catalogs together if text changes, and keep affected user guides aligned if screen navigation or documented behavior changes.

## Step 6 — Regression checks and teacher demo

- Use disposable data for the container checks described in [Container tests](../CONTAINER_TESTS.md). Run the full suite after the screen work. Check Light, Dark and System, the four UI languages, contrast, keyboard navigation, and text wrapping and scrolling at 1440 × 900 and 1024 × 700. Record any manual Windows scaling results separately from automated checks, following [Windows acceptance](../WINDOWS_ACCEPTANCE.md).
- Capture matching before/after screenshots of Dashboard, active Practice Test and Flashcard review. In the live demo, select a subject, start a focus session, answer a practice question, and reveal and rate a flashcard. Use the new Light mode and the disposable dataset.
- If someone unfamiliar with SOSkúška is available, ask them to start a focus session and answer a practice question without hints. Record whether they found the right control on the first try and where they hesitated. Describe the design intent and any observed results separately in the presentation.
