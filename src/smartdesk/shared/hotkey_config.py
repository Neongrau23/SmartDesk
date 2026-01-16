import json
import os
import logging
from typing import Dict
from .config import DATA_DIR

# Logger konfigurieren, falls noch nicht geschehen
logger = logging.getLogger(__name__)

class HotkeyConfig:
    """
    Verwaltet die Hotkey-Konfiguration für SmartDesk.
    Liest und schreibt die 'config.json' im DATA_DIR.

    Anleitung für Benutzer zum Hinzufügen neuer Tasten:
    1. Öffnen Sie die Datei 'config.json' im SmartDesk-Datenverzeichnis (%APPDATA%\SmartDesk).
    2. Fügen Sie im Abschnitt "hotkeys" einen neuen Eintrag hinzu.
       Beispiel: "f1": "switch_1"
       Dies würde F1 als Hotkey für Desktop 1 festlegen.
    3. Starten Sie die Anwendung neu.

    Verfügbare Aktionen:
    - switch_1 bis switch_9: Wechselt zum jeweiligen Desktop.
    - save_icons: Speichert die aktuelle Icon-Position.
    """

    CONFIG_FILENAME = "config.json"

    # Standard-Belegung: Tasten 1-8 für Desktop-Wechsel, 9 für Speichern
    DEFAULT_HOTKEYS = {
        "1": "switch_1",
        "2": "switch_2",
        "3": "switch_3",
        "4": "switch_4",
        "5": "switch_5",
        "6": "switch_6",
        "7": "switch_7",
        "8": "switch_8",
        "9": "save_icons"
    }

    def __init__(self):
        self.config_path = os.path.join(DATA_DIR, self.CONFIG_FILENAME)
        self.hotkeys: Dict[str, str] = self.DEFAULT_HOTKEYS.copy()
        self.load_config()

    def load_config(self):
        """Liest die Konfiguration aus der JSON-Datei."""
        if not os.path.exists(self.config_path):
            # Datei existiert nicht -> Defaults schreiben
            logger.info(f"Konfigurationsdatei nicht gefunden. Erstelle Standardwerte in {self.config_path}")
            self.save_config()
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if "hotkeys" in data and isinstance(data["hotkeys"], dict):
                # Konfiguration erfolgreich geladen
                self.hotkeys = data["hotkeys"]
                logger.info("Hotkey-Konfiguration erfolgreich geladen.")
            else:
                logger.warning(f"Ungültige Struktur in {self.config_path}. Verwende Standardwerte.")
                # Wir überschreiben die Datei hier NICHT, um Datenverlust zu vermeiden,
                # falls der User nur einen Tippfehler hat.

        except json.JSONDecodeError as e:
            logger.error(f"JSON-Fehler in {self.config_path}: {e}. Verwende Standardwerte.")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {e}. Verwende Standardwerte.")

    def save_config(self):
        """Speichert die aktuelle Konfiguration in die JSON-Datei."""
        try:
            data = {"hotkeys": self.hotkeys}
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Konfiguration gespeichert: {self.config_path}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")

    def get_hotkeys(self) -> Dict[str, str]:
        """Gibt das Dictionary der Tastenbelegungen zurück."""
        return self.hotkeys
