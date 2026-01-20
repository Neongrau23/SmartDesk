import pytest
from unittest.mock import MagicMock, patch
from smartdesk.core.services.auto_switch_service import AutoSwitchService
from smartdesk.core.models.desktop import Desktop

@pytest.fixture
def mock_dependencies():
    with patch('smartdesk.core.services.auto_switch_service.psutil') as mock_psutil, \
         patch('smartdesk.core.services.auto_switch_service.desktop_service') as mock_desktop, \
         patch('smartdesk.core.services.auto_switch_service.settings_service') as mock_settings, \
         patch('smartdesk.core.services.auto_switch_service.RULES_FILE', 'dummy_rules.json'):

        mock_settings.get_setting.return_value = True
        yield mock_psutil, mock_desktop, mock_settings

def test_optimization_stops_early(mock_dependencies):
    """
    Verifies that the process iteration stops immediately after finding
    the highest priority rule process, without iterating the rest.
    """
    mock_psutil, mock_desktop, mock_settings = mock_dependencies

    # Setup service
    service = AutoSwitchService(check_interval=1)
    # Rule 1: high_prio.exe -> HighPrio (Top priority)
    service.add_rule("high_prio.exe", "HighPrio")
    # Rule 2: low_prio.exe -> LowPrio
    service.add_rule("low_prio.exe", "LowPrio")

    # Setup Desktops
    d1 = Desktop("HighPrio", "path/1", is_active=False)
    d2 = Desktop("LowPrio", "path/2", is_active=False)
    d3 = Desktop("Idle", "path/3", is_active=True)
    mock_desktop.get_all_desktops.return_value = [d1, d2, d3]
    mock_desktop.switch_to_desktop.return_value = True

    # Setup Process Generator
    def process_generator():
        # 1. Some random process
        p1 = MagicMock()
        p1.info = {'name': 'random.exe'}
        yield p1

        # 2. The high priority process!
        p2 = MagicMock()
        p2.info = {'name': 'high_prio.exe'}
        yield p2

        # 3. This should NOT be reached if optimization works
        raise RuntimeError("Optimization failed: Iterated too far!")

    mock_psutil.process_iter.side_effect = lambda attrs: process_generator()

    # Execute
    service._check_and_switch()

    # Verify switch happened
    mock_desktop.switch_to_desktop.assert_called_with("HighPrio")

def test_priority_logic_mixed_order(mock_dependencies):
    """
    Verifies that if a lower priority rule is matched first,
    we continue searching for a higher priority rule.
    """
    mock_psutil, mock_desktop, mock_settings = mock_dependencies

    service = AutoSwitchService(check_interval=1)
    # Rule 1: high_prio.exe -> HighPrio (Top priority)
    service.add_rule("high_prio.exe", "HighPrio")
    # Rule 2: low_prio.exe -> LowPrio
    service.add_rule("low_prio.exe", "LowPrio")

    d1 = Desktop("HighPrio", "path/1", is_active=False)
    d2 = Desktop("LowPrio", "path/2", is_active=False)
    d3 = Desktop("Idle", "path/3", is_active=True)
    mock_desktop.get_all_desktops.return_value = [d1, d2, d3]
    mock_desktop.switch_to_desktop.return_value = True

    # Process list where Low Prio appears BEFORE High Prio
    def process_generator():
        p1 = MagicMock()
        p1.info = {'name': 'low_prio.exe'}
        yield p1

        p2 = MagicMock()
        p2.info = {'name': 'random.exe'}
        yield p2

        p3 = MagicMock()
        p3.info = {'name': 'high_prio.exe'}
        yield p3

        # We can yield more, it doesn't matter, we should have found the winner.
        # But for this test, we just provide the data.

    mock_psutil.process_iter.side_effect = lambda attrs: process_generator()

    service._check_and_switch()

    # Should switch to HighPrio because it is first in rules, even if found later in process list
    mock_desktop.switch_to_desktop.assert_called_with("HighPrio")

def test_no_match_iterates_all(mock_dependencies):
    """
    Verifies that if no rule matches, we iterate everything (no crash).
    """
    mock_psutil, mock_desktop, mock_settings = mock_dependencies

    service = AutoSwitchService(check_interval=1)
    service.add_rule("target.exe", "Target")

    mock_desktop.get_all_desktops.return_value = [Desktop("Idle", "p", is_active=True)]

    def process_generator():
        yield MagicMock(info={'name': 'p1.exe'})
        yield MagicMock(info={'name': 'p2.exe'})

    mock_psutil.process_iter.side_effect = lambda attrs: process_generator()

    service._check_and_switch()

    mock_desktop.switch_to_desktop.assert_not_called()
