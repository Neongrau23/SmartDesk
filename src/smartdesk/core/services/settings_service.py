"""
Service zur Verwaltung von Anwendungseinstellungen (settings.json).
"""
import json
import os
from typing import Any

from ...shared.config import DATA_DIR
from ...shared.logging_config import get_logger

logger = get_logger(__name__)

SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Standardwerte
DEFAULTS = {
    "auto_switch_enabled": False,
    "theme": "dark",
    "start_minimized": False,
    "show_switch_animation": True,
    "activation_keys": "Ctrl+Shift",
    "action_modifier": "Alt",
    "hold_duration": 0.5
}

def load_settings() -> dict:
    """Lädt die Einstellungen aus der JSON-Datei."""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULTS.copy()

    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Merge mit Defaults, falls neue Keys dazu kamen
            settings = DEFAULTS.copy()
            settings.update(data)
            return settings
    except Exception as e:
        logger.error(f"Fehler beim Laden der Einstellungen: {e}")
        return DEFAULTS.copy()

def save_settings(settings: dict) -> bool:
    """Speichert die Einstellungen."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Einstellungen: {e}")
        return False

def get_setting(key: str, default: Any = None) -> Any:
    """Holt einen einzelnen Einstellungswert."""
    settings = load_settings()
    return settings.get(key, default if default is not None else DEFAULTS.get(key))

def set_setting(key: str, value: Any) -> bool:
    """Setzt einen einzelnen Einstellungswert und speichert."""
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)
