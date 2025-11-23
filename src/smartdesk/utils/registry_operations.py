import winreg
from ..localization import get_text # <-- NEUER IMPORT

def update_registry_key(key_path: str, value_name: str, value: str, value_type=winreg.REG_SZ) -> bool:
    """
    Setzt einen Wert in der Windows Registry (HKEY_CURRENT_USER).
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, value_name, 0, value_type, value)
        return True
    except WindowsError as e:
        # --- LOKALISIERT ---
        print(get_text("registry.error.update", key_path=key_path, e=e))
        return False

def get_registry_value(key_path: str, value_name: str) -> str:
    """
    Liest einen Wert aus der Windows Registry (HKEY_CURRENT_USER).
    Gibt einen leeren String zurück, wenn der Schlüssel nicht existiert.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
    except WindowsError:
        return ""
    