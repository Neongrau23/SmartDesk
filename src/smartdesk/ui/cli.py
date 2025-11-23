# Dateipfad: src/smartdesk/ui/cli.py
# (Aktualisiert, um die neue locale.py für alle Menütexte zu verwenden)

import os
import platform
import time 

# --- Imports (ANGEPASST) ---
try:
    from ..handlers import desktop_handler
    from ..handlers import system_manager
    from .style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN 
    from .locale import TEXT # <-- NEU: Importiert das Text-Wörterbuch
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

# --- NEUES ASCII-LOGO ---
SMARTDESK_LOGO = r""" ___                _   ___         _   
/ __|_ __  __ _ _ _| |_|   \ ___ __| |__
\__ \ '  \/ _` | '_|  _| |) / -_|_-< / /
|___/_|_|_\__,_|_|  \__|___/\___/__/_\_\ """

def clear_screen():
    """Löscht den Terminal-Bildschirm, abhängig vom Betriebssystem."""
    system_name = platform.system()
    
    if system_name == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# --- NEUES HAUPTMENÜ (ANGEPASST) ---
def print_main_menu():
    """Zeigt das neue Hauptmenü an (liest Texte aus locale.py)."""
    print(SMARTDESK_LOGO)
    print(TEXT["MAIN_MENU_SEPARATOR"])
    print(f"1. {TEXT['MAIN_MENU_SWITCH']}")
    print(f"2. {TEXT['MAIN_MENU_CREATE']}")
    print(f"3. {TEXT['MAIN_MENU_SETTINGS']}")
    print(f"0. {TEXT['MAIN_MENU_EXIT']}")

# --- NEUES EINSTELLUNGSMENÜ (ANGEPASST) ---
def print_settings_menu():
    """Zeigt das neue Einstellungs-Untermenü an (liest Texte aus locale.py)."""
    print({TEXT["SETTINGS_MENU_HEADER"]})
    print({TEXT["MAIN_MENU_SEPARATOR"]}) # Wiederverwendung des Separators
    print(f"1. {TEXT['SETTINGS_MENU_LIST']}")
    print(f"2. {TEXT['SETTINGS_MENU_DELETE']}")
    print(f"3. {TEXT['SETTINGS_MENU_SAVE_ICONS']}")
    print(f"4. {TEXT['SETTINGS_MENU_RESTART']}")
    print(f"0. {TEXT['SETTINGS_MENU_BACK']}")

# --- NEUE FUNKTION FÜR EINSTELLUNGEN (ANGEPASST) ---
def run_settings_menu():
    """Verwaltet die Schleife für das Einstellungsmenü."""
    while True:
        clear_screen()
        print_settings_menu()
        choice = input(TEXT["PROMPT_CHOOSE"]) # <-- Geändert

        # --- 1. Alle Desktops anzeigen (Ehemals 1) ---
        if choice == "1":
            desktops = desktop_handler.get_all_desktops()
            if not desktops:
                print("Keine Desktops vorhanden.")
            else:
                print("\nVerfügbare Desktops:")
                for d in desktops:
                    status = "[AKTIV]" if d.is_active else "[ ]"
                    print(f"{status} {d.name} -> {d.path}")
            input(TEXT["PROMPT_CONTINUE"]) # <-- Geändert

        # --- 2. Desktop löschen (Ehemals 6) ---
        elif choice == "2":
            print("\n--- Desktop löschen ---")
            desktops = desktop_handler.get_all_desktops()
            
            if not desktops:
                print("Keine Desktops vorhanden.")
                input("\n--- Drücke Enter, um fortzufahren ---")
                continue

            print("\n--- Welchen Desktop löschen? ---")
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
                        # --- VERWENDET JETZT PREFIX_ERROR ---
                        print(f"{PREFIX_ERROR} Fehler: Desktop '{target_desktop.name}' ist aktiv. Bitte wechseln Sie vorher den Desktop.")
                        input("\n--- Drücke Enter, um fortzufahren ---")
                        continue

                    delete_folder_confirm = input(f"Soll der Ordner '{target_desktop.path}' auch physisch gelöscht werden? (y/n): ").strip().lower()
                    delete_folder = (delete_folder_confirm == 'y')
                    
                    desktop_handler.delete_desktop(target_desktop.name, delete_folder)
                    
                else:
                    print("Ungültige Nummer.")
            except ValueError:
                print("Bitte eine gültige Zahl eingeben.")
            input(TEXT["PROMPT_CONTINUE"]) # <-- Geändert

        # --- 3. Icons speichern (Ehemals 4) ---
        elif choice == "3":
            print("\nSpeichere aktuelle Icon-Positionen...")
            if desktop_handler.save_current_desktop_icons():
                # --- VERWENDET JETZT PREFIX_OK ---
                print(f"{PREFIX_OK} Speichern abgeschlossen.")
            else:
                print(f"{PREFIX_ERROR} Speichern fehlgeschlagen. Siehe Meldung oben.")
            input(TEXT["PROMPT_CONTINUE"]) # <-- Geändert

        # --- 4. Explorer neu starten (Ehemals 5) ---
        elif choice == "4":
            print("Explorer wird manuell neu gestartet...")
            system_manager.restart_explorer()
            print("Explorer wurde neu gestartet.")
            input(TEXT["PROMPT_CONTINUE"]) # <-- Geändert

        # --- 0. Zurück ---
        elif choice == "0":
            break # Verlässt die Einstellungs-Schleife
        
        else:
            print(TEXT["ERROR_INVALID_INPUT"]) # <-- Geändert
            input(TEXT["PROMPT_CONTINUE"]) # <-- Geändert

# --- run() FUNKTION STARK ANGEPASST (ANGEPASST) ---
def run():
    """Verwaltet die Schleife für das Hauptmenü."""
    while True:
        clear_screen()
        print_main_menu() # Zeigt das neue Hauptmenü
        choice = input(TEXT["PROMPT_CHOOSE"]) # <-- Geändert

        # --- 1. Desktop wechseln (Ehemals 3) ---
        if choice == "1":
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
                    
                    if desktop_handler.switch_to_desktop(target_desktop.name):
                        
                        print(f"Registry erfolgreich auf '{target_desktop.name}' gesetzt.")
                        print("Starte Explorer neu, um Änderungen anzuwenden...")
                        system_manager.restart_explorer()
                        
                        print("Explorer wurde neu gestartet. Warte 3 Sekunden auf Initialisierung...")
                        time.sleep(3) 

                        print("Synchronisiere Status und stelle Icons wieder her...")
                        desktop_handler.sync_desktop_state_and_apply_icons()
                        # --- VERWENDET JETZT PREFIX_OK ---
                        print(f"{PREFIX_OK} Wechsel zu '{target_desktop.name}' abgeschlossen.")
                        
                    else:
                        # Fehler/Bereits aktiv (Meldung kommt vom Handler)
                        pass
                else:
                    print("Ungültige Nummer.")
            except ValueError:
                print("Bitte eine gültige Zahl eingeben.")
            input(TEXT["PROMPT_CONTINUE"]) # <-- Geändert

        # --- 2. Neuen Desktop erstellen (Ehemals 2) ---
        elif choice == "2":
            print("\n--- Neuen Desktop anlegen ---")
            name = input("Name des neuen Desktops: ").strip()
            
            if not name:
                # --- VERWENDET JETZT PREFIX_ERROR ---
                print(f"{PREFIX_ERROR} Fehler: Der Name darf nicht leer sein.")
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
                    # --- VERWENDET JETZT PREFIX_ERROR ---
                    print(f"{PREFIX_ERROR} Fehler: Basis-Verzeichnis darf nicht leer sein.")
            else:
                print("Ungültige Auswahl.")
                input("\n--- Drücke Enter, um fortzufahren ---")
                continue

            if final_path:
                desktop_handler.create_desktop(name, final_path)
            else:
                print("Vorgang abgebrochen (kein Pfad angegeben).")
            input(TEXT["PROMPT_CONTINUE"]) # <-- Geändert
        
        # --- 3. Einstellungen ---
        elif choice == "3":
            run_settings_menu() # Ruft die neue Untermenü-Schleife auf
        
        # --- 0. Beenden (Ehemals 7) ---
        elif choice == "0":
            print(TEXT["EXIT_MESSAGE"]) # <-- Geändert
            break
            
        else:
            print(TEXT["ERROR_INVALID_INPUT"]) # <-- Geändert
            input(TEXT["PROMPT_CONTINUE"]) # <-- Geändert

# --- Start des Skripts (unverändert) ---
if __name__ == "__main__":
    clear_screen()
    run()