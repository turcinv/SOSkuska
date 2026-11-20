# Build on the target OS; one-folder app plus console JSON helper share resources.
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

root = Path(SPECPATH).parent
sources = root / 'soskuska'
data = collect_data_files('customtkinter') + [(str(sources / 'i18n'), 'i18n')]
app = Analysis([str(sources / 'app.py')], pathex=[str(sources)], datas=data)
helper = Analysis([str(sources / 'worker_entry.py')], pathex=[str(sources)])
main_exe = EXE(PYZ(app.pure), app.scripts, [], exclude_binaries=True,
    name='SOSkuska', console=False, debug=False, strip=False, upx=False)
worker_exe = EXE(PYZ(helper.pure), helper.scripts, [], exclude_binaries=True,
    name='SOSkuska-worker', console=True, debug=False, strip=False, upx=False)
COLLECT(main_exe, worker_exe, app.binaries, app.datas, helper.binaries, helper.datas,
    name='SOSkuska', strip=False, upx=False)
