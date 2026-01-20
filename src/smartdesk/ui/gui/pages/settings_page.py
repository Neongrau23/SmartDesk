import os
import logging
from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QCheckBox, QGroupBox, QPushButton, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtGui import QDesktopServices

# Importiere die existierende HotkeyPage
from .hotkey_page import HotkeyPage
from smartdesk.core.services import settings_service
from smartdesk.core.utils import registry_operations
from smartdesk.core.services.update_service import UpdateService
from smartdesk import __version__

# Logger Setup
try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.update_service = UpdateService() # UpdateService Instanz
        self.load_ui()
        self.setup_tabs()
        self.load_settings_to_ui() 
        self.setup_connections()   

    def load_ui(self):
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "ui", "settings_page.ui")
        
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(f"UI file not found: {ui_path}")
            return
            
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        layout = self.layout()
        if not layout:
            layout = QVBoxLayout(self)
            self.setLayout(layout)
            
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # Elemente finden
        self.tab_hotkeys = self.ui.findChild(QWidget, "tab_hotkeys")
        self.layout_hotkeys = self.ui.findChild(QVBoxLayout, "layout_hotkeys_container")
        self.layout_general = self.ui.findChild(QVBoxLayout, "verticalLayout_general")
        
        # General Tab Widgets
        self.check_autostart = self.ui.findChild(QCheckBox, "check_autostart")
        self.check_show_fade = self.ui.findChild(QCheckBox, "check_show_fade")
        self.btn_check_for_updates = self.ui.findChild(QPushButton, "btn_check_for_updates")
        self.lbl_update_status = self.ui.findChild(QLabel, "lbl_update_status")

    def setup_tabs(self):
        if self.layout_hotkeys:
            # HotkeyPage instanziieren und einbetten
            self.hotkey_page_widget = HotkeyPage()
            self.layout_hotkeys.addWidget(self.hotkey_page_widget)
            
    def load_settings_to_ui(self):
        """Lädt alle Einstellungen und setzt den Zustand der UI-Elemente."""
        if not self.layout_general: return

        # Auto-Switch (dynamisch erstellt, da es BETA ist)
        self.group_autopilot = QGroupBox("Auto-Pilot (BETA)")
        layout_ap = QVBoxLayout()
        self.check_autoswitch = QCheckBox("Automatisch wechseln bei erkanntem Programmstart")
        is_enabled = settings_service.get_setting("auto_switch_enabled", False)
        self.check_autoswitch.setChecked(is_enabled)
        layout_ap.addWidget(self.check_autoswitch)
        self.group_autopilot.setLayout(layout_ap)
        self.layout_general.insertWidget(0, self.group_autopilot)

        # Autostart
        if self.check_autostart:
            is_autostart = registry_operations.is_autostart_enabled()
            self.check_autostart.setChecked(is_autostart)

        # Animation Settings
        if self.check_show_fade:
            is_fade_enabled = settings_service.get_setting("show_switch_animation", True)
            self.check_show_fade.setChecked(is_fade_enabled)
            
        # Update Status
        if self.lbl_update_status:
            self.lbl_update_status.setText(f"Aktuelle Version: v{__version__}")

    def setup_connections(self):
        """Verbindet die Signale der UI-Elemente."""
        if self.check_autoswitch:
            self.check_autoswitch.toggled.connect(self.on_autoswitch_toggled)
        if self.check_autostart:
            self.check_autostart.toggled.connect(self.on_autostart_toggled)
        if self.check_show_fade:
            self.check_show_fade.toggled.connect(self.on_fade_toggled)
        if self.btn_check_for_updates:
            self.btn_check_for_updates.clicked.connect(self.check_for_updates)

    def on_autoswitch_toggled(self, checked):
        settings_service.set_setting("auto_switch_enabled", checked)
        logger.info(f"Auto-Switch setting changed to: {checked}")

    def on_autostart_toggled(self, checked):
        registry_operations.set_autostart(checked)
        logger.info(f"Autostart setting changed to: {checked}")

    def on_fade_toggled(self, checked):
        settings_service.set_setting("show_switch_animation", checked)
        logger.info(f"Fade Animation setting changed to: {checked}")

    def check_for_updates(self):
        self.lbl_update_status.setText("Suche nach Updates...")
        self.btn_check_for_updates.setEnabled(False)
        
        try:
            is_newer, latest_version = self.update_service.check_for_updates()
            
            if is_newer:
                self.lbl_update_status.setText(f"Neue Version verfügbar: v{latest_version}! Klicken zum Download.")
                self.lbl_update_status.setStyleSheet("color: green;")
                download_url = self.update_service.get_download_url()
                if download_url:
                    self.lbl_update_status.setText(f'<a href="{download_url}">Neue Version v{latest_version} verfügbar! Hier klicken zum Download.</a>')
                    self.lbl_update_status.setOpenExternalLinks(True)
                
            elif latest_version:
                self.lbl_update_status.setText(f"SmartDesk ist aktuell (v{__version__}).")
                self.lbl_update_status.setStyleSheet("color: black;")
            else:
                # This case might happen if the check fails but no exception was raised (e.g., non-200 status)
                self.lbl_update_status.setText("Fehler beim Prüfen auf Updates (API-Antwort).")
                self.lbl_update_status.setStyleSheet("color: red;")

        except Exception as e:
            logger.error(f"Update check failed with an exception: {e}")
            self.lbl_update_status.setText(f"Fehler: {e}")
            self.lbl_update_status.setStyleSheet("color: red;")

        self.btn_check_for_updates.setEnabled(True)

    def refresh_hotkey_status(self):
        """Wrapper, um den Status der eingebetteten HotkeyPage zu aktualisieren."""
        if hasattr(self, 'hotkey_page_widget'):
            self.hotkey_page_widget.refresh_status()