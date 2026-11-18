# Backup and restore

[English](BACKUP_RESTORE.md) · [Čeština](cs/BACKUP_RESTORE.md) · [Slovenčina](sk/BACKUP_RESTORE.md) · [Русский](ru/BACKUP_RESTORE.md)

## Create a backup

Open **Settings → Backup and restore → Create backup**, choose a local folder and an unused `.sqlite3` filename, then wait for completion. Existing files are never overwritten. The app remains usable while copying. Normal close/Quit waits for the job to finish.

The SQLite snapshot contains saved subjects, topics/questions, checklist, focus sessions, practice attempts/answers, decks/cards/review history and preferences. It includes committed data from WAL mode, but not uncommitted edits, unsaved focus time, form drafts or session-only AI chat. Finish focus and save forms first if you need those changes included. The exported backup is a standalone file in DELETE journal mode, not a raw copy of a live database.

## Restore a backup

1. Finish the current focus session and finish/discard any current practice test. Wait for or stop AI generation. Save needed drafts and copy any AI chat you want to keep.
2. Close other SOSkúška windows using this database, older app versions and external SQLite tools. Current versions enforce shared/exclusive database leases; external tools and old versions do not participate in those leases.
3. In Settings, choose **Choose backup…** and select a regular local standalone schema **6** SQLite file. WAL-mode working files, unrelated, corrupt, invalid, older and newer schemas are rejected. Use Create backup to export a WAL database first.
4. Validation checks integrity, expected structure, constraints, application value types/dates/timestamps, practice consistency and record references in a private copy. Inspect the displayed filename and counts. **Cancel** or navigation discards the selection without changing saved data. Changing the source file afterward does not change the validated selection.
5. **Confirm restore and close** replaces all saved data and preferences. Existing form drafts and in-memory AI chat will be lost. State guards run again at confirmation. During restore, editing is blocked and periodic database callbacks pause.
6. A safety copy of current committed data is created under `backups/` next to the active database before replacement. Its name is `SOSkuska-before-restore-<date>-<unique-id>.sqlite3`; the success message shows its exact path. Restore is one SQLite transaction, preserves ID sequences, checks final data against the validated copy, and rolls back on pre-commit failure. If safety-copy creation fails, data is not replaced.
7. The app closes after an actual restore attempt, including failure. Reopen using the same `--data` path (or the same ordinary launch) to load the resulting database. A backup may contain an unfinished practice test, which can resume after reopening. Any safety copy already created remains available if a later step fails; restore it through the same workflow when needed.

## Scope and limitations

This is manual local backup, not synchronization, scheduled backup, encryption or complete crash/power-loss recovery. Keep copies somewhere safe; they contain private study data and saved AI connection preferences. Normal study stays offline and no cloud service is used.

The schema stays 6; only schema 6 snapshots are supported by this first restore implementation. There is no downgrade or automatic migration during restore. Hard-linked active databases are rejected to keep locking reliable. Active database/companion paths, including case/Unicode aliases, cannot be used as backup outputs.

On macOS/Linux, atomic no-overwrite publication requires a filesystem supporting hard links (such as the usual local APFS/ext4 volumes); use a supported local folder if an external drive rejects publication. Windows uses its no-overwrite rename behavior. Database jobs run in helper processes, with a 60-second operation budget and a 90-second process safeguard. Avoid network paths and do not force-quit during a job. If a helper stops unexpectedly, reopen and inspect the database and safety copies instead of assuming the restore failed before commit.
