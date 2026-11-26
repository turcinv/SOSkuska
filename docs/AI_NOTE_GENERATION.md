# Generate flashcards and questions from notes

[English](AI_NOTE_GENERATION.md) · [Čeština](cs/AI_NOTE_GENERATION.md) · [Slovenčina](sk/AI_NOTE_GENERATION.md) · [Русский](ru/AI_NOTE_GENERATION.md)

SOSkúška can turn pasted study notes into draft flashcards or multiple-choice questions using your optional local Ollama server. Every draft is reviewed by you before anything is saved. Ordinary study never needs AI.

## Before you start

1. Install and start [Ollama](https://ollama.com) and pull a model, for example `ollama pull llama3.2:3b`. Structured output requires Ollama 0.5 or newer.
2. In **AI Tutor**, connect and pick the model, then choose **Use Tutor choices** and **Save** in Settings. Alternatively, enter the server URL and preferred model directly in **Settings → AI**.

The generator always uses the **saved** server and preferred model shown in its panel. It never connects on its own and never uses a cloud fallback.

## Use it

- **Flashcards:** open a deck and choose **Generate with AI**.
- **Questions:** open a subject's question bank and choose **Generate with AI**.

Paste notes (up to 12,000 characters), choose how many items you want (3, 5, 10, 15 or 20) and press **Generate**. Only then are your notes sent to the server shown in the panel. You can **Stop** at any time or keep studying on other pages while it runs.

When it finishes, each draft appears with a checkbox. Questions show all four options with the correct one marked, difficulty, optional topic and explanation. Untick anything wrong or unwanted and press **Save selected**. Items that break the usual rules (empty text, duplicate options, invalid answer letter, too long) are listed and skipped automatically.

## What is saved

- Selected items are saved together in one step, through the same rules as CSV import. If any selected item already exists in the deck or subject, or the deck/subject was renamed or deleted, nothing is saved and the problem is listed. Untick the listed items, or reopen the target, and save again.
- New flashcards are due immediately. Question topics are created when needed. Existing cards, questions, schedules and history are never changed.
- Your notes are not stored in the database. They stay in the panel while it is open for the same deck or subject, also after Save. Opening another deck or subject discards unsaved drafts; drafts are also discarded on Stop, Close or a new Generate.

## Limits and accuracy

AI drafts can be wrong, incomplete or not supported by your notes even though the model is told to use only them. Read every item before saving. Smaller models follow the structure less reliably; if you get "did not return valid JSON", retry or choose another model. Requests time out after 5 minutes; long notes or 20 questions take longer on slow computers. Changing AI settings and restoring a backup wait until generation finishes or is stopped.

Automated checks use a local test server, not a real model. The quality of real models has not been evaluated.
