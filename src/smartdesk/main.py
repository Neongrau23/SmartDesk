import sys
import os

# ist dieser Pfad-Hack für lokale Tests.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# --- NEUER IMPORT für Lokalisierung ---
try:
    from smartdesk.localization import get_text
except ImportError:
    # Fallback, falls Pfad-Hack nicht funktioniert
    print("CRITICAL: localization.py nicht gefunden.")
    # Dummy-Funktion, damit der Rest nicht abstürzt
    def get_text(key, **kwargs):
        return key

# Importiere UI Module
try:
    from smartdesk.ui import cli
    from smartdesk.handlers import desktop_handler
    from smartdesk.handlers import system_manager 
    from smartdesk.ui.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN 
except ImportError as e:
    try:
        from ui import cli
        from handlers import desktop_handler
        from handlers import system_manager
    except ImportError:
        # --- LOKALISIERT ---
        print(get_text("MAIN_ERROR_IMPORT", e=e))
        print(get_text("MAIN_ERROR_IMPORT_HINT_1"))
        print(get_text("MAIN_ERROR_IMPORT_HINT_2"))
        sys.exit(1)

# --- FAKE HANDLER FÜR DEN FALL EINES FEHLERS ---
if 'desktop_handler' not in locals():
    # --- LOKALISIERT ---
    print(get_text("MAIN_WARN_HANDLER_LOAD_FAILED", handler="desktop_handler"))
    class FakeHandler:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                # --- LOKALISIERT ---
                print(get_text("MAIN_ERROR_HANDLER_CALL_FAILED", name=name))
            return method
    desktop_handler = FakeHandler()
    system_manager = FakeHandler()


if __name__ == "__main__":
    
    args = sys.argv[1:] 

    # --- KEINE ARGUMENTE: Interaktives Menü ---
    if not args:
        # --- LOKALISIERT ---
        print(get_text("MAIN_INFO_STARTING_INTERACTIVE"))
        cli.run()
        
    # --- ARGUMENTE VORHANDEN: Befehl parsen ---
    else:
        command = args[0].lower()
        
        # --- BEFEHL: delete ---
        if command == "delete":
            if len(args) < 2:
                # --- LOKALISIERT ---
                print(f"{PREFIX_ERROR} {get_text('MAIN_ERROR_NAME_MISSING')}")
                print(get_text("MAIN_USAGE_DELETE"))
            else:
                name = args[1]
                delete_folder = "--delete-folder" in args or "-f" in args
                
                # Handler gibt lokalisierte Meldungen aus
                desktop_handler.delete_desktop(name, delete_folder)
        
        # --- BEFEHL: switch ---
        elif command == "switch":
            if len(args) < 2:
                 # --- LOKALISIERT ---
                 print(f"{PREFIX_ERROR} {get_text('MAIN_ERROR_NAME_MISSING')}")
                 print(get_text("MAIN_USAGE_SWITCH"))
            else:
                name = args[1]
                # --- LOKALISIERT ---
                print(get_text("MAIN_INFO_SWITCHING_TO", name=name))
                
                if desktop_handler.switch_to_desktop(name):
                    # --- LOKALISIERT ---
                    print(get_text("MAIN_INFO_RESTARTING_EXPLORER"))
                    system_manager.restart_explorer()
                    print(get_text("MAIN_INFO_WAITING_EXPLORER"))
                    import time
                    time.sleep(3) 
                    
                    desktop_handler.sync_desktop_state_and_apply_icons()
                    print(f"{PREFIX_OK} {get_text('MAIN_SUCCESS_SWITCH', name=name)}")

        # --- BEFEHL: list ---
        elif command == "list":
             desktops = desktop_handler.get_all_desktops()
             if not desktops:
                # --- LOKALISIERT ---
                print(get_text("INFO_NO_DESKTOPS"))
             else:
                # --- LOKALISIERT ---
                print(get_text("MAIN_INFO_LIST_HEADER"))
                for d in desktops:
                    # --- LOKALISIERT ---
                    status = f"[{get_text('STATUS_ACTIVE')}]" if d.is_active else f"[{get_text('STATUS_INACTIVE')}]"
                    print(f"{status} {d.name} -> {d.path}")

        # --- UNBEKANNTER BEFEHL ---
        else:
            # --- LOKALISIERT ---
            print(get_text("MAIN_ERROR_UNKNOWN_COMMAND", command=command))
            print(get_text("MAIN_INFO_AVAILABLE_COMMANDS"))
            print(get_text("MAIN_INFO_HINT_INTERACTIVE"))
            