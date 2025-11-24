import os
import sys
import subprocess
from typing import Optional

# Interne Importe
try:
    # --- GEÄNDERT ---
    # Wir brauchen jetzt DATA_DIR (für die Logs) und BASE_DIR (für das venv)
    from ..config import BASE_DIR, DATA_DIR
    from ..localization import get_text
    from ..ui.style import PREFIX_OK, PREFIX_WARN, PREFIX_ERROR
except ImportError:
    # Fallback für den Fall, dass das Skript isoliert getestet wird
    print("FEHLER: hotkey_manager.py konnte Pakete nicht importieren.")
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    # Simuliere DATA_DIR im Fallback
    DATA_DIR = BASE_DIR 
    def get_text(key, **kwargs): return key.format(**kwargs)
    PREFIX_OK = "[OK]"
    PREFIX_WARN = "[WARN]"
    PREFIX_ERROR = "[FEHLER]"


# --- Pfad-Konfiguration (AKTUALISIERT) ---

# Das Arbeitsverzeichnis ist weiterhin der Projekt-Root (für venv)
WORKING_DIRECTORY = BASE_DIR

# --- GEÄNDERT: Alle Laufzeit-Dateien nutzen jetzt DATA_DIR (AppData) ---
PID_FILE = os.path.join(DATA_DIR, "listener.pid")
LOG_FILE = os.path.join(DATA_DIR, "listener.log")
ERR_FILE = os.path.join(DATA_DIR, "listener_error.log")

# Pfad zur Python-Exe im venv (bleibt im WORKING_DIRECTORY)
PYTHON_EXECUTABLE = os.path.join(WORKING_DIRECTORY, ".venv", "Scripts", "python.exe")

# Befehl zum Starten des Listener-Moduls
COMMAND_TO_RUN = [PYTHON_EXECUTABLE, "-m", "smartdesk.hotkeys.listener"]


def get_listener_pid() -> Optional[int]:
    """
    Prüft, ob die PID-Datei existiert und liest die PID.
    Gibt die PID als Integer zurück oder None, wenn nicht gefunden/ungültig.
    """
    if not os.path.exists(PID_FILE):
        return None
    
    try:
        with open(PID_FILE, 'r', encoding='utf-8') as f:
            pid = int(f.read().strip())
        return pid
    except (IOError, ValueError) as e:
        print(f"{PREFIX_ERROR} {get_text('hotkey_manager.error.read_pid', e=e)}")
        # Lösche defekte PID-Datei
        try:
            os.remove(PID_FILE)
        except OSError:
            pass
        return None

def start_listener():
    """
    Startet den Hotkey-Listener als separaten Prozess.
    Implementiert die Logik von start_listener.py.
    """
    if get_listener_pid():
        print(f"{PREFIX_WARN} {get_text('hotkey_manager.warn.already_running')}")
        return

    # 1. Prüfen, ob die venv-Python-Exe existiert
    if not os.path.exists(PYTHON_EXECUTABLE):
        print(f"{PREFIX_ERROR} {get_text('hotkey_manager.error.python_not_found', path=PYTHON_EXECUTABLE)}")
        print(f"{PREFIX_WARN} Stelle sicher, dass das venv '.venv' heißt oder passe den Pfad in 'hotkey_manager.py' an.")
        return

    print(f"{PREFIX_OK} {get_text('hotkey_manager.info.starting')}")
    
    try:
        # 2. Flags für Windows setzen (kein Konsolenfenster)
        creation_flags = 0
        if os.name == 'nt':
            creation_flags = subprocess.CREATE_NO_WINDOW
            
        # 3. Log-Dateien öffnen (im 'append'-Modus)
        # WICHTIG: Diese Handles werden an den Popen-Prozess übergeben.
        # Wir schließen sie hier NICHT, da Popen sie braucht.
        # HINWEIS: DATA_DIR (AppData) wird in config.py erstellt, 
        # daher müssen wir hier nicht os.makedirs() aufrufen.
        log_f = open(LOG_FILE, 'a', buffering=1, encoding='utf-8')
        err_f = open(ERR_FILE, 'a', buffering=1, encoding='utf-8')

        # 4. Prozess starten (nicht blockierend)
        process = subprocess.Popen(
            COMMAND_TO_RUN,
            cwd=WORKING_DIRECTORY, # CWD muss BASE_DIR sein, damit "python -m" funktioniert
            stdout=log_f,
            stderr=err_f,
            stdin=subprocess.DEVNULL,
            creationflags=creation_flags,
            close_fds=True # Wichtig für non-Windows
        )
        
        print(f"{PREFIX_OK} {get_text('hotkey_manager.info.start_success', pid=process.pid)}")

        # 5. PID in Datei schreiben
        try:
            with open(PID_FILE, 'w', encoding='utf-8') as f:
                f.write(str(process.pid))
        except IOError as e:
            print(f"{PREFIX_WARN} {get_text('hotkey_manager.warn.pid_write_failed', e=e)}")

    except Exception as e:
        print(f"{PREFIX_ERROR} {get_text('hotkey_manager.error.start_failed', e=e)}")

def stop_listener():
    """
    Stoppt den Hotkey-Listener-Prozess anhand der PID-Datei.
    Implementiert die Logik von stop_listener.py.
    """
    pid = get_listener_pid()
    if not pid:
        print(f"{PREFIX_WARN} {get_text('hotkey_manager.warn.not_running')}")
        return

    print(f"{PREFIX_OK} {get_text('hotkey_manager.info.stopping', pid=pid)}")
    
    try:
        # 1. Prozess beenden (Windows-spezifisch)
        if os.name == 'nt':
            # Versteckt das taskkill-Fenster
            kill_flags = subprocess.CREATE_NO_WINDOW
            
            # --- KORREKTUR: Das "/T" Flag wurde entfernt ---
            result = subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)], # <-- "/T" ENTFERNT
                check=True,
                capture_output=True,
                text=True,
                creationflags=kill_flags 
            )
        
        # 2. Prozess beenden (Linux/macOS)
        else:
            os.kill(pid, 15) # 15 = signal.SIGTERM
            print(f"{PREFIX_OK} {get_text('hotkey_manager.info.signal_sent', pid=pid)}")

        print(f"{PREFIX_OK} {get_text('hotkey_manager.info.stop_success', pid=pid)}")

    except (subprocess.CalledProcessError, ProcessLookupError):
        # CalledProcessError: taskkill konnte den Prozess nicht finden
        # ProcessLookupError: os.kill konnte den Prozess nicht finden
        print(f"{PREFIX_WARN} {get_text('hotkey_manager.warn.process_not_found', pid=pid)}")
    
    except Exception as e:
        print(f"{PREFIX_ERROR} {get_text('hotkey_manager.error.stop_failed', e=e)}")
        
    finally:
        # 3. PID-Datei aufräumen, auch wenn der Prozess nicht gefunden wurde
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
                print(f"{PREFIX_OK} {get_text('hotkey_manager.info.pid_cleaned')}")
            except OSError as e:
                print(f"{PREFIX_WARN} {get_text('hotkey_manager.warn.pid_clean_failed', e=e)}")