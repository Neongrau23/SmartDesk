import pytest
from unittest.mock import patch, MagicMock
from smartdesk.core.services.system_service import restart_explorer

@patch('smartdesk.core.services.system_service.psutil')
@patch('smartdesk.core.services.system_service.subprocess')
@patch('smartdesk.core.services.system_service.time')
def test_restart_explorer_success(mock_time, mock_subprocess, mock_psutil):
    # Setup
    proc = MagicMock()
    proc.name.return_value = "explorer.exe"

    # process_iter returns list with one explorer
    # Note: process_iter is an iterator usually, but list is fine for mock return_value if iterated once
    # Wait, process_iter is called twice. Once at start, once at end.
    mock_psutil.process_iter.side_effect = [
        [proc], # First call: finding processes to kill
        [proc]  # Second call: verifying restart (success)
    ]

    # wait_procs returns (gone, alive)
    mock_psutil.wait_procs.return_value = ([proc], [])

    # Run
    restart_explorer()

    # Assertions
    # 1. Check if process_iter was called with ['name']
    mock_psutil.process_iter.assert_called_with(['name'])

    # 2. Check if taskkill was called
    mock_subprocess.run.assert_called_with(
        ["taskkill", "/F", "/IM", "explorer.exe"],
        capture_output=True,
        check=False
    )

    # 3. Check if wait_procs was called with the captured list
    mock_psutil.wait_procs.assert_called()
    args, kwargs = mock_psutil.wait_procs.call_args
    # args[0] should be the list [proc]
    assert args[0] == [proc]
    assert kwargs.get('timeout') == 5 or args[1] == 5

    # 4. Check if Popen was called to restart
    mock_subprocess.Popen.assert_called_with("explorer.exe")

@patch('smartdesk.core.services.system_service.psutil')
@patch('smartdesk.core.services.system_service.subprocess')
@patch('smartdesk.core.services.system_service.time')
def test_restart_explorer_not_running_initially(mock_time, mock_subprocess, mock_psutil):
    # Setup
    mock_psutil.process_iter.return_value = [] # No processes

    # Run
    restart_explorer()

    # Assertions
    # Should start explorer immediately
    mock_subprocess.Popen.assert_called_with("explorer.exe")
    # Should NOT call taskkill
    mock_subprocess.run.assert_not_called()
    # Should NOT call wait_procs
    mock_psutil.wait_procs.assert_not_called()

@patch('smartdesk.core.services.system_service.psutil')
@patch('smartdesk.core.services.system_service.subprocess')
@patch('smartdesk.core.services.system_service.time')
def test_restart_explorer_timeout(mock_time, mock_subprocess, mock_psutil):
    # Setup
    proc = MagicMock()
    proc.name.return_value = "explorer.exe"

    # Side effect for process_iter:
    # 1. Start: found explorer
    # 2. End: found explorer (restart success)
    mock_psutil.process_iter.side_effect = [[proc], [proc]]

    # wait_procs returns alive list (timeout)
    mock_psutil.wait_procs.return_value = ([], [proc])

    # Run
    restart_explorer()

    # Should still try to restart
    mock_subprocess.Popen.assert_called_with("explorer.exe")

    # wait_procs should have been called
    mock_psutil.wait_procs.assert_called()
