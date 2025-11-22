import os
import platform 
class Desktop:
    def __init__(self, name, path, is_active=False):
        self.name = name
        self.path = path
        self.is_active = is_active

class MockDesktopHandler:
    def __init__(self):
        self._desktops = [
            Desktop("Standard", "C:\\Users\\Default\\Desktop", is_active=True),
            Desktop("Work", "F:\\SmartDesk\\Work", is_active=False)
        ]
    
    def get_all_desktops(self):
        print("[Handler] Rufe get_all_desktops auf...")
        return self._desktops
    
    def create_desktop(self, name, path):
        print(f"[Handler] Erstelle Desktop '{name}' unter '{path}'...")
        new_desktop = Desktop(name, path)
        self._desktops.append(new_desktop)
        print("-> Desktop erstellt.")
    
    def switch_to_desktop(self, name):
        print(f"[Handler] Wechsle zu Desktop '{name}'...")
        active_desktop = None
        target_desktop = None
        for d in self._desktops:
            if d.is_active:
                active_desktop = d
            if d.name == name:
                target_desktop = d
        
        if target_desktop and active_desktop:
            active_desktop.is_active = False
            target_desktop.is_active = True
            print(f"-> Aktiv: {target_desktop.name}")
            return True
        return False

class MockSystemManager:
    def restart_explorer(self):
        print("[System] Starte Explorer neu...")
        # In einer echten Anwendung würde hier z.B. os.system('taskkill ...') stehen
        print("-> Explorer neu gestartet.")

# Ersetze die echten Imports mit den Mock-Objekten
desktop_handler = MockDesktopHandler()
system_manager = MockSystemManager()
# --- Ende des Platzhalter-Blocks ---


def clear_screen():
    """
    Löscht den Terminal-Bildschirm, abhängig vom Betriebssystem.
    """
    # Ruft das Betriebssystem ab (z.B. "Windows", "Linux", "Darwin" für macOS)
    system_name = platform.system()
    
    if system_name == "Windows":
        # Der Befehl für Windows
        os.system('cls')
    else:
        # Der Befehl für Linux und macOS
        os.system('clear')

def print_menu():
    print("\n--- SmartDesk Manager ---")
    print("1. Alle Desktops anzeigen")
    print("2. Neuen Desktop erstellen")
    print("3. Desktop wechseln (Auswahl per Nummer)")
    print("4. Explorer manuell neu starten")
    print("5. Beenden")

def run():
    while True:
        # 1. Bildschirm löschen
        # Dies geschieht jetzt VOR dem Anzeigen des Menüs
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
                    status = "[AKTIV]" if d.is_active else "[    ]"
                    print(f"{status} {d.name} -> {d.path}")

        elif choice == "2":
            print("\n--- Neuen Desktop anlegen ---")
            name = input("Name des neuen Desktops: ").strip()
            
            if not name:
                print("Fehler: Der Name darf nicht leer sein.")
                # 'continue' springt direkt zur nächsten Schleifeniteration
                # (und damit zum "Enter drücken"-Prompt)
                input("\n--- Drücke Enter, um fortzufahren ---")
                continue 

            print("\nWie soll der Ordner gewählt werden?")
            print("1. Einen existierenden Ordner verwenden")
            print("2. Einen neuen Ordner erstellen")
            
            mode = input("Auswahl (1/2): ").strip()
            final_path = ""

            if mode == "1":
                final_path = input(r"Bitte vollen Pfad eingeben (z.B. F:\SmartDesk\Work): ").strip()
                if final_path and not os.path.exists(final_path):
                    print(f"Info: Der Ordner '{final_path}' existiert noch nicht, wird aber angelegt.")

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
                continue # Springt direkt zur nächsten Iteration (ohne Enter-Prompt)

            try:
                index = int(selection) - 1
                
                if 0 <= index < len(desktops):
                    target_desktop = desktops[index]
                    
                    if target_desktop.is_active:
                        print(f"'{target_desktop.name}' ist bereits aktiv.")
                    elif desktop_handler.switch_to_desktop(target_desktop.name):
                        print(f"Erfolgreich zu '{target_desktop.name}' gewechselt.")
                        print("Registry aktualisiert. Explorer wird neu gestartet...")
                        system_manager.restart_explorer()
                else:
                    print("Ungültige Nummer.")
            except ValueError:
                print("Bitte eine gültige Zahl eingeben.")

        elif choice == "4":
            print("Explorer wird manuell neu gestartet...")
            system_manager.restart_explorer()
            print("Explorer wurde neu gestartet.") # Feedback hinzugefügt

        elif choice == "5":
            print("Auf Wiedersehen!")
            break # WICHTIG: Beendet die 'while True'-Schleife
        else:
            print("Ungültige Eingabe.")
            
        # 2. Warten auf Benutzer
        # Dieser Code wird nur erreicht, wenn die Schleife NICHT
        # durch 'break' (bei Auswahl "5") oder 'continue' (bei "0")
        # verlassen wurde.
        input("\n--- Drücke Enter, um fortzufahren ---")

# --- Start des Skripts ---
if __name__ == "__main__":
    # Den Bildschirm beim allerersten Start einmal löschen
    clear_screen()
    run()
