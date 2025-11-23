import os
import time
from ..localization import get_text # <-- NEUER IMPORT


def restart_explorer():
    """
    Startet den Windows Explorer Prozess neu.
    """
    # --- LOKALISIERT ---
    print(get_text("system.info.restarting"))

    os.system("taskkill /f /im explorer.exe")

    time.sleep(2)

    os.system("start explorer.exe")
    # --- LOKALISIERT ---
    print(get_text("system.info.restarted"))
    