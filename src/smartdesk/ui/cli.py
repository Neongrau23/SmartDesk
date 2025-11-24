# Dateipfad: src/smartdesk/ui/cli.py
# (Aktualisiert, um die NEUE localization.py zu verwenden)

import os
import platform
import time 
import threading

# --- Imports (ANGEPASST) ---
try:
    from ..handlers import desktop_handler
    from ..handlers import system_manager
    from .style import (
        PREFIX_ERROR, PREFIX_OK, PREFIX_WARN, 
        format_status_active, format_status_inactive
    )
    # --- GEÄNDERTER IMPORT ---
    from ..localization import get_text
except ImportError as e:
    # --- (Lokalisierung hier nicht möglich, da Import fehlschlägt) ---
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

# --- HAUPTMENÜ (ANGEPASST) ---
def print_main_menu():
    """Zeigt das Hauptmenü an (liest Texte aus localization.py)."""
    # --- LOKALISIERT ---
    print(get_text("logo.ascii"))
    print(get_text("ui.menu.main.separator"))
    print(f"1. {get_text('ui.menu.main.switch')}")
    print(f"2. {get_text('ui.menu.main.create')}")
    print(f"3. {get_text('ui.menu.main.settings')}")
    print(f"0. {get_text('ui.menu.main.exit')}")

# --- EINSTELLUNGSMENÜ (ANGEPASST) ---
def print_settings_menu():
    """Zeigt das Einstellungs-Untermenü an (liest Texte aus localization.py)."""
    # --- LOKALISIERT ---
    print(get_text("ui.menu.settings.header"))
    print(get_text("ui.menu.main.separator"))
    print(f"1. {get_text('ui.menu.settings.list')}")
    print(f"2. {get_text('ui.menu.settings.delete')}")
    print(f"3. {get_text('ui.menu.settings.save_icons')}")
    print(f"4. {get_text('ui.menu.settings.restart')}")
    print(f"0. {get_text('ui.menu.settings.back')}")

# --- EINSTELLUNGEN (ANGEPASST) ---
def run_settings_menu():
    """Verwaltet die Schleife für das Einstellungsmenü."""
    while True:
        clear_screen()
        print_settings_menu()
        # --- LOKALISIERT ---
        choice = input(get_text("ui.prompts.choose"))

        # --- 1. Alle Desktops anzeigen ---
        if choice == "1":
            desktops = desktop_handler.get_all_desktops()
            if not desktops:
                # --- LOKALISIERT ---
                print(get_text("ui.messages.no_desktops"))
            else:
                # --- LOKALISIERT ---
                print(get_text("main.info.list_header"))
                for d in desktops:
                    if d.is_active:
                        status = format_status_active(get_text("ui.status.active"))
                    else:
                        status = format_status_inactive(get_text("ui.status.inactive"))
                    print(f"{status} {d.name} -> {d.path}")
            # --- LOKALISIERT ---
            input(get_text("ui.prompts.continue"))

        # --- 2. Desktop löschen ---
        elif choice == "2":
            # --- LOKALISIERT ---
            print(get_text("ui.headings.delete"))
            desktops = desktop_handler.get_all_desktops()
            
            if not desktops:
                # --- LOKALISIERT ---
                print(get_text("ui.messages.no_desktops"))
                input(get_text("ui.prompts.continue"))
                continue

            # --- LOKALISIERT ---
            print(get_text("ui.headings.which_desktop_delete"))
            for i, d in enumerate(desktops, 1):
                if d.is_active:
                    status = format_status_active(get_text("ui.status.active"))
                else:
                    status = format_status_inactive(get_text("ui.status.inactive"))
                print(f"{i}. {status} {d.name} ({d.path})")
            
            # --- LOKALISIERT ---
            print(get_text("ui.prompts.cancel"))
            selection = input(get_text("ui.prompts.choose_number")).strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1
                
                if 0 <= index < len(desktops):
                    target_desktop = desktops[index]
                    
                    if target_desktop.is_active:
                        # --- LOKALISIERT (Handler-Text wird hier dupliziert, da UI-Logik) ---
                        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.delete_active', name=target_desktop.name)}")
                        input(get_text("ui.prompts.continue"))
                        continue

                    # --- LOKALISIERT ---
                    delete_folder_confirm = input(get_text("ui.prompts.delete_folder_confirm", path=target_desktop.path)).strip().lower()
                    delete_folder = (delete_folder_confirm == 'y')
                    
                    # Handler gibt eigene (lokalisierte) Meldungen aus
                    desktop_handler.delete_desktop(target_desktop.name, delete_folder)
                    
                else:
                    # --- LOKALISIERT & GEFÄRBT ---
                    print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            except ValueError:
                # --- LOKALISIERT & GEFÄRBT ---
                print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            # --- LOKALISIERT ---
            input(get_text("ui.prompts.continue"))

        # --- 3. Icons speichern ---
        elif choice == "3":
            # --- LOKALISIERT (Handler gibt eigene Meldungen aus) ---
            print(get_text("desktop_handler.info.saving_icons", name="...")) # Platzhalter, Handler weiß es besser
            if desktop_handler.save_current_desktop_icons():
                # Erfolgsmeldung kommt jetzt vom Handler
                pass
            else:
                # Fehlermeldung kommt jetzt vom Handler
                pass
            # --- LOKALISIERT ---
            input(get_text("ui.prompts.continue"))

        # --- 4. Explorer neu starten ---
        elif choice == "4":
            # --- LOKALISIERT (Handler gibt eigene Meldungen aus) ---
            system_manager.restart_explorer()
            input(get_text("ui.prompts.continue"))

        # --- 0. Zurück ---
        elif choice == "0":
            break 
        
        else:
            # --- LOKALISIERT & GEFÄRBT ---
            print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_input')}")
            input(get_text("ui.prompts.continue"))

# --- run() FUNKTION (ANGEPASST) ---
def run():
    """Verwaltet die Schleife für das Hauptmenü."""
    while True:
        clear_screen()
        print_main_menu()
        # --- LOKALISIERT ---
        choice = input(get_text("ui.prompts.choose"))

        # --- 1. Desktop wechseln ---
        if choice == "1":
            desktops = desktop_handler.get_all_desktops()
            
            if not desktops:
                # --- LOKALISIERT ---
                print(get_text("ui.messages.no_desktops_create_first"))
                input(get_text("ui.prompts.continue"))
                continue

            # --- LOKALISIERT ---
            print(get_text("ui.headings.which_desktop_switch"))
            for i, d in enumerate(desktops, 1):
                if d.is_active:
                    status = format_status_active(get_text("ui.status.active"))
                else:
                    status = format_status_inactive(get_text("ui.status.inactive"))
                print(f"{i}. {status} {d.name} ({d.path})")
            
            # --- LOKALISIERT ---
            print(get_text("ui.prompts.cancel"))
            selection = input(get_text("ui.prompts.choose_number")).strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1
                
                if 0 <= index < len(desktops):
                    target_desktop = desktops[index]
                    
                    # Handler (switch_to_desktop) gibt lokalisierte Meldungen aus
                    if desktop_handler.switch_to_desktop(target_desktop.name):
                        
                        # --- LOKALISIERT ---
                        print(get_text("ui.messages.registry_set_success", name=target_desktop.name))
                        print(get_text("ui.messages.restarting_explorer"))
                        system_manager.restart_explorer()
                        
                        print(get_text("ui.messages.waiting_for_explorer"))
                        time.sleep(1) 

                        print(get_text("ui.messages.syncing_icons"))
                        desktop_handler.sync_desktop_state_and_apply_icons()
                        print(f"{PREFIX_OK} {get_text('ui.messages.switch_success', name=target_desktop.name)}")
                        
                    else:
                        pass
                else:
                    # --- LOKALISIERT & GEFÄRBT ---
                    print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            except ValueError:
                # --- LOKALISIERT & GEFÄRBT ---
                print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            # --- LOKALISIERT ---
            input(get_text("ui.prompts.continue"))

        # --- 2. Neuen Desktop erstellen ---
        elif choice == "2":
            # --- LOKALISIERT ---
            print(get_text("ui.headings.create"))
            name = input(get_text("ui.prompts.desktop_name")).strip()
            
            if not name:
                # --- LOKALISIERT & GEFÄRBT ---
                print(f"{PREFIX_ERROR} {get_text('ui.errors.name_empty')}")
                input(get_text("ui.prompts.continue"))
                continue

            print(get_text("ui.prompts.folder_mode"))
            print(get_text("ui.prompts.folder_mode_1"))
            print(get_text("ui.prompts.folder_mode_2"))
            
            mode = input(get_text("ui.prompts.choose_1_or_2")).strip()
            
            # --- START ÄNDERUNG: Logik aufgeteilt ---
            if mode == "1":
                final_path = input(get_text("ui.prompts.existing_path")).strip()
                if final_path:
                    # Rufe Handler auf, OHNE Ordner zu erstellen (create_if_missing=False)
                    desktop_handler.create_desktop(name, final_path, create_if_missing=False)
                else:
                    print(get_text("ui.messages.aborted_no_path"))

            elif mode == "2":
                # --- START ÄNDERUNG: Schleife für Pfad-Validierung ---
                while True: 
                    parent_path = input(get_text("ui.prompts.new_path_parent")).strip()
                    
                    if not parent_path:
                        # --- LOKALISIERT & GEFÄRBT ---
                        print(f"{PREFIX_ERROR} {get_text('ui.errors.base_dir_empty')}")
                        # --- START ERSATZ FÜR 'input(continue)' ---
                        print(get_text("ui.prompts.path_error_menu.title")) # 1. Anderen Pfad eingeben
                        print(get_text("ui.prompts.path_error_menu.abort")) # 2. Zurück zum Hauptmenü
                        sub_choice = input(get_text("ui.prompts.choose")).strip()
                        if sub_choice == "2":
                            break # Verlässt die while-Schleife -> zurück zum Hauptmenü
                        else:
                            continue # (Wahl 1 or ungültig) -> Zurück zur parent_path-Abfrage
                        # --- ENDE ERSATZ ---

                    # --- START NEUE (VERBESSERTE) PRÜFUNG ---
                    
                    # 1. Prüfen, ob der Pfad absolut ist (muss mit Laufwerksbuchstabe beginnen)
                    if not os.path.isabs(parent_path):
                        # 'dl' ist nicht absolut -> Fehler
                        print(f"{PREFIX_ERROR} {get_text('ui.errors.path_not_absolute', path=parent_path)}")
                        print(get_text("ui.prompts.path_error_menu.title"))
                        print(get_text("ui.prompts.path_error_menu.abort"))
                        sub_choice = input(get_text("ui.prompts.choose")).strip()
                        if sub_choice == "2":
                            break # Verlässt die while-Schleife
                        else:
                            continue # Zurück zur parent_path-Abfrage

                    # 2. Prüfen, ob das Laufwerk existiert
                    try:
                        # Zerlegt den Pfad in Laufwerk (z.B. 'K:') und Rest ('/test')
                        drive, _ = os.path.splitdrive(parent_path)
                        
                        # Prüft, ob das Laufwerk existiert (nur wenn es ein Laufwerk gibt)
                        if drive and not os.path.exists(drive):
                            # Wenn das Laufwerk ungültig ist (K: existiert nicht)
                            # Wir nutzen die "path_invalid" Meldung, da der Pfad nicht erstellt werden KANN.
                            # --- LOKALISIERT & GEFÄRBT ---
                            print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.path_invalid', path=parent_path)}")
                            # --- START ERSATZ FÜR 'input(continue)' ---
                            print(get_text("ui.prompts.path_error_menu.title"))
                            print(get_text("ui.prompts.path_error_menu.abort"))
                            sub_choice = input(get_text("ui.prompts.choose")).strip()
                            if sub_choice == "2":
                                break # Verlässt die while-Schleife
                            else:
                                continue # Zurück zur parent_path-Abfrage
                            # --- ENDE ERSATZ ---
                    
                    except Exception:
                        # Fängt ungültige Pfad-Syntax ab (z.B. C::/test)
                        # --- LOKALISIERT & GEFÄRBT ---
                        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.path_invalid', path=parent_path)}")
                        # --- START ERSATZ FÜR 'input(continue)' ---
                        print(get_text("ui.prompts.path_error_menu.title"))
                        print(get_text("ui.prompts.path_error_menu.abort"))
                        sub_choice = input(get_text("ui.prompts.choose")).strip()
                        if sub_choice == "2":
                            break # Verlässt die while-Schleife
                        else:
                            continue # Zurück zur parent_path-Abfrage
                        # --- ENDE ERSATZ ---
                    # --- ENDE NEUE (VERBESSERTE) PRÜFUNG ---

                    # Fall 1: Pfad existiert, alles super
                    # (Wir verwenden den ursprünglichen parent_path, nicht den abs_path)
                    if os.path.exists(parent_path) and os.path.isdir(parent_path):
                        final_path = os.path.join(parent_path, name)
                        print(get_text("ui.messages.new_path_location", path=final_path))
                        desktop_handler.create_desktop(name, final_path, create_if_missing=True)
                        break # Verlässt die while-Schleife

                    # Fall 2: Pfad existiert nicht (aber Laufwerk ist gültig)
                    else:
                        print(f"{PREFIX_WARN} {get_text('ui.prompts.parent_dir_menu.not_found', path=parent_path)}")
                        print(get_text("ui.prompts.parent_dir_menu.title"))
                        print(get_text("ui.prompts.parent_dir_menu.create", path=parent_path))
                        print(get_text("ui.prompts.parent_dir_menu.reenter"))
                        print(get_text("ui.prompts.parent_dir_menu.abort"))
                        
                        sub_choice = input(get_text("ui.prompts.choose")).strip()

                        if sub_choice == "1":
                            # Erstellen
                            try:
                                os.makedirs(parent_path)
                                print(f"{PREFIX_OK} {get_text('ui.messages.parent_created', path=parent_path)}")
                                # Jetzt, da es erstellt ist, fahre fort
                                final_path = os.path.join(parent_path, name)
                                print(get_text("ui.messages.new_path_location", path=final_path))
                                desktop_handler.create_desktop(name, final_path, create_if_missing=True)
                                break # Verlässt die while-Schleife

                            except Exception as e:
                                # --- LOKALISIERT & GEFÄRBT ---
                                print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.path_invalid', path=parent_path)}")
                                input(get_text("ui.prompts.continue"))
                                continue # Zurück zur parent_path-Abfrage

                        elif sub_choice == "2":
                            # Anderes Verzeichnis -> Zurück zur parent_path-Abfrage
                            continue 
                        
                        else: # 0 or anything else
                            # Abbrechen
                            print(get_text("ui.messages.aborted_no_path"))
                            break # Verlässt die while-Schleife
                # --- ENDE ÄNDERUNG ---

            else:
                # --- LOKALISIERT & GEFÄRBT ---
                print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_choice')}")
            
            # Der 'if final_path:' Block von vorher ist nun oben integriert.
            # --- ENDE ÄNDERUNG ---
                
            # --- LOKALISIERT ---
            input(get_text("ui.prompts.continue"))
        
        # --- 3. Einstellungen ---
        elif choice == "3":
            run_settings_menu() 
        
        # --- 0. Beenden ---
        elif choice == "0":
            # --- LOKALISIERT ---
            print(get_text("ui.messages.exit"))
            break
            
        else:
            # --- LOKALISIERT & GEFÄRBT ---
            print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_input')}")
            input(get_text("ui.prompts.continue"))

# --- Start des Skripts (unverändert) ---
if __name__ == "__main__":
    clear_screen()
    run()
