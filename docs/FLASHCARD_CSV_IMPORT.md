# Import flashcards from CSV

[English](FLASHCARD_CSV_IMPORT.md) · [Čeština](cs/FLASHCARD_CSV_IMPORT.md) · [Slovenčina](sk/FLASHCARD_CSV_IMPORT.md) · [Русский](ru/FLASHCARD_CSV_IMPORT.md)

Flashcards now supports UTF-8 CSV import into an existing deck: a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records. New cards are due immediately; existing schedules and review history are preserved. Schema stays 6.

1. Open **Flashcards → Open deck → Import CSV**. Create the subject/deck first if needed.
2. Use **Save CSV template**, choose an unused filename, then fill its `front,back` columns in a text editor or spreadsheet. Export comma-separated UTF-8 CSV (an optional BOM is supported).
3. Use **Choose CSV…**. Inspect each card with Previous / Next. Every issue must be fixed before **Import all** becomes available. Nothing is saved during preview.
4. Choose **Import all**. All cards save together or none do. Wait for completion before navigating or closing. New cards can be studied immediately with **Study due**.

Front is required (1–2,000 characters); back is required (1–4,000). Outer whitespace is trimmed. Header order/case/outer whitespace may vary; unknown or repeated columns are rejected. Quote commas and multiline values using standard CSV quoting. Blank records are ignored. Semicolon CSV, legacy encodings, images, automatic question conversion and merge/update are unsupported.

Duplicates mean the exact trimmed front **and** back, case-sensitive, within the file or the destination deck. The whole batch is rejected; nothing is skipped or overwritten. Another deck may contain the same card. The deck identity/name and duplicates are rechecked under the write lock. Renamed/deleted decks require reopening and selecting again; a deck retained after subject deletion remains usable.

The preview is a private batch: editing the original file requires **Choose CSV…** again. Close import/navigation discards a pending preview. During parsing you can cancel; actual saving blocks navigation/Quit. If a write error occurs, you can retry the retained preview. If saving succeeded but totals failed, use **Refresh totals**; it never imports again. If the helper stops without confirming an outcome, inspect the deck before selecting again because the batch may have committed.

Templates contain only headers, publish atomically and never overwrite existing files or database companions. POSIX requires hard-link support; use a supported local folder if an external filesystem rejects publication. Files are read/validated in isolated processes; preview opens the existing database read-only without migration. No cloud, schema change or invented reviews.

[CSV template](examples/flashcards-template.csv)
