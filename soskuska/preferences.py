"""Validated local study and optional AI preferences; no I/O."""
from ollama_client import endpoint_url
from tutor import LANGUAGES

DEFAULTS = {'focus_minutes': 15, 'daily_goal_minutes': 60,
            'ollama_endpoint': 'http://127.0.0.1:11434', 'ollama_model': '',
            'answer_language': 'Automatic', 'ui_language': 'English', 'appearance_mode': 'Dark'}
AI_KEYS = ('ollama_endpoint', 'ollama_model', 'answer_language')


APPEARANCE_MODES = ('Light', 'Dark', 'System')

UI_LANGUAGES = ('English', 'Czech', 'Slovak', 'Russian')


def preference_fields(focus_minutes, daily_goal_minutes, ollama_endpoint, ollama_model, answer_language, ui_language='English', appearance_mode='Dark'):
    if type(focus_minutes) is not int or not 1 <= focus_minutes <= 180:
        raise ValueError('Focus duration must be a whole number from 1 to 180 minutes.')
    if type(daily_goal_minutes) is not int or not 1 <= daily_goal_minutes <= 1440:
        raise ValueError('Daily goal must be a whole number from 1 to 1,440 minutes.')
    endpoint = endpoint_url(ollama_endpoint)
    model = ollama_model.strip()
    if len(model) > 200 or any(ord(c) < 32 or ord(c) == 127 for c in model):
        raise ValueError('Preferred model must be at most 200 characters without control characters.')
    try:
        model.encode('utf-8')
    except UnicodeError:
        raise ValueError('Preferred model contains invalid Unicode.') from None
    if answer_language not in LANGUAGES:
        raise ValueError('Choose a supported answer language.')
    if ui_language not in UI_LANGUAGES:
        raise ValueError('Choose a supported interface language.')
    if appearance_mode not in APPEARANCE_MODES:
        raise ValueError('Choose Light, Dark or System appearance.')
    return dict(focus_minutes=focus_minutes, daily_goal_minutes=daily_goal_minutes,
                ollama_endpoint=endpoint, ollama_model=model, answer_language=answer_language, ui_language=ui_language, appearance_mode=appearance_mode)
