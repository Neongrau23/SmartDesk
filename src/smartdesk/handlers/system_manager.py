import subprocess
import time  # <- Korrigiert
import psutil
from ..localization import get_text


def restart_explorer():
    """
    Startet den Windows Explorer Prozess neu.
    Verwendet subprocess statt os.system für bessere Kontrolle und Fehlerbehandlung.
    """
    print(get_text("system.info.restarting"))
    
    try:
        # Prüfe ob Explorer läuft
        explorer_running = any(p.name().lower() == "explorer.exe" for p in psutil.process_iter(['name']))
        
        if not explorer_running:
            print(get_text("system.warning.explorer_not_running"))
            subprocess.Popen("explorer.exe")
            return
        
        # Beende Explorer (subprocess.run für bessere Kontrolle)
        subprocess.run(
            ["taskkill", "/F", "/IM", "explorer.exe"],
            capture_output=True,
            check=False  # Kein Fehler wenn Prozess nicht existiert
        )
        
        # Warte bis Explorer wirklich beendet ist
        timeout = 5  # <- Korrigiert
        start_time = time.time()  # <- Korrigiert
        while any(p.name().lower() == "explorer.exe" for p in psutil.process_iter(['name'])):
            if time.time() - start_time > timeout:  # <- Korrigiert
                print(get_text("system.warning.explorer_timeout"))  # <- Korrigiert von out
                break
            time.sleep(0.1)  # <- Korrigiert
        
        # Zusätzliche kurze Pause für Systemstabilität
        time.sleep(0.5)  # <- Korrigiert
        
        # Starte Explorer neu
        subprocess.Popen("explorer.exe")
        
        # Warte kurz und prüfe ob Explorer gestartet ist
        time.sleep(1)  # <- Korrigiert
        if any(p.name().lower() == "explorer.exe" for p in psutil.process_iter(['name'])):
            print(get_text("system.info.restarted"))
        else:
            print(get_text("system.error.restart_failed"))
            
    except Exception as e:
        print(get_text("system.error.restart_exception").format(error=str(e)))
        # Notfall-Neustart
        try:
            subprocess.Popen("explorer.exe")
        except:
            pass


def restart_explorer_simple():
    """
    Vereinfachte Version ohne psutil-Abhängigkeit.
    Gut für minimale Abhängigkeiten.
    """
    print(get_text("system.info.restarting"))
    
    try:
        # Beende Explorer
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "explorer.exe"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Prüfe ob taskkill erfolgreich war
        if result.returncode != 0 and "not found" not in result.stderr.lower():
            print(get_text("system.warning.kill_failed"))
        
        # Warte auf sauberes Beenden
        time.sleep(0.8)  # <- Korrigiert
        
        # Starte Explorer neu
        subprocess.Popen("explorer.exe", shell=True)
        
        # Kurze Pause zum Überprüfen
        time.sleep(0.5)  # <- Korrigiert
        
        print(get_text("system.info.restarted"))
        
    except Exception as e:
        print(get_text("system.error.restart_exception").format(error=str(e)))
        # Notfall-Versuch
        try:
            subprocess.Popen("explorer.exe", shell=True)
        except:
            pass


def restart_explorer_powershell():
    """
    PowerShell-basierte Version für maximale Zuverlässigkeit.
    """
    print(get_text("system.info.restarting"))
    
    try:
        # PowerShell-Befehl mit Fehlerbehandlung
        ps_command = """
        Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 800
        Start-Process explorer.exe
        """
        
        subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            check=False
        )
        
        print(get_text("system.info.restarted"))
        
    except Exception as e:
        print(get_text("system.error.restart_exception").format(error=str(e)))