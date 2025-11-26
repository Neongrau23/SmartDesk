# -*- coding: utf-8 -*-
"""
Stellt Werte aus einer JSON-Sicherungsdatei im 
'User Shell Folders'-Registrierungsschlüssel und das Hintergrundbild wieder her.
"""
import winreg
import json
import os
import sys
import ctypes
from ctypes import wintypes

def set_wallpaper_api(image_path):
    """
    Setzt das Desktop-Hintergrundbild mithilfe der Windows-API.
    Dies ist zuverlässiger als der RUNDLL32-Befehl.
    """
    try:
        SPI_SETDESKWALLPAPER = 20
        SPIF_UPDATEINIFILE = 1
        SPIF_SENDWININICHANGE = 2

        # Prüfen, ob der Pfad überhaupt existiert
        if not os.path.exists(image_path):
            print(f"API-Warnung: Bildpfad nicht gefunden: {image_path}", file=sys.stderr)
            print("Hintergrundbild kann nicht gesetzt werden, da die Datei fehlt.", file=sys.stderr)
            return

        # Konvertiert den Python-String in einen C-String (Wide-String für Unicode)
        image_path_wide = ctypes.c_wchar_p(image_path)
        
        # Ruft die Windows-API-Funktion auf
        success = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            image_path_wide,
            SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
        )
        if success:
            print("Windows-API-Aufruf zum Setzen des Hintergrundbilds war erfolgreich.")
        else:
            print("Windows-API-Aufruf zum Setzen des Hintergrundbilds meldete einen Fehler.", file=sys.stderr)
            
    except Exception as e:
        print(f"Fehler beim Setzen des Hintergrundbilds via API: {e}", file=sys.stderr)

def restore_registry_paths():
    """
    Hauptfunktion zum Wiederherstellen der Registry-Pfade.
    """
    try:
        # --- Konfiguration ---
        
        # Pfad 1: User Shell Folders
        REG_PATH_SHELL = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        # Pfad 2: Desktop-Einstellungen (für Hintergrundbild)
        REG_PATH_DESKTOP = r"Control Panel\Desktop"
        
        REG_KEY = winreg.HKEY_CURRENT_USER

        # Der Pfad zur Sicherungsdatei (NEUER NAME)
        backup_dir = os.path.join(os.environ.get('APPDATA', ''), 'SmartDesk')
        backup_file = os.path.join(backup_dir, 'registry_paths_backup.json')

        # --- Sicherheitsabfrage ---
        
        print(f"WARNUNG: Dieses Skript wird Werte in der Windows-Registry ändern.")
        print(f"Betroffene Pfade:")
        print(f"1. HKEY_CURRENT_USER\\{REG_PATH_SHELL}")
        print(f"2. HKEY_CURRENT_USER\\{REG_PATH_DESKTOP}")

        confirmation = input(f"\nMöchten Sie die Wiederherstellung aus {backup_file} wirklich starten? (ja / nein): ")

        if confirmation.lower() != 'ja':
            print("Vorgang vom Benutzer abgebrochen.")
            return

        # --- Skriptlogik ---

        # 1. Prüfen, ob die Sicherungsdatei existiert
        if not os.path.exists(backup_file):
            print(f"Fehler: Sicherungsdatei nicht gefunden: {backup_file}", file=sys.stderr)
            return

        # 2. JSON-Datei lesen und konvertieren
        print(f"Lese Sicherungsdatei: {backup_file}")
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # 3. User Shell Folders wiederherstellen
        if "UserShellFolders" in backup_data and backup_data["UserShellFolders"]:
            print(f"\nStarte Wiederherstellung von {len(backup_data['UserShellFolders'])} 'User Shell Folders' Werten...")
            try:
                with winreg.OpenKey(REG_KEY, REG_PATH_SHELL, 0, winreg.KEY_WRITE) as key:
                    for name, data in backup_data["UserShellFolders"].items():
                        value = data['value']
                        type_id = data['type']
                        try:
                            print(f"Setze Wert: {name} (Typ: {type_id})")
                            winreg.SetValueEx(key, name, 0, type_id, value)
                        except Exception as e:
                            print(f"  Konnte Wert '{name}' nicht setzen: {e}", file=sys.stderr)
            except FileNotFoundError:
                 print(f"Fehler: Pfad {REG_PATH_SHELL} nicht gefunden.", file=sys.stderr)
        else:
            print("\nKeine 'UserShellFolders'-Daten in der Sicherung gefunden. Überspringe.")

        # 4. Desktop-Hintergrundbild wiederherstellen
        if "DesktopWallpaper" in backup_data and backup_data["DesktopWallpaper"]:
            print(f"\nStarte Wiederherstellung von {len(backup_data['DesktopWallpaper'])} 'Desktop' Werten (Hintergrundbild)...")
            wallpaper_path_to_set = None
            try:
                with winreg.OpenKey(REG_KEY, REG_PATH_DESKTOP, 0, winreg.KEY_WRITE) as key:
                    for name, data in backup_data["DesktopWallpaper"].items():
                        value = data['value']
                        type_id = data['type']
                        try:
                            print(f"Setze Registrierungswert: {name} (Typ: {type_id})")
                            winreg.SetValueEx(key, name, 0, type_id, value)
                            
                            # Speichern des Pfads für den API-Aufruf
                            if name.lower() == 'wallpaper':
                                wallpaper_path_to_set = value
                                
                        except Exception as e:
                            print(f"  Konnte Wert '{name}' nicht setzen: {e}", file=sys.stderr)
                
                # API-Aufruf NACHDEM die Registry geschrieben wurde
                if wallpaper_path_to_set:
                    print(f"Versuche, Hintergrundbild direkt via API zu setzen auf: {wallpaper_path_to_set}")
                    set_wallpaper_api(wallpaper_path_to_set) # Neuer API-Aufruf
                
            except FileNotFoundError:
                 print(f"Fehler: Pfad {REG_PATH_DESKTOP} nicht gefunden.", file=sys.stderr)
        else:
            print("\nKeine 'DesktopWallpaper'-Daten in der Sicherung gefunden. Überspringe.")


        print("--------------------------------------------------")
        print("Wiederherstellung erfolgreich abgeschlossen!")
        
        # Änderungen werden automatisch angewendet (Systemaktualisierung und Explorer-Neustart)
        print("\nDamit die 'User Shell Folders' (Ordnerpfade) wirksam werden,")
        print("wird der Explorer jetzt neu gestartet.")
        
        print("Starte Explorer neu...")
        try:
            # HINWEIS: RUNDLL32.EXE wurde entfernt, da set_wallpaper_api() dies bereits erledigt.
            
            # 1. Explorer-Prozess beenden
            os.system("taskkill /f /im explorer.exe")
            
            # 2. Explorer-Prozess neu starten
            os.system("start explorer.exe")
            
            print("Explorer-Neustart wurde ausgeführt.")
        except Exception as e:
            print(f"Fehler beim Anwenden der Änderungen: {e}", file=sys.stderr)
            print("Bitte melden Sie sich manuell ab und wieder an, um die Änderungen zu sehen.")

        print("--------------------------------------------------")

    except FileNotFoundError:
        print(f"Fehler: Ein wichtiger Registrierungspfad wurde nicht gefunden.", file=sys.stderr)
    except Exception as e:
        # Fehlerbehandlung
        print(f"Ein schwerwiegender Fehler ist aufgetreten: {e}", file=sys.stderr)

if __name__ == "__main__":
    restore_registry_paths()