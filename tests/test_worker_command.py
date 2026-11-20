"""Source/frozen helper launch arguments preserve isolation, paths and Unicode."""
import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'soskuska'))
from worker_command import worker_command


class WorkerLaunchTests(unittest.TestCase):
    def test_source_command_keeps_unicode_spaces_and_leading_hyphen_name_separate(self):
        with patch.object(sys,'frozen',False,create=True):
            command=worker_command('questions','parse',Path('/tmp/a b.sqlite3'),'файл.csv','--subject-name=--Русский')
        self.assertEqual(command[:2],[sys.executable,'-u'])
        self.assertEqual(Path(command[2]).name,'csv_import_worker.py')
        self.assertEqual(command[3:],['parse',str(Path('/tmp/a b.sqlite3')),'файл.csv','--subject-name=--Русский'])

    def test_frozen_commands_use_sibling_helper_not_python_or_script_path(self):
        with patch.object(sys,'frozen',True,create=True),patch.object(sys,'executable','/tmp/portable folder/SOSkuska.exe'),patch.object(sys,'platform','win32'):
            for kind in ('backup','questions','flashcards'):
                self.assertEqual(worker_command(kind,'template','active','out'),
                    [str(Path('/tmp/portable folder/SOSkuska.exe').with_name('SOSkuska-worker.exe')),kind,'template','active','out'])

    def test_worker_dispatch_stays_headless(self):
        code="import sys; import worker_entry; assert 'tkinter' not in sys.modules; assert 'customtkinter' not in sys.modules"
        subprocess.run([sys.executable,'-c',code],cwd=Path(__file__).resolve().parents[1]/'soskuska',check=True,timeout=10)

    def test_dispatch_routes_each_worker_protocol_without_gui(self):
        entry=Path(__file__).resolve().parents[1]/'soskuska/worker_entry.py'
        import json
        with tempfile.TemporaryDirectory() as folder:
            for kind in ('questions','flashcards'):
                target=Path(folder)/(kind+'.csv')
                result=subprocess.run([sys.executable,str(entry),kind,'template',str(Path(folder)/'active.db'),str(target)],capture_output=True,check=True,timeout=10)
                self.assertEqual(json.loads(result.stdout)['state'],'done')
                self.assertTrue(target.is_file())
            result=subprocess.run([sys.executable,str(entry),'backup','validate',str(Path(folder)/'active.db'),str(Path(folder)/'missing.db')],capture_output=True,check=True,timeout=10)
            self.assertEqual(json.loads(result.stdout)[0],'error')


if __name__=='__main__':unittest.main()
