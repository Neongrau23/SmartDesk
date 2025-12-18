# Dateipfad: src/smartdesk/shared/first_run.py
"""
First-Run Setup für SmartDesk.
Führt beim ersten Start alle notwendigen Initialisierungen durch:
- Registry-Backup erstellen
- Datenordner initialisieren
- Konfigurationsdatei erstellen
- Original Desktop erstellen (geschützt)
"""

import os
from typing import Optional
import json
import winreg
from datetime import datetime

from .config import DATA_DIR
from .logging_config import get_logger

logger = get_logger(__name__)

# Pfad zur Setup-Konfigurationsdatei
SETUP_CONFIG_FILE = os.path.join(DATA_DIR, "setup.json")


def is_first_run() -> bool:
    """
    Prüft, ob dies der erste Start von SmartDesk ist.

    Returns:
        True wenn erster Start, False sonst
    """
    if not os.path.exists(SETUP_CONFIG_FILE):
        return True

    try:
        with open(SETUP_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return not config.get('first_run_completed', False)
    except (json.JSONDecodeError, IOError):
        return True


def get_setup_info() -> dict:
    """
    Liest die Setup-Konfiguration.

    Returns:
        Dict mit Setup-Informationen oder leeres Dict
    """
    if not os.path.exists(SETUP_CONFIG_FILE):
        return {}

    try:
        with open(SETUP_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_setup_info(info: dict) -> bool:
    """
    Speichert Setup-Informationen.

    Args:
        info: Dict mit Setup-Daten

    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SETUP_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error(f"Fehler beim Speichern der Setup-Info: {e}")
        return False


def get_current_wallpaper_path() -> str:
    """
    Liest den aktuellen Wallpaper-Pfad aus der Registry.
    
    Returns:
        Pfad zum aktuellen Wallpaper oder leerer String
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 
            r"Control Panel\Desktop", 
            0, 
            winreg.KEY_READ
        ) as key:
            value, _ = winreg.QueryValueEx(key, "Wallpaper")
            return value if value else ""
    except (FileNotFoundError, OSError) as e:
        logger.warning(f"Konnte Wallpaper-Pfad nicht lesen: {e}")
        return ""


def get_current_desktop_path() -> str:
    """
    Liest den aktuellen Desktop-Pfad aus der Registry.
    
    Returns:
        Pfad zum aktuellen Desktop-Ordner
    """
    from .config import KEY_USER_SHELL, VALUE_NAME
    
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            KEY_USER_SHELL,
            0,
            winreg.KEY_READ
        ) as key:
            value, _ = winreg.QueryValueEx(key, VALUE_NAME)
            return os.path.expandvars(value) if value else ""
    except (FileNotFoundError, OSError) as e:
        logger.warning(f"Konnte Desktop-Pfad nicht lesen: {e}")
        # Fallback zum Standard-Desktop
        return os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')


def create_original_desktop(silent: bool = False) -> bool:
    """
    Erstellt den geschützten Original Desktop beim Erststart.
    Erfasst den aktuellen Systemzustand als Sicherheitsnetz.
    
    Args:
        silent: Wenn True, keine Konsolenausgabe
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    from ..core.models.desktop import Desktop
    from ..core.storage.file_operations import load_desktops, save_desktops
    from ..core.services.icon_service import get_current_icon_positions
    
    try:
        # Prüfen ob bereits ein Original Desktop existiert
        desktops = load_desktops()
        if any(d.protected for d in desktops):
            logger.info("Original Desktop existiert bereits")
            return True
        
        # Aktuellen Systemzustand erfassen
        current_desktop_path = get_current_desktop_path()
        current_wallpaper = get_current_wallpaper_path()
        
        # Icon-Positionen erfassen (mit Timeout)
        try:
            icon_positions = get_current_icon_positions(timeout_seconds=5)
        except Exception as e:
            logger.warning(f"Konnte Icon-Positionen nicht lesen: {e}")
            icon_positions = []
        
        # Datum für den Namen
        date_str = datetime.now().strftime("%d.%m.%Y")
        
        # Original Desktop erstellen
        original_desktop = Desktop(
            name=f"🔒 Original ({date_str})",
            path=current_desktop_path,
            is_active=True,  # Der aktuelle Zustand ist aktiv
            wallpaper_path=current_wallpaper,
            icon_positionen=icon_positions,
            protected=True,  # GESCHÜTZT!
            created_at=datetime.now().isoformat()
        )
        
        # Am Anfang der Liste einfügen
        desktops.insert(0, original_desktop)
        save_desktops(desktops)
        
        logger.info(f"Original Desktop erstellt: {original_desktop.name}")
        return True
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Original Desktops: {e}")
        return False


def run_first_time_setup(silent: bool = False) -> bool:
    """
    Führt das First-Run-Setup durch.

    Args:
        silent: Wenn True, keine Konsolenausgabe

    Returns:
        True bei Erfolg, False bei Fehler
    """
    from .style import PREFIX_OK, PREFIX_WARN, PREFIX_ERROR
    from ..core.utils.backup_service import create_registry_backup

    def log_msg(prefix: str, msg: str):
        if not silent:
            print(f"{prefix} {msg}")
        logger.info(msg)

    logger.info("Starte First-Run-Setup...")

    if not silent:
        print("\n" + "=" * 50)
        print("  SmartDesk - Ersteinrichtung")
        print("=" * 50 + "\n")

    setup_info = get_setup_info()
    errors = []

    # 1. Datenordner erstellen
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        wallpapers_dir = os.path.join(DATA_DIR, "wallpapers")
        backups_dir = os.path.join(DATA_DIR, "backups")
        os.makedirs(wallpapers_dir, exist_ok=True)
        os.makedirs(backups_dir, exist_ok=True)
        log_msg(PREFIX_OK, "Datenordner erstellt")
        setup_info['data_dir'] = DATA_DIR
    except Exception as e:
        errors.append(f"Datenordner: {e}")
        log_msg(PREFIX_ERROR, f"Fehler beim Erstellen der Datenordner: {e}")

    # 2. Registry-Backup erstellen
    try:
        backup_path = create_registry_backup()
        if backup_path:
            log_msg(PREFIX_OK, f"Registry-Backup erstellt: {backup_path}")
            setup_info['initial_backup'] = backup_path
            setup_info['initial_backup_date'] = datetime.now().isoformat()
        else:
            log_msg(PREFIX_WARN, "Registry-Backup konnte nicht erstellt werden")
    except Exception as e:
        errors.append(f"Registry-Backup: {e}")
        log_msg(PREFIX_WARN, f"Registry-Backup fehlgeschlagen: {e}")

    # 3. Original Desktop erstellen (geschützt)
    try:
        original_created = create_original_desktop(silent=silent)
        if original_created:
            log_msg(PREFIX_OK, "Original Desktop erstellt (geschützt)")
            setup_info['original_desktop_created'] = True
        else:
            log_msg(PREFIX_WARN, "Original Desktop konnte nicht erstellt werden")
    except Exception as e:
        errors.append(f"Original Desktop: {e}")
        log_msg(PREFIX_ERROR, f"Fehler beim Erstellen des Original Desktops: {e}")

    # 4. Setup als abgeschlossen markieren
    setup_info['first_run_completed'] = True
    setup_info['setup_date'] = datetime.now().isoformat()
    setup_info['setup_version'] = '1.0.0'

    if errors:
        setup_info['setup_errors'] = errors

    if save_setup_info(setup_info):
        log_msg(PREFIX_OK, "Ersteinrichtung abgeschlossen")
    else:
        log_msg(PREFIX_ERROR, "Konnte Setup-Info nicht speichern")
        return False

    if not silent:
        print("\n" + "=" * 50)
        print(f"  Daten gespeichert in: {DATA_DIR}")
        print("=" * 50 + "\n")

    return len(errors) == 0


def ensure_setup_complete() -> bool:
    """
    Stellt sicher, dass das Setup durchgeführt wurde.
    Führt es bei Bedarf automatisch aus.

    Returns:
        True wenn Setup erfolgreich (oder bereits abgeschlossen)
    """
    if is_first_run():
        logger.info("Erster Start erkannt - führe Setup durch")
        return run_first_time_setup(silent=False)
    return True


def get_backup_path() -> str:
    """
    Gibt den Pfad zum Backup-Ordner zurück.
    """
    return os.path.join(DATA_DIR, "backups")


def get_initial_backup() -> Optional[str]:
    """
    Gibt den Pfad zum initialen Registry-Backup zurück.

    Returns:
        Pfad zum Backup oder None
    """
    info = get_setup_info()
    return info.get('initial_backup')
