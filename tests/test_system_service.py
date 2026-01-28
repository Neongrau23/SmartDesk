import pytest
from unittest.mock import MagicMock, patch
import time
import psutil

from smartdesk.core.services import system_service

def test_restart_explorer_kills_and_waits(mocker):
    """
    Verifies that restart_explorer:
    1. Finds 'explorer.exe' processes.
    2. Calls kill() on them.
    3. Calls wait_procs() on them.
    4. Waits for restart (simulated).
    """

    # Mock processes
    mock_proc = MagicMock()
    mock_proc.name.return_value = "explorer.exe"

    # Mock psutil.process_iter
    mock_iter = mocker.patch("psutil.process_iter")

    # Mock psutil.wait_procs
    mock_wait = mocker.patch("psutil.wait_procs", return_value=([], []))

    # Mock time.sleep to run fast
    mocker.patch("time.sleep")

    # Mock get_text
    mocker.patch("smartdesk.core.services.system_service.get_text", return_value="test info")

    # Setup side effects for process_iter:
    # 1. First call: Finding processes to kill -> returns [mock_proc]
    # 2. Second call: Checking if restarted (loop 1) -> returns [] (not yet)
    # 3. Third call: Checking if restarted (loop 2) -> returns [mock_proc] (restarted)

    # Note: loop uses process_iter(['name']).
    new_proc = MagicMock()
    new_proc.name.return_value = "explorer.exe"

    mock_iter.side_effect = [
        [mock_proc], # Finding to kill
        [],          # Restart check loop iteration 1
        [new_proc]   # Restart check loop iteration 2 (success)
    ]

    # Execute
    system_service.restart_explorer()

    # Verify kill called
    mock_proc.kill.assert_called_once()

    # Verify wait_procs called
    mock_wait.assert_called_once()
    args, kwargs = mock_wait.call_args
    assert args[0] == [mock_proc]
    assert kwargs['timeout'] == 5

def test_restart_explorer_no_process_found(mocker):
    """
    Verifies that if no explorer process is found initially,
    we skip kill/wait and go straight to restart check/start.
    """
    mock_iter = mocker.patch("psutil.process_iter")
    mock_wait = mocker.patch("psutil.wait_procs")
    mocker.patch("smartdesk.core.services.system_service.get_text", return_value="test info")
    mocker.patch("time.sleep")

    # Mock fallback Popen
    mock_popen = mocker.patch("subprocess.Popen")

    # Side effects:
    # 1. Finding -> []
    # 2. Restart check -> []
    # 3. Restart check -> [] ... until timeout

    mock_iter.side_effect = [[], [], [], [], [], [], [], [], [], [], []] # enough for loop

    # Force timeout in loop
    mocker.patch("time.time", side_effect=[0, 0, 10]) # Start check, loop check (fail), loop check (fail/timeout)

    system_service.restart_explorer()

    # Verify NO kill/wait
    mock_wait.assert_not_called()

    # Verify fallback start was attempted
    mock_popen.assert_called_with("explorer.exe")

def test_restart_explorer_kill_permission_error(mocker):
    """
    Verifies that if kill fails with NoSuchProcess, we continue safely.
    """
    mock_proc = MagicMock()
    mock_proc.name.return_value = "explorer.exe"
    mock_proc.kill.side_effect = psutil.NoSuchProcess(123)

    mock_iter = mocker.patch("psutil.process_iter", return_value=[mock_proc])
    mock_wait = mocker.patch("psutil.wait_procs", return_value=([], []))
    mocker.patch("smartdesk.core.services.system_service.get_text", return_value="test info")
    mocker.patch("time.sleep")

    # Handle the restart check loop
    new_proc = MagicMock()
    new_proc.name.return_value = "explorer.exe"
    mock_iter.side_effect = [
        [mock_proc],
        [new_proc] # Restarted immediately
    ]

    system_service.restart_explorer()

    mock_proc.kill.assert_called_once()
    # Should still wait (even if kill failed, we added it to list)
    # Actually if kill fails with NoSuchProcess, it means it's gone?
    # Logic:
    # try: p.kill() except NoSuchProcess: pass
    # procs.append(p) happened BEFORE kill attempt.
    # So wait_procs is called with it.
    mock_wait.assert_called_once()
