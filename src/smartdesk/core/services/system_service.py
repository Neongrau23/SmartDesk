# Dateipfad: src/smartdesk/core/services/system_service.py

import subprocess
import time
import psutil
import os

from ...shared.localization import get_text


def restart_explorer():
    """
    Startet den Windows Explorer Prozess neu.
    Nutzt psutil für einen effizienten Prozess-Kill und prüft anschließend,
    ob Windows den Prozess automatisch neu startet.
    """
    print(get_text("system.info.restarting"))

    try:
        # Beende den Explorer via psutil (effizienter als PowerShell Subprozess)
        procs = []
        for p in psutil.process_iter(['name']):
            if p.name().lower() == 'explorer.exe':
                procs.append(p)
                try:
                    p.kill()
                except psutil.NoSuchProcess:
                    pass

        if procs:
            # Warte bis die Prozesse beendet sind
            psutil.wait_procs(procs, timeout=5)

        # Warte kurz und prüfe, ob Windows den Explorer selbstständig neu gestartet hat
        max_wait = 5
        start_check = time.time()
        restarted_by_system = False

        while time.time() - start_check < max_wait:
            time.sleep(0.5)
            if any(p.name().lower() == "explorer.exe" for p in psutil.process_iter(["name"])):
                restarted_by_system = True
                break

        if not restarted_by_system:
            # Fallback: Falls der Autostart von Windows deaktiviert ist, manuell starten
            subprocess.Popen("explorer.exe")

        print(get_text("system.info.restarted"))

    except Exception as e:
        print(get_text("system.error.restart_exception").format(error=str(e)))
        try:
            # Letzter Rettungsversuch
            subprocess.Popen("explorer.exe")
        except Exception:
            pass


def restart_explorer_simple():
    """
    Vereinfachte Version des Explorer-Neustarts.
    """
    print(get_text("system.info.restarting"))
    try:
        # Direkter Stop via PowerShell (schneller Einzeiler)
        subprocess.run(["powershell.exe", "-NoProfile", "-Command", "Stop-Process -Name explorer -Force"], capture_output=True)
        time.sleep(0.5)
        # Sicherstellen, dass er läuft
        if not any(p.name().lower() == "explorer.exe" for p in psutil.process_iter(["name"])):
            subprocess.Popen("explorer.exe")
        print(get_text("system.info.restarted"))
    except Exception:
        subprocess.Popen("explorer.exe")
