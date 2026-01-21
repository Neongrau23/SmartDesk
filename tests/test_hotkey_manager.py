# Dateipfad: tests/test_hotkey_manager.py
"""
Unit Tests für den Hotkey-Manager.

Diese Tests nutzen Mock-Implementierungen der Interfaces,
um die Geschäftslogik ohne echte Prozesse zu testen.
"""

import os
import sys
import pytest
from typing import Optional, List
from unittest.mock import patch

# Projekt-Root zum Path hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from smartdesk.hotkeys.interfaces import ProcessResult, ProcessState, StartResult
from smartdesk.hotkeys.listener_manager import ListenerManager, ListenerStatus


# =============================================================================
# Mock-Implementierungen
# =============================================================================


class MockProcessController:
    """
    Mock-Implementierung von ProcessController.

    Erlaubt das Konfigurieren von Rückgabewerten für Tests.
    """

    def __init__(self, exists_return: bool = True, is_running_return: bool = True, terminate_success: bool = True, kill_success: bool = True):
        self.exists_return = exists_return
        self.is_running_return = is_running_return
        self.terminate_success = terminate_success
        self.kill_success = kill_success

        # Call tracking
        self.exists_calls: List[int] = []
        self.is_running_calls: List[int] = []
        self.terminate_calls: List[tuple] = []
        self.kill_calls: List[int] = []

    def exists(self, pid: int) -> bool:
        self.exists_calls.append(pid)
        return self.exists_return

    def is_running(self, pid: int) -> bool:
        self.is_running_calls.append(pid)
        return self.is_running_return

    def terminate(self, pid: int, timeout: float = 3.0) -> ProcessResult:
        self.terminate_calls.append((pid, timeout))

        if not self.exists_return:
            return ProcessResult(success=False, state=ProcessState.NOT_FOUND, message="process_not_found", pid=pid)

        if self.terminate_success:
            return ProcessResult(success=True, state=ProcessState.TERMINATED, message="terminated", pid=pid)
        else:
            return ProcessResult(success=False, state=ProcessState.RUNNING, message="timeout_expired", pid=pid)

    def kill(self, pid: int) -> ProcessResult:
        self.kill_calls.append(pid)

        if self.kill_success:
            return ProcessResult(success=True, state=ProcessState.KILLED, message="killed", pid=pid)
        else:
            return ProcessResult(success=False, state=ProcessState.ERROR, message="kill_error", pid=pid)


class MockPidStorage:
    """
    Mock-Implementierung von PidStorage.

    Speichert PID im Speicher statt in einer Datei.
    """

    def __init__(self, initial_pid: Optional[int] = None):
        self._pid = initial_pid

        # Call tracking
        self.read_calls: int = 0
        self.write_calls: List[int] = []
        self.delete_calls: int = 0

    def read(self) -> Optional[int]:
        self.read_calls += 1
        return self._pid

    def write(self, pid: int) -> bool:
        self.write_calls.append(pid)
        self._pid = pid
        return True

    def delete(self) -> bool:
        self.delete_calls += 1
        self._pid = None
        return True

    def exists(self) -> bool:
        return self._pid is not None


class MockProcessStarter:
    """
    Mock-Implementierung von ProcessStarter.

    Simuliert das Starten von Prozessen.
    """

    def __init__(self, success: bool = True, pid: int = 12345, error: Optional[Exception] = None):
        self.success = success
        self.pid = pid
        self.error = error

        # Call tracking
        self.start_calls: List[dict] = []

    def start(self, command: List[str], working_dir: str, log_file: Optional[str] = None, error_file: Optional[str] = None) -> StartResult:
        self.start_calls.append({"command": command, "working_dir": working_dir, "log_file": log_file, "error_file": error_file})

        if self.success:
            return StartResult(success=True, pid=self.pid, message="started")
        else:
            return StartResult(success=False, message="start_error", error=self.error)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_controller():
    """Erstellt einen Mock-ProcessController."""
    return MockProcessController()


@pytest.fixture
def mock_storage():
    """Erstellt einen Mock-PidStorage."""
    return MockPidStorage()


@pytest.fixture
def mock_starter():
    """Erstellt einen Mock-ProcessStarter."""
    return MockProcessStarter()


@pytest.fixture
def test_command():
    """Test-Befehl für den Listener."""
    return ["python", "-m", "smartdesk.hotkeys.listener"]


@pytest.fixture
def test_working_dir(tmp_path):
    """Temporäres Arbeitsverzeichnis."""
    return str(tmp_path)


@pytest.fixture
def manager(mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
    """Erstellt einen ListenerManager mit Mocks."""
    return ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)


# =============================================================================
# Tests: Status
# =============================================================================


class TestListenerStatus:
    """Tests für Status-Abfragen."""

    def test_status_stopped_when_no_pid(self, manager, mock_storage):
        """Status ist STOPPED wenn keine PID gespeichert ist."""
        mock_storage._pid = None

        status = manager.get_status()

        assert status == ListenerStatus.STOPPED

    def test_status_running_when_process_exists(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Status ist RUNNING wenn Prozess läuft."""
        mock_storage._pid = 12345
        mock_controller.is_running_return = True

        manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

        status = manager.get_status()

        assert status == ListenerStatus.RUNNING

    def test_status_stopped_when_process_not_running(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Status ist STOPPED und PID wird gelöscht wenn Prozess nicht läuft."""
        mock_storage._pid = 12345
        mock_controller.is_running_return = False

        manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

        status = manager.get_status()

        assert status == ListenerStatus.STOPPED
        assert mock_storage.delete_calls == 1  # PID wurde aufgeräumt

    def test_is_running_returns_bool(self, manager, mock_storage):
        """is_running() gibt einen Boolean zurück."""
        mock_storage._pid = None

        result = manager.is_running()

        assert result is False

    def test_get_pid_returns_none_when_not_running(self, manager, mock_storage):
        """get_pid() gibt None zurück wenn nicht läuft."""
        mock_storage._pid = None

        result = manager.get_pid()

        assert result is None


# =============================================================================
# Tests: Start
# =============================================================================


class TestListenerStart:
    """Tests für das Starten des Listeners."""

    def test_start_success(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Erfolgreicher Start erstellt PID."""
        mock_storage._pid = None
        mock_starter.pid = 99999

        # Mock os.path.exists für den Command-Check
        with patch("os.path.exists", return_value=True):
            manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

            result = manager.start()

        assert result.success is True
        assert result.pid == 99999
        assert mock_storage._pid == 99999
        assert len(mock_starter.start_calls) == 1

    def test_start_fails_when_already_running(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Start schlägt fehl wenn Listener bereits läuft."""
        mock_storage._pid = 12345
        mock_controller.is_running_return = True

        manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

        result = manager.start()

        assert result.success is False
        assert result.message == "already_running"
        assert len(mock_starter.start_calls) == 0  # Kein Start-Versuch

    def test_start_fails_when_python_not_found(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Start schlägt fehl wenn Python-Executable nicht existiert."""
        mock_storage._pid = None

        with patch("os.path.exists", return_value=False):
            manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

            result = manager.start()

        assert result.success is False
        assert result.message == "python_not_found"

    def test_start_fires_callback(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Start löst registrierte Callbacks aus."""
        mock_storage._pid = None
        callback_called = []

        with patch("os.path.exists", return_value=True):
            manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

            manager.on_start(lambda pid: callback_called.append(pid))
            result = manager.start()

        assert result.success is True
        assert callback_called == [12345]


# =============================================================================
# Tests: Stop
# =============================================================================


class TestListenerStop:
    """Tests für das Stoppen des Listeners."""

    def test_stop_when_not_running(self, manager, mock_storage):
        """Stop gibt Fehler zurück wenn nicht läuft."""
        mock_storage._pid = None

        result = manager.stop()

        assert result.success is False
        assert result.message == "not_running"

    def test_stop_success_graceful(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Erfolgreicher Stop mit SIGTERM."""
        mock_storage._pid = 12345
        mock_controller.exists_return = True
        mock_controller.terminate_success = True

        manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

        result = manager.stop()

        assert result.success is True
        assert result.forced is False
        assert mock_storage._pid is None  # PID wurde gelöscht
        assert len(mock_controller.terminate_calls) == 1
        assert len(mock_controller.kill_calls) == 0  # Kein Kill nötig

    def test_stop_with_force_kill(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Stop mit Force-Kill wenn SIGTERM fehlschlägt."""
        mock_storage._pid = 12345
        mock_controller.exists_return = True
        mock_controller.terminate_success = False  # SIGTERM schlägt fehl
        mock_controller.kill_success = True

        manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

        result = manager.stop()

        assert result.success is True
        assert result.forced is True
        assert len(mock_controller.kill_calls) == 1

    def test_stop_when_process_not_found(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Stop räumt auf wenn Prozess nicht mehr existiert."""
        mock_storage._pid = 12345
        mock_controller.exists_return = False

        manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

        result = manager.stop()

        assert result.success is False
        assert result.message == "process_not_found"
        assert mock_storage._pid is None  # PID wurde trotzdem aufgeräumt

    def test_stop_fires_callback(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Stop löst registrierte Callbacks aus."""
        mock_storage._pid = 12345
        mock_controller.exists_return = True
        callback_called = []

        manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

        manager.on_stop(lambda pid: callback_called.append(pid))
        result = manager.stop()

        assert result.success is True
        assert callback_called == [12345]


# =============================================================================
# Tests: Restart
# =============================================================================


class TestListenerRestart:
    """Tests für den Neustart des Listeners."""

    def test_restart_when_running(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Neustart stoppt und startet den Listener."""
        mock_storage._pid = 12345
        mock_controller.is_running_return = True
        mock_controller.exists_return = True
        mock_controller.terminate_success = True
        mock_starter.pid = 99999

        with patch("os.path.exists", return_value=True):
            manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

            result = manager.restart()

        assert result.success is True
        assert result.pid == 99999
        assert len(mock_controller.terminate_calls) == 1  # Stop wurde aufgerufen
        assert len(mock_starter.start_calls) == 1  # Start wurde aufgerufen

    def test_restart_when_not_running(self, mock_controller, mock_storage, mock_starter, test_command, test_working_dir):
        """Neustart startet einfach wenn nicht läuft."""
        mock_storage._pid = None
        mock_starter.pid = 99999

        with patch("os.path.exists", return_value=True):
            manager = ListenerManager(controller=mock_controller, storage=mock_storage, starter=mock_starter, command=test_command, working_dir=test_working_dir)

            result = manager.restart()

        assert result.success is True
        assert result.pid == 99999
        assert len(mock_controller.terminate_calls) == 0  # Kein Stop nötig
        assert len(mock_starter.start_calls) == 1


# =============================================================================
# Tests: FilePidStorage
# =============================================================================


class TestFilePidStorage:
    """Tests für die Datei-basierte PID-Speicherung."""

    def test_read_returns_none_when_file_not_exists(self, tmp_path):
        """read() gibt None zurück wenn Datei nicht existiert."""
        from smartdesk.hotkeys.implementations import FilePidStorage

        storage = FilePidStorage(str(tmp_path / "nonexistent.pid"))

        result = storage.read()

        assert result is None

    def test_write_and_read(self, tmp_path):
        """write() speichert PID, read() liest sie."""
        from smartdesk.hotkeys.implementations import FilePidStorage

        storage = FilePidStorage(str(tmp_path / "test.pid"))

        storage.write(12345)
        result = storage.read()

        assert result == 12345

    def test_delete_removes_file(self, tmp_path):
        """delete() löscht die PID-Datei."""
        from smartdesk.hotkeys.implementations import FilePidStorage

        pid_file = tmp_path / "test.pid"
        storage = FilePidStorage(str(pid_file))

        storage.write(12345)
        assert pid_file.exists()

        storage.delete()
        assert not pid_file.exists()

    def test_read_handles_corrupt_file(self, tmp_path):
        """read() gibt None zurück bei korrupter Datei."""
        from smartdesk.hotkeys.implementations import FilePidStorage

        pid_file = tmp_path / "test.pid"
        pid_file.write_text("not a number")

        storage = FilePidStorage(str(pid_file))
        result = storage.read()

        assert result is None
        assert not pid_file.exists()  # Datei wurde gelöscht


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration Tests mit echten Implementierungen."""

    def test_full_lifecycle(self, tmp_path):
        """Test des kompletten Start/Stop Zyklus mit Mocks."""
        from smartdesk.hotkeys.implementations import FilePidStorage

        # Setup
        controller = MockProcessController()
        storage = FilePidStorage(str(tmp_path / "listener.pid"))
        starter = MockProcessStarter(pid=12345)

        manager = ListenerManager(controller=controller, storage=storage, starter=starter, command=["python", "-m", "test"], working_dir=str(tmp_path))

        # Start
        with patch("os.path.exists", return_value=True):
            start_result = manager.start()

        assert start_result.success is True
        assert storage.read() == 12345

        # Status prüfen
        controller.is_running_return = True
        assert manager.is_running() is True

        # Stop
        stop_result = manager.stop()

        assert stop_result.success is True
        assert storage.read() is None
