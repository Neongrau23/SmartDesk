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
        # Prüfe ob Explorer läuft
        explorer_running = any(
            p.name().lower() == "explorer.exe" for p in psutil.process_iter(['name'])
        )

        if not explorer_running:
            print(get_text("system.warning.explorer_not_running"))
            subprocess.Popen("explorer.exe")
            return

        # Beende Explorer
        for proc in psutil.process_iter(['name']):
            if proc.name().lower() == "explorer.exe":
                try:
                    proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        # Warte bis Explorer wirklich beendet ist
        timeout = 5
        start_time = time.time()
        while any(
            p.name().lower() == "explorer.exe" for p in psutil.process_iter(['name'])
        ):
            if time.time() - start_time > timeout:
                print(get_text("system.warning.explorer_timeout"))
                break
            time.sleep(0.1)

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
