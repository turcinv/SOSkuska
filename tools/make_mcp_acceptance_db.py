"""Create a disposable SOSkúška database with sample study data for MCP host acceptance.

Example: python tools/make_mcp_acceptance_db.py .local-data/mcp-acceptance/study.sqlite3

The data is invented and clearly labelled as a sample. The tool refuses to touch an
existing file and refuses the app's normal per-user database, so real study data is
never mixed with samples.
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'soskuska'))
from storage import Store, user_database_path  # noqa: E402

QUESTIONS = {
    'Sample Biology': [
        ('Cells', 'Which organelle produces most of the cell\'s ATP?', ['Mitochondrion', 'Ribosome', 'Golgi apparatus', 'Lysosome'], 0, 'Easy',
         'Oxidative phosphorylation in the mitochondria produces most ATP.'),
        ('Cells', 'Where does glycolysis take place?', ['Nucleus', 'Cytoplasm', 'Mitochondrial matrix', 'Cell wall'], 1, 'Medium',
         'Glycolysis runs in the cytoplasm and does not need oxygen.'),
        ('Plants', 'Which pigment absorbs light for photosynthesis?', ['Haemoglobin', 'Melanin', 'Chlorophyll', 'Keratin'], 2, 'Easy',
         'Chlorophyll in the chloroplasts absorbs mainly red and blue light.'),
        ('Plants', 'Which gas do plants release during photosynthesis?', ['Carbon dioxide', 'Nitrogen', 'Methane', 'Oxygen'], 3, 'Easy',
         'Water is split and oxygen is released.'),
        (None, 'Who proposed natural selection together with Alfred Russel Wallace?', ['Charles Darwin', 'Gregor Mendel', 'Louis Pasteur', 'Robert Hooke'], 0, 'Hard',
         'Darwin and Wallace presented natural selection in 1858.'),
    ],
    'Sample History': [
        ('Middle Ages', 'In which year was Charles University in Prague founded?', ['1248', '1348', '1448', '1548'], 1, 'Medium',
         'Charles IV founded the university in 1348.'),
        ('20th century', 'In which year did Czechoslovakia split into two countries?', ['1989', '1990', '1993', '2004'], 2, 'Easy',
         'The Czech Republic and Slovakia became independent on 1 January 1993.'),
    ],
}
CARDS = [('ATP', 'The cell\'s energy currency'), ('Glycolysis', 'Splits glucose into two pyruvate molecules'),
         ('Photosynthesis equation', '6 CO2 + 6 H2O → C6H12O6 + 6 O2'), ('Stomata', 'Pores in leaves for gas exchange')]


def create(path):
    path = Path(path).expanduser().resolve()
    # The GUI may use either the current or the legacy folder; never write into either.
    normal = user_database_path().expanduser().resolve()
    base = normal.parent.parent
    if path == normal or path.parent in {base / 'SOSkuska', base / 'ExamPrep'}:
        raise SystemExit('Refusing to write samples into the normal SOSkúška data folder. Choose a disposable path.')
    if path.exists():
        raise SystemExit(f'{path} already exists. Choose a new path; this tool never changes an existing file.')
    store = Store(path)
    try:
        today = date.today()
        ids = {}
        for index, (subject, questions) in enumerate(QUESTIONS.items()):
            exam = (today + timedelta(days=5 + 9 * index)).isoformat()
            sid = ids[subject] = store.create_subject(subject, 'Invented sample data for MCP acceptance.', exam)
            topics = {}
            for topic, prompt, options, correct, difficulty, explanation in questions:
                if topic and topic not in topics:
                    topics[topic] = store.create_topic(sid, topic)
                store.create_question(sid, prompt, options, correct, difficulty, topics.get(topic), explanation)
        deck = store.create_deck(ids['Sample Biology'], 'Sample Biology cards')
        for front, back in CARDS:
            store.create_flashcard(deck, front, back)
        store.add_session(25 * 60, ids['Sample Biology'])
        store.add_session(15 * 60, ids['Sample History'])
        attempt = store.start_practice(ids['Sample Biology'], 4)
        for item in store.practice_items(attempt):
            # Two right, two wrong, so weak topics have something to find.
            right = item['position'] % 2 == 0
            store.save_practice_answer(attempt, item['position'], item['correct_option'] if right else (item['correct_option'] + 1) % 4)
        store.complete_practice(attempt)
    finally:
        store.close()
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('path', help='new disposable database file, for example .local-data/mcp-acceptance/study.sqlite3')
    print(f'Created sample database: {create(parser.parse_args().path)}')


if __name__ == '__main__':
    main()
