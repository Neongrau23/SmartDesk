# Dateipfad: src/smartdesk/hotkeys/banner_controller.py
"""
Banner-Controller für Hold-to-Show Funktionalität.
Korrigierte Version: Non-blocking Close für sofortige Reaktion.
"""

import time
import threading
from enum import Enum, auto
from typing import Optional, Callable
from dataclasses import dataclass
import subprocess
import sys
import os

class BannerState(Enum):
    IDLE = auto()
    ARMED = auto()
    HOLDING = auto()
    SHOWING = auto()

@dataclass
class BannerConfig:
    hold_duration_sec: float = 0.01
    arm_timeout_sec: float = 5.0
    check_interval_ms: int = 0.01

class BannerController:
    def __init__(
        self,
        config: Optional[BannerConfig] = None,
        log_func: Optional[Callable[[str], None]] = None,
    ):
        self.config = config or BannerConfig()
        self._log = log_func or (lambda msg: None)

        # State
        self._state = BannerState.IDLE
        self._arm_time: float = 0
        self._hold_start_time: float = 0
        self._gui_process: Optional[subprocess.Popen] = None

        # Threading
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_timer = threading.Event()
        self._lock = threading.Lock()

    @property
    def state(self) -> BannerState:
        return self._state

    def on_ctrl_shift_triggered(self) -> None:
        with self._lock:
            if self._state == BannerState.IDLE:
                self._state = BannerState.ARMED
                self._arm_time = time.time()
                self._log("Controller: ARMED - Warte auf Alt")

    def on_alt_pressed(self) -> None:
        with self._lock:
            if self._state == BannerState.ARMED:
                self._state = BannerState.HOLDING
                self._hold_start_time = time.time()
                
                if self.config.hold_duration_sec <= 0:
                    self._log("Controller: Instant Show (0s delay)")
                    self._show_banner()
                    self._state = BannerState.SHOWING
                else:
                    self._log(f"Controller: HOLDING - Timer gestartet ({self.config.hold_duration_sec}s)")
                    self._start_hold_timer()

    def on_alt_released(self) -> None:
        with self._lock:
            if self._state == BannerState.SHOWING:
                self._log("Controller: Alt losgelassen - Schließe GUI")
                self._close_banner()
                self._state = BannerState.IDLE

            elif self._state == BannerState.HOLDING:
                self._log("Controller: Alt zu früh losgelassen - Abbruch")
                self._stop_timer.set()
                self._state = BannerState.IDLE

            elif self._state == BannerState.ARMED:
                self._state = BannerState.IDLE

    def check_arm_timeout(self) -> None:
        with self._lock:
            if self._state == BannerState.ARMED:
                elapsed = time.time() - self._arm_time
                if elapsed > self.config.arm_timeout_sec:
                    self._log("Controller: ARM Timeout - Reset")
                    self._state = BannerState.IDLE

    def reset(self) -> None:
        with self._lock:
            self._stop_timer.set()
            self._close_banner()
            self._state = BannerState.IDLE
            self._arm_time = 0
            self._hold_start_time = 0

    def _start_hold_timer(self) -> None:
        self._stop_timer.clear()

        def timer_loop():
            while not self._stop_timer.is_set():
                with self._lock:
                    if self._state != BannerState.HOLDING:
                        break

                    elapsed = time.time() - self._hold_start_time
                    if elapsed >= self.config.hold_duration_sec:
                        self._log(f"Controller: Hold-Zeit erreicht ({elapsed:.1f}s)")
                        self._show_banner()
                        self._state = BannerState.SHOWING
                        break

                self._stop_timer.wait(self.config.check_interval_ms / 1000)

        self._timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self._timer_thread.start()

    def _start_gui_overview(self) -> None:
        """Startet die gui_overview.py."""
        if self._gui_process is not None and self._gui_process.poll() is None:
            return

        try:
            python_exe = sys.executable
            # Pfad muss ggf. an deine Ordnerstruktur angepasst werden
            script_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "..", "ui", "gui", "gui_overview.py"
            ))

            if not os.path.exists(script_path):
                self._log(f"GUI: Fehler - Skript nicht gefunden: {script_path}")
                return

            self._gui_process = subprocess.Popen(
                [python_exe, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                ),
            )
            self._log(f"GUI: gui_overview.py gestartet. PID: {self._gui_process.pid}")
        except Exception as e:
            self._log(f"GUI: Fehler beim Starten von gui_overview.py: {e}")

    def _stop_gui_overview(self) -> None:
        """
        Sendet das Schließen-Signal (via stdin close).
        Wartet NICHT im Hauptthread auf das Ende des Prozesses,
        damit die GUI sofort reagiert.
        """
        if self._gui_process and self._gui_process.poll() is None:
            self._log("GUI: Signal zum Schließen gesendet (non-blocking).")
            
            # 1. Signal senden: Stdin schließen
            if self._gui_process.stdin:
                try:
                    self._gui_process.stdin.close()
                except Exception as e:
                    self._log(f"GUI: Fehler beim Schließen von stdin: {e}")

            # 2. Aufräumen in separaten Thread auslagern
            cleanup_thread = threading.Thread(
                target=self._wait_and_cleanup,
                args=(self._gui_process,),
                daemon=True
            )
            cleanup_thread.start()

            # Referenz sofort entfernen
            self._gui_process = None
        else:
            self._gui_process = None

    def _wait_and_cleanup(self, process: subprocess.Popen):
        """Hilfsmethode für den Hintergrund-Thread."""
        try:
            # Gib der GUI Zeit für die Animation (1.5s Puffer)
            process.wait(timeout=1.5)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception:
            pass

    def _show_banner(self) -> None:
        self._start_gui_overview()
        self._log("GUI: Anzeige gestartet")

    def _close_banner(self) -> None:
        self._stop_gui_overview()
        self._log("GUI: Geschlossen")

# Singleton
_controller: Optional[BannerController] = None
_controller_lock = threading.Lock()

def get_banner_controller() -> BannerController:
    global _controller
    with _controller_lock:
        if _controller is None:
            _controller = BannerController()
        return _controller

def set_banner_controller(controller: BannerController) -> None:
    global _controller
    with _controller_lock:
        if _controller:
            _controller.reset()
        _controller = controller