# Dateipfad: src/smartdesk/hotkeys/listener.py

# --- ALLE NOTWENDIGEN IMPORTS ---
from pynput.keyboard import Listener, Key
import sys
import os
import traceback
from datetime import datetime

# --- NEUER IMPORT ---
try:
    # Importiere die get_text Funktion aus dem shared-Modul
    from ..shared.localization import get_text
except ImportError:
    # Fallback, falls das Skript eigenständig oder falsch importiert wird
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
    from .actions import (  # type: ignore[import-not-found]
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
    print(get_text("hotkey_listener.error.actions_load", e=e))
    print(get_text("hotkey_listener.error.actions_hint"))

    # Fallback, damit das Skript nicht abstürzt
    def aktion_alt_1():
        print(get_text("hotkey_listener.error.action_fallback", n=1))

    def aktion_alt_2():
        print(get_text("hotkey_listener.error.action_fallback", n=2))

    def aktion_alt_3():
        print(get_text("hotkey_listener.error.action_fallback", n=3))

    def aktion_alt_4():
        print(get_text("hotkey_listener.error.action_fallback", n=4))

    def aktion_alt_5():
        print(get_text("hotkey_listener.error.action_fallback", n=5))

    def aktion_alt_6():
        print(get_text("hotkey_listener.error.action_fallback", n=6))

    def aktion_alt_7():
        print(get_text("hotkey_listener.error.action_fallback", n=7))

    def aktion_alt_8():
        print(get_text("hotkey_listener.error.action_fallback", n=8))

    def aktion_alt_9():
        print(get_text("hotkey_listener.error.action_fallback", n=9))


# --- 2. Zustand und Tastenspeicher ---
# (Dieser Teil bleibt unverändert)
current_keys = set()
wait_state = "IDLE"

# Log-Funktion (wird von start_listener() gesetzt)
_log_func = None


# --- 3. Listener-Funktionen (Das Kernstück) ---


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
    ctrl = _get_banner_ctrl()
    if ctrl:
        ctrl.reset()


def on_press(key):
    global wait_state

    # Banner-Controller: Alt-Erkennung
    if key == Key.alt_l or key == Key.alt_r:
        ctrl = _get_banner_ctrl()
        if ctrl:
            ctrl.on_alt_pressed()

    if wait_state == "WAITING_FOR_ALT_NUM":
        alt_gehalten = Key.alt_l in current_keys or Key.alt_r in current_keys

        key_char = None
        try:
            key_char = key.char
        except AttributeError:
            pass

        is_modifier = key in (
            Key.alt_l,
            Key.alt_r,
            Key.ctrl_l,
            Key.ctrl_r,
            Key.shift,
            Key.shift_r,
        )

        if alt_gehalten:
            if key_char == '1':
                if _log_func:
                    _log_func(get_text("hotkey_listener.log.action_executed", n=1))
                _close_banner_and_reset()
                aktion_alt_1()
                wait_state = "IDLE"
            elif key_char == '2':
                if _log_func:
                    _log_func(get_text("hotkey_listener.log.action_executed", n=2))
                _close_banner_and_reset()
                aktion_alt_2()
                wait_state = "IDLE"
            elif key_char == '3':
                if _log_func:
                    _log_func(get_text("hotkey_listener.log.action_executed", n=3))
                _close_banner_and_reset()
                aktion_alt_3()
                wait_state = "IDLE"
            elif key_char == '4':
                if _log_func:
                    _log_func(get_text("hotkey_listener.log.action_executed", n=4))
                _close_banner_and_reset()
                aktion_alt_4()
                wait_state = "IDLE"
            elif key_char == '5':
                if _log_func:
                    _log_func(get_text("hotkey_listener.log.action_executed", n=5))
                _close_banner_and_reset()
                aktion_alt_5()
                wait_state = "IDLE"
            elif key_char == '6':
                if _log_func:
                    _log_func(get_text("hotkey_listener.log.action_executed", n=6))
                _close_banner_and_reset()
                aktion_alt_6()
                wait_state = "IDLE"
            elif key_char == '7':
                if _log_func:
                    _log_func(get_text("hotkey_listener.log.action_executed", n=7))
                _close_banner_and_reset()
                aktion_alt_7()
                wait_state = "IDLE"
            elif key_char == '8':
                if _log_func:
                    _log_func(get_text("hotkey_listener.log.action_executed", n=8))
                _close_banner_and_reset()
                aktion_alt_8()
                wait_state = "IDLE"
            elif key_char == '9':
                if _log_func:
                    _log_func(get_text("hotkey_listener.log.action_executed", n=9))
                _close_banner_and_reset()
                aktion_alt_9()
                wait_state = "IDLE"

            elif is_modifier:
                pass

            else:
                print(get_text("hotkey_listener.info.abort_invalid_key"))
                _close_banner_and_reset()
                wait_state = "IDLE"

        elif is_modifier:
            pass

        else:
            if _log_func:
                _log_func(get_text("hotkey_listener.log.abort_no_alt"))
            wait_state = "IDLE"

    current_keys.add(key)


def on_release(key):
    global wait_state

    # Banner-Controller: Alt losgelassen
    if key == Key.alt_l or key == Key.alt_r:
        # Prüfe ob die andere Alt-Taste noch gehalten wird
        other_alt_held = False
        if key == Key.alt_l and Key.alt_r in current_keys:
            other_alt_held = True
        if key == Key.alt_r and Key.alt_l in current_keys:
            other_alt_held = True

        if not other_alt_held:
            ctrl = _get_banner_ctrl()
            if ctrl:
                ctrl.on_alt_released()

    if wait_state == "WAITING_FOR_ALT_NUM":
        if key == Key.alt_l or key == Key.alt_r:
            other_alt_held = False
            if key == Key.alt_l and Key.alt_r in current_keys:
                other_alt_held = True
            if key == Key.alt_r and Key.alt_l in current_keys:
                other_alt_held = True

            if not other_alt_held:
                print(get_text("hotkey_listener.info.abort_alt_released"))
                wait_state = "IDLE"

    strg_gehalten = Key.ctrl_l in current_keys or Key.ctrl_r in current_keys
    shift_gehalten = Key.shift in current_keys or Key.shift_r in current_keys

    is_shift_release = key == Key.shift or key == Key.shift_r
    trigger_1 = is_shift_release and strg_gehalten

    is_ctrl_release = key == Key.ctrl_l or key == Key.ctrl_r
    trigger_2 = is_ctrl_release and shift_gehalten

    if (trigger_1 or trigger_2) and wait_state == "IDLE":
        wait_state = "WAITING_FOR_ALT_NUM"
        msg = get_text("hotkey_listener.info.wait_for_alt_num")
        print(msg)
        if _log_func:
            _log_func(get_text("hotkey_listener.log.wait_for_alt_num"))

        # Banner-Controller: Strg+Shift erkannt
        ctrl = _get_banner_ctrl()
        if ctrl:
            ctrl.on_ctrl_shift_triggered()

    try:
        current_keys.remove(key)
    except KeyError:
        pass


# --- 4. Starte den Listener ---


def start_listener():
    import os
    import sys
    from datetime import datetime

    # Setze UTF-8 Encoding für stdout/stderr um Unicode-Fehler zu vermeiden
    if sys.platform == 'win32':
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding='utf-8', errors='replace'
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding='utf-8', errors='replace'
        )

    # Log-Datei einrichten
    try:
        from ..shared.config import DATA_DIR

        log_file = os.path.join(DATA_DIR, "listener.log")
    except ImportError:
        log_file = "listener.log"

    def log_message(msg):
        """Schreibt eine Nachricht ins Log mit Zeitstempel."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {msg}\n"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception:
            pass  # Fehler beim Loggen ignorieren

    print(get_text("hotkey_listener.info.starting"))
    log_message(get_text("hotkey_listener.log.started"))
    print(get_text("hotkey_listener.info.instructions"))
    print(get_text("hotkey_listener.info.instructions_stop"))
    log_message(get_text("hotkey_listener.log.waiting"))

    # Cleanup-Funktion für PID-Datei
    def cleanup_pid_file():
        try:
            from ..shared.config import DATA_DIR

            pid_file = os.path.join(DATA_DIR, "listener.pid")
            if os.path.exists(pid_file):
                os.remove(pid_file)
                print(get_text("hotkey_listener.info.pid_cleaned"))
                log_message(get_text("hotkey_listener.log.pid_cleaned"))
        except Exception as e:
            print(get_text("hotkey_listener.warn.pid_clean_failed", e=e))
            log_message(get_text("hotkey_listener.log.pid_clean_failed", e=e))

    # Setze die globale Log-Funktion
    global _log_func
    _log_func = log_message

    with Listener(on_press=on_press, on_release=on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print(get_text("hotkey_listener.info.stopped_user"))
            log_message(get_text("hotkey_listener.log.stopped_user"))
            cleanup_pid_file()
            sys.exit(0)
        except Exception as e:
            print(get_text("hotkey_listener.error.generic", e=e))
            log_message(get_text("hotkey_listener.log.error_generic", e=e))
            cleanup_pid_file()
        finally:
            print(get_text("hotkey_listener.info.stopping"))
            log_message(get_text("hotkey_listener.log.stopped"))
            cleanup_pid_file()


def run_listener():
    """
    Hauptfunktion des Listener-Prozesses.
    """
    try:
        from ..shared.config import DATA_DIR
    except ImportError:
        DATA_DIR = "."

    log_file = os.path.join(DATA_DIR, "listener.log")

    # HINWEIS: Die folgenden log.write-Aufrufe werden NICHT internationalisiert.
    # Dies sind System-Logs auf niedriger Ebene (wie Tracebacks), die für
    # die Entwickler-Fehlersuche gedacht sind. Die "log_message"-Aufrufe
    # (die internationalisiert sind) werden dem Benutzer im UI-Debug-Fenster angezeigt.
    try:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"\n{'=' * 50}\n")
            log.write(f"[{datetime.now()}] === LISTENER START ===")
            log.write(f"[{datetime.now()}] PID: {os.getpid()}\n")
            log.write(f"[{datetime.now()}] Python: {sys.executable}\n")
            log.write(f"[{datetime.now()}] Working Dir: {os.getcwd()}\n")
            log.flush()

            log.write(f"[{datetime.now()}] Starte pynput Listener...\n")
            log.flush()

        # Starte den bestehenden Listener
        start_listener()

    except KeyboardInterrupt:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"[{datetime.now()}] === KEYBOARD INTERRUPT ===\n")
    except Exception as e:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"[{datetime.now()}] === KRITISCHER FEHLER ===\n")
            log.write(f"[{datetime.now()}] {type(e).__name__}: {e}\n")
            log.write(f"[{datetime.now()}] Traceback:\n{traceback.format_exc()}\n")
    finally:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"[{datetime.now()}] === LISTENER ENDE ===\n")


# --- 5. Skript ausführen ---
# (Dieser Teil bleibt unverändert)
if __name__ == "__main__":
    # Direkt den Listener starten
    start_listener()

    # Füge das src-Verzeichnis zum Python-Path hinzu
    script_dir = os.path.dirname(os.path.abspath(__file__))
    smartdesk_dir = os.path.dirname(script_dir)
    src_dir = os.path.dirname(smartdesk_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
