# Dateipfad: src/smartdesk/hotkeys/banner_controller.py
"""
Banner-Controller für Hold-to-Show Funktionalität.

Verwaltet den Zustand für die Tastenkombination:
1. Strg+Shift drücken (und loslassen)
2. Alt halten → Nach 1 Sekunde erscheint Banner
3. Alt loslassen → Banner verschwindet

Dieser Controller ist unabhängig vom UI und kann getestet werden.
"""

import time
import threading
import queue
from enum import Enum, auto
from typing import Optional, Callable, Protocol
from dataclasses import dataclass


class BannerState(Enum):
    """Zustände der Banner State-Machine."""
    IDLE = auto()                    # Warte auf Strg+Shift
    ARMED = auto()                   # Strg+Shift erkannt, warte auf Alt
    HOLDING = auto()                 # Alt wird gehalten, Timer läuft
    SHOWING = auto()                 # Banner wird angezeigt


@dataclass
class BannerConfig:
    """Konfiguration für den Banner-Controller."""
    hold_duration_sec: float = 1.0   # Wie lange Alt gehalten werden muss
    arm_timeout_sec: float = 5.0     # Timeout nach Strg+Shift
    check_interval_ms: int = 50      # Wie oft der Timer geprüft wird


class BannerUI(Protocol):
    """Interface für die Banner-UI."""
    
    def show(self) -> None:
        """Zeigt das Banner an."""
        ...
    
    def close(self) -> None:
        """Schließt das Banner."""
        ...
    
    @property
    def is_visible(self) -> bool:
        """Gibt zurück, ob das Banner sichtbar ist."""
        ...


class BannerController:
    """
    Steuert die Hold-to-Show Logik für das Desktop-Status-Banner.
    
    Verwendung:
        controller = BannerController(banner_factory=create_banner)
        
        # Im Listener:
        controller.on_ctrl_shift_triggered()  # Wenn Strg+Shift losgelassen
        controller.on_alt_pressed()           # Wenn Alt gedrückt
        controller.on_alt_released()          # Wenn Alt losgelassen
    """
    
    def __init__(
        self,
        banner_factory: Optional[Callable[[], BannerUI]] = None,
        config: Optional[BannerConfig] = None,
        log_func: Optional[Callable[[str], None]] = None
    ):
        """
        Initialisiert den Controller.
        
        Args:
            banner_factory: Funktion die ein neues BannerUI erstellt
            config: Optionale Konfiguration
            log_func: Optionale Log-Funktion
        """
        self.config = config or BannerConfig()
        self._banner_factory = banner_factory
        self._log = log_func or (lambda msg: None)
        
        # State
        self._state = BannerState.IDLE
        self._arm_time: float = 0
        self._hold_start_time: float = 0
        self._banner: Optional[BannerUI] = None
        
        # Threading
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_timer = threading.Event()
        self._lock = threading.Lock()
    
    @property
    def state(self) -> BannerState:
        """Aktueller Zustand."""
        return self._state
    
    def on_ctrl_shift_triggered(self) -> None:
        """
        Wird aufgerufen, wenn Strg+Shift losgelassen wurde.
        Setzt den Controller in den ARMED-Zustand.
        """
        with self._lock:
            if self._state == BannerState.IDLE:
                self._state = BannerState.ARMED
                self._arm_time = time.time()
                self._log("Banner: ARMED - Warte auf Alt")
    
    def on_alt_pressed(self) -> None:
        """
        Wird aufgerufen, wenn Alt gedrückt wird.
        Startet den Hold-Timer wenn ARMED.
        """
        with self._lock:
            if self._state == BannerState.ARMED:
                self._state = BannerState.HOLDING
                self._hold_start_time = time.time()
                self._log("Banner: HOLDING - Timer gestartet")
                self._start_hold_timer()
    
    def on_alt_released(self) -> None:
        """
        Wird aufgerufen, wenn Alt losgelassen wird.
        Schließt das Banner oder bricht den Timer ab.
        """
        with self._lock:
            if self._state == BannerState.SHOWING:
                self._log("Banner: Alt losgelassen - Schließe Banner")
                self._close_banner()
                self._state = BannerState.IDLE
                
            elif self._state == BannerState.HOLDING:
                self._log("Banner: Alt zu früh losgelassen - Abbruch")
                self._stop_timer.set()
                self._state = BannerState.IDLE
                
            elif self._state == BannerState.ARMED:
                # Alt wurde vor dem Halten losgelassen
                self._state = BannerState.IDLE
    
    def check_arm_timeout(self) -> None:
        """
        Prüft ob der ARMED-Zustand abgelaufen ist.
        Sollte periodisch aufgerufen werden.
        """
        with self._lock:
            if self._state == BannerState.ARMED:
                elapsed = time.time() - self._arm_time
                if elapsed > self.config.arm_timeout_sec:
                    self._log("Banner: ARM Timeout - Reset")
                    self._state = BannerState.IDLE
    
    def reset(self) -> None:
        """Setzt den Controller zurück."""
        with self._lock:
            self._stop_timer.set()
            self._close_banner()
            self._state = BannerState.IDLE
            self._arm_time = 0
            self._hold_start_time = 0
    
    def _start_hold_timer(self) -> None:
        """Startet den Timer-Thread für die Hold-Duration."""
        self._stop_timer.clear()
        
        def timer_loop():
            while not self._stop_timer.is_set():
                with self._lock:
                    if self._state != BannerState.HOLDING:
                        break
                    
                    elapsed = time.time() - self._hold_start_time
                    if elapsed >= self.config.hold_duration_sec:
                        self._log(f"Banner: Hold-Zeit erreicht ({elapsed:.1f}s)")
                        self._show_banner()
                        self._state = BannerState.SHOWING
                        break
                
                # Warte mit Unterbrechungsmöglichkeit
                self._stop_timer.wait(self.config.check_interval_ms / 1000)
        
        self._timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self._timer_thread.start()
    
    def _show_banner(self) -> None:
        """Zeigt das Banner an (thread-safe via BannerManager)."""
        try:
            manager = get_banner_manager()
            manager.show_banner()
            self._log("Banner: Anzeige gestartet")
        except Exception as e:
            self._log(f"Banner: Fehler beim Anzeigen: {e}")
    
    def _close_banner(self) -> None:
        """Schließt das Banner (thread-safe via BannerManager)."""
        try:
            manager = get_banner_manager()
            manager.close_banner()
            self._log("Banner: Geschlossen")
        except Exception as e:
            self._log(f"Banner: Fehler beim Schließen: {e}")


# =============================================================================
# Singleton-Instanz für globalen Zugriff
# =============================================================================

_controller: Optional[BannerController] = None
_controller_lock = threading.Lock()


def get_banner_controller() -> BannerController:
    """
    Gibt die globale BannerController-Instanz zurück.
    Erstellt sie bei Bedarf mit Standard-Einstellungen.
    """
    global _controller
    
    with _controller_lock:
        if _controller is None:
            _controller = BannerController(
                banner_factory=_create_default_banner
            )
        return _controller


def set_banner_controller(controller: BannerController) -> None:
    """Setzt eine benutzerdefinierte Controller-Instanz."""
    global _controller
    
    with _controller_lock:
        if _controller:
            _controller.reset()
        _controller = controller


def _create_default_banner() -> BannerUI:
    """Erstellt das Standard-Banner mit Desktop-Status."""
    # Import hier um zirkuläre Imports zu vermeiden
    from ..shared.animations.taskbar_banner import TaskbarBanner
    from ..core.services import desktop_service
    
    # Desktop-Status abrufen
    try:
        desktops = desktop_service.get_all_desktops()
        
        if not desktops:
            message = "Keine SmartDesk-Desktops konfiguriert"
            icon = "⚠"
        else:
            parts = []
            active_found = False
            
            for d in desktops:
                if d.is_active:
                    parts.append(f"▶ {d.name}")
                    active_found = True
                else:
                    parts.append(f"• {d.name}")
            
            message = "    ".join(parts)
            icon = "💻" if active_found else "🔔"
            
    except Exception as e:
        message = f"Fehler: {e}"
        icon = "❌"
    
    return TaskbarBanner(message=message, icon=icon)


# =============================================================================
# Thread-Safe Banner-Manager für Tkinter
# =============================================================================

class ThreadedBannerManager:
    """
    Verwaltet das Banner in einem separaten Thread mit eigenem Tkinter-Root.
    
    Tkinter muss im Main-Thread laufen, aber der Listener läuft auch im Main-Thread.
    Lösung: Wir starten einen eigenen Thread mit eigenem Tkinter-Root für das Banner.
    """
    
    def __init__(self):
        self._banner_thread: Optional[threading.Thread] = None
        self._command_queue: queue.Queue = queue.Queue()
        self._running = False
        self._lock = threading.Lock()
    
    def show_banner(self) -> None:
        """Zeigt das Banner an (thread-safe)."""
        with self._lock:
            if not self._running:
                self._start_banner_thread()
            self._command_queue.put(("show", None))
    
    def close_banner(self) -> None:
        """Schließt das Banner (thread-safe)."""
        with self._lock:
            self._command_queue.put(("close", None))
    
    def _start_banner_thread(self) -> None:
        """Startet den Banner-Thread."""
        self._running = True
        self._banner_thread = threading.Thread(
            target=self._banner_thread_loop,
            daemon=True
        )
        self._banner_thread.start()
    
    def _banner_thread_loop(self) -> None:
        """Der Haupt-Loop des Banner-Threads."""
        import tkinter as tk
        
        try:
            root = tk.Tk()
            root.withdraw()
            
            banner = None
            
            def check_commands():
                nonlocal banner
                try:
                    while True:
                        cmd, data = self._command_queue.get_nowait()
                        
                        if cmd == "show" and banner is None:
                            banner = _create_default_banner_with_parent(root)
                            banner.show()
                            
                        elif cmd == "close" and banner is not None:
                            banner.close()
                            banner = None
                            
                        elif cmd == "quit":
                            root.quit()
                            return
                            
                except queue.Empty:
                    pass
                
                # Weiter prüfen alle 50ms
                root.after(50, check_commands)
            
            # Starte Command-Check
            root.after(50, check_commands)
            root.mainloop()
            
        except Exception as e:
            print(f"Banner-Thread Fehler: {e}")
        finally:
            with self._lock:
                self._running = False


def _create_default_banner_with_parent(parent) -> 'BannerUI':
    """Erstellt das Standard-Banner mit Parent-Fenster."""
    from ..shared.animations.taskbar_banner import TaskbarBanner
    from ..core.services import desktop_service
    
    try:
        desktops = desktop_service.get_all_desktops()
        
        if not desktops:
            message = "Keine SmartDesk-Desktops konfiguriert"
            icon = "⚠"
        else:
            parts = []
            active_found = False
            
            for d in desktops:
                if d.is_active:
                    parts.append(f"▶ {d.name}")
                    active_found = True
                else:
                    parts.append(f"• {d.name}")
            
            message = "    ".join(parts)
            icon = "💻" if active_found else "🔔"
            
    except Exception as e:
        message = f"Fehler: {e}"
        icon = "❌"
    
    return TaskbarBanner(message=message, icon=icon, parent=parent)


# Globaler Banner-Manager
_banner_manager: Optional[ThreadedBannerManager] = None
_banner_manager_lock = threading.Lock()


def get_banner_manager() -> ThreadedBannerManager:
    """Gibt den globalen Banner-Manager zurück."""
    global _banner_manager
    
    with _banner_manager_lock:
        if _banner_manager is None:
            _banner_manager = ThreadedBannerManager()
        return _banner_manager
