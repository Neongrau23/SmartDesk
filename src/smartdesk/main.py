import sys
import os

# Pfad zum src-Verzeichnis hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importiere UI Module
try:
    from smartdesk.ui import cli
    from smartdesk.ui import gui
except ImportError as e:
    # Fallback
    try:
        from ui import cli, gui
    except ImportError:
        print(f"Import Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Einfache Logik: Wenn '--cli' als Argument übergeben wird, starte Textmodus.
    # Sonst starte GUI.
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        print("Starte CLI Modus...")
        cli.run()
    else:
        # GUI Starten
        gui.run()
        