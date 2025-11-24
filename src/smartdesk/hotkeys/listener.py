# Dateipfad: src/smartdesk/hotkeys/listener.py

# --- ALLE NOTWENDIGEN IMPORTS ---
from pynput.keyboard import Listener, Key
import sys
import os
import time
import traceback
from datetime import datetime

# --- NEUER IMPORT ---
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
        aktion_alt_9
    )
except ImportError as e:
    print(f"FEHLER: Konnte .actions nicht laden: {e}")
    print("Stelle sicher, dass actions.py im 'hotkeys'-Ordner liegt.")
    # Fallback, damit das Skript nicht abstürzt
    def aktion_alt_1(): print("FEHLER: Aktion 1 nicht geladen")
    def aktion_alt_2(): print("FEHLER: Aktion 2 nicht geladen")
    def aktion_alt_3(): print("FEHLER: Aktion 3 nicht geladen")
    def aktion_alt_4(): print("FEHLER: Aktion 4 nicht geladen")
    def aktion_alt_5(): print("FEHLER: Aktion 5 nicht geladen")
    def aktion_alt_6(): print("FEHLER: Aktion 6 nicht geladen")
    def aktion_alt_7(): print("FEHLER: Aktion 7 nicht geladen")
    def aktion_alt_8(): print("FEHLER: Aktion 8 nicht geladen")
    def aktion_alt_9(): print("FEHLER: Aktion 9 nicht geladen")


# --- 2. Zustand und Tastenspeicher ---
# (Dieser Teil bleibt unverändert)
current_keys = set()
wait_state = "IDLE"

# Log-Funktion (wird von start_listener() gesetzt)
_log_func = None


# --- 3. Listener-Funktionen (Das Kernstück) ---
# (Dieser Teil bleibt unverändert)

def on_press(key):
    global wait_state
    
    if wait_state == "WAITING_FOR_ALT_NUM":
        alt_gehalten = Key.alt_l in current_keys or Key.alt_r in current_keys
        
        key_char = None
        try:
            key_char = key.char
        except AttributeError:
            pass 

        is_modifier = key in (Key.alt_l, Key.alt_r, Key.ctrl_l, Key.ctrl_r, Key.shift, Key.shift_r)

        if alt_gehalten:
            if key_char == '1':
                if _log_func:
                    _log_func("Hotkey Alt+1 ausgeführt")
                aktion_alt_1()
                wait_state = "IDLE"
            elif key_char == '2':
                if _log_func:
                    _log_func("Hotkey Alt+2 ausgeführt")
                aktion_alt_2()
                wait_state = "IDLE"
            elif key_char == '3':
                if _log_func:
                    _log_func("Hotkey Alt+3 ausgeführt")
                aktion_alt_3()
                wait_state = "IDLE"
            elif key_char == '4':
                if _log_func:
                    _log_func("Hotkey Alt+4 ausgeführt")
                aktion_alt_4()
                wait_state = "IDLE"
            elif key_char == '5':
                if _log_func:
                    _log_func("Hotkey Alt+5 ausgeführt")
                aktion_alt_5()
                wait_state = "IDLE"
            elif key_char == '6':
                if _log_func:
                    _log_func("Hotkey Alt+6 ausgeführt")
                aktion_alt_6()
                wait_state = "IDLE"
            elif key_char == '7':
                if _log_func:
                    _log_func("Hotkey Alt+7 ausgeführt")
                aktion_alt_7()
                wait_state = "IDLE"
            elif key_char == '8':
                if _log_func:
                    _log_func("Hotkey Alt+8 ausgeführt")
                aktion_alt_8()
                wait_state = "IDLE"
            elif key_char == '9':
                if _log_func:
                    _log_func("Hotkey Alt+9 ausgeführt")
                aktion_alt_9()
                wait_state = "IDLE"
            
            elif is_modifier:
                pass
            
            else:
                print("-> Abgebrochen. (Alt + ungültige Taste gedrückt)")
                wait_state = "IDLE"

        elif is_modifier:
            pass
        
        else:
            if _log_func:
                _log_func("Abgebrochen: Ungültige Taste ohne Alt gedrückt")
            wait_state = "IDLE"
    
    current_keys.add(key)


def on_release(key):
    global wait_state
    
    if wait_state == "WAITING_FOR_ALT_NUM":
        if key == Key.alt_l or key == Key.alt_r:
            other_alt_held = False
            if key == Key.alt_l and Key.alt_r in current_keys:
                other_alt_held = True
            if key == Key.alt_r and Key.alt_l in current_keys:
                other_alt_held = True
                
            if not other_alt_held:
                print("-> Abgebrochen. (Alt losgelassen)")
                wait_state = "IDLE"

    strg_gehalten = Key.ctrl_l in current_keys or Key.ctrl_r in current_keys
    shift_gehalten = Key.shift in current_keys or Key.shift_r in current_keys
    
    is_shift_release = key == Key.shift or key == Key.shift_r
    trigger_1 = is_shift_release and strg_gehalten
    
    is_ctrl_release = key == Key.ctrl_l or key == Key.ctrl_r
    trigger_2 = is_ctrl_release and shift_gehalten

    if (trigger_1 or trigger_2) and wait_state == "IDLE":
        wait_state = "WAITING_FOR_ALT_NUM"
        msg = "\nStrg+Shift erkannt. Warte auf Alt + (1-9)..."
        print(msg)
        if _log_func:
            _log_func("Strg+Shift erkannt, warte auf Alt + (1-9)")
        
    try:
        current_keys.remove(key)
    except KeyError:
        pass 

# --- 4. Starte den Listener ---
# (Dieser Teil bleibt unverändert)

def start_listener():
    import os
    import sys
    from datetime import datetime
    
    # Setze UTF-8 Encoding für stdout/stderr um Unicode-Fehler zu vermeiden
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Log-Datei einrichten
    try:
        from ..config import DATA_DIR
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
    
    print("Hotkey-Listener wird gestartet...")
    log_message("Hotkey-Listener gestartet")
    print("Drücke 'Strg+Shift' (eine der Tasten loslassen) und dann Alt + (1-9).")
    print("Drücke 'Strg+C' im Terminal, um das Skript zu beenden.")
    log_message("Warte auf Hotkey-Eingaben...")
    
    # Cleanup-Funktion für PID-Datei
    def cleanup_pid_file():
        try:
            from ..config import DATA_DIR
            pid_file = os.path.join(DATA_DIR, "listener.pid")
            if os.path.exists(pid_file):
                os.remove(pid_file)
                print("PID-Datei bereinigt.")
                log_message("PID-Datei bereinigt")
        except Exception as e:
            print(f"Warnung: PID-Datei konnte nicht bereinigt werden: {e}")
            log_message(f"Warnung: PID-Datei-Cleanup fehlgeschlagen: {e}")
    
    # Setze die globale Log-Funktion
    global _log_func
    _log_func = log_message
    
    with Listener(on_press=on_press, on_release=on_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nListener durch Benutzer (Strg+C) gestoppt.")
            log_message("Listener durch Benutzer gestoppt (Strg+C)")
            cleanup_pid_file()
            sys.exit(0)
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
            log_message(f"Fehler aufgetreten: {e}")
            cleanup_pid_file()
        finally:
            print("Listener wird beendet.")
            log_message("Listener beendet")
            cleanup_pid_file()

def run_listener():
    """
    Hauptfunktion des Listener-Prozesses.
    """
    try:
        from ..config import DATA_DIR
    except ImportError:
        DATA_DIR = "."
    
    log_file = os.path.join(DATA_DIR, "listener.log")
    
    try:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"\n{'='*50}\n")
            log.write(f"[{datetime.now()}] === LISTENER START ===\n")
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
# Dieser Teil ist wichtig, falls du die Datei direkt mit
# python -m smartdesk.hotkeys.listener
# ausführen möchtest.
if __name__ == "__main__":
    # Direkt den Listener starten
    start_listener()