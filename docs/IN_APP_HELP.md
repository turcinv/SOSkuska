# In-app Help

[English](IN_APP_HELP.md) · [Čeština](cs/IN_APP_HELP.md) · [Slovenčina](sk/IN_APP_HELP.md) · [Русский](ru/IN_APP_HELP.md)

SOSkúška has a built-in Help page with short guides to every part of the app. It works offline, sends nothing and never changes your data.

## Open Help

- Select the **?** button next to **Settings** at the bottom of the sidebar. In a collapsed sidebar it sits below the Settings icon.
- Press **F1** on any page. On a Mac, **Cmd+?** works too.

Help opens on the topic for the page you were using: for example, opening it from Flashcards shows *Flashcards and review*, and from a question bank shows *Question bank*. Opening Help again while you are already reading it keeps your place.

## Use it

- Pick a topic from the list. In wide windows the list sits beside the article; in smaller windows it is above it.
- Type in **Search help…** to narrow the list. Search ignores capital letters and accents (`nastaveni` finds *Nastavení*), and every word you type must appear in the topic. **Ctrl+K** (Cmd+K on a Mac) jumps to the search field, and **Esc** clears it.
- Names of buttons and fields appear in quotation marks, exactly as they are labelled in your interface language.
- **Open …** at the end of a topic goes to the page it describes; **See also** links to related topics.

**← Back to …** at the top returns to the page you came from exactly as you left it, at the same scroll position. Unsaved drafts are kept, and so are a CSV import preview and a chosen backup when you come back this way; switching to a different page from Help cancels those as usual.

## Topics

Getting started · Dashboard and focus sessions · Subjects and exam dates · Question bank · Practice tests · Flashcards and review · Statistics · AI Tutor · AI drafts from notes · Importing from CSV · Settings and language · Backups and restore · Your data and privacy · Keyboard shortcuts · Troubleshooting.

Help follows the interface language chosen in Settings (English, Czech, Slovak or Russian) after restart. The guides in this `docs/` folder remain the detailed reference.

## For developers

Topics live in `soskuska/i18n/help-<en|cs|sk|ru>.json`. `help_content.py` validates them, folds text for search and maps pages to topics; `help_page.py` renders them and is built on first use so startup is not slowed. Each topic has an `id`, `title`, `summary`, optional `page` to open, `blocks` (`heading`, `text`, `steps` or `bullets`) and `related` topic ids. Mark literal UI labels as `**Label**`.

`tests/test_help.py` requires all four files to have the same structure, every `**Label**` to be a real label in that language's UI catalog, and validates search; `check_help.py` covers the page in four languages and at 150%. Update all four files together when a feature or label changes.
