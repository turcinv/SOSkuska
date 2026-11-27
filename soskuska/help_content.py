"""Offline in-app help: bundled topic files, validation and search. No Tk, I/O beyond the bundle."""
import json
import re
import unicodedata
from pathlib import Path

from localization import LANGUAGE_CODES

BLOCK_KINDS = ('heading', 'text', 'steps', 'bullets')
# Pages a topic may offer to open; these are Dashboard.navigate targets.
PAGES = ('Dashboard', 'My Subjects', 'Practice Tests', 'Flashcards', 'Statistics', 'AI Tutor', 'Settings')
# Help opens on the topic for the page the student was using.
PAGE_TOPICS = {
    'Dashboard': 'dashboard',
    'My Subjects': 'subjects',
    'Question Bank': 'questions',
    'Practice Tests': 'practice',
    'Flashcards': 'flashcards',
    'Statistics': 'statistics',
    'AI Tutor': 'ai-tutor',
    'Settings': 'settings',
}
# `**Label**` marks a literal UI label; it is shown in the language's quotation marks.
LABEL = re.compile(r'\*\*(.+?)\*\*')
QUOTES = {'English': ('“', '”'), 'Czech': ('„', '“'), 'Slovak': ('„', '“'), 'Russian': ('«', '»')}
MAX_TEXT = 1200


def help_path(language):
    return Path(__file__).with_name('i18n') / f"help-{LANGUAGE_CODES.get(language, 'en')}.json"


def validate(data):
    """Return the topic list or raise ValueError; bundled files are trusted but still checked."""
    if not isinstance(data, dict) or not isinstance(data.get('topics'), list) or not data['topics']:
        raise ValueError('Help file must contain a non-empty topic list.')
    topics, ids = data['topics'], set()

    def text(value, where):
        if not isinstance(value, str) or not value.strip() or len(value) > MAX_TEXT:
            raise ValueError(f'Invalid help text in {where}.')
        if any(ord(c) < 32 for c in value) or value.count('**') % 2:
            raise ValueError(f'Invalid help text in {where}.')

    for topic in topics:
        if not isinstance(topic, dict) or set(topic) != {'id', 'title', 'summary', 'page', 'blocks', 'related'}:
            raise ValueError('Invalid help topic fields.')
        if not isinstance(topic['id'], str) or not re.fullmatch(r'[a-z][a-z-]*', topic['id']) or topic['id'] in ids:
            raise ValueError('Invalid or repeated help topic id.')
        ids.add(topic['id'])
        text(topic['title'], topic['id'])
        text(topic['summary'], topic['id'])
        if topic['page'] is not None and topic['page'] not in PAGES:
            raise ValueError(f"Unknown help page in {topic['id']}.")
        if not isinstance(topic['blocks'], list) or not topic['blocks']:
            raise ValueError(f"Help topic {topic['id']} has no content.")
        for block in topic['blocks']:
            if not isinstance(block, dict) or len(block) != 1 or next(iter(block)) not in BLOCK_KINDS:
                raise ValueError(f"Invalid help block in {topic['id']}.")
            kind, value = next(iter(block.items()))
            if kind in ('steps', 'bullets'):
                if not isinstance(value, list) or not value:
                    raise ValueError(f"Invalid help list in {topic['id']}.")
                for item in value:
                    text(item, topic['id'])
            else:
                text(value, topic['id'])
        if not isinstance(topic['related'], list) or not all(isinstance(item, str) for item in topic['related']):
            raise ValueError(f"Invalid related topics in {topic['id']}.")
    for topic in topics:
        if any(item not in ids or item == topic['id'] for item in topic['related']):
            raise ValueError(f"Unknown related topic in {topic['id']}.")
    if not set(PAGE_TOPICS.values()) <= ids:
        raise ValueError('Help is missing a page topic.')
    return topics


def load_topics(language='English'):
    path = help_path(language if language in LANGUAGE_CODES else 'English')
    return validate(json.loads(path.read_text(encoding='utf-8')))


def display(text, language='English'):
    """Replace label markers with the language's quotation marks."""
    opening, closing = QUOTES.get(language, QUOTES['English'])
    return LABEL.sub(lambda match: opening + match[1] + closing, text)


def labels(text):
    return LABEL.findall(text)


def fold(text):
    """Case- and accent-insensitive search key: 'Nastavení' matches 'nastaveni'."""
    decomposed = unicodedata.normalize('NFKD', text.replace('**', '').casefold())
    return ''.join(c for c in decomposed if not unicodedata.combining(c))


def topic_text(topic):
    parts = [topic['title'], topic['summary']]
    for block in topic['blocks']:
        value = next(iter(block.values()))
        parts.extend(value if isinstance(value, list) else [value])
    return '\n'.join(parts)


def search(topics, query):
    """Topics containing every query word, title matches first; a blank query keeps all."""
    words = fold(query).split()
    if not words:
        return list(topics)
    hits = [(any(word in fold(t['title']) for word in words), index, t) for index, t in enumerate(topics)
            if all(word in fold(topic_text(t)) for word in words)]
    return [topic for _, _, topic in sorted(hits, key=lambda hit: (not hit[0], hit[1]))]
