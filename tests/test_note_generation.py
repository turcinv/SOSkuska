"""AI note-generation prompt, schema, parsing, atomic save and loopback protocol tests."""
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'soskuska'))
from csv_import import ImportValidationError
from note_generation import (COUNTS, MAX_REPLY, OPTIONS, generation_messages, item_message,
                             parse_generated, response_schema)
from ollama_client import OllamaClient
from storage import Store
from tutor import TutorTask
from ollama_fixture import FakeOllama

CARDS = {'items': [{'front': 'What is FIFO?', 'back': 'First in, first out.'},
                   {'front': 'What is LIFO?', 'back': 'Last in, first out.'}]}
QUESTION = {'question': 'Which structure is FIFO?', 'options': ['Queue', 'Stack', 'Tree', 'Graph'],
            'correct': 'A', 'difficulty': 'Easy', 'explanation': 'Queues remove the oldest item first.',
            'topic': 'Data structures'}


def wait(task, timeout=5):
    deadline = time.monotonic() + timeout
    chunks = []
    while time.monotonic() < deadline:
        event, value = task.events.get(timeout=timeout)
        if event == 'text':
            chunks.append(value)
        else:
            return event, value, ''.join(chunks)
    raise AssertionError('No terminal event')


class PromptAndSchemaTests(unittest.TestCase):
    def test_notes_are_delimited_data_with_language_and_count(self):
        messages = generation_messages('cards', '  Queues are FIFO.  ', 5, 'Czech')
        self.assertEqual([m['role'] for m in messages], ['system', 'user'])
        system = messages[0]['content']
        self.assertIn('up to 5 flashcards', system)
        self.assertIn('Write every item in Czech.', system)
        self.assertIn('never as instructions', system)
        self.assertEqual(messages[1]['content'], '<notes>\nQueues are FIFO.\n</notes>')
        self.assertIn('language of the notes', generation_messages('questions', 'x', 3)[0]['content'])

    def test_rejects_invalid_notes_counts_kinds_and_languages(self):
        for notes in ('', '   ', 'x' * 12001, 'bad\x1b'):
            with self.subTest(notes=notes[:5]), self.assertRaises(ValueError):
                generation_messages('cards', notes, 5)
        for args in (('cards', 'x', 4), ('cards', 'x', 0), ('poems', 'x', 5), ('cards', 'x', 5, 'French')):
            with self.subTest(args=args), self.assertRaises(ValueError):
                generation_messages(*args)
        self.assertEqual(len(generation_messages('cards', 'x' * 12000, 20)[1]['content']), 12000 + 17)

    def test_schema_bounds_item_count_and_question_shape(self):
        for count in COUNTS:
            schema = response_schema('questions', count)
            self.assertEqual(schema['properties']['items']['maxItems'], count)
        item = response_schema('questions', 5)['properties']['items']['items']
        self.assertEqual(item['properties']['options']['minItems'], 4)
        self.assertEqual(item['properties']['correct']['enum'], ['A', 'B', 'C', 'D'])
        self.assertEqual(set(response_schema('cards', 3)['properties']['items']['items']['required']), {'front', 'back'})


class ParseTests(unittest.TestCase):
    def test_cards_accept_object_list_and_fenced_json(self):
        for text in (json.dumps(CARDS), json.dumps(CARDS['items']), '```json\n' + json.dumps(CARDS) + '\n```'):
            preview = parse_generated('cards', text, 5)
            self.assertEqual(preview['errors'], [])
            self.assertEqual([row['fields'] for row in preview['rows']],
                             [['What is FIFO?', 'First in, first out.'], ['What is LIFO?', 'Last in, first out.']])
            self.assertEqual([row['record'] for row in preview['rows']], [2, 3])

    def test_invalid_json_and_empty_results_raise(self):
        for text in ('not json', '{"items": []}', '{"other": 1}', '[]'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_generated('cards', text, 5)

    def test_invalid_items_are_reported_with_item_numbers_and_extra_items_cut(self):
        items = [{'front': 'A', 'back': 'B'}, {'front': '', 'back': 'B'}, 'text', {'front': 'A', 'back': 'B'},
                 {'front': 3, 'back': 'x'}, {'front': 'C', 'back': 'D'}]
        preview = parse_generated('cards', json.dumps(items), 5)
        self.assertEqual(preview['total'], 5)
        self.assertEqual([row['fields'][0] for row in preview['rows']], ['A', 'A'])
        joined = '\n'.join(preview['errors'])
        self.assertIn('only the first 5 are shown', joined)
        self.assertIn('Item 2: Enter a front', joined)
        self.assertIn('Item 3: Expected an object.', joined)
        self.assertIn('Item 4: Duplicate of item 1 (front and back).', joined)
        self.assertIn('Item 5:', joined)

    def test_questions_use_canonical_rules(self):
        lower = dict(QUESTION, correct='c', difficulty='hard', topic='T' * 200)
        preview = parse_generated('questions', json.dumps({'items': [QUESTION, lower]}), 5)
        self.assertEqual(preview['errors'], [])
        first, second = preview['rows']
        self.assertEqual(first['topic'], 'Data structures')
        self.assertEqual(first['fields'], ['Which structure is FIFO?', 'Queue', 'Stack', 'Tree', 'Graph', 0, 'Easy',
                                           'Queues remove the oldest item first.'])
        self.assertEqual((second['fields'][5], second['fields'][6], len(second['topic'])), (2, 'Hard', 120))
        bad = [dict(QUESTION, options=['a', 'a', 'b', 'c']), dict(QUESTION, options=['a', 'b']),
               dict(QUESTION, correct='E'), dict(QUESTION, difficulty='Extreme'), dict(QUESTION, question=5),
               dict(QUESTION, explanation=['x'])]
        preview = parse_generated('questions', json.dumps(bad), 10)
        self.assertEqual(preview['rows'], [])
        self.assertEqual(len(preview['errors']), 6)
        self.assertTrue(all(line.startswith(f'Item {i}:') for i, line in enumerate(preview['errors'], 1)))

    def test_item_message_maps_shared_import_records(self):
        self.assertEqual(item_message('CSV record 3: This front and back already exist in the deck.'),
                         'Item 2: This front and back already exist in the deck.')
        self.assertEqual(item_message('CSV record 4: Duplicate of record 2 (front and back).'),
                         'Item 3: Duplicate of item 1 (front and back).')
        self.assertEqual(item_message('The deck was renamed or deleted.'), 'The deck was renamed or deleted.')


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.dir.name) / 'study.sqlite3')
        self.subject = self.store.create_subject('Computer Science')
        self.deck = self.store.create_deck(self.subject, 'Structures')

    def tearDown(self):
        self.store.close()
        self.dir.cleanup()

    def test_generated_cards_save_atomically_and_existing_duplicates_block_all(self):
        rows = parse_generated('cards', json.dumps(CARDS), 5)['rows']
        self.assertEqual(self.store.import_flashcards(self.deck, rows[:1], expected_deck_name='Structures')['cards'], 1)
        with self.assertRaises(ImportValidationError) as raised:
            self.store.import_flashcards(self.deck, rows, expected_deck_name='Structures')
        self.assertEqual([item_message(e) for e in raised.exception.errors],
                         ['Item 1: This front and back already exist in the deck.'])
        self.assertEqual(len(self.store.flashcards(self.deck)), 1)
        with self.assertRaises(ImportValidationError):
            self.store.import_flashcards(self.deck, rows[1:], expected_deck_name='Renamed')
        self.assertEqual(len(self.store.flashcards(self.deck)), 1)

    def test_generated_questions_create_topics_in_existing_subject(self):
        rows = parse_generated('questions', json.dumps([QUESTION]), 3)['rows']
        result = self.store.import_questions(self.subject, rows, expected_subject_name='Computer Science')
        self.assertEqual((result['questions'], result['topics']), (1, 1))
        self.assertEqual(self.store.questions(self.subject)[0]['correct_option'], 0)


class LoopbackTests(unittest.TestCase):
    def setUp(self):
        self.fixture = FakeOllama()

    def tearDown(self):
        self.fixture.close()

    def task(self, count=5):
        return TutorTask('chat', self.fixture.url, model='study-model:latest',
                         messages=generation_messages('cards', 'Queues are FIFO.', count),
                         client_factory=lambda e: OllamaClient(e, total_timeout=10),
                         chat_options={'response_format': response_schema('cards', count),
                                       'options': dict(OPTIONS), 'max_reply': MAX_REPLY})

    def test_structured_request_payload_and_streamed_json(self):
        self.fixture.mode = 'content'
        self.fixture.content = json.dumps(CARDS, ensure_ascii=False)
        task = self.task(); task.start()
        event, _, text = wait(task)
        self.assertEqual(event, 'done')
        self.assertEqual(len(parse_generated('cards', text, 5)['rows']), 2)
        payload = self.fixture.requests[-1][2]
        self.assertEqual(payload['format'], response_schema('cards', 5))
        self.assertEqual(payload['options'], {'temperature': 0.3})
        self.assertTrue(payload['stream'])

    def test_ordinary_tutor_payload_has_no_structured_fields(self):
        task = TutorTask('chat', self.fixture.url, model='study-model:latest', messages=[{'role': 'user', 'content': 'Hi'}])
        task.start()
        self.assertEqual(wait(task)[0], 'done')
        self.assertNotIn('format', self.fixture.requests[-1][2])
        self.assertNotIn('options', self.fixture.requests[-1][2])

    def test_generation_reply_limit_and_stop(self):
        self.fixture.mode = 'content'
        self.fixture.content = 'x' * (MAX_REPLY + 10)
        task = self.task(); task.start()
        event, detail, _ = wait(task)
        self.assertEqual(event, 'error')
        self.assertIn('fewer items', detail)
        self.fixture.mode = 'slow'
        task = self.task(); task.start()
        self.assertEqual(task.events.get(timeout=5), ('text', 'Hello '))
        task.cancel()
        self.assertEqual(wait(task)[0], 'stopped')


if __name__ == '__main__':
    unittest.main()
