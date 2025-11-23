# Dateipfad: src/smartdesk/ui/cli.py
# (Vollständig aktualisiert, um deine 7-Schritt-Logik aufzurufen)

import os
import platform
import time  # <--- NEUER IMPORT

# --- Imports (unverändert) ---
try:
    from ..handlers import desktop_handler
    from ..handlers import system_manager
except ImportError as e:
    print(f"WARNUNG: Import-Fehler in cli.py: {e}")
    print("Prüfe Import-Pfade in cli.py")
    class FakeHandler:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                print(f"FEHLER: {name} konnte nicht geladen werden!")
            return method
    desktop_handler = FakeHandler()
    system_manager = FakeHandler()
# --- Ende Imports ---


def clear_screen():
    """Löscht den Terminal-Bildschirm, abhängig vom Betriebssystem."""
    system_name = platform.system()
    
    if system_name == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def print_menu():
    print("\n--- SmartDesk Manager ---")
    print("1. Alle Desktops anzeigen")
    print("2. Neuen Desktop erstellen")
    print("3. Desktop wechseln (Auswahl per Nummer)")
    print("4. Aktuelle Icon-Positionen speichern") 
    print("5. Explorer manuell neu starten")       
    print("6. Beenden")                           

def run():
    while True:
        clear_screen()
        
        print_menu()
        choice = input("\nBitte wählen: ")

        if choice == "1":
            desktops = desktop_handler.get_all_desktops()
            if not desktops:
                print("Keine Desktops vorhanden.")
            else:
                print("\nVerfügbare Desktops:")
                for d in desktops:
                    status = "[AKTIV]" if d.is_active else "[ ]"
                    print(f"{status} {d.name} -> {d.path}")

        elif choice == "2":
            print("\n--- Neuen Desktop anlegen ---")
            name = input("Name des neuen Desktops: ").strip()
            
            if not name:
                print("Fehler: Der Name darf nicht leer sein.")
                input("\n--- Drücke Enter, um fortzufahren ---")
                continue

            print("\nWie soll der Ordner gewählt werden?")
            print("1. Einen existierenden Ordner verwenden")
            print("2. Einen neuen Ordner erstellen")
            
            mode = input("Auswahl (1/2): ").strip()
            final_path = ""

            if mode == "1":
                final_path = input(r"Bitte vollen Pfad eingeben (z.B. F:\SmartDesk\Work): ").strip()

            elif mode == "2":
                parent_path = input(r"In welchem Verzeichnis soll der Ordner erstellt werden? (z.B. F:\SmartDesk): ").strip()
                
                if parent_path:
                    final_path = os.path.join(parent_path, name)
                    print(f"Der neue Desktop wird hier erstellt: {final_path}")
                else:
                    print("Fehler: Basis-Verzeichnis darf nicht leer sein.")
            else:
                print("Ungültige Auswahl.")
                input("\n--- Drücke Enter, um fortzufahren ---")
                continue

            if final_path:
                desktop_handler.create_desktop(name, final_path)
            else:
                print("Vorgang abgebrochen (kein Pfad angegeben).")

        # --- BLOCK FÜR SCHRITT 3 STARK GEÄNDERT ---
        elif choice == "3":
            desktops = desktop_handler.get_all_desktops()
            
            if not desktops:
                print("Keine Desktops vorhanden. Bitte erstelle zuerst einen.")
                input("\n--- Drücke Enter, um fortzufahren ---")
                continue

            print("\n--- Zu welchem Desktop wechseln? ---")
            for i, d in enumerate(desktops, 1):
                status = "[AKTIV]" if d.is_active else "[    ]"
                print(f"{i}. {status} {d.name} ({d.path})")
            
            print("0. Abbrechen")
            selection = input("\nNummer eingeben: ").strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1
                
                if 0 <= index < len(desktops):
                    target_desktop = desktops[index]
                    
                    # (Schritt 1 & 2: Alte Icons speichern, Registry ändern)
                    # die 'switch_to_desktop' gibt False zurück, wenn Desktop schon aktiv ist
                    if desktop_handler.switch_to_desktop(target_desktop.name):
                        
                        # (Schritt 3: Explorer neu starten)
                        print(f"Registry erfolgreich auf '{target_desktop.name}' gesetzt.")
                        print("Starte Explorer neu, um Änderungen anzuwenden...")
                        system_manager.restart_explorer()
                        
                        print("Explorer wurde neu gestartet. Warte 3 Sekunden auf Initialisierung...")
                        time.sleep(1) # Kurze Pause, damit Windows den Desktop "laden" kann

                        # (Schritt 4, 5, 6, 7: Sync & Icons wiederherstellen)
                        print("Synchronisiere Status und stelle Icons wieder her...")
                        desktop_handler.sync_desktop_state_and_apply_icons()
                        print(f"Wechsel zu '{target_desktop.name}' abgeschlossen.")
                        
                    else:
                        # Fehler oder "bereits aktiv" wurde im Handler gedruckt
                        pass
                else:
                    print("Ungültige Nummer.")
            except ValueError:
                print("Bitte eine gültige Zahl eingeben.")
        # --- ENDE ÄNDERUNG ---
        
        elif choice == "4":
            print("\nSpeichere aktuelle Icon-Positionen...")
            if desktop_handler.save_current_desktop_icons():
                print("Speichern abgeschlossen.")
            else:
                print("Speichern fehlgeschlagen. Siehe Meldung oben.")

        elif choice == "5":
            print("Explorer wird manuell neu gestartet...")
            system_manager.restart_explorer()
            print("Explorer wurde neu gestartet.")

        elif choice == "6":
            print("Auf Wiedersehen!")
            break
        else:
            print("Ungültige Eingabe.")
            
        input("\n--- Drücke Enter, um fortzufahren ---")

# --- Start des Skripts ---
if __name__ == "__main__":
    clear_screen()
    run()
