"""Localized option labels with canonical variables and explicit user-data boundaries."""
import tkinter
import customtkinter as ctk
from localization import tr, LANGUAGE_NAMES
from theme import COLORS as C


class LocalizedOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, master, *, owner, variable, values, command=None, translate_values=True, empty_text=None, **kwargs):
        self.owner=owner;self.canonical=variable;self.canonical_values=list(values)
        self.original_command=command;self.translate_values=translate_values;self.empty_text=empty_text
        self.display_variable=ctk.StringVar(master=master)
        self._mapping={}
        displayed=self.labels(values)
        self.display_variable.set(self.current_label())
        for key, role in dict(fg_color='raised', button_color='border', button_hover_color='selected',
            text_color='text', text_color_disabled='secondary', dropdown_fg_color='card',
            dropdown_text_color='text', dropdown_hover_color='raised').items():
            kwargs.setdefault(key, C[role])
        super().__init__(master,variable=self.display_variable,values=displayed,command=self.selected,**kwargs)
        self.canonical_trace=variable.trace_add('write',self.sync)

    def label(self,value):
        if self.translate_values=='language_names':return LANGUAGE_NAMES.get(value,value)
        return tr(self.owner,value) if self.translate_values else value

    def labels(self,values):
        labels=[self.label(value) for value in values]
        # Duplicate display text must not change the selected domain identity.
        if len(set(labels))!=len(labels):labels=list(values)
        self._mapping=dict(zip(labels,values));return labels

    def current_label(self):
        if not self.canonical_values and self.empty_text is not None:return tr(self.owner,self.empty_text)
        value=self.canonical.get()
        return next((label for label,key in self._mapping.items() if key==value),self.label(value))

    def sync(self,*_):
        self.display_variable.set(self.current_label())

    def selected(self,label):
        if label not in self._mapping:return
        value=self._mapping[label];self.canonical.set(value)
        if self.original_command:self.original_command(value)

    def configure(self,require_redraw=False,**kwargs):
        if 'empty_text' in kwargs:self.empty_text=kwargs.pop('empty_text')
        if 'values' in kwargs:
            self.canonical_values=list(kwargs['values']);kwargs['values']=self.labels(self.canonical_values)
        result=super().configure(require_redraw=require_redraw,**kwargs)
        if hasattr(self,'canonical_trace'):self.sync()
        return result

    def get(self):return self.canonical.get()

    def set(self,value):self.canonical.set(value)

    def destroy(self):
        if getattr(self,'canonical_trace',None):
            try:self.canonical.trace_remove('write',self.canonical_trace)
            except tkinter.TclError:pass
            self.canonical_trace=None
        super().destroy()
