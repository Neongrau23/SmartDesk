# Dateipfad: src/smartdesk/handlers/tray_manager.py

import os
import sys
import subprocess


def start_tray():
    """Startet das Tray-Icon in einem separaten, fensterlosen Prozess."""
    try:
        from ..utils.registry_operations import (
            is_process_running,
            get_tray_pid,
            save_tray_pid
        )
        from ..ui.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN
        from ..localization import get_text
        
        # 0. Prüfe, ob Tray-Icon bereits läuft
        existing_pid = get_tray_pid()
        if existing_pid and is_process_running(existing_pid):
            print(f"{PREFIX_WARN} {get_text('main.warn.tray_already_running', pid=existing_pid)}")
            return False
        
        # 1. Finde die relevanten Pfade
        smartdesk_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        handlers_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.dirname(smartdesk_dir)
        project_root = os.path.dirname(src_dir)

        # 2. Baue den Pfad zu tray_icon.py (jetzt in handlers)
        tray_icon_path = os.path.join(handlers_dir, 'tray_icon.py')
        
        if not os.path.exists(tray_icon_path):
            print(f"{PREFIX_ERROR} {get_text('main.error.tray_not_found', path=tray_icon_path)}")
            return False

        # 3. Finde den 'pythonw.exe' Interpreter (windowless)
        pythonw_executable = sys.executable.replace("python.exe", "pythonw.exe")
        
        # 4. Starte das Tray-Icon als neuen, unabhängigen Prozess
        process = subprocess.Popen(
            [pythonw_executable, tray_icon_path],
            cwd=project_root,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # 5. Speichere die PID
        save_tray_pid(process.pid)
        
        print(f"{PREFIX_OK} {get_text('main.success.tray_started')}")
        return True
        
    except Exception as e:
        from ..ui.style import PREFIX_ERROR
        from ..localization import get_text
        print(f"{PREFIX_ERROR} {get_text('main.error.tray_failed', e=e)}")
        return False


def stop_tray():
    """Stoppt das laufende Tray-Icon."""
    try:
        from ..utils.registry_operations import (
            is_process_running,
            get_tray_pid,
            cleanup_tray_pid
        )
        from ..ui.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN
        from ..localization import get_text
        import psutil
        
        pid = get_tray_pid()
        
        if not pid:
            print(f"{PREFIX_WARN} {get_text('tray_manager.warn.not_running')}")
            return False
        
        if not is_process_running(pid):
            print(f"{PREFIX_WARN} {get_text('tray_manager.warn.pid_not_found', pid=pid)}")
            cleanup_tray_pid()
            return False
        
        # Beende den Prozess
        process = psutil.Process(pid)
        process.terminate()
        
        # Warte kurz, ob der Prozess beendet wird
        try:
            process.wait(timeout=3)
        except psutil.TimeoutExpired:
            # Force kill, falls der Prozess nicht terminiert
            process.kill()
        
        # Bereinige die PID
        cleanup_tray_pid()
        
        print(f"{PREFIX_OK} {get_text('tray_manager.success.stopped')}")
        return True
        
    except Exception as e:
        from ..ui.style import PREFIX_ERROR
        from ..localization import get_text
        print(f"{PREFIX_ERROR} {get_text('tray_manager.error.stop_failed', e=e)}")
        return False


def get_tray_status():
    """Gibt zurück, ob das Tray-Icon läuft und die PID."""
    try:
        from ..utils.registry_operations import is_process_running, get_tray_pid
        
        pid = get_tray_pid()
        if pid and is_process_running(pid):
            return True, pid
        return False, None
    except Exception:
        return False, None
