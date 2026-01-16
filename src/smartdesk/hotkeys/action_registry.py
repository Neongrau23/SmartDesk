# src/smartdesk/hotkeys/action_registry.py

from typing import Callable, Dict, Optional, Tuple
import logging

# Logger Setup
logger = logging.getLogger(__name__)

# --- 1. Importiere die Aktionen ---
try:
    from .actions import (
        aktion_alt_1,
        aktion_alt_2,
        aktion_alt_3,
        aktion_alt_4,
        aktion_alt_5,
        aktion_alt_6,
        aktion_alt_7,
        aktion_alt_8,
        aktion_alt_9,
    )
except ImportError as e:
    print(f"Fehler beim Importieren der Aktionen: {e}")
    def create_dummy_action(name: str) -> Callable[[], None]:
        def dummy_action():
            print(f"Aktion '{name}' nicht verfügbar.")
        return dummy_action
    aktion_alt_1 = create_dummy_action("aktion_alt_1")
    aktion_alt_2 = create_dummy_action("aktion_alt_2")
    aktion_alt_3 = create_dummy_action("aktion_alt_3")
    aktion_alt_4 = create_dummy_action("aktion_alt_4")
    aktion_alt_5 = create_dummy_action("aktion_alt_5")
    aktion_alt_6 = create_dummy_action("aktion_alt_6")
    aktion_alt_7 = create_dummy_action("aktion_alt_7")
    aktion_alt_8 = create_dummy_action("aktion_alt_8")
    aktion_alt_9 = create_dummy_action("aktion_alt_9")

# --- Import Hotkey Config ---
try:
    from ..shared.hotkey_config import HotkeyConfig
except ImportError:
    HotkeyConfig = None
    print("Warnung: HotkeyConfig konnte nicht importiert werden.")

# --- Mapping Action Names to Functions ---
# Maps configuration strings to (Function, Description)
ACTION_MAP: Dict[str, Tuple[Callable[[], None], str]] = {
    "switch_1": (aktion_alt_1, "Wechsel zu Desktop 1"),
    "switch_2": (aktion_alt_2, "Wechsel zu Desktop 2"),
    "switch_3": (aktion_alt_3, "Wechsel zu Desktop 3"),
    "switch_4": (aktion_alt_4, "Wechsel zu Desktop 4"),
    "switch_5": (aktion_alt_5, "Wechsel zu Desktop 5"),
    "switch_6": (aktion_alt_6, "Wechsel zu Desktop 6"),
    "switch_7": (aktion_alt_7, "Wechsel zu Desktop 7"),
    "switch_8": (aktion_alt_8, "Wechsel zu Desktop 8"),
    "save_icons": (aktion_alt_9, "Speichere Icons"),
}

# --- 2. ActionRegistry-Klasse ---
class ActionRegistry:
    def __init__(self):
        self._combo_actions: Dict[str, Callable[[], None]] = {}
        self._action_descriptions: Dict[str, str] = {}
        self._log_func: Optional[Callable[[str], None]] = None

    def register_combo_action(self, key: str, action: Callable[[], None], description: str):
        """Registriert eine Aktion für eine Tastenkombination."""
        if self._log_func:
            self._log_func(f"Registriere Aktion für Taste '{key}': {description}")
        self._combo_actions[key] = action
        self._action_descriptions[key] = description

    def has_combo_action(self, key: str) -> bool:
        """Prüft, ob eine Aktion für die gegebene Taste registriert ist."""
        # Key comparison is case-insensitive for robustness
        # But we expect the listener to normalize it.
        return key in self._combo_actions

    def execute_combo(self, key: str):
        """Führt die Aktion aus, die der Taste zugeordnet ist."""
        if self.has_combo_action(key):
            if self._log_func:
                self._log_func(f"Führe Aktion für Taste '{key}' aus.")
            self._combo_actions[key]()
        elif self._log_func:
            self._log_func(f"Keine Aktion für Taste '{key}' gefunden.")

    def get_combo_description(self, key: str) -> str:
        """Gibt eine Beschreibung der Aktion zurück."""
        return self._action_descriptions.get(key, f"Aktion für Alt+{key}")

    def set_log_func(self, log_func: Callable[[str], None]):
        self._log_func = log_func
        
    def has_hold_action(self) -> bool:
        return False
        
    def execute_hold(self):
        pass

# --- 3. Singleton-Instanz ---
_registry_instance = ActionRegistry()

def setup_actions():
    """Registriert Aktionen basierend auf der HotkeyConfig."""
    # Clear existing actions to avoid duplicates on re-run (if ever called multiple times)
    # _registry_instance._combo_actions.clear() # Not strictly necessary if only called once

    if HotkeyConfig:
        config = HotkeyConfig()
        hotkeys = config.get_hotkeys()

        for key_code, action_name in hotkeys.items():
            if action_name in ACTION_MAP:
                func, desc = ACTION_MAP[action_name]
                # Wir registrieren den Key so wie er ist.
                # WICHTIG: Der Listener muss Strings (z.B. "1", "f1") liefern.
                _registry_instance.register_combo_action(key_code, func, desc)
            else:
                msg = f"Warnung: Unbekannte Aktion '{action_name}' für Taste '{key_code}' in config.json"
                print(msg)
    else:
        # Fallback hardcoded defaults if import failed
        print("Fallback to hardcoded defaults due to missing HotkeyConfig.")
        _registry_instance.register_combo_action('1', aktion_alt_1, "Wechsel zu Desktop 1")
        _registry_instance.register_combo_action('2', aktion_alt_2, "Wechsel zu Desktop 2")
        _registry_instance.register_combo_action('3', aktion_alt_3, "Wechsel zu Desktop 3")
        _registry_instance.register_combo_action('4', aktion_alt_4, "Wechsel zu Desktop 4")
        _registry_instance.register_combo_action('5', aktion_alt_5, "Wechsel zu Desktop 5")
        _registry_instance.register_combo_action('6', aktion_alt_6, "Wechsel zu Desktop 6")
        _registry_instance.register_combo_action('7', aktion_alt_7, "Wechsel zu Desktop 7")
        _registry_instance.register_combo_action('8', aktion_alt_8, "Wechsel zu Desktop 8")
        _registry_instance.register_combo_action('9', aktion_alt_9, "Speichere Icons")

def get_registry() -> ActionRegistry:
    return _registry_instance

# --- 4. Initialisierung ---
setup_actions()
