# Dateipfad: src/smartdesk/ui/tray/tray_manager.py

import os
import sys
import subprocess
import time
import psutil
from typing import Optional, Tuple

# Interne Importe
try:
    from ...core.utils.registry_operations import (
        is_process_running,
        get_tray_pid,
        save_tray_pid,
        cleanup_tray_pid,
    )
    from ...shared.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN
    from ...shared.localization import get_text
except ImportError:
    # Fallback für isolierte Tests
    def get_text(key, **kwargs): return key
    PREFIX_OK = "[OK]"
    PREFIX_WARN = "[WARN]"
    PREFIX_ERROR = "[ERR]"
    
    def is_process_running(pid): return False
    def get_tray_pid(): return None
    def save_tray_pid(pid): pass
    def cleanup_tray_pid(): pass


TRAY_START_VALIDATION_DELAY = 0.5


class TrayManager:
    """
    Verwaltet den Lebenszyklus des System-Tray-Icons als separaten Prozess.
    """

    @staticmethod
    def start() -> bool:
        """
        Startet das Tray-Icon in einem separaten, fensterlosen Prozess.
        
        Returns:
            True wenn erfolgreich gestartet, sonst False.
        """
        try:
            existing_pid = get_tray_pid()
            if existing_pid and is_process_running(existing_pid):
                msg = get_text('main.warn.tray_already_running', pid=existing_pid)
                print(f"{PREFIX_WARN} {msg}")
                return False
            elif existing_pid:
                cleanup_tray_pid()

            # Finde die relevanten Pfade
            # Wir sind in src/smartdesk/ui/tray/tray_manager.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # tray_icon.py liegt im selben Ordner
            tray_icon_path = os.path.join(current_dir, 'tray_icon.py')
            
            # Projekt-Root finden (3 Ebenen hoch: tray -> ui -> smartdesk -> src -> root)
            # src/smartdesk/ui/tray -> src/smartdesk/ui -> src/smartdesk -> src -> root
            # Aber wir wollen das Root-Verzeichnis, wo main.py liegt? 
            # Normalerweise wird cwd auf Project-Root gesetzt.
            # Gehen wir sicher:
            src_smartdesk_ui_tray = current_dir
            src_smartdesk_ui = os.path.dirname(src_smartdesk_ui_tray)
            src_smartdesk = os.path.dirname(src_smartdesk_ui)
            src_dir = os.path.dirname(src_smartdesk)
            project_root = os.path.dirname(src_dir)

            if not os.path.exists(tray_icon_path):
                msg = get_text('main.error.tray_not_found', path=tray_icon_path)
                print(f"{PREFIX_ERROR} {msg}")
                return False

            # Finde den 'pythonw.exe' Interpreter (windowless)
            pythonw_executable = sys.executable.replace("python.exe", "pythonw.exe")
            if not os.path.exists(pythonw_executable):
                # Fallback auf python.exe wenn pythonw.exe nicht da ist (z.B. venv)
                pythonw_executable = sys.executable

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
            msg = get_text('main.error.tray_failed', e=e)
            print(f"{PREFIX_ERROR} {msg}")
            return False

    @staticmethod
    def stop() -> bool:
        """
        Stoppt das laufende Tray-Icon.
        
        Returns:
            True wenn erfolgreich gestoppt, sonst False.
        """
        try:
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

            try:
                process = psutil.Process(pid)
                process.terminate()

                try:
                    process.wait(timeout=3)
                except psutil.TimeoutExpired:
                    process.kill()
            except psutil.NoSuchProcess:
                # Prozess ist schon weg
                pass

            cleanup_tray_pid()

            msg = get_text('tray_manager.success.stopped')
            print(f"{PREFIX_OK} {msg}")
            return True

        except Exception as e:
            msg = get_text('tray_manager.error.stop_failed', e=e)
            print(f"{PREFIX_ERROR} {msg}")
            return False

    @staticmethod
    def get_status() -> Tuple[bool, Optional[int]]:
        """
        Gibt zurück, ob das Tray-Icon läuft und die PID.
        
        Returns:
            (is_running, pid)
        """
        try:
            pid = get_tray_pid()
            if pid:
                if is_process_running(pid):
                    return True, pid
                else:
                    cleanup_tray_pid()
            return False, None
        except Exception:
            return False, None


# --- Wrapper-Funktionen für Rückwärtskompatibilität ---

def start_tray() -> bool:
    return TrayManager.start()

def stop_tray() -> bool:
    return TrayManager.stop()

def get_tray_status() -> Tuple[bool, Optional[int]]:
    return TrayManager.get_status()