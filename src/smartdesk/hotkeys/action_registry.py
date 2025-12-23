
# src/smartdesk/hotkeys/action_registry.py

from typing import Callable, Dict, Optional

# --- 1. Importiere die Aktionen ---
# Diese Aktionen werden ausgef├╝hrt, wenn eine Hotkey-Kombination erkannt wird.
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
    # Importiere hier weitere Aktionen, wenn du sie in actions.pyw hinzuf├╝gst.
except ImportError as e:
    print(f"Fehler beim Importieren der Aktionen: {e}")
    # Definiere Dummy-Funktionen als Fallback, damit der Listener nicht abst├╝rzt.
    def create_dummy_action(name: str) -> Callable[[], None]:
        def dummy_action():
            print(f"Aktion '{name}' nicht verf├╝gbar.")
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


# --- 2. ActionRegistry-Klasse ---
# Diese Klasse verwaltet die Zuordnung von Tasten zu Aktionen.
class ActionRegistry:
    def __init__(self):
        self._combo_actions: Dict[str, Callable[[], None]] = {}
        self._log_func: Optional[Callable[[str], None]] = None

    def register_combo_action(self, key: str, action: Callable[[], None], description: str):
        """Registriert eine Aktion f├╝r eine Tastenkombination (z.B. '1' f├╝r Alt+1)."""
        if self._log_func:
            self._log_func(f"Registriere Aktion f├╝r Taste '{key}': {description}")
        self._combo_actions[key] = action
        # Die Beschreibung wird hier nicht gespeichert, k├╢nnte aber erweitert werden.

    def has_combo_action(self, key: str) -> bool:
        """Pr├╝ft, ob eine Aktion f├╝r die gegebene Taste registriert ist."""
        if self._log_func:
            self._log_func(f"Checking for key '{key}'. Available keys: {list(self._combo_actions.keys())}")
        return key in self._combo_actions

    def execute_combo(self, key: str):
        """F├╝hrt die Aktion aus, die der Taste zugeordnet ist."""
        if self.has_combo_action(key):
            if self._log_func:
                self._log_func(f"F├╝hre Aktion f├╝r Taste '{key}' aus.")
            self._combo_actions[key]()
        elif self._log_func:
            self._log_func(f"Keine Aktion f├╝r Taste '{key}' gefunden.")

    def get_combo_description(self, key: str) -> str:
        """Gibt eine Beschreibung der Aktion zur├╝ck."""
        # Dies ist eine vereinfachte Version. F├╝r echte Beschreibungen
        # m├╝sste die Beschreibung in register_combo_action gespeichert werden.
        return f"Aktion f├╝r Alt+{key}"

    def set_log_func(self, log_func: Callable[[str], None]):
        """Setzt die Log-Funktion, die vom Listener verwendet wird."""
        self._log_func = log_func
        
    def has_hold_action(self) -> bool:
        return False
        
    def execute_hold(self):
        pass

# --- 3. Singleton-Instanz ---
# Wir erstellen eine einzige Instanz der Registry, die im gesamten Programm verwendet wird.
_registry_instance = ActionRegistry()

def setup_actions():
    """Registriert alle Aktionen in der Registry."""
    _registry_instance.register_combo_action('1', aktion_alt_1, "Wechsel zu Desktop 1")
    _registry_instance.register_combo_action('2', aktion_alt_2, "Wechsel zu Desktop 2")
    _registry_instance.register_combo_action('3', aktion_alt_3, "Wechsel zu Desktop 3")
    _registry_instance.register_combo_action('4', aktion_alt_4, "Wechsel zu Desktop 4")
    _registry_instance.register_combo_action('5', aktion_alt_5, "Wechsel zu Desktop 5")
    _registry_instance.register_combo_action('6', aktion_alt_6, "Wechsel zu Desktop 6")
    _registry_instance.register_combo_action('7', aktion_alt_7, "Wechsel zu Desktop 7")
    _registry_instance.register_combo_action('8', aktion_alt_8, "Wechsel zu Desktop 8")
    _registry_instance.register_combo_action('9', aktion_alt_9, "Speichere Icons")
    # F├╝ge hier weitere Aktionen hinzu.

def get_registry() -> ActionRegistry:
    """Gibt die Singleton-Instanz der ActionRegistry zur├╝ck."""
    return _registry_instance

# --- 4. Initialisierung ---
# Dieser Aufruf sorgt daf├╝r, dass die Aktionen beim Importieren des Moduls registriert werden.
setup_actions()
