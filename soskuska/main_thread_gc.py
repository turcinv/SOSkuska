"""Run Python's cyclic garbage collector only on the Tk thread.

Automatic collection runs in whichever thread happens to allocate. When a Tutor
or AI-drafting worker thread triggers it, unreachable Tk objects (fonts,
variables, images) are finalized there and call into Tcl from the wrong thread.
In the Linux test container that blocked the worker for about 4 seconds
("main thread is not in main loop"); thread-side collection previously crashed
Tk on macOS. Disabling automatic collection and running the same
generation-threshold policy from a Tk timer keeps every finalizer on the main
thread while still reclaiming cycles.

Lifetime: `install` is called when the Dashboard is created and `uninstall`
when it is destroyed, which collects once more on the Tk thread and restores
the previous automatic-collection setting for the rest of the process.
"""
import gc
import threading
import tkinter

INTERVAL_MS = 200
_state = {'installed': 0, 'was_enabled': None}


def collect_due():
    """Collect the generation CPython would collect now; return it, or None.

    Unlike CPython 3.12 this does not also require a quarter of the long-lived
    objects to be new before a full (generation 2) collection, so full
    collections can be somewhat more frequent: a small CPU cost, never a leak.
    """
    count, threshold = gc.get_count(), gc.get_threshold()
    if threshold[0] <= 0 or count[0] <= threshold[0]:
        return None
    generation = next(g for g in (2, 1, 0) if count[g] > threshold[g])
    gc.collect(generation)
    return generation


def install(root, interval_ms=INTERVAL_MS):
    """Disable automatic collection and collect from `root`'s event loop."""
    if _state['installed'] == 0:
        _state['was_enabled'] = gc.isenabled()
    _state['installed'] += 1
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


def uninstall():
    """Call on the Tk thread after the window is destroyed.

    Automatic collection is restored only when no other thread is alive: a
    cancelled AI worker may still be finishing, and it must not collect.
    """
    if _state['installed'] == 0:
        return
    _state['installed'] -= 1
    gc.collect()
    if _state['installed'] == 0 and _state['was_enabled'] and threading.active_count() == 1:
        gc.enable()
