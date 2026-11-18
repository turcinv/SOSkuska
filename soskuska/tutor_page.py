"""Optional Ollama chat. Session-only; all widget access stays on the Tk thread."""
import queue

import customtkinter as ctk
from ollama_client import OllamaError, endpoint_url
from tutor import LANGUAGES, TutorTask, chat_messages


class TutorPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color='transparent', corner_radius=0)
        self.app = app
        self.turns = []
        self.task = None
        self.closed = False
        self.connected_endpoint = None
        self.models = []
        self.pending_clear = False
        self.grid_columnconfigure(0, weight=1)
        app.label(self, 'AI Tutor', 28, bold=True).grid(row=0, column=0, sticky='w')
        self.status = app.label(self, 'Not connected. Start Ollama, then connect to load its models.', 13, 'secondary', wraplength=600)
        self.status.grid(row=1, column=0, sticky='ew', pady=(6, 14))
        connection = app.frame(self)
        connection.grid(row=2, column=0, sticky='ew', pady=(0, 12))
        connection.grid_columnconfigure(0, weight=1)
        self.endpoint = ctk.CTkEntry(connection, height=38, font=app.font())
        self.endpoint.insert(0, app.preferences['ollama_endpoint'])
        self.endpoint.grid(row=0, column=0, sticky='ew', padx=(0, 8))
        self.connect_button = app.button(connection, 'Connect / refresh', self.connect, width=155)
        self.connect_button.grid(row=0, column=1)
        options = app.frame(self)
        options.grid(row=3, column=0, sticky='ew', pady=(0, 12))
        options.grid_columnconfigure(0, weight=1)
        self.preferred_model = app.preferences['ollama_model']
        self.model = ctk.StringVar(value=self.preferred_model or 'Connect to load models')
        self.model_menu = ctk.CTkOptionMenu(options, variable=self.model, values=[self.model.get()], dynamic_resizing=False, font=app.font(), height=38, state='disabled')
        app.label(options, 'Model', 12, 'secondary').grid(row=0, column=0, sticky='w')
        self.model_menu.grid(row=1, column=0, sticky='ew', padx=(0, 8))
        self.language = ctk.StringVar(value=app.preferences['answer_language'])
        self.language_menu = ctk.CTkOptionMenu(options, variable=self.language, values=list(LANGUAGES), dynamic_resizing=False, font=app.font(), height=38, width=125)
        app.label(options, 'Answer language', 12, 'secondary').grid(row=0, column=1, sticky='w')
        self.language_menu.grid(row=1, column=1)
        self.info = app.label(self, 'Only this chat is sent to the displayed server. Chat stays in this app session and is cleared when the app closes. AI answers may be incorrect; check important facts.', 12, 'secondary', wraplength=600)
        self.info.grid(row=4, column=0, sticky='ew', pady=(0, 12))
        self.transcript = ctk.CTkTextbox(self, height=330, font=app.font(), wrap='word', state='disabled')
        self.transcript.grid(row=5, column=0, sticky='ew', pady=(0, 12))
        self.prompt = ctk.CTkTextbox(self, height=100, font=app.font(), wrap='word')
        app.label(self, 'Your question (up to 4,000 characters)', 12, 'secondary').grid(row=6, column=0, sticky='w')
        self.prompt.grid(row=7, column=0, sticky='ew', pady=(0, 12))
        actions = app.frame(self)
        actions.grid(row=8, column=0, sticky='ew')
        self.send_button = app.button(actions, 'Send', self.send, primary=True, width=95)
        self.send_button.pack(side='left', padx=(0, 8))
        self.stop_button = app.button(actions, 'Stop', self.stop, width=85)
        self.stop_button.pack(side='left', padx=(0, 8))
        self.clear_button = app.button(actions, 'New chat', self.new_chat, width=120)
        self.clear_button.pack(side='left')
        self.bind('<Configure>', self.resize, add='+')
        self.controls()
        self.poll_job = self.after(50, self.poll)

    def resize(self, event):
        for label in (self.status, self.info):
            label.configure(wraplength=max(250, event.width - 12))

    def load(self):
        self.pending_clear = False  # Navigation preserves chat; cancels clear confirmation.
        self.clear_button.configure(text='New chat')

    def apply_preferences(self, saved, previous):
        # Called only after explicit Settings Save; never starts networking.
        endpoint_changed = saved['ollama_endpoint'] != previous['ollama_endpoint']
        model_changed = saved['ollama_model'] != previous['ollama_model']
        if endpoint_changed:
            self.endpoint.delete(0, 'end')
            self.endpoint.insert(0, saved['ollama_endpoint'])
            # Remembering the already connected server must retain chat ownership.
            if saved['ollama_endpoint'] != self.connected_endpoint:
                self.connected_endpoint = None
                self.models = []
                self.app.ai_status.configure(text='○  AI not connected')
        if model_changed:
            self.preferred_model = saved['ollama_model']
        if endpoint_changed or model_changed:
            self.model.set(self.preferred_model if not self.models or self.preferred_model in self.models else '')
            self.status.configure(text='Saved AI preferences applied. Connect to check available models.')
        if saved['answer_language'] != previous['answer_language']:
            self.language.set(saved['answer_language'])
        self.controls()

    def controls(self):
        busy = self.task is not None
        self.endpoint.configure(state='disabled' if busy else 'normal')
        self.connect_button.configure(state='disabled' if busy else 'normal')
        self.model_menu.configure(state='normal' if self.models and not busy else 'disabled')
        self.language_menu.configure(state='disabled' if busy else 'normal')
        self.send_button.configure(state='normal' if self.models and not busy else 'disabled')
        self.stop_button.configure(state='normal' if busy else 'disabled')
        self.clear_button.configure(state='disabled' if busy else 'normal')
        self.prompt.configure(state='disabled' if busy else 'normal')

    def append(self, text):
        self.transcript.configure(state='normal')
        self.transcript.insert('end', text)
        self.transcript.configure(state='disabled')
        if self.app.current_page == 'AI Tutor':
            self.transcript.see('end')

    def connect(self):
        if self.task is not None:
            return
        self.pending_clear = False
        self.clear_button.configure(text='New chat')
        try:
            endpoint = endpoint_url(self.endpoint.get())
            if self.turns and self.connected_endpoint and endpoint != self.connected_endpoint:
                raise OllamaError('Start a new chat before connecting to a different server.')
            task = TutorTask('models', endpoint)
        except OllamaError as exc:
            self.status.configure(text=str(exc))
            return
        self.task = task
        self.request_endpoint = endpoint
        self.status.configure(text='Connecting to Ollama and loading models…')
        self.controls()
        task.start()

    def send(self):
        if self.task is not None:
            return
        self.pending_clear = False
        self.clear_button.configure(text='New chat')
        try:
            if endpoint_url(self.endpoint.get()) != self.connected_endpoint:
                raise OllamaError('Connect to the displayed server before sending.')
            if self.model.get() not in self.models:
                raise OllamaError('Connect and choose an available model.')
            messages = chat_messages(self.turns, self.prompt.get('1.0', 'end-1c'), self.language.get())
            if len(self.turns) >= 12:
                raise OllamaError('This session has 12 turns. Start a new chat to continue.')
            task = TutorTask('chat', self.connected_endpoint, model=self.model.get(), messages=messages)
        except OllamaError as exc:
            self.status.configure(text=str(exc))
            return
        question = messages[-1]['content']
        self.turns.append({'prompt': question, 'answer': '', 'status': 'pending'})
        self.prompt.delete('1.0', 'end')
        self.append(f'\nYou\n{question}\n\nTutor ({self.model.get()})\n')
        self.task = task
        self.status.configure(text='Generating… You can Stop or use another screen.')
        self.controls()
        task.start()

    def stop(self):
        if self.task is not None:
            self.task.cancel()
            self.status.configure(text='Stopping… Partial text will remain visible.')
            self.stop_button.configure(state='disabled')

    def new_chat(self):
        if self.task is not None:
            return
        if self.turns and not self.pending_clear:
            self.pending_clear = True
            self.clear_button.configure(text='Confirm clear')
            self.status.configure(text='Click Confirm clear again to remove this session chat. Send or Connect cancels this confirmation.')
            return
        self.pending_clear = False
        self.turns.clear()
        self.transcript.configure(state='normal')
        self.transcript.delete('1.0', 'end')
        self.transcript.configure(state='disabled')
        self.clear_button.configure(text='New chat')
        self.status.configure(text='New session chat. Connect if you changed the server.')

    def poll(self):
        if self.closed:
            return
        try:
            task = self.task
            if task is not None:
                for _ in range(200):
                    try:
                        kind, value = task.events.get_nowait()
                    except queue.Empty:
                        break
                    if kind == 'text':
                        self.turns[-1]['answer'] += value
                        self.append(value)
                    else:
                        stopped = kind == 'stopped' or (kind == 'done' and task.control.cancelled.is_set())
                        if task.kind == 'models':
                            if kind == 'done' and not stopped:
                                same_server = self.connected_endpoint == self.request_endpoint
                                self.connected_endpoint = self.request_endpoint
                                self.models = value
                                self.model_menu.configure(values=value or ['No models installed'])
                                missing_preference = bool(self.preferred_model and self.preferred_model not in value)
                                # A manual override belongs to its server; refresh may keep it.
                                if same_server and self.model.get() in value:
                                    selected = self.model.get()
                                elif self.preferred_model in value:
                                    selected = self.preferred_model
                                else:
                                    selected = '' if missing_preference else next(iter(value), 'No models installed')
                                self.model.set(selected)
                                notice = ('Preferred model is unavailable. Choose a listed model before sending.' if missing_preference and not selected else 'Ready. Choose a model and ask a study question.')
                                self.status.configure(text=notice if value else 'Connected, but no models are available. Install a model in Ollama, then refresh.')
                                self.app.ai_status.configure(text='○  AI ready' if value else '○  AI has no models')
                            else:
                                self.models = []
                                self.status.configure(text='Connection stopped.' if stopped else value)
                                self.app.ai_status.configure(text='○  AI not connected')
                        else:
                            state = 'stopped' if stopped else ('completed' if kind == 'done' else 'failed')
                            self.turns[-1]['status'] = state
                            notice = 'Reply complete.' if state == 'completed' else ('Stopped. Partial text is kept.' if stopped else value)
                            self.append(f'\n[{notice}]\n')
                            self.status.configure(text=notice)
                        self.task = None
                        self.controls()
                        break
        finally:
            if not self.closed:
                self.poll_job = self.after(50, self.poll)

    def shutdown(self):
        self.closed = True
        if self.task is not None:
            self.task.cancel()
        if getattr(self, 'poll_job', None):
            self.after_cancel(self.poll_job)
            self.poll_job = None

    def destroy(self):
        self.shutdown()
        super().destroy()
