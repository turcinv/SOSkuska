# Semester report outline

[English](REPORT_OUTLINE.md) · [Čeština](cs/REPORT_OUTLINE.md) · [Slovenčina](sk/REPORT_OUTLINE.md) · [Русский](ru/REPORT_OUTLINE.md)

Planning draft, **23 November 2026**, based on **SOSkúška v0.18.1**, schema 10. Proposed topic: **SOSkúška: design and implementation of a local study assistant**. Topic approval, final report language and student/course details remain pending. This outline is not the final Word document. The [requirements checklist](SEMESTER_CHECKLIST.md) identifies the assignment source, formatting rules and unresolved submission items.

## Front matter and page budget

Create a cover/title page using the supplied sample, then an automatic table of contents and generated figure/table lists. Use real heading/caption fields; update them in the final editor. Keep front matter, references and appendices outside the conservative main-text count.

| Main chapter | Target pages | Writing purpose |
| --- | --- | --- |
| 1 Introduction | 1 | Explain the study problem, intended user and project aim. |
| 2 Goals and scope | 1 | Distinguish assignment obligations, chosen app features and exclusions. |
| 3 Technology choices | 1 | Explain Python, CustomTkinter, SQLite and optional Ollama, including trade-offs. |
| 4 Architecture and data | 2 | Explain runtime/data flows, persistence, history snapshots and migrations. |
| 5 Implementation | 3 | Describe representative workflows and their failure/retry behavior. |
| 6 Verification and evaluation | 2 | Present actual automated evidence, manual gaps, review fixes and limitations. |
| 7 Conclusion and future work | 1 | Evaluate achieved goals and prioritize remaining work. |
| **Total main text** | **11** | Planning allocation only; verify actual rendered pagination against the 10-page minimum. |

Each main chapter starts on a new page. Use heading levels 1–3 with Arabic multilevel numbering. Do not count a chapter as written because a repository guide exists.

## Chapter writing prompts and reusable material

### 1 Introduction

Describe why students need to organise their own subjects, questions and practice. State the aim: a local desktop study assistant with optional AI support. Define the target user and offline use. Avoid claims of improved grades, validated learning effectiveness or measured mastery without evidence.

### 2 Goals and scope

- **2.1 Assignment and project choices:** S1 requires a formatted report and exam presentation; it does not mandate this technology stack or feature list. State confirmed topic approval and any separately supplied rubric.
- **2.2 Functional scope:** subjects/questions, practice, cards, focus/statistics, settings, backup/import and optional Tutor. Point to the [feature evidence mapping](SEMESTER_CHECKLIST.md#application-material-available-for-the-report).
- **2.3 Boundaries:** local data, no account/cloud requirement, no installer/synchronization, custom repetition rules, plain-text AI responses and manual platform checks still outstanding. Separate implemented behavior from [future proposals](PLANNED_ARCHITECTURE.md).

### 3 Technology choices

Explain each dependency's role and a concrete trade-off: native GUI and platform/Tk behavior; transactional local SQLite and file locking; optional Ollama HTTP/HTTPS, cancellation and model-dependent output. Cite sources actually consulted. This section is analysis, not a list of installation commands; link to [developer setup](DEVELOPMENT.md) for reproduction.

### 4 Architecture and data

- **4.1 Runtime:** the Tk main thread handles widgets, short Store operations and queued network results. CSV/backup jobs use isolated processes with their own database connections and file-backed output. Network workers do not touch Tk/SQLite; file workers do use SQLite. Reuse and verify diagrams in [current architecture](CURRENT_ARCHITECTURE.md).
- **4.2 Persistence:** schema 10, transactional migration, subject/topic/question relationships, immutable practice/review/chat snapshots, deletion rules and saved preferences. Explain why historical names/answers survive source deletion. Present selected relationships, not the entire SQL dump.
- **4.3 Reliability:** atomic writes, stale-snapshot checks, read retries separated from committed writes, focus ownership/checkpoints and the machine-local backup plan. Distinguish SQLite study data from `<database>.backup-plan.json`; it is not transferred inside an exported database.

### 5 Implementation

- **5.1 Content authoring:** create a Unicode subject/topic/question, validate four distinct answers, filter and safely edit/delete. Include the kept-draft/stale-confirmation behavior from [resolved findings](REVIEW_FINDINGS.md).
- **5.2 Practice and flashcards:** saved answers, timed resume, immutable results, reveal-before-rating, deterministic scheduling and retained history. Do not describe the custom card rules as SM-2 or FSRS.
- **5.3 Focus and reports:** monotonic elapsed time, paused crash recovery without downtime credit, idempotent Finish and save-day statistics. Midnight splitting is not implemented.
- **5.4 Optional Tutor:** explicit Connect/Send, model discovery, streaming/Stop and saved conversations. Explain context bounds and that generated answers are not automatically verified.
- **5.5 Settings and data management:** separate UI/answer languages, live appearance, CSV preview/atomic import, manual restore/safety copy and opt-in daily backups while open. Explain backup retention and same-day scheduling limits. Refer to the feature guides instead of claiming missing features exist.

### 6 Verification and evaluation

- **6.1 Reproducibility:** record version, commit, schema, OS/Tk/runtime and test command. Use disposable data and [container checks](CONTAINER_TESTS.md).
- **6.2 Automated evidence:** cite the recorded 306-unit/18-GUI validation and [main CI for the release commit](https://github.com/turcinv/SOSkuska/actions/runs/45065149649). Explain the two platform skips and five jobs. Distinguish Linux GUI tests, three-OS unit tests and hosted Windows packaged-executable checks.
- **6.3 Review case study:** summarize A62-01 through A62-04, reproduce the trigger in words, explain the fix and point to regression evidence. Present tests as evidence of covered cases, not proof of no bugs.
- **6.4 Outstanding evaluation:** record real [Windows acceptance](WINDOWS_ACCEPTANCE.md) and Ollama results when performed. Until then, keep them explicitly unverified; fake-server response tests are not model-quality evaluation.

### 7 Conclusion and future work

Compare outcomes with the stated goals, summarise limits and name the next priorities: report/acceptance evidence first, then selected roadmap improvements. Do not describe planned architecture, advanced statistics, export or an installer as completed. Include a realistic maintenance/testing discussion.

## Planned figures and tables

These are asset IDs, not final caption numbers. All assets are **pending capture/export/insertion**. Use disposable content, retain version/date/context, and insert real caption fields. S1's examples use `Obrázok`, `Tabuľka` and `Graf`; confirm labels if a different report language is approved.

| Asset | Planned content | Destination / evidence |
| --- | --- | --- |
| F-01 | Actual runtime/data-flow diagram, including isolated file workers | Chapter 4; adapt and verify current Mermaid source, then export for the report. |
| F-02 | Selected schema-10 relationships and retained-history rules | Chapter 4; derive from `storage.py`, not the proposed future model. |
| F-03 | Subject/question editor with clearly labelled disposable content | Chapter 5.1; capture the released app. |
| F-04 | Practice result or revealed flashcard with saved history | Chapter 5.2; record the exact workflow/data. |
| F-05 | Paused focus recovery or daily-backup controls | Chapter 5.3/5.5; show the implemented behavior. |
| T-01 | Goals and implemented-feature mapping | Chapter 2; distinguish S1 requirements from project scope. |
| T-02 | Verification matrix with actual outcomes and unverified checks | Chapter 6; include OS/environment/version and skips. |
| T-03 | Four Astra findings, fixes and regression checks | Chapter 6.3; use the preserved resolution record. |

Do not invent screenshots or results. A statistical graph is optional; if included, use actual saved data, explain its units/limits and apply the graph-caption rule. Generated lists must match the assets actually inserted.

## Bibliography preparation

Choose and read relevant sources for the technologies and study context. Use the supplied author–date citation examples consistently; record actual bibliographic metadata and online access dates. The course PDF's sample bibliography is a formatting example, not sources already consulted for this app. Confirm the book/internet expectation before finalising. No fabricated author/year/ISBN entries are supplied here.

## Proposed presentation rehearsal

This sequence is a proposal; S1 gives no time limit or slide count. Confirm those details with the lecturer.

1. Introduce the problem and show an empty/disposable workspace working without AI.
2. Create a subject/question, complete a short practice and show a retained result; demonstrate a card reveal/rating if time permits.
3. Show focus save/recovery and explain that app downtime is not counted.
4. Show backup/restore using a separate disposable database. Restore closes the app; rehearse the restart and never replace ordinary study data for a demo.
5. Demonstrate Tutor streaming/Stop only after a real-model check. If unavailable, explain the limitation and use the offline study workflow.
6. Explain the architecture, one review fix, the test evidence and remaining limitations.

End with a generated-document check: update TOC/lists/cross-references, inspect captions/margins/page numbers, verify at least 10 counted pages, apply the confirmed filename, rehearse and retain the Moodle receipt. A PDF preview may help inspection; the required editable submission must still be prepared.
