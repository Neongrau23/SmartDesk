import sys
import os
import traceback
import argparse


def main():
    """Main function to run the SmartDesk application."""
    # --- PATH SETUP ---
    try:
        if getattr(sys, "frozen", False):
            project_root = os.path.dirname(sys.executable)
        else:
            project_root = os.path.dirname(os.path.abspath(__file__))

        src_dir = os.path.join(project_root, "src")
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

    except Exception as e:
        with open("smartdesk_error.log", "a") as f:
            f.write(f"FATAL ERROR: Could not configure sys.path. {e}\n")
        sys.exit(1)

    # --- ARGUMENT PARSING ---
    parser = argparse.ArgumentParser(description="SmartDesk Application")
    parser.add_argument("command", nargs="?", default="start-tray", choices=["start-tray"], help="Command to execute (default: start-tray)")
    args = parser.parse_args()

    # --- APPLICATION LAUNCH ---
    if args.command == "start-tray":
        try:
            # SmartDeskTrayApp is a QApplication subclass, so we just instantiate it
            from smartdesk.ui.tray.tray_icon import SmartDeskTrayApp

            app = SmartDeskTrayApp(sys.argv)
            sys.exit(app.exec())

        except ImportError as e:
            with open("smartdesk_error.log", "a") as f:
                f.write("----------- DETAILED IMPORT TRACEBACK -----------\\n")
                traceback.print_exc(file=f)
                f.write(f"\nIMPORT ERROR: {e}\n")
            sys.exit(1)
        except Exception as e:
            with open("smartdesk_error.log", "a") as f:
                f.write("----------- DETAILED GENERIC TRACEBACK -----------\\n")
                traceback.print_exc(file=f)
                f.write(f"\nAn unexpected error occurred: {e}\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
