# Dateipfad: src/smartdesk/hotkeys/implementations.py
"""
Konkrete Implementierungen der Hotkey-Manager Interfaces.

Diese Datei enthält:
- PsutilProcessController: Prozessverwaltung via psutil
- FilePidStorage: PID-Speicherung in Datei
- SubprocessStarter: Prozess-Start via subprocess

Jede Klasse implementiert ein Interface aus interfaces.py.
"""

import os
import subprocess
from typing import Optional, List

from .interfaces import ProcessResult, ProcessState, StartResult

# Logging
try:
    from ..shared.logging_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class PsutilProcessController:
    """
    Prozess-Controller basierend auf psutil.

    Implementiert ProcessController Protocol für robuste
    Prozessverwaltung auf Windows, Linux und macOS.
    """

    def __init__(self):
        """Initialisiert den Controller und prüft psutil-Verfügbarkeit."""
        try:
            import psutil

            self._psutil = psutil
        except ImportError:
            logger.error("psutil ist nicht installiert")
            raise ImportError(
                "psutil wird für die Prozessverwaltung benötigt. "
                "Installiere es mit: pip install psutil"
            )

    def exists(self, pid: int) -> bool:
        """Prüft, ob ein Prozess existiert."""
        return self._psutil.pid_exists(pid)

    def is_running(self, pid: int) -> bool:
        """Prüft, ob ein Prozess aktiv läuft."""
        if not self.exists(pid):
            return False

        try:
            process = self._psutil.Process(pid)
            return process.is_running()
        except self._psutil.NoSuchProcess:
            return False
        except self._psutil.AccessDenied:
            # Prozess existiert, aber wir haben keinen Zugriff
            return True

    def terminate(self, pid: int, timeout: float = 3.0) -> ProcessResult:
        """
        Beendet einen Prozess sanft mit SIGTERM.

        Wartet bis zu 'timeout' Sekunden auf Beendigung.
        """
        if not self.exists(pid):
            return ProcessResult(
                success=False,
                state=ProcessState.NOT_FOUND,
                message="process_not_found",
                pid=pid,
            )

        try:
            process = self._psutil.Process(pid)
            process.terminate()

            try:
                process.wait(timeout=timeout)
                logger.info(f"Prozess {pid} erfolgreich beendet")
                return ProcessResult(
                    success=True,
                    state=ProcessState.TERMINATED,
                    message="terminated",
                    pid=pid,
                )
            except self._psutil.TimeoutExpired:
                logger.warning(f"Prozess {pid} reagiert nicht auf terminate")
                return ProcessResult(
                    success=False,
                    state=ProcessState.RUNNING,
                    message="timeout_expired",
                    pid=pid,
                )

        except self._psutil.NoSuchProcess:
            return ProcessResult(
                success=False,
                state=ProcessState.NOT_FOUND,
                message="process_not_found",
                pid=pid,
            )
        except self._psutil.AccessDenied as e:
            logger.error(f"Zugriff auf Prozess {pid} verweigert")
            return ProcessResult(
                success=False,
                state=ProcessState.ACCESS_DENIED,
                message="access_denied",
                pid=pid,
                error=e,
            )
        except Exception as e:
            logger.exception(f"Fehler beim Beenden von Prozess {pid}")
            return ProcessResult(
                success=False,
                state=ProcessState.ERROR,
                message="terminate_error",
                pid=pid,
                error=e,
            )

    def kill(self, pid: int) -> ProcessResult:
        """Beendet einen Prozess erzwungen mit SIGKILL."""
        if not self.exists(pid):
            return ProcessResult(
                success=False,
                state=ProcessState.NOT_FOUND,
                message="process_not_found",
                pid=pid,
            )

        try:
            process = self._psutil.Process(pid)
            process.kill()
            process.wait(timeout=3.0)

            logger.info(f"Prozess {pid} erzwungen beendet (kill)")
            return ProcessResult(
                success=True, state=ProcessState.KILLED, message="killed", pid=pid
            )

        except self._psutil.NoSuchProcess:
            return ProcessResult(
                success=False,
                state=ProcessState.NOT_FOUND,
                message="process_not_found",
                pid=pid,
            )
        except self._psutil.AccessDenied as e:
            logger.error(f"Zugriff auf Prozess {pid} verweigert")
            return ProcessResult(
                success=False,
                state=ProcessState.ACCESS_DENIED,
                message="access_denied",
                pid=pid,
                error=e,
            )
        except Exception as e:
            logger.exception(f"Fehler beim Kill von Prozess {pid}")
            return ProcessResult(
                success=False,
                state=ProcessState.ERROR,
                message="kill_error",
                pid=pid,
                error=e,
            )


class FilePidStorage:
    """
    Dateibasierte PID-Speicherung.

    Implementiert PidStorage Protocol für persistente
    Speicherung der Listener-PID.
    """

    def __init__(self, filepath: str):
        """
        Initialisiert den Storage mit dem Dateipfad.

        Args:
            filepath: Absoluter Pfad zur PID-Datei
        """
        self._filepath = filepath
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Stellt sicher, dass das Verzeichnis existiert."""
        directory = os.path.dirname(self._filepath)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                logger.warning(f"Konnte Verzeichnis nicht erstellen: {e}")

    def read(self) -> Optional[int]:
        """Liest die gespeicherte PID."""
        if not self.exists():
            return None

        try:
            with open(self._filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return None
                pid = int(content)
                logger.debug(f"PID {pid} aus {self._filepath} gelesen")
                return pid
        except ValueError as e:
            logger.warning(f"Ungültige PID in Datei: {e}")
            self.delete()  # Lösche korrupte Datei
            return None
        except IOError as e:
            logger.error(f"Fehler beim Lesen der PID-Datei: {e}")
            return None

    def write(self, pid: int) -> bool:
        """Speichert eine PID."""
        try:
            with open(self._filepath, 'w', encoding='utf-8') as f:
                f.write(str(pid))
            logger.debug(f"PID {pid} in {self._filepath} geschrieben")
            return True
        except IOError as e:
            logger.error(f"Fehler beim Schreiben der PID-Datei: {e}")
            return False

    def delete(self) -> bool:
        """Löscht die PID-Datei."""
        if not self.exists():
            return True

        try:
            os.remove(self._filepath)
            logger.debug(f"PID-Datei {self._filepath} gelöscht")
            return True
        except OSError as e:
            logger.warning(f"Fehler beim Löschen der PID-Datei: {e}")
            return False

    def exists(self) -> bool:
        """Prüft, ob die PID-Datei existiert."""
        return os.path.isfile(self._filepath)


class SubprocessStarter:
    """
    Prozess-Starter via subprocess.

    Implementiert ProcessStarter Protocol für das Starten
    von Hintergrundprozessen.
    """

    def __init__(self, hide_window: bool = True):
        """
        Initialisiert den Starter.

        Args:
            hide_window: Ob das Konsolenfenster versteckt werden soll (Windows)
        """
        self._hide_window = hide_window

    def start(
        self,
        command: List[str],
        working_dir: str,
        log_file: Optional[str] = None,
        error_file: Optional[str] = None,
    ) -> StartResult:
        """Startet einen neuen Prozess."""

        # Validierung
        if not command:
            return StartResult(
                success=False,
                message="empty_command",
                error=ValueError("Befehl darf nicht leer sein"),
            )

        executable = command[0]
        if not os.path.exists(executable):
            return StartResult(
                success=False,
                message="executable_not_found",
                error=FileNotFoundError(
                    f"Ausführbare Datei nicht gefunden: {executable}"
                ),
            )

        try:
            # Plattform-spezifische Flags
            creation_flags = 0
            if os.name == 'nt' and self._hide_window:
                creation_flags = subprocess.CREATE_NO_WINDOW

            # Umgebungsvariablen - PYTHONPATH für Modul-Auflösung
            env = os.environ.copy()
            # Füge src-Verzeichnis zum PYTHONPATH hinzu
            src_dir = os.path.join(working_dir, 'src')
            if os.path.isdir(src_dir):
                current_pythonpath = env.get('PYTHONPATH', '')
                if current_pythonpath:
                    env['PYTHONPATH'] = f"{src_dir};{current_pythonpath}"
                else:
                    env['PYTHONPATH'] = src_dir

            # Log-Dateien öffnen
            stdout_handle = subprocess.DEVNULL
            stderr_handle = subprocess.DEVNULL
            log_f = None
            err_f = None

            if log_file:
                log_f = open(log_file, 'a', buffering=1, encoding='utf-8')
                stdout_handle = log_f

            if error_file:
                err_f = open(error_file, 'a', buffering=1, encoding='utf-8')
                stderr_handle = err_f

            # Prozess starten
            process = subprocess.Popen(
                command,
                cwd=working_dir,
                env=env,
                stdout=stdout_handle,
                stderr=stderr_handle,
                stdin=subprocess.DEVNULL,
                creationflags=creation_flags,
                close_fds=(os.name != 'nt'),  # close_fds=False auf Windows
            )

            logger.info(f"Prozess gestartet mit PID {process.pid}")
            return StartResult(success=True, pid=process.pid, message="started")

        except FileNotFoundError as e:
            logger.error(f"Ausführbare Datei nicht gefunden: {e}")
            return StartResult(success=False, message="executable_not_found", error=e)
        except PermissionError as e:
            logger.error(f"Keine Berechtigung zum Starten: {e}")
            return StartResult(success=False, message="permission_denied", error=e)
        except Exception as e:
            logger.exception("Unerwarteter Fehler beim Starten des Prozesses")
            return StartResult(success=False, message="start_error", error=e)
