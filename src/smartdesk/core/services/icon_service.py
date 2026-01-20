# Dateipfad: src/smartdesk/core/services/icon_service.py

import ctypes
from ctypes import wintypes
import time
import win32gui
import win32process
from threading import Thread
from typing import List

from ...shared.localization import get_text
from ...shared.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN
from ..models.desktop import IconPosition

# --- CTypes Strukturen und Konstanten ---
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class LVITEM(ctypes.Structure):
    _fields_ = [
        ("mask", ctypes.c_uint), ("iItem", ctypes.c_int), ("iSubItem", ctypes.c_int),
        ("state", ctypes.c_uint), ("stateMask", ctypes.c_uint), ("pszText", ctypes.c_wchar_p),
        ("cchTextMax", ctypes.c_int), ("iImage", ctypes.c_int), ("lParam", ctypes.c_void_p),
        ("iIndent", ctypes.c_int), ("iGroupId", ctypes.c_int), ("cColumns", ctypes.c_uint),
        ("puColumns", ctypes.c_void_p),
    ]

# --- WinAPI Konstanten ---
LVM_FIRST = 0x1000
LVIF_TEXT = 0x0001
LVM_GETITEMCOUNT = LVM_FIRST + 4
LVM_GETITEMW = LVM_FIRST + 75
LVM_GETITEMPOSITION = LVM_FIRST + 16
LVM_SETITEMPOSITION = LVM_FIRST + 15
LVM_UPDATE = LVM_FIRST + 42

PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
MEM_COMMIT = 0x1000
MEM_RELEASE = 0x8000
PAGE_READWRITE = 0x04

get_last_error = ctypes.windll.kernel32.GetLastError
read_process_memory = ctypes.windll.kernel32.ReadProcessMemory
write_process_memory = ctypes.windll.kernel32.WriteProcessMemory

# Thread-Klasse für Timeout
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def _get_desktop_listview_handle():
    """Findet das Handle des Desktop-ListView-Fensters."""
    h_progman = win32gui.FindWindow("Progman", "Program Manager")
    h_shell_def_view = win32gui.FindWindowEx(h_progman, 0, "SHELLDLL_DefView", None)
    if h_shell_def_view == 0:
        h_workerw = 0
        while True:
            h_workerw = win32gui.FindWindowEx(0, h_workerw, "WorkerW", None)
            if not h_workerw: break
            h_shell_def_view = win32gui.FindWindowEx(h_workerw, 0, "SHELLDLL_DefView", None)
            if h_shell_def_view: break
    if h_shell_def_view == 0: return None
    return win32gui.FindWindowEx(h_shell_def_view, 0, "SysListView32", "FolderView")

def get_current_icon_positions(timeout_seconds=5) -> List[IconPosition]:
    """
    Liest die aktuellen Positionen aller Desktop-Icons.
    Optimiert für Performance durch Batch-Speicheroperationen.
    """
    icons: List[IconPosition] = []
    h_listview = _get_desktop_listview_handle()
    if not h_listview:
        print(f"{PREFIX_ERROR} {get_text('icon_manager.error.listview_not_found')}")
        return []

    try:
        pid = win32process.GetWindowThreadProcessId(h_listview)[1]
    except Exception as e:
        print(f"{PREFIX_ERROR} Prozess-ID konnte nicht ermittelt werden: {e}")
        return []

    h_process = ctypes.windll.kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_VM_OPERATION | PROCESS_VM_WRITE, False, pid)
    if not h_process:
        err_msg = get_text('icon_manager.error.open_process', code=get_last_error())
        print(f"{PREFIX_ERROR} {err_msg}")
        return []

    try:
        item_count = [None]
        error = [None]

        def get_count_with_timeout():
            try: item_count[0] = win32gui.SendMessage(h_listview, LVM_GETITEMCOUNT, 0, 0)
            except Exception as e: error[0] = e
        
        thread = ThreadWithReturnValue(target=get_count_with_timeout)
        thread.start()
        thread.join(timeout=timeout_seconds)

        if thread.is_alive():
            print(f"{PREFIX_ERROR} {get_text('icon_manager.error.timeout')}")
            return []
        
        if error[0]: raise error[0]
        if item_count[0] is None:
            print(f"{PREFIX_ERROR} Konnte Item-Count nicht abrufen")
            return []

        count = item_count[0]
        if count == 0: return []

        point_size = ctypes.sizeof(POINT)
        lvitem_size = ctypes.sizeof(LVITEM)
        text_buffer_size = 260 * 2

        p_points_base = ctypes.windll.kernel32.VirtualAllocEx(h_process, 0, count * point_size, MEM_COMMIT, PAGE_READWRITE)
        p_lvitems_base = ctypes.windll.kernel32.VirtualAllocEx(h_process, 0, count * lvitem_size, MEM_COMMIT, PAGE_READWRITE)
        p_texts_base = ctypes.windll.kernel32.VirtualAllocEx(h_process, 0, count * text_buffer_size, MEM_COMMIT, PAGE_READWRITE)

        if not all([p_points_base, p_lvitems_base, p_texts_base]):
            err_msg = get_text('icon_manager.error.mem_alloc', code=get_last_error())
            print(f"{PREFIX_ERROR} {err_msg}")
            return []

        try:
            bytes_written = ctypes.c_size_t(0)
            bytes_read = ctypes.c_size_t(0)
            LVItemArray = LVITEM * count
            lvitems_array = LVItemArray()

            for i in range(count):
                lvitem = lvitems_array[i]
                lvitem.mask = LVIF_TEXT
                lvitem.iItem = i
                lvitem.pszText = p_texts_base + (i * text_buffer_size)
                lvitem.cchTextMax = 260

            if not write_process_memory(h_process, p_lvitems_base, ctypes.byref(lvitems_array), count * lvitem_size, ctypes.byref(bytes_written)):
                 return []

            for i in range(count):
                win32gui.SendMessage(h_listview, LVM_GETITEMPOSITION, i, p_points_base + i * point_size)
                win32gui.SendMessage(h_listview, LVM_GETITEMW, i, p_lvitems_base + i * lvitem_size)

            points_buffer = (POINT * count)()
            if not read_process_memory(h_process, p_points_base, ctypes.byref(points_buffer), count * point_size, ctypes.byref(bytes_read)):
                return []

            raw_text_data = (ctypes.c_char * (count * text_buffer_size))()
            if not read_process_memory(h_process, p_texts_base, ctypes.byref(raw_text_data), count * text_buffer_size, ctypes.byref(bytes_read)):
                return []

            for i in range(count):
                point = points_buffer[i]
                offset = i * text_buffer_size
                raw_bytes = raw_text_data[offset : offset + text_buffer_size]
                try:
                    name = bytes(raw_bytes).decode('utf-16-le').split('\x00')[0]
                    if name:
                        icons.append(IconPosition(index=i, name=name, x=point.x, y=point.y))
                except Exception as e:
                    print(f"{PREFIX_WARN} Icon {i} parsing error: {e}")
        finally:
            if p_points_base: ctypes.windll.kernel32.VirtualFreeEx(h_process, p_points_base, 0, MEM_RELEASE)
            if p_lvitems_base: ctypes.windll.kernel32.VirtualFreeEx(h_process, p_lvitems_base, 0, MEM_RELEASE)
            if p_texts_base: ctypes.windll.kernel32.VirtualFreeEx(h_process, p_texts_base, 0, MEM_RELEASE)
    except Exception as e:
        print(f"{PREFIX_ERROR} Unexpected error in icon retrieval: {e}")
    finally:
        if h_process: ctypes.windll.kernel32.CloseHandle(h_process)

    return icons

def set_icon_positions(icons: List[IconPosition]):
    """
    Setzt die Positionen der Icons auf dem Windows-Desktop.
    """
    if not icons: return

    h_listview = _get_desktop_listview_handle()
    if not h_listview: return

    current_item_count = win32gui.SendMessage(h_listview, LVM_GETITEMCOUNT, 0, 0)
    if current_item_count == 0: return

    restored, failed = 0, 0
    for icon in icons:
        if icon.index < current_item_count:
            lParam = (icon.y << 16) | (icon.x & 0xFFFF)
            if win32gui.SendMessage(h_listview, LVM_SETITEMPOSITION, icon.index, lParam):
                restored += 1
            else:
                failed += 1
            win32gui.SendMessage(h_listview, LVM_UPDATE, icon.index, 0)
        else:
            failed += 1
            print(f"{PREFIX_WARN} {get_text('icon_manager.warn.index_not_found', name=icon.name, index=icon.index, max=current_item_count-1)}")

    win32gui.InvalidateRect(h_listview, None, True)
    win32gui.UpdateWindow(h_listview)
    print(f"{PREFIX_OK} {get_text('icon_manager.info.restore_complete', restored=restored, failed=failed)}")
