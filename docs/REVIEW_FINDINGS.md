# Astra 6.2 main-branch findings

[English](REVIEW_FINDINGS.md) · [Čeština](cs/REVIEW_FINDINGS.md) · [Slovenčina](sk/REVIEW_FINDINGS.md) · [Русский](ru/REVIEW_FINDINGS.md)

Recorded from the Astra 6.2 low-effort review of v0.18.0 at `252acc588700e46f0df5f76c9a31879104924fa2`. Keep this file as the resolution record; change a status only after its fix is verified. Fix branch: `fix/main-review-findings`. No merge or release is authorized by this record.

| ID | Priority | Status | Finding | Required behavior |
| --- | --- | --- | --- | --- |
| A62-01 | P2 | Released in v0.18.1 | An older subject form silently overwrites another window’s description or exam-date changes. | Compare the original editable snapshot under the write lock; preserve the rejected draft. |
| A62-02 | P2 | Released in v0.18.1 | A pending question-delete confirmation removes a question edited in another window. The topic path has the same confirmation pattern. | Recheck the displayed snapshot atomically before deleting; changed content requires a new confirmation. |
| A62-03 | P2 | Released in v0.18.1 | Returning to the same subject’s question bank loses an unfinished question draft. | Preserve the active editor, original identity and draft when revisiting the same subject. |
| A62-04 | P3 | Released in v0.18.1 | A backup failure banner remains after another window successfully creates today’s backup. | Reconcile a newer success receipt and clear only the superseded failure indicators. |

## Resolution and validation

All four findings were fixed on `fix/main-review-findings`, merged through [PR #38](https://github.com/turcinv/SOSkuska/pull/38) and released in [v0.18.1](https://github.com/turcinv/SOSkuska/releases/tag/v0.18.1). This file remains the resolution and validation record.

Local Docker/Xvfb: **306 unit tests** (two platform skips), **18 GUI scripts** passed. Independent Sol review at medium effort found no remaining blockers. Native hardware/manual acceptance remains separate.

- A62-01: `test_subject_draft_does_not_overwrite_concurrent_description_or_exam`; `check_state_fixes.py`.
- A62-02: `test_question_deletion_requires_reconfirmation_after_changed_answers`, `test_topic_rename_invalidates_delete_warning_without_removing_questions`, `test_disappearing_record_clears_old_confirmation_and_does_not_retry_delete`; `check_state_fixes.py`.
- A62-03: `check_state_fixes.py` — new/edit drafts, initial read retry, topic rename/deletion/recreation, explicit cancel and subject switching.
- A62-04: `test_real_external_worker_success_reconciles_failed_window`, `test_older_or_invalid_receipt_does_not_clear_unresolved_failure`; `check_scheduled_backups.py`.

[Unit tests](../tests/test_review_findings.py) · [GUI state checks](../soskuska/check_state_fixes.py) · [Backup GUI checks](../soskuska/check_scheduled_backups.py).


## Full main review · 26 November 2026 · Astra 6.2 medium

`main` · v0.26.0 · `db38e08802058480bbed250c16eeffc23bad143b`

| ID | Priority | Status | Finding | Reproduction / location | Required behavior |
| --- | --- | --- | --- | --- | --- |
| A62-05 | P2 | Open | A stale deck editor silently restores the old description when saving a title after another window saved a new description. | `flashcard_page.py:291`, `storage.py:713`. Open Edit deck, save a changed description from another Store/window, then change only the original title and press Save: both succeed; the newer description is lost. | Compare the original editable deck snapshot under the write lock; retain the rejected draft. |
| A62-06 | P2 | Open | A stale topic rename form silently replaces a newer rename from another window. | `question_bank.py:284`, `storage.py:402`. Open Rename topic, rename elsewhere, then Save from the original form: the later database name is overwritten without a conflict warning. | Compare the original topic identity/name atomically before saving; retain the rejected draft. |
| A62-07 | P3 | Open | A restored flashcard with an accepted non-UTC timestamp can be hidden or rejected despite already being due. | `storage.py:687,811,823`, `flashcard_page.py:388`. Store a due time five minutes ago encoded as `+10:00`, then back up, validate, restore and reopen: due queue is empty and rating says the card is not due. | Compare parsed instants consistently in deck counts, queues, UI checks and rating validation. |
| A62-08 | P3 | Open | Statistics drops a restored completion whose accepted UTC offset includes seconds. | `study_statistics.py:42,45`, `backup_validation.py:28`. Restore a completion encoded with `+03:00:07`: history counts 1; All time Statistics counts 0 because SQLite date parsing returns NULL. | Align Statistics timestamp parsing with the accepted backup/history domain for practice and reviews. |
| A62-09 | P3 | Open | Restore instructions in Tutor history and UI language guides still claim schema 9. | `docs/TUTOR_HISTORY.md:31`, `docs/UI_LANGUAGES.md:13` and all translations; `backup.py:102` requires schema 10. | Correct present-tense restore requirements in all four languages while preserving historical migration descriptions. |

Existing exact-commit CI passed all five jobs: 322 unit tests on each platform and all 23 Linux GUI scripts. Targeted disposable-data probes reproduced both stale forms through actual Save buttons in Docker/Xvfb and both timestamp cases through backup validation, restore and reopening; the parent independently repeated those probes. Timestamp findings require accepted encodings different from ordinary app UTC writes. Broader source coverage included runtime, storage/migrations, study flows, Tutor/modes, preferences, transfers, CI/Windows packaging and documentation. These are findings, not fixes; application code is unchanged. Real-model testing remains deferred, and native hardware/manual platform acceptance was not performed.
