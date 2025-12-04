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
    from smartdesk.interfaces.cli import cli
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
        from interfaces.cli import cli
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

    # --- KEINE ARGUMENTE: Interaktives Menü ---
    if not args:
        # --- LOKALISIERT ---
        print(get_text("main.info.starting_interactive"))
        cli.run()

    # --- ARGUMENTE VORHANDEN: Befehl parsen ---
    else:
        command = args[0].lower()

        # --- BEFEHL: delete ---
        if command == "delete":
            if len(args) < 2:
                # --- LOKALISIERT ---
                print(f"{PREFIX_ERROR} {get_text('main.error.name_missing')}")
                print(get_text("main.usage.delete"))
            else:
                name = args[1]
                delete_folder = "--delete-folder" in args or "-f" in args

                # Handler gibt lokalisierte Meldungen aus
                desktop_handler.delete_desktop(name, delete_folder)

        # --- BEFEHL: switch ---
        elif command == "switch":
            if len(args) < 2:
                # --- LOKALISIERT ---
                print(f"{PREFIX_ERROR} {get_text('main.error.name_missing')}")
                print(get_text("main.usage.switch"))
            else:
                name = args[1]
                # --- LOKALISIERT ---
                print(get_text("main.info.switching_to", name=name))

                if desktop_handler.switch_to_desktop(name):
                    # --- LOKALISIERT ---
                    print(get_text("main.info.restarting_explorer"))
                    system_manager.restart_explorer()
                    print(get_text("main.info.waiting_explorer"))
                    time.sleep(3)  # Wartezeit für Explorer

                    desktop_handler.sync_desktop_state_and_apply_icons()
                    print(f"{PREFIX_OK} {get_text('main.success.switch', name=name)}")

        # --- BEFEHL: list ---
        elif command == "list":
            desktops = desktop_handler.get_all_desktops()
            if not desktops:
                # --- LOKALISIERT ---
                print(get_text("ui.messages.no_desktops"))
            else:
                # --- LOKALISIERT ---
                print(get_text("main.info.list_header"))
                for d in desktops:
                    # --- LOKALISIERT ---
                    status = (
                        f"[{get_text('ui.status.active')}]"
                        if d.is_active
                        else f"[{get_text('ui.status.inactive')}]"
                    )
                    print(f"{status} {d.name} -> {d.path}")

        # --- BEFEHL: create (Text-Version) ---
        elif command == "create":
            print(get_text("main.info.starting_create_menu"))
            cli.run_create_desktop_menu()

        # --- KORRIGIERT: BEFEHL: create-gui (Von Tray Icon aufgerufen) ---
        elif command == "create-gui":
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
                # Wir leiten stdout/stderr um, damit `desktop_handler.create_desktop`
                # kein Terminal aufpoppen lässt.

                f_stdout = io.StringIO()
                f_stderr = io.StringIO()

                with redirect_stdout(f_stdout), redirect_stderr(f_stderr):
                    try:
                        # Diese Funktion macht `print()`-Ausgaben,
                        # die wir hier unterdrücken.
                        desktop_handler.create_desktop(name, path, create_if_missing)
                    except Exception:
                        # Fehler werden still ignoriert, wenn sie von der GUI kommen
                        pass
        # --- ENDE KORREKTUR ---

        # --- BEFEHL: start-listener ---
        elif command == "start-listener":
            # Dieser Befehl wird vom hotkey_manager als separater Prozess aufgerufen
            # Die PID-Datei wird vom Manager geschrieben
            import os
            from smartdesk.shared.config import DATA_DIR

            # Schreibe die eigene PID in die Datei (überschreibt die vom Elternprozess)
            pid_file = os.path.join(DATA_DIR, "listener.pid")
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))

            # --- LOKALISIERT ---
            print(get_text("main.info.starting_listener"))
            print(f"Listener-PID: {os.getpid()}")

            # Starte den blockierenden Listener
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
                # 0. Prüfe, ob Tray-Icon bereits läuft
                from smartdesk.core.utils.registry_operations import (
                    is_process_running,
                    get_tray_pid,
                )

                existing_pid = get_tray_pid()
                if existing_pid and is_process_running(existing_pid):
                    print(
                        f"{PREFIX_WARN} {get_text('main.warn.tray_already_running', pid=existing_pid)}"
                    )
                    sys.exit(0)

                # 1. Finde die relevanten Pfade
                smartdesk_dir = os.path.dirname(os.path.abspath(__file__))
                src_dir = os.path.dirname(smartdesk_dir)
                project_root = os.path.dirname(src_dir)

                # 2. Baue den Pfad zu tray_icon.py (jetzt in interfaces/tray)
                tray_icon_path = os.path.join(
                    smartdesk_dir, 'interfaces', 'tray', 'tray_icon.py'
                )

                if not os.path.exists(tray_icon_path):
                    print(
                        f"{PREFIX_ERROR} {get_text('main.error.tray_not_found', path=tray_icon_path)}"
                    )
                    sys.exit(1)

                # 3. Finde den 'pythonw.exe' Interpreter (windowless)
                pythonw_executable = sys.executable.replace("python.exe", "pythonw.exe")

                # 4. Starte das Tray-Icon als neuen, unabhängigen Prozess
                process = subprocess.Popen(
                    [pythonw_executable, tray_icon_path],
                    cwd=project_root,
                    creationflags=(
                        subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                    ),
                )

                # 5. Speichere die PID
                from smartdesk.core.utils.registry_operations import save_tray_pid

                save_tray_pid(process.pid)

                print(f"{PREFIX_OK} {get_text('main.success.tray_started')}")

            except Exception as e:
                print(f"{PREFIX_ERROR} {get_text('main.error.tray_failed', e=e)}")

        # --- UNBEKANNTER BEFEHL ---
        else:
            # --- LOKALISIERT ---
            print(
                f"{PREFIX_ERROR} {get_text('main.error.unknown_command', command=command)}"
            )
            print(get_text("main.info.available_commands"))
            print(get_text("main.info.hint_interactive"))
