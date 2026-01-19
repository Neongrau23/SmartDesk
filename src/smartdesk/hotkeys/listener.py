# --- ALLE NOTWENDIGEN IMPORTS ---
from pynput.keyboard import Listener, Key, KeyCode
import sys
import os
import traceback
from datetime import datetime
import threading

# --- DUMMY KLASSEN DEFINIEREN (vor Verwendung) ---
class DummyRegistry:
    def has_combo_action(self, key): return False
    def has_direct_action(self): return False
    def execute_combo(self, key): return False
    def execute_direct(self): return False
    def has_hold_action(self): return False
    def execute_hold(self): return False
    def get_combo_description(self, key): return ""
    def set_log_func(self, func): pass

# --- I18N IMPORT ---
try:
    from ..shared.localization import get_text
except ImportError:
    def get_text(key, **kwargs):
        text = key.split('.')[-1].replace('_', ' ').capitalize()
        if kwargs:
            text += ": " + str(kwargs)
        return f"[i18n: {text}]"

# --- SETTINGS IMPORT ---
try:
    from ..core.services.settings_service import load_settings
except ImportError:
    def load_settings(): return {}

# --- BANNER CONTROLLER IMPORT ---
try:
    from .banner_controller import get_banner_controller
    _banner_controller = None
except ImportError:
    _banner_controller = None
    def get_banner_controller(): return None

# --- AKTIONEN IMPORT ---
try:
    from .action_registry import get_registry, setup_actions
except ImportError:
    def get_registry(): return DummyRegistry()
    def setup_actions(): pass


# --- KONFIGURATION & KEY MAPPING ---

KEY_MAP = {
    'Ctrl': {Key.ctrl_l, Key.ctrl_r},
    'Shift': {Key.shift, Key.shift_r},
    'Alt': {Key.alt_l, Key.alt_r},
    'Win': {Key.cmd, Key.cmd_l, Key.cmd_r},
    'Tab': {Key.tab},
    'Space': {Key.space},
    'Enter': {Key.enter},
}

# Globale Konfiguration (wird in start_listener geladen)
ACTIVATION_KEY_GROUPS = [] # Liste von Sets, z.B. [{Ctrl_L, Ctrl_R}, {Shift_L, Shift_R}]
ACTION_KEY_GROUP = set()   # Set, z.B. {Alt_L, Alt_R}
ACTION_KEY_NAME = "Alt"    # Für Logs/Anzeige

def parse_key_config(config_str):
    """Parsed Strings wie 'Ctrl+Shift' in Key-Sets."""
    if not config_str: return []
    parts = [p.strip() for p in config_str.split('+')]
    groups = []
    for part in parts:
        if part in KEY_MAP:
            groups.append(KEY_MAP[part])
        elif len(part) == 1:
            # Einzelne Buchstaben/Zeichen
            char_code = KeyCode.from_char(part.lower())
            groups.append({char_code})
    return groups

def is_key_in_group(key, group):
    """Prüft ob key im group-Set ist."""
    return key in group

def are_activation_keys_held(current_keys):
    """Prüft ob alle Aktivierungs-Gruppen gedrückt sind."""
    if not ACTIVATION_KEY_GROUPS: return False
    for group in ACTIVATION_KEY_GROUPS:
        if not any(k in current_keys for k in group):
            return False
    return True

def is_action_key(key):
    """Prüft ob die Taste Teil der Aktions-Taste (z.B. Alt) ist."""
    return key in ACTION_KEY_GROUP

def is_any_action_key_held(current_keys):
    """Prüft ob irgendeine der Aktions-Tasten gehalten wird."""
    return any(k in current_keys for k in ACTION_KEY_GROUP)


# --- ZUSTANDSVARIABLEN ---
current_keys = set()
wait_state = "IDLE"
alt_hold_timer = None # Heißt historisch so, meint den Timer für Action-Key-Hold
_log_func = None


# --- LISTENER LOGIK ---

def _get_banner_ctrl():
    global _banner_controller
    if _banner_controller is None:
        ctrl = get_banner_controller()
        if ctrl and _log_func:
            ctrl._log = _log_func
        _banner_controller = ctrl
    return _banner_controller

def _close_banner_and_reset():
    global wait_state
    _cancel_hold_timer()
    ctrl = _get_banner_ctrl()
    if ctrl:
        ctrl.reset()
    wait_state = "IDLE"

def _execute_hold_action():
    global wait_state
    if wait_state == "WAITING_FOR_ACTION":
        if _log_func:
            _log_func(f"{ACTION_KEY_NAME}-Hold-Timer abgelaufen, führe Hold-Aktion aus.")
        
        registry = get_registry()
        if registry.has_hold_action():
            registry.execute_hold()

        wait_state = "IDLE"
        ctrl = _get_banner_ctrl()
        if ctrl:
            ctrl.on_action_executed()

def _cancel_hold_timer():
    global alt_hold_timer
    if alt_hold_timer and alt_hold_timer.is_alive():
        alt_hold_timer.cancel()
    alt_hold_timer = None

def on_press(key):
    global wait_state, alt_hold_timer
    
    # --- 1. Banner Controller Update ---
    if is_action_key(key):
        ctrl = _get_banner_ctrl()
        if ctrl:
            ctrl.on_alt_pressed() # Name im Controller ist noch on_alt_pressed, logisch aber on_action_key_pressed
    
    # --- 2. Logik im Warte-Zustand ---
    if wait_state == "WAITING_FOR_ACTION":
        
        # Timer starten wenn Action-Key gedrückt wird
        if is_action_key(key):
            registry = get_registry()
            if registry.has_hold_action() and alt_hold_timer is None:
                if _log_func:
                    _log_func(f"{ACTION_KEY_NAME} gedrückt, starte Timer...")
                alt_hold_timer = threading.Timer(0.3, _execute_hold_action)
                alt_hold_timer.start()

        action_held = is_any_action_key_held(current_keys) or is_action_key(key) # key is not yet in current_keys completely reliable here? add it logically

        key_char = None
        try:
            key_char = key.char
        except AttributeError:
            pass
        
        # Ist es eine Modifier-Taste? (Ignorieren wir meistens)
        # Wir prüfen, ob es eine der Aktivierungs- oder Aktionstasten ist
        is_known_modifier = False
        for group in ACTIVATION_KEY_GROUPS:
            if key in group: is_known_modifier = True
        if is_action_key(key): is_known_modifier = True

        if action_held:
            registry = get_registry()
            
            # Prüfen auf Kombinationen (ActionKey + Zeichen)
            if key_char and registry.has_combo_action(key_char):
                _cancel_hold_timer()
                if _log_func:
                    desc = registry.get_combo_description(key_char)
                    _log_func(get_text("hotkey_listener.log.action_executed", n=key_char, desc=desc))
                
                _close_banner_and_reset()
                registry.execute_combo(key_char)
            elif is_known_modifier:
                pass
            else:
                # Ungültige Taste während ActionKey gehalten
                if _log_func:
                    _log_func(f"Keine Aktion für: {key_char}")
                _close_banner_and_reset()
                print(get_text("hotkey_listener.info.abort_invalid_key"))

        elif is_known_modifier:
            pass
        else:
            # Irgendeine andere Taste ohne ActionKey -> Abbruch
            _close_banner_and_reset()

    # Taste zum Set hinzufügen
    current_keys.add(key)
    
    # --- 3. Aktivierungserkennung (State Transition) ---
    if are_activation_keys_held(current_keys) and wait_state == "IDLE":
        wait_state = "WAITING_FOR_ACTION"
        if _log_func:
            _log_func(f"Aktivierung erkannt! Warte auf {ACTION_KEY_NAME} + Taste...")
        print(get_text("hotkey_listener.info.wait_for_alt_num"))

        ctrl = _get_banner_ctrl()
        if ctrl:
            ctrl.on_ctrl_shift_triggered()
            
        # FIX: Wenn die Aktivierungstaste gleichzeitig die Aktionstaste ist (z.B. Ctrl+Alt -> Alt halten),
        # müssen wir den Timer hier manuell starten, da on_press für Alt schon vorbei ist.
        if is_any_action_key_held(current_keys):
            registry = get_registry()
            if registry.has_hold_action() and alt_hold_timer is None:
                if _log_func:
                    _log_func(f"{ACTION_KEY_NAME} ist bereits gedrückt, starte Timer...")
                alt_hold_timer = threading.Timer(0.3, _execute_hold_action)
                alt_hold_timer.start()


def on_release(key):
    global wait_state

    try:
        current_keys.remove(key)
    except KeyError:
        pass

    # Wenn wir warten...
    if wait_state == "WAITING_FOR_ACTION":
        # Prüfen ob Aktivierungs-Keys losgelassen wurden (optional, hier relevant für Abbruchbedingungen?)
        # Die ursprüngliche Logik war: Wenn Strg+Shift losgelassen, aber Alt noch nicht gedrückt -> warten weiter.
        pass

    # Timer abbrechen wenn ActionKey losgelassen
    if is_action_key(key):
        _cancel_hold_timer()
        
        # Banner Controller Info
        # Prüfen ob noch ein ANDERER ActionKey gehalten wird (z.B. Alt_R wenn Alt_L losgelassen)
        if not is_any_action_key_held(current_keys):
            ctrl = _get_banner_ctrl()
            if ctrl:
                ctrl.on_alt_released()

    # Sicherheits-Reset wenn ActionKey losgelassen wird und wir im Waiting Mode sind
    if wait_state == "WAITING_FOR_ACTION":
        if is_action_key(key):
            if not is_any_action_key_held(current_keys):
                if _log_func:
                    _log_func(f"{ACTION_KEY_NAME} losgelassen, Zyklus beendet.")
                _close_banner_and_reset()


def start_listener():
    # Windows Console Fix
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    # Logging
    try:
        from ..shared.logging_config import get_logger
        logger = get_logger('hotkey_listener')
    except ImportError:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger('hotkey_listener_fallback')

    def log_message(msg):
        logger.debug(msg)

    global _log_func
    _log_func = log_message

    # --- SETTINGS LADEN ---
    global ACTIVATION_KEY_GROUPS, ACTION_KEY_GROUP, ACTION_KEY_NAME
    settings = load_settings()
    act_str = settings.get("activation_keys", "Ctrl+Shift")
    mod_str = settings.get("action_modifier", "Alt")
    
    ACTION_KEY_NAME = mod_str
    ACTIVATION_KEY_GROUPS = parse_key_config(act_str)
    
    # Action Key parsen (hier erwarten wir meist einen Modifier)
    parsed_mod = parse_key_config(mod_str)
    ACTION_KEY_GROUP = set()
    for group in parsed_mod:
        ACTION_KEY_GROUP.update(group)

    log_message(f"Listener Konfiguration: Aktivierung='{act_str}', Aktion='{mod_str}'")
    print(f"[INFO] Listener geladen. Aktivierung: {act_str}, Aktion: {mod_str}")

    # --- START ---
    print(get_text("hotkey_listener.info.starting"))
    
    def cleanup_pid_file():
        try:
            from ..shared.config import DATA_DIR
            pid_file = os.path.join(DATA_DIR, "listener.pid")
            if os.path.exists(pid_file):
                os.remove(pid_file)
        except Exception:
            pass

    registry = get_registry()
    registry.set_log_func(log_message)
    
    try:
        setup_actions()
    except Exception as e:
        logger.error(str(e), exc_info=True)

    with Listener(on_press=on_press, on_release=on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            cleanup_pid_file()
            sys.exit(0)
        except Exception as e:
            cleanup_pid_file()
        finally:
            cleanup_pid_file()

if __name__ == "__main__":
    start_listener()
