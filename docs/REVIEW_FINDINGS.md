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
