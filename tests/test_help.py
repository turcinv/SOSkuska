"""Bundled in-app help: aligned translations, real UI labels, validation and search."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'soskuska'))
from help_content import PAGE_TOPICS, PAGES, display, fold, help_path, labels, load_topics, search, topic_text, validate
from localization import LANGUAGE_CODES, Translator


def shape(topics):
    """Everything except the translated wording."""
    return [(t['id'], t['page'], t['related'],
             [(kind, len(value) if isinstance(value, list) else 1) for block in t['blocks'] for kind, value in block.items()])
            for t in topics]


def normal(label):
    return label.strip(' +→←⚙▤○\u00a0').strip()


class HelpContentTests(unittest.TestCase):
    def test_every_language_loads_with_the_same_structure(self):
        english = load_topics('English')
        self.assertGreaterEqual(len(english), 12)
        for language in LANGUAGE_CODES:
            with self.subTest(language=language):
                topics = load_topics(language)
                self.assertEqual(shape(topics), shape(english))
                if language != 'English':
                    # Translated, not copied: titles differ from English.
                    self.assertFalse({t['title'] for t in topics} & {t['title'] for t in english})

    def test_marked_labels_are_real_ui_labels_in_that_language(self):
        for language in LANGUAGE_CODES:
            catalog = Translator(language).catalog
            known = {normal(value) for value in catalog.values()} | {normal(key) for key in catalog} if language == 'English' \
                else {normal(value) for value in catalog.values()}
            for topic in load_topics(language):
                for label in labels(topic_text(topic)):
                    with self.subTest(language=language, topic=topic['id'], label=label):
                        self.assertIn(normal(label), known)

    def test_page_topics_cover_every_navigable_page(self):
        ids = {t['id'] for t in load_topics()}
        self.assertTrue(set(PAGE_TOPICS.values()) <= ids)
        self.assertTrue(set(PAGES) <= set(PAGE_TOPICS))
        self.assertIn('Question Bank', PAGE_TOPICS)

    def test_unknown_language_falls_back_to_english(self):
        self.assertEqual(help_path('French').name, 'help-en.json')
        self.assertEqual(load_topics('French'), load_topics('English'))

    def test_display_uses_each_languages_quotation_marks(self):
        self.assertEqual(display('Choose **Finish**.', 'English'), 'Choose “Finish”.')
        self.assertEqual(display('Zvolte **Dokončit**.', 'Czech'), 'Zvolte „Dokončit“.')
        self.assertEqual(display('Zvoľte **Dokončiť**.', 'Slovak'), 'Zvoľte „Dokončiť“.')
        self.assertEqual(display('Нажмите **Готово**.', 'Russian'), 'Нажмите «Готово».')
        for language in LANGUAGE_CODES:
            for topic in load_topics(language):
                self.assertNotIn('**', display(topic_text(topic), language))


class HelpValidationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(help_path('English').read_text(encoding='utf-8'))

    def rejects(self, change):
        data = copy.deepcopy(self.data)
        change(data['topics'])
        with self.assertRaises(ValueError):
            validate(data)

    def test_rejects_malformed_topics(self):
        self.rejects(lambda topics: topics[0].pop('summary'))
        self.rejects(lambda topics: topics[1].update(id=topics[0]['id']))
        self.rejects(lambda topics: topics[0].update(page='Nowhere'))
        self.rejects(lambda topics: topics[0].update(related=['missing']))
        self.rejects(lambda topics: topics[0].update(related=[topics[0]['id']]))
        self.rejects(lambda topics: topics[0].update(blocks=[]))
        self.rejects(lambda topics: topics[0].update(blocks=[{'video': 'x'}]))
        self.rejects(lambda topics: topics[0].update(blocks=[{'steps': []}]))
        self.rejects(lambda topics: topics[0].update(title='Unclosed **label'))
        self.rejects(lambda topics: topics[0].update(title='Bell\x07'))
        self.rejects(lambda topics: topics[0].update(title='x' * 1201))
        self.rejects(lambda topics: [topics.remove(t) for t in list(topics) if t['id'] == 'questions'])
        with self.assertRaises(ValueError):
            validate({'topics': []})


class HelpSearchTests(unittest.TestCase):
    def setUp(self):
        self.topics = load_topics('English')

    def test_blank_query_keeps_every_topic_in_order(self):
        self.assertEqual(search(self.topics, '   '), self.topics)

    def test_all_words_must_match_and_title_hits_come_first(self):
        ids = [t['id'] for t in search(self.topics, 'backup')]
        self.assertEqual(ids[0], 'backups')
        self.assertIn('privacy', ids)
        self.assertEqual([t['id'] for t in search(self.topics, 'flashcards REVEAL')], ['flashcards'])
        self.assertEqual(search(self.topics, 'zzz-no-such-help'), [])

    def test_search_ignores_case_accents_and_label_markers(self):
        self.assertEqual(fold('Nastavení **Uložit**'), 'nastaveni ulozit')
        czech = load_topics('Czech')
        settings_title = next(t['title'] for t in czech if t['id'] == 'settings')
        self.assertIn('settings', [t['id'] for t in search(czech, fold(settings_title).split()[0])])
        russian = load_topics('Russian')
        self.assertIn('flashcards', [t['id'] for t in search(russian, 'КАРТОЧКИ')])


class HelpIsolationTests(unittest.TestCase):
    def test_content_module_needs_no_tk_or_network(self):
        code = ('import sys,socket\n'
                'socket.socket=None\n'
                f'sys.path.insert(0,{str(ROOT / "soskuska")!r})\n'
                'import help_content\n'
                'for language in ("English","Czech","Slovak","Russian"):help_content.load_topics(language)\n'
                'assert "tkinter" not in sys.modules and "customtkinter" not in sys.modules\n')
        subprocess.run([sys.executable, '-c', code], check=True, timeout=30)


if __name__ == '__main__':
    unittest.main()
