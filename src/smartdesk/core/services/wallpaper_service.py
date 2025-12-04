# Dateipfad: src/smartdesk/core/services/wallpaper_service.py

import ctypes
import os
import shutil
from typing import Optional

from ...shared.config import WALLPAPERS_DIR
from ...shared.localization import get_text
from ...shared.style import PREFIX_ERROR, PREFIX_OK

# Windows API Konstanten
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDWININICHANGE = 0x02


def set_wallpaper(path: str) -> bool:
    """
    Setzt das Desktop-Hintergrundbild über die Windows-API.
    """
    if not path or not os.path.exists(path):
        print(
            f"{PREFIX_ERROR} {get_text('wallpaper_manager.error.path_not_found', path=path)}"
        )
        return False

    try:
        path_c = ctypes.c_wchar_p(path)
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 0, path_c, SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
        )

        if result:
            print(f"{PREFIX_OK} {get_text('wallpaper_manager.success.set')}")
            return True
        else:
            print(f"{PREFIX_ERROR} {get_text('wallpaper_manager.error.api_fail')}")
            return False

    except Exception as e:
        print(
            f"{PREFIX_ERROR} {get_text('wallpaper_manager.error.api_exception', e=e)}"
        )
        return False


def copy_wallpaper_to_datadir(source_path: str, desktop_name: str) -> Optional[str]:
    """
    Kopiert ein Bild in den AppData-Ordner von SmartDesk.
    """
    if not os.path.exists(source_path):
        print(
            f"{PREFIX_ERROR} {get_text('wallpaper_manager.error.source_not_found', path=source_path)}"
        )
        return None

    try:
        base_name = os.path.basename(source_path)
        safe_desktop_name = "".join(c for c in desktop_name if c.isalnum())
        _, ext = os.path.splitext(base_name)
        new_filename = f"{safe_desktop_name}_{base_name}"
        destination_path = os.path.join(WALLPAPERS_DIR, new_filename)

        shutil.copy(source_path, destination_path)
        print(
            f"{PREFIX_OK} {get_text('wallpaper_manager.success.copy', path=destination_path)}"
        )
        return destination_path

    except Exception as e:
        print(f"{PREFIX_ERROR} {get_text('wallpaper_manager.error.copy', e=e)}")
        return None


# Alias für Kompatibilität
assign_wallpaper = set_wallpaper
