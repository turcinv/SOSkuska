# Scheduled local backups

[English](SCHEDULED_BACKUPS.md) · [Čeština](cs/SCHEDULED_BACKUPS.md) · [Slovenčina](sk/SCHEDULED_BACKUPS.md) · [Русский](ru/SCHEDULED_BACKUPS.md)

## Unreleased — Settings and shared data panels

Daily backup schedules, manual backup/restore and both CSV importers now use the shared card style, consistent insets and wrapped messages. Action groups use three columns in wide layouts or two in compact ones. Restore warnings appear above the destructive confirmation and Cancel controls. CSV preview/error fields have visible borders and keep their own scrolling. Preview, cancellation, atomic writes, isolated workers, restore closure and safety-copy rules are unchanged.

Scheduled local backups are available in **v0.18.0**. SQLite schema remains **10**. Manual backup/restore continues to work independently.

In Settings, scroll to **Daily local backups**. Choose an existing local folder, enable **Enable daily backups**, then select **Save backup schedule**. This has its own Save/Reload controls; saving the study/AI form does not save the backup schedule. Automation starts only after explicit opt-in. Disabling the saved schedule stops future automatic backups.

The app checks after startup and about once a minute while open. When due, a separate helper creates one backup for the current local day. A closed app does not run jobs; after several days away, it creates one current backup rather than one for each missed day. Changing folders or toggling the setting does not create another backup after a recorded success that day. A clock rollback waits until the calendar advances beyond the last success. Retry backup checks whether a backup is due; use Create backup for an additional manual copy.

The helper snapshots committed SQLite data, including saved focus checkpoints, using the existing consistent, standalone backup format. It excludes unsaved drafts and elapsed time since the last focus checkpoint. Existing files are never overwritten or deleted. Unique filenames start with `SOSkuska-auto-`; manage old copies and free space yourself. These are unencrypted local copies, with no automatic upload or cloud service.

Only one helper may create a daily backup for a database at a time. Another window waits and checks again; a stale plan cannot overwrite newer settings. A background receipt does not invalidate an unrelated settings draft. Reload confirms replacement of an edited draft; failed Save/Reload preserves it. Errors remain visible after navigation. Closing during a job keeps the current page and drafts and shows a notice at the bottom of the window. Wait for completion before closing; normal study can continue.

Failures retry after roughly fifteen minutes; Retry backup requests an earlier due check. Confirm that the folder is available, permissions allow writing and the drive has free space. Filesystem jobs have bounded process timeouts. A crash after a complete snapshot is published but before its success receipt is written can leave an extra valid copy on retry; the app keeps it. This is not a power-loss durability guarantee.

The machine-specific plan and last-success receipt are stored beside the database in `<database>.backup-plan.json`, with an exclusive `<database>.backup-plan.lock`. Writes replace a private temporary file atomically; malformed settings disable automation until explicitly repaired. Do not delete lock files while windows are open. The plan is not inside SQLite exports: restoring a backup on another computer does not opt that computer in. Restoring data in an already configured database keeps that computer's existing plan. Moving/copying only the database to a new path requires opt-in again. No schema migration is needed.

Development: `automatic_backup.py` owns validation, compare-and-swap plan IDs, the success receipt and exclusive lease. `scheduled_backups.py` owns main-thread controls and file-backed helper polling; `backup_worker.py automatic` performs file/database work without Tk. `tests/test_automatic_backup.py` covers persistence, concurrency and failures; `check_scheduled_backups.py` verifies the GUI and fresh-process behavior under the [container suite](CONTAINER_TESTS.md). Windows CI exercises the bundled helper with a Unicode folder. Hosted automation does not replace manual hardware/clean-machine acceptance.

A successful receipt from another window is reconciled on the next check (or Retry backup), clearing the superseded failure notice without starting a duplicate job.
