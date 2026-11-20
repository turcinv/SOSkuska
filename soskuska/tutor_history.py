"""Pure validation for local conversation snapshots."""
from csv_import import safe_text
from ollama_client import endpoint_url
from tutor import LANGUAGES

TERMINAL = ('completed', 'stopped', 'failed', 'interrupted')


def turn_fields(prompt, answer, language, status):
    prompt = safe_text(prompt).strip()
    answer = safe_text(answer)
    if not 1 <= len(prompt) <= 4000 or len(answer) > 16000:
        raise ValueError('Keep questions within 4,000 and answers within 16,000 characters.')
    if language not in LANGUAGES or status not in ('pending', *TERMINAL):
        raise ValueError('Invalid saved conversation state.')
    return prompt, answer, language, status


def owner_fields(endpoint, model):
    endpoint = endpoint_url(safe_text(endpoint))
    model = safe_text(model).strip()
    if not 1 <= len(model) <= 200:
        raise ValueError('Choose a model name within 200 characters.')
    return endpoint, model
