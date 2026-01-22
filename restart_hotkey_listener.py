import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from smartdesk.hotkeys import hotkey_manager
from smartdesk.shared.localization import get_text

if __name__ == "__main__":
    print(get_text("scripts.restart_listener.starting"))
    hotkey_manager.restart_listener()
    print(get_text("scripts.restart_listener.done"))
