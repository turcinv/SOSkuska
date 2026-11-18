"""Cooperative cross-process shared Store / exclusive restore leases."""
import os
from pathlib import Path


class DatabaseLease:
    def __init__(self, path, *, exclusive=False):
        self.file = None
        path = Path(path).resolve()
        if path.exists() and path.stat().st_nlink > 1:
            raise ValueError('Hard-linked database files are unsupported. Use an ordinary database file.')
        handle = open(str(path) + '.lock', 'a+b')
        try:
            if os.name == 'nt':
                import ctypes
                import msvcrt
                from ctypes import wintypes
                class Overlapped(ctypes.Structure):
                    _fields_ = [('Internal', ctypes.c_size_t), ('InternalHigh', ctypes.c_size_t),
                                ('Offset', wintypes.DWORD), ('OffsetHigh', wintypes.DWORD),
                                ('hEvent', wintypes.HANDLE)]
                self.overlapped = Overlapped()
                self.native = msvcrt.get_osfhandle(handle.fileno())
                self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
                self.kernel.LockFileEx.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD,
                                                  wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(Overlapped)]
                self.kernel.LockFileEx.restype = wintypes.BOOL
                self.kernel.UnlockFileEx.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD,
                                                    wintypes.DWORD, ctypes.POINTER(Overlapped)]
                self.kernel.UnlockFileEx.restype = wintypes.BOOL
                if not self.kernel.LockFileEx(self.native, 1 | (2 if exclusive else 0), 0, 1, 0, ctypes.byref(self.overlapped)):
                    raise OSError(ctypes.get_last_error(), 'Database lease unavailable')
            else:
                import fcntl
                fcntl.flock(handle.fileno(), (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
        except OSError:
            handle.close()
            raise ValueError('Close other SOSkúška windows using this database, then retry.') from None
        if path.exists() and path.stat().st_nlink > 1:
            handle.close()
            raise ValueError('Hard-linked database files are unsupported.')
        self.file = handle

    def close(self):
        if self.file is not None:
            if os.name == 'nt':
                import ctypes
                self.kernel.UnlockFileEx(self.native, 0, 1, 0, ctypes.byref(self.overlapped))
            self.file.close()
            self.file = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
