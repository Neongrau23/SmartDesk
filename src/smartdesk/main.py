import sys
import os

# Pfad zum src-Verzeichnis hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Importiere UI Module
try:
    from smartdesk.ui import cli
except ImportError as e:
    # Fallback
    try:
        from ui import cli, gui
    except ImportError:
        print(f"Import Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":

        print("Starte CLI")
        cli.run()
