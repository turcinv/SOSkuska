# Session lessons and project handoff

[English](SESSION_LESSONS.md) · [Čeština](cs/SESSION_LESSONS.md) · [Slovenčina](sk/SESSION_LESSONS.md) · [Русский](ru/SESSION_LESSONS.md)

Recorded on **20 November 2026**, after publishing **v0.11.0 — Flashcard CSV import**. This is a dated handoff, not a live status report. Verify Git, releases, current code and CI before making a new claim.

## Project and working preferences

SOSkúška is a native Python/CustomTkinter/SQLite semester project. Deliver manageable weekly features and leave time for the semester write-up. Keep the application usable offline; Ollama is optional. The user chose local development to avoid paid design generation. HTML in `soskuska-local/` is a design reference.

Conversation may switch between Czech, Slovak, English and Russian. Reply in the latest language. The UI stays English. Maintain English-primary user documentation and separate Czech, Slovak and Russian versions. Internal agent instructions stay English.

## Coding and release flow

1. Start a new branch from current main; implement the requested step from the roadmap. Never commit or push directly to main.
2. Use disposable data, run the checks appropriate to the change, and request independent **Sol review at medium effort** for implementation features. Fix findings on that branch and re-review affected changes.
3. Open a PR, describe actual verification and inspect CI. Fix failures without weakening checks. Green CI is not merge authorization.
4. Merge only when the user authorizes it. A request to merge and create a release also covers the necessary release-label PR and publication. Align the footer, four README release links, changelog headings and current-architecture status before tagging the exact merged commit.
5. Verify the published release and clean synchronized main. Do not assume the next feature, merge, release or branch cleanup is authorized by earlier unrelated work.

## Lessons worth preserving

- **Separate writes from refresh retries.** After a successful save, consume the batch before reading totals. A refresh failure must retry reads only. An unknown helper outcome may already have committed; inspect before importing again.
- **Keep preview stable.** Parse a private batch once. Changes to the source CSV require re-selection. Check target identity/name and duplicates again under the write lock, then save all rows in one transaction.
- **Use processes for CSV/backup jobs.** Python thread garbage collection previously finalized Tk objects and crashed macOS. Keep Tk on its main thread and use file-backed subprocess output; undrained pipes can deadlock on Windows.
- **Keep preview read-only.** Open the existing database without creation or migration. Capture the target already displayed in the UI; synchronous SQLite lookups during file selection can freeze Tk under a database lock.
- **Preserve unfinished text.** Rebuilding a screen can discard an unsubmitted search or editor draft. Capture/restore it separately from applied filters; test navigation and post-save refresh.
- **Review small UI details too.** During flashcard import, wait messages must reach the active importer. Duplicate tests must create enough existing records to exercise data beyond the display limit.
- **Treat platform evidence precisely.** Local macOS and Linux/Xvfb GUI checks do not prove manual Windows UI or physical trackpad behavior. The prepared Mac uses `.venv-macos`; Apple Tk 8.5 in `.venv-desktop` produced a blank window.

## Verified baseline at handoff

- Release **v0.11.0**, commit `b5acbdcc47310b1fab0ba9fb4b24dbac0db041ce`; implementation PR **#19**, release alignment **#20**.
- **202 unit tests** and **12 native GUI scripts** passed locally on macOS for the feature. Its four CI jobs passed: unit tests on Linux/Windows/macOS and GUI scripts on Ubuntu/Xvfb. Release-label changes received focused version, syntax and documentation checks.
- Schema **6**. Both question and flashcard CSV import exist. Flashcard imports support UTF-8/BOM comma CSV, exactly `front,back`, at most **2 MiB / 500 records**, exact-duplicate rejection and atomic saving into an existing deck. New cards are due now; existing schedules/review history remain intact.

## Keeping future context small

Use the short root `AGENTS.md` as a routing index. Read the required `@docs/agents/...` topic files before editing the corresponding area; avoid loading unrelated safeguards. These are explicit file-reading references, not a promise of automatic transclusion. The official [Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md) documents hierarchical instruction discovery; this repository therefore explicitly tells the agent to open its referenced files.

Record durable rules in the relevant topic file and new dated evidence here. Keep detailed release history in the changelog. When behavior changes, update the applicable safeguard and all language versions of user documentation.

## Next steps · 22 November 2026

Status updated 22 November 2026: the user confirmed v0.15.0 baseline testing complete and approved appearance PR #32. This checklist now targets v0.18.1; item-by-item clean-machine/DPI results are not recorded here. Leave unchecked items unverified and record device-specific evidence when testing the new release. [Next steps · 22 November 2026](NEXT_STEPS.md).

## Focus recovery review · 22 November 2026

Durable Start/Recover must install usable timer controls before fallible Dashboard reads. A failed read must invalidate cached recovery actions; confirmations belong to the currently visible warning and must cancel on navigation or recovery. Periodic save failures need a persistent visible action even while another page is open. Backup validation must accept the same name domain as the original CRUD API and require bounded integer revisions with overflow-safe advancement. At the implementation review, focus changes were unreleased and v0.16.0 used schema 9. PR #34 is now merged; v0.17.0 publishes schema 10.

Independent Sol medium review resolved its findings. Local Linux/Docker verification passed 279 unit tests (two platform skips) and all 17 GUI scripts, including forced GUI termination and fresh-process focus recovery. Native hardware/manual Windows acceptance remains separate; hosted PR checks must be read for their own result.

## Scheduled backups review · 22 November 2026

Keep a machine's backup consent/folder out of exported study data. Separate editable-plan identity from automatic success receipts so background completion cannot authorize stale controls or invalidate valid drafts. Treat another helper's lease as temporary busy. Keep runtime failures separate from form-load notices, and show blocked Close without navigating away or cancelling an import preview. Validate canonical paths and bounded UTF-8 receipts before snapshot publication; invalid sidecars must never prevent startup or enable automation. PR #36 is merged; this feature is released in v0.18.0 with schema 10.

## Astra main review fixes · 22 November 2026

The Astra 6.2 low-effort review of main/v0.18.0 identified three P2 issues and one P3 issue. Track them with stable IDs A62-01 through A62-04 in [Review findings](REVIEW_FINDINGS.md), initially committed Open before implementation. Keep the tracker after resolution as evidence; mark fixes verified on their branch separately from merge/release status. Compare editable source snapshots atomically, keep changed-delete warnings beside Confirm, preserve same-subject editor identities and unavailable topic IDs, and reconcile background backup success across windows without another write.

## Dashboard redesign review · 25 November 2026

Dashboard Step 2 groups study actions and keeps subjects/search below them, with a compact metrics summary and explicit sidebar selection. Viewport dimensions and title wrap lengths must be converted from native pixels to CTk logical units inside the scrolling adapter. Bounds checks must use the real viewport. Set simulated DPI before constructing widgets in fresh processes: live CTk 5.2.2 scaling can re-grid hidden pages. Re-review found no blockers; 308 unit tests (two skips) and all 18 container GUI scripts passed, including four-language 100/150% startup recovery/retry checks. Native platform/live-DPI acceptance is separate.

## Practice redesign review · 25 November 2026

CTkFrame.bind forwards Configure to its canvas: widget-local resize callbacks must not reject those events by comparing event.widget with the wrapper. Apply logical-unit conversion before CTk wrap lengths. Render running answer highlights from committed snapshots, restore them after write failure, and guard row/label/radio events with both current page and run visibility; checked radio contrast must be audited against the selected surface. Verify native drawing/text event targets in tests, not only direct callbacks. Progress counts saved answers, never correctness.

## 2026-11-25 · Flashcard retry

Keep rating-write failure separate from postcommit read failure. Preserve revealed content for a failed write; after a successful write, disable old rating controls and retry only the next-card read. Put retry feedback beside long-answer rating controls and use localized action names.

## 2026-11-25 · Responsive reports and Tutor

Use a stable shared-container width to wrap labels inside equal-width columns. Deriving wrap length from each rounded card width can cause a one-pixel geometry loop during resize. Reflow only when the column mode changes, and keep recovery warnings beside their confirmation controls.

## 2026-11-26 — App logo review

- Tk's Aqua implementation consumes only the first `iconphoto` image; use a 512 px source rather than putting the 16 px Windows titlebar size first. Keep images root-owned and use public CustomTkinter icon methods.
- A Windows executable already has PyInstaller's default icon. Verify branded artwork by comparing embedded RT_ICON payloads against the shipped ICO, rather than testing icon presence alone.
- New runtime artwork must be included in the restrictive Docker context and frozen build datas. Keep sidebar image labels on the navigation palette so shared appearance checks remain valid.

## 2026-11-26 — Cat brand, AI drafting and real-model evaluation (v0.29.0–v0.30.1)

- **Brand palette and contrast.** The brand lavender `#9884D6` gives white text only about 3.2:1. Buttons use a deeper `#6E5ABF`, and the brand colour is kept for outlines. Every decorative image label needs a readable `text_color` because the live audit inspects all mapped labels.
- **Compact layout has little vertical slack.** The 1024 × 700 Finish-visibility check failed when a banner image was added. Decorative scenes appear only in the wide layout, and sidebar art is gridded only when its weighted row can hold it whole.
- **Startup cost is a tested constraint.** Fresh-process layout probes in CI have 7-second bounds. Two extra panels built at startup made them time out. Build optional panels such as the AI drafting panels on first use.
- **Real-model testing finds what fixtures cannot.** A 4B model marked the wrong answer letter in 3 of 22 questions and followed instructions injected into notes. Never let the model choose the answer letter. Fence notes as data and repeat the task after them. Show weak-support drafts unticked rather than rejecting them. Re-run `tools/evaluate_ai.py` after any prompt or schema change.
- **Container runs need `--init`.** Without it, `xvfb-run` hangs before the check starts. Bound single-script runs with `timeout`.
- **Parallel tool calls.** Calls in one step run in no fixed order, so never build and edit in the same step and trust the result. Re-run after the edit has landed.
