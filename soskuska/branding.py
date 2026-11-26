"""Local app identity shared by the sidebar and native window icon."""
from pathlib import Path
import sys
import tkinter as tk

import customtkinter as ctk
from PIL import Image

ASSETS = Path(__file__).resolve().parent / 'assets' / 'brand'


def sidebar_logo():
    with Image.open(ASSETS / 'logo-128.png') as source:
        image = source.copy()
    return ctk.CTkImage(light_image=image, dark_image=image, size=(36, 36))


def install_window_icon(window):
    # Public iconbitmap prevents CTk's delayed Windows default icon override.
    if sys.platform == 'win32':
        window.iconbitmap(str(ASSETS / 'soskuska.ico'))
    # Aqua consumes only the first image; use its recommended large source.
    sizes = (512,) if sys.platform == 'darwin' else (256, 128, 64, 48, 32, 16)
    icons = tuple(tk.PhotoImage(master=window, file=str(ASSETS / f'logo-{size}.png'))
                  for size in sizes)
    window.iconphoto(True, *icons)
    # Tk image names are interpreter-local and need Python references per root.
    window.brand_window_icons = icons
