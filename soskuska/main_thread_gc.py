"""Run Python's cyclic garbage collector only on the Tk thread.

Automatic collection runs in whichever thread happens to allocate. When a Tutor
or AI-drafting worker thread triggers it, unreachable Tk objects (fonts,
variables, images) are finalized there and call into Tcl from the wrong thread.
In the Linux test container that blocked the worker for about 4 seconds
("main thread is not in main loop"); thread-side collection previously crashed
Tk on macOS. Disabling automatic collection and running the same
generation-threshold policy from a Tk timer keeps every finalizer on the main
thread while still reclaiming cycles.
"""
import gc
import tkinter

INTERVAL_MS = 200


def collect_due():
    """Collect the generation CPython would collect now; return it, or None."""
    count, threshold = gc.get_count(), gc.get_threshold()
    if threshold[0] <= 0 or count[0] <= threshold[0]:
        return None
    generation = next(g for g in (2, 1, 0) if count[g] > threshold[g])
    gc.collect(generation)
    return generation


def install(root, interval_ms=INTERVAL_MS):
    """Disable automatic collection and collect from `root`'s event loop."""
    gc.disable()

    def tick():
        try:
            collect_due()
        finally:
            try:
                root.after(interval_ms, tick)
            except (RuntimeError, tkinter.TclError):
                pass  # Window destroyed or interpreter shutting down.
    root.after(interval_ms, tick)
