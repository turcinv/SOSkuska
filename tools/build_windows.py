"""Build an unsigned Windows x64 portable folder, ZIP and checksum on Windows."""
import hashlib
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.platform != 'win32' or sysconfig.get_platform() != 'win-amd64':
        raise SystemExit('Build this Windows x64 bundle using 64-bit Python on Windows.')
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
        '--distpath', str(ROOT/'dist'), '--workpath', str(ROOT/'build'),
        str(ROOT/'packaging/windows.spec')], cwd=ROOT, check=True, timeout=600)
    bundle = ROOT/'dist/SOSkuska'
    # Include user guides outside the private runtime directory.
    docs = bundle/'docs'
    docs.mkdir(exist_ok=True)
    for language in ('', 'cs', 'sk', 'ru'):
        source = ROOT/'docs'/language
        destination = docs/language
        destination.mkdir(exist_ok=True)
        for name in ('WINDOWS_PORTABLE.md', 'WINDOWS_ACCEPTANCE.md'):
            shutil.copy2(source/name, destination/name)
    archive = Path(shutil.make_archive(str(ROOT/'dist/SOSkuska-windows-x64'), 'zip', ROOT/'dist', 'SOSkuska'))
    with archive.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n', encoding='utf-8')
    print(archive)


if __name__ == '__main__':
    main()
