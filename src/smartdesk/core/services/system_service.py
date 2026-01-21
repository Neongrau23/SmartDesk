# Dateipfad: src/smartdesk/core/services/system_service.py

import subprocess
import time
import psutil
import os

from ...shared.localization import get_text


def restart_explorer():
    """
    Startet den Windows Explorer Prozess neu.
    Nutzt Stop-Process, um Windows zum automatischen Neustart der Shell zu zwingen,
    was das Öffnen eines neuen Fensters verhindert.
    """
    print(get_text("system.info.restarting"))

    try:
        # Beende den Explorer via PowerShell.
        # Das löst unter Win 10/11 normalerweise einen automatischen, "stillen" Neustart der Shell aus.
        subprocess.run(["powershell.exe", "-NoProfile", "-Command", "Stop-Process -Name explorer -Force"], capture_output=True)

        # Warte kurz und prüfe, ob Windows den Explorer selbstständig neu gestartet hat
        max_wait = 5
        start_check = time.time()
        restarted_by_system = False

        while time.time() - start_check < max_wait:
            time.sleep(0.5)
            if any(p.name().lower() == "explorer.exe" for p in psutil.process_iter(["name"])):
                restarted_by_system = True
                break

        if restarted_by_system:
            print(get_text("system.info.restarted"))
            return

        # Fallback: Falls der Autostart von Windows deaktiviert ist, manuell starten
        print(get_text("system.warning.explorer_not_running"))
        subprocess.Popen("explorer.exe")

    except Exception as e:
        print(get_text("system.error.restart_exception").format(error=str(e)))
        try:
            # Letzter Rettungsversuch
            subprocess.Popen("explorer.exe")
        except Exception:
            pass


def restart_explorer_simple():
    """
    Vereinfachte Version, die ebenfalls den PowerShell-Weg nutzt.
    """
    print(get_text("system.info.restarting"))
    try:
        subprocess.run(["powershell.exe", "-NoProfile", "-Command", "Stop-Process -Name explorer -Force"], capture_output=True)
        time.sleep(1.0)
        print(get_text("system.info.restarted"))
    except Exception:
        # Fallback auf die alte Methode
        subprocess.Popen("explorer.exe", shell=True)
