# Practice history

[English](PRACTICE_HISTORY.md) · [Čeština](cs/PRACTICE_HISTORY.md) · [Slovenčina](sk/PRACTICE_HISTORY.md) · [Русский](ru/PRACTICE_HISTORY.md)

Open **Practice Tests → Completed tests**. History now shows all retained completed attempts in pages of 20, newest completion first, with attempt ID as the tie-breaker. Use Previous / Next to browse, and View result to reopen the saved score, selected/correct answers and explanations. Returning to setup/history keeps the page and filters.

If a test is unfinished, choose **← Test setup / history** from the running test to reach this view; Resume test returns to that attempt.

Select a **Subject name saved with the test**, optionally fill Completed from / Completed through in strict `YYYY-MM-DD` format, then choose Apply filters (Enter in either date field also applies). Blank bounds are unlimited. Dates include the whole local calendar day at both ends, based on the saved completion timestamp. Changing the system time zone can move an attempt to another date. Reset filters clears both dates and the subject; applying or resetting starts on page 1. Invalid dates or reversed ranges keep the previous results and applied filters.

Names come from completed snapshots, including deleted subjects. Renaming creates a separate historical name when later attempts use the new name. Identical saved names are grouped, including a deleted and recreated subject with the same name; this filter is by saved name, not current subject ID. User names/content are never translated. Tests that are unfinished or discarded do not appear here.

Editing filter controls creates a draft until Apply. Moving pages or leaving/returning to the screen keeps drafts while paging the previously applied filters. Filters and page are retained within this app session, not saved across restart. A read error keeps the previous cards, filters and page; retry the same action. Counts, names and rows are read in one SQLite snapshot. A page is clamped if the number of results changes; separate page requests refresh their snapshot, so concurrent completions can move rows between pages.

Results remain immutable snapshots of the test’s original questions/options, correct answers, explanations and subject name. Source edits/deletions do not rewrite them. Opening history does not answer or complete an unfinished test; its existing timer still runs and deadline completion can take precedence as before. No schema change, network connection or new dependency is required; the schema remains 8.

Developer checks: `tests/test_practice_history.py` and `soskuska/check_practice_history.py` use disposable databases. The GUI check covers older results, filters, errors/retries, drafts/navigation, active-attempt isolation, compact scrolling and a fresh process. Automated checks do not establish manual Windows UI or physical trackpad verification.
