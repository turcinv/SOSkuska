# Focus-session recovery

[English](FOCUS_RECOVERY.md) · [Čeština](cs/FOCUS_RECOVERY.md) · [Slovenčina](sk/FOCUS_RECOVERY.md) · [Русский](ru/FOCUS_RECOVERY.md)

This branch adds focus recovery to the published v0.16.0 baseline. It is unreleased and uses schema **10**. Keep a backup before opening existing data: migration is transactional, but v0.16.0 cannot open a schema-10 database.

Start Studying creates a pending focus record before the timer starts. The app checkpoints whole elapsed seconds about every five seconds while running and immediately on Pause. It stores the original subject name, target and verified elapsed time. It does not store a monotonic clock value for reuse after restarting.

After a crash or forced termination, Dashboard offers **Recover paused**, **Discard checkpoint** and **Refresh**. Recovery always starts paused, preserves the original target even if Settings changed, and never counts time while the app was closed. Resume continues the timer; Finish saves the recovered time. Pending time is excluded from Statistics until completion. Discard requires a second confirmation and adds no study history. Navigation, Escape, Refresh and Recover cancel a pending discard confirmation. A failed read disables stale actions until Refresh succeeds.

A separate persistent `.focus.lock` file gives one window exclusive ownership. Another open window may display its checkpoint but cannot recover or discard it while the owner is alive. Refresh after the owner closes. Never delete lock files manually. Process termination releases the operating-system lock.

Checkpoint writes wait at most about 200 ms for SQLite contention. A failed checkpoint or Finish pauses the timer, disables Resume and retains elapsed time in memory. Use **Finish** to retry. The timer shows instructions and the sidebar shows **Focus needs saving** on other pages; selecting it opens Dashboard. A failed close stays open on Dashboard. Closing normally saves elapsed time; do not force-close if saving has failed.

Completion inserts a study session and marks the focus run completed in one transaction; retry cannot create a second session. Zero seconds creates no statistics row. Time belongs to the local calendar day of completion, including a recovered session. Sessions are not split at midnight. Subject rename/deletion preserves the original historical name; deletion clears only its live reference.

Backups include committed pending checkpoints and completed/discarded records, but omit elapsed time since the last checkpoint and unsaved drafts. Restore requires resolving the target database's pending focus first. Restoring a valid schema-10 backup containing a pending checkpoint offers recovery on the next launch. Restore accepts only standalone schema-10 snapshots; it does not migrate old backups. To export an older database, first open a separate copy in this version and create a new backup.

Abrupt termination can lose roughly the last five seconds plus a fractional second since the latest checkpoint; event-loop delays or a failed write may increase that gap. This is process-crash recovery, not a power-loss durability guarantee, synchronization or continuous backup.

Development and verification: use the existing [developer setup](DEVELOPMENT.md), an isolated `--data .local-data/dev.sqlite3` database and [container checks](CONTAINER_TESTS.md). `tests/test_focus.py` covers migration/rollback, stale ownership, process death, atomic/idempotent completion and backup round trips. `check_focus_recovery.py` kills a disposable GUI process and verifies paused recovery in fresh processes, failed reads/saves, confirmation cancellation and normal close. Windows CI also opens/closes the extracted portable app with a pending checkpoint. Linux/Xvfb checks do not establish native macOS or manual Windows hardware acceptance.
