# -*- coding: utf-8 -*-
"""
Sichert alle Werte aus dem 'User Shell Folders'-Registrierungsschlüssel
sowie das aktuelle Desktop-Hintergrundbild in eine JSON-Datei.
"""
import winreg
import json
import os
import sys

def backup_registry_paths():
    """
    Hauptfunktion zum Sichern der Registry-Pfade.
    """
    try:
        # --- Konfiguration ---

        # Pfad 1: User Shell Folders
        REG_PATH_SHELL = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        
        # Pfad 2: Desktop-Einstellungen (für Hintergrundbild)
        REG_PATH_DESKTOP = r"Control Panel\Desktop"
        
        REG_KEY = winreg.HKEY_CURRENT_USER

        # Der Zielordner für die Sicherung
        # os.environ['APPDATA'] verweist auf C:\Users\<IhrName>\AppData\Roaming
        backup_dir = os.path.join(os.environ.get('APPDATA', ''), 'SmartDesk')
        
        # Der vollständige Dateipfad für die Sicherungs-JSON
        backup_file = os.path.join(backup_dir, 'registry_paths_backup.json')

        # --- Skriptlogik ---
        
        # 1. Sicherstellen, dass das Backup-Verzeichnis existiert
        if not os.path.exists(backup_dir):
            print(f"Erstelle Backup-Verzeichnis: {backup_dir}")
            os.makedirs(backup_dir, exist_ok=True)

        # 2. NEUE PRÜFUNG: Verhindern des Überschreibens
        if os.path.exists(backup_file):
            print("--------------------------------------------------")
            print(f"FEHLER: Sicherungsdatei existiert bereits:")
            print(f"{backup_file}")
            print("Die Datei wird NICHT überschrieben. Breche ab.")
            print("--------------------------------------------------")
            return # Stoppt die Funktion hier

        print("Starte Sicherung (Backup-Datei existiert noch nicht)...")

        # Haupt-Datenobjekt, das beide Bereiche speichert
        main_backup_data = {
            "UserShellFolders": {},
            "DesktopWallpaper": {}
        }

        # 3. User Shell Folders auslesen
        print(f"Lese: HKEY_CURRENT_USER\\{REG_PATH_SHELL}")
        try:
            with winreg.OpenKey(REG_KEY, REG_PATH_SHELL, 0, winreg.KEY_READ) as key:
                num_values = winreg.QueryInfoKey(key)[1]
                for i in range(num_values):
                    name, value, type_id = winreg.EnumValue(key, i)
                    main_backup_data["UserShellFolders"][name] = {
                        "value": value,
                        "type": type_id 
                    }
        except FileNotFoundError:
            print(f"Warnung: Pfad {REG_PATH_SHELL} nicht gefunden. Überspringe.")

        # 4. Desktop-Hintergrundbild auslesen
        print(f"Lese: HKEY_CURRENT_USER\\{REG_PATH_DESKTOP}")
        try:
            with winreg.OpenKey(REG_KEY, REG_PATH_DESKTOP, 0, winreg.KEY_READ) as key:
                # Wir holen nur den einen spezifischen Wert 'Wallpaper'
                name = "Wallpaper"
                value, type_id = winreg.QueryValueEx(key, name)
                main_backup_data["DesktopWallpaper"][name] = {
                    "value": value,
                    "type": type_id
                }
        except FileNotFoundError:
            print(f"Warnung: Pfad {REG_PATH_DESKTOP} oder Wert 'Wallpaper' nicht gefunden. Überspringe.")
        except Exception as e:
            print(f"Warnung beim Lesen des Hintergrundbilds: {e}")


        # 5. Daten in JSON konvertieren und in die Datei schreiben
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(main_backup_data, f, indent=4, ensure_ascii=False)

        print("--------------------------------------------------")
        print("Sicherung erfolgreich abgeschlossen!")
        print(f"Gespeichert in: {backup_file}")
        print(f"Insgesamt {len(main_backup_data['UserShellFolders'])} Shell-Werte und {len(main_backup_data['DesktopWallpaper'])} Desktop-Werte gesichert.")
        print("--------------------------------------------------")

    except Exception as e:
        # Fehlerbehandlung
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}", file=sys.stderr)

if __name__ == "__main__":
    backup_registry_paths()