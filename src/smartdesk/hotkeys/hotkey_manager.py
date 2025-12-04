# Dateipfad: src/smartdesk/hotkeys/hotkey_manager.py
"""
Hotkey-Manager - Öffentliche API für die Listener-Verwaltung.

Dieses Modul bietet die öffentliche Schnittstelle für:
- start_listener(): Startet den Hotkey-Listener
- stop_listener(): Stoppt den Hotkey-Listener
- restart_listener(): Neustart des Listeners
- is_listener_running(): Status-Abfrage
- get_listener_pid(): PID-Abfrage

Die Implementierung nutzt intern den ListenerManager mit Dependency Injection.
"""

import os
from typing import Optional

# Interne Importe
try:
    from ..shared.config import BASE_DIR, DATA_DIR
    from ..shared.localization import get_text
    from ..shared.style import PREFIX_OK, PREFIX_WARN, PREFIX_ERROR
    from ..shared.logging_config import get_logger
except ImportError:
    # Fallback für isoliertes Testen
    import logging

    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..')
    )
    DATA_DIR = BASE_DIR

    def get_text(key, **kwargs):
        return key.format(**kwargs) if kwargs else key

    PREFIX_OK = "[OK]"
    PREFIX_WARN = "[WARN]"
    PREFIX_ERROR = "[FEHLER]"

    def get_logger(name):
        return logging.getLogger(name)


# Manager-Komponenten
from .implementations import PsutilProcessController, FilePidStorage, SubprocessStarter
from .listener_manager import ListenerManager, ManagerResult

# Logging
logger = get_logger(__name__)

# =============================================================================
# Konfiguration
# =============================================================================

# Arbeitsverzeichnis (Projekt-Root für venv)
WORKING_DIRECTORY = BASE_DIR

# Laufzeit-Dateien in AppData
PID_FILE = os.path.join(DATA_DIR, "listener.pid")
LOG_FILE = os.path.join(DATA_DIR, "listener.log")
ERR_FILE = os.path.join(DATA_DIR, "listener_error.log")

# Python-Executable im venv
PYTHON_EXECUTABLE = os.path.join(WORKING_DIRECTORY, ".venv", "Scripts", "python.exe")

# Befehl zum Starten des Listeners
COMMAND_TO_RUN = [PYTHON_EXECUTABLE, "-m", "smartdesk.hotkeys.listener"]

# Timeout für graceful shutdown (Sekunden)
TERMINATE_TIMEOUT = 3.0


# =============================================================================
# Manager-Instanz (Singleton Pattern)
# =============================================================================

_manager: Optional[ListenerManager] = None


def _get_manager() -> ListenerManager:
    """
    Gibt die Manager-Instanz zurück (Lazy Initialization).

    Erstellt bei Bedarf eine neue Instanz mit allen Abhängigkeiten.
    """
    global _manager

    if _manager is None:
        logger.debug("Initialisiere ListenerManager...")

        _manager = ListenerManager(
            controller=PsutilProcessController(),
            storage=FilePidStorage(PID_FILE),
            starter=SubprocessStarter(hide_window=True),
            command=COMMAND_TO_RUN,
            working_dir=WORKING_DIRECTORY,
            log_file=LOG_FILE,
            error_file=ERR_FILE,
            terminate_timeout=TERMINATE_TIMEOUT,
        )

        # Optional: Callbacks registrieren
        _manager.on_start(lambda pid: logger.info(f"Listener gestartet (PID {pid})"))
        _manager.on_stop(lambda pid: logger.info(f"Listener gestoppt (PID {pid})"))

    return _manager


def reset_manager() -> None:
    """
    Setzt die Manager-Instanz zurück (für Tests).
    """
    global _manager
    _manager = None


def configure_manager(
    pid_file: Optional[str] = None,
    log_file: Optional[str] = None,
    error_file: Optional[str] = None,
    working_dir: Optional[str] = None,
    command: Optional[list] = None,
) -> None:
    """
    Konfiguriert den Manager mit benutzerdefinierten Pfaden.

    Muss VOR dem ersten Aufruf von start_listener/stop_listener aufgerufen werden.

    Args:
        pid_file: Pfad zur PID-Datei
        log_file: Pfad zur Log-Datei
        error_file: Pfad zur Error-Log-Datei
        working_dir: Arbeitsverzeichnis
        command: Befehl zum Starten
    """
    global _manager, PID_FILE, LOG_FILE, ERR_FILE, WORKING_DIRECTORY, COMMAND_TO_RUN

    if pid_file:
        PID_FILE = pid_file
    if log_file:
        LOG_FILE = log_file
    if error_file:
        ERR_FILE = error_file
    if working_dir:
        WORKING_DIRECTORY = working_dir
    if command:
        COMMAND_TO_RUN = command

    # Manager zurücksetzen, damit er neu initialisiert wird
    _manager = None


# =============================================================================
# Öffentliche API (Wrapper-Funktionen)
# =============================================================================


def _format_message(result: ManagerResult) -> str:
    """
    Formatiert die Nachricht mit i18n und PID.

    Args:
        result: Das ManagerResult-Objekt

    Returns:
        Formatierte Nachricht
    """
    key = f"hotkey_manager.{'info' if result.success else 'warn'}.{result.message}"

    kwargs = {}
    if result.pid:
        kwargs['pid'] = result.pid
    if result.error:
        kwargs['e'] = result.error

    return get_text(key, **kwargs) if kwargs else get_text(key)


def _print_result(result: ManagerResult) -> None:
    """
    Gibt das Ergebnis formatiert aus.

    Args:
        result: Das ManagerResult-Objekt
    """
    if result.success:
        if result.forced:
            print(f"{PREFIX_WARN} {_format_message(result)} (forced)")
        else:
            print(f"{PREFIX_OK} {_format_message(result)}")
    else:
        print(f"{PREFIX_WARN} {_format_message(result)}")


def start_listener() -> bool:
    """
    Startet den Hotkey-Listener als separaten Prozess.

    Returns:
        True bei Erfolg, False bei Fehler

    Beispiel:
        >>> from smartdesk.hotkeys import hotkey_manager
        >>> success = hotkey_manager.start_listener()
        >>> if success:
        ...     print("Listener läuft!")
    """
    manager = _get_manager()
    result = manager.start()

    if result.success:
        logger.info(f"Listener gestartet mit PID {result.pid}")
        print(
            f"{PREFIX_OK} {get_text('hotkey_manager.info.start_success', pid=result.pid)}"
        )
    elif result.message == "already_running":
        logger.warning(f"Listener läuft bereits (PID {result.pid})")
        print(f"{PREFIX_WARN} {get_text('hotkey_manager.warn.already_running')}")
    elif result.message == "python_not_found":
        logger.error(f"Python nicht gefunden: {PYTHON_EXECUTABLE}")
        print(
            f"{PREFIX_ERROR} {get_text('hotkey_manager.error.python_not_found', path=PYTHON_EXECUTABLE)}"
        )
        print(
            f"{PREFIX_WARN} Stelle sicher, dass das venv '.venv' heißt oder passe den Pfad an."
        )
    else:
        logger.error(f"Start fehlgeschlagen: {result.message}")
        print(
            f"{PREFIX_ERROR} {get_text('hotkey_manager.error.start_failed', e=result.error or result.message)}"
        )

    return result.success


def stop_listener() -> bool:
    """
    Stoppt den Hotkey-Listener-Prozess.

    Versucht zuerst ein sanftes Beenden. Falls das nicht funktioniert,
    wird der Prozess erzwungen beendet.

    Returns:
        True bei Erfolg, False bei Fehler

    Beispiel:
        >>> from smartdesk.hotkeys import hotkey_manager
        >>> hotkey_manager.stop_listener()
    """
    manager = _get_manager()
    result = manager.stop()

    if result.success:
        if result.forced:
            logger.warning(f"Listener erzwungen beendet (PID {result.pid})")
            print(
                f"{PREFIX_WARN} {get_text('hotkey_manager.warn.force_kill', pid=result.pid)}"
            )
        else:
            logger.info(f"Listener beendet (PID {result.pid})")
        print(
            f"{PREFIX_OK} {get_text('hotkey_manager.info.stop_success', pid=result.pid)}"
        )
        print(f"{PREFIX_OK} {get_text('hotkey_manager.info.pid_cleaned')}")
    elif result.message == "not_running":
        logger.info("Kein Listener läuft")
        print(f"{PREFIX_WARN} {get_text('hotkey_manager.warn.not_running')}")
    elif result.message == "process_not_found":
        logger.warning(f"Prozess {result.pid} nicht gefunden")
        print(
            f"{PREFIX_WARN} {get_text('hotkey_manager.warn.process_not_found', pid=result.pid)}"
        )
    elif result.message == "access_denied":
        logger.error(f"Zugriff auf Prozess {result.pid} verweigert")
        print(
            f"{PREFIX_ERROR} {get_text('hotkey_manager.error.access_denied', pid=result.pid)}"
        )
    else:
        logger.error(f"Stop fehlgeschlagen: {result.message}")
        print(
            f"{PREFIX_ERROR} {get_text('hotkey_manager.error.stop_failed', e=result.error or result.message)}"
        )

    return result.success


def restart_listener() -> bool:
    """
    Startet den Hotkey-Listener neu.

    Returns:
        True bei Erfolg, False bei Fehler
    """
    manager = _get_manager()
    result = manager.restart()

    if result.success:
        logger.info(f"Listener neu gestartet (PID {result.pid})")
        print(
            f"{PREFIX_OK} {get_text('hotkey_manager.info.restart_success', pid=result.pid)}"
        )
    else:
        logger.error(f"Neustart fehlgeschlagen: {result.message}")
        print(
            f"{PREFIX_ERROR} {get_text('hotkey_manager.error.restart_failed', e=result.error or result.message)}"
        )

    return result.success


def is_listener_running() -> bool:
    """
    Prüft, ob der Listener läuft.

    Returns:
        True wenn der Listener läuft, sonst False
    """
    return _get_manager().is_running()


def get_listener_pid() -> Optional[int]:
    """
    Gibt die PID des laufenden Listeners zurück.

    Returns:
        Die PID oder None wenn kein Listener läuft
    """
    return _get_manager().get_pid()


# =============================================================================
# Legacy-Kompatibilität
# =============================================================================


# Alte Funktionsnamen für Rückwärtskompatibilität
def get_pid() -> Optional[int]:
    """
    Alias für get_listener_pid().

    Deprecated: Verwende stattdessen get_listener_pid().
    """
    logger.warning("get_pid() ist deprecated, verwende get_listener_pid()")
    return get_listener_pid()
