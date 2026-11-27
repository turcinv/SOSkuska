# Semester presentation materials

Working drafts for the author's semester demo and report, written against v0.31.1 on 27 November 2026. They are English-only on purpose: the report language is still a placeholder, and the final text will be written in that language. These files describe the project; they are not user documentation and have no translations.

- [Demo script](DEMO_SCRIPT.md): preparation, a 6-minute walkthrough with talking points, fallbacks and likely questions.
- [Report outline](REPORT_OUTLINE.md): section-by-section outline with checked facts, sources and `[[placeholders]]`.

## Screenshots

All captures use disposable fixture data, at 1440 × 900 in the Linux/Xvfb test container (Noto Sans font). They are not native macOS/Windows screenshots; take native ones during the rehearsal if the report needs them. Data such as the 0/2 practice result and the Tutor reply come from the design fixture, and the AI drafts come from a local fake server, not a real model.

| File | Shows |
| --- | --- |
| `01-dashboard-light.png` | Dashboard, Light |
| `02-dashboard-dark.png` | Dashboard, Dark |
| `03-dashboard-czech.png` | Dashboard in Czech |
| `04-subjects.png` | My Subjects |
| `05-question-bank.png` | Question bank of a subject |
| `06-question-editor.png` | Question editor with validation |
| `07-ai-drafts-questions.png` | Questions drafted from notes, ready for review |
| `08-practice-setup.png` | Practice test setup and history |
| `09-practice-running.png` | A running practice test |
| `10-practice-result.png` | Result with saved snapshots and Explain this question |
| `11-flashcard.png` / `12-flashcard-revealed.png` | Flashcard review before and after reveal |
| `13-statistics.png` | Statistics for the last 7 days |
| `14-ai-tutor.png` | A saved AI Tutor conversation, opened offline |
| `15-settings-ai.png` | AI settings (server and preferred model) |
| `16-restore-preview.png` | Validated restore preview with confirmation |
| `17-csv-import.png` | CSV question import preview |

To regenerate screens 01–06 and 08–17, run `tools/capture_redesign.py` in the test image as described in `docs/agents/design/study-studio-dashboard/README.md`, with `--dashboard-only` (and `--mode Dark` or `--language Czech`), `--authoring-views`, `--practice-views`, `--flashcard-views`, `--report-views` or `--data-views`. Screen 07 comes from `tools/capture_ai_drafts.py` (same image, same fake local Ollama server as `check_note_generation.py`).
