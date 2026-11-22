"""Public CTk appearance API with a System fallback avoiding continuous desktop polling on Linux."""
import sys
import customtkinter as ctk

SYSTEM_MODE_SUPPORTED = sys.platform in ('win32', 'darwin')


def apply_appearance(mode):
    # darkdetect 0.8 Linux calls gsettings synchronously; CTk polls every 30ms.
    # Do not start that command loop on Tk. Native Windows/macOS detection uses
    # local APIs; other platforms deliberately resolve System to Light.
    ctk.set_appearance_mode('Light' if mode == 'System' and not SYSTEM_MODE_SUPPORTED else mode)
