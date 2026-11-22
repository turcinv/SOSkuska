"""Bounded checks for CI or a container virtual display; no normal user database."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI_CHECKS = (
    'check_dashboard.py',
    'check_question_bank.py',
    'check_review_fixes.py',
    'check_practice.py',
    'check_practice_history.py',
    'check_flashcards.py',
    'check_statistics.py',
    'check_state_fixes.py',
    'check_tutor.py',
    'check_settings.py',
    'check_appearance.py',
    'check_backup.py',
    'check_csv_import.py',
    'check_flashcard_import.py',
    'check_tutor_history.py',
    'check_ui_languages.py',
)


def run(args, timeout):
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True, timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gui-only', action='store_true', help='Skip syntax, dependency and unit checks already run by CI.')
    args = parser.parse_args()
    if not args.gui_only:
        run(['-m', 'pip', 'check'], 60)
        run(['-m', 'compileall', '-q', 'soskuska', 'tests', 'tools'], 60)
        run(['-m', 'unittest', 'discover', '-s', 'tests', '-v'], 120)
    for script in GUI_CHECKS:
        print(f'Running {script}', flush=True)
        run(['-X', 'faulthandler', '-u', str(Path('soskuska') / script)], 60)
    print(f'PASS: all {len(GUI_CHECKS)} GUI scripts', flush=True)


if __name__ == '__main__':
    main()
