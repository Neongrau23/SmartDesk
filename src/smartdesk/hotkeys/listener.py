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
            char_code = KeyCode.from_char(part.lower())
            groups.append({char_code})
    return groups

def is_key_in_group(key, group):
    return key in group

def are_activation_keys_held(current_keys):
    if not ACTIVATION_KEY_GROUPS: return False
    for group in ACTIVATION_KEY_GROUPS:
        if not any(k in current_keys for k in group):
            return False
    return True

def is_part_of_activation(key):
    """Prüft ob key Teil der Aktivierungs-Gruppen ist."""
    for group in ACTIVATION_KEY_GROUPS:
        if key in group: return True
    return False

def is_action_key(key):
    return key in ACTION_KEY_GROUP

def is_any_action_key_held(current_keys):
    return any(k in current_keys for k in ACTION_KEY_GROUP)


# --- ZUSTANDSVARIABLEN ---
current_keys = set()
wait_state = "IDLE"

# Activation Logic
activation_potential = False # Wurde die Combo einmal voll erreicht?
activation_spoiled = False   # Wurde eine andere Taste gedrückt?

# Safety Logic for overlapping keys
action_key_used_after_activation = False 

alt_hold_timer = None
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
    global wait_state, activation_potential, activation_spoiled, action_key_used_after_activation
    _cancel_hold_timer()
    ctrl = _get_banner_ctrl()
    if ctrl:
        ctrl.reset()
    wait_state = "IDLE"
    activation_potential = False
    activation_spoiled = False
    action_key_used_after_activation = False

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

def _trigger_activation():
    global wait_state, alt_hold_timer, action_key_used_after_activation
    wait_state = "WAITING_FOR_ACTION"
    action_key_used_after_activation = False # Reset flag
    
    if _log_func:
        _log_func(f"Aktivierung erkannt (Release)! Warte auf {ACTION_KEY_NAME} + Taste...")
    print(get_text("hotkey_listener.info.wait_for_alt_num"))

    ctrl = _get_banner_ctrl()
    if ctrl:
        ctrl.on_ctrl_shift_triggered()
        
    # Wenn ActionKey bereits gehalten wird (z.B. Teil der Aktivierung), Timer starten
    if is_any_action_key_held(current_keys):
        # Wir markieren den Key als "benutzt", da er gehalten wird und wir in den Modus gehen
        pass

def on_press(key):
    global wait_state, alt_hold_timer, activation_potential, activation_spoiled, action_key_used_after_activation
    
    # 1. Action Key Feedback (unabhängig vom State)
    if is_action_key(key):
        ctrl = _get_banner_ctrl()
        if ctrl: ctrl.on_alt_pressed()
    
    # 2. Logik im WAITING State
    if wait_state == "WAITING_FOR_ACTION":
        
        # Markiere Action Key als aktiv benutzt
        if is_action_key(key):
            action_key_used_after_activation = True

        # Timer starten wenn Action-Key gedrückt wird
        if is_action_key(key):
            registry = get_registry()
            if registry.has_hold_action() and alt_hold_timer is None:
                alt_hold_timer = threading.Timer(0.3, _execute_hold_action)
                alt_hold_timer.start()

        action_held = is_any_action_key_held(current_keys) or is_action_key(key)
        is_ignored_key = is_action_key(key) or is_part_of_activation(key)

        key_char = None
        try: key_char = key.char
        except AttributeError: pass

        if action_held:
            registry = get_registry()
            
            if key_char and registry.has_combo_action(key_char):
                _cancel_hold_timer()
                if _log_func:
                    desc = registry.get_combo_description(key_char)
                    _log_func(get_text("hotkey_listener.log.action_executed", n=key_char, desc=desc))
                
                _close_banner_and_reset()
                registry.execute_combo(key_char)
            elif is_ignored_key:
                pass
            else:
                if _log_func: _log_func(f"Keine Aktion für: {key_char}")
                _close_banner_and_reset()
                print(get_text("hotkey_listener.info.abort_invalid_key"))

        elif is_ignored_key:
            pass
        else:
            # Irgendeine andere Taste ohne ActionKey -> Abbruch
            _close_banner_and_reset()

    # 3. Activation Logic im IDLE State
    elif wait_state == "IDLE":
        if is_part_of_activation(key):
            # Prüfen ob mit diesem Key die Combo voll ist
            temp_keys = current_keys.copy()
            temp_keys.add(key)
            if are_activation_keys_held(temp_keys):
                activation_potential = True
                activation_spoiled = False
        else:
            # Fremde Taste gedrückt -> Aktivierung kaputt
            if activation_potential or are_activation_keys_held(current_keys):
                activation_spoiled = True

    current_keys.add(key)


def on_release(key):
    global wait_state, activation_potential, activation_spoiled, action_key_used_after_activation

    just_triggered = False

    # 1. Activation Trigger (beim Loslassen im IDLE State)
    if wait_state == "IDLE":
        if is_part_of_activation(key):
            # Trigger Bedingung: War mal voll da, und nichts Fremdes gedrückt
            if activation_potential and not activation_spoiled:
                _trigger_activation()
                just_triggered = True
                # Wichtig: Nach Trigger nicht resetten, wait_state ist jetzt anders

    try:
        current_keys.remove(key)
    except KeyError:
        pass

    # Timer abbrechen
    if is_action_key(key):
        _cancel_hold_timer()
        if not is_any_action_key_held(current_keys):
            ctrl = _get_banner_ctrl()
            if ctrl: ctrl.on_alt_released()

    # Safety Reset wenn ActionKey losgelassen wird und wir im Waiting Mode sind
    if wait_state == "WAITING_FOR_ACTION" and not just_triggered:
        if is_action_key(key):
            if not is_any_action_key_held(current_keys):
                # NUR Resetten, wenn der Key NACH der Aktivierung benutzt wurde!
                if action_key_used_after_activation:
                    if _log_func: _log_func(f"{ACTION_KEY_NAME} losgelassen, Zyklus beendet.")
                    _close_banner_and_reset()
                else:
                    # Wir sind noch in der "Grace Period" nach der Aktivierung (User hat noch nicht neu gedrückt)
                    pass
    
    # Potential Reset wenn keine Activation Keys mehr gehalten werden
    if wait_state == "IDLE":
        if not any(is_part_of_activation(k) for k in current_keys):
            activation_potential = False
            activation_spoiled = False


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
    
    parsed_mod = parse_key_config(mod_str)
    ACTION_KEY_GROUP = set()
    for group in parsed_mod:
        ACTION_KEY_GROUP.update(group)

    log_message(f"Listener Konfiguration: Aktivierung='{act_str}', Aktion='{mod_str}'")
    print(f"[INFO] Listener geladen. Aktivierung: {act_str} (On Release), Aktion: {mod_str}")

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
