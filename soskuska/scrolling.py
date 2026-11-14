"""Compatibility for precise Tk 9 scrolling and legacy mouse wheels.

CTk 5.2.2 only binds MouseWheel; Tk 9 trackpads emit TouchpadScroll.
Keep access to CTk's internal canvas isolated in this adapter.
Tk event format: https://core.tcl-lang.org/tips/doc/main/tip/684.md
"""
import sys
import tkinter

import customtkinter as ctk


def touchpad_deltas(packed):
    """Decode signed X/Y deltas from Tk's packed 32-bit event field."""
    raw = int(packed) & 0xFFFFFFFF
    x, y = (raw >> 16) & 0xFFFF, raw & 0xFFFF
    return (x - 65536 if x >= 32768 else x,
            y - 65536 if y >= 32768 else y)


class DashboardScrollFrame(ctk.CTkScrollableFrame):
    def __init__(self, *args, **kwargs):
        self._wheel_remainder = 0.0
        super().__init__(*args, **kwargs)
        # Precise events report pixel distances; one canvas unit must be one pixel.
        self._parent_canvas.configure(yscrollincrement=1)
        root = self.winfo_toplevel()
        if tkinter.TkVersion >= 9:
            root.bind("<TouchpadScroll>", self._touchpad_scroll, add="+")
        elif self.tk.call("tk", "windowingsystem") == "x11":
            root.bind("<Button-4>", self._legacy_wheel, add="+")
            root.bind("<Button-5>", self._legacy_wheel, add="+")

    def _owns_event(self, widget):
        while widget is not None:
            if widget in (self._parent_canvas, self._scrollbar):
                return True
            widget = getattr(widget, "master", None)
        return False

    def _scrollable_text(self, widget):
        """Find the native text behind an editor's writing area, border or scrollbar."""
        while widget is not None:
            if isinstance(widget, (tkinter.Text, ctk.CTkTextbox)):
                first, last = widget.yview()
                if last - first < 1:
                    if isinstance(widget, tkinter.Text):
                        return widget
                    return next((child for child in widget.winfo_children()
                                 if isinstance(child, tkinter.Text)), None)
            widget = getattr(widget, "master", None)
        return None

    def _scroll_pixels(self, pixels):
        self._wheel_remainder += pixels
        whole_pixels = int(self._wheel_remainder)
        self._wheel_remainder -= whole_pixels
        if whole_pixels:
            self._parent_canvas.yview_scroll(whole_pixels, "units")

    def _mouse_wheel_all(self, event):
        if not self._owns_event(event.widget) or self._shift_pressed:
            return
        if self._scrollable_text(event.widget) is not None:
            return  # Native Text/CTkScrollbar wheel bindings already scroll the editor.
        # Tk 9 normalizes conventional wheels to 120 per notch on every OS.
        # Earlier Aqua versions use small deltas rather than multiples of 120.
        scale = 8 if sys.platform == "darwin" and tkinter.TkVersion < 9 else 40 / 120
        self._scroll_pixels(-event.delta * scale)
        return "break"

    def _touchpad_scroll(self, event):
        if not self._owns_event(event.widget):
            return
        text = self._scrollable_text(event.widget)
        if text is not None:
            # Canvas borders/scrollbars lack Tk's Text touchpad binding. Forward
            # to Text once; events originating there were already handled by Tk.
            if event.widget is not text:
                text.event_generate("<TouchpadScroll>", delta=event.delta)
            return "break"
        _, delta_y = touchpad_deltas(event.delta)
        if delta_y:
            self._scroll_pixels(-delta_y)
            return "break"

    def _legacy_wheel(self, event):
        if self._owns_event(event.widget) and self._scrollable_text(event.widget) is None:
            self._scroll_pixels(-40 if event.num == 4 else 40)
            return "break"
