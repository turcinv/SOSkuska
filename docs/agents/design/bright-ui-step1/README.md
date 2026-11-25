# Bright UI Step 1 evidence and handoff

Internal design evidence, captured **25 November 2026** on `feature/bright-ui-theme`. Implements only [Step 1](../../BRIGHT_UI_REDESIGN.md): shared theme foundation. Dashboard/Practice sketches describe future layouts, not screens implemented by this change. Published version stays v0.18.1; schema stays 10 and the default appearance stays Dark.

## Scope and next session

- Warm off-white Light workspace, white cards, navy text, blue actions/selection and mint progress; paired Dark colors.
- A separate secondary-button hover role avoids using an outline color as the hover fill. Statistics bars now use the same explicit raised track as Dashboard; calculations and layout are untouched.
- Existing font/label/frame/button helpers, dimensions, navigation, settings Save flow and study logic remain in use. No new labels, translation keys, dependency, database migration or network action.
- **Next: Step 2 only**, Dashboard/sidebar. Keep focus recovery/retry controls and drafts intact; use these sketches as a starting point, not as evidence of implemented layout. Repeat release acceptance against the finished redesign before v1.0.0. No merge or release is authorized by this handoff.

## Actual application captures

Each image is **1440 × 900**, Linux/Xvfb, Noto Sans, English, 100% widget/window scale. `capture.json` in each folder records runtime and fixture metadata. These are automated captures, not native Windows/macOS acceptance.

Baseline: `origin/main` commit `9f013eb` before changing the runtime files (same application runtime as v0.18.1). After: this branch's Step 1 source. Both use the fixture in `tools/capture_redesign.py`: 25 November 2026, Computer Science with 15 December exam, two questions, one saved 25-minute session, one active untimed practice with an answer selected, and two due cards. Each run creates and removes its own temporary database; no database is committed. Random sampling/date/time are controlled by the capture utility only. Keep that fixture for Step 6 comparisons.

| Screen | Baseline Light | Step 1 Light | Step 1 Dark |
| --- | --- | --- | --- |
| Dashboard | [Before](before-light/dashboard.png) | [After](after-light/dashboard.png) | [Dark](after-dark/dashboard.png) |
| Active practice | [Before](before-light/practice.png) | [After](after-light/practice.png) | [Dark](after-dark/practice.png) |
| Card before reveal | [Before](before-light/flashcard.png) | [After](after-light/flashcard.png) | [Dark](after-dark/flashcard.png) |
| Card after reveal | [Before](before-light/flashcard-revealed.png) | [After](after-light/flashcard-revealed.png) | [Dark](after-dark/flashcard-revealed.png) |

## Future layout sketches

- [Dashboard SVG](dashboard-sketch.svg) / [PNG](dashboard-sketch.png): Today's Study groups subject/start/timer/goal/checklist; subjects/search follow, with exams and sessions alongside. Recovery/retry actions remain in the study section when needed.
- [Practice SVG](practice-sketch.svg) / [PNG](practice-sketch.png): progress/timer header, answer rows and stable navigation/Finish positions.

These are annotated concepts for Steps 2–3, with illustrative content. They are not screenshot evidence and do not add new runtime states or functionality.

## Reproduce captures without host windows

From the repository root, with Docker already running:

```sh
docker build -f Dockerfile.tests -t soskuska-tests .
docker run --name soskuska-design-capture --init --network none --cpus 2 --memory 2g -i \
  --entrypoint xvfb-run soskuska-tests --auto-servernum \
  --server-args='-screen 0 1920x1080x24' python - --output /tmp/design-capture \
  < tools/capture_redesign.py
mkdir -p .local-data
docker cp soskuska-design-capture:/tmp/design-capture .local-data/design-capture
docker rm soskuska-design-capture
```

The script is intentionally passed through stdin: the test image only copies the shared test runner from `tools/`. No host display or user-data directory is mounted. Use a new container/output name when retaining multiple runs; add `--mode Dark` after the script's output argument for Dark captures. The virtual screen must contain the entire window: the script checks display bounds before cropping and rejects clipped captures. It refuses native macOS/Windows execution. New captures reflect the checked-out runtime, not the historical baseline automatically.

## Validation and limits

- All **308 unit tests** completed, **two platform skips**, and all **18 GUI scripts** passed in the final Linux Docker/Xvfb suite. The focused appearance suite passed all **12 tests**.
- Coverage includes live Light/Dark/System Save, failed/stale saves, retained question/Tutor drafts, active focus/practice state, fresh-process preferences, visible text contrast and progress contrast. Extra semantic checks cover selected navigation/button hover and dark disabled selector/checkbox outlines. Actual progress widgets are audited, not just palette constants.
- Independent Sol review at medium effort: capture bounds and progress/disabled-control feedback addressed; re-review found no remaining blockers.
- Captures and sketches were visually inspected. The full suite also covers compact layouts, scrolling and four UI languages. Simulated System notifications are not real OS/hardware evidence.
- Manual Windows scaling, native macOS trackpad/Quit and real-model checks remain separate. The full redesign and Step 5 consistency pass are not complete. CI results must be checked on the PR; this local record does not predeclare them green.
