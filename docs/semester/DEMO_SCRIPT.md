# Teacher demo script (about 6 minutes)

Working draft for the author's semester presentation, written against v0.31.1. It uses only disposable sample data; your real database is never opened.

## Prepare (10 minutes, the day before)

1. Sample database with two subjects, exams, due cards and one practice result:

   ```sh
   .venv-macos/bin/python tools/make_mcp_acceptance_db.py .local-data/demo/study.sqlite3
   ```

   Run it again into a new path (for example `.local-data/demo2/study.sqlite3`) if you want a fresh copy for a second rehearsal; it never overwrites a file.
2. Start Ollama and check the model answers: `ollama run qwen3:4b-instruct-2507-q4_K_M "Say hello"`. Cold start can take 10–20 s, so run it once just before the demo.
3. Start the app on the sample data and save the AI settings once:

   ```sh
   .venv-macos/bin/python soskuska/app.py --data .local-data/demo/study.sqlite3
   ```

   In **Settings → AI**, set the server `http://127.0.0.1:11434` and the preferred model, then **Save settings**.
4. Optional MCP part: connect Claude Desktop to the same database as in `.local-data/mcp-acceptance/README.md` (use the demo path for `--data`).
5. Keep a copy of the notes below in a text file to paste. Set the window to full screen; Light mode reads best on a projector.

Notes to paste:

> Mitosis produces two identical daughter cells. It has four phases: prophase, metaphase, anaphase and telophase. In metaphase the chromosomes line up in the middle of the cell. Meiosis produces four genetically different cells with half the chromosome number and is used to make gametes.

## Script

| Time | Do | Say |
| --- | --- | --- |
| 0:00 | **Dashboard** | "SOSkúška is an offline study app: Python, CustomTkinter and SQLite. Everything here is stored in one local file; nothing needs the internet." Point at the stat tiles, the exam calendar dots and *Upcoming exams*. |
| 0:40 | **Start Studying** on *Sample Biology*, wait a few seconds, **Pause**, **Finish** | "Focus time is saved per subject and checkpointed every few seconds, so a crash or power cut does not lose it." |
| 1:20 | **My Subjects → New subject** *Cell Biology*, exam date two weeks ahead, **Save** | "Validation stops empty, duplicate or wrong-format input. New installations start empty; the app never invents data." |
| 1:50 | Open its **Questions → Generate with AI**, paste the notes, 5 items, **Generate** | "The notes go only to my local Ollama model, only when I press Generate. The model writes the correct answer as text and the app places it, because in testing the model sometimes marked the wrong letter." |
| 2:40 | Untick one draft, **Save selected** | "Nothing is saved until I review it. Drafts not clearly supported by my notes start unticked with a warning." |
| 3:10 | **Practice Tests**: *Cell Biology*, 3 questions, **Start**; answer, **Finish** | "Each answer is saved immediately; the result keeps a snapshot, so editing questions later does not change history." |
| 3:50 | **Explain this question** on a wrong answer → **AI Tutor** | "The explanation request is prepared from the saved question; I see exactly what will be sent and choose a mode such as *Give me a hint*." |
| 4:30 | **Flashcards → Sample Biology cards → Study due**, reveal, rate *Good* | "Spaced repetition with self-ratings; the next due date is saved." |
| 5:00 | **Statistics**, period *Last 7 days* | "Accuracy weighs every question equally, unanswered count as wrong, and ratings are labelled as self-assessment, not mastery." |
| 5:30 | Optional: Claude Desktop, *"Quiz me on Sample Biology"* | "A read-only MCP server lets my own assistant use this data. It cannot change anything and hides answers until I reply." |
| 6:00 | Close | "There are 382 unit tests and 26 GUI checks, run in a Linux container and on GitHub (unit tests also on Windows and macOS); a Windows portable ZIP is built and checked for each release." |

## If something goes wrong

- **Ollama is slow or fails:** say so, press **Stop**, and show `docs/semester/screenshots/07-ai-drafts-questions.png` instead. Practice and flashcards work without AI.
- **No due flashcards:** the sample deck has four due cards; a second run of the same database has fewer after rating. Use a fresh sample copy.
- **Wrong database opened:** the footer shows the version; close and restart with `--data .local-data/demo/study.sqlite3`.
- **Questions you may get:** why offline (privacy, no accounts, works on school Wi-Fi); why SQLite (single file, transactions); how AI mistakes are handled (review before save, app-placed answers, warnings); how it is tested (unit tests, Xvfb GUI checks, real-model evaluation in `docs/agents/design/ai-note-generation/EVALUATION.md`).

## Not rehearsed yet

The full flow has not been run natively on the presentation computer. Do one rehearsal there, including the projector resolution (the app needs at least 1024 × 700).
