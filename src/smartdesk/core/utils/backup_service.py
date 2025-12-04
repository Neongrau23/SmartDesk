# Dateipfad: src/smartdesk/core/utils/backup_service.py
"""
Backup-Service für SmartDesk.
Erstellt und verwaltet Registry-Backups für sichere Wiederherstellung.
"""

import os
import winreg
from datetime import datetime
from typing import Optional

from ...shared.config import DATA_DIR, KEY_USER_SHELL, KEY_LEGACY_SHELL, VALUE_NAME
from ...shared.logging_config import get_logger

logger = get_logger(__name__)

# Backup-Ordner
BACKUP_DIR = os.path.join(DATA_DIR, "backups")


def get_backup_dir() -> str:
    """Gibt den Backup-Ordner zurück und erstellt ihn falls nötig."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    return BACKUP_DIR


def create_registry_backup(reason: str = "manual") -> Optional[str]:
    """
    Erstellt ein Backup der aktuellen Desktop-Registry-Werte.

    Args:
        reason: Grund für das Backup (z.B. "initial", "before_switch", "manual")

    Returns:
        Pfad zur Backup-Datei oder None bei Fehler
    """
    try:
        backup_dir = get_backup_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"registry_{reason}_{timestamp}.reg")

        # Aktuelle Werte auslesen
        user_shell_value = _read_registry_value(KEY_USER_SHELL, VALUE_NAME)
        legacy_shell_value = _read_registry_value(KEY_LEGACY_SHELL, VALUE_NAME)

        if not user_shell_value and not legacy_shell_value:
            logger.warning("Keine Registry-Werte zum Sichern gefunden")
            return None

        # .reg Datei erstellen
        with open(backup_file, 'w', encoding='utf-16') as f:
            f.write("Windows Registry Editor Version 5.00\n\n")

            # User Shell Folders
            if user_shell_value:
                key_path = f"HKEY_CURRENT_USER\\{KEY_USER_SHELL}"
                f.write(f"[{key_path}]\n")
                # Backslashes escapen für .reg Format
                escaped_value = user_shell_value.replace("\\", "\\\\")
                f.write(
                    f'"{VALUE_NAME}"=hex(2):{_string_to_reg_hex(user_shell_value)}\n\n'
                )

            # Legacy Shell Folders
            if legacy_shell_value:
                key_path = f"HKEY_CURRENT_USER\\{KEY_LEGACY_SHELL}"
                f.write(f"[{key_path}]\n")
                escaped_value = legacy_shell_value.replace("\\", "\\\\")
                f.write(f'"{VALUE_NAME}"="{escaped_value}"\n\n')

            # Metadata als Kommentar
            f.write(f"; Backup erstellt: {datetime.now().isoformat()}\n")
            f.write(f"; Grund: {reason}\n")
            f.write(f"; User Shell: {user_shell_value}\n")
            f.write(f"; Legacy Shell: {legacy_shell_value}\n")

        logger.info(f"Registry-Backup erstellt: {backup_file}")
        return backup_file

    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Registry-Backups: {e}")
        return None


def _read_registry_value(key_path: str, value_name: str) -> Optional[str]:
    """Liest einen Registry-Wert."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return os.path.expandvars(value)
    except WindowsError:
        return None


def _string_to_reg_hex(s: str) -> str:
    """
    Konvertiert einen String in das REG_EXPAND_SZ Hex-Format.
    Für .reg Dateien wird UTF-16LE mit null-terminator verwendet.
    """
    # In UTF-16LE kodieren + null-terminator
    encoded = (s + '\0').encode('utf-16-le')
    # Als Hex-Bytes mit Komma getrennt
    hex_bytes = ','.join(f'{b:02x}' for b in encoded)
    return hex_bytes


def list_backups() -> list[dict]:
    """
    Listet alle vorhandenen Backups auf.

    Returns:
        Liste von Dicts mit Backup-Informationen
    """
    backup_dir = get_backup_dir()
    backups = []

    try:
        for filename in os.listdir(backup_dir):
            if filename.endswith('.reg'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append(
                    {
                        'filename': filename,
                        'path': filepath,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                    }
                )

        # Nach Datum sortieren (neueste zuerst)
        backups.sort(key=lambda x: x['created'], reverse=True)

    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Backups: {e}")

    return backups


def get_latest_backup() -> Optional[str]:
    """
    Gibt den Pfad zum neuesten Backup zurück.

    Returns:
        Pfad zur neuesten Backup-Datei oder None
    """
    backups = list_backups()
    if backups:
        return backups[0]['path']
    return None


def restore_from_backup(backup_path: str) -> bool:
    """
    Stellt die Registry aus einem Backup wieder her.

    Args:
        backup_path: Pfad zur .reg Backup-Datei

    Returns:
        True bei Erfolg, False bei Fehler
    """
    import subprocess

    if not os.path.exists(backup_path):
        logger.error(f"Backup-Datei nicht gefunden: {backup_path}")
        return False

    try:
        # reg import ausführen (erfordert keine Admin-Rechte für HKCU)
        result = subprocess.run(
            ['reg', 'import', backup_path], capture_output=True, text=True
        )

        if result.returncode == 0:
            logger.info(f"Registry wiederhergestellt aus: {backup_path}")
            return True
        else:
            logger.error(f"Registry-Import fehlgeschlagen: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Fehler bei der Wiederherstellung: {e}")
        return False


def cleanup_old_backups(keep_count: int = 10) -> int:
    """
    Löscht alte Backups und behält nur die neuesten.

    Args:
        keep_count: Anzahl der Backups die behalten werden sollen

    Returns:
        Anzahl der gelöschten Backups
    """
    backups = list_backups()
    deleted = 0

    if len(backups) <= keep_count:
        return 0

    # Lösche alle außer den neuesten keep_count
    for backup in backups[keep_count:]:
        try:
            os.remove(backup['path'])
            deleted += 1
            logger.debug(f"Altes Backup gelöscht: {backup['filename']}")
        except Exception as e:
            logger.warning(f"Konnte Backup nicht löschen: {e}")

    if deleted > 0:
        logger.info(f"{deleted} alte Backup(s) gelöscht")

    return deleted


def create_backup_before_switch() -> Optional[str]:
    """
    Erstellt ein Backup vor einem Desktop-Wechsel.
    Räumt auch alte Backups auf.

    Returns:
        Pfad zum Backup oder None
    """
    # Alte Backups aufräumen
    cleanup_old_backups(keep_count=10)

    # Neues Backup erstellen
    return create_registry_backup(reason="before_switch")
