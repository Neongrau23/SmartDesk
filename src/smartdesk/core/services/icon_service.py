# Dateipfad: src/smartdesk/core/services/icon_service.py

import win32gui
import win32process
import ctypes
import ctypes.wintypes
from typing import List
import time
import threading

from ...shared.style import PREFIX_ERROR, PREFIX_WARN
from ...shared.localization import get_text

try:
    from commctrl import LVM_FIRST, LVIF_TEXT
except ImportError:
    print(f"{PREFIX_ERROR} {get_text('icon_manager.error.fatal_commctrl')}")
    LVM_FIRST = 0x1000
    LVIF_TEXT = 0x0001

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


# --- Konstanten ---
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
set_last_error = ctypes.windll.kernel32.SetLastError
read_process_memory = ctypes.windll.kernel32.ReadProcessMemory
write_process_memory = ctypes.windll.kernel32.WriteProcessMemory


def _get_desktop_listview_handle():
    """Findet das Handle des Desktop-ListView-Fensters."""
    h_progman = win32gui.FindWindow("Progman", "Program Manager")

    h_shell_def_view = 0
    h_workerw = 0
    while h_shell_def_view == 0:
        h_workerw = win32gui.FindWindowEx(0, h_workerw, "WorkerW", None)
        if h_workerw == 0:
            break
        h_shell_def_view = win32gui.FindWindowEx(h_workerw, 0, "SHELLDLL_DefView", None)

    if h_shell_def_view == 0:
        h_shell_def_view = win32gui.FindWindowEx(h_progman, 0, "SHELLDLL_DefView", None)

    if h_shell_def_view == 0:
        print(f"{PREFIX_ERROR} {get_text('icon_manager.error.shelldll_not_found')}")
        return None

    h_listview = win32gui.FindWindowEx(
        h_shell_def_view, 0, "SysListView32", "FolderView"
    )
    if h_listview == 0:
        print(f"{PREFIX_ERROR} {get_text('icon_manager.error.listview_not_found')}")
        return None

    return h_listview


def get_current_icon_positions(timeout_seconds=5) -> List[IconPosition]:
    """
    Liest die Positionen aller Icons vom Windows-Desktop aus.
    """
    print(get_text("icon_manager.info.reading"))
    start_time = time.time()

    h_listview = _get_desktop_listview_handle()
    if not h_listview:
        return []

    if time.time() - start_time > timeout_seconds:
        print(f"{PREFIX_WARN} Timeout beim Finden des Desktop-Fensters")
        return []

    icons = []
    try:
        pid = win32process.GetWindowThreadProcessId(h_listview)[1]
    except Exception as e:
        print(f"{PREFIX_ERROR} Prozess-ID konnte nicht ermittelt werden: {e}")
        return []

    h_process = ctypes.windll.kernel32.OpenProcess(
        PROCESS_VM_READ | PROCESS_VM_OPERATION | PROCESS_VM_WRITE, False, pid
    )
    if not h_process:
        err_msg = get_text('icon_manager.error.open_process', code=get_last_error())
        print(f"{PREFIX_ERROR} {err_msg}")
        return []

    try:
        item_count = [None]
        error = [None]

        def get_item_count():
            try:
                item_count[0] = win32gui.SendMessage(h_listview, LVM_GETITEMCOUNT, 0, 0)
            except Exception as e:
                error[0] = e

        thread = threading.Thread(target=get_item_count)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout_seconds)

        if thread.is_alive():
            print(f"{PREFIX_WARN} Timeout: Desktop antwortet nicht")
            return []

        if error[0]:
            print(f"{PREFIX_ERROR} ListView nicht erreichbar: {error[0]}")
            return []

        if item_count[0] is None:
            print(f"{PREFIX_ERROR} Konnte Item-Count nicht abrufen")
            return []

        count = item_count[0]
        print(get_text("icon_manager.debug.item_count", count=count))

        if count == 0:
            print(get_text("icon_manager.info.icons_found", count=0))
            return []

        # Batch processing: Allocate memory for all items at once
        point_size = ctypes.sizeof(POINT)
        lvitem_size = ctypes.sizeof(LVITEM)
        text_buffer_size = 260 * 2 # MAX_PATH * sizeof(wchar_t)

        total_points_size = count * point_size
        total_lvitems_size = count * lvitem_size
        total_text_buffers_size = count * text_buffer_size

        # Allocate remote memory
        p_points_base = ctypes.windll.kernel32.VirtualAllocEx(
            h_process, 0, total_points_size, MEM_COMMIT, PAGE_READWRITE
        )
        p_lvitems_base = ctypes.windll.kernel32.VirtualAllocEx(
            h_process, 0, total_lvitems_size, MEM_COMMIT, PAGE_READWRITE
        )
        p_texts_base = ctypes.windll.kernel32.VirtualAllocEx(
            h_process, 0, total_text_buffers_size, MEM_COMMIT, PAGE_READWRITE
        )

        if not all([p_points_base, p_lvitems_base, p_texts_base]):
            err_msg = get_text('icon_manager.error.mem_alloc', code=get_last_error())
            print(f"{PREFIX_ERROR} {err_msg}")
            # Try to cleanup allocated memory if any
            for p in [p_points_base, p_lvitems_base, p_texts_base]:
                if p:
                    ctypes.windll.kernel32.VirtualFreeEx(h_process, p, 0, MEM_RELEASE)
            ctypes.windll.kernel32.CloseHandle(h_process)
            return []

        try:
            bytes_written = ctypes.c_size_t(0)
            bytes_read = ctypes.c_size_t(0)

            # Prepare all LVITEM structures locally
            # We create a big buffer to hold all LVITEMs
            LVItemArray = LVITEM * count
            lvitems_array = LVItemArray()

            for i in range(count):
                lvitem = lvitems_array[i]
                lvitem.mask = LVIF_TEXT
                lvitem.iItem = i
                lvitem.iSubItem = 0
                # Calculate remote address for this item's text buffer
                lvitem.pszText = p_texts_base + (i * text_buffer_size)
                lvitem.cchTextMax = 260

            # Write all LVITEMs to remote memory in one go
            if not write_process_memory(
                h_process,
                p_lvitems_base,
                ctypes.byref(lvitems_array),
                total_lvitems_size,
                ctypes.byref(bytes_written),
            ):
                 print(f"{PREFIX_ERROR} Failed to write LVITEMs batch")
                 return []

            # Loop SendMessage calls (unavoidable)
            for i in range(count):
                # Request position -> write to p_points_base + offset
                win32gui.SendMessage(h_listview, LVM_GETITEMPOSITION, i, p_points_base + i * point_size)

                # Request text -> write to p_texts_base + offset (via LVITEM)
                win32gui.SendMessage(h_listview, LVM_GETITEMW, i, p_lvitems_base + i * lvitem_size)

            # Read all points in one go
            points_buffer = (POINT * count)()
            if not read_process_memory(
                h_process,
                p_points_base,
                ctypes.byref(points_buffer),
                total_points_size,
                ctypes.byref(bytes_read),
            ):
                print(f"{PREFIX_ERROR} Failed to read points batch")
                return []

            # Read all texts in one go
            # Create a character buffer
            # text_buffer_size is in bytes (520). Total size is count * 520 bytes.
            # We use c_char array for raw bytes reading
            raw_text_data = (ctypes.c_char * total_text_buffers_size)()
            if not read_process_memory(
                h_process,
                p_texts_base,
                ctypes.byref(raw_text_data),
                total_text_buffers_size,
                ctypes.byref(bytes_read),
            ):
                print(f"{PREFIX_ERROR} Failed to read texts batch")
                return []

            # Process retrieved data
            for i in range(count):
                point = points_buffer[i]

                # Extract text for this item
                offset = i * text_buffer_size
                # We need to interpret these 520 bytes as a wide string (UTF-16LE)
                # Slicing the raw char array
                raw_bytes = raw_text_data[offset : offset + text_buffer_size]

                # Convert bytes to string (handling double-null termination or length)
                # ctypes.create_unicode_buffer equivalent from bytes
                try:
                    # In a real Windows environment, this is UTF-16LE.
                    # We can use bytes.decode('utf-16-le') and strip nulls.
                    # bytes(raw_bytes) converts the ctypes array slice to python bytes
                    name_full = bytes(raw_bytes).decode('utf-16-le')
                    name = name_full.split('\x00')[0]

                    if name:
                        icons.append(IconPosition(index=i, name=name, x=point.x, y=point.y))
                except Exception as e:
                    print(f"{PREFIX_WARN} Icon {i} parsing error: {e}")
                    continue

        finally:
            ctypes.windll.kernel32.VirtualFreeEx(h_process, p_points_base, 0, MEM_RELEASE)
            ctypes.windll.kernel32.VirtualFreeEx(h_process, p_lvitems_base, 0, MEM_RELEASE)
            ctypes.windll.kernel32.VirtualFreeEx(h_process, p_texts_base, 0, MEM_RELEASE)
            ctypes.windll.kernel32.CloseHandle(h_process)

    except Exception as e:
        print(f"{PREFIX_ERROR} Unexpected error in icon retrieval: {e}")
        # Ensure handle is closed if it wasn't already (though finally block above handles it if allocations succeeded)
        # If allocations failed, handle is closed.
        pass

    print(get_text("icon_manager.info.icons_found", count=len(icons)))
    return icons


def set_icon_positions(icons: List[IconPosition]):
    """
    Setzt die Positionen der Icons auf dem Windows-Desktop.
    """
    print(get_text("icon_manager.info.setting", count=len(icons)))
    if not icons:
        print(get_text("icon_manager.info.no_icons_to_set"))
        return

    h_listview = _get_desktop_listview_handle()
    if not h_listview:
        return

    current_item_count = win32gui.SendMessage(h_listview, LVM_GETITEMCOUNT, 0, 0)
    if current_item_count == 0:
        msg = get_text('icon_manager.warn.no_icons_on_desktop')
        print(f"{PREFIX_WARN} {msg}")
        return

    restored = 0
    failed = 0

    for icon in icons:
        if icon.index < current_item_count:
            y_shifted = (icon.y & 0xFFFF) << 16
            x_masked = icon.x & 0xFFFF
            lParam = y_shifted | x_masked

            result = win32gui.SendMessage(
                h_listview, LVM_SETITEMPOSITION, icon.index, lParam
            )

            if result != 0:
                restored += 1
            else:
                failed += 1

            win32gui.SendMessage(h_listview, LVM_UPDATE, icon.index, 0)
        else:
            msg = get_text(
                'icon_manager.warn.index_not_found',
                index=icon.index,
                name=icon.name,
                max=(current_item_count - 1),
            )
            print(f"{PREFIX_WARN} {msg}")
            failed += 1

    win32gui.InvalidateRect(h_listview, None, True)
    win32gui.UpdateWindow(h_listview)

    print(
        get_text("icon_manager.info.restore_complete", restored=restored, failed=failed)
    )
