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

Status updated 22 November 2026: the user confirmed v0.15.0 baseline testing complete and approved appearance PR #32. This checklist now targets v0.16.0; item-by-item clean-machine/DPI results are not recorded here. Leave unchecked items unverified and record device-specific evidence when testing the new release. [Next steps · 22 November 2026](NEXT_STEPS.md).

## Focus recovery review · 22 November 2026

Durable Start/Recover must install usable timer controls before fallible Dashboard reads. A failed read must invalidate cached recovery actions; confirmations belong to the currently visible warning and must cancel on navigation or recovery. Periodic save failures need a persistent visible action even while another page is open. Backup validation must accept the same name domain as the original CRUD API and require bounded integer revisions with overflow-safe advancement. Focus changes are unreleased on a feature branch; published v0.16.0 remains schema 9.

Independent Sol medium review resolved its findings. Local Linux/Docker verification passed 279 unit tests (two platform skips) and all 17 GUI scripts, including forced GUI termination and fresh-process focus recovery. Native hardware/manual Windows acceptance remains separate; hosted PR checks must be read for their own result.
