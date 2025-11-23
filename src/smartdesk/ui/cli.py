# Dateipfad: src/smartdesk/ui/cli.py
# (Aktualisiert, um die NEUE localization.py zu verwenden)

import os
import platform
import time 

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
    print(get_text("LOGO_ASCII"))
    print(get_text("MAIN_MENU_SEPARATOR"))
    print(f"1. {get_text('MAIN_MENU_SWITCH')}")
    print(f"2. {get_text('MAIN_MENU_CREATE')}")
    print(f"3. {get_text('MAIN_MENU_SETTINGS')}")
    print(f"0. {get_text('MAIN_MENU_EXIT')}")

# --- EINSTELLUNGSMENÜ (ANGEPASST) ---
def print_settings_menu():
    """Zeigt das Einstellungs-Untermenü an (liest Texte aus localization.py)."""
    # --- LOKALISIERT ---
    print(get_text("SETTINGS_MENU_HEADER"))
    print(get_text("MAIN_MENU_SEPARATOR"))
    print(f"1. {get_text('SETTINGS_MENU_LIST')}")
    print(f"2. {get_text('SETTINGS_MENU_DELETE')}")
    print(f"3. {get_text('SETTINGS_MENU_SAVE_ICONS')}")
    print(f"4. {get_text('SETTINGS_MENU_RESTART')}")
    print(f"0. {get_text('SETTINGS_MENU_BACK')}")

# --- EINSTELLUNGEN (ANGEPASST) ---
def run_settings_menu():
    """Verwaltet die Schleife für das Einstellungsmenü."""
    while True:
        clear_screen()
        print_settings_menu()
        # --- LOKALISIERT ---
        choice = input(get_text("PROMPT_CHOOSE"))

        # --- 1. Alle Desktops anzeigen ---
        if choice == "1":
            desktops = desktop_handler.get_all_desktops()
            if not desktops:
                # --- LOKALISIERT ---
                print(get_text("INFO_NO_DESKTOPS"))
            else:
                # --- LOKALISIERT ---
                print(get_text("MAIN_INFO_LIST_HEADER"))
                for d in desktops:
                    if d.is_active:
                        status = format_status_active(get_text("STATUS_ACTIVE"))
                    else:
                        status = format_status_inactive(get_text("STATUS_INACTIVE"))
                    print(f"{status} {d.name} -> {d.path}")
            # --- LOKALISIERT ---
            input(get_text("PROMPT_CONTINUE"))

        # --- 2. Desktop löschen ---
        elif choice == "2":
            # --- LOKALISIERT ---
            print(get_text("INFO_DELETE_HEADING"))
            desktops = desktop_handler.get_all_desktops()
            
            if not desktops:
                # --- LOKALISIERT ---
                print(get_text("INFO_NO_DESKTOPS"))
                input(get_text("PROMPT_CONTINUE"))
                continue

            # --- LOKALISIERT ---
            print(get_text("PROMPT_WHICH_DESKTOP_DELETE"))
            for i, d in enumerate(desktops, 1):
                if d.is_active:
                    status = format_status_active(get_text("STATUS_ACTIVE"))
                else:
                    status = format_status_inactive(get_text("STATUS_INACTIVE"))
                print(f"{i}. {status} {d.name} ({d.path})")
            
            # --- LOKALISIERT ---
            print(get_text("PROMPT_CANCEL"))
            selection = input(get_text("PROMPT_CHOOSE_NUMBER")).strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1
                
                if 0 <= index < len(desktops):
                    target_desktop = desktops[index]
                    
                    if target_desktop.is_active:
                        # --- LOKALISIERT (Handler-Text wird hier dupliziert, da UI-Logik) ---
                        print(f"{PREFIX_ERROR} {get_text('DH_ERROR_DELETE_ACTIVE', name=target_desktop.name)}")
                        input(get_text("PROMPT_CONTINUE"))
                        continue

                    # --- LOKALISIERT ---
                    delete_folder_confirm = input(get_text("PROMPT_DELETE_FOLDER_CONFIRM", path=target_desktop.path)).strip().lower()
                    delete_folder = (delete_folder_confirm == 'y')
                    
                    # Handler gibt eigene (lokalisierte) Meldungen aus
                    desktop_handler.delete_desktop(target_desktop.name, delete_folder)
                    
                else:
                    # --- LOKALISIERT ---
                    print(get_text("ERROR_INVALID_NUMBER"))
            except ValueError:
                # --- LOKALISIERT ---
                print(get_text("ERROR_INVALID_NUMBER"))
            # --- LOKALISIERT ---
            input(get_text("PROMPT_CONTINUE"))

        # --- 3. Icons speichern ---
        elif choice == "3":
            # --- LOKALISIERT (Handler gibt eigene Meldungen aus) ---
            print(get_text("DH_INFO_SAVING_ICONS", name="...")) # Platzhalter, Handler weiß es besser
            if desktop_handler.save_current_desktop_icons():
                print(f"{PREFIX_OK} {get_text('DH_SUCCESS_SAVE_ICONS', name='...')}") # Platzhalter
            else:
                print(f"{PREFIX_ERROR} {get_text('DH_ERROR_SAVE_ICONS', e='...')}") # Platzhalter
            # --- LOKALISIERT ---
            input(get_text("PROMPT_CONTINUE"))

        # --- 4. Explorer neu starten ---
        elif choice == "4":
            # --- LOKALISIERT (Handler gibt eigene Meldungen aus) ---
            system_manager.restart_explorer()
            input(get_text("PROMPT_CONTINUE"))

        # --- 0. Zurück ---
        elif choice == "0":
            break 
        
        else:
            # --- LOKALISIERT ---
            print(get_text("ERROR_INVALID_INPUT"))
            input(get_text("PROMPT_CONTINUE"))

# --- run() FUNKTION (ANGEPASST) ---
def run():
    """Verwaltet die Schleife für das Hauptmenü."""
    while True:
        clear_screen()
        print_main_menu()
        # --- LOKALISIERT ---
        choice = input(get_text("PROMPT_CHOOSE"))

        # --- 1. Desktop wechseln ---
        if choice == "1":
            desktops = desktop_handler.get_all_desktops()
            
            if not desktops:
                # --- LOKALISIERT ---
                print(get_text("INFO_NO_DESKTOPS_CREATE_FIRST"))
                input(get_text("PROMPT_CONTINUE"))
                continue

            # --- LOKALISIERT ---
            print(get_text("PROMPT_WHICH_DESKTOP_SWITCH"))
            for i, d in enumerate(desktops, 1):
                if d.is_active:
                    status = format_status_active(get_text("STATUS_ACTIVE"))
                else:
                    status = format_status_inactive(get_text("STATUS_INACTIVE"))
                print(f"{i}. {status} {d.name} ({d.path})")
            
            # --- LOKALISIERT ---
            print(get_text("PROMPT_CANCEL"))
            selection = input(get_text("PROMPT_CHOOSE_NUMBER")).strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1
                
                if 0 <= index < len(desktops):
                    target_desktop = desktops[index]
                    
                    # Handler (switch_to_desktop) gibt lokalisierte Meldungen aus
                    if desktop_handler.switch_to_desktop(target_desktop.name):
                        
                        # --- LOKALISIERT ---
                        print(get_text("INFO_REGISTRY_SET_SUCCESS", name=target_desktop.name))
                        print(get_text("INFO_RESTARTING_EXPLORER"))
                        system_manager.restart_explorer()
                        
                        print(get_text("INFO_WAITING_FOR_EXPLORER"))
                        time.sleep(3) 

                        print(get_text("INFO_SYNCING_ICONS"))
                        desktop_handler.sync_desktop_state_and_apply_icons()
                        print(f"{PREFIX_OK} {get_text('SWITCH_SUCCESS', name=target_desktop.name)}")
                        
                    else:
                        pass
                else:
                    # --- LOKALISIERT ---
                    print(get_text("ERROR_INVALID_NUMBER"))
            except ValueError:
                # --- LOKALISIERT ---
                print(get_text("ERROR_INVALID_NUMBER"))
            # --- LOKALISIERT ---
            input(get_text("PROMPT_CONTINUE"))

        # --- 2. Neuen Desktop erstellen ---
        elif choice == "2":
            # --- LOKALISIERT ---
            print(get_text("INFO_CREATE_HEADING"))
            name = input(get_text("PROMPT_DESKTOP_NAME")).strip()
            
            if not name:
                print(f"{PREFIX_ERROR} {get_text('ERROR_NAME_EMPTY')}")
                input(get_text("PROMPT_CONTINUE"))
                continue

            print(get_text("PROMPT_FOLDER_MODE"))
            print(get_text("PROMPT_FOLDER_MODE_1"))
            print(get_text("PROMPT_FOLDER_MODE_2"))
            
            mode = input(get_text("PROMPT_CHOOSE_1_OR_2")).strip()
            final_path = ""

            if mode == "1":
                final_path = input(get_text("PROMPT_EXISTING_PATH")).strip()

            elif mode == "2":
                parent_path = input(get_text("PROMPT_NEW_PATH_PARENT")).strip()
                
                if parent_path:
                    final_path = os.path.join(parent_path, name)
                    print(get_text("INFO_NEW_PATH_LOCATION", path=final_path))
                else:
                    print(f"{PREFIX_ERROR} {get_text('ERROR_BASE_DIR_EMPTY')}")
            else:
                # --- LOKALISIERT ---
                print(get_text("ERROR_INVALID_CHOICE"))
                input(get_text("PROMPT_CONTINUE"))
                continue

            if final_path:
                # Handler gibt lokalisierte Meldungen aus
                desktop_handler.create_desktop(name, final_path)
            else:
                # --- LOKALISIERT ---
                print(get_text("INFO_ABORTED_NO_PATH"))
            # --- LOKALISIERT ---
            input(get_text("PROMPT_CONTINUE"))
        
        # --- 3. Einstellungen ---
        elif choice == "3":
            run_settings_menu() 
        
        # --- 0. Beenden ---
        elif choice == "0":
            # --- LOKALISIERT ---
            print(get_text("EXIT_MESSAGE"))
            break
            
        else:
            # --- LOKALISIERT ---
            print(get_text("ERROR_INVALID_INPUT"))
            input(get_text("PROMPT_CONTINUE"))

# --- Start des Skripts (unverändert) ---
if __name__ == "__main__":
    clear_screen()
    run()
    