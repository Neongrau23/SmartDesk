import sys
import os
import traceback

# --- PATH SETUP ---
try:
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_root, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
except Exception as e:
    print(f"FATAL ERROR: Could not configure sys.path. {e}")
    sys.exit(1)

# --- DEBUG & APPLICATION LAUNCH ---
try:
    from smartdesk.interfaces.tray.tray_icon import SmartDeskTrayApp
    app = SmartDeskTrayApp(sys.argv)
    sys.exit(app.exec())

except ImportError as e:
    # Gib den vollständigen Import-Traceback aus
    print("----------- DETAILED IMPORT TRACEBACK -----------")
    traceback.print_exc()
    print("-------------------------------------------------")
    print(f"\nIMPORT ERROR: {e}")
    print("Please check the file mentioned in the traceback above.")
    sys.exit(1)
except Exception as e:
    print("----------- DETAILED GENERIC TRACEBACK -----------")
    traceback.print_exc()
    print("--------------------------------------------------")
    print(f"\nAn unexpected error occurred: {e}")
    sys.exit(1)