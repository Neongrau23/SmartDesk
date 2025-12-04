# Dateipfad: src/smartdesk/hotkeys/listener_manager.py
"""
Zentraler Manager für den Hotkey-Listener.

Diese Klasse implementiert die gesamte Geschäftslogik für:
- Starten des Listeners
- Stoppen des Listeners
- Statusabfragen

Durch Dependency Injection ist diese Klasse vollständig testbar.
"""

import os
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Callable

from .interfaces import ProcessController, PidStorage, ProcessStarter, ProcessState

# Logging
try:
    from ..shared.logging_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class ListenerStatus(Enum):
    """Status des Listeners."""

    RUNNING = auto()
    STOPPED = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class ManagerResult:
    """
    Ergebnis einer Manager-Operation.

    Attributes:
        success: Ob die Operation erfolgreich war
        message: Beschreibende Nachricht (i18n-Key)
        pid: Betroffene PID (falls relevant)
        forced: Ob ein Force-Kill nötig war
        error: Optionale Exception
    """

    success: bool
    message: str
    pid: Optional[int] = None
    forced: bool = False
    error: Optional[Exception] = None


class ListenerManager:
    """
    Verwaltet den Lebenszyklus des Hotkey-Listeners.

    Diese Klasse folgt dem Dependency Injection Prinzip:
    Alle externen Abhängigkeiten werden im Konstruktor übergeben.

    Beispiel:
        from smartdesk.hotkeys.implementations import (
            PsutilProcessController,
            FilePidStorage,
            SubprocessStarter
        )

        manager = ListenerManager(
            controller=PsutilProcessController(),
            storage=FilePidStorage("/path/to/pid"),
            starter=SubprocessStarter()
        )

        result = manager.start()
        if result.success:
            print(f"Listener gestartet mit PID {result.pid}")
    """

    def __init__(
        self,
        controller: ProcessController,
        storage: PidStorage,
        starter: ProcessStarter,
        command: List[str],
        working_dir: str,
        log_file: Optional[str] = None,
        error_file: Optional[str] = None,
        terminate_timeout: float = 3.0,
    ):
        """
        Initialisiert den Manager.

        Args:
            controller: Prozess-Controller für Start/Stop
            storage: PID-Storage für Persistierung
            starter: Prozess-Starter
            command: Befehl zum Starten des Listeners
            working_dir: Arbeitsverzeichnis
            log_file: Optionaler Pfad für stdout
            error_file: Optionaler Pfad für stderr
            terminate_timeout: Timeout für graceful shutdown
        """
        self._controller = controller
        self._storage = storage
        self._starter = starter
        self._command = command
        self._working_dir = working_dir
        self._log_file = log_file
        self._error_file = error_file
        self._terminate_timeout = terminate_timeout

        # Event-Callbacks (Observer Pattern)
        self._on_start_callbacks: List[Callable[[int], None]] = []
        self._on_stop_callbacks: List[Callable[[int], None]] = []

    # -------------------------------------------------------------------------
    # Event Registration (Observer Pattern)
    # -------------------------------------------------------------------------

    def on_start(self, callback: Callable[[int], None]) -> None:
        """
        Registriert einen Callback für Listener-Start.

        Args:
            callback: Funktion die mit der PID aufgerufen wird
        """
        self._on_start_callbacks.append(callback)

    def on_stop(self, callback: Callable[[int], None]) -> None:
        """
        Registriert einen Callback für Listener-Stop.

        Args:
            callback: Funktion die mit der PID aufgerufen wird
        """
        self._on_stop_callbacks.append(callback)

    def _notify_start(self, pid: int) -> None:
        """Benachrichtigt alle Start-Listener."""
        for callback in self._on_start_callbacks:
            try:
                callback(pid)
            except Exception as e:
                logger.warning(f"Error in start callback: {e}")

    def _notify_stop(self, pid: int) -> None:
        """Benachrichtigt alle Stop-Listener."""
        for callback in self._on_stop_callbacks:
            try:
                callback(pid)
            except Exception as e:
                logger.warning(f"Error in stop callback: {e}")

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    def get_status(self) -> ListenerStatus:
        """
        Ermittelt den aktuellen Status des Listeners.

        Returns:
            ListenerStatus.RUNNING wenn der Listener läuft
            ListenerStatus.STOPPED wenn kein Listener läuft
            ListenerStatus.UNKNOWN bei Fehlern
        """
        pid = self._storage.read()
        if pid is None:
            return ListenerStatus.STOPPED

        try:
            if self._controller.is_running(pid):
                return ListenerStatus.RUNNING
            else:
                # Verwaiste PID-Datei aufräumen
                self._storage.delete()
                return ListenerStatus.STOPPED
        except Exception as e:
            logger.warning(f"Konnte Status nicht ermitteln: {e}")
            return ListenerStatus.UNKNOWN

    def is_running(self) -> bool:
        """Prüft, ob der Listener läuft."""
        return self.get_status() == ListenerStatus.RUNNING

    def get_pid(self) -> Optional[int]:
        """Gibt die PID des laufenden Listeners zurück."""
        pid = self._storage.read()
        if pid and self._controller.is_running(pid):
            return pid
        return None

    # -------------------------------------------------------------------------
    # Start
    # -------------------------------------------------------------------------

    def start(self) -> ManagerResult:
        """
        Startet den Hotkey-Listener.

        Returns:
            ManagerResult mit Erfolg/Misserfolg und Details
        """
        # Prüfe ob bereits läuft
        if self.is_running():
            pid = self._storage.read()
            logger.warning(f"Listener läuft bereits mit PID {pid}")
            return ManagerResult(success=False, message="already_running", pid=pid)

        # Validiere Command
        if not self._command:
            return ManagerResult(
                success=False,
                message="empty_command",
                error=ValueError("Kein Befehl konfiguriert"),
            )

        executable = self._command[0]
        if not os.path.exists(executable):
            logger.error(f"Python-Executable nicht gefunden: {executable}")
            return ManagerResult(
                success=False,
                message="python_not_found",
                error=FileNotFoundError(executable),
            )

        # Starte den Prozess
        logger.info("Starte Hotkey-Listener...")
        result = self._starter.start(
            command=self._command,
            working_dir=self._working_dir,
            log_file=self._log_file,
            error_file=self._error_file,
        )

        if not result.success:
            logger.error(f"Start fehlgeschlagen: {result.message}")
            return ManagerResult(
                success=False, message=result.message, error=result.error
            )

        # PID speichern
        if result.pid:
            if not self._storage.write(result.pid):
                logger.warning("PID konnte nicht gespeichert werden")

            self._notify_start(result.pid)
            logger.info(f"Listener gestartet mit PID {result.pid}")

        return ManagerResult(success=True, message="started", pid=result.pid)

    # -------------------------------------------------------------------------
    # Stop
    # -------------------------------------------------------------------------

    def stop(self) -> ManagerResult:
        """
        Stoppt den Hotkey-Listener.

        Versucht zuerst ein sanftes Beenden (SIGTERM).
        Falls das nicht funktioniert, wird SIGKILL verwendet.

        Returns:
            ManagerResult mit Erfolg/Misserfolg und Details
        """
        pid = self._storage.read()

        if pid is None:
            logger.info("Kein Listener läuft (keine PID)")
            return ManagerResult(success=False, message="not_running")

        # Prüfe ob Prozess existiert
        if not self._controller.exists(pid):
            logger.warning(f"Prozess {pid} existiert nicht mehr")
            self._storage.delete()
            return ManagerResult(success=False, message="process_not_found", pid=pid)

        # Versuche sanftes Beenden
        logger.info(f"Beende Listener (PID {pid})...")
        result = self._controller.terminate(pid, self._terminate_timeout)

        if result.success:
            self._storage.delete()
            self._notify_stop(pid)
            return ManagerResult(
                success=True, message="terminated", pid=pid, forced=False
            )

        # Sanftes Beenden fehlgeschlagen
        if result.state == ProcessState.ACCESS_DENIED:
            return ManagerResult(
                success=False, message="access_denied", pid=pid, error=result.error
            )

        # Force Kill
        logger.warning("Sanftes Beenden fehlgeschlagen, erzwinge Kill...")
        kill_result = self._controller.kill(pid)

        if kill_result.success:
            self._storage.delete()
            self._notify_stop(pid)
            return ManagerResult(success=True, message="killed", pid=pid, forced=True)

        # Auch Kill fehlgeschlagen
        logger.error(f"Konnte Prozess {pid} nicht beenden")
        return ManagerResult(
            success=False, message="stop_failed", pid=pid, error=kill_result.error
        )

    # -------------------------------------------------------------------------
    # Restart
    # -------------------------------------------------------------------------

    def restart(self) -> ManagerResult:
        """
        Startet den Listener neu.

        Returns:
            ManagerResult mit Erfolg/Misserfolg
        """
        logger.info("Neustart des Listeners...")

        # Stop (ignoriere Fehler wenn nicht läuft)
        if self.is_running():
            stop_result = self.stop()
            if not stop_result.success and stop_result.message != "not_running":
                return stop_result

        # Start
        return self.start()
