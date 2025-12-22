import sys
import os
import logging
import threading
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PIL import Image

# --- Grundlegendes Logging ---
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
logger = logging.getLogger('smartdesk.tray')

# --- Path Hack ---
try:
    current_file_path = os.path.abspath(__file__)
    tray_dir = os.path.dirname(current_file_path)
    interfaces_dir = os.path.dirname(tray_dir)
    smartdesk_dir = os.path.dirname(interfaces_dir)
    src_dir = os.path.dirname(smartdesk_dir)
    if src_dir not in sys.path:
        sys.path.append(src_dir)
except Exception as e:
    logger.error(f"FEHLER im Path Hack: {e}")
    sys.exit(1)

# --- Projekt-Imports ---
from smartdesk.hotkeys import hotkey_manager
from smartdesk.interfaces.gui.control_panel import SmartDeskControlPanel
from smartdesk.shared.localization import get_text, init_localization

# --- PID-Management ---
PID_FILE_DIR = os.path.join(os.environ.get('APPDATA', ''), 'SmartDesk')
LISTENER_PID_FILE = os.path.join(PID_FILE_DIR, 'listener.pid')

class SmartDeskTrayApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False) 

        # Lade explizit die Lokalisierung, bevor UI-Elemente erstellt werden
        init_localization()

        self.control_panel = None
        
        # --- Icons Laden ---
        icon_path = os.path.join(smartdesk_dir, 'icons')
        self.idle_icon = QIcon(os.path.join(icon_path, 'idle_icon.png'))
        self.active_icon = QIcon(os.path.join(icon_path, 'activ_icon.png'))

        # --- Tray Icon Erstellen ---
        self.tray_icon = QSystemTrayIcon(self.idle_icon, self)
        self.tray_icon.setToolTip("SmartDesk")
        
        # --- Menü Erstellen ---
        menu = QMenu()
        
        open_panel_action = QAction(get_text("tray.menu.control_panel"), self)
        open_panel_action.triggered.connect(self.open_control_panel)
        menu.addAction(open_panel_action)

        # Platzhalter für "SmartDesk Manager öffnen"
        open_manager_action = QAction(get_text("tray.menu.manager"), self)
        open_manager_action.triggered.connect(self.open_manager_placeholder)
        menu.addAction(open_manager_action)
        
        menu.addSeparator()

        self.activate_action = QAction(get_text("tray.menu.activate"), self)
        self.activate_action.triggered.connect(self.activate_hotkeys)
        menu.addAction(self.activate_action)
        
        self.deactivate_action = QAction(get_text("tray.menu.deactivate"), self)
        self.deactivate_action.triggered.connect(self.deactivate_hotkeys)
        menu.addAction(self.deactivate_action)
        
        menu.addSeparator()
        
        quit_action = QAction(get_text("tray.menu.quit"), self)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        # Linksklick-Aktion hinzufügen
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

        # --- Status-Überwachung ---
        self.status_thread = threading.Thread(target=self.monitor_status, daemon=True)
        self.status_thread.start()

    def on_tray_activated(self, reason):
        """Wird aufgerufen, wenn auf das Tray-Icon geklickt wird."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger: # Trigger ist der normale Linksklick
            self.open_control_panel()

    def open_control_panel(self):
        if self.control_panel is None or not self.control_panel.isVisible():
            self.control_panel = SmartDeskControlPanel()
            self.control_panel.show_animated()
            # Verbinde das "destroyed"-Signal, um die Referenz zu löschen
            self.control_panel.destroyed.connect(self.on_panel_closed)

    def on_panel_closed(self):
        self.control_panel = None

    def open_manager_placeholder(self):
        # Hier kann später die Logik für den Manager implementiert werden
        logger.info("Funktion 'SmartDesk Manager öffnen' ist noch nicht implementiert.")
        pass

    def activate_hotkeys(self):
        hotkey_manager.start_listener()

    def deactivate_hotkeys(self):
        hotkey_manager.stop_listener()
        
    def monitor_status(self):
        while True:
            if os.path.exists(LISTENER_PID_FILE):
                self.tray_icon.setIcon(self.active_icon)
                self.tray_icon.setToolTip("SmartDesk (Aktiv)")
                self.activate_action.setEnabled(False)
                self.deactivate_action.setEnabled(True)
            else:
                self.tray_icon.setIcon(self.idle_icon)
                self.tray_icon.setToolTip("SmartDesk (Inaktiv)")
                self.activate_action.setEnabled(True)
                self.deactivate_action.setEnabled(False)
            threading.Event().wait(1)


if __name__ == '__main__':
    try:
        from smartdesk.core.utils.registry_operations import save_tray_pid, cleanup_tray_pid
        save_tray_pid(os.getpid())
        
        app = SmartDeskTrayApp(sys.argv)
        exit_code = app.exec()
        
        cleanup_tray_pid()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fehler beim Starten der Tray-Anwendung: {e}")
        sys.exit(1)