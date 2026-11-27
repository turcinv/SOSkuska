"""Regression coverage for the 27 November 2026 repository review (S27) storage and query findings."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'soskuska'))
import study_queries as queries
from practice import PracticeChangedError
from storage import Store


class TwoWindowTests(unittest.TestCase):
    """Two Stores on one file stand in for two app windows."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = Path(self.temp.name) / 'study.sqlite3'
        self.one, self.two = Store(path), Store(path)
        self.addCleanup(self.one.close)
        self.addCleanup(self.two.close)
        self.sid = self.one.create_subject('Biology')
        for n in range(2):
            self.one.create_question(self.sid, f'Question {n}?', ['a', 'b', 'c', 'd'], 0)

    def start(self):
        attempt = self.one.start_practice(self.sid, 2)
        self.one.save_practice_answer(attempt, 0, 1)
        return attempt

    # S27-02 -------------------------------------------------------------
    def test_discard_keeps_a_test_whose_answers_changed_after_confirmation(self):
        attempt = self.start()
        shown = self.one.practice_answers(attempt)
        self.two.save_practice_answer(attempt, 1, 2)  # Another window answers meanwhile.
        with self.assertRaisesRegex(PracticeChangedError, 'changed in another window'):
            self.one.discard_practice(attempt, expected_answers=shown)
        self.assertEqual(self.two.practice_answers(attempt), (1, 2))
        self.assertTrue(self.one.discard_practice(attempt, expected_answers=self.one.practice_answers(attempt)))
        self.assertIsNone(self.two.practice_attempt(attempt))

    def test_submit_refuses_answers_changed_after_confirmation(self):
        attempt = self.start()
        shown = self.one.practice_answers(attempt)
        self.two.save_practice_answer(attempt, 0, None)
        with self.assertRaises(PracticeChangedError):
            self.one.complete_practice(attempt, expected_answers=shown)
        self.assertEqual(self.two.practice_attempt(attempt)['status'], 'in_progress')
        done = self.one.complete_practice(attempt, expected_answers=self.one.practice_answers(attempt))
        self.assertEqual((done['status'], done['answered']), ('completed', 0))

    def test_unconfirmed_and_expired_submissions_still_save(self):
        attempt = self.start()
        self.two.save_practice_answer(attempt, 1, 3)
        self.assertEqual(self.one.complete_practice(attempt)['status'], 'completed')  # Timer/expiry path.

    # S27-03 -------------------------------------------------------------
    def test_deck_deletion_rejects_a_same_count_replacement(self):
        deck = self.one.create_deck(self.sid, 'Cards')
        card = self.one.create_flashcard(deck, 'Front', 'Back')
        state = self.one.deck_deletion_state(deck)
        self.two.delete_flashcard(card)
        replacement = self.two.create_flashcard(deck, 'New front', 'New back')
        self.assertEqual(self.one.deck_deletion_state(deck)[:2], state[:2], 'name and count alone look unchanged')
        self.assertFalse(self.one.delete_deck(deck, state))
        self.assertIsNotNone(self.two.flashcard(replacement))
        self.assertTrue(self.one.delete_deck(deck, self.one.deck_deletion_state(deck)))

    def test_deck_deletion_rejects_edited_card_content(self):
        deck = self.one.create_deck(self.sid, 'Cards')
        card = self.one.create_flashcard(deck, 'Front', 'Back')
        state = self.one.deck_deletion_state(deck)
        self.two.update_flashcard(card, 'Front', 'Corrected back', 0)
        self.assertFalse(self.one.delete_deck(deck, state))

    def test_subject_deletion_rejects_a_same_count_question_replacement_or_edit(self):
        state = self.one.subject_deletion_state(self.sid)
        old = self.two.questions(self.sid)[0]
        self.two.delete_question(old['id'])
        self.two.create_question(self.sid, 'Replacement?', ['a', 'b', 'c', 'd'], 1)
        self.assertEqual(self.one.subject_deletion_state(self.sid)[:3], state[:3])
        self.assertFalse(self.one.delete_subject(self.sid, state))
        state = self.one.subject_deletion_state(self.sid)
        question = self.two.questions(self.sid)[0]
        self.two.update_question(question['id'], question['prompt'], ['a', 'b', 'c', 'changed'], question['correct_option'],
                                 question['difficulty'], question['topic_id'], question['explanation'])
        self.assertFalse(self.one.delete_subject(self.sid, state))
        self.assertTrue(self.one.delete_subject(self.sid, self.one.subject_deletion_state(self.sid)))


class McpQueryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(Path(self.temp.name) / 'study.sqlite3')
        self.addCleanup(self.store.close)
        self.sid = self.store.create_subject('Long')

    # S27-05 -------------------------------------------------------------
    def test_long_options_are_returned_whole_and_stay_distinct(self):
        shared = 'x' * 400
        options = [shared + suffix for suffix in ('-alpha', '-beta', '-gamma', '-delta')]
        qid = self.store.create_question(self.sid, 'Which?', options, 2)
        item = queries.find_questions(self.store, self.sid)['items'][0]
        self.assertEqual(list(item['options'].values()), options)
        self.assertFalse(queries.find_questions(self.store, self.sid)['truncated'])
        self.assertEqual(item['id'], qid)

    def test_question_version_changes_with_edits_and_does_not_reveal_the_key(self):
        import hashlib
        import json
        qid = self.store.create_question(self.sid, 'Which?', ['a', 'b', 'c', 'd'], 2)
        version = queries.find_questions(self.store, self.sid, question_id=qid)['items'][0]['version']
        self.assertEqual(queries.find_questions(self.store, self.sid, question_id=qid)['items'][0]['version'], version)
        plain = {hashlib.sha256(json.dumps(['Which?', 'a', 'b', 'c', 'd', key, ''], ensure_ascii=False).encode()).hexdigest()[:12]
                 for key in range(4)}
        self.assertNotIn(version, plain, 'a host must not be able to test candidate answers')
        self.store.update_question(qid, 'Which?', ['a', 'b', 'c', 'd'], 3)
        self.assertNotEqual(queries.find_questions(self.store, self.sid, question_id=qid)['items'][0]['version'], version)

    def test_exact_question_lookup_for_grading(self):
        first = self.store.create_question(self.sid, 'First?', ['a', 'b', 'c', 'd'], 3)
        for n in range(60):
            self.store.create_question(self.sid, f'Newer {n}?', ['a', 'b', 'c', 'd'], 0)
        result = queries.find_questions(self.store, self.sid, question_id=first, include_answers=True)
        self.assertEqual([(i['id'], i['correct_option']) for i in result['items']], [(first, 'D')])
        other = self.store.create_subject('Other')
        with self.assertRaisesRegex(ValueError, 'does not belong'):
            queries.find_questions(self.store, other, question_id=first)
        with self.assertRaises(ValueError):
            queries.find_questions(self.store, self.sid, question_id=True)


if __name__ == '__main__':
    unittest.main()
