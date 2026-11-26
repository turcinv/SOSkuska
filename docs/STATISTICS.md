# Statistics (introduced in v0.6.0)

[English](STATISTICS.md) · [Čeština](cs/STATISTICS.md) · [Slovenčina](sk/STATISTICS.md) · [Русский](ru/STATISTICS.md)

## v0.23.0 — Statistics and AI Tutor design

Statistics groups the period selector and Refresh in a header, with three summary cards side by side on wide screens or stacked in compact windows. Subject and daily activity remain below, with readable wrapped labels. Resizing preserves the existing report and does not query the database; failed Refresh keeps the prior snapshot. Definitions, weighted accuracy and self-rating counts are unchanged.

Select Last 7 days, Last 30 days or All time. Statistics shows saved focus time/sessions, question-weighted accuracy for completed practice tests, flashcard self-rating counts, subject time and daily activity. Refresh or reopening loads a new snapshot. These numbers do not measure mastery.

## What the numbers mean

- **Focus:** saved nonzero sessions only; running/unsaved time is excluded. Study days have saved focus time.
- **Practice Tests:** completed attempts only, grouped by completion date. Accuracy = correct answers / all questions; each question has equal weight and unanswered questions count incorrect. Unfinished/discarded attempts are excluded. No invented percentage appears when no tests are completed.
- **Flashcards:** stored Again / Hard / Good / Easy ratings, including repeated reviews of the same card. These are self-assessments, not accuracy or mastery. Practice and flashcards never add focus time.

## Periods and retained history

The periods include today and the preceding 6 or 29 local calendar days. All time includes everything through today, but the daily chart covers only the latest 30 days. Future calendar days are excluded. Focus sessions use their stored local day; practice/review UTC timestamps convert using the current system time zone. Changing zone may rebucket historical events. A focus session crossing midnight stays entirely on its save day.

Reports include history beyond Flashcards’ 20-row review-history display limit. Deleting a subject, card or deck does not remove retained historical results. Existing subjects group by ID/current name; unavailable subjects group by saved name, and unnamed legacy sessions appear as Unassigned sessions. Deleted subjects with identical names may merge into one row. At most 50 subject groups are displayed by time; totals include all groups. Bars compare rows, not progress toward a goal.

## Implementation and limits

`statistics_page.py` renders the report; `study_statistics.py` runs queries through `Store.statistics()`. Four aggregates share one read transaction. The feature introduced no schema change (schema 5 at v0.6.0; current schema is 10) or new dependencies and does not write data. Refresh is manual or on reopening, without a background timer. Read failures keep the previous report with a retry notice; it may be stale.

Export, custom date ranges, subject filters and advanced charts remain future work. AI Tutor provides separate optional chat with local history through Ollama.
