# How it works: a simple explanation

[English](HOW_IT_WORKS.md) · [Čeština](cs/HOW_IT_WORKS.md) · [Slovenčina](sk/HOW_IT_WORKS.md) · [Русский](ru/HOW_IT_WORKS.md)

SOSkúška is a desktop app. Python and CustomTkinter create the window; SQLite stores information in a file on your computer. Normal study needs no browser, cloud or running AI. HTML in `soskuska-local/` is a historical design reference.

## Your first subject

1. Open **My Subjects → New subject**.
2. Enter a name, optional description and optional exam date in `YYYY-MM-DD` format.
3. Select **Save subject**. It appears in My Subjects and Dashboard.
4. Use **Edit** to change it. The form rejects empty, oversized or duplicate names and invalid dates.

A new installation is empty: subjects, exam dates and statistics are never invented. Each screen's search filters your own subjects independently.

## Studying and saving

Choose a subject on Dashboard and select **Start Studying**, or use **Study** on a subject card. A configurable timer starts (default 15 minutes); pause/resume as needed. **Finish** saves actual elapsed seconds against that subject. Reaching the target finishes automatically, and normal window close also saves active time.

Dashboard shows saved time, session count, study-day streak and subject count. Settings changes the daily goal (default 60 minutes). Recent activity comes from saved sessions and upcoming exams from your dates. These are not measurements of mastery; test results appear in Practice Tests and summaries in Statistics.

The daily checklist also persists. Mark Review a subject manually; saving nonzero focus time marks Complete a focus session automatically. Reopening on the same day restores the checklist.

## Questions and practice

Use **My Subjects → Questions**. New topic creates an optional topic; New question creates four distinct required answers A–D, exactly one correct choice, Easy/Medium/Hard difficulty and optional explanation. Search combines question text, topic and difficulty. Rename/delete topics using the selected-topic actions; deleting a topic leaves its questions in No topic. Forms keep drafts after validation/write errors. Correct answers are visible here because this is the authoring screen. Import and images are not implemented.

In **Practice Tests**, choose a subject, topic (all / no topic / specific), difficulty and 1–100 available questions. Questions are selected randomly without repetition. Choose Untimed or a 5/10/15/30/60-minute limit.

Each answer and navigation position saves immediately. Use Clear answer, Previous/Next and Resume test as needed. Only one test may be unfinished, and restart does not lose it. Discard test confirms removal of that unfinished attempt. Finish test confirms submission, counts unanswered questions incorrect and shows correct answers/explanations afterward. Deadlines run while away/closed; expired attempts finish during use or on return. Snapshots preserve questions/results through later source edits/deletions. History shows 20 completed tests; older rows remain. Practice does not add invented focus time.

## Flashcards, statistics and AI

- [Flashcards](FLASHCARDS.md): create a deck for a subject, edit cards, Study due, reveal and self-rate Again / Hard / Good / Easy. The app saves next due dates and history. This is custom scheduling, not measured mastery.
- [Statistics](STATISTICS.md): choose Last 7 days, Last 30 days or All time to inspect saved focus time, question-weighted completed-test accuracy, self-rating counts and daily activity. Refresh or reopening gets a new snapshot.
- [AI Tutor](AI_TUTOR.md): explicitly Connect / refresh your Ollama server, choose model/language and Send. Replies stream; Stop cancels. Other screens remain usable without Ollama. Chat is in memory and disappears on closing.
- [Settings](SETTINGS.md): explicitly save the next focus duration, daily goal and AI choices. No automatic connection occurs. Active/paused sessions keep their original duration; only the next session changes. Preferences persist, chat does not.

## Deletion and error recovery

Delete first displays an inline confirmation. Removing a subject removes its exam date/topics/questions, but saved study time/name snapshots remain; the active subject cannot be deleted before finishing. Decks/cards and practice history survive subject deletion. Removing a card/deck retains review history.

Leaving My Subjects cancels pending subject deletion. If another window changes a subject name or content counts, the warning refreshes and needs a second confirmation. Stale question edits preserve drafts instead of overwriting another window's changes. New-deck choices refresh subject names without losing title/description; a deleted selected subject requires an explicit replacement.

Window close and the macOS Quit menu share save/retry behavior. Failed focus writes keep the app open with paused time; retry Finish or Quit. Failed daily reads keep retrying and do not stop the timer; the header changes only after a successful refresh. If time was committed but the report read failed, only the read is retried, avoiding duplicate sessions. Press Finish remains visible while a session is unsaved.

Long text editors contain their own scrolling, including at boundaries and over editor scrollbar/border surfaces. Scroll elsewhere to move the page. Short editors still allow page scrolling.

## Where data lives and current limitations

On macOS, the default is `~/Library/Application Support/SOSkuska/dashboard.sqlite3`; Windows uses `%LOCALAPPDATA%\SOSkuska\dashboard.sqlite3`, Linux uses `$XDG_DATA_HOME/SOSkuska/dashboard.sqlite3` or `~/.local/share/SOSkuska/dashboard.sqlite3`. If no new database exists but legacy `ExamPrep/dashboard.sqlite3` does, the app continues using that file without moving it. Migration preserves records without assigning invented subjects to old sessions. `--data` selects another file.

There is no automatic synchronization, encryption or backup. Focus time is not continuously persisted, so a crash may lose the active session. Sessions crossing midnight belong entirely to their save day. UI translations, saved AI conversations and installers remain future work. See [current architecture](CURRENT_ARCHITECTURE.md) for details.

## Backup and restore

Settings now includes manual local backup and validated restore, with a pre-restore safety copy. Schema stays 6. Restore closes the app; reopen it afterward. See [Backup and restore](BACKUP_RESTORE.md).
