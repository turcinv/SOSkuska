"""Headless coverage for Settings and Tutor state transitions."""
import sqlite3
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'soskuska'))
from app import Dashboard
from preferences import DEFAULTS
from settings_page import SettingsPage, ctk
from tutor_page import TutorPage


class Entry:
    def __init__(self, value=''):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def insert(self, index, value):
        self.value = value

    def delete(self, start, end):
        self.value = ''

    def grid(self, **kwargs):
        pass


class SettingsUiTests(unittest.TestCase):
    def tutor(self, preferences, endpoint=None):
        page = TutorPage.__new__(TutorPage)
        page.app = SimpleNamespace(preferences=preferences, ai_status=Mock(), tutor_page=page)
        page.endpoint = Entry()
        page.endpoint.insert(0, endpoint or preferences['ollama_endpoint'])
        page.preferred_model = preferences['ollama_model']
        page.model = Entry(page.preferred_model)
        page.connected_endpoint = endpoint
        page.language = Mock()
        page.status = Mock()
        page.clear_button = Mock()
        page.models = []
        page.turns = []
        page.task = None
        page.controls = Mock()
        return page

    def test_saving_already_connected_server_keeps_chat_bound_to_that_server(self):
        connected = 'http://localhost:11435'
        tutor = self.tutor(DEFAULTS, endpoint=connected)
        tutor.models = ['study-model']
        turn = {'prompt': 'Prior prompt', 'answer': 'Prior response', 'status': 'completed'}
        tutor.turns = [turn]
        saved = dict(DEFAULTS, ollama_endpoint=connected, ollama_model='study-model')

        with patch('tutor_page.TutorTask') as job:
            Dashboard.validate_preferences_change(tutor.app, saved)
            tutor.apply_preferences(saved, DEFAULTS)
            self.assertEqual(tutor.connected_endpoint, connected)
            self.assertEqual(tutor.models, ['study-model'])
            self.assertEqual(tutor.turns, [turn])

            tutor.endpoint.insert(0, 'http://localhost:11436')
            tutor.connect()
            job.assert_not_called()
            self.assertIn('new chat', tutor.status.configure.call_args.kwargs['text'])

    def test_saving_preferred_model_before_connect_selects_it_from_server_list(self):
        tutor = self.tutor(DEFAULTS)
        tutor.model_menu = Mock()
        tutor.after = Mock()
        tutor.closed = False
        saved = dict(DEFAULTS, ollama_model='preferred-model')

        with patch('tutor_page.TutorTask') as job:
            tutor.apply_preferences(saved, DEFAULTS)
            job.assert_not_called()
            tutor.connect()
            job.assert_called_once_with('models', saved['ollama_endpoint'])
            task = job.return_value
            task.kind = 'models'
            task.control.cancelled.is_set.return_value = False
            task.events.get_nowait.return_value = ('done', ['first-model', 'preferred-model'])
            tutor.poll()

        self.assertEqual(tutor.model.get(), 'preferred-model')

    def test_edits_after_failed_initial_read_survive_navigation(self):
        saved = dict(DEFAULTS, revision=0, invalid=False)
        store = Mock()
        store.preferences.side_effect = [sqlite3.OperationalError('busy'), saved]
        app = SimpleNamespace(store=store, label=Mock(), button=Mock(), frame=Mock(), font=Mock())
        language = Entry('Automatic')

        with (patch.object(ctk.CTkFrame, '__init__', return_value=None),
              patch.object(SettingsPage, 'grid_columnconfigure'),
              patch.object(SettingsPage, 'bind'),
              patch.object(ctk, 'CTkEntry', side_effect=lambda *args, **kwargs: Entry()),
              patch.object(ctk, 'CTkOptionMenu'),
              patch.object(ctk, 'StringVar', return_value=language)):
            page = SettingsPage(None, app)

        page.load()
        self.assertIn('Could not load', page.status.configure.call_args.kwargs['text'])
        page.entries['focus_minutes'].insert(0, '27')
        page.load()
        self.assertEqual(page.entries['focus_minutes'].get(), '27')
        store.preferences.assert_called_once()

        page.reload()
        self.assertTrue(page.pending_reload)
        self.assertEqual(page.entries['focus_minutes'].get(), '27')
        page.reload()
        self.assertEqual(page.entries['focus_minutes'].get(), str(DEFAULTS['focus_minutes']))
        self.assertEqual(page.snapshot, saved)


if __name__ == '__main__':
    unittest.main()
