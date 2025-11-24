# Dateipfad: src/smartdesk/ui/cli.py
# (Vollständig und korrigiert)

import os
import platform
import time 

# --- Imports (Korrigiert auf absolute Pfade) ---
try:
    from smartdesk.handlers import desktop_handler
    from smartdesk.handlers import system_manager
    # DATA_DIR wird für die .lock-Datei benötigt
    from smartdesk.config import DATA_DIR 
    from smartdesk.ui.style import (
        PREFIX_ERROR, PREFIX_OK, PREFIX_WARN, 
        format_status_active, format_status_inactive
    )
    from smartdesk.localization import get_text
except ImportError as e:
    # --- (Lokalisierung hier nicht möglich, da Import fehlschlägt) ---
    print(f"FATALER IMPORT FEHLER in cli.py: {e}")
    print("Stelle sicher, dass alle Importe in den 'handler'- und 'utils'-Dateien")
    print("auf 'smartdesk.' (absolut) statt '..' (relativ) umgestellt sind.")
    
    # Fallback, damit das Programm nicht sofort abstürzt,
    # obwohl es wahrscheinlich nicht funktionieren wird.
    class FakeHandler:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                print(f"FEHLER: {name} konnte nicht geladen werden!")
            return method
    desktop_handler = FakeHandler()
    system_manager = FakeHandler()
    # Dummy-Funktion, um Abstürze zu vermeiden
    def get_text(key, **kwargs): return key
    PREFIX_ERROR = "ERROR:"
    PREFIX_OK = "OK:"
    PREFIX_WARN = "WARN:"
    DATA_DIR = "." # Dummy-Wert
    def format_status_active(t): return f"[{t}]"
    def format_status_inactive(t): return f"[{t}]"
# --- Ende Imports ---


def clear_screen():
    """Löscht den Terminal-Bildschirm, abhängig vom Betriebssystem."""
    system_name = platform.system()
    
    if system_name == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# --- HAUPTMENÜ ---
def print_main_menu():
    """Zeigt das Hauptmenü an (liest Texte aus localization.py)."""
    print(get_text("logo.ascii"))
    print(get_text("ui.menu.main.separator"))
    print(f"1. {get_text('ui.menu.main.switch')}")
    print(f"2. {get_text('ui.menu.main.create')}")
    print(f"3. {get_text('ui.menu.main.settings')}")
    print(f"0. {get_text('ui.menu.main.exit')}")

# --- EINSTELLUNGSMENÜ ---
def print_settings_menu():
    """Zeigt das Einstellungs-Untermenü an (liest Texte aus localization.py)."""
    print(get_text("ui.menu.settings.header"))
    print(get_text("ui.menu.main.separator"))
    print(f"1. {get_text('ui.menu.settings.list')}")
    print(f"2. {get_text('ui.menu.settings.delete')}")
    print(f"3. {get_text('ui.menu.settings.save_icons')}")
    print(f"4. {get_text('ui.menu.settings.wallpaper')}")
    print(f"5. {get_text('ui.menu.settings.restart')}")
    print(f"0. {get_text('ui.menu.settings.back')}")

# --- EINSTELLUNGEN ---
def run_settings_menu():
    """Verwaltet die Schleife für das Einstellungsmenü."""
    while True:
        clear_screen()
        print_settings_menu()
        choice = input(get_text("ui.prompts.choose"))

        # --- 1. Alle Desktops anzeigen ---
        if choice == "1":
            desktops = desktop_handler.get_all_desktops()
            if not desktops:
                print(get_text("ui.messages.no_desktops"))
            else:
                print(get_text("main.info.list_header"))
                for d in desktops:
                    if d.is_active:
                        status = format_status_active(get_text("ui.status.active"))
                    else:
                        status = format_status_inactive(get_text("ui.status.inactive"))
                    
                    wallpaper_info = ""
                    if d.wallpaper_path:
                        wallpaper_info = f" ({get_text('ui.status.wallpaper')}: {os.path.basename(d.wallpaper_path)})"
                    
                    print(f"{status} {d.name} -> {d.path}{wallpaper_info}")
                    
            input(get_text("ui.prompts.continue"))

        # --- 2. Desktop löschen ---
        elif choice == "2":
            print(get_text("ui.headings.delete"))
            desktops = desktop_handler.get_all_desktops()
            
            if not desktops:
                print(get_text("ui.messages.no_desktops"))
                input(get_text("ui.prompts.continue"))
                continue

            print(get_text("ui.headings.which_desktop_delete"))
            for i, d in enumerate(desktops, 1):
                if d.is_active:
                    status = format_status_active(get_text("ui.status.active"))
                else:
                    status = format_status_inactive(get_text("ui.status.inactive"))
                print(f"{i}. {status} {d.name} ({d.path})")
            
            print(get_text("ui.prompts.cancel"))
            selection = input(get_text("ui.prompts.choose_number")).strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1
                
                if 0 <= index < len(desktops):
                    target_desktop = desktops[index]
                    
                    if target_desktop.is_active:
                        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.delete_active', name=target_desktop.name)}")
                        input(get_text("ui.prompts.continue"))
                        continue

                    delete_folder_confirm = input(get_text("ui.prompts.delete_folder_confirm", path=target_desktop.path)).strip().lower()
                    delete_folder = (delete_folder_confirm == 'y')
                    
                    desktop_handler.delete_desktop(target_desktop.name, delete_folder)
                    
                else:
                    print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            except ValueError:
                print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            input(get_text("ui.prompts.continue"))

        # --- 3. Icons speichern ---
        elif choice == "3":
            print(get_text("desktop_handler.info.reading_icons", name="...")) 
            desktop_handler.save_current_desktop_icons()
            input(get_text("ui.prompts.continue"))

        # --- 4. HINTERGRUNDBILD ZUWEISEN ---
        elif choice == "4":
            print(get_text("ui.headings.wallpaper"))
            desktops = desktop_handler.get_all_desktops()
            
            if not desktops:
                print(get_text("ui.messages.no_desktops"))
                input(get_text("ui.prompts.continue"))
                continue

            print(get_text("ui.headings.which_desktop_wallpaper"))
            for i, d in enumerate(desktops, 1):
                status = format_status_inactive("") 
                if d.is_active:
                    status = format_status_active(get_text("ui.status.active_short"))
                
                wallpaper_info = ""
                if d.wallpaper_path:
                    wallpaper_info = f" ({get_text('ui.status.wallpaper')}: {os.path.basename(d.wallpaper_path)})"
                else:
                    wallpaper_info = f" ({get_text('ui.status.wallpaper_none')})"

                print(f"{i}. {status} {d.name}{wallpaper_info}")
            
            print(get_text("ui.prompts.cancel"))
            selection = input(get_text("ui.prompts.choose_number")).strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1
                if not (0 <= index < len(desktops)):
                    print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
                    input(get_text("ui.prompts.continue"))
                    continue
                    
                target_desktop = desktops[index]
                
                source_path = input(get_text("ui.prompts.wallpaper_path")).strip()
                
                if not source_path:
                    print(get_text("ui.messages.aborted_no_path"))
                    input(get_text("ui.prompts.continue"))
                    continue
                
                source_path = source_path.strip('"')
                
                desktop_handler.assign_wallpaper(target_desktop.name, source_path)
                
            except ValueError:
                print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            
            input(get_text("ui.prompts.continue"))
            
        # --- 5. Explorer neu starten ---
        elif choice == "5":
            system_manager.restart_explorer()
            input(get_text("ui.prompts.continue"))

        # --- 0. Zurück ---
        elif choice == "0":
            break 
        
        else:
            print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_input')}")
            input(get_text("ui.prompts.continue"))

# --- run() FUNKTION ---
def run():
    """Verwaltet die Schleife für das Hauptmenü."""
    while True:
        clear_screen()
        print_main_menu()
        choice = input(get_text("ui.prompts.choose"))

        # --- 1. Desktop wechseln ---
        if choice == "1":
            desktops = desktop_handler.get_all_desktops()
            
            if not desktops:
                print(get_text("ui.messages.no_desktops_create_first"))
                input(get_text("ui.prompts.continue"))
                continue

            print(get_text("ui.headings.which_desktop_switch"))
            for i, d in enumerate(desktops, 1):
                if d.is_active:
                    status = format_status_active(get_text("ui.status.active"))
                else:
                    status = format_status_inactive(get_text("ui.status.inactive"))
                print(f"{i}. {status} {d.name} ({d.path})")
            
            print(get_text("ui.prompts.cancel"))
            selection = input(get_text("ui.prompts.choose_number")).strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1
                
                if 0 <= index < len(desktops):
                    target_desktop = desktops[index]
                    
                    # switch_to_desktop gibt True zurück, wenn Neustart nötig
                    if desktop_handler.switch_to_desktop(target_desktop.name):
                        
                        print(get_text("ui.messages.registry_set_success", name=target_desktop.name))
                        print(get_text("ui.messages.restarting_explorer"))
                        system_manager.restart_explorer()
                        
                        print(get_text("ui.messages.waiting_for_explorer"))
                        time.sleep(1) 

                        print(get_text("ui.messages.syncing_icons"))
                        desktop_handler.sync_desktop_state_and_apply_icons()

                        # --- Signaldatei erstellen, um Animation zu beenden ---
                        SIGNAL_FILE_PATH = os.path.join(DATA_DIR, "fade_signal.lock")
                        time.sleep(1)
                        try:
                            with open(SIGNAL_FILE_PATH, "w") as f:
                                f.write("done")
                        except Exception as e:
                            print(f"{PREFIX_WARN} Animations-Signaldatei konnte nicht geschrieben werden: {e}")
                        # --- ENDE ---

                        print(f"{PREFIX_OK} {get_text('ui.messages.switch_success', name=target_desktop.name)}")
                        
                    else:
                        # Kein Neustart nötig (z.B. Desktop war schon aktiv)
                        pass
                else:
                    print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            except ValueError:
                print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            input(get_text("ui.prompts.continue"))

        # --- 2. Neuen Desktop erstellen ---
        elif choice == "2":
            print(get_text("ui.headings.create"))
            name = input(get_text("ui.prompts.desktop_name")).strip()
            
            if not name:
                print(f"{PREFIX_ERROR} {get_text('ui.errors.name_empty')}")
                input(get_text("ui.prompts.continue"))
                continue

            print(get_text("ui.prompts.folder_mode"))
            print(get_text("ui.prompts.folder_mode_1"))
            print(get_text("ui.prompts.folder_mode_2"))
            
            mode = input(get_text("ui.prompts.choose_1_or_2")).strip()
            
            if mode == "1":
                final_path_input = input(get_text("ui.prompts.existing_path")).strip()
                if final_path_input:
                    final_path = os.path.normpath(final_path_input) 
                    desktop_handler.create_desktop(name, final_path, create_if_missing=False)
                else:
                    print(get_text("ui.messages.aborted_no_path"))

            elif mode == "2":
                while True: 
                    parent_path_input = input(get_text("ui.prompts.new_path_parent")).strip()
                    
                    if not parent_path_input:
                        print(get_text("ui.messages.aborted_no_path"))
                        break # Zurück zum Hauptmenü
                    
                    parent_path = os.path.normpath(parent_path_input)

                    if not os.path.isabs(parent_path):
                        print(f"{PREFIX_ERROR} {get_text('ui.errors.path_not_absolute', path=parent_path)}")
                        print(get_text("ui.prompts.path_error_menu.title"))
                        print(get_text("ui.prompts.path_error_menu.abort"))
                        sub_choice = input(get_text("ui.prompts.choose")).strip()
                        if sub_choice == "2":
                            break 
                        else:
                            continue 
                    try:
                        drive, _ = os.path.splitdrive(parent_path)
                        if drive and not os.path.exists(drive):
                            print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.path_invalid', path=parent_path)}")
                            print(get_text("ui.prompts.path_error_menu.title"))
                            print(get_text("ui.prompts.path_error_menu.abort"))
                            sub_choice = input(get_text("ui.prompts.choose")).strip()
                            if sub_choice == "2":
                                break 
                            else:
                                continue 
                    except Exception:
                        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.path_invalid', path=parent_path)}")
                        print(get_text("ui.prompts.path_error_menu.title"))
                        print(get_text("ui.prompts.path_error_menu.abort"))
                        sub_choice = input(get_text("ui.prompts.choose")).strip()
                        if sub_choice == "2":
                            break 
                        else:
                            continue 

                    if os.path.exists(parent_path) and os.path.isdir(parent_path):
                        final_path = os.path.join(parent_path, name)
                        print(get_text("ui.messages.new_path_location", path=final_path))
                        desktop_handler.create_desktop(name, final_path, create_if_missing=True)
                        break 
                    else:
                        print(f"{PREFIX_WARN} {get_text('ui.prompts.parent_dir_menu.not_found', path=parent_path)}")
                        print(get_text("ui.prompts.parent_dir_menu.title"))
                        print(get_text("ui.prompts.parent_dir_menu.create", path=parent_path))
                        print(get_text("ui.prompts.parent_dir_menu.reenter"))
                        print(get_text("ui.prompts.parent_dir_menu.abort"))
                        
                        sub_choice = input(get_text("ui.prompts.choose")).strip()

                        if sub_choice == "1":
                            try:
                                os.makedirs(parent_path)
                                print(f"{PREFIX_OK} {get_text('ui.messages.parent_created', path=parent_path)}")
                                final_path = os.path.join(parent_path, name)
                                print(get_text("ui.messages.new_path_location", path=final_path))
                                desktop_handler.create_desktop(name, final_path, create_if_missing=True)
                                break 
                            except Exception as e:
                                print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.path_invalid', path=parent_path)}")
                                input(get_text("ui.prompts.continue"))
                                continue 
                        elif sub_choice == "2":
                            continue 
                        else: 
                            print(get_text("ui.messages.aborted_no_path"))
                            break 
            else:
                print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_choice')}")
                
            input(get_text("ui.prompts.continue"))
        
        # --- 3. Einstellungen ---
        elif choice == "3":
            run_settings_menu() 
        
        # --- 0. Beenden ---
        elif choice == "0":
            print(get_text("ui.messages.exit"))
            break
            
        else:
            print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_input')}")
            input(get_text("ui.prompts.continue"))

# --- Start des Skripts ---
if __name__ == "__main__":
    clear_screen()
    run()