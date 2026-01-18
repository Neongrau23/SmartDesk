import os
import logging
from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QCheckBox, QGroupBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice

# Importiere die existierende HotkeyPage
from .hotkey_page import HotkeyPage
from smartdesk.core.services import settings_service

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
        self.load_ui()
        self.setup_tabs()
        self.setup_general_tab()

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

    def setup_tabs(self):
        if self.layout_hotkeys:
            # HotkeyPage instanziieren und einbetten
            self.hotkey_page_widget = HotkeyPage()
            self.layout_hotkeys.addWidget(self.hotkey_page_widget)
            
    def setup_general_tab(self):
        if not self.layout_general: return

        # Auto-Pilot Group
        self.group_autopilot = QGroupBox("Auto-Pilot (BETA)")
        layout_ap = QVBoxLayout()
        
        self.check_autoswitch = QCheckBox("Automatisch wechseln bei erkanntem Programmstart")
        self.check_autoswitch.setToolTip("Wechselt automatisch den Desktop, wenn verknüpfte Programme gestartet werden.")
        
        # Load state
        is_enabled = settings_service.get_setting("auto_switch_enabled", False)
        self.check_autoswitch.setChecked(is_enabled)
        
        self.check_autoswitch.toggled.connect(self.on_autoswitch_toggled)
        
        layout_ap.addWidget(self.check_autoswitch)
        self.group_autopilot.setLayout(layout_ap)
        
        # Insert at top (index 0)
        self.layout_general.insertWidget(0, self.group_autopilot)

    def on_autoswitch_toggled(self, checked):
        settings_service.set_setting("auto_switch_enabled", checked)
        logger.info(f"Auto-Switch setting changed to: {checked}")

    def refresh_hotkey_status(self):
        """Wrapper, um den Status der eingebetteten HotkeyPage zu aktualisieren."""
        if hasattr(self, 'hotkey_page_widget'):
            self.hotkey_page_widget.refresh_status()
