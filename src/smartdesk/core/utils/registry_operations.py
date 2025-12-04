# Dateipfad: src/smartdesk/core/utils/registry_operations.py

import winreg
import psutil

from ...shared.style import PREFIX_ERROR
from ...shared.localization import get_text


def update_registry_key(
    key_path: str, value_name: str, value: str, value_type=winreg.REG_SZ
) -> bool:
    """
    Setzt einen Wert in der Windows Registry (HKEY_CURRENT_USER).
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, value_name, 0, value_type, value)
        return True
    except WindowsError as e:
        print(
            f"{PREFIX_ERROR} {get_text('registry.error.update', key_path=key_path, e=e)}"
        )
        return False


def get_registry_value(key_path: str, value_name: str) -> str:
    """
    Liest einen Wert aus der Windows Registry (HKEY_CURRENT_USER).
    Gibt einen leeren String zurück, wenn der Schlüssel nicht existiert.
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ
        ) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
    except WindowsError:
        return ""


def save_tray_pid(pid):
    """Speichert die PID des Tray-Icon-Prozesses in der Registry"""
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\SmartDesk")
        winreg.SetValueEx(key, "TrayPID", 0, winreg.REG_DWORD, pid)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[DEBUG] Fehler beim Speichern der Tray-PID: {e}")


def get_tray_pid():
    """Liest die gespeicherte PID des Tray-Icon-Prozesses"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\SmartDesk")
        pid, _ = winreg.QueryValueEx(key, "TrayPID")
        winreg.CloseKey(key)
        return pid
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[DEBUG] Fehler beim Lesen der Tray-PID: {e}")
        return None


def is_process_running(pid):
    """
    Prüft, ob ein Prozess mit der gegebenen PID läuft
    und ob es ein Python-Prozess ist
    """
    try:
        if not psutil.pid_exists(pid):
            return False

        process = psutil.Process(pid)

        if not process.is_running():
            return False

        # Prüfe ob es ein Python-Prozess ist
        process_name = process.name().lower()
        if 'python' not in process_name:
            return False

        try:
            cmdline = ' '.join(process.cmdline()).lower()
            if 'tray_icon' in cmdline:
                return True
            return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return True

    except psutil.NoSuchProcess:
        return False
    except psutil.AccessDenied:
        return True
    except Exception as e:
        print(f"[DEBUG] Unerwarteter Fehler bei PID-Prüfung: {e}")
        return False


def cleanup_tray_pid():
    """Entfernt die gespeicherte Tray-PID (beim Beenden aufrufen)"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\SmartDesk", 0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, "TrayPID")
        winreg.CloseKey(key)
    except Exception:
        pass
