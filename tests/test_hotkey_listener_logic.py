import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Adjust path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock pynput BEFORE importing listener
mock_pynput = MagicMock()
sys.modules['pynput'] = mock_pynput
sys.modules['pynput.keyboard'] = mock_pynput

# Define mock classes for pynput
class MockListener:
    def __init__(self, on_press=None, on_release=None):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def join(self):
        pass

mock_pynput.Listener = MockListener
mock_pynput.Key = MagicMock()
mock_pynput.KeyCode = MagicMock()

# Now we can import listener
from smartdesk.hotkeys import listener

def test_controller_synchronization_fix():
    """
    Test that the listener re-arms the controller before triggering HOLDING,
    handling cases where the controller might have timed out or reset.
    """
    # Setup state
    listener.wait_state = "WAITING_FOR_ACTION"
    listener.action_key_used_after_activation = False

    # Mock dependencies
    mock_ctrl = MagicMock()
    listener._banner_controller = mock_ctrl

    # Mock helpers
    with patch('smartdesk.hotkeys.listener.is_action_key', return_value=True), \
         patch('smartdesk.hotkeys.listener.is_any_action_key_held', return_value=False), \
         patch('smartdesk.hotkeys.listener.is_part_of_activation', return_value=False), \
         patch('smartdesk.hotkeys.listener.get_registry') as mock_registry:

        # Setup registry mock
        mock_reg_instance = MagicMock()
        mock_registry.return_value = mock_reg_instance
        mock_reg_instance.has_hold_action.return_value = False
        mock_reg_instance.has_combo_action.return_value = False

        # Action: Press the action key
        key_mock = MagicMock()
        listener.on_press(key_mock)

        # Verification
        assert mock_ctrl.on_ctrl_shift_triggered.called, "Should ensure controller is ARMED"
        assert mock_ctrl.on_alt_pressed.called, "Should trigger HOLDING"

        # Verify order
        calls = mock_ctrl.method_calls
        relevant_calls = [c[0] for c in calls if c[0] in ('on_ctrl_shift_triggered', 'on_alt_pressed')]

        assert relevant_calls == ['on_ctrl_shift_triggered', 'on_alt_pressed'], \
            f"Expected call order [ARMED, HOLDING], but got {relevant_calls}"
