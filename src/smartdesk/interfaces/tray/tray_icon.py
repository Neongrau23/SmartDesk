"""
SmartDesk Tray Icon
Benötigt: pip install pystray pillow
"""

import sys
import os
import logging

# Einfaches Logging für Tray (vor allen anderen Imports)
logging.basicConfig(
    level=logging.DEBUG if os.environ.get('SMARTDESK_DEBUG') else logging.WARNING,
    format='[%(levelname)s] %(message)s',
)
logger = logging.getLogger('smartdesk.tray')

try:
    # Pfad zur Datei: .../src/smartdesk/interfaces/tray/tray_icon.py
    current_file_path = os.path.abspath(__file__)
    tray_dir = os.path.dirname(current_file_path)
    interfaces_dir = os.path.dirname(tray_dir)
    smartdesk_dir = os.path.dirname(interfaces_dir)
    src_dir = os.path.dirname(smartdesk_dir)

    if src_dir not in sys.path:
        sys.path.append(src_dir)
        logger.debug("'src' Verzeichnis zum Pfad hinzugefügt: %s", src_dir)
except Exception as e:
    logger.error("FEHLER im Path Hack: %s", e)
    sys.exit(1)

import pystray
from PIL import Image
import threading
import time
import psutil
from smartdesk.hotkeys import hotkey_manager
import subprocess

try:
    PID_FILE_DIR = os.path.join(os.environ['APPDATA'], 'SmartDesk')
    PID_FILE_PATH = os.path.join(PID_FILE_DIR, 'listener.pid')
    CONTROL_PANEL_PID_PATH = os.path.join(PID_FILE_DIR, 'control_panel.pid')
    logger.debug("Überwache PID-Datei: %s", PID_FILE_PATH)
    logger.debug("Control Panel PID: %s", CONTROL_PANEL_PID_PATH)
except Exception as e:
    logger.error("Konnte APPDATA-Pfad nicht finden: %s", e)
    PID_FILE_PATH = None
    CONTROL_PANEL_PID_PATH = None


def load_icon(filepath):
    """Lädt ein Icon aus einer Datei"""
    logger.debug("Versuche Icon zu laden: %s", filepath)
    try:
        if os.path.exists(filepath):
            logger.debug("Datei gefunden: %s", filepath)
            image = Image.open(filepath)
            image = image.resize((64, 64), Image.Resampling.LANCZOS)
            logger.debug("Icon erfolgreich geladen und skaliert")
            return image
        else:
            logger.warning("Icon nicht gefunden: %s", filepath)
            return create_fallback_icon()
    except Exception as e:
        logger.error("Fehler beim Laden des Icons: %s", e)
        return create_fallback_icon()


def create_fallback_icon(color="gray"):
    """Fallback wenn Datei nicht gefunden wird"""
    image = Image.new('RGB', (64, 64), color)
    return image


class StatusMonitor:
    def __init__(self, active_icon_path, idle_icon_path):
        self.is_active = False
        self.active_icon = load_icon(active_icon_path)
        self.idle_icon = load_icon(idle_icon_path)

    def set_active(self):
        self.is_active = True

    def set_idle(self):
        self.is_active = False

    def get_current_icon(self):
        return self.active_icon if self.is_active else self.idle_icon


# Icon-Pfade relativ zur neuen Struktur
ICONS_DIR = os.path.join(smartdesk_dir, 'shared', 'icons')
ACTIVE_ICON = os.path.join(ICONS_DIR, 'activ_icon.png')
IDLE_ICON = os.path.join(ICONS_DIR, 'idle_icon.png')

# Fallback zu alter Struktur falls nicht vorhanden
if not os.path.exists(ACTIVE_ICON):
    OLD_ICONS_DIR = os.path.join(smartdesk_dir, 'icons')
    ACTIVE_ICON = os.path.join(OLD_ICONS_DIR, 'activ_icon.png')
    IDLE_ICON = os.path.join(OLD_ICONS_DIR, 'idle_icon.png')

status = StatusMonitor(ACTIVE_ICON, IDLE_ICON)


def update_icon(icon):
    """Aktualisiert das Icon basierend auf der Existenz der listener.pid"""
    logger.debug("Update-Thread (PID-Überwachung) gestartet")

    if not PID_FILE_PATH:
        logger.error("PID_FILE_PATH ist nicht gesetzt.")
        return

    while True:
        try:
            old_state = status.is_active

            if os.path.exists(PID_FILE_PATH):
                status.set_active()
            else:
                status.set_idle()

            icon.icon = status.get_current_icon()

            if status.is_active:
                icon.title = "SmartDesk (Aktiv)"
            else:
                icon.title = "SmartDesk (Inaktiv)"

            if old_state != status.is_active:
                new_status = "AKTIV" if status.is_active else "INAKTIV"
                logger.debug("Status geändert: %s", new_status)

        except Exception as e:
            logger.error("Fehler im Update-Thread: %s", e)

        time.sleep(1)

def set_active(icon, item):
    logger.debug("'Aktivieren' geklickt.")
    hotkey_manager.start_listener()


def set_inactiv(icon, item):
    logger.debug("'Deaktivieren' geklickt.")
    hotkey_manager.stop_listener()


def open_smart_desk(icon, item):
    """Öffnet das Control Panel und verhindert Duplikate."""
    logger.debug("'SmartDesk Manager öffnen' geklickt.")

    # Prüfen, ob eine Instanz bereits läuft
    try:
        if os.path.exists(CONTROL_PANEL_PID_PATH):
            with open(CONTROL_PANEL_PID_PATH, 'r') as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                logger.warning("Control Panel (PID: %d) läuft bereits.", pid)
                # Optional: Fenster in den Vordergrund bringen
                return
    except (FileNotFoundError, ValueError, psutil.NoSuchProcess):
        pass  # PID-Datei ist alt oder Prozess existiert nicht mehr

    # Starte das Control Panel
    try:
        pythonw_executable = sys.executable
        if "python.exe" in pythonw_executable.lower():
            pythonw_executable = pythonw_executable.replace("python.exe", "pythonw.exe")

        # Pfad zur gui_main.py
        gui_main_py = os.path.join(smartdesk_dir, 'interfaces', 'gui', 'gui_main.py')
        logger.debug("Starte Control Panel: %s %s", pythonw_executable, gui_main_py)

        # Starte den Prozess
        proc = subprocess.Popen(
            [pythonw_executable, gui_main_py],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        # Speichere die neue PID
        if not os.path.exists(PID_FILE_DIR):
            os.makedirs(PID_FILE_DIR)
        with open(CONTROL_PANEL_PID_PATH, 'w') as f:
            f.write(str(proc.pid))
        logger.debug("Control Panel PID %d gespeichert.", proc.pid)

    except Exception as e:
        logger.error("Fehler beim Öffnen des Control Panels: %s", e)


def open_control_panel(icon, item):
    """Öffnet das kleine Control Panel und verhindert Duplikate."""
    logger.debug("'Control Panel öffnen' geklickt (default action).")

    # Prüfen, ob eine Instanz bereits läuft
    try:
        if os.path.exists(CONTROL_PANEL_PID_PATH):
            with open(CONTROL_PANEL_PID_PATH, 'r') as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                logger.warning("Control Panel (PID: %d) läuft bereits.", pid)
                # Sende ein "Schließ dich" Signal, damit ein neues geöffnet werden kann
                # oder bringe es in den Vordergrund (komplexer).
                # Einfacher: Verhindere doppeltes Öffnen.
                # Signal an das Panel senden, sich zu schließen
                close_signal_file = CONTROL_PANEL_PID_PATH + '.close'
                with open(close_signal_file, 'w') as f:
                    f.write('1')
                time.sleep(0.5) # Kurze Pause, damit das alte Panel sich schließen kann
        
    except (FileNotFoundError, ValueError, psutil.NoSuchProcess):
        pass  # PID-Datei ist alt oder Prozess existiert nicht mehr
    except Exception as e:
        logger.error(f"Fehler beim Prüfen des Control Panels: {e}")


    # Starte das Control Panel
    try:
        pythonw_executable = sys.executable
        if "python.exe" in pythonw_executable.lower():
            pythonw_executable = pythonw_executable.replace("python.exe", "pythonw.exe")

        # Pfad zur control_panel.py
        control_panel_py = os.path.join(smartdesk_dir, 'interfaces', 'gui', 'control_panel.py')
        logger.debug("Starte Control Panel: %s %s", pythonw_executable, control_panel_py)

        # Starte den Prozess
        proc = subprocess.Popen(
            [pythonw_executable, control_panel_py],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        # Speichere die neue PID
        if not os.path.exists(PID_FILE_DIR):
            os.makedirs(PID_FILE_DIR)
        with open(CONTROL_PANEL_PID_PATH, 'w') as f:
            f.write(str(proc.pid))
        logger.debug("Control Panel PID %d gespeichert.", proc.pid)

    except Exception as e:
        logger.error("Fehler beim Öffnen des Control Panels: %s", e)


def stop_smartdesk(icon, item):
    logger.debug("'Beenden' geklickt.")

    try:
        from smartdesk.core.utils.registry_operations import cleanup_tray_pid

        cleanup_tray_pid()
        logger.debug("Tray-PID aus Registry entfernt")
    except Exception as e:
        logger.debug("Fehler beim Cleanup: %s", e)

    icon.stop()


icon = pystray.Icon(
    "smartdesk_tray",
    status.get_current_icon(),
    "SmartDesk",
    menu=pystray.Menu(
        pystray.MenuItem("Control Panel", open_control_panel, default=True),
        pystray.MenuItem("SmartDesk Manager öffnen", open_smart_desk),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Aktivieren", set_active),
        pystray.MenuItem("Deaktivieren", set_inactiv),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Beenden", stop_smartdesk),
    ),
)

update_thread = threading.Thread(target=update_icon, args=(icon,), daemon=True)
update_thread.start()

logger.debug("Starte Tray-Icon...")
icon.run()
