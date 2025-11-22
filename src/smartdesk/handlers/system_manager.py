import os
import time


def restart_explorer():
    """
    Startet den Windows Explorer Prozess neu.
    """
    print("[SYSTEM] Starte Windows Explorer neu...")

    # Beendet den Prozess
    os.system("taskkill /f /im explorer.exe")

    # Warten um Konflikte zu vermeiden
    time.sleep(2)

    # Startet den Prozess neu
    os.system("start explorer.exe")
    print("[SYSTEM] Explorer neu gestartet.")
