import pytest
from unittest.mock import MagicMock, patch
from smartdesk.core.services.system_service import restart_explorer

@patch('smartdesk.core.services.system_service.psutil')
@patch('smartdesk.core.services.system_service.subprocess')
@patch('smartdesk.core.services.system_service.time')
def test_restart_explorer_uses_wait_procs(mock_time, mock_subprocess, mock_psutil):
    """
    Verifies that restart_explorer uses psutil.wait_procs instead of polling.
    """
    # Setup mocks
    proc = MagicMock()
    proc.name.return_value = "explorer.exe"

    # process_iter returns our mock process (first call only, or always)
    # The code calls process_iter twice:
    # 1. To find/kill: [proc]
    # 2. To check if restarted: [proc]
    mock_psutil.process_iter.side_effect = [[proc], [proc]]

    # wait_procs returns empty list (all gone)
    mock_psutil.wait_procs.return_value = ([], [])

    # Run the function
    restart_explorer()

    # Verification
    # process_iter should be called at least once
    assert mock_psutil.process_iter.called

    # process.kill() should be called
    proc.kill.assert_called_once()

    # wait_procs should be called
    mock_psutil.wait_procs.assert_called_once_with([proc], timeout=5)

    # check that subprocess.run was NOT called with taskkill
    for call in mock_subprocess.run.call_args_list:
        args, _ = call
        if args and "taskkill" in args[0]:
            pytest.fail("subprocess.run called with taskkill! Optimization not effective.")
