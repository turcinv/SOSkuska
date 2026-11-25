# Import questions from CSV (v0.10.0)

[English](QUESTION_CSV_IMPORT.md) · [Čeština](cs/QUESTION_CSV_IMPORT.md) · [Slovenčina](sk/QUESTION_CSV_IMPORT.md) · [Русский](ru/QUESTION_CSV_IMPORT.md)

## v0.24.0 — Settings and shared data panels

Daily backup schedules, manual backup/restore and both CSV importers now use the shared card style, consistent insets and wrapped messages. Action groups use three columns in wide layouts or two in compact ones. Restore warnings appear above the destructive confirmation and Cancel controls. CSV preview/error fields have visible borders and keep their own scrolling. Preview, cancellation, atomic writes, isolated workers, restore closure and safety-copy rules are unchanged.

The v0.22.0 authoring redesign groups filters and search in one card and keeps Import CSV in the bank header. Import entry points, preview/draft separation and save/retry rules below are unchanged.

Open **My Subjects → Questions → Import CSV** in an existing subject. The file adds questions to that subject only; it never creates a subject or edits existing questions. Flashcard CSV import is available separately in Flashcards.

## Prepare a file

Use **Save CSV template** or the [header-only template](examples/questions-template.csv). Add your own rows; the template contains no sample questions and is never imported automatically. Save as UTF-8 (optional BOM), comma-separated CSV. Quoted commas and multiline fields are supported. Semicolon-separated files, unknown/duplicate headers and invalid UTF-8 are rejected. The maximum is **2 MiB and 500 nonblank question records**; split larger files. Blank records are ignored.

Required columns: `prompt`, `option_a`, `option_b`, `option_c`, `option_d`, `correct_option`, `difficulty`. Optional columns: `topic`, `explanation`. Column order is flexible and header case/outer whitespace is ignored. `correct_option` uses **A, B, C or D**, not numeric indexes. Difficulty is Easy, Medium or Hard; answer letters and difficulty are case-insensitive.

Existing question limits apply: prompt 1–2,000 characters, four distinct answers of 1–500 characters, explanation up to 2,000 characters, topic name up to 120 characters. Invalid control characters are rejected. Empty topic means No topic. Topics are reused by normalized name (whitespace, Unicode NFKC and casefold); missing topics are created only when the full batch commits.

## Preview and import

1. Select **Choose CSV…**. Preview uses a read-only, non-creating database connection; it does not migrate the database or save questions/topics.
2. Read the issues and use Previous/Next to inspect every valid question, answer, correct choice, difficulty, explanation and topic. Invalid rows may coexist with valid preview rows, but **any issue disables Import all**. Record numbers refer to CSV records including the header, not necessarily physical lines for quoted multiline text; malformed CSV errors may identify a physical line.
3. Exact duplicates are rejected within the file and against the selected subject. Identity includes all normalized question fields and the normalized topic name. Different explanations, difficulty or topics count as different questions. Existing questions are never overwritten or silently skipped.
4. **Import all** confirms saving the preview. The private preview snapshot is used even if the original CSV changes afterward. To load file edits, choose the file again. The subject identity/name, duplicates and current topics are rechecked under the write lock. A renamed/deleted subject or new duplicate rejects the whole batch rather than retargeting it.
5. Topics/questions save in one transaction. A validation or write failure saves none of the batch and keeps the preview for retry or correction. If another window changed the data, fix the listed issues and choose the CSV again.
6. Success consumes the batch before refreshing reports. If totals cannot refresh, use **Refresh totals**; it does not import again. If the helper stops before confirming a result, the import may have committed: refresh/inspect the subject before choosing the CSV again. The consumed preview cannot be submitted again by the same callback.

Close import or navigation cancels a file-read preview and preserves separate question/topic editor drafts while staying in the bank. During the actual save, a modal blocks editing, navigation and normal close/Quit until completion. A helper process performs file parsing and database work; no networking or AI is involved. Jobs have a 60-second process safeguard. Use regular local files, not network paths.

The question bank now displays **50 questions per page**. Search and filters apply to the entire subject, not just the current page. Editing/refresh preserves the current page where possible; changing filters or subjects returns to page 1. Existing filters can hide newly imported questions.

Template files are published atomically without overwriting existing files or database companion paths. On POSIX, no-overwrite publication requires a filesystem supporting hard links; if an external drive rejects it, use a supported local folder. Current schema is **9** and existing practice snapshots/history are unaffected. Import is not synchronization, merge/update, spreadsheet-formula evaluation or flashcard import in this screen.

[Import flashcards from CSV](FLASHCARD_CSV_IMPORT.md)
