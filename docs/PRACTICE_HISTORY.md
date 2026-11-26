# Practice history

[English](PRACTICE_HISTORY.md) · [Čeština](cs/PRACTICE_HISTORY.md) · [Slovenčina](sk/PRACTICE_HISTORY.md) · [Русский](ru/PRACTICE_HISTORY.md)

**v0.20.0 — Practice redesign Step 3:** Running tests now group progress/timing in a header and show a bar of saved answers. Full-width A–D rows highlight the saved choice, not correctness; background/text clicks save through the existing answer path. Previous/Next/Clear and Finish share a footer. Setup selectors share a card, and results/history use matching surfaces. Failed saves restore selection/style; hidden setup or off-page answer callbacks do not write. Long content wraps and scrolls at compact size. Scoring, deadlines, confirmations, resume, filters and retained snapshots remain unchanged; current schema is 10.

Open **Practice Tests → Completed tests**. History now shows all retained completed attempts in pages of 20, newest completion first, with attempt ID as the tie-breaker. Use Previous / Next to browse, and View result to reopen the saved score, selected/correct answers and explanations. Returning to setup/history keeps the page and filters.

If a test is unfinished, choose **← Test setup / history** from the running test to reach this view; Resume test returns to that attempt.

Select a **Subject name saved with the test**, optionally fill Completed from / Completed through in strict `YYYY-MM-DD` format, then choose Apply filters (Enter in either date field also applies). Blank bounds are unlimited. Dates include the whole local calendar day at both ends, based on the saved completion timestamp. Changing the system time zone can move an attempt to another date. Reset filters clears both dates and the subject; applying or resetting starts on page 1. Invalid dates or reversed ranges keep the previous results and applied filters.

Names come from completed snapshots, including deleted subjects. Renaming creates a separate historical name when later attempts use the new name. Identical saved names are grouped, including a deleted and recreated subject with the same name; this filter is by saved name, not current subject ID. User names/content are never translated. Tests that are unfinished or discarded do not appear here.

Editing filter controls creates a draft until Apply. Moving pages or leaving/returning to the screen keeps drafts while paging the previously applied filters. Filters and page are retained within this app session, not saved across restart. A read error keeps the previous cards, filters and page; retry the same action. Counts, names and rows are read in one SQLite snapshot. A page is clamped if the number of results changes; separate page requests refresh their snapshot, so concurrent completions can move rows between pages.

Results remain immutable snapshots of the test’s original questions/options, correct answers, explanations and subject name. Source edits/deletions do not rewrite them. Opening history does not answer or complete an unfinished test; its existing timer still runs and deadline completion can take precedence as before. No schema change, network connection or new dependency is required; this history feature was introduced at schema 8, and the current database schema is 10.

Developer checks: `tests/test_practice_history.py` and `soskuska/check_practice_history.py` use disposable databases. The GUI check covers older results, filters, errors/retries, drafts/navigation, active-attempt isolation, compact scrolling and a fresh process. Automated checks do not establish manual Windows UI or physical trackpad verification.


## Question explanations · v0.25.0

Completed Practice results, including reopened history, offer **Explain this question**. Open the local preview, then choose **Prepare in Tutor**. It uses the saved question snapshot (all four choices, selected answer or Unanswered, stored answer key and explanation), even after the original question/subject is deleted. Nothing connects or sends during preview/preparation. In Tutor, review the server, model and answer language, explicitly Connect if needed, then Send. The draft is editable and uses ordinary local chat history, Stop and save-retry paths.

Tutor must be an idle, clean New chat with an empty prompt and no pending confirmation or unsaved reply. Existing work is preserved; finish it or explicitly use the confirmed New chat action before retrying. A complete generated prompt above 4,000 characters is rejected with its measured length; nothing is truncated. The saved answer key and AI explanation may be wrong; scores and source content never change. Automatic asks for the supplied question language; explicit answer language overrides it. Prompt instructions stay in English and user content stays unchanged. No schema change (10), released version is v0.30.1.

Implementation: `question_explanation.py` builds/validates the bounded snapshot prompt; `practice_page.py` owns preview and stale-result checks; `tutor_page.py` guards draft insertion. Existing Send persists the prompt before HTTP. Automated checks use disposable data and loopback FakeOllama; real-model quality and native platform/DPI acceptance remain manual.


## AI study modes · v0.26.0

In a completed result, open **Explain this question**, then choose **Study mode** before **Prepare in Tutor**. **Explain answer** keeps the existing explanation; **Explain simply** requests short beginner-friendly steps and an example; **Give me a hint** requests one conceptual hint and omits your selected answer, stored key and explanation from the prompt; **Quiz me** asks one new follow-up at a time, waiting for your response before feedback. This is informal practice and never writes a scored attempt or changes source content.

Changing mode regenerates the exact local preview and invalidates its previous Prepare action. Nothing connects, sends or creates a conversation until the existing explicit controls are used. The sent prompt is saved in ordinary local chat history, with the existing language, 4,000-character bound, clean-chat guard, Stop and save-retry rules. Hint mode still includes all four choices: a model may infer/reveal the answer, and text already visible in completed results remains visible. Mode following and explanation quality require later real-model testing, explicitly deferred by the user. Automated checks use loopback FakeOllama. Released version is v0.30.1 / schema 10.
