# Cat brand redesign

26 November 2026 · `feature/cat-brand-redesign` · unreleased. Source: the user's "SOSkúška brand & app concept" board (logo, mascot, palette/UI elements, desktop mockup). Native Python/CustomTkinter implementation; no web runtime.

## What changed

- **Logo.** `tools/build_brand_assets.py` now renders a charcoal cat reading a pale-violet book on a lavender-to-charcoal rounded square (pure Pillow, supersampled), with a matching `logo.svg`. All PNG/ICO/ICNS sizes are regenerated; packaging paths are unchanged.
- **Palette.** `theme.py` uses the board's Charcoal `#2B2A34`, Lavender `#9884D6`, Violet `#C9B6F2` and Cream `#F6F3FA`. Filled buttons use a deeper lavender (`#6E5ABF`, selected navigation `#7A66C7`) so white labels keep ≥ 4.5:1 contrast; the brand lavender is the new `outline` role for secondary buttons, search and the Add subject card.
- **Shared controls.** Buttons are pills (radius 18 at 38 px height) with lavender outlines; cards use radius 16. Every page inherits this through the existing `app.button`/`app.frame` helpers and paired roles.
- **Sidebar.** Always-charcoal, serif wordmark, filled lavender selected item, and a locally drawn tail/paw decoration in the flexible row (it shrinks first at 700 px height and hides when collapsed).
- **Dashboard.** Greeting header with paw mark and cat avatar (decorative; no profile data); summary tiles with drawn icons; a "Continue studying" banner showing the selected or active saved subject, with an illustrated cat-in-window scene that fades into the focus surface. The scene appears only in the wide layout so compact windows keep the study controls near the top. An outlined **Add subject** card follows real subject cards (hidden during a search) and opens an empty subject form without replacing an open draft.

Intentionally not copied from the mockup: per-subject percentage bars and "practice test average"/"sessions this week" tiles, because the existing cards show only real stored data and must not invent mastery. Metrics remain the four existing real values.

## Evidence

Disposable fixture, frozen 25 November date, Linux/Xvfb captures (not native macOS/Windows acceptance):

| View | Capture |
| --- | --- |
| Dashboard Dark 1440×900 | [dark-wide.png](dark-wide.png) · [metadata](dark-wide.json) |
| Dashboard Light 1440×900 | [light-wide.png](light-wide.png) · [metadata](light-wide.json) |
| Dashboard Light 1024×700 | [light-compact.png](light-compact.png) · [metadata](light-compact.json) |
| Flashcard revealed, Light | [flashcard-light.png](flashcard-light.png) |
| Practice running, Dark | [practice-dark.png](practice-dark.png) |
| Logo 256 px | [logo-256.png](logo-256.png) |

`check_studio_layout.py` adds compact-scene, banner subject, Add subject visibility/search and draft-preservation assertions; `check_ui_languages.py` checks the translated banner title and subject in four languages at 100/150% startup scaling. Palette contrast is covered by `tests/test_appearance.py` and the live `check_appearance.py` audit.

Reproduce captures as in the [study-studio handoff](../study-studio-dashboard/README.md) with `tools/capture_redesign.py --dashboard-only`.
