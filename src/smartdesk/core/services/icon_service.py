# Dateipfad: src/smartdesk/core/services/icon_service.py

import ctypes
from ctypes import wintypes
import time

from ...shared.localization import get_text
from ...shared.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN
from ..models.desktop import IconPosition
from typing import List

# CTypes Strukturen und Konstanten
# ... (rest of the file remains the same until get_current_icon_positions)

def get_current_icon_positions(timeout_seconds=5) -> List[IconPosition]:
    """
    Liest die aktuellen Positionen aller Desktop-Icons.
    Nutzt Windows API, um direkt mit dem ListView-Control zu interagieren.
    Optimiert für Performance durch Batch-Speicheroperationen.
    """
    icons: List[IconPosition] = []
    
    # ... (rest of the file remains the same until the main try block)
    
    try:
        item_count = [None]
        error = [None]

        # Timeout-Wrapper für SendMessage
        def get_count_with_timeout():
            try:
                item_count[0] = win32gui.SendMessage(h_listview, LVM_GETITEMCOUNT, 0, 0)
            except Exception as e:
                error[0] = e
        
        thread = ThreadWithReturnValue(target=get_count_with_timeout)
        thread.start()
        thread.join(timeout=timeout_seconds)

        if thread.is_alive():
            err_msg = get_text('icon_manager.error.timeout')
            print(f"{PREFIX_ERROR} {err_msg}")
            return []
        
        if error[0]:
            raise error[0]

        if item_count[0] is None:
            print(f"{PREFIX_ERROR} Konnte Item-Count nicht abrufen")
            return []

        count = item_count[0]
        print(get_text("icon_manager.debug.item_count", count=count))

        if count == 0:
            print(get_text("icon_manager.info.icons_found", count=0))
            return []

        # Batch processing
        point_size = ctypes.sizeof(POINT)
        lvitem_size = ctypes.sizeof(LVITEM)
        text_buffer_size = 260 * 2 # MAX_PATH * sizeof(wchar_t)

        total_points_size = count * point_size
        total_lvitems_size = count * lvitem_size
        total_text_buffers_size = count * text_buffer_size

        p_points_base = ctypes.windll.kernel32.VirtualAllocEx(h_process, 0, total_points_size, MEM_COMMIT, PAGE_READWRITE)
        p_lvitems_base = ctypes.windll.kernel32.VirtualAllocEx(h_process, 0, total_lvitems_size, MEM_COMMIT, PAGE_READWRITE)
        p_texts_base = ctypes.windll.kernel32.VirtualAllocEx(h_process, 0, total_text_buffers_size, MEM_COMMIT, PAGE_READWRITE)

        if not all([p_points_base, p_lvitems_base, p_texts_base]):
            err_msg = get_text('icon_manager.error.mem_alloc', code=get_last_error())
            print(f"{PREFIX_ERROR} {err_msg}")
            for p in [p_points_base, p_lvitems_base, p_texts_base]:
                if p:
                    ctypes.windll.kernel32.VirtualFreeEx(h_process, p, 0, MEM_RELEASE)
            ctypes.windll.kernel32.CloseHandle(h_process)
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
                lvitem.iSubItem = 0
                lvitem.pszText = p_texts_base + (i * text_buffer_size)
                lvitem.cchTextMax = 260

            if not write_process_memory(h_process, p_lvitems_base, ctypes.byref(lvitems_array), total_lvitems_size, ctypes.byref(bytes_written)):
                 print(f"{PREFIX_ERROR} Failed to write LVITEMs batch")
                 return []

            for i in range(count):
                win32gui.SendMessage(h_listview, LVM_GETITEMPOSITION, i, p_points_base + i * point_size)
                win32gui.SendMessage(h_listview, LVM_GETITEMW, i, p_lvitems_base + i * lvitem_size)

            points_buffer = (POINT * count)()
            if not read_process_memory(h_process, p_points_base, ctypes.byref(points_buffer), total_points_size, ctypes.byref(bytes_read)):
                print(f"{PREFIX_ERROR} Failed to read points batch")
                return []

            raw_text_data = (ctypes.c_char * total_text_buffers_size)()
            if not read_process_memory(h_process, p_texts_base, ctypes.byref(raw_text_data), total_text_buffers_size, ctypes.byref(bytes_read)):
                print(f"{PREFIX_ERROR} Failed to read texts batch")
                return []

            for i in range(count):
                point = points_buffer[i]
                offset = i * text_buffer_size
                raw_bytes = raw_text_data[offset : offset + text_buffer_size]
                try:
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
        pass

    print(get_text("icon_manager.info.icons_found", count=len(icons)))
    return icons

# ... (rest of the file remains the same)