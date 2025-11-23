# Dateipfad: src/smartdesk/handlers/wallpaper_manager.py
# Handler für Windows Desktop-Hintergrund-Verwaltung

import ctypes
import winreg
import os
from typing import Optional

# Windows API Konstanten für SystemParametersInfo
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

# Registry Keys für Wallpaper
WALLPAPER_KEY_PATH = r"Control Panel\Desktop"
WALLPAPER_VALUE_NAME = "Wallpaper"


def set_wallpaper(image_path: str) -> bool:
    """
    Setzt den Desktop-Hintergrund auf den angegebenen Bildpfad.
    
    Args:
        image_path: Vollständiger Pfad zum Hintergrundbild
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    if not image_path:
        print("[Wallpaper] Kein Hintergrundbild-Pfad angegeben.")
        return False
    
    # Pfad erweitern (für Umgebungsvariablen)
    expanded_path = os.path.expandvars(image_path)
    
    # Prüfen, ob Datei existiert
    if not os.path.exists(expanded_path):
        print(f"[Wallpaper] Fehler: Hintergrundbild nicht gefunden: {expanded_path}")
        return False
    
    try:
        # 1. Registry-Wert setzen
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WALLPAPER_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, WALLPAPER_VALUE_NAME, 0, winreg.REG_SZ, expanded_path)
        
        # 2. SystemParametersInfo aufrufen, um Windows zu benachrichtigen
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            expanded_path,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        
        if result:
            print(f"[Wallpaper] Hintergrund erfolgreich gesetzt: {expanded_path}")
            return True
        else:
            print("[Wallpaper] Fehler beim Setzen des Hintergrunds (SystemParametersInfo fehlgeschlagen)")
            return False
            
    except OSError as e:
        print(f"[Wallpaper] Registry-Fehler: {e}")
        return False
    except Exception as e:
        print(f"[Wallpaper] Unerwarteter Fehler: {e}")
        return False


def get_current_wallpaper() -> Optional[str]:
    """
    Liest den aktuellen Desktop-Hintergrund aus der Registry.
    
    Returns:
        Pfad zum aktuellen Hintergrundbild oder None bei Fehler
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WALLPAPER_KEY_PATH, 0, winreg.KEY_READ) as key:
            wallpaper_path, _ = winreg.QueryValueEx(key, WALLPAPER_VALUE_NAME)
            return wallpaper_path if wallpaper_path else None
    except OSError:
        print("[Wallpaper] Konnte aktuellen Hintergrund nicht aus Registry lesen")
        return None


def save_current_wallpaper_to_desktop(desktop) -> bool:
    """
    Speichert den aktuellen Windows-Hintergrund im Desktop-Objekt.
    
    Args:
        desktop: Desktop-Objekt, dessen wallpaper_path aktualisiert werden soll
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    current_wallpaper = get_current_wallpaper()
    
    if current_wallpaper:
        desktop.wallpaper_path = current_wallpaper
        print(f"[Wallpaper] Aktueller Hintergrund gespeichert: {current_wallpaper}")
        return True
    else:
        print("[Wallpaper] Konnte aktuellen Hintergrund nicht ermitteln")
        return False
