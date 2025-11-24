# Dateipfad: src/smartdesk/handlers/_manager.py
# (NEUE DATEI)

import ctypes
import os
import shutil
from typing import Optional

from ..config import WALLPAPERS_DIR  # <- Korrigiert von S_DIR
from ..localization import get_text
from ..ui.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN

# Windows API Konstanten zum Setzen des s
SPI_SETDESK = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDWININICHANGE = 0x02

def set_(path: str) -> bool:
    """
    Setzt das Desktop-Hintergrundbild über die Windows-API.
    
    Args:
        path (str): Der (absolute) Pfad zum Bild.
    
    Returns:
        bool: True bei Erfolg, False bei Fehler.
    """
    if not path or not os.path.exists(path):
        print(f"{PREFIX_ERROR} {get_text('_manager.error.path_not_found', path=path)}")
        return False
        
    try:
        # Wandle den Pfad in einen C-String (Wide Char) um,
        # damit auch Pfade mit Umlauten etc. funktionieren.
        path_c = ctypes.c_wchar_p(path)
        
        # Rufe die Windows-API-Funktion auf
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESK,
            0,
            path_c,
            SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
        )
        
        if result:
            print(f"{PREFIX_OK} {get_text('_manager.success.set')}")
            return True
        else:
            print(f"{PREFIX_ERROR} {get_text('_manager.error.api_fail')}")
            return False
            
    except Exception as e:
        print(f"{PREFIX_ERROR} {get_text('_manager.error.api_exception', e=e)}")
        return False

def copy__to_datadir(source_path: str, desktop_name: str) -> Optional[str]:
    """
    Kopiert ein Bild in den AppData-Ordner von SmartDesk und gibt den neuen Pfad zurück.
    
    Args:
        source_path (str): Pfad zur Quelldatei.
        desktop_name (str): Name des Desktops (für den Dateinamen).
    
    Returns:
        Optional[str]: Der neue, permanente Pfad oder None bei Fehler.
    """
    if not os.path.exists(source_path):
        print(f"{PREFIX_ERROR} {get_text('_manager.error.source_not_found', path=source_path)}")
        return None
        
    try:
        # Erzeuge einen "sicheren" Dateinamen
        base_name = os.path.basename(source_path)
        # Entferne Leerzeichen und Umlaute aus dem Desktop-Namen für den Dateinamen
        safe_desktop_name = "".join(c for c in desktop_name if c.isalnum())
        
        # Nimm die Original-Dateiendung
        _, ext = os.path.splitext(base_name)
        
        # Neuer Dateiname: z.B. "Work_.jpg"
        new_filename = f"{safe_desktop_name}_{base_name}"
        destination_path = os.path.join(WALLPAPERS_DIR, new_filename)  # <- Korrigiert
        
        # Kopiere die Datei
        shutil.copy(source_path, destination_path)
        
        print(f"{PREFIX_OK} {get_text('_manager.success.copy', path=destination_path)}")
        return destination_path
        
    except Exception as e:
        print(f"{PREFIX_ERROR} {get_text('_manager.error.copy', e=e)}")
        return None
