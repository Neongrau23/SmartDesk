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


# --- C-Strukturen ---
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class LVITEM(ctypes.Structure):
    _fields_ = [
        ("mask", ctypes.c_uint),
        ("iItem", ctypes.c_int),
        ("iSubItem", ctypes.c_int),
        ("state", ctypes.c_uint),
        ("stateMask", ctypes.c_uint),
        ("pszText", ctypes.c_wchar_p),
        ("cchTextMax", ctypes.c_int),
        ("iImage", ctypes.c_int),
        ("lParam", ctypes.c_void_p),
        ("iIndent", ctypes.c_int),
        ("iGroupId", ctypes.c_int),
        ("cColumns", ctypes.c_uint),
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


def _get_desktop_listview_handle():
    """Findet das Handle des Desktop-ListView-Fensters."""
    h_progman = win32gui.FindWindow("Progman", "Program Manager")
    h_shell_def_view = win32gui.FindWindowEx(h_progman, 0, "SHELLDLL_DefView", None)
    if h_shell_def_view == 0:
        h_workerw = 0
        while True:
            h_workerw = win32gui.FindWindowEx(0, h_workerw, "WorkerW", None)
            if not h_workerw:
                break
            h_shell_def_view = win32gui.FindWindowEx(h_workerw, 0, "SHELLDLL_DefView", None)
            if h_shell_def_view:
                break
    if h_shell_def_view == 0:
        return None
    return win32gui.FindWindowEx(h_shell_def_view, 0, "SysListView32", "FolderView")


def get_current_icon_positions(timeout_seconds=5) -> List[IconPosition]:
    """
    Liest die Positionen aller Icons vom Windows-Desktop aus.
    Stabile Version mit Einzelabfragen.
    """
    icons = []
    h_listview = _get_desktop_listview_handle()
    if not h_listview:
        return []

    try:
        pid = win32process.GetWindowThreadProcessId(h_listview)[1]
        h_process = ctypes.windll.kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_VM_OPERATION | PROCESS_VM_WRITE, False, pid)
        if not h_process:
            return []

        item_count = win32gui.SendMessage(h_listview, LVM_GETITEMCOUNT, 0, 0)
        if item_count <= 0:
            return []

        # Speicher im Zielprozess reservieren
        p_point = ctypes.windll.kernel32.VirtualAllocEx(h_process, 0, ctypes.sizeof(POINT), MEM_COMMIT, PAGE_READWRITE)
        p_lvitem = ctypes.windll.kernel32.VirtualAllocEx(h_process, 0, ctypes.sizeof(LVITEM), MEM_COMMIT, PAGE_READWRITE)
        p_text_buffer = ctypes.windll.kernel32.VirtualAllocEx(h_process, 0, 520, MEM_COMMIT, PAGE_READWRITE)

        if not all([p_point, p_lvitem, p_text_buffer]):
            ctypes.windll.kernel32.CloseHandle(h_process)
            return []

        try:
            for i in range(item_count):
                # Position holen
                win32gui.SendMessage(h_listview, LVM_GETITEMPOSITION, i, p_point)
                pt = POINT()
                read_process_memory(h_process, p_point, ctypes.byref(pt), ctypes.sizeof(pt), None)

                # Name holen
                lv_item = LVITEM()
                lv_item.mask = LVIF_TEXT
                lv_item.iItem = i
                lv_item.pszText = p_text_buffer
                lv_item.cchTextMax = 260

                write_process_memory(h_process, p_lvitem, ctypes.byref(lv_item), ctypes.sizeof(lv_item), None)
                win32gui.SendMessage(h_listview, LVM_GETITEMW, i, p_lvitem)

                name_buffer = ctypes.create_unicode_buffer(260)
                read_process_memory(h_process, p_text_buffer, name_buffer, 520, None)

                name = name_buffer.value
                if name:
                    icons.append(IconPosition(index=i, name=name, x=pt.x, y=pt.y))
        finally:
            ctypes.windll.kernel32.VirtualFreeEx(h_process, p_point, 0, MEM_RELEASE)
            ctypes.windll.kernel32.VirtualFreeEx(h_process, p_lvitem, 0, MEM_RELEASE)
            ctypes.windll.kernel32.VirtualFreeEx(h_process, p_text_buffer, 0, MEM_RELEASE)
            ctypes.windll.kernel32.CloseHandle(h_process)
    except Exception as e:
        print(f"Fehler beim Lesen der Icons: {e}")

    return icons


def set_icon_positions(saved_icons: List[IconPosition]):
    """
    Setzt die Positionen der Icons.
    Nutzt Namens-Matching für maximale Zuverlässigkeit.
    """
    if not saved_icons:
        return

    h_listview = _get_desktop_listview_handle()
    if not h_listview:
        return

    # 1. Aktuellen Stand holen, um Namen -> Index Map zu bauen
    current_icons = get_current_icon_positions()
    name_to_index = {icon.name: icon.index for icon in current_icons}

    current_item_count = win32gui.SendMessage(h_listview, LVM_GETITEMCOUNT, 0, 0)

    restored, failed = 0, 0
    for saved in saved_icons:
        # Index über Name finden (statt den gespeicherten Index blind zu nutzen)
        index = name_to_index.get(saved.name)

        if index is not None and index < current_item_count:
            lParam = ((saved.y & 0xFFFF) << 16) | (saved.x & 0xFFFF)
            if win32gui.SendMessage(h_listview, LVM_SETITEMPOSITION, index, lParam):
                restored += 1
                win32gui.SendMessage(h_listview, LVM_UPDATE, index, 0)
            else:
                failed += 1
        else:
            failed += 1

    # Desktop aktualisieren
    win32gui.InvalidateRect(h_listview, None, True)
    win32gui.UpdateWindow(h_listview)
    print(f"{PREFIX_OK} {get_text('icon_manager.info.restore_complete', restored=restored, failed=failed)}")
