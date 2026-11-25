# Bright UI Step 5 Settings/data evidence and handoff

Internal implementation record, **25 November 2026**, branch `feature/bright-ui-settings-data`. Implements the **Settings and shared backup/import portion of [Step 5](../../BRIGHT_UI_REDESIGN.md)** only. Published labels remain **v0.23.0 / schema 10**; this portion is unreleased pending its PR and merge authorization.

## Implemented

Settings groups Study and Interface into two cards at 950 logical pixels, otherwise stacked. AI settings occupy a full-width card. Fields and canonical choices retain their original identities. `set_status` mirrors existing Save/Reload feedback in the header and beside the responsive actions. The footer comes before the separate daily schedule and backup/restore cards. Only the new Interface caption adds a catalog key, translated in all four languages.

BackupPanel, ScheduledBackups and both CsvImportPanel instances use paired theme cards with an inset content frame. Logical-unit label wrapping is left aligned. Three-action groups use three columns from 850 logical pixels and two below; existing command/state references are retained. Restore confirmation is an inset warning above the destructive Confirm and Cancel actions. CSV details/errors have theme borders and retain nested scrolling. `panel_layout.py` contains widget-local wrapping/reflow only, using shared source widths and guarded updates, with no I/O or persistent state.

Operation methods, validations, stale snapshots, explicit Save/Reload, active timer target, schedule consent, preview identity, atomic writes, backup safety copy/restore closure and isolated worker processes remain. Resizing performs no preference reads and does not recreate fields or previews. No schema/dependency change, automatic networking or sample data in normal databases.

## Captures and reproduction

The disposable fixture and frozen clock follow earlier captures: Computer Science, two questions, one completed practice attempt, a 25-minute session and a due two-card deck. A standalone copy is validated for restore preview, then cancelled. Header-only CSV formats are populated with one explicit synthetic row for each preview. Neither Confirm restore nor Import all is invoked. Schedules remain opt-in and unsaved; no normal user data or destination is touched.

Baseline uses the retained v0.22.0 container. Settings/backup/schedule/CSV source is unchanged between it and v0.23.0; the baseline footer therefore shows v0.22.0, while new captures show v0.23.0. The new capture utility runs against each runtime with the same fixture. These are Linux/Xvfb UI artifacts, not native hardware or student outcome evidence.

| View | Previous Light | New Light | New Dark | Compact Russian |
| --- | --- | --- | --- | --- |
| Settings groups | [Before](before-light/settings.png) | [Light](wide-light/settings.png) | [Dark](wide-dark/settings.png) | [Russian](compact-russian/settings.png) |
| AI preferences | [Before](before-light/settings-ai.png) | [Light](wide-light/settings-ai.png) | [Dark](wide-dark/settings-ai.png) | [Russian](compact-russian/settings-ai.png) |
| Save/Reload feedback area | [Before](before-light/settings-actions.png) | [Light](wide-light/settings-actions.png) | [Dark](wide-dark/settings-actions.png) | [Russian](compact-russian/settings-actions.png) |
| Daily local schedule | [Before](before-light/backup-schedule.png) | [Light](wide-light/backup-schedule.png) | [Dark](wide-dark/backup-schedule.png) | [Russian](compact-russian/backup-schedule.png) |
| Validated restore warning | [Before](before-light/restore-preview.png) | [Light](wide-light/restore-preview.png) | [Dark](wide-dark/restore-preview.png) | [Russian](compact-russian/restore-preview.png) |
| Question CSV preview | [Before](before-light/question-import.png) | [Light](wide-light/question-import.png) | [Dark](wide-dark/question-import.png) | [Russian](compact-russian/question-import.png) |
| Flashcard CSV preview | [Before](before-light/flashcard-import.png) | [Light](wide-light/flashcard-import.png) | [Dark](wide-dark/flashcard-import.png) | [Russian](compact-russian/flashcard-import.png) |

Use the [Step 1 Docker capture command](../bright-ui-step1/README.md#reproduce-captures-without-host-windows), adding `--data-views` after the output argument. Add `--mode Dark`, or `--size compact --language Russian`. Capture modes are mutually exclusive. Use unique container/output names and copy `container:/tmp/design-capture/.` into an already created destination. Metadata records options/runtime. No host display/data mount or retained fixture database. Historical baseline requires its earlier runtime.

## Validation and review

- macOS headless unit suite: **308 passed**. Full Docker/Xvfb and hosted CI results are recorded on the PR; they must be inspected separately.
- Existing Settings, appearance, backup/restore, schedule and both CSV checks exercise persistence, stale conflicts, retained drafts, active timer safety, no auto-connection, worker errors/retry, atomic import, postcommit refresh, restore guards/safety copy/closure, pagination and fresh-process reopening.
- New `check_data_layout.py` is the **21st bounded GUI script** in the shared runner. Four languages at 100/150% startup scaling passed real compact/wide resizing without preference reads, stable field/snapshot identities, active timer target, failed Save and Reload confirmation feedback beside controls, retained schedule draft, actual validated backup/cancel and visible warning/actions, and both worker-read CSV previews with stable preview identity and question editor/deck search drafts.
- Preview waits handle already-finished jobs and are bounded. The previous test wait race was fixed in the probe; it did not require changing production worker code. Each script retains its 60-second limit.
- Independent Sol medium review found no production blockers; unused import removed and requested real viewport/identity coverage added. Final review includes the probe and capture utility.
- All **28 captures** visually inspected. Syntax, documentation/artifact links, catalog parity, baseline source equivalence and diff checks are checked before commit.

After merge, Step 5 implementation is complete. Next only when requested: **Step 6 regression checks, manual platform acceptance and teacher demo preparation**. Native Windows hardware/DPI, macOS trackpad/Quit and real Ollama quality remain separate recorded acceptance; automated Linux checks do not establish those outcomes. No manual checklist is marked passed here.
