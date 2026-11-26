# Study studio · substantial redesign, stage 1

26 November 2026 · `feature/study-studio-redesign` · unpublished preview based on v0.26.1 (`5405461586ee9deebb3a96c42df564b5be743d8e`). App/release labels remain unchanged until release authorization.

The user explicitly rejected the earlier incremental bright UI work as too small. This stage replaces the Dashboard composition, navigation treatment and shared visual system. It is a working native Python/CustomTkinter implementation. Visual feedback on this stage comes before extending the remaining page compositions. The old bright UI handoffs remain historical evidence.

## Visual direction and scope

Graphite and violet in Dark; warm neutral workspace with a lavender focus surface in Light. A persistent dark sidebar has locally drawn line icons and a compact brand tile. The header uses an editorial title; four separate summary tiles move above a large focus room. A circular clock displays the actual configured/remaining time and elapsed fraction of the original focus target. Saved subject data becomes monogram-led library cards. A month agenda uses all saved subject exam dates, while the upcoming list retains its top-five limit and exact saved dates. Actual saved sessions and goal progress remain the source of metrics; new user databases still start empty.

Global colors and borderless card surfaces apply across existing screens. The other pages retain their current composition in this stage. Their full redesign is follow-up work after visual feedback, not something claimed complete here. SQLite schema remains 10; store writes, focus ownership/checkpoint/retry semantics, history and optional Ollama remain through the established paths.

## Before and after

All captures use the same disposable fixture and frozen 25 November date, never the normal database. The displayed clock target is the fixture's saved 15-minute preference. These are Linux/Xvfb screenshots, not native Mac/Windows acceptance.

| View | Evidence |
| --- | --- |
| Released Dashboard, Dark 1440×900 | [Before](before-dark.png) · [metadata](before.json) |
| Redesigned Dashboard, Dark 1440×900 | [After](dark-wide.png) · [metadata](dark-wide.json) |
| Redesigned Dashboard, Light 1440×900 | [Light](light-wide.png) · [metadata](light-wide.json) |
| Redesigned Dashboard, Dark 1024×700 | [Compact](dark-compact.png) · [metadata](dark-compact.json) |

## Implementation and interaction

- `app.py` owns the revised shell and Dashboard composition; widgets and callbacks stay connected to existing study behavior. Focus target changes apply to the next session, and Finish resets the idle clock to the saved preference.
- `studio_widgets.py` owns line-icon drawing, the paired-color clock and calendar. It performs no database/network work. Clock arcs redraw only when the integer elapsed percentage changes; all Tk access stays on the UI thread.
- `theme.py` owns the new paired palette, including separate always-dark navigation roles and readable focus/track colors. Appearance Save updates existing widgets/images.
- `scrolling.py` converts descendant positions to absolute canvas coordinates. Search and recovery/Finish controls reveal from any scroll position. Scheduled recovery reveals are cancelled by navigation or explicit search, so hidden work cannot move another page.
- Responsive reflow repositions the existing controls and converts native widths to logical CTk units. It performs no database reads. Compact layouts remain scrollable, with the primary study action first and keyboard search revealed on demand.

## Verification and reproduction

`check_studio_layout.py` covers four interface languages at 100/150% startup scaling, all saved calendar marks (including beyond the top-five rail), month rollover, exact exam dates, maximum focus duration, pause/progress, applying Light and next-session duration, Ctrl+K from both ends, stable already-visible Search, save failure/retry and cancelled hidden/recovery reveals. Contrast regressions cover navigation/focus text, arcs and checkbox outlines. Independent Sol medium review findings were fixed and rechecked. Full-suite/hosted results are recorded in the PR.

From the repository root, build the test image and run the shared checks:

```sh
docker build -f Dockerfile.tests -t soskuska-study-studio .
docker run --rm --init --network none --cpus 2 --memory 2g soskuska-study-studio
```

To reproduce a disposable capture, pass `tools/capture_redesign.py` on stdin to that image with Xvfb and `--dashboard-only --mode Dark --size wide --output /tmp/capture`. Use a named container and `docker cp` to collect `/tmp/capture`; do not mount a host display or normal data folder. Light and compact captures change only the mode/size options.

## Next

Review the screenshots with the user, then carry the approved design language into Subjects/Question Bank, Flashcards, Practice, Tutor, Statistics and Settings through separately reviewable steps. Do not treat automated checks as visual approval or manual hardware acceptance. Real-model evaluation remains deferred. Merge/release require separate authorization.
