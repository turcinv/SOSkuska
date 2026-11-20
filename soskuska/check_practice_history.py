"""Native paged history workflow using disposable data; no network or normal user DB."""
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch
import customtkinter as ctk
from app import Dashboard
from storage import Store


def widgets(root):
    for child in root.winfo_children():
        yield child
        yield from widgets(child)


def run(path, reopen=False):
    if not reopen:
        store=Store(path)
        try:
            sid=store.create_subject('Settings')
            store.create_question(sid,'Original prompt',['one','two','three','four'],1,explanation='Original explanation')
            for i in range(45):
                aid=store.start_practice(sid,1);store.save_practice_answer(aid,0,1);store.complete_practice(aid)
                store.db.execute('UPDATE practice_attempts SET completed_at=? WHERE id=?',
                    (datetime(2026,11,10 if i<25 else 11,12).astimezone(timezone.utc).isoformat(),aid));store.db.commit()
            store.delete_subject(sid)
            sid=store.create_subject('All subjects')
            store.create_question(sid,'Live prompt',['a','b','c','d'],0)
            aid=store.start_practice(sid,1);store.complete_practice(aid)
        finally:store.close()
    if reopen:
        app=Dashboard(path)
    else:
        with patch.object(Store,'practice_history_page',side_effect=sqlite3.OperationalError('locked on first load')):
            app=Dashboard(path)
    page=app.practice_page;errors=[]
    def labels(): return [w.cget('text') for w in widgets(page.results) if isinstance(w,ctk.CTkLabel)]
    def guarded(callback):
        def wrapped():
            try:callback()
            except Exception as exc:errors.append(str(exc));traceback.print_exc();app.destroy()
        return wrapped
    def initial():
        assert page.history_previous.cget('state')=='disabled' and page.history_next.cget('state')=='disabled'
        page.history_apply.invoke()
        assert '46 completed tests' in page.history_status.cget('text')
        app.geometry('1024x700');app.navigate('Practice Tests');app.update_idletasks()
        assert page.history_page==0 and len(page.history.winfo_children())==20
        assert '46 completed tests' in page.history_status.cget('text')
        page.history_next.invoke();page.history_next.invoke()
        assert page.history_page==2 and len(page.history.winfo_children())==6
        assert page.history_next.cget('state')=='disabled'
        # Open an older retained result and return to the same page.
        button=next(w for w in widgets(page.history) if isinstance(w,ctk.CTkButton))
        button.invoke();app.update_idletasks()
        assert page.results.winfo_ismapped()
        assert any('Original prompt' in str(t) for t in labels())
        assert any('Original explanation' in str(t) for t in labels())
        page.show_config();assert page.history_page==2
        page.history_subject.set('Subject: Settings');page.history_apply.invoke()
        assert page.history_filters==('Settings','','') and page.history_page==0
        assert '45 completed tests' in page.history_status.cget('text')
        # Date filters apply only on Apply; navigation and paging preserve drafts.
        page.history_date_entries[0].insert(0,'2026-11-10')
        page.history_date_entries[1].insert(0,'2026-11-10')
        page.history_next.invoke();assert page.history_page==1 and page.history_filters[1]==''
        app.navigate('Dashboard');app.navigate('Practice Tests')
        assert page.history_page==1 and page.history_date_entries[1].get()=='2026-11-10'
        page.history_apply.invoke();assert page.history_page==0
        assert '25 completed tests' in page.history_status.cget('text')
        # Preserve visible results, applied filters and page on invalid/failed reads.
        page.history_next.invoke();before=list(page.history.winfo_children());old=page.history_filters
        page.history_date_entries[0].delete(0,'end');page.history_date_entries[0].insert(0,'bad date')
        page.history_apply.invoke()
        assert list(page.history.winfo_children())==before and page.history_page==1 and page.history_filters==old
        assert 'YYYY-MM-DD' in page.history_status.cget('text')
        with patch.object(app.store,'practice_history_page',side_effect=sqlite3.OperationalError('locked')):
            page.history_previous.invoke()
        assert list(page.history.winfo_children())==before and page.history_page==1
        assert 'Previous results are kept' in page.history_status.cget('text')
        page.history_previous.invoke();assert page.history_page==0
        page.history_reset.invoke();assert page.history_filters==(None,'','')
        assert all(not entry.get() for entry in page.history_date_entries)
        page.history_subject.set('Subject: All subjects');page.history_apply.invoke()
        assert '1 completed tests' in page.history_status.cget('text')
        page.history_date_entries[0].insert(0,'2099-01-01');page.history_apply.invoke()
        assert len(page.history.winfo_children())==1 and page.history_next.cget('state')=='disabled'
        page.history_reset.invoke()
        # Reviewing old history must not answer/complete an unfinished attempt.
        sid=app.store.subjects()[0]['id'];aid=app.store.start_practice(sid,1)
        page.load();app.update_idletasks();assert page.history_button.winfo_ismapped()
        page.history_button.invoke();app.update_idletasks()
        assert page.setup.winfo_ismapped()
        next(w for w in widgets(page.history) if isinstance(w,ctk.CTkButton)).invoke()
        assert app.store.active_practice()['id']==aid and app.store.active_practice()['answered']==0
        page.show_config();app.update_idletasks()
        right=app.winfo_rootx()+app.winfo_width()
        for button in (page.history_apply,page.history_reset,page.history_previous,page.history_next):
            assert button.winfo_rootx()+button.winfo_width()<=right
        app.scroll._parent_canvas.yview_moveto(1);app.update_idletasks()
        assert app.scroll._parent_canvas.yview()[0]>0
        app.close()
    def reopened():
        app.navigate('Practice Tests');assert page.active_id is not None
        app.update_idletasks();page.history_button.invoke();assert '46 completed tests' in page.history_status.cget('text')
        page.view_result(1);assert any('Original explanation' in str(t) for t in labels())
        assert app.store.active_practice()['answered']==0
        app.close()
    def callback_error(kind,value,tb):
        errors.append(str(value));traceback.print_exception(kind,value,tb);app.destroy()
    app.report_callback_exception=callback_error
    app.after(700,guarded(reopened if reopen else initial))
    app.after(22000,lambda:(errors.append('Practice history check timed out'),app.destroy()))
    try:app.mainloop()
    finally:app.store.close()
    assert not errors,errors


if __name__=='__main__':
    ctk.set_appearance_mode('dark')
    if len(sys.argv)>1:run(Path(sys.argv[1]),reopen=True)
    else:
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'history.db';run(path)
            subprocess.run([sys.executable,'-X','faulthandler','-u',str(Path(__file__).resolve()),str(path)],check=True,timeout=30)
        print('PASS: all history pages, subject/date filters, snapshots after deletion, result return, kept drafts, invalid/read failure retry, active attempt isolation, compact scrolling and fresh-process history',flush=True)
