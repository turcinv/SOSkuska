"""Widget-local layout helpers; no reads, state changes or global bindings."""
import customtkinter as ctk


def wrap_labels(parent, app, *, source=None, columns=None, inset=36):
    labels=[w for w in parent.winfo_children() if isinstance(w,ctk.CTkLabel)]
    for label in labels:
        label.configure(justify='left',wraplength=500)
    source=source if source is not None else parent
    def resize(event):
        available=app.scroll.logical_pixels(event.width)
        count=columns(available) if columns else 1
        width=max(160,int(available/count)-(12 if count>1 else 0)-inset-4)
        for label in labels:
            if label.cget('wraplength')!=width:
                label.configure(wraplength=width)
    source.bind('<Configure>',resize,add='+')


def responsive_actions(parent, app, buttons):
    mode=None
    def resize(event):
        nonlocal mode
        columns=3 if app.scroll.logical_pixels(event.width)>=850 else 2
        if columns==mode:return
        mode=columns
        for index,button in enumerate(buttons):
            button.grid(row=index//columns,column=index%columns,sticky='w',padx=(0,8),pady=(0,8))
    parent.bind('<Configure>',resize,add='+')
    # A gridded child gives the action frame its initial height before Configure.
    for index,button in enumerate(buttons):
        button.grid(row=index//2,column=index%2,sticky='w',padx=(0,8),pady=(0,8))
