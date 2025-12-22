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


def create_desktop(icon, item):
    """Startet die GUI-Version ('create-gui') ohne Konsole."""
    logger.debug("'Desktop Erstellen' geklickt (GUI-Version).")
    try:
        pythonw_executable = sys.executable
        if "python.exe" in pythonw_executable.lower():
            pythonw_executable = pythonw_executable.replace("python.exe", "pythonw.exe")

        main_py = os.path.join(smartdesk_dir, 'main.py')

        logger.debug("Starte: %s %s create-gui", pythonw_executable, main_py)

        subprocess.Popen(
            [pythonw_executable, main_py, "create-gui"],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except Exception as e:
        logger.error("Fehler beim Erstellen der GUI: %s", e)


def set_active(icon, item):
    logger.debug("'Aktivieren' geklickt.")
    hotkey_manager.start_listener()


def set_inactiv(icon, item):
    logger.debug("'Deaktivieren' geklickt.")
    hotkey_manager.stop_listener()


def is_control_panel_running():
    """Prüft ob das Control Panel läuft anhand der PID-Datei."""
    if not CONTROL_PANEL_PID_PATH:
        return False
    try:
        if os.path.exists(CONTROL_PANEL_PID_PATH):
            with open(CONTROL_PANEL_PID_PATH, 'r') as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                    return True
            os.remove(CONTROL_PANEL_PID_PATH)
    except Exception as e:
        logger.debug("Fehler beim Prüfen der Control Panel PID: %s", e)
    return False


def close_control_panel():
    """Sendet ein Schließ-Signal an das Control Panel."""
    if not CONTROL_PANEL_PID_PATH:
        return False
    try:
        if os.path.exists(CONTROL_PANEL_PID_PATH):
            signal_file = CONTROL_PANEL_PID_PATH + '.close'
            with open(signal_file, 'w') as f:
                f.write('close')
            logger.debug("Schließ-Signal an Control Panel gesendet")
            return True
    except Exception as e:
        logger.error("Fehler beim Senden des Schließ-Signals: %s", e)
    return False


def on_primary_click(icon, item):
    """Toggle: Öffnet oder schließt das Control Panel."""
    logger.debug("Primär-Klick erkannt...")

    if is_control_panel_running():
        logger.debug("Control Panel läuft - schließe es...")
        close_control_panel()
        return

    logger.debug("Öffne Control Panel...")
    try:
        pythonw_executable = sys.executable
        if "python.exe" in pythonw_executable.lower():
            pythonw_executable = pythonw_executable.replace("python.exe", "pythonw.exe")

        control_panel_py = os.path.join(interfaces_dir, 'gui', 'control_panel.py')

        logger.debug("Starte: %s %s", pythonw_executable, control_panel_py)

        proc = subprocess.Popen(
            [pythonw_executable, control_panel_py],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        if CONTROL_PANEL_PID_PATH:
            os.makedirs(PID_FILE_DIR, exist_ok=True)
            with open(CONTROL_PANEL_PID_PATH, 'w') as f:
                f.write(str(proc.pid))
            logger.debug("Control Panel PID gespeichert: %s", proc.pid)

    except Exception as e:
        logger.error("Fehler beim Öffnen des Control Panels: %s", e)


def open_smart_desk(icon, item):
    """Startet das Haupt-CLI-Menü in einer NEUEN Konsole."""
    logger.debug("'SmartDesk Öffnen' geklickt")
    try:
        main_py = os.path.join(smartdesk_dir, 'main.py')

        python_executable = sys.executable
        if "pythonw.exe" in python_executable.lower():
            python_executable = python_executable.replace("pythonw.exe", "python.exe")

        logger.debug("Starte: %s %s in neuer Konsole", python_executable, main_py)

        subprocess.Popen(
            [python_executable, main_py], creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        logger.error("Fehler beim Öffnen: %s", e)


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
    "status_indicator",
    status.get_current_icon(),
    "○ Bereit",
    menu=pystray.Menu(
        pystray.MenuItem(
            "Primary Action", on_primary_click, default=True, visible=False
        ),
        pystray.MenuItem("SmartDesk Öffnen", open_smart_desk),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Desktop Erstellen", create_desktop),
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
