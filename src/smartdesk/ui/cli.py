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
                    # --- LOKALISIERT ---
                    print(get_text("ui.errors.invalid_number"))
            except ValueError:
                # --- LOKALISIERT ---
                print(get_text("ui.errors.invalid_number"))
            # --- LOKALISIERT ---
            input(get_text("ui.prompts.continue"))

        # --- 3. Icons speichern ---
        elif choice == "3":
            # --- LOKALISIERT (Handler gibt eigene Meldungen aus) ---
            print(get_text("desktop_handler.info.saving_icons", name="...")) # Platzhalter, Handler weiß es besser
            if desktop_handler.save_current_desktop_icons():
                print(f"{PREFIX_OK} {get_text('desktop_handler.success.save_icons', name='...')}") # Platzhalter
            else:
                print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.save_icons', e='...')}") # Platzhalter
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
            # --- LOKALISIERT ---
            print(get_text("ui.errors.invalid_input"))
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
                        time.sleep(3) 

                        print(get_text("ui.messages.syncing_icons"))
                        desktop_handler.sync_desktop_state_and_apply_icons()
                        print(f"{PREFIX_OK} {get_text('ui.messages.switch_success', name=target_desktop.name)}")
                        
                    else:
                        pass
                else:
                    # --- LOKALISIERT ---
                    print(get_text("ui.errors.invalid_number"))
            except ValueError:
                # --- LOKALISIERT ---
                print(get_text("ui.errors.invalid_number"))
            # --- LOKALISIERT ---
            input(get_text("ui.prompts.continue"))

        # --- 2. Neuen Desktop erstellen ---
        elif choice == "2":
            # --- LOKALISIERT ---
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
            final_path = ""

            if mode == "1":
                final_path = input(get_text("ui.prompts.existing_path")).strip()

            elif mode == "2":
                parent_path = input(get_text("ui.prompts.new_path_parent")).strip()
                
                if parent_path:
                    final_path = os.path.join(parent_path, name)
                    print(get_text("ui.messages.new_path_location", path=final_path))
                else:
                    print(f"{PREFIX_ERROR} {get_text('ui.errors.base_dir_empty')}")
            else:
                # --- LOKALISIERT ---
                print(get_text("ui.errors.invalid_choice"))
                input(get_text("ui.prompts.continue"))
                continue

            if final_path:
                # Handler gibt lokalisierte Meldungen aus
                desktop_handler.create_desktop(name, final_path)
            else:
                # --- LOKALISIERT ---
                print(get_text("ui.messages.aborted_no_path"))
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
            # --- LOKALISIERT ---
            print(get_text("ui.errors.invalid_input"))
            input(get_text("ui.prompts.continue"))

# --- Start des Skripts (unverändert) ---
if __name__ == "__main__":
    clear_screen()
    run()
    