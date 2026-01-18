# Dateipfad: tests/test_banner_controller.py
"""
Unit-Tests für den Banner-Controller.
"""

import time
from unittest.mock import patch, MagicMock

from smartdesk.hotkeys.banner_controller import (
    BannerController,
    BannerState,
    BannerConfig
)


class MockBanner:
    """Mock-Implementierung des BannerUI Protocols."""
    
    def __init__(self):
        self._visible = False
        self.show_called = False
        self.close_called = False
    
    def show(self) -> None:
        self._visible = True
        self.show_called = True
    
    def close(self) -> None:
        self._visible = False
        self.close_called = True
    
    @property
    def is_visible(self) -> bool:
        return self._visible


class TestBannerControllerStates:
    """Tests für die State-Machine des Banner-Controllers."""
    
    def test_initial_state_is_idle(self):
        """Controller startet im IDLE-Zustand."""
        ctrl = BannerController()
        assert ctrl.state == BannerState.IDLE
    
    def test_ctrl_shift_triggers_armed_state(self):
        """Strg+Shift wechselt von IDLE zu ARMED."""
        ctrl = BannerController()
        ctrl.on_ctrl_shift_triggered()
        assert ctrl.state == BannerState.ARMED
    
    def test_ctrl_shift_only_works_from_idle(self):
        """Strg+Shift funktioniert nur aus IDLE."""
        ctrl = BannerController()
        ctrl.on_ctrl_shift_triggered()  # -> ARMED
        ctrl.on_ctrl_shift_triggered()  # Sollte nichts ändern
        assert ctrl.state == BannerState.ARMED
    
    def test_alt_pressed_triggers_holding_from_armed(self):
        """Alt drücken wechselt von ARMED zu HOLDING."""
        ctrl = BannerController()
        ctrl.on_ctrl_shift_triggered()
        ctrl.on_alt_pressed()
        assert ctrl.state == BannerState.HOLDING
    
    def test_alt_pressed_does_nothing_from_idle(self):
        """Alt drücken aus IDLE ändert nichts."""
        ctrl = BannerController()
        ctrl.on_alt_pressed()
        assert ctrl.state == BannerState.IDLE
    
    def test_alt_released_from_holding_returns_to_idle(self):
        """Alt loslassen aus HOLDING geht zurück zu IDLE."""
        ctrl = BannerController()
        ctrl.on_ctrl_shift_triggered()
        ctrl.on_alt_pressed()
        ctrl.on_alt_released()
        assert ctrl.state == BannerState.IDLE
    
    def test_reset_returns_to_idle(self):
        """Reset bringt Controller immer zurück zu IDLE."""
        ctrl = BannerController()
        ctrl.on_ctrl_shift_triggered()
        ctrl.on_alt_pressed()
        ctrl.reset()
        assert ctrl.state == BannerState.IDLE


class TestBannerControllerTiming:
    """Tests für die Timing-Logik."""

    @patch('smartdesk.hotkeys.banner_controller.subprocess.Popen')
    def test_banner_shows_after_hold_duration(self, mock_popen):
        """Banner erscheint nach der Hold-Duration."""
        # Mock Popen return value to simulate running process
        process_mock = mock_popen.return_value
        process_mock.poll.return_value = None
        process_mock.pid = 12345

        config = BannerConfig(hold_duration_sec=0.1)
        ctrl = BannerController(config=config)

        ctrl.on_ctrl_shift_triggered()
        ctrl.on_alt_pressed()

        # Warte länger als Hold-Duration
        time.sleep(0.2)

        assert ctrl.state == BannerState.SHOWING
        mock_popen.assert_called()

    @patch('smartdesk.hotkeys.banner_controller.subprocess.Popen')
    def test_banner_does_not_show_if_released_early(self, mock_popen):
        """Banner erscheint nicht, wenn Alt zu früh losgelassen."""
        config = BannerConfig(hold_duration_sec=1.0)
        ctrl = BannerController(config=config)
        
        ctrl.on_ctrl_shift_triggered()
        ctrl.on_alt_pressed()
        
        # Sofort loslassen
        ctrl.on_alt_released()
        
        assert ctrl.state == BannerState.IDLE
        mock_popen.assert_not_called()
    
    @patch('smartdesk.hotkeys.banner_controller.subprocess.Popen')
    def test_banner_closes_on_alt_release(self, mock_popen):
        """Banner schließt wenn Alt losgelassen wird."""
        # Setup Mock Process
        process_mock = mock_popen.return_value
        process_mock.poll.return_value = None
        process_mock.stdin = MagicMock()
        
        config = BannerConfig(hold_duration_sec=0.05)
        ctrl = BannerController(config=config)

        ctrl.on_ctrl_shift_triggered()
        ctrl.on_alt_pressed()
        time.sleep(0.1)  # Warte bis Banner erscheint

        assert ctrl.state == BannerState.SHOWING
        mock_popen.assert_called()

        ctrl.on_alt_released()

        assert ctrl.state == BannerState.IDLE
        # Prüfen ob stdin.close() aufgerufen wurde (Signal zum Schließen)
        process_mock.stdin.close.assert_called()
class TestBannerControllerLogging:
    """Tests für die Logging-Funktionalität."""
    
    def test_log_function_is_called(self):
        """Log-Funktion wird bei State-Änderungen aufgerufen."""
        log_messages = []
        
        ctrl = BannerController(log_func=log_messages.append)
        ctrl.on_ctrl_shift_triggered()
        
        assert len(log_messages) == 1
        assert "ARMED" in log_messages[0]
    
    def test_log_function_optional(self):
        """Controller funktioniert ohne Log-Funktion."""
        ctrl = BannerController()  # Keine log_func
        ctrl.on_ctrl_shift_triggered()
        assert ctrl.state == BannerState.ARMED


class TestBannerControllerConfig:
    """Tests für die Konfiguration."""
    
    def test_custom_hold_duration(self):
        """Benutzerdefinierte Hold-Duration wird respektiert."""
        config = BannerConfig(hold_duration_sec=2.5)
        ctrl = BannerController(config=config)
        assert ctrl.config.hold_duration_sec == 2.5
    
    def test_default_config_values(self):
        """Standard-Konfiguration hat sinnvolle Werte."""
        ctrl = BannerController()
        assert ctrl.config.hold_duration_sec == 0.01
        assert ctrl.config.arm_timeout_sec == 5.0
        assert ctrl.config.check_interval_ms == 0.01


class TestBannerControllerArmTimeout:
    """Tests für das ARM-Timeout."""
    
    def test_arm_timeout_resets_to_idle(self):
        """ARMED-Zustand läuft nach Timeout ab."""
        config = BannerConfig(arm_timeout_sec=0.1)  # Kurz für Tests
        ctrl = BannerController(config=config)
        
        ctrl.on_ctrl_shift_triggered()
        assert ctrl.state == BannerState.ARMED
        
        # Warte länger als Timeout
        time.sleep(0.15)
        
        # Manuell prüfen (im echten System durch Polling)
        ctrl.check_arm_timeout()
        
        assert ctrl.state == BannerState.IDLE
