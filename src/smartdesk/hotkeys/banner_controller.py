# Dateipfad: src/smartdesk/hotkeys/banner_controller.py
"""
Banner-Controller für Hold-to-Show Funktionalität.
Persistent-GUI Version: Hält den GUI-Prozess am Leben für sofortige Reaktion.
"""

import time
import threading
from enum import Enum, auto
from typing import Optional, Callable
from dataclasses import dataclass
import subprocess
import sys
import os
from smartdesk.shared.config import get_resource_path


class BannerState(Enum):
    IDLE = auto()
    ARMED = auto()
    HOLDING = auto()
    SHOWING = auto()


@dataclass
class BannerConfig:
    hold_duration_sec: float = 0.5
    arm_timeout_sec: float = 5.0
    check_interval_ms: int = 10


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
                # Pre-Start GUI process if not running
                self._ensure_process_running()

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
                self._log("Controller: Alt losgelassen - Verstecke GUI")
                self._hide_banner()
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
            self._hide_banner()
            self._state = BannerState.IDLE
            self._arm_time = 0
            self._hold_start_time = 0

    def shutdown(self) -> None:
        """Beendet den GUI-Prozess komplett."""
        self._send_command("QUIT")
        if self._gui_process:
            try:
                self._gui_process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                self._gui_process.kill()
            self._gui_process = None

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

    def _ensure_process_running(self) -> None:
        """Startet den GUI-Prozess im Hintergrund, falls er nicht läuft."""
        if self._gui_process is not None:
            if self._gui_process.poll() is None:
                return  # Läuft noch
            self._log(f"GUI: Prozess war beendet (Code {self._gui_process.returncode}). Starte neu...")

        try:
            python_exe = sys.executable
            script_path = get_resource_path("smartdesk/ui/gui/gui_overview.py")

            if not os.path.exists(script_path):
                self._log(f"GUI: Fehler - Skript nicht gefunden: {script_path}")
                return

            # Start mit PIPE für stdin
            self._gui_process = subprocess.Popen(
                [python_exe, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0),
                text=True,  # Text-Modus für einfacheres Schreiben
                bufsize=1,  # Line buffering
            )
            self._log(f"GUI: Prozess gestartet (PID: {self._gui_process.pid})")
        except Exception as e:
            self._log(f"GUI: Fehler beim Starten: {e}")

    def _send_command(self, cmd: str) -> None:
        if not self._gui_process or self._gui_process.poll() is not None:
            self._ensure_process_running()

        if self._gui_process and self._gui_process.stdin:
            try:
                self._gui_process.stdin.write(f"{cmd}\n")
                self._gui_process.stdin.flush()
                # self._log(f"GUI CMD: {cmd}")
            except Exception as e:
                self._log(f"GUI: Fehler beim Senden von '{cmd}': {e}")

    def _show_banner(self) -> None:
        self._send_command("SHOW")

    def _hide_banner(self) -> None:
        self._send_command("HIDE")


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
            _controller.shutdown()  # Cleanup old one
        _controller = controller
