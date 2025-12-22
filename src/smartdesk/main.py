import sys
import os
import time  # Importiere time hier, falls es an anderer Stelle benötigt wird
import subprocess  # <--- NEU: Wird benötigt, um das Tray-Icon zu starten


# --- VENV AUTO-AKTIVIERUNG ---
def activate_venv_if_needed():
    """Aktiviert automatisch die venv, falls vorhanden und noch nicht aktiv."""
    # Prüfe, ob wir bereits in einer venv sind
    if hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ):
        return  # Bereits in venv

    # Finde das Projekt-Root (2 Ebenen über main.py: main.py -> smartdesk -> src -> root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(script_dir)
    project_root = os.path.dirname(src_dir)

    # Suche nach .venv im Projekt-Root
    venv_path = os.path.join(project_root, '.venv')

    if os.path.exists(venv_path):
        # Finde den Python-Interpreter in der venv
        if sys.platform == 'win32':
            venv_python = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:
            venv_python = os.path.join(venv_path, 'bin', 'python')

        if os.path.exists(venv_python):
            # Starte das Skript neu mit dem venv-Python
            os.execv(venv_python, [venv_python] + sys.argv)


# Aktiviere venv, bevor irgendetwas anderes passiert
activate_venv_if_needed()

# --- PFAD-KONFIGURATION ---
# Finde das src-Verzeichnis für korrekte Imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.dirname(_script_dir)

# Füge src zum Pfad hinzu (für "from smartdesk.xxx import yyy")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# --- NEUER IMPORT für Lokalisierung ---
try:
    from smartdesk.shared.localization import get_text
    from smartdesk.shared.first_run import ensure_setup_complete
except ImportError:
    # Fallback, falls Import nicht funktioniert
    print(f"CRITICAL: localization.py nicht gefunden. sys.path: {sys.path}")

    def get_text(key, **kwargs):
        # Einfaches Ersetzen für die Dummy-Funktion
        text = key
        for k, v in kwargs.items():
            text = text.replace(f"{{{k}}}", str(v))
        return text

    def ensure_setup_complete():
        return True


# Importiere UI Module
try:
    from smartdesk.core.services import desktop_service as desktop_handler
    from smartdesk.core.services import system_service as system_manager
    from smartdesk.shared.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN
    from smartdesk.hotkeys import listener as hotkey_listener

    # --- NEUE IMPORTS FÜR DIE STILLE GUI ---
    from smartdesk.interfaces.gui import ui_manager
    from contextlib import redirect_stdout, redirect_stderr
    import io

    # --- ENDE NEUE IMPORTS ---
except ImportError as e:
    try:
        # Fallback für andere Import-Strukturen (weniger wahrscheinlich)
        from core.services import desktop_service as desktop_handler
        from core.services import system_service as system_manager
    except ImportError:
        # --- LOKALISIERT ---
        print(get_text("main.error.import", e=e))
        print(get_text("main.error.import_hint_1"))
        print(get_text("main.error.import_hint_2"))
        sys.exit(1)

# --- FAKE HANDLER FÜR DEN FALL EINES FEHLERS ---
if 'desktop_handler' not in locals():
    # --- LOKALISIERT ---
    print(get_text("main.warn.handler_load_failed", handler="desktop_handler"))

    class FakeHandler:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                # --- LOKALISIERT ---
                print(get_text("main.error.handler_call_failed", name=name))

            return method

    desktop_handler = FakeHandler()
    system_manager = FakeHandler()


if __name__ == "__main__":

    # --- FIRST-RUN SETUP ---
    # Prüfe ob erster Start und führe Setup durch
    ensure_setup_complete()

    args = sys.argv[1:]

    # --- BEFEHLS-LOGIK ---
    # Wenn keine Argumente übergeben werden, starte das Tray-Icon.
    # Ansonsten, verarbeite das übergebene Kommando.
    command = args[0].lower() if args else "start-tray"

    # --- BEFEHL: create-gui (Von Tray Icon aufgerufen) ---
    if command == "create-gui":
        # (Diese Sektion gibt absichtlich nichts aus, da sie still im Hintergrund läuft)
        # 1. Starte den GUI-Dialog
        result_data = ui_manager.launch_create_desktop_dialog()

        # 2. Prüfen, ob der Benutzer "Abbrechen" geklickt hat
        if result_data is None:
            pass  # Einfach still beenden
        else:
            # 3. Daten extrahieren
            name = result_data["name"]
            path = result_data["path"]
            create_if_missing = result_data["create_if_missing"]

            # 4. Den Desktop-Handler "still" aufrufen (ohne Konsolenausgabe)
            f_stdout = io.StringIO()
            f_stderr = io.StringIO()
            with redirect_stdout(f_stdout), redirect_stderr(f_stderr):
                try:
                    desktop_handler.create_desktop(name, path, create_if_missing)
                except Exception:
                    # Fehler werden still ignoriert, wenn sie von der GUI kommen
                    pass

    # --- BEFEHL: start-listener ---
    elif command == "start-listener":
        # Dieser Befehl wird vom hotkey_manager als separater Prozess aufgerufen
        import os
        from smartdesk.shared.config import DATA_DIR

        # Schreibe die eigene PID in die Datei
        pid_file = os.path.join(DATA_DIR, "listener.pid")
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))

        print(get_text("main.info.starting_listener"))
        print(f"Listener-PID: {os.getpid()}")
        hotkey_listener.start_listener()

    # --- BEFEHL: stop-listener ---
    elif command == "stop-listener":
        from smartdesk.hotkeys import hotkey_manager
        hotkey_manager.stop_listener()

    # --- BEFEHL: start-tray ---
    elif command == "start-tray":
        """
        Startet das Tray-Icon in einem separaten, fensterlosen Prozess.
        """
        print(get_text("main.info.starting_tray"))
        try:
            from smartdesk.core.utils.registry_operations import is_process_running, get_tray_pid
            existing_pid = get_tray_pid()
            if existing_pid and is_process_running(existing_pid):
                print(f"{PREFIX_WARN} {get_text('main.warn.tray_already_running', pid=existing_pid)}")
                sys.exit(0)

            smartdesk_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(smartdesk_dir)
            project_root = os.path.dirname(src_dir)
            tray_icon_path = os.path.join(smartdesk_dir, 'interfaces', 'tray', 'tray_icon.py')

            if not os.path.exists(tray_icon_path):
                print(f"{PREFIX_ERROR} {get_text('main.error.tray_not_found', path=tray_icon_path)}")
                sys.exit(1)

            pythonw_executable = sys.executable.replace("python.exe", "pythonw.exe")
            process = subprocess.Popen(
                [pythonw_executable, tray_icon_path],
                cwd=project_root,
                creationflags=(subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0),
            )

            from smartdesk.core.utils.registry_operations import save_tray_pid
            save_tray_pid(process.pid)

            print(f"{PREFIX_OK} {get_text('main.success.tray_started')}")

        except Exception as e:
            print(f"{PREFIX_ERROR} {get_text('main.error.tray_failed', e=e)}")

    # --- UNBEKANNTER BEFEHL (sollte nur bei interner, falscher Verwendung auftreten) ---
    else:
        print(f"{PREFIX_ERROR} Internal error: Unknown command '{command}' passed to main.py.")
