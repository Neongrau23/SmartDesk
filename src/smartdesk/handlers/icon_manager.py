# (Version mit detaillierten DEBUG-Ausgaben)

import win32gui
import win32con
import win32process
import ctypes
import ctypes.wintypes
from typing import List

try:
    from commctrl import (
        LVM_FIRST, 
        LVIF_TEXT, 
        LVFI_STRING
    )
except ImportError:
    print("FATAL ERROR: 'commctrl' nicht gefunden. pywin32 ist nicht korrekt installiert.")
    LVM_FIRST = 0x1000 
    LVIF_TEXT = 0x0001
    LVFI_STRING = 0x0002

from ..models.desktop import IconPosition

# --- C-Strukturen (unverändert) ---
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

class LVITEM(ctypes.Structure):
    _fields_ = [("mask", ctypes.c_uint),
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
                ("puColumns", ctypes.c_void_p)]

# --- Konstanten (unverändert) ---
LVM_GETITEMCOUNT = (LVM_FIRST + 4)
LVM_GETITEMW = (LVM_FIRST + 75)
LVM_GETITEMPOSITION = (LVM_FIRST + 16)
LVM_SETITEMPOSITION = (LVM_FIRST + 15)
LVM_FINDITEMW = (LVM_FIRST + 83)

PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
MEM_COMMIT = 0x1000
MEM_RELEASE = 0x8000
PAGE_READWRITE = 0x04


def _get_desktop_listview_handle():
    """Findet das "Handle" des Desktop-ListView-Fensters."""
    
    # --- DEBUG-AUSGABEN HINZUGEFÜGT ---
    print("[IconManager DEBUG] Suche 'Progman'...")
    h_progman = win32gui.FindWindow("Progman", "Program Manager")
    if not h_progman:
        print("[IconManager ERROR] Progman-Fenster nicht gefunden.")
        return None
    print(f"[IconManager DEBUG] 'Progman' gefunden: {h_progman}")

    print("[IconManager DEBUG] Suche 'SHELLDLL_DefView'...")
    h_shell_def_view = win32gui.FindWindowEx(h_progman, 0, "SHELLDLL_DefView", None)
    if not h_shell_def_view:
        print("[IconManager ERROR] SHELLDLL_DefView-Fenster nicht gefunden.")
        return None
    print(f"[IconManager DEBUG] 'SHELLDLL_DefView' gefunden: {h_shell_def_view}")

    print("[IconManager DEBUG] Suche 'SysListView32'...")
    h_listview = win32gui.FindWindowEx(h_shell_def_view, 0, "SysListView32", "FolderView")
    if not h_listview:
        print("[IconManager ERROR] SysListView32 (FolderView) nicht gefunden.")
        return None
    print(f"[IconManager DEBUG] 'SysListView32' (Desktop) gefunden: {h_listview}")
        
    return h_listview


def get_current_icon_positions() -> List[IconPosition]:
    """Liest die ECHTEN Positionen aller Icons vom Windows-Desktop aus."""
    print("[IconManager] Lese ECHTE Icon-Positionen vom Desktop...")
    h_listview = _get_desktop_listview_handle()
    if not h_listview:
        print("[IconManager ERROR] Abbruch: Desktop-Handle nicht gefunden.")
        return []

    icons = []
    
    pid = win32process.GetWindowThreadProcessId(h_listview)[1]
    print(f"[IconManager DEBUG] Prozess-ID (PID) des Desktops: {pid}")
    
    h_process = ctypes.windll.kernel32.OpenProcess(
        PROCESS_VM_READ | PROCESS_VM_OPERATION, False, pid)
    if not h_process:
        print("[IconManager ERROR] Konnte Prozess nicht öffnen (OpenProcess fehlgeschlagen).")
        return []
    print(f"[IconManager DEBUG] Prozess-Handle geöffnet: {h_process}")

    p_point = ctypes.windll.kernel32.VirtualAllocEx(
        h_process, 0, ctypes.sizeof(POINT), MEM_COMMIT, PAGE_READWRITE)
    p_lvitem = ctypes.windll.kernel32.VirtualAllocEx(
        h_process, 0, ctypes.sizeof(LVITEM), MEM_COMMIT, PAGE_READWRITE)
    p_text_buffer = ctypes.windll.kernel32.VirtualAllocEx(
        h_process, 0, 260 * 2, MEM_COMMIT, PAGE_READWRITE)
        
    if not all([p_point, p_lvitem, p_text_buffer]):
        print("[IconManager ERROR] Speicherreservierung im Zielprozess fehlgeschlagen (VirtualAllocEx).")
        if h_process:
            ctypes.windll.kernel32.CloseHandle(h_process)
        return []
    print("[IconManager DEBUG] Speicher im Zielprozess erfolgreich reserviert.")

    try:
        item_count = win32gui.SendMessage(h_listview, LVM_GETITEMCOUNT, 0, 0)
        print(f"[IconManager DEBUG] Anzahl gefundener Items (Icons): {item_count}")
        
        if item_count == 0:
            print("[IconManager WARN] 0 Icons gefunden. Desktop ist leer oder Zugriff blockiert.")

        for i in range(item_count):
            
            # --- Position (X, Y) holen ---
            win32gui.SendMessage(
                h_listview, LVM_GETITEMPOSITION, i, p_point)
            
            point = POINT()
            ctypes.windll.kernel32.ReadProcessMemory(
                h_process, p_point, ctypes.byref(point), ctypes.sizeof(point), 0)

            # --- Name (Text) holen ---
            lvitem = LVITEM()
            lvitem.mask = LVIF_TEXT 
            lvitem.iItem = i
            lvitem.iSubItem = 0
            lvitem.pszText = p_text_buffer
            lvitem.cchTextMax = 260
            
            ctypes.windll.kernel32.WriteProcessMemory(
                h_process, p_lvitem, ctypes.byref(lvitem), ctypes.sizeof(lvitem), 0)
            
            win32gui.SendMessage(h_listview, LVM_GETITEMW, i, p_lvitem)
            
            text_buffer = ctypes.create_unicode_buffer(260)
            ctypes.windll.kernel32.ReadProcessMemory(
                h_process, p_text_buffer, text_buffer, 260 * 2, 0)
            
            name = text_buffer.value
            
            if name:
                print(f"[IconManager DEBUG] Item {i}: Name='{name}', X={point.x}, Y={point.y}")
                icons.append(IconPosition(name=name, x=point.x, y=point.y))
            else:
                print(f"[IconManager DEBUG] Item {i}: Name konnte nicht gelesen werden.")

    finally:
        print("[IconManager DEBUG] Räume Speicher auf und schließe Prozess-Handle.")
        ctypes.windll.kernel32.VirtualFreeEx(h_process, p_point, 0, MEM_RELEASE)
        ctypes.windll.kernel32.VirtualFreeEx(h_process, p_lvitem, 0, MEM_RELEASE)
        ctypes.windll.kernel32.VirtualFreeEx(h_process, p_text_buffer, 0, MEM_RELEASE)
        ctypes.windll.kernel32.CloseHandle(h_process)

    print(f"-> {len(icons)} ECHTE Icons gefunden und zur Liste hinzugefügt.")
    return icons


def set_icon_positions(icons: List[IconPosition]):
    """Setzt die ECHTEN Positionen der Icons auf dem Windows-Desktop."""
    print(f"[IconManager] Setze {len(icons)} ECHTE Icon-Positionen...")
    if not icons:
        print("-> Keine Icons zum Setzen vorhanden.")
        return

    h_listview = _get_desktop_listview_handle()
    if not h_listview:
        return
        
    pid = win32process.GetWindowThreadProcessId(h_listview)[1]
    h_process = ctypes.windll.kernel32.OpenProcess(
        PROCESS_VM_WRITE | PROCESS_VM_OPERATION, False, pid)
    if not h_process:
        print("[IconManager ERROR] Konnte Prozess für Schreibzugriff nicht öffnen.")
        return

    p_point = ctypes.windll.kernel32.VirtualAllocEx(
        h_process, 0, ctypes.sizeof(POINT), MEM_COMMIT, PAGE_READWRITE)
    if not p_point:
        print("[IconManager ERROR] Speicher (p_point) konnte nicht reserviert werden.")
        ctypes.windll.kernel32.CloseHandle(h_process)
        return

    try:
        for icon in icons:
            index = win32gui.SendMessage(
                h_listview, 
                LVM_FINDITEMW, 
                -1, 
                win32gui.LVFINDINFO(LVFI_STRING, icon.name)
            )

            if index != -1:
                point = POINT(x=icon.x, y=icon.y)
                
                ctypes.windll.kernel32.WriteProcessMemory(
                    h_process, p_point, ctypes.byref(point), ctypes.sizeof(point), 0)
                
                win32gui.SendMessage(
                    h_listview, LVM_SETITEMPOSITION, index, p_point)
            else:
                print(f"[IconManager WARN] Icon '{icon.name}' nicht auf Desktop gefunden. Überspringe.")

    finally:
        ctypes.windll.kernel32.VirtualFreeEx(h_process, p_point, 0, MEM_RELEASE)
        ctypes.windll.kernel32.CloseHandle(h_process)
        
    print("-> Icon-Positionen wiederhergestellt.")