# Dateipfad: src/smartdesk/core/services/system_service.py

import subprocess
import time
import psutil

from ...shared.localization import get_text


def restart_explorer():
    """
    Startet den Windows Explorer Prozess neu.
    """
    print(get_text("system.info.restarting"))

    try:
        # Finde und sammle alle Explorer Prozesse
        explorer_procs = [
            p for p in psutil.process_iter(['name']) if p.name().lower() == "explorer.exe"
        ]

        if not explorer_procs:
            print(get_text("system.warning.explorer_not_running"))
            subprocess.Popen("explorer.exe")
            return

        # Beende Explorer
        for p in explorer_procs:
            try:
                p.kill()
            except psutil.NoSuchProcess:
                pass
        
        # Warte bis Explorer wirklich beendet ist
        gone, alive = psutil.wait_procs(explorer_procs, timeout=5)

        if alive:
            print(get_text("system.warning.explorer_timeout"))

        # Zusätzliche kurze Pause für Systemstabilität
        time.sleep(0.5)

        # Starte Explorer neu
        subprocess.Popen("explorer.exe")

        # Warte kurz und prüfe ob Explorer gestartet ist
        time.sleep(1)
        if any(
            p.name().lower() == "explorer.exe" for p in psutil.process_iter(['name'])
        ):
            print(get_text("system.info.restarted"))
        else:
            print(get_text("system.error.restart_failed"))

    except Exception as e:
        print(get_text("system.error.restart_exception").format(error=str(e)))
        try:
            subprocess.Popen("explorer.exe")
        except Exception:
            pass


def restart_explorer_simple():
    """
    Vereinfachte Version ohne psutil-Abhängigkeit.
    """
    print(get_text("system.info.restarting"))

    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "explorer.exe"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0 and "not found" not in result.stderr.lower():
            print(get_text("system.warning.kill_failed"))

        time.sleep(0.8)
        subprocess.Popen("explorer.exe", shell=True)
        time.sleep(0.5)
        print(get_text("system.info.restarted"))

    except Exception as e:
        print(get_text("system.error.restart_exception").format(error=str(e)))
        try:
            subprocess.Popen("explorer.exe", shell=True)
        except Exception:
            pass
