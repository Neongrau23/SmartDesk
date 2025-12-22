# Dateipfad: src/smartdesk/hotkeys/interfaces.py
"""
Interfaces (Protocols) für den Hotkey-Manager.

Diese Datei definiert die Schnittstellen für:
- Prozessverwaltung (ProcessController)
- PID-Speicherung (PidStorage)
- Prozess-Starter (ProcessStarter)

Durch die Verwendung von Protocols können wir:
1. Dependency Injection implementieren
2. Komponenten einfach mocken für Tests
3. Implementierungen austauschen ohne Core-Logik zu ändern
"""

from typing import Protocol, Optional, List
from dataclasses import dataclass
from enum import Enum, auto


class ProcessState(Enum):
    """Mögliche Zustände eines Prozesses."""

    RUNNING = auto()
    NOT_FOUND = auto()
    TERMINATED = auto()
    KILLED = auto()
    ACCESS_DENIED = auto()
    ERROR = auto()


@dataclass(frozen=True)
class ProcessResult:
    """
    Ergebnis einer Prozess-Operation.

    Attributes:
        success: Ob die Operation erfolgreich war
        state: Der resultierende Prozess-Zustand
        message: Beschreibende Nachricht (i18n-Key oder Text)
        pid: Die betroffene PID (falls relevant)
        error: Optionale Exception bei Fehlern
    """

    success: bool
    state: ProcessState
    message: str
    pid: Optional[int] = None
    error: Optional[Exception] = None


@dataclass(frozen=True)
class StartResult:
    """
    Ergebnis eines Prozess-Starts.

    Attributes:
        success: Ob der Start erfolgreich war
        pid: Die PID des gestarteten Prozesses
        message: Beschreibende Nachricht
        error: Optionale Exception bei Fehlern
    """

    success: bool
    pid: Optional[int] = None
    message: str = ""
    error: Optional[Exception] = None


class ProcessController(Protocol):
    """
    Interface für Prozess-Kontrolle.

    Ermöglicht das Prüfen, Beenden und Killen von Prozessen.
    Implementierung kann psutil, Windows-API oder Mock sein.
    """

    def exists(self, pid: int) -> bool:
        """
        Prüft, ob ein Prozess mit der gegebenen PID existiert.

        Args:
            pid: Die zu prüfende Prozess-ID

        Returns:
            True wenn der Prozess existiert, sonst False
        """
        ...

    def is_running(self, pid: int) -> bool:
        """
        Prüft, ob ein Prozess aktiv läuft (nicht nur existiert).

        Args:
            pid: Die zu prüfende Prozess-ID

        Returns:
            True wenn der Prozess läuft, sonst False
        """
        ...

    def terminate(self, pid: int, timeout: float = 3.0) -> ProcessResult:
        """
        Beendet einen Prozess sanft (SIGTERM).

        Args:
            pid: Die PID des zu beendenden Prozesses
            timeout: Maximale Wartezeit in Sekunden

        Returns:
            ProcessResult mit Erfolg/Misserfolg und Details
        """
        ...

    def kill(self, pid: int) -> ProcessResult:
        """
        Beendet einen Prozess erzwungen (SIGKILL).

        Args:
            pid: Die PID des zu beendenden Prozesses

        Returns:
            ProcessResult mit Erfolg/Misserfolg und Details
        """
        ...


class PidStorage(Protocol):
    """
    Interface für PID-Persistierung.

    Ermöglicht das Speichern und Laden der Listener-PID.
    Implementierung kann Datei, Registry oder In-Memory sein.
    """

    def read(self) -> Optional[int]:
        """
        Liest die gespeicherte PID.

        Returns:
            Die gespeicherte PID oder None wenn nicht vorhanden/ungültig
        """
        ...

    def write(self, pid: int) -> bool:
        """
        Speichert eine PID.

        Args:
            pid: Die zu speichernde Prozess-ID

        Returns:
            True bei Erfolg, False bei Fehler
        """
        ...

    def delete(self) -> bool:
        """
        Löscht die gespeicherte PID.

        Returns:
            True bei Erfolg, False bei Fehler
        """
        ...

    def exists(self) -> bool:
        """
        Prüft, ob eine PID gespeichert ist.

        Returns:
            True wenn eine PID existiert, sonst False
        """
        ...


class ProcessStarter(Protocol):
    """
    Interface für das Starten von Prozessen.

    Ermöglicht das Starten des Listener-Prozesses.
    Implementierung kann subprocess, Windows-API oder Mock sein.
    """

    def start(
        self,
        command: List[str],
        working_dir: str,
        log_file: Optional[str] = None,
        error_file: Optional[str] = None,
    ) -> StartResult:
        """
        Startet einen neuen Prozess.

        Args:
            command: Der auszuführende Befehl als Liste
            working_dir: Das Arbeitsverzeichnis
            log_file: Optionaler Pfad für stdout-Logging
            error_file: Optionaler Pfad für stderr-Logging

        Returns:
            StartResult mit PID bei Erfolg oder Fehlerdetails
        """
        ...
