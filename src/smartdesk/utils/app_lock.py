import os
import psutil
from ..shared.config import DATA_DIR

class AppLock:
    """
    Verwaltet eine Lock-Datei, um sicherzustellen, dass nur eine Instanz läuft.
    """
    def __init__(self, app_name="manager"):
        self.pid_file = os.path.join(DATA_DIR, f"{app_name}.lock")
        self.existing_pid = None

    def try_acquire(self) -> bool:
        """
        Versucht, den Lock zu setzen.
        Gibt True zurück, wenn erfolgreich (wir sind die einzige Instanz).
        Gibt False zurück, wenn bereits eine Instanz läuft (self.existing_pid ist gesetzt).
        """
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        pid = int(content)
                        
                        # Prüfen ob Prozess noch läuft
                        if psutil.pid_exists(pid):
                            self.existing_pid = pid
                            return False # Lock besetzt
                        else:
                            # Prozess tot, Lock übernehmen
                            pass
            except (ValueError, OSError):
                # Lock-Datei korrupt, überschreiben
                pass
        
        # Lock setzen
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except OSError:
            return False

    def release(self):
        """Entfernt die Lock-Datei."""
        try:
            if os.path.exists(self.pid_file):
                # Nur löschen wenn wir es auch sind (Safety Check)
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                if pid == os.getpid():
                    os.remove(self.pid_file)
        except (OSError, ValueError):
            pass
