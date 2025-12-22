# Dateipfad: src/smartdesk/interfaces/tray/tray_manager.py

import os
import sys
import subprocess
import time

TRAY_START_VALIDATION_DELAY = 0.5


def start_tray():
    """Startet das Tray-Icon in einem separaten, fensterlosen Prozess."""
    try:
        from ...core.utils.registry_operations import (
            is_process_running,
            get_tray_pid,
            save_tray_pid,
            cleanup_tray_pid,
        )
        from ...shared.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN
        from ...shared.localization import get_text

        existing_pid = get_tray_pid()
        if existing_pid and is_process_running(existing_pid):
            msg = get_text('main.warn.tray_already_running', pid=existing_pid)
            print(f"{PREFIX_WARN} {msg}")
            return False
        elif existing_pid:
            cleanup_tray_pid()

        # Finde die relevanten Pfade
        interfaces_dir = os.path.dirname(os.path.abspath(__file__))
        smartdesk_dir = os.path.dirname(os.path.dirname(interfaces_dir))
        src_dir = os.path.dirname(smartdesk_dir)
        project_root = os.path.dirname(src_dir)

        # Baue den Pfad zu tray_icon.py
        tray_icon_path = os.path.join(interfaces_dir, 'tray_icon.py')

        if not os.path.exists(tray_icon_path):
            msg = get_text('main.error.tray_not_found', path=tray_icon_path)
            print(f"{PREFIX_ERROR} {msg}")
            return False

        # Finde den 'pythonw.exe' Interpreter (windowless)
        pythonw_executable = sys.executable.replace("python.exe", "pythonw.exe")

        # Starte das Tray-Icon als neuen Prozess
        process = subprocess.Popen(
            [pythonw_executable, tray_icon_path],
            cwd=project_root,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

        save_tray_pid(process.pid)

        # Validierung nach dem Start
        time.sleep(TRAY_START_VALIDATION_DELAY)
        if not is_process_running(process.pid):
            msg = get_text(
                'main.error.tray_failed', e='Prozess wurde nach Start beendet'
            )
            print(f"{PREFIX_ERROR} {msg}")
            cleanup_tray_pid()
            return False

        msg = get_text('main.success.tray_started')
        print(f"{PREFIX_OK} {msg}")
        return True

    except Exception as e:
        from ...shared.style import PREFIX_ERROR
        from ...shared.localization import get_text

        msg = get_text('main.error.tray_failed', e=e)
        print(f"{PREFIX_ERROR} {msg}")
        return False


def stop_tray():
    """Stoppt das laufende Tray-Icon."""
    try:
        from ...core.utils.registry_operations import (
            is_process_running,
            get_tray_pid,
            cleanup_tray_pid,
        )
        from ...shared.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN
        from ...shared.localization import get_text
        import psutil

        pid = get_tray_pid()

        if not pid:
            msg = get_text('tray_manager.warn.not_running')
            print(f"{PREFIX_WARN} {msg}")
            return False

        if not is_process_running(pid):
            msg = get_text('tray_manager.warn.pid_not_found', pid=pid)
            print(f"{PREFIX_WARN} {msg}")
            cleanup_tray_pid()
            return False

        process = psutil.Process(pid)
        process.terminate()

        try:
            process.wait(timeout=3)
        except psutil.TimeoutExpired:
            process.kill()

        cleanup_tray_pid()

        msg = get_text('tray_manager.success.stopped')
        print(f"{PREFIX_OK} {msg}")
        return True

    except Exception as e:
        from ...shared.style import PREFIX_ERROR
        from ...shared.localization import get_text

        msg = get_text('tray_manager.error.stop_failed', e=e)
        print(f"{PREFIX_ERROR} {msg}")
        return False


def get_tray_status():
    """Gibt zurück, ob das Tray-Icon läuft und die PID."""
    try:
        from ...core.utils.registry_operations import (
            is_process_running,
            get_tray_pid,
            cleanup_tray_pid,
        )

        pid = get_tray_pid()
        if pid:
            if is_process_running(pid):
                return True, pid
            else:
                cleanup_tray_pid()
        return False, None
    except Exception:
        return False, None
