"""Exercise the extracted frozen Windows bundle with disposable Unicode paths."""
import argparse
import ctypes
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'soskuska'))
from storage import Store, SCHEMA_VERSION
from preferences import DEFAULTS


def visible_window(pid):
    from ctypes import wintypes
    user = ctypes.WinDLL('user32', use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user.IsWindowVisible.argtypes = [wintypes.HWND]
    user.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    found = []
    def visit(hwnd, _):
        owner = wintypes.DWORD()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        title = ctypes.create_unicode_buffer(256)
        user.GetWindowTextW(hwnd, title, 256)
        if owner.value == pid and user.IsWindowVisible(hwnd) and title.value == 'SOSkúška':
            found.append(hwnd)
        return True
    user.EnumWindows(callback_type(visit), 0)
    return found[0] if found else None


def check_window(exe, database, cwd, env):
    from ctypes import wintypes
    process = subprocess.Popen([str(exe), '--data', str(database)], cwd=cwd, env=env,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic()+30
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise AssertionError(f'Frozen app exited before opening its window: {process.returncode}')
            hwnd = visible_window(process.pid)
            if hwnd:
                break
            time.sleep(.2)
        else:
            raise AssertionError('Frozen app did not open its Dashboard in 30 seconds.')
        # Let after callbacks and layout run before requesting the normal close path.
        time.sleep(1)
        user = ctypes.WinDLL('user32', use_last_error=True)
        user.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        if not user.PostMessageW(hwnd, 0x0010, 0, 0):
            raise ctypes.WinError(ctypes.get_last_error())
        assert process.wait(timeout=20) == 0, 'Frozen GUI failed while closing.'
    finally:
        if process.poll() is None:
            process.kill(); process.wait(timeout=10)


def main():
    if sys.platform != 'win32':
        raise SystemExit('This check must run on Windows; it does not emulate manual Windows testing.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory(prefix='SOSkuska проверка ') as folder:
        folder = Path(folder)
        # Test the actual distributed ZIP, not the original build tree.
        shutil.unpack_archive(str(args.archive.resolve()), str(folder/'extracted'))
        bundle = folder/'extracted/SOSkuska'
        app, worker = bundle/'SOSkuska.exe', bundle/'SOSkuska-worker.exe'
        assert app.is_file() and worker.is_file()
        cwd = folder/'another working directory'; cwd.mkdir()
        env = dict(os.environ)
        env.pop('PYTHONPATH', None); env.pop('PYTHONHOME', None)
        # No installed Python or tools may be discovered via PATH by either EXE.
        env['PATH'] = str(Path(env['SystemRoot'])/'System32')
        database = folder/'данные skúška.sqlite3'
        check_window(app, database, cwd, env)
        with sqlite3.connect(database) as db:
            assert db.execute('PRAGMA user_version').fetchone()[0] == SCHEMA_VERSION
            assert db.execute('SELECT COUNT(*) FROM subjects').fetchone()[0] == 0
        results.append('Empty startup/normal close from extracted ZIP without Python on PATH')
        store = Store(database)
        try:
            sid = store.create_subject('--Математика skúška')
            did = store.create_deck(sid, '--Kartičky русский')
            store.create_question(sid, 'Saved original?', ['one','two','three','four'], 1)
        finally:
            store.close()
        def job(kind, *arguments):
            reply = subprocess.run([str(worker),kind,*(str(arg) for arg in arguments)], cwd=cwd,
                env=env, capture_output=True, check=True, timeout=45)
            return json.loads(reply.stdout.decode('utf-8'))
        for kind, headers, row, identity in (
            ('questions', 'prompt,option_a,option_b,option_c,option_d,correct_option,difficulty\n',
                'Русский вопрос?,a,b,c,d,B,Easy\n', ('--subject-id',sid,'--subject-name=--Математика skúška')),
            ('flashcards', 'front,back\n', 'Česká otázka,Русский ответ\n',
                ('--deck-id',did,'--deck-name=--Kartičky русский')),
        ):
            template = folder/(kind+' template.csv')
            assert job(kind,'template',database,template)['state']=='done'
            source = folder/(kind+' Unicode.csv'); source.write_text(headers+row,encoding='utf-8')
            parsed = job(kind,'parse',database,source,*identity)
            assert parsed['state']=='done' and not parsed['value']['errors'],parsed
            payload = folder/(kind+' payload.json')
            payload.write_text(json.dumps(parsed['value']['rows'],ensure_ascii=False),encoding='utf-8')
            assert job(kind,'save',database,payload,*identity)['state']=='done'
            results.append(kind+' bundled helper: template, Unicode preview and atomic import')
        backup = folder/'backup copy.sqlite3'; staged = folder/'validated.sqlite3'
        assert job('backup','backup',database,backup)[0]=='done'
        assert job('backup','validate',database,backup,'--staging',staged)[0]=='done'
        store=Store(database)
        try:
            store.create_subject('Temporary extra')
        finally:store.close()
        assert job('backup','restore',database,staged)[0]=='done'
        store=Store(database)
        try:
            assert len(store.subjects())==1
            assert len(store.questions(sid))==2 and len(store.flashcards(did))==1
        finally:store.close()
        results.append('Bundled backup, validation, restore and retained imported data')
        for language in ('English','Czech','Slovak','Russian'):
            store=Store(database)
            try:
                saved=store.preferences()
                store.save_preferences(dict(DEFAULTS,ui_language=language),expected_revision=saved['revision'])
            finally:store.close()
            check_window(app,database,cwd,env)
            results.append(language+' frozen startup and normal close with bundled catalogs/fonts')
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps({'platform':sys.platform,'automated_checks':results,
        'manual_clean_machine_status':'NOT RUN: hosted automated checks do not establish manual acceptance'},indent=2)+'\n',encoding='utf-8')
    print('PASS: extracted Windows bundle startup, all catalogs, isolated helpers/imports/backup/restore and fresh-process persistence')


if __name__ == '__main__':
    main()
