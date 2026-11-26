"""Prompt preparation from immutable, completed practice snapshots."""
import re
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'soskuska'))
from question_explanation import build_prompt, read_prompt
from storage import Store
from tutor import chat_messages


class QuestionExplanationTests(unittest.TestCase):
    def setUp(self):
        self.attempt = {'id': 8, 'status': 'completed', 'question_count': 2}
        self.item = {
            'attempt_id': 8, 'position': 1, 'prompt': 'Ktoré tvrdenie platí?\nПоясни вибір.',
            'option_a': 'Tlak', 'option_b': 'Čas', 'option_c': 'Hmotnosť', 'option_d': 'Rýchlosť',
            'selected_option': 0, 'correct_option': 3, 'explanation': 'Vysvetlenie zo skúšky.\nΔ = 2.',
        }

    def test_includes_snapped_question_answers_and_explanation(self):
        prompt = build_prompt(self.attempt, self.item, 8, 1)

        self.assertIn(self.item['prompt'], prompt)
        self.assertIn(self.item['explanation'], prompt)
        for letter in 'ABCD':
            option = self.item['option_' + letter.lower()]
            self.assertRegex(prompt, rf'(?m)^\s*{letter}[.):]?\s+{re.escape(option)}$')
        self.assertRegex(prompt, r'(?im)^[^\n]*(?:select|your answer|student(?:.?s)? answer)[^\n]*\bA\b')
        self.assertRegex(prompt, r'(?im)^[^\n]*correct[^\n]*\bD\b')

    def test_unanswered_question_can_be_explained_without_stored_notes(self):
        item = dict(self.item, selected_option=None, explanation='')
        prompt = build_prompt(self.attempt, item, 8, 1)

        self.assertRegex(prompt, r'(?i)unanswered|no answer|no option selected')
        self.assertRegex(prompt, r'(?im)^[^\n]*correct[^\n]*\bD\b')

    def test_correct_selection_keeps_both_answer_references(self):
        item = dict(self.item, selected_option=self.item['correct_option'])
        prompt = build_prompt(self.attempt, item, 8, 1)

        self.assertRegex(prompt, r'(?im)^[^\n]*(?:select|your answer|student(?:.?s)? answer)[^\n]*\bD\b')
        self.assertRegex(prompt, r'(?im)^[^\n]*correct[^\n]*\bD\b')

    def test_preview_rejects_text_tutor_cannot_store(self):
        item = dict(self.item, explanation='Question saved with a control character: \x1f')

        with self.assertRaises(ValueError):
            build_prompt(self.attempt, item, 8, 1)

    def test_rejects_incomplete_or_mismatched_snapshots(self):
        cases = (
            (None, self.item, 8, 1),
            (dict(self.attempt, status='in_progress'), self.item, 8, 1),
            (self.attempt, None, 8, 1),
            (self.attempt, self.item, 9, 1),
            (self.attempt, self.item, 8, 0),
            (self.attempt, self.item, 8, True),
            (self.attempt, dict(self.item, attempt_id=7), 8, 1),
            (self.attempt, dict(self.item, correct_option=4), 8, 1),
            (self.attempt, dict(self.item, selected_option=-1), 8, 1),
        )
        for attempt, item, attempt_id, position in cases:
            with self.subTest(attempt=attempt, item=item, attempt_id=attempt_id, position=position):
                with self.assertRaises(ValueError):
                    build_prompt(attempt, item, attempt_id, position)

    def test_prompt_limit_matches_tutor_and_counts_unicode_characters(self):
        item = dict(self.item, prompt='ž' * 1900, explanation='Ж')
        for letter in 'abcd':
            item[f'option_{letter}'] = letter * 350
        baseline = build_prompt(self.attempt, item, 8, 1)
        item['explanation'] += 'Ж' * (4000 - len(baseline))
        prompt = build_prompt(self.attempt, item, 8, 1)

        self.assertEqual(len(prompt), 4000)
        self.assertEqual(chat_messages([], prompt)[-1]['content'], prompt)
        item['explanation'] += 'Ж'
        with self.assertRaises(ValueError):
            build_prompt(self.attempt, item, 8, 1)

    def test_reads_only_the_requested_saved_item_after_source_deletion(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        store = Store(Path(directory.name) / 'explanation.db')
        self.addCleanup(store.close)
        subject = store.create_subject('Study subject')
        store.create_question(subject, 'First original?', ['red', 'blue', 'green', 'gold'], 2)
        store.create_question(subject, 'Second original?', ['east', 'west', 'north', 'south'], 1)
        attempt_id = store.start_practice(subject, 2)
        store.save_practice_answer(attempt_id, 1, 0)
        with self.assertRaises(ValueError):
            read_prompt(store, attempt_id, 1)

        store.complete_practice(attempt_id)
        store.delete_subject(subject)
        first, second = store.practice_items(attempt_id)
        changes = store.db.total_changes
        prompt = read_prompt(store, attempt_id, 1)

        self.assertEqual(prompt, build_prompt(store.practice_attempt(attempt_id), second, attempt_id, 1))
        self.assertIn(second['prompt'], prompt)
        self.assertNotIn(first['prompt'], prompt)
        with self.assertRaises(ValueError):
            read_prompt(store, attempt_id, 2)
        with self.assertRaises(ValueError):
            read_prompt(store, attempt_id + 1, 0)
        self.assertEqual(store.db.total_changes, changes)

    def test_read_errors_are_available_to_the_ui_for_retry(self):
        store = Mock(spec=Store)
        store.practice_attempt.return_value = self.attempt
        failure = sqlite3.OperationalError('test read failure')
        store.practice_items.side_effect = (failure, [self.item])

        with self.assertRaises(sqlite3.OperationalError):
            read_prompt(store, 8, 1)
        self.assertEqual(read_prompt(store, 8, 1), build_prompt(self.attempt, self.item, 8, 1))


if __name__ == '__main__':
    unittest.main()
