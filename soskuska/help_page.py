"""In-app Help: offline topics with search. Reads only the bundled help file; no database or network."""
import json

import customtkinter as ctk

from help_content import PAGE_TOPICS, display, load_topics, search
from localization import tr
from theme import COLORS as C

SIDE_MIN_WIDTH = 900   # Logical width at which topics sit beside the article.
TOPIC_COLUMN = 296     # Logical width of the side topic list.
MARKER = 40            # Step-number/bullet column inside the article, padding included.


class HelpPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color='transparent', corner_radius=0)
        self.app = app
        self.language = app.translator.language
        self.topics = None
        self.by_id = {}
        self.visible = []
        self.selected = None
        self.side = None
        self.wrap = 560
        self.grid_columnconfigure(0, weight=1)
        header = app.frame(self, card=True)
        header.grid(row=0, column=0, sticky='ew', pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)
        app.label(header, tr(app, 'Help'), 28, bold=True).grid(row=0, column=0, sticky='w', padx=18, pady=(16, 6))
        # Returns to the page Help was opened from (reloaded through normal navigation).
        self.back_button = app.button(header, '', app.back_from_help)
        self.back_button.grid(row=0, column=1, sticky='e', padx=18, pady=(16, 6))
        self.back_button.grid_remove()
        self.intro = tr(app, 'Short guides to every part of SOSkúška. Help works offline and never changes your data.')
        self.status = app.label(header, self.intro, 13, 'secondary', wraplength=600, justify='left')
        self.status.grid(row=1, column=0, columnspan=2, sticky='ew', padx=18, pady=(0, 12))
        self.query = ctk.StringVar()
        # CTkEntry hides placeholder text when a textvariable is set, so label the field (as on the Dashboard).
        self.search_label = app.label(header, tr(app, 'Search help…'), 11, 'secondary')
        self.search_label.grid(row=2, column=0, columnspan=2, sticky='w', padx=18, pady=(0, 4))
        self.search = ctk.CTkEntry(header, height=38, corner_radius=18,
                                   textvariable=self.query, fg_color=C['card'], border_width=1, border_color=C['outline'],
                                   text_color=C['text'], font=app.font(13))
        self.search.grid(row=3, column=0, columnspan=2, sticky='ew', padx=18, pady=(0, 16))
        self.matches = app.label(header, '', 11, 'secondary', wraplength=600, justify='left')
        self.matches.grid(row=4, column=0, columnspan=2, sticky='ew', padx=18, pady=(0, 14))
        self.matches.grid_remove()  # Shown only while a search is active.
        self.query.trace_add('write', lambda *_: self.filter())
        self.body = app.frame(self)
        self.body.grid(row=1, column=0, sticky='ew')
        self.topic_card = app.frame(self.body, card=True)
        self.topic_card.grid_columnconfigure(0, weight=1)
        self.topic_list = app.frame(self.topic_card)
        self.topic_list.grid(row=0, column=0, sticky='ew', padx=8, pady=8)
        self.topic_list.grid_columnconfigure((0, 1), weight=1, uniform='help-topics')
        self.article = app.frame(self.body, card=True)
        self.article.grid_columnconfigure(1, weight=1)
        self.topic_buttons = {}
        self.bind('<Configure>', self.resize, add='+')

    # ----- loading and layout -------------------------------------------------
    def ensure_loaded(self):
        if self.topics is not None:
            return True
        try:
            topics = load_topics(self.language)
        except (OSError, ValueError, json.JSONDecodeError):
            self.status.configure(text=tr(self.app, 'Help could not be loaded. Reinstall or update SOSkúška to restore it.'))
            return False
        self.topics, self.by_id = topics, {topic['id']: topic for topic in topics}
        for topic in topics:
            self.topic_buttons[topic['id']] = ctk.CTkButton(
                self.topic_list, text=topic['title'], anchor='w', height=36, corner_radius=12, font=self.app.font(13),
                fg_color='transparent', hover_color=C['secondary_hover'], text_color=C['text'], border_width=0,
                command=lambda topic_id=topic['id']: self.show(topic_id, reveal=True))
        self.visible = list(topics)
        width = int(self.app.scroll.viewport_width()) - 56
        self.side = width >= SIDE_MIN_WIDTH
        self.wrap = max(200, width - (TOPIC_COLUMN + 16 if self.side else 0) - 36 - MARKER)
        self.layout()
        return True

    def resize(self, event):
        width = int(self.app.scroll.logical_pixels(event.width))
        side = width >= SIDE_MIN_WIDTH
        article = width - (TOPIC_COLUMN + 16 if side else 0)
        # Derive wrapping from this page's stable width, never from a child's rounded width.
        wrap = max(200, article - 36 - MARKER)
        for label in (self.status, self.matches):
            if label.cget('wraplength') != max(200, width - 36):
                label.configure(wraplength=max(200, width - 36))
        if side != self.side:
            self.side = side
            self.layout()
        if wrap != self.wrap:
            self.wrap = wrap
            for label in self.wrapped_labels():
                label.configure(wraplength=wrap + (MARKER if label.wide else 0))

    def layout(self):
        if self.topics is None:
            return
        side = bool(self.side)
        self.body.grid_columnconfigure(0, weight=0 if side else 1,
                                       minsize=round(self.app.scroll.native_pixels(TOPIC_COLUMN)) if side else 0)
        self.body.grid_columnconfigure(1, weight=1 if side else 0)
        self.topic_card.grid(row=0, column=0, sticky='new', padx=(0, 16) if side else 0, pady=0 if side else (0, 16))
        self.article.grid(row=0 if side else 1, column=1 if side else 0, sticky='new')
        self.place_topics()

    def place_topics(self):
        columns = 1 if self.side else 2
        self.topic_list.grid_columnconfigure(1, weight=0 if columns == 1 else 1, uniform='' if columns == 1 else 'help-topics')
        # Grid matches in search rank (title hits first); hide the rest.
        visible = [topic['id'] for topic in self.visible]
        for topic in self.topics:
            if topic['id'] not in visible:
                self.topic_buttons[topic['id']].grid_remove()
        for index, topic_id in enumerate(visible):
            row, col = divmod(index, columns)
            self.topic_buttons[topic_id].grid(row=row, column=col, sticky='ew', padx=2, pady=2)
        self.mark_selected()

    def mark_selected(self):
        for topic_id, button in self.topic_buttons.items():
            active = topic_id == self.selected
            button.configure(fg_color=C['selected'] if active else 'transparent',
                             text_color=C['hover'] if active else C['text'], font=self.app.font(13, active))

    # ----- navigation entry points -------------------------------------------
    def open(self, context=None, notice=None):
        """Show Help; a page name selects that page's topic and clears an old search.

        `notice` explains staged work that leaving the page cancelled."""
        if not self.ensure_loaded():
            return
        self.status.configure(text=notice or self.intro,
                              text_color=C['warning'] if notice else C['secondary'])
        if context in PAGE_TOPICS:
            self.back_button.configure(text=tr(self.app, '← Back to {v0}', v0=tr(self.app, context)))
            self.back_button.grid()
        else:
            self.back_button.grid_remove()
        topic_id = PAGE_TOPICS.get(context)
        if topic_id is not None:
            if self.query.get():
                self.query.set('')
            self.show(topic_id)
        elif self.selected is None:
            self.show(self.topics[0]['id'])

    def filter(self):
        if self.topics is None:
            return
        query = self.query.get()
        self.visible = search(self.topics, query)
        self.place_topics()
        if not query.strip():
            self.matches.configure(text='')
            self.matches.grid_remove()
        else:
            self.matches.configure(text=tr(self.app, 'No help topics match your search. Try another word.') if not self.visible
                                   else tr(self.app, '{v0} of {v1} help topics match.', v0=len(self.visible), v1=len(self.topics)))
            self.matches.grid()
        if self.visible and self.selected not in {topic['id'] for topic in self.visible}:
            self.show(self.visible[0]['id'])

    # ----- article rendering --------------------------------------------------
    def wrapped_labels(self):
        return [w for w in self.article.winfo_children() if isinstance(w, ctk.CTkLabel) and hasattr(w, 'wide')]

    def text_label(self, text, row, size=13, color='text', bold=False, wide=True, column=0, pady=(4, 4)):
        label = self.app.label(self.article, display(text, self.language), size, color, bold=bold, justify='left',
                               wraplength=self.wrap + (MARKER if wide else 0))
        label.wide = wide
        if wide:
            label.grid(row=row, column=0, columnspan=2, sticky='ew', padx=18, pady=pady)
        else:
            label.grid(row=row, column=column, sticky='new', padx=(0, 18), pady=pady)
        return label

    def show(self, topic_id, reveal=False):
        if self.topics is None or topic_id not in self.by_id:
            return
        self.selected = topic_id
        self.mark_selected()
        topic = self.by_id[topic_id]
        for child in self.article.winfo_children():
            child.destroy()
        row = 0
        self.title = self.text_label(topic['title'], row, 24, bold=True, pady=(18, 4)); row += 1
        self.text_label(topic['summary'], row, 13, 'secondary', pady=(0, 10)); row += 1
        for block in topic['blocks']:
            kind, value = next(iter(block.items()))
            if kind == 'heading':
                self.text_label(value, row, 16, bold=True, pady=(12, 2)); row += 1
            elif kind == 'text':
                self.text_label(value, row); row += 1
            else:
                for number, item in enumerate(value, 1):
                    marker = f'{number}.' if kind == 'steps' else '•'
                    ctk.CTkLabel(self.article, text=marker, font=self.app.font(13, True), text_color=C['hover'],
                                 width=MARKER - 6, anchor='e').grid(row=row, column=0, sticky='ne', padx=(18, 6), pady=(4, 4))
                    self.text_label(item, row, wide=False, column=1); row += 1
        actions = self.app.frame(self.article)
        actions.grid(row=row, column=0, columnspan=2, sticky='ew', padx=18, pady=(14, 18))
        self.open_button = None
        if topic['page']:
            self.open_button = self.app.button(actions, tr(self.app, 'Open {v0}', v0=tr(self.app, topic['page'])),
                                               lambda page=topic['page']: self.app.navigate(page), primary=True)
            self.open_button.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))
        if topic['related']:
            self.app.label(actions, tr(self.app, 'See also'), 12, 'secondary', bold=True).grid(
                row=1, column=0, columnspan=2, sticky='w', pady=(4, 4))
            for index, related in enumerate(topic['related']):
                self.app.button(actions, self.by_id[related]['title'], lambda target=related: self.show(target, reveal=True)).grid(
                    row=2 + index // 2, column=index % 2, sticky='w', padx=(0, 8), pady=(0, 8))
        if reveal and self.app.current_page == 'Help':
            if self.side:
                self.app.scroll.scroll_to_top()
            else:
                self.app.scroll.scroll_to_widget(self.article)
