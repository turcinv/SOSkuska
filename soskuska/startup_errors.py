"""Keep startup failures visible when the frozen GUI has no console."""
import sys


def report_startup_error(error):
    message = f'Could not open the study workspace: {error}'
    if getattr(sys, 'frozen', False):
        from tkinter import messagebox
        messagebox.showerror('SOSkúška — Startup error', message)
    else:
        print(message, file=sys.stderr)
