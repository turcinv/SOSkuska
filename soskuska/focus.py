"""Durable monotonic-time checkpoints with a cooperative exclusive focus lease."""
import uuid
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from database_lock import DatabaseLease
from practice import utc_now


MAX_FOCUS_REVISION = 2**63-1


def next_revision(value):
    # Bounded integers keep even imported boundary values usable. Ownership is
    # also checked with the exclusive process lease and immutable run ID.
    if type(value) is not int or not 0<=value<=MAX_FOCUS_REVISION:
        raise FocusStateError("Refresh recovery before continuing.")
    return (value+1) % (MAX_FOCUS_REVISION+1)


class FocusStateError(ValueError):
    """A stale checkpoint cannot be resumed, changed or finalized."""


class FocusStoreMixin:
    @contextmanager
    def _focus_timeout(self):
        # Checkpoint contention must pause safely rather than stall Tk for seconds.
        previous=self.db.execute('PRAGMA busy_timeout').fetchone()[0]
        self.db.execute('PRAGMA busy_timeout=200')
        try:
            yield
        finally:self.db.execute(f'PRAGMA busy_timeout={previous}')

    @contextmanager
    def _focus_transaction(self):
        with self._focus_timeout(),self.db:
            yield

    def pending_focus(self):
        with self._focus_timeout():
            row=self.db.execute("SELECT * FROM focus_runs WHERE status='pending'").fetchone()
        return dict(row) if row else None

    def _focus_lock(self):
        return DatabaseLease(Path(str(self.path)+'.focus'),exclusive=True)

    def release_focus(self):
        lease=getattr(self,'_focus_lease',None)
        self._focus_lease=None;self._focus_id=None;self._focus_revision=None
        if lease is not None:lease.close()

    def _own_focus(self,run_id):
        if getattr(self,'_focus_id',None)!=run_id or getattr(self,'_focus_lease',None) is None:
            raise FocusStateError('This window does not own the focus session. Refresh recovery.')
        row=self.db.execute('SELECT * FROM focus_runs WHERE id=?',(run_id,)).fetchone()
        if row is None or row['status']!='pending' or row['revision']!=self._focus_revision:
            raise FocusStateError('Saved focus session changed. Refresh recovery.')
        return dict(row)

    @staticmethod
    def _elapsed(row,seconds):
        if type(seconds) is not int or not row['elapsed_seconds']<=seconds<=row['target_seconds']:
            raise ValueError('Focus time must be whole seconds between the saved checkpoint and target.')

    def start_focus_checkpoint(self,subject_id,target_seconds):
        if type(target_seconds) is not int or not 1<=target_seconds<=10800:
            raise ValueError('Focus duration must be between 1 and 10,800 seconds.')
        if getattr(self,'_focus_lease',None) is not None:
            raise FocusStateError('A focus session is already owned by this window.')
        lease=self._focus_lock()
        try:
            with self._focus_transaction():
                self.db.execute('BEGIN IMMEDIATE')
                if self.pending_focus() is not None:
                    raise FocusStateError('Recover or discard the saved focus session before starting another.')
                subject=self.subject(subject_id)
                if subject is None:raise ValueError('Choose an existing subject.')
                now=utc_now().isoformat();run_id=uuid.uuid4().hex
                self.db.execute("""INSERT INTO focus_runs(id,subject_id,subject_name,target_seconds,elapsed_seconds,status,revision,started_at,updated_at)
                    VALUES (?,?,?,?,0,'pending',0,?,?)""",(run_id,subject_id,subject['name'],target_seconds,now,now))
            self._focus_lease=lease;self._focus_id=run_id;self._focus_revision=0
        except BaseException:
            lease.close();raise
        return dict(id=run_id,subject_id=subject_id,subject_name=subject['name'],target_seconds=target_seconds,elapsed_seconds=0,revision=0)

    def claim_focus_checkpoint(self,run_id,expected_revision):
        if type(expected_revision) is not int or expected_revision<0:
            raise FocusStateError('Refresh recovery before continuing.')
        if getattr(self,'_focus_lease',None) is not None:
            raise FocusStateError('A focus session is already owned by this window.')
        lease=self._focus_lock()
        try:
            with self._focus_transaction():
                self.db.execute('BEGIN IMMEDIATE')
                row=self.pending_focus()
                if row is None or row['id']!=run_id or row['revision']!=expected_revision:
                    raise FocusStateError('Saved focus session changed. Refresh recovery.')
                revision=next_revision(row['revision'])
                self.db.execute('UPDATE focus_runs SET revision=? WHERE id=?',(revision,run_id))
            self._focus_lease=lease;self._focus_id=run_id;self._focus_revision=revision
        except BaseException:
            lease.close();raise
        return dict(row,revision=revision)

    def checkpoint_focus(self,run_id,seconds):
        with self._focus_transaction():
            self.db.execute('BEGIN IMMEDIATE')
            row=self._own_focus(run_id);self._elapsed(row,seconds)
            revision=next_revision(row['revision'])
            self.db.execute('UPDATE focus_runs SET elapsed_seconds=?,revision=?,updated_at=? WHERE id=?',
                (seconds,revision,utc_now().isoformat(),run_id))
        self._focus_revision=revision

    def finish_focus_checkpoint(self,run_id,seconds):
        with self._focus_transaction():
            self.db.execute('BEGIN IMMEDIATE')
            row=self.db.execute('SELECT * FROM focus_runs WHERE id=?',(run_id,)).fetchone()
            if row is not None and row['status']=='completed':
                # A retry after an uncertain commit must never add another session.
                result=dict(seconds=row['elapsed_seconds'],session_id=row['session_id'])
            else:
                row=self._own_focus(run_id);self._elapsed(row,seconds)
                session_id=None
                if seconds:
                    session_id=self.db.execute('INSERT INTO sessions(day,seconds,subject_id,subject_name) VALUES (?,?,?,?)',
                        (date.today().isoformat(),seconds,row['subject_id'],row['subject_name'])).lastrowid
                now=utc_now().isoformat()
                self.db.execute("UPDATE focus_runs SET elapsed_seconds=?,status='completed',revision=?,updated_at=?,completed_at=?,session_id=? WHERE id=?",
                    (seconds,next_revision(row['revision']),now,now,session_id,run_id))
                result=dict(seconds=seconds,session_id=session_id)
        if getattr(self,'_focus_id',None)==run_id:
            try:self.release_focus()
            except OSError:pass  # The finalization is known committed.
        return result

    def discard_focus_checkpoint(self,run_id,expected_revision):
        if type(expected_revision) is not int or expected_revision<0:
            raise FocusStateError('Refresh recovery before continuing.')
        if getattr(self,'_focus_lease',None) is not None:
            raise FocusStateError('Finish the focus session owned by this window before discarding recovery.')
        with self._focus_lock(),self._focus_transaction():
            self.db.execute('BEGIN IMMEDIATE')
            row=self.pending_focus()
            if row is None or row['id']!=run_id or row['revision']!=expected_revision:
                raise FocusStateError('Saved focus session changed. Refresh recovery.')
            now=utc_now().isoformat()
            self.db.execute("UPDATE focus_runs SET status='discarded',revision=?,completed_at=? WHERE id=?",(next_revision(row['revision']),now,run_id))
