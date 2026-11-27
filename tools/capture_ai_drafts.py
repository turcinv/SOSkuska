"""Capture the AI question-drafting panel with the loopback fake Ollama (Xvfb only, disposable data).

Run from the repository root inside the test image, for example:
  docker run -i --init --network none soskuska-tests xvfb-run -a -s '-screen 0 1920x1080x24' \
      python - --mode Light --output /tmp/capture < tools/capture_ai_drafts.py
Design/report artifact only; the drafts are a fixed fake reply, not real model output.
"""
import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd() if __file__ == '<stdin>' else Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'soskuska'))
sys.path.insert(0, str(ROOT / 'tests'))

NOTES = ('Photosynthesis happens in chloroplasts. Chlorophyll absorbs mainly red and blue light. Water is split and oxygen '
         'is released. Carbon dioxide is fixed into glucose in the Calvin cycle.')
DRAFTS = {'items': [
    {'question': 'Where does photosynthesis happen?', 'correct_answer': 'In chloroplasts',
     'wrong_answers': ['In ribosomes', 'In the nucleus', 'In lysosomes'], 'difficulty': 'Easy',
     'explanation': 'The notes say photosynthesis happens in chloroplasts.', 'topic': 'Plants'},
    {'question': 'Which gas is released when water is split?', 'correct_answer': 'Oxygen',
     'wrong_answers': ['Nitrogen', 'Carbon dioxide', 'Methane'], 'difficulty': 'Easy',
     'explanation': 'Splitting water releases oxygen.', 'topic': 'Plants'},
    {'question': 'In which cycle is carbon dioxide fixed into glucose?', 'correct_answer': 'The Calvin cycle',
     'wrong_answers': ['The Krebs cycle', 'The urea cycle', 'The cell cycle'], 'difficulty': 'Medium',
     'explanation': 'The notes name the Calvin cycle.', 'topic': 'Plants'}]}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--mode', choices=('Light', 'Dark'), default='Light')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if sys.platform != 'linux' or not os.environ.get('DISPLAY'):
        parser.error('Run inside the Linux/Xvfb test container.')
    from PIL import ImageGrab
    from app import Dashboard
    from ollama_fixture import FakeOllama
    from preferences import DEFAULTS
    from storage import Store

    fixture = FakeOllama()
    fixture.model_names = ['llama3.2:3b']
    with tempfile.TemporaryDirectory(prefix='soskuska-capture-') as folder:
        path = Path(folder) / 'fixture.sqlite3'
        store = Store(path)
        try:
            store.save_preferences(dict(DEFAULTS, ollama_endpoint=fixture.url, ollama_model='llama3.2:3b',
                                        appearance_mode=args.mode), expected_revision=0)
            sid = store.create_subject('Sample Biology', 'Disposable capture fixture')
        finally:
            store.close()
        app = Dashboard(path)
        try:
            app.geometry('1440x900+0+0')
            app.update()
            app.open_question_bank(sid)
            app.question_bank.generate_button.invoke()
            app.update()
            panel = app.question_bank.generator
            panel.notes.insert('1.0', NOTES)
            panel.count.set('5')
            fixture.mode, fixture.content = 'content', json.dumps(DRAFTS)
            panel.generate_button.invoke()
            deadline = time.monotonic() + 30
            while panel.busy and time.monotonic() < deadline:
                app.update()
                time.sleep(0.05)
            assert panel.preview and len(panel.preview['rows']) == 3, panel.status.cget('text')
            canvas = app.scroll._parent_canvas
            app.update()
            top = panel.winfo_rooty() - canvas.winfo_rooty() + canvas.canvasy(0) - 12
            canvas.yview_moveto(max(0, top / canvas.bbox('all')[3]))
            app.update()
            time.sleep(0.3)
            app.update()
            box = (app.winfo_rootx(), app.winfo_rooty(), app.winfo_rootx() + app.winfo_width(), app.winfo_rooty() + app.winfo_height())
            args.output.mkdir(parents=True, exist_ok=True)
            ImageGrab.grab(xdisplay=os.environ['DISPLAY']).crop(box).save(args.output / f'ai-drafts-{args.mode.lower()}.png')
            panel.close()
        finally:
            app.close()
            fixture.close()


if __name__ == '__main__':
    main()
