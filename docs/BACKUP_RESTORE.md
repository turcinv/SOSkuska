# Backup and restore (v0.9.0)

[English](BACKUP_RESTORE.md) · [Čeština](cs/BACKUP_RESTORE.md) · [Slovenčina](sk/BACKUP_RESTORE.md) · [Русский](ru/BACKUP_RESTORE.md)

## v0.24.0 — Settings and shared data panels

Daily backup schedules, manual backup/restore and both CSV importers now use the shared card style, consistent insets and wrapped messages. Action groups use three columns in wide layouts or two in compact ones. Restore warnings appear above the destructive confirmation and Cancel controls. CSV preview/error fields have visible borders and keep their own scrolling. Preview, cancellation, atomic writes, isolated workers, restore closure and safety-copy rules are unchanged.

## Create a backup

Open **Settings → Backup and restore → Create backup**, choose a local folder and an unused `.sqlite3` filename, then wait for completion. Existing files are never overwritten. The app remains usable while copying. Normal close/Quit waits for the job to finish.

The SQLite snapshot contains all saved study data, preferences and local AI conversations. It includes committed WAL data, but excludes uncommitted edits, unsaved focus time, drafts and any reply text not yet saved. Finish focus, save forms and resolve unsaved Tutor replies first. The export is a standalone DELETE-mode database, not a raw copy of a live file.

## Restore a backup

1. Finish focus and finish/discard any practice test. Wait for or stop AI generation, then save needed drafts and resolve unsaved replies through Retry save reply or Discard unsaved.
2. Close other SOSkúška windows using this database, older app versions and external SQLite tools. Current versions enforce shared/exclusive database leases; external tools and old versions do not participate in those leases.
3. In Settings, choose **Choose backup…** and select a regular local standalone schema **10** SQLite file. WAL-mode working files, unrelated, corrupt, invalid, older and newer schemas are rejected. Use Create backup to export a WAL database first.
4. Validation checks integrity, expected structure, constraints, application value types/dates/timestamps, practice consistency and record references in a private copy. Inspect the displayed filename and counts. **Cancel** or navigation discards the selection without changing saved data. Changing the source file afterward does not change the validated selection.
5. **Confirm restore and close** replaces all saved study data, preferences and conversations with the backup. Unsaved forms are lost. Guards are checked again; editing is blocked and periodic database callbacks are paused during restore.
6. A safety copy of current committed data is created under `backups/` next to the active database before replacement. Its name is `SOSkuska-before-restore-<date>-<unique-id>.sqlite3`; the success message shows its exact path. Restore is one SQLite transaction, preserves ID sequences, checks final data against the validated copy, and rolls back on pre-commit failure. If safety-copy creation fails, data is not replaced.
7. The app closes after an actual restore attempt, including failure. Reopen using the same `--data` path (or the same ordinary launch) to load the resulting database. A backup may contain an unfinished practice test, which can resume after reopening. Any safety copy already created remains available if a later step fails; restore it through the same workflow when needed.

## Scope and limitations

This is manual local backup, not synchronization, scheduled backup, encryption or complete crash/power-loss recovery. Keep copies somewhere safe; they contain private study data and saved AI connection preferences. Normal study stays offline and no cloud service is used.

The current schema is 10; only schema 10 snapshots are supported by this first restore implementation. There is no downgrade or automatic migration during restore. Hard-linked active databases are rejected to keep locking reliable. Active database/companion paths, including case/Unicode aliases, cannot be used as backup outputs.

On macOS/Linux, atomic no-overwrite publication requires a filesystem supporting hard links (such as the usual local APFS/ext4 volumes); use a supported local folder if an external drive rejects publication. Windows uses its no-overwrite rename behavior. Database jobs run in helper processes, with a 60-second operation budget and a 90-second process safeguard. Avoid network paths and do not force-quit during a job. If a helper stops unexpectedly, reopen and inspect the database and safety copies instead of assuming the restore failed before commit.

## Saved AI Tutor conversations

AI Tutor now saves conversations locally, including the original server/model and reply status. Open saved history without networking, reconnect explicitly to continue, or delete a selected conversation after confirmation. Released in v0.12.0 with schema 7, which migrates existing study data transactionally. [Saved AI Tutor conversations](TUTOR_HISTORY.md).

## Focus-session recovery

v0.17.0 adds focus-session crash recovery using schema **10**. Keep a backup before opening existing data: migration is transactional, but v0.16.0 cannot open a schema-10 database. [Focus-session recovery](FOCUS_RECOVERY.md).

## Scheduled local backups

Scheduled local backups are available in **v0.18.0**. SQLite schema remains **10**. Manual backup/restore continues to work independently. [Scheduled local backups](SCHEDULED_BACKUPS.md).
