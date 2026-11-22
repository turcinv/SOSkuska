# Astra 6.2 main-branch findings

[English](REVIEW_FINDINGS.md) · [Čeština](cs/REVIEW_FINDINGS.md) · [Slovenčina](sk/REVIEW_FINDINGS.md) · [Русский](ru/REVIEW_FINDINGS.md)

Recorded from the Astra 6.2 low-effort review of v0.18.0 at `252acc588700e46f0df5f76c9a31879104924fa2`. Keep this file as the resolution record; change a status only after its fix is verified. Fix branch: `fix/main-review-findings`. No merge or release is authorized by this record.

| ID | Priority | Status | Finding | Required behavior |
| --- | --- | --- | --- | --- |
| A62-01 | P2 | Open | An older subject form silently overwrites another window’s description or exam-date changes. | Compare the original editable snapshot under the write lock; preserve the rejected draft. |
| A62-02 | P2 | Open | A pending question-delete confirmation removes a question edited in another window. The topic path has the same confirmation pattern. | Recheck the displayed snapshot atomically before deleting; changed content requires a new confirmation. |
| A62-03 | P2 | Open | Returning to the same subject’s question bank loses an unfinished question draft. | Preserve the active editor, original identity and draft when revisiting the same subject. |
| A62-04 | P3 | Open | A backup failure banner remains after another window successfully creates today’s backup. | Reconcile a newer success receipt and clear only the superseded failure indicators. |
