# Flashcards and repetition (introduced in v0.5.0)

[English](FLASHCARDS.md) · [Čeština](cs/FLASHCARDS.md) · [Slovenčina](sk/FLASHCARDS.md) · [Русский](ru/FLASHCARDS.md)

Open **Flashcards** in the sidebar. New deck creates a deck for an existing subject; deck names are globally unique. A deck's subject cannot later change, but its name and description can. Open deck lets you add/edit cards. Front: 1–2,000 characters; back: 1–4,000. Search checks both sides. Lists show up to 100 matches; narrow your search for others.

**Study due** opens at most 100 currently due cards, oldest first. Reveal answer shows the back and enables Again / Hard / Good / Easy. Ratings are your own assessment of recall, not measured accuracy or mastery. Each rating saves a history snapshot and next due date together. Unrated cards stay due; after restart, start another batch. Refresh reloads counts and due status; lists do not rebuild in the background.

## Scheduling rules

These are simple custom rules, not SM-2 or FSRS.

| Rating | New / learning card (interval 0) | Card with an interval of at least one day |
| --- | --- | --- |
| Again | In 10 minutes; reset interval to 0 | In 10 minutes; reset interval to 0 |
| Hard | In 1 hour; interval stays 0 | Previous days × 1.2, rounded up |
| Good | In 1 day | Previous days × 2.5, rounded up |
| Easy | In 4 days | Previous days × 3.5, rounded up |

The maximum is 365 days. Due dates are UTC and displayed in local time. System-clock changes can affect due status. Editing card content makes it due now and resets its interval to 0; earlier ratings remain.

## History and deletion

Review history shows the latest 20 ratings with front/back, deck/subject names and due-date snapshots. Older rows remain stored. Deleting a subject keeps its decks/cards and historical subject name. Deleting a card or deck needs confirmation and retains review history. A changed deck name/card count requires a refreshed deletion confirmation. Stale edits/ratings are rejected instead of overwriting newer content. Write errors preserve form drafts and revealed answers for retry.

Conversion from questions and AI material integration remain planned. Aggregate activity is in [Statistics](STATISTICS.md).

## Import flashcards from CSV

Flashcards now supports UTF-8 CSV import into an existing deck: a header-only template, paged preview, exact-duplicate rejection and one atomic save. Maximum 2 MiB / 500 records. New cards are due immediately; existing schedules and review history are preserved. Current branch schema is 10. [Import flashcards from CSV](FLASHCARD_CSV_IMPORT.md).
