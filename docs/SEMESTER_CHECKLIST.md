# Semester submission checklist

[English](SEMESTER_CHECKLIST.md) · [Čeština](cs/SEMESTER_CHECKLIST.md) · [Slovenčina](sk/SEMESTER_CHECKLIST.md) · [Русский](ru/SEMESTER_CHECKLIST.md)

Prepared **23 November 2026** for **SOSkúška v0.18.1**, commit `f358804f99ce0133d137b035b16bd897b3761142`, schema 10. This is a submission plan, not a completed report or a declaration of assignment compliance. Use the [report outline](REPORT_OUTLINE.md) for writing.

## Assignment source and interpretation

**S1:** the user-provided `Pokyny pre vypracovanie semestralneho projektu.pdf`, 10 PDF pages. SHA-256: `06aaa6f075665e39cfc9dea855ffd4f1a27f8c854254f8a1b19125db0081fc9a`. The ChatGPT project reference and original supplied file matched when checked. The PDF remains outside this Git repository; retain the supplied original with the course materials. Page numbers below mean **physical PDF pages**, not the printed appendix numbers 12 and 18–23.

S1 sets document, formatting and submission requirements. It does **not** prescribe Python, SQLite, AI, an application feature list, a test count or a software grading rubric. The feature mapping below is proposed report content, not a list of teacher-mandated features. Confirm that the SOSkúška topic and any additional course rubric are accepted.

Status: **Pending** = final evidence/deliverable missing; **Partial** = reusable material exists but the final report is not verified. No formal requirement is marked complete just because application tests pass.

## Formal requirements

| ID | S1 page | Requirement | Status | Evidence / next action |
| --- | --- | --- | --- | --- |
| DOC-01 | 1 | Prepare the project in Word, Writer or another full text editor; submit an editable file. | Pending | Create the final `.docx` from the outline. Repository Markdown is preparation only. |
| DOC-02 | 1 | At least 10 pages, excluding title page, contents and references. | Pending | Target 11 main-text pages; conservatively exclude figure/table lists and appendices too. Verify the rendered final document. |
| DOC-03 | 1, 4 | Title page with topic and student name; use the supplied cover example. | Pending | Confirm student/institution/faculty/year; apply the cover layout separately. |
| DOC-04 | 1 | Generated table of contents. | Pending | Use heading styles and an automatic TOC; update fields after pagination. |
| DOC-05 | 1–2 | Generated lists of figures and tables. | Pending | Add real caption fields to the planned figures/tables and generate the lists. Typed lists do not satisfy this. |
| DOC-06 | 1 | Introduction, main chapters and subchapters. | Partial | Existing architecture/feature guides supply material; write a connected report using chapters 1–7 in the outline. |
| DOC-07 | 1, 5–10 | References and in-text citations following the supplied examples. | Pending | Build a bibliography from sources actually consulted; see citation decisions below. |
| DOC-08 | 2 | Body paragraph formatting. | Pending | Apply the style specification below in the final editor. |
| DOC-09 | 2 | Heading hierarchy, Arabic numbering and a new page for each main chapter. | Pending | Use levels 1–3 and linked multilevel numbering; verify page breaks. |
| DOC-10 | 2 | Figure/table/graph alignment and captions; indented bullets. | Pending | Insert prepared assets with caption styles; verify placement and generated lists. |
| DOC-11 | 3 | Page margins and header/footer distances; special cover margins. | Pending | Configure separate cover/body sections and inspect all pages. |
| DOC-12 | 3 | Page numbers at bottom right or bottom centre in Times New Roman 12 pt. | Pending | Insert automatic page fields; confirm where numbering starts. |
| DOC-13 | 1 | Filename pattern `Priezvisko_Meno_kruzok_cislo.doc` or `.docx` (another editor format is allowed). | Pending | Confirm the exact student/group identifiers before naming the final file. |
| DOC-14 | 1 | Submit for the exam through Moodle, section `Semestrálny projekt a prezentácia`. | Pending | Confirm exam/deadline and access; upload and retain a submission receipt. S1 gives lecturer email as fallback if Moodle upload fails. This task sends nothing. |
| DOC-15 | 1 | Present the semester project at the exam. | Pending | Rehearse the proposed demo; confirm allotted time and required presentation format. |

## Final document style specification

These are S1 requirements, not styles already applied to the Markdown files.

| Element | Required settings | S1 page |
| --- | --- | --- |
| Body | Times New Roman 12 pt; 1.5 line spacing; justified; 6 pt before, 0 pt after. First paragraph after a heading has no first-line indent; later paragraphs use 0.5 cm. | 2 |
| Heading 1 | Times New Roman 16 pt bold, left; 1.5 spacing; 6 pt before/after; no indent; Arabic numbering; start on a new page. | 2 |
| Heading 2 | Times New Roman 14 pt bold, left; 1.5 spacing; 6 pt before/after; no indent; numbering such as 1.1. | 2 |
| Heading 3 | Times New Roman 12 pt bold, left; same spacing/indent settings; numbering such as 1.1.1. | 2 |
| Heading 4 | Times New Roman 12 pt regular, left; same spacing/indent settings. S1 repeats 1.1.1 for this level; avoid level 4 in this outline rather than silently changing its rule. | 2 |
| Figures | Centre; 6 pt before. Caption below, Times New Roman 11 pt, 1.5 spacing, 6 pt before/after, no indent; example `Obrázok 1 Názov`. | 2 |
| Tables | Left align. Caption above, Times New Roman 11 pt, 1.5 spacing, 6 pt before/after, no indent; example `Tabuľka 1`. | 2 |
| Graphs, if used | Centre; caption below with the same 11 pt caption style; example `Graf 1 Názov`. S1 explicitly requires figure/table lists, not a separate graph list. | 2 |
| Bullets | Left indent 0.5 cm. | 2 |
| Body pages | Top/bottom 2.5 cm; left 3.5 cm; right 2 cm; header/footer distance 1.25 cm. | 3 |
| Cover | All four margins 2.5 cm; adapt the sample on PDF page 4 after confirming the institution/faculty. | 3–4 |
| Page numbers | Bottom right or bottom centre; Times New Roman 12 pt. S1 does not specify the first displayed page number. | 3 |

S1 first says “without indentation” for body text and then specifies 0.5 cm except after headings; the table uses the latter, more specific rule. Confirm a different lecturer interpretation before final styling. Caption examples are Slovak; confirm labels if the final report uses another language.

## Application material available for the report

All rows mean **implemented in v0.18.1; report figures/narrative still pending**. These are project choices, not extra S1 requirements.

| Area | Evidence available | Proposed use |
| --- | --- | --- |
| Subjects and question bank | [Architecture](CURRENT_ARCHITECTURE.md), `subjects.py`, `question_bank.py`, `tests/test_subjects.py`, `tests/test_questions.py` | Explain actual CRUD, validation, topic ownership and stale-state protection. |
| Practice and flashcards | [Practice history](PRACTICE_HISTORY.md), [Flashcards](FLASHCARDS.md), `practice.py`, `repetition.py`, related tests | Explain saved attempts, immutable answer snapshots and self-rated review scheduling. |
| Focus and statistics | [Focus recovery](FOCUS_RECOVERY.md), [Statistics](STATISTICS.md), `focus.py`, `study_statistics.py` | Explain monotonic elapsed time/checkpoints, paused recovery and aggregates; do not equate statistics with mastery. |
| Optional AI Tutor | [AI Tutor](AI_TUTOR.md), [Saved chat](TUTOR_HISTORY.md), `ollama_client.py`, Tutor tests | Explain explicit connection, streaming/Stop, local history and offline study; separate protocol fixtures from real-model quality. |
| Settings and interface | [Settings](SETTINGS.md), [Languages](UI_LANGUAGES.md), [Appearance](APPEARANCE.md) | Explain four UI languages, independent answer language and saved appearance choices. |
| Data protection and transfers | [Backup/restore](BACKUP_RESTORE.md), [Scheduled backups](SCHEDULED_BACKUPS.md), [Question CSV](QUESTION_CSV_IMPORT.md), [Card CSV](FLASHCARD_CSV_IMPORT.md) | Explain atomic import/restore, standalone snapshots, machine-local opt-in and limits. |
| Delivery and quality | [Windows package](WINDOWS_PORTABLE.md), [Container tests](CONTAINER_TESTS.md), [Resolved findings](REVIEW_FINDINGS.md) | Explain packaging, five CI jobs, regression review and honest platform limitations. |

## Evidence boundaries and remaining work

- **Available:** v0.18.1 at the commit above; [release notes and downloads](https://github.com/turcinv/SOSkuska/releases/tag/v0.18.1); [successful main CI](https://github.com/turcinv/SOSkuska/actions/runs/45065149649). The recorded implementation validation is 306 unit tests with two platform skips and all 18 Linux/Xvfb GUI scripts. This documentation task does not rerun or relabel that historical test run.
- **Available:** the release Windows acceptance JSON and ZIP/checksum. Hosted executable/helper checks are not manual clean-machine, scaling or hardware evidence.
- **Pending:** complete [manual Windows acceptance](WINDOWS_ACCEPTANCE.md) with OS/build, hardware, scaling, version/hash, date and results. The user's earlier v0.15.0 confirmation is not item-by-item v0.18.1 evidence.
- **Pending:** a real Ollama model run with model/version, hardware, server, date and outcomes. Fake-server tests do not establish answer quality or real-model performance.
- **Pending:** final editable report, real screenshots/caption fields, generated lists, selected sources, presentation and Moodle submission receipt. Existing Mermaid diagrams are reusable source material, not already inserted report figures.

## Citation and metadata decisions

S1 pages 5–10 give author–date/Harvard-style ISO 690 examples and bibliography metadata guidance. Follow those supplied examples consistently; this plan does not assert which ISO edition is currently normative. Record author/organisation, title, actual date/edition, applicable publisher/identifiers, and URL/access date for online sources. Do not copy unrelated example references into the project's bibliography. The wording on page 1 mentions book/internet references: plan both categories where genuinely used, or confirm the lecturer's expectation; never invent a book citation.

Still pending: student's full name; institution/faculty/course; study group and filename identifiers; exam/submission date; accepted topic/additional rubric; final report language; presentation duration/format. Repository account names are not evidence of student identity. No exact deadline or presentation length is stated in S1.

## Completion order

1. Confirm the pending metadata and topic/rubric; choose actual bibliography sources.
2. Create the editable report with the specified styles, automatic fields and the [11-page outline](REPORT_OUTLINE.md).
3. Capture disposable-data figures, add evidence and record manual/real-model checks without fabricating results.
4. Update all fields, inspect the rendered pages, verify the counted page total and filename, rehearse, then submit through the required course route. Publishing this documentation PR does not submit the semester project.
