# Dateipfad: src/smartdesk/ui/cli.py
# (Vollständige Datei mit korrigiertem Import)

import os
import platform

# --- GEÄNDERT: Echte Imports statt Mocks ---
# Wir importieren die echten Handler aus den anderen Modulen.
# Die Pfade (z.B. '..') funktionieren, weil main.py
# das src-Verzeichnis zum sys.path hinzufügt.
try:
    from ..handlers import desktop_handler
    
    # --- KORREKTUR HIER ---
    # system_manager liegt (oder sollte) auch in handlers/ liegen
    from ..handlers import system_manager 
    # --- ENDE KORREKTUR ---

except ImportError as e:
    # Fallback, falls die Struktur leicht anders ist
    print(f"WARNUNG: Import-Fehler in cli.py: {e}")
    print("Prüfe Import-Pfade in cli.py")
    # Als Notlösung, damit das Skript nicht abstürzt
    class FakeHandler:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                print(f"FEHLER: {name} konnte nicht geladen werden!")
            return method
    desktop_handler = FakeHandler()
    system_manager = FakeHandler()
# --- Ende der geänderten Imports ---


def clear_screen():
    """
    Löscht den Terminal-Bildschirm, abhängig vom Betriebssystem.
    """
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
            # Ruft jetzt den echten Handler auf
            desktops = desktop_handler.get_all_desktops()
            if not desktops:
                print("Keine Desktops vorhanden.")
            else:
                print("\nVerfügbare Desktops:")
                for d in desktops:
                    # Greift auf die echten 'Desktop'-Objekte zu
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
                # Der echte Handler prüft den Pfad selbst (ensure_directory_exists)

            elif mode == "2":
                # 1.fragen nach Basis-Pfad
                parent_path = input(r"In welchem Verzeichnis soll der Ordner erstellt werden? (z.B. F:\SmartDesk): ").strip()
                
                if parent_path:
                    # 2. kombinieren Pfad mit  Desktop-Namen
                    final_path = os.path.join(parent_path, name)
                    print(f"Der neue Desktop wird hier erstellt: {final_path}")
                else:
                    # 3. Wenn kein Pfad angegeben, abbrechen
                    print("Fehler: Basis-Verzeichnis darf nicht leer sein.")
                    # final_path bleibt leer = Abbruch             
            else:
                print("Ungültige Auswahl.")
                input("\n--- Drücke Enter, um fortzufahren ---")
                continue

            if final_path:
                # Ruft jetzt den echten Handler auf
                desktop_handler.create_desktop(name, final_path)
            else:
                print("Vorgang abgebrochen (kein Pfad angegeben).")

        elif choice == "3":
            # Ruft jetzt den echten Handler auf
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
                    
                    if target_desktop.is_active:
                        print(f"'{target_desktop.name}' ist bereits aktiv.")
                    
                    # Ruft jetzt den echten Handler auf
                    elif desktop_handler.switch_to_desktop(target_desktop.name):
                        print(f"Erfolgreich zu '{target_desktop.name}' gewechselt.")
                        print("Registry aktualisiert. Explorer wird neu gestartet...")
                        # Ruft jetzt den echten SystemManager auf
                        system_manager.restart_explorer()
                else:
                    print("Ungültige Nummer.")
            except ValueError:
                print("Bitte eine gültige Zahl eingeben.")
        
        elif choice == "4":
            print("\nSpeichere aktuelle Icon-Positionen...")
            # Ruft die neue Funktion im echten Handler auf
            if desktop_handler.save_current_desktop_icons():
                print("Speichern abgeschlossen.")
            else:
                print("Speichern fehlgeschlagen. Siehe Meldung oben.")

        elif choice == "5": 
            print("Explorer wird manuell neu gestartet...")
            # Ruft jetzt den echten SystemManager auf
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
    