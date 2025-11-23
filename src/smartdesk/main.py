import sys
import os

# ist dieser Pfad-Hack für lokale Tests.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importiere UI Module
try:
    from smartdesk.ui import cli
    from smartdesk.handlers import desktop_handler
    from smartdesk.handlers import system_manager # system_manager für switch
    from smartdesk.ui.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN # <-- NEU
except ImportError as e:
    # Fallback, falls die Struktur anders ist oder es lokal läuft
    try:
        from ui import cli
        from handlers import desktop_handler
        from handlers import system_manager
    except ImportError:
        print(f"Import Fehler: {e}")
        print("Stelle sicher, dass du das Skript aus dem Projekt-Root ausführst")
        print("oder dass das Paket korrekt installiert ist.")
        sys.exit(1)

# --- FAKE HANDLER FÜR DEN FALL EINES FEHLERS (aus cli.py übernommen) ---
# (Wird benötigt, falls nur einer der Imports fehlschlägt)
if 'desktop_handler' not in locals():
    print("Warnung: desktop_handler konnte nicht geladen werden.")
    class FakeHandler:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                print(f"FEHLER: {name} konnte nicht geladen werden!")
            return method
    desktop_handler = FakeHandler()
    system_manager = FakeHandler()


if __name__ == "__main__":
    
    args = sys.argv[1:] # Hole alle Argumente nach dem Skriptnamen

    # --- KEINE ARGUMENTE: Interaktives Menü ---
    if not args:
        print("Starte interaktives Menü...")
        cli.run()
        
    # --- ARGUMENTE VORHANDEN: Befehl parsen ---
    else:
        command = args[0].lower()
        
        # --- BEFEHL: delete ---
        # Erfüllt Akzeptanzkriterium: smartdesk delete <desktop-name>
        if command == "delete":
            if len(args) < 2:
                # --- VERWENDET JETZT PREFIX_ERROR ---
                print(f"{PREFIX_ERROR} Fehler: Desktop-Name fehlt.")
                print("Verwendung: python -m smartdesk.main delete <desktop-name> [--delete-folder]")
            else:
                name = args[1]
                # Bonus: Erlaube das Löschen des Ordners per Flag
                delete_folder = "--delete-folder" in args or "-f" in args
                
                # Rufe den Handler auf.
                # Der Handler stellt die Bestätigungsfrage (y/n)
                desktop_handler.delete_desktop(name, delete_folder)
        
        # --- BEFEHL: switch (Beispiel für Erweiterung) ---
        elif command == "switch":
            if len(args) < 2:
                 # --- VERWENDET JETZT PREFIX_ERROR ---
                 print(f"{PREFIX_ERROR} Fehler: Desktop-Name fehlt.")
                 print("Verwendung: python -m smartdesk.main switch <desktop-name>")
            else:
                name = args[1]
                print(f"Versuche, zu '{name}' zu wechseln...")
                # Der Handler (switch_to_desktop) macht die Vorarbeit (Registry)
                if desktop_handler.switch_to_desktop(name):
                    print("Starte Explorer neu...")
                    system_manager.restart_explorer()
                    print("Warte auf Explorer-Initialisierung...")
                    import time
                    time.sleep(3) # Kurze Pause
                    # Der Handler (sync...) macht die Nacharbeit (Icons)
                    desktop_handler.sync_desktop_state_and_apply_icons()
                    # --- VERWENDET JETZT PREFIX_OK ---
                    print(f"{PREFIX_OK} Wechsel zu '{name}' abgeschlossen.")
                # 'else' wird vom Handler abgedeckt (Fehler oder bereits aktiv)

        # --- BEFEHL: list (Beispiel für Erweiterung) ---
        elif command == "list":
             desktops = desktop_handler.get_all_desktops()
             if not desktops:
                print("Keine Desktops vorhanden.")
             else:
                print("\nVerfügbare Desktops:")
                for d in desktops:
                    status = "[AKTIV]" if d.is_active else "[ ]"
                    print(f"{status} {d.name} -> {d.path}")

        # --- UNBEKANNTER BEFEHL ---
        else:
            print(f"Unbekannter Befehl: {command}")
            print("Verfügbare Befehle: delete, switch, list")
            print("Oder starte ohne Argumente für das interaktive Menü.")
            