# --- ALLE NOTWENDIGEN IMPORTS ---
from pynput.keyboard import Listener, Key
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
    # Importiere die get_text Funktion aus dem shared-Modul
    from ..shared.localization import get_text
except ImportError:
    # Fallback
    print("[FALLBACK] Konnte 'get_text' nicht importieren.")
    def get_text(key, **kwargs):
        text = key.split('.')[-1].replace('_', ' ').capitalize()
        if kwargs:
            text += ": " + str(kwargs)
        return f"[i18n: {text}]"

# --- BANNER CONTROLLER IMPORT ---
try:
    from .banner_controller import get_banner_controller
    _banner_controller = None  # Wird lazy initialisiert
    print("[INFO] Banner-Controller erfolgreich importiert")
except ImportError as e:
    print(f"[WARNING] Banner-Controller Import fehlgeschlagen: {e}")
    _banner_controller = None
    def get_banner_controller():
        return None

# --- AKTIONEN IMPORT ---
try:
    from .action_registry import get_registry, setup_actions
except ImportError as e:
    print(get_text("hotkey_listener.error.actions_load", e=e))
    # Fallback-Funktionen
    def get_registry(): return DummyRegistry()
    def setup_actions(): pass


# --- 2. Zustand und Tastenspeicher ---
current_keys = set()
wait_state = "IDLE"

# Timer für Alt-Hold-Aktion
alt_hold_timer = None

# Log-Funktion
_log_func = None


# --- 3. Listener-Funktionen ---

def _get_key_identifier(key):
    """
    Konvertiert ein pynput Key-Objekt in einen String-Identifier,
    wie er in der Konfiguration erwartet wird.
    """
    if hasattr(key, 'char') and key.char is not None:
        return key.char # Z.B. '1', 'a'

    # Check for special keys (Key.f1, Key.enter, etc.)
    try:
        if isinstance(key, Key):
            return key.name # Z.B. 'f1'
    except AttributeError:
        pass

    return str(key).replace('Key.', '')


def _get_banner_ctrl():
    """Lazy-Initialisierung des Banner-Controllers."""
    global _banner_controller
    if _banner_controller is None:
        ctrl = get_banner_controller()
        if ctrl and _log_func:
            ctrl._log = _log_func
        _banner_controller = ctrl
    return _banner_controller


def _close_banner_and_reset():
    """Schließt das Banner und setzt den Controller zurück."""
    global wait_state
    _cancel_alt_hold_timer()
    ctrl = _get_banner_ctrl()
    if ctrl:
        ctrl.reset()
    wait_state = "IDLE"


def _execute_alt_hold_action():
    """Wird vom Timer aufgerufen, um die Hold-Aktion auszuführen."""
    global wait_state
    if wait_state == "WAITING_FOR_ALT_NUM":
        if _log_func:
            _log_func("Alt-Hold-Timer abgelaufen, führe Hold-Aktion aus.")
        
        registry = get_registry()
        if registry.has_hold_action():
            registry.execute_hold()

        # Zustand zurücksetzen
        wait_state = "IDLE"
        
        # Banner-Controller benachrichtigen
        ctrl = _get_banner_ctrl()
        if ctrl:
            ctrl.on_action_executed()


def _cancel_alt_hold_timer():
    """Bricht den laufenden Alt-Hold-Timer ab."""
    global alt_hold_timer
    if alt_hold_timer and alt_hold_timer.is_alive():
        alt_hold_timer.cancel()
    alt_hold_timer = None


def on_press(key):
    global wait_state
    
    # Banner-Controller: Alt-Erkennung (für interne State-Machine des Controllers)
    if key == Key.alt_l or key == Key.alt_r:
        ctrl = _get_banner_ctrl()
        if ctrl:
            ctrl.on_alt_pressed()
    
    # Wenn wir bereits auf Alt warten (Strg+Shift wurden vorher gedrückt)
    if wait_state == "WAITING_FOR_ALT_NUM":
        global alt_hold_timer
        
        # Timer für Hold-Aktion starten, wenn JETZT Alt gedrückt wird
        if key in (Key.alt_l, Key.alt_r):
            registry = get_registry()
            # Nur starten, wenn Timer noch nicht läuft
            if registry.has_hold_action() and alt_hold_timer is None:
                if _log_func:
                    _log_func("Alt gedrückt, starte Hold-Timer...")
                alt_hold_timer = threading.Timer(0.3, _execute_alt_hold_action)
                alt_hold_timer.start()

        alt_gehalten = Key.alt_l in current_keys or Key.alt_r in current_keys

        # Identifier für die Taste ermitteln (z.B. '1', 'f1')
        key_id = _get_key_identifier(key)

        is_modifier = key in (
            Key.alt_l, Key.alt_r, Key.ctrl_l, Key.ctrl_r,
            Key.shift, Key.shift_r
        )

        if alt_gehalten:
            registry = get_registry()
            if _log_func:
                _log_func(f"alt held, key_id: {key_id}")
            
            # Prüfen auf Kombinationen (z.B. Alt+1 oder Alt+F1)
            if key_id and registry.has_combo_action(key_id):
                _cancel_alt_hold_timer()
                if _log_func:
                    desc = registry.get_combo_description(key_id)
                    _log_func(get_text("hotkey_listener.log.action_executed", n=key_id, desc=desc))
                    _log_func(f"Executing combo action for key: {key_id}")
                
                _close_banner_and_reset()
                registry.execute_combo(key_id)
            elif is_modifier:
                pass
            else:
                # Ungültige Taste während Alt gehalten wird -> Reset
                if _log_func:
                    _log_func(f"No combo action for key: {key_id}")
                _close_banner_and_reset()
                print(get_text("hotkey_listener.info.abort_invalid_key"))

        elif is_modifier:
            pass
        else:
            # Irgendeine andere Taste (z.B. Buchstabe) ohne Alt -> Abbruch des Wartens
            _close_banner_and_reset()
            if _log_func:
                _log_func(get_text("hotkey_listener.log.abort_no_alt"))

    current_keys.add(key)
    
    # Strg+Shift-Erkennung (Der Einstiegspunkt)
    ctrl_held = Key.ctrl_l in current_keys or Key.ctrl_r in current_keys
    shift_held = Key.shift in current_keys or Key.shift_r in current_keys

    # Wenn IDLE und Strg+Shift gedrückt werden -> Zustand wechseln
    if ctrl_held and shift_held and wait_state == "IDLE":
        wait_state = "WAITING_FOR_ALT_NUM"
        if _log_func:
            _log_func("State changed to WAITING_FOR_ALT_NUM")
        msg = get_text("hotkey_listener.info.wait_for_alt_num")
        print(msg)
        if _log_func:
            _log_func(get_text("hotkey_listener.log.wait_for_alt_num"))

        ctrl = _get_banner_ctrl()
        if ctrl:
            ctrl.on_ctrl_shift_triggered()


def on_release(key):
    global wait_state

    try:
        current_keys.remove(key)
    except KeyError:
        pass

    # Logik während wir auf Alt (oder Alt-Release) warten
    if wait_state == "WAITING_FOR_ALT_NUM":
        
        # Prüfung: Sind Modifizierer losgelassen worden?
        if key in (Key.ctrl_l, Key.ctrl_r, Key.shift, Key.shift_r):
            ctrl_held = any(k in current_keys for k in (Key.ctrl_l, Key.ctrl_r))
            shift_held = any(k in current_keys for k in (Key.shift, Key.shift_r))
            alt_held = any(k in current_keys for k in (Key.alt_l, Key.alt_r))

            # KORREKTUR: Wenn Strg+Shift losgelassen sind, aber Alt noch nicht gedrückt ist:
            # Wir RESETTEN NICHT. Wir warten weiter auf Alt.
            if not ctrl_held and not shift_held and not alt_held:
                if _log_func:
                    _log_func("Strg und Shift losgelassen, warte weiter auf Alt...")
                # HIER WURDE DER FEHLER BEHOBEN: _close_banner_and_reset() ENTFERNT

    # Timer abbrechen, wenn Alt losgelassen wird (egal in welchem Zustand)
    if key in (Key.alt_l, Key.alt_r):
        _cancel_alt_hold_timer()

    # Banner-Controller: Alt losgelassen (Signal an Controller zum Schließen der UI)
    if key == Key.alt_l or key == Key.alt_r:
        other_alt_held = any(k in current_keys for k in (Key.alt_l, Key.alt_r))
        if not other_alt_held:
            ctrl = _get_banner_ctrl()
            if ctrl:
                ctrl.on_alt_released()

    # Sicherheits-Reset, nur wenn wir wirklich fertig sind
    # (Dies verhindert, dass der Listener im "WAITING" hängen bleibt, wenn Alt losgelassen wurde)
    if wait_state == "WAITING_FOR_ALT_NUM":
        if key == Key.alt_l or key == Key.alt_r:
            other_alt_held = any(k in current_keys for k in (Key.alt_l, Key.alt_r))
            if not other_alt_held:
                if _log_func:
                    _log_func("Alt losgelassen, Zyklus beendet.")
                    _log_func("Resetting state to IDLE")
                _close_banner_and_reset()


# --- 4. Starte den Listener ---

def start_listener():
    # Logging Setup für Windows Konsole
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    try:
        from ..shared.logging_config import get_logger
        logger = get_logger('hotkey_listener')
    except ImportError:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger('hotkey_listener_fallback')

    def log_message(msg):
        logger.debug(msg)

    print(get_text("hotkey_listener.info.starting"))
    log_message(get_text("hotkey_listener.log.started"))
    print(get_text("hotkey_listener.info.instructions"))
    print(get_text("hotkey_listener.info.instructions_stop"))
    log_message(get_text("hotkey_listener.log.waiting"))

    def cleanup_pid_file():
        try:
            from ..shared.config import DATA_DIR
            pid_file = os.path.join(DATA_DIR, "listener.pid")
            if os.path.exists(pid_file):
                os.remove(pid_file)
        except Exception:
            pass

    global _log_func
    _log_func = log_message

    registry = get_registry()
    registry.set_log_func(log_message)
    
    try:
        setup_actions()
        log_message(get_text("hotkey_listener.log.actions_loaded"))
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


def run_listener():
    """Hauptfunktion des Listener-Prozesses."""
    try:
        from ..shared.config import DATA_DIR
    except ImportError:
        DATA_DIR = "."
    
    log_file = os.path.join(DATA_DIR, "listener.log")
    
    try:
        start_listener()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"\nCRITICAL ERROR: {e}\n{traceback.format_exc()}\n")


if __name__ == "__main__":
    start_listener()
    
    # Path Setup für Standalone-Test
    script_dir = os.path.dirname(os.path.abspath(__file__))
    smartdesk_dir = os.path.dirname(script_dir)
    src_dir = os.path.dirname(smartdesk_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)