import os
import time
# --- NEUE IMPORTS ---
from ..localization import get_text


def restart_explorer():
    """
    Startet den Windows Explorer Prozess neu.
    """
    # --- LOKALISIERT ---
    print(get_text("system.info.restarting"))

    # Beendet den Prozess
    os.system("taskkill /f /im explorer.exe")

    # Warten um Konflikte zu vermeiden
    time.sleep(2)

    # Startet den Prozess neu
    os.system("start explorer.exe")
    # --- LOKALISIERT ---
    print(get_text("system.info.restarted"))