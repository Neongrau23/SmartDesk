import pytest
import os
import json
from unittest.mock import MagicMock, patch
from smartdesk.core.services.auto_switch_service import AutoSwitchService
from smartdesk.core.models.desktop import Desktop

# --- Fixtures ---

@pytest.fixture
def mock_psutil_service():
    """Mocks psutil imported in auto_switch_service."""
    with patch('smartdesk.core.services.auto_switch_service.psutil') as mock:
        yield mock

@pytest.fixture
def mock_desktop_service():
    """Mocks desktop_service imported in auto_switch_service."""
    with patch('smartdesk.core.services.auto_switch_service.desktop_service') as mock:
        yield mock

@pytest.fixture
def auto_switch_service(temp_data_dir, mock_psutil_service, mock_desktop_service):
    """Returns an instance of AutoSwitchService using a temp data dir."""
    # We need to patch RULES_FILE because it is defined at module level and might have been
    # imported with the original DATA_DIR value.
    rules_file = os.path.join(temp_data_dir, "rules.json")
    with patch('smartdesk.core.services.auto_switch_service.RULES_FILE', rules_file), \
         patch('smartdesk.core.services.auto_switch_service.settings_service') as mock_settings:

        # Mock settings to enable auto-switch by default for tests
        mock_settings.get_setting.return_value = True

        service = AutoSwitchService(check_interval=1)
        yield service
        service.stop()

# --- Tests ---

def test_load_rules_empty(auto_switch_service):
    """Test loading rules when file doesn't exist."""
    assert auto_switch_service.get_rules() == {}

def test_add_and_save_rule(auto_switch_service, temp_data_dir):
    """Test adding a rule and persistence."""
    auto_switch_service.add_rule("Notepad.exe", "Work")

    # Check in memory
    assert auto_switch_service.get_rules() == {"notepad.exe": "Work"}

    # Check file
    rules_file = os.path.join(temp_data_dir, "rules.json")
    with open(rules_file, 'r') as f:
        data = json.load(f)
    assert data == {"notepad.exe": "Work"}

def test_delete_rule(auto_switch_service, temp_data_dir):
    """Test deleting a rule."""
    auto_switch_service.add_rule("Steam.exe", "Gaming")
    assert "steam.exe" in auto_switch_service.get_rules()

    auto_switch_service.delete_rule("Steam.exe")
    assert "steam.exe" not in auto_switch_service.get_rules()

    # Check file
    rules_file = os.path.join(temp_data_dir, "rules.json")
    with open(rules_file, 'r') as f:
        data = json.load(f)
    assert data == {}

def test_load_existing_rules(temp_data_dir):
    """Test loading existing rules from file."""
    rules = {"vlc.exe": "Media", "code.exe": "Dev"}
    rules_file = os.path.join(temp_data_dir, "rules.json")
    with open(rules_file, 'w') as f:
        json.dump(rules, f)

    with patch('smartdesk.core.services.auto_switch_service.RULES_FILE', rules_file):
        service = AutoSwitchService()
        loaded_rules = service.get_rules()
        assert loaded_rules == rules

def test_check_and_switch_no_match(auto_switch_service, mock_psutil_service, mock_desktop_service):
    """Test that no switch happens if no rule matches."""
    # Setup desktops
    active_desktop = Desktop("Work", "path/to/work", is_active=True)
    other_desktop = Desktop("Gaming", "path/to/gaming", is_active=False)
    mock_desktop_service.get_all_desktops.return_value = [active_desktop, other_desktop]

    # Setup processes
    mock_proc = MagicMock()
    mock_proc.info = {'name': 'explorer.exe'}
    mock_psutil_service.process_iter.return_value = [mock_proc]

    # Add rule for something else
    auto_switch_service.add_rule("steam.exe", "Gaming")

    auto_switch_service._check_and_switch()

    mock_desktop_service.switch_to_desktop.assert_not_called()

def test_check_and_switch_match(auto_switch_service, mock_psutil_service, mock_desktop_service):
    """Test switch happens if rule matches and not on target desktop."""
    # Setup desktops
    active_desktop = Desktop("Work", "path/to/work", is_active=True)
    gaming_desktop = Desktop("Gaming", "path/to/gaming", is_active=False)
    mock_desktop_service.get_all_desktops.return_value = [active_desktop, gaming_desktop]

    # Setup processes
    mock_proc1 = MagicMock()
    mock_proc1.info = {'name': 'explorer.exe'}
    mock_proc2 = MagicMock()
    mock_proc2.info = {'name': 'steam.exe'}
    mock_psutil_service.process_iter.return_value = [mock_proc1, mock_proc2]

    # Add rule
    auto_switch_service.add_rule("Steam.exe", "Gaming")

    # Execute
    auto_switch_service._check_and_switch()

    mock_desktop_service.switch_to_desktop.assert_called_with("Gaming")

def test_check_and_switch_already_active(auto_switch_service, mock_psutil_service, mock_desktop_service):
    """Test no switch if already on target desktop."""
    # Setup desktops (Gaming is active)
    active_desktop = Desktop("Gaming", "path/to/gaming", is_active=True)
    work_desktop = Desktop("Work", "path/to/work", is_active=False)
    mock_desktop_service.get_all_desktops.return_value = [active_desktop, work_desktop]

    # Setup processes
    mock_proc = MagicMock()
    mock_proc.info = {'name': 'steam.exe'}
    mock_psutil_service.process_iter.return_value = [mock_proc]

    # Add rule
    auto_switch_service.add_rule("Steam.exe", "Gaming")

    # Execute
    auto_switch_service._check_and_switch()

    mock_desktop_service.switch_to_desktop.assert_not_called()

def test_cooldown(auto_switch_service, mock_psutil_service, mock_desktop_service):
    """Test that cooldown prevents immediate re-switch."""
    # Setup desktops
    active_desktop = Desktop("Work", "path/to/work", is_active=True)
    gaming_desktop = Desktop("Gaming", "path/to/gaming", is_active=False)
    mock_desktop_service.get_all_desktops.return_value = [active_desktop, gaming_desktop]
    mock_desktop_service.switch_to_desktop.return_value = True

    # Setup processes
    mock_proc = MagicMock()
    mock_proc.info = {'name': 'steam.exe'}
    mock_psutil_service.process_iter.return_value = [mock_proc]

    auto_switch_service.add_rule("Steam.exe", "Gaming")

    # First switch
    auto_switch_service._check_and_switch()
    assert mock_desktop_service.switch_to_desktop.call_count == 1

    # Second switch (immediate) - should be blocked by cooldown
    # Even if we pretend we switched back to Work manually (so we are on Work again)
    active_desktop.is_active = True # We are back on Work

    auto_switch_service._check_and_switch()
    assert mock_desktop_service.switch_to_desktop.call_count == 1 # Count should stay 1
