# Dateipfad: src/smartdesk/handlers/hotkey_manager.py

"""
Dieser Manager steuert den Hotkey-Listener-Prozess.
Er kann ihn als separaten Prozess starten, stoppen und prüfen, ob er läuft.
"""

import os
import sys
import subprocess
import time
import psutil # WICHTIG: muss mit 'pip install psutil' installiert werden

try:
    from ..config import DATA_DIR
    from ..localization import get_text
    from ..ui.style import PREFIX_OK, PREFIX_ERROR, PREFIX_WARN
except ImportError:
    print("FEHLER: hotkey_manager.py konnte Config/Localization nicht laden.")
    # Fallbacks
    DATA_DIR = "."
    def get_text(key, **kwargs): return key
    PREFIX_OK = "OK:"
    PREFIX_ERROR = "FEHLER:"
    PREFIX_WARN = "WARNUNG:"

# Name der Datei, in der wir die Prozess-ID (PID) des Listeners speichern
PID_FILE = os.path.join(DATA_DIR, "listener.pid")

def get_listener_pid() -> int | None:
    """
    Prüft, ob der Listener läuft, indem die PID-Datei gelesen
    und verifiziert wird, ob der Prozess noch existiert.
    Gibt die PID zurück, wenn er läuft, sonst None.
    """
    if not os.path.exists(PID_FILE):
        return None
        
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
            
        # Prüfen, ob der Prozess mit dieser PID noch existiert
        if psutil.pid_exists(pid):
            # Optional: Prüfen, ob es auch der richtige Prozess ist
            # proc = psutil.Process(pid)
            # if "python" in proc.name().lower():
            #     return pid
            return pid # Für uns reicht die Existenz der PID
            
        # Prozess existiert nicht mehr, PID-Datei ist veraltet ("stale")
        os.remove(PID_FILE)
        return None
        
    except (IOError, ValueError, psutil.NoSuchProcess):
        # Fehler beim Lesen oder Prozess nicht gefunden
        try:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
        except OSError:
            pass # Kann nicht entfernt werden, ist aber auch ok
        return None

def start_listener():
    """
    Startet den Hotkey-Listener als separaten Hintergrundprozess.
    """
    # Prüfe ob bereits läuft
    pid = get_listener_pid()
    if pid:
        print(f"{PREFIX_WARN} {get_text('hotkey_manager.warn.already_running', pid=pid)}")
        return
    
    try:
        # WICHTIG: Verwende ein Log-File statt DEVNULL für Debugging
        log_file = os.path.join(DATA_DIR, "listener_subprocess.log")
        
        # Bestimme den src-Ordner (Parent von smartdesk)
        # __file__ ist in: src/smartdesk/hotkeys/hotkey_manager.py
        # Wir wollen: src/
        src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Erstelle eine Kopie der Umgebungsvariablen
        env = os.environ.copy()
        
        # Füge den src-Ordner zum PYTHONPATH hinzu
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{src_dir}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = src_dir
        
        with open(log_file, 'a', encoding='utf-8') as log_f:
            log_f.write(f"\n{'='*50}\n")
            log_f.write(f"Starte Listener-Prozess...\n")
            log_f.write(f"Python: {sys.executable}\n")
            log_f.write(f"PYTHONPATH: {env['PYTHONPATH']}\n")
            log_f.write(f"Working Dir: {os.getcwd()}\n")
            log_f.flush()
            
            # Starte Listener als separaten Prozess
            if sys.platform == 'win32':
                process = subprocess.Popen(
                    [sys.executable, "-m", "smartdesk.hotkeys.listener"],
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    stdout=log_f,
                    stderr=log_f,
                    stdin=subprocess.DEVNULL,
                    env=env
                )
            else:
                process = subprocess.Popen(
                    [sys.executable, "-m", "smartdesk.hotkeys.listener"],
                    stdout=log_f,
                    stderr=log_f,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    env=env
                )
        
        # Warte länger, damit der Prozess wirklich starten kann
        time.sleep(1.5)
        
        # Prüfe ob der Prozess noch läuft
        if not psutil.pid_exists(process.pid):
            print(f"{PREFIX_ERROR} Listener-Prozess ist sofort beendet. Prüfe {log_file}")
            return
        
        # Speichere PID
        pid_file = os.path.join(DATA_DIR, "listener.pid")
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        print(f"{PREFIX_OK} {get_text('hotkey_manager.info.started', pid=process.pid)}")
        
    except Exception as e:
        print(f"{PREFIX_ERROR} {get_text('hotkey_manager.error.start_failed', e=e)}")
        import traceback
        traceback.print_exc()