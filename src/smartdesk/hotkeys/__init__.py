# Dateipfad: src/smartdesk/hotkeys/__init__.py
"""
Hotkeys-Modul für SmartDesk.

Dieses Modul bietet:
- Listener-Management (start/stop)
- Hotkey-Aktionen
- Abstrakte Interfaces für Testbarkeit

Öffentliche API:
    - start_listener(): Startet den Hotkey-Listener
    - stop_listener(): Stoppt den Hotkey-Listener
    - restart_listener(): Neustart des Listeners
    - is_listener_running(): Prüft ob Listener läuft
    - get_listener_pid(): Gibt die PID zurück
"""

from .hotkey_manager import (
    start_listener,
    stop_listener,
    restart_listener,
    is_listener_running,
    get_listener_pid,
    configure_manager,
    reset_manager,
)

from .listener_manager import ListenerManager, ManagerResult, ListenerStatus

from .interfaces import (
    ProcessController,
    PidStorage,
    ProcessStarter,
    ProcessResult,
    ProcessState,
    StartResult,
)

from .implementations import PsutilProcessController, FilePidStorage, SubprocessStarter

# Banner-Controller für Hold-to-Show
from .banner_controller import (
    BannerController,
    BannerState,
    BannerConfig,
    get_banner_controller,
    set_banner_controller,
)

__all__ = [
    # Öffentliche API
    'start_listener',
    'stop_listener',
    'restart_listener',
    'is_listener_running',
    'get_listener_pid',
    'configure_manager',
    'reset_manager',
    # Manager-Klassen
    'ListenerManager',
    'ManagerResult',
    'ListenerStatus',
    # Interfaces (für Tests)
    'ProcessController',
    'PidStorage',
    'ProcessStarter',
    'ProcessResult',
    'ProcessState',
    'StartResult',
    # Implementierungen
    'PsutilProcessController',
    'FilePidStorage',
    'SubprocessStarter',
    # Banner-Controller
    'BannerController',
    'BannerState',
    'BannerConfig',
    'get_banner_controller',
    'set_banner_controller',
]
