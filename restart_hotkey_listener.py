import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from smartdesk.hotkeys import hotkey_manager

if __name__ == "__main__":
    print("Restarting the hotkey listener...")
    hotkey_manager.restart_listener()
    print("Hotkey listener restarted.")
