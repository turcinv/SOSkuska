"""Bounded chat context rules and background jobs. Workers never access Tk or SQLite."""
import queue
import threading

from ollama_client import Cancelled, OllamaClient, OllamaError, RequestControl

LANGUAGES = ('Automatic', 'English', 'Czech', 'Slovak', 'Russian')


def chat_messages(turns, prompt, language='Automatic'):
    prompt = prompt.strip()
    if not prompt or len(prompt) > 4000:
        raise OllamaError('Enter a question between 1 and 4,000 characters.')
    if language not in LANGUAGES:
        raise OllamaError('Choose a supported answer language.')
    instruction = ('You are a study tutor. Explain clearly, help the student reason and admit uncertainty. '
                   'Do not claim to have read course materials that were not provided. ')
    instruction += 'Reply in the language of the latest student question.' if language == 'Automatic' else f'Reply in {language}.'
    messages = [{'role': 'system', 'content': instruction}]
    # Six recent complete turns, bounded by characters, never failed partials.
    selected = []
    budget = 24000
    for turn in reversed(turns):
        if turn['status'] != 'completed':
            continue
        size = len(turn['prompt']) + len(turn['answer'])
        if len(selected) >= 6 or size > budget:
            break
        selected.append(turn)
        budget -= size
    for turn in reversed(selected):
        messages.extend([{'role': 'user', 'content': turn['prompt']},
                         {'role': 'assistant', 'content': turn['answer']}])
    messages.append({'role': 'user', 'content': prompt})
    return messages


class TutorTask:
    def __init__(self, kind, endpoint, *, model=None, messages=None, client_factory=OllamaClient, chat_options=None):
        self.events = queue.Queue()
        self.control = RequestControl()
        self.kind = kind
        self.chat_options = dict(chat_options or {})
        self.client = client_factory(endpoint)
        self.thread = threading.Thread(target=self._run, args=(model, messages), daemon=True)

    def start(self):
        self.thread.start()

    def _run(self, model, messages):
        try:
            if self.kind == 'models':
                result = self.client.models(self.control)
            else:
                self.client.chat(model, messages, self.control, lambda value: self.events.put(('text', value)),
                                 **self.chat_options)
                result = None
            self.control.check()
            self.events.put(('done', result))
        except Cancelled:
            self.events.put(('stopped', None))
        except Exception as exc:
            # Contain worker failures and always give the UI a terminal event.
            detail = str(exc) if isinstance(exc, OllamaError) else 'Unexpected Ollama response. Please reconnect and retry.'
            self.events.put(('error', detail))

    def cancel(self):
        self.control.cancel()
