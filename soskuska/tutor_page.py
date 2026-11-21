"""Optional Ollama chat with local history; all widget access stays on the Tk thread."""
from theme import COLORS as C
from localization_widgets import LocalizedOptionMenu
from localization import tr
import queue
import sqlite3

import customtkinter as ctk
from ollama_client import OllamaError, endpoint_url
from tutor import LANGUAGES, TutorTask, chat_messages


class TutorPage(ctk.CTkFrame):
    conversation_id = None
    conversation_endpoint = None
    conversation_model = None
    unsaved_reply = False
    def __init__(self, parent, app):
        super().__init__(parent, fg_color='transparent', corner_radius=0)
        self.app = app
        self.turns = []
        self.task = None
        self.closed = False
        self.connected_endpoint = None
        self.models = []
        self.pending_clear = False
        self.conversation_id = None; self.conversation_revision = 0
        self.conversation_endpoint = None; self.conversation_model = None
        self.unsaved_reply = False; self.pending_discard = False; self.pending_delete = None; self.pending_recover = False
        self.history_offset = 0; self.history_rows = {}; self.history_has_next = False
        self.grid_columnconfigure(0, weight=1)
        app.label(self, tr(self.app, 'AI Tutor'), 28, bold=True).grid(row=0, column=0, sticky='w')
        self.status = app.label(self, tr(self.app, 'Not connected. Start Ollama, then connect to load its models.'), 13, 'secondary', wraplength=600)
        self.status.grid(row=1, column=0, sticky='ew', pady=(6, 14))
        history = app.frame(self); history.grid(row=2,column=0,sticky='ew',pady=(0,12));history.grid_columnconfigure(0,weight=1)
        self.history_choice = ctk.StringVar(value='Choose saved conversation')
        self.history_menu = LocalizedOptionMenu(history,owner=self.app,translate_values=False,empty_text="No saved conversations",variable=self.history_choice,values=[],dynamic_resizing=False,height=36,font=app.font(),command=lambda _:self.cancel_delete())
        self.history_menu.grid(row=0,column=0,sticky='ew',padx=(0,8))
        self.open_button = app.button(history,tr(self.app, 'Open'),self.open_history,width=70);self.open_button.grid(row=0,column=1,padx=(0,8))
        self.history_refresh_button = app.button(history,tr(self.app, 'Refresh'),self.refresh_history,width=85);self.history_refresh_button.grid(row=0,column=2,padx=(0,8))
        self.delete_button = app.button(history,tr(self.app, 'Delete'),self.delete_history,width=85);self.delete_button.grid(row=0,column=3)
        pages = app.frame(history);pages.grid(row=1,column=0,columnspan=4,sticky='w',pady=(8,0))
        self.history_previous = app.button(pages,tr(self.app, 'Previous chats'),lambda:self.history_page(-1),width=125);self.history_previous.pack(side='left',padx=(0,8))
        self.history_next = app.button(pages,tr(self.app, 'Next chats'),lambda:self.history_page(1),width=110);self.history_next.pack(side='left')
        self.owner = app.label(history,tr(self.app, 'New chat — saved locally when you Send.'),12,'secondary',wraplength=600);self.owner.grid(row=2,column=0,columnspan=4,sticky='ew',pady=(8,0))
        connection = app.frame(self)
        connection.grid(row=3, column=0, sticky='ew', pady=(0, 12))
        connection.grid_columnconfigure(0, weight=1)
        self.endpoint = ctk.CTkEntry(connection, height=38, font=app.font(), placeholder_text_color=C["secondary"])
        self.endpoint.insert(0, app.preferences['ollama_endpoint'])
        self.endpoint.grid(row=0, column=0, sticky='ew', padx=(0, 8))
        self.connect_button = app.button(connection, tr(self.app, 'Connect / refresh'), self.connect, width=155)
        self.connect_button.grid(row=0, column=1)
        options = app.frame(self)
        options.grid(row=4, column=0, sticky='ew', pady=(0, 12))
        options.grid_columnconfigure(0, weight=1)
        self.preferred_model = app.preferences['ollama_model']
        self.model = ctk.StringVar(value=self.preferred_model or 'Connect to load models')
        self.model_menu = LocalizedOptionMenu(options,owner=self.app,translate_values=False,empty_text="Connect to load models" if not self.preferred_model else None, variable=self.model, values=[], dynamic_resizing=False, font=app.font(), height=38, state='disabled')
        app.label(options, tr(self.app, 'Model'), 12, 'secondary').grid(row=0, column=0, sticky='w')
        self.model_menu.grid(row=1, column=0, sticky='ew', padx=(0, 8))
        self.language = ctk.StringVar(value=app.preferences['answer_language'])
        self.language_menu = LocalizedOptionMenu(options,owner=self.app, variable=self.language, values=list(LANGUAGES), dynamic_resizing=False, font=app.font(), height=38, width=125)
        app.label(options, tr(self.app, 'Answer language'), 12, 'secondary').grid(row=0, column=1, sticky='w')
        self.language_menu.grid(row=1, column=1)
        self.info = app.label(self, tr(self.app, 'Chats are saved in the local database and included in backups. Only this chat is sent after Send; opening history never connects. AI answers may be incorrect; check important facts.'), 12, 'secondary', wraplength=600)
        self.info.grid(row=5, column=0, sticky='ew', pady=(0, 12))
        self.transcript = ctk.CTkTextbox(self, height=330, font=app.font(), wrap='word', state='disabled')
        self.transcript.grid(row=6, column=0, sticky='ew', pady=(0, 12))
        self.prompt = ctk.CTkTextbox(self, height=100, font=app.font(), wrap='word')
        app.label(self, tr(self.app, 'Your question (up to 4,000 characters)'), 12, 'secondary').grid(row=7, column=0, sticky='w')
        self.prompt.grid(row=8, column=0, sticky='ew', pady=(0, 12))
        actions = app.frame(self)
        actions.grid(row=9, column=0, sticky='ew')
        self.send_button = app.button(actions, tr(self.app, 'Send'), self.send, primary=True, width=95)
        self.send_button.pack(side='left', padx=(0, 8))
        self.stop_button = app.button(actions, tr(self.app, 'Stop'), self.stop, width=85)
        self.stop_button.pack(side='left', padx=(0, 8))
        self.clear_button = app.button(actions, tr(self.app, 'New chat'), self.new_chat, width=120)
        self.clear_button.pack(side='left')
        recovery = app.frame(self);recovery.grid(row=10,column=0,sticky='w',pady=(10,0))
        self.retry_button = app.button(recovery,tr(self.app, 'Retry save reply'),self.retry_save,width=145);self.retry_button.pack(side='left',padx=(0,8))
        self.discard_button = app.button(recovery,tr(self.app, 'Discard unsaved'),self.discard_unsaved,width=155);self.discard_button.pack(side='left',padx=(0,8))
        self.recover_button = app.button(recovery,tr(self.app, 'Mark interrupted'),self.recover_pending,width=155);self.recover_button.pack(side='left')
        self.bind('<Configure>', self.resize, add='+')
        self.controls()
        self.poll_job = self.after(50, self.poll)

    def resize(self, event):
        for label in (self.status, self.info, self.owner):
            label.configure(wraplength=max(250, event.width - 12))

    def load(self):
        self.pending_clear = False  # Navigation preserves chat; cancels clear confirmation.
        self.clear_button.configure(text=tr(self.app, 'New chat'))
        self.cancel_delete()
        self.pending_recover=False;self.recover_button.configure(text=tr(self.app, 'Mark interrupted'))
        self.refresh_history()

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
                self.app.ai_status.configure(text=tr(self.app, '○  AI not connected'))
        if model_changed:
            self.preferred_model = saved['ollama_model']
        if endpoint_changed or model_changed:
            if not self.models:
                self.model_menu.configure(values=[],empty_text=None if self.preferred_model else 'Connect to load models')
            self.model.set(self.preferred_model if not self.models or self.preferred_model in self.models else '')
            self.status.configure(text=tr(self.app, 'Saved AI preferences applied. Connect to check available models.'))
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
        self.clear_button.configure(state='disabled' if busy or self.unsaved_reply else 'normal')
        for button in (self.open_button,self.history_refresh_button,self.delete_button,self.history_menu):
            button.configure(state='disabled' if busy or self.unsaved_reply else 'normal')
        self.history_previous.configure(state='normal' if self.history_offset and not busy and not self.unsaved_reply else 'disabled')
        self.history_next.configure(state='normal' if self.history_has_next and not busy and not self.unsaved_reply else 'disabled')
        self.retry_button.configure(state='normal' if self.unsaved_reply and not busy else 'disabled')
        self.discard_button.configure(state='normal' if self.unsaved_reply and not busy else 'disabled')
        self.recover_button.configure(state='normal' if self.turns and self.turns[-1]['status']=='pending' and not busy and not self.unsaved_reply else 'disabled')
        if self.unsaved_reply:self.send_button.configure(state='disabled')
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
        self.clear_button.configure(text=tr(self.app, 'New chat'))
        try:
            endpoint = endpoint_url(self.endpoint.get())
            owner = self.conversation_endpoint or self.connected_endpoint
            if self.turns and owner and endpoint != owner:
                raise OllamaError('Start a new chat before connecting to a different server.')
            task = TutorTask('models', endpoint)
        except OllamaError as exc:
            self.status.configure(text=tr(self.app, str(exc)))
            return
        self.task = task
        self.request_endpoint = endpoint
        self.status.configure(text=tr(self.app, 'Connecting to Ollama and loading models…'))
        self.controls()
        task.start()

    def send(self):
        if self.task is not None or self.unsaved_reply:
            return
        self.pending_clear = False
        self.clear_button.configure(text=tr(self.app, 'New chat'))
        try:
            if endpoint_url(self.endpoint.get()) != self.connected_endpoint:
                raise OllamaError('Connect to the displayed server before sending.')
            if self.model.get() not in self.models:
                raise OllamaError('Connect and choose an available model.')
            if self.conversation_id is not None and (self.connected_endpoint,self.model.get()) != (self.conversation_endpoint,self.conversation_model):
                raise OllamaError('Start a New chat before changing this conversation’s server or model.')
            messages = chat_messages(self.turns, self.prompt.get('1.0', 'end-1c'), self.language.get())
            if len(self.turns) >= 12:
                raise OllamaError('This session has 12 turns. Start a new chat to continue.')
            task = TutorTask('chat', self.connected_endpoint, model=self.model.get(), messages=messages)
        except OllamaError as exc:
            self.status.configure(text=tr(self.app, str(exc)))
            return
        question = messages[-1]['content']
        try:
            saved = self.app.store.begin_tutor_turn(self.conversation_id,self.connected_endpoint,self.model.get(),question,self.language.get(),expected_revision=self.conversation_revision)
        except (ValueError,sqlite3.Error) as exc:
            self.status.configure(text=tr(self.app,tr(self.app, str(exc)) if isinstance(exc, ValueError) else tr(self.app, 'Could not save the question. Your draft is kept; retry Send.')));return
        self.conversation_id=saved['id'];self.conversation_revision=saved['revision']
        self.conversation_endpoint=saved['endpoint'];self.conversation_model=saved['model']
        self.owner.configure(text=tr(self.app, '{v0} · {v1} · {v2}', v0=saved['title'], v1=self.conversation_endpoint, v2=self.conversation_model))
        self.turns.append({'id':saved['turn_id'],'prompt':question,'answer':'','status':'pending'})
        self.prompt.delete('1.0', 'end')
        self.append(tr(self.app, '\nYou\n{v0}\n\nTutor ({v1})\n', v0=question, v1=self.model.get()))
        self.task = task
        self.status.configure(text=tr(self.app, 'Generating… You can Stop or use another screen.'))
        self.controls()
        try:task.start()
        except RuntimeError:
            self.task=None;self.turns[-1]['status']='failed';self.unsaved_reply=True
            self.status.configure(text=tr(self.app, 'Could not start the request.'));self.persist_reply();self.controls()

    def stop(self):
        if self.task is not None:
            self.task.cancel()
            self.status.configure(text=tr(self.app, 'Stopping… Partial text will remain visible.'))
            self.stop_button.configure(state='disabled')

    def new_chat(self):
        if self.task is not None or self.unsaved_reply:
            return
        if (self.turns or self.prompt.get('1.0','end-1c').strip()) and not self.pending_clear:
            self.pending_clear = True
            self.clear_button.configure(text=tr(self.app, 'Confirm clear'))
            self.status.configure(text=tr(self.app, 'Click Confirm clear again to start a new chat and clear the prompt draft. Saved history is kept. Send or Connect cancels this confirmation.'))
            return
        self.pending_clear = False
        self.turns.clear()
        self.conversation_id=None;self.conversation_revision=0;self.conversation_endpoint=None;self.conversation_model=None
        self.prompt.delete('1.0','end');self.owner.configure(text=tr(self.app, 'New chat — saved locally when you Send.'))
        self.cancel_delete()
        self.transcript.configure(state='normal')
        self.transcript.delete('1.0', 'end')
        self.transcript.configure(state='disabled')
        self.clear_button.configure(text=tr(self.app, 'New chat'))
        self.status.configure(text=tr(self.app, 'New chat. Saved history is kept. Connect if you changed the server.'))
        self.controls()

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
                                self.model_menu.configure(values=value,empty_text="No models installed" if not value else None)
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
                                self.status.configure(text=tr(self.app,notice if value else tr(self.app, 'Connected, but no models are available. Install a model in Ollama, then refresh.')))
                                self.app.ai_status.configure(text=tr(self.app, '○  AI ready') if value else tr(self.app, '○  AI has no models'))
                            else:
                                self.models = []
                                self.status.configure(text=tr(self.app,tr(self.app, 'Connection stopped.') if stopped else value))
                                self.app.ai_status.configure(text=tr(self.app, '○  AI not connected'))
                        else:
                            state = 'stopped' if stopped else ('completed' if kind == 'done' else 'failed')
                            self.turns[-1]['status'] = state
                            notice = 'Reply complete.' if state == 'completed' else ('Stopped. Partial text is kept.' if stopped else value)
                            self.append(tr(self.app, '\n[{v0}]\n', v0=tr(self.app,notice)))
                            self.status.configure(text=tr(self.app, notice))
                            self.unsaved_reply=True
                            self.persist_reply()
                        self.task = None
                        self.controls()
                        if task.kind=="chat":self.refresh_history()
                        break
        finally:
            if not self.closed:
                self.poll_job = self.after(50, self.poll)

    def refresh_history(self, offset=None):
        if self.task is not None or self.unsaved_reply:return
        candidate=self.history_offset if offset is None else offset
        try:
            rows=self.app.store.tutor_conversations(candidate)
            if not rows and candidate:
                candidate=0;rows=self.app.store.tutor_conversations(candidate)
        except sqlite3.Error:
            self.status.configure(text=tr(self.app, 'Could not read history. Retry Refresh; your current chat is kept.'));return
        self.history_offset=candidate
        self.history_has_next=len(rows)>20
        self.history_rows={f'{r["id"]} · {r["title"][:40]}':r for r in rows[:20]}
        values=list(self.history_rows) or ['No saved conversations']
        previous=self.history_choice.get()
        self.history_menu.configure(values=list(self.history_rows))
        self.history_choice.set(previous if previous in values else values[0])
        self.cancel_delete();self.controls()

    def history_page(self, direction):
        if self.task is not None or self.unsaved_reply:return
        self.refresh_history(offset=max(0,self.history_offset+direction*20))

    def cancel_delete(self):
        self.pending_delete=None;self.delete_button.configure(text=tr(self.app, 'Delete'))

    def open_history(self):
        if self.task is not None or self.unsaved_reply:return
        selected=self.history_rows.get(self.history_choice.get())
        if selected is None:return
        if self.prompt.get('1.0','end-1c').strip() and self.conversation_id!=selected['id']:
            self.status.configure(text=tr(self.app, 'Your question draft is kept. Clear it explicitly before opening another conversation.'));return
        try:saved=self.app.store.tutor_conversation(selected['id'])
        except (ValueError,sqlite3.Error) as exc:
            self.status.configure(text=tr(self.app,tr(self.app, str(exc)) if isinstance(exc, ValueError) else tr(self.app, 'Could not open history. Retry Open; current chat is kept.')));return
        self.conversation_id=saved['id'];self.conversation_revision=saved['revision']
        self.conversation_endpoint=saved['endpoint'];self.conversation_model=saved['model']
        self.turns=saved['turns'];self.cancel_delete();self.pending_clear=False;self.pending_recover=False
        self.clear_button.configure(text=tr(self.app, 'New chat'));self.recover_button.configure(text=tr(self.app, 'Mark interrupted'))
        self.endpoint.delete(0,'end');self.endpoint.insert(0,saved['endpoint'])
        self.connected_endpoint=None;self.models=[];self.preferred_model=saved['model'];self.model_menu.configure(values=[],empty_text=None);self.model.set(saved['model'])
        self.app.ai_status.configure(text=tr(self.app, '○  AI not connected'))
        if self.turns:self.language.set(self.turns[-1]['language'])
        self.owner.configure(text=tr(self.app, '{v0} · {v1} · {v2}', v0=saved['title'], v1=saved['endpoint'], v2=saved['model']))
        self.transcript.configure(state='normal');self.transcript.delete('1.0','end');self.transcript.configure(state='disabled')
        for turn in self.turns:
            self.append(tr(self.app, '\nYou\n{v0}\n\nTutor ({v1})\n{v2}\n[{v3}]\n', v0=turn['prompt'], v1=saved['model'], v2=turn['answer'], v3=tr(self.app,turn['status'])))
        self.status.configure(text=tr(self.app, 'Saved chat opened offline. Connect to its server/model to continue. An unfinished reply may belong to another window; Mark interrupted only if you intend to abandon it.'))
        self.controls()

    def delete_history(self):
        if self.task is not None or self.unsaved_reply:return
        selected=self.history_rows.get(self.history_choice.get())
        if selected is None:return
        identity=(selected['id'],selected['revision'])
        if self.pending_delete!=identity:
            self.pending_delete=identity;self.delete_button.configure(text=tr(self.app, 'Confirm'))
            self.status.configure(text=tr(self.app, 'Delete saved chat "{v0}" and all its turns? Click Confirm again. This also invalidates a reply running in another window.', v0=selected['title']));return
        try:self.app.store.delete_tutor_conversation(identity[0],expected_revision=identity[1])
        except (ValueError,sqlite3.Error) as exc:
            self.cancel_delete();self.status.configure(text=tr(self.app,tr(self.app, str(exc)) if isinstance(exc, ValueError) else tr(self.app, 'Could not delete history. Nothing was removed; retry.')));return
        if self.conversation_id==identity[0]:
            # Current chat is already saved; detach it without losing a prompt draft.
            self.turns=[];self.conversation_id=None;self.conversation_revision=0;self.conversation_endpoint=None;self.conversation_model=None
            self.transcript.configure(state='normal');self.transcript.delete('1.0','end');self.transcript.configure(state='disabled')
            self.owner.configure(text=tr(self.app, 'New chat — saved locally when you Send.'))
        self.refresh_history();self.status.configure(text=tr(self.app, 'Conversation deleted. Other chats and any prompt draft are kept.'))

    def persist_reply(self):
        if not self.unsaved_reply:return True
        turn=self.turns[-1]
        try:revision=self.app.store.finish_tutor_turn(self.conversation_id,turn['id'],turn['answer'],turn['status'],expected_revision=self.conversation_revision)
        except (ValueError,sqlite3.Error) as exc:
            reason=str(exc) if isinstance(exc,ValueError) else 'Could not save the reply.'
            self.status.configure(text=tr(self.app,tr(self.app,reason) + tr(self.app,' Unsaved text is kept. Retry save reply, or copy it before Discard unsaved.')));return False
        self.conversation_revision=revision;self.unsaved_reply=False;self.pending_discard=False
        self.discard_button.configure(text=tr(self.app, 'Discard unsaved'));return True

    def retry_save(self):
        if self.task is not None:return
        if self.persist_reply():self.status.configure(text=tr(self.app, 'Reply saved locally.'));self.refresh_history()
        self.controls()

    def discard_unsaved(self):
        if self.task is not None or not self.unsaved_reply:return
        if not self.pending_discard:
            self.pending_discard=True;self.discard_button.configure(text=tr(self.app, 'Confirm discard'))
            self.status.configure(text=tr(self.app, 'Copy the unsaved reply first. Click Confirm discard to clear it; saved history (possibly unfinished) is kept.'));return
        self.unsaved_reply=False;self.pending_discard=False
        draft=self.prompt.get('1.0','end-1c')
        self.turns=[];self.prompt.delete('1.0','end');self.new_chat()
        self.prompt.insert('1.0',draft);self.discard_button.configure(text=tr(self.app, 'Discard unsaved'))
        self.status.configure(text=tr(self.app, 'Unsaved reply discarded. Your question draft and saved history are kept.'))

    def recover_pending(self):
        if self.task is not None or self.unsaved_reply or not self.turns or self.turns[-1]['status']!='pending':return
        if not self.pending_recover:
            self.pending_recover=True;self.recover_button.configure(text=tr(self.app, 'Confirm interruption'))
            self.status.configure(text=tr(self.app, 'This reply might be running in another window. Confirm interruption to abandon its saved pending turn; a late response cannot overwrite it.'));return
        self.turns[-1]['status']='interrupted';self.unsaved_reply=True
        if self.persist_reply():self.status.configure(text=tr(self.app, 'Marked interrupted. Connect to continue; incomplete turns are excluded from context.'))
        self.pending_recover=False;self.recover_button.configure(text=tr(self.app, 'Mark interrupted'));self.controls()

    def prepare_close(self):
        if self.task is not None and self.task.kind=='chat':
            self.turns[-1]['status']='interrupted';self.unsaved_reply=True
        if not self.persist_reply():
            if self.task is not None:self.task.cancel()
            self.controls();return False
        return True

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
