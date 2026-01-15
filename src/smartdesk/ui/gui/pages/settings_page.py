import os
import logging
from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice

# Importiere die existierende HotkeyPage
from .hotkey_page import HotkeyPage

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

    def setup_tabs(self):
        if self.layout_hotkeys:
            # HotkeyPage instanziieren und einbetten
            self.hotkey_page_widget = HotkeyPage()
            
            # Da HotkeyPage einen eigenen Titel hat ("Hotkey Verwaltung"), 
            # können wir diesen ggf. ausblenden, da der Tab schon so heißt.
            # Aber wir lassen es erstmal so.
            
            self.layout_hotkeys.addWidget(self.hotkey_page_widget)
            
    def refresh_hotkey_status(self):
        """Wrapper, um den Status der eingebetteten HotkeyPage zu aktualisieren."""
        if hasattr(self, 'hotkey_page_widget'):
            self.hotkey_page_widget.refresh_status()
