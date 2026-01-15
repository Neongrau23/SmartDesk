import os
import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QListWidget, QListWidgetItem,
    QTextEdit
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt, Slot, QTimer

# --- Pfad-Hack ---
if __name__ == "__main__" or __package__ is None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    interfaces_dir = os.path.dirname(current_dir)
    smartdesk_dir = os.path.dirname(interfaces_dir)
    src_dir = os.path.dirname(smartdesk_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

# --- Logger Setup ---
try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

# --- Projekt-Imports ---
try:
    from smartdesk.core.services import desktop_service
    from smartdesk.core.services import system_service
    from smartdesk.hotkeys import hotkey_manager
    from smartdesk.ui.tray import tray_manager
    from smartdesk.shared.config import DATA_DIR
    from smartdesk.shared.localization import get_text
    
    # Pages
    from smartdesk.ui.gui.pages.desktop_page import DesktopPage
except ImportError as e:
    logger.error(f"Import Error: {e}")
    # Mocks für Standalone
    def get_text(key, **kwargs): return key
    class FakeService:
        def get_all_desktops(self): return []
    desktop_service = FakeService()
    system_service = FakeService()
    hotkey_manager = FakeService()
    tray_manager = FakeService()
    DATA_DIR = "."
    DesktopPage = QWidget

class SmartDeskMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.load_stylesheet() # Style laden
        self.setup_pages()
        self.setup_connections()
        
        # Start auf Dashboard
        self.show_dashboard()

    def load_stylesheet(self):
        """Lädt das zentrale CSS Design."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            style_path = os.path.join(current_dir, "style.qss")
            if os.path.exists(style_path):
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            else:
                logger.warning(f"Style file not found: {style_path}")
        except Exception as e:
            logger.error(f"Error loading stylesheet: {e}")

    def load_ui(self):
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "designer", "main.ui")
        
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(f"UI file not found: {ui_path}")
            sys.exit(-1)
            
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        self.setCentralWidget(self.ui)
        self.setWindowTitle("SmartDesk Manager")
        self.resize(1100, 700)

        # UI Elemente finden
        self.stacked_widget = self.ui.findChild(QStackedWidget, "stackedWidget")
        
        # Nav Buttons
        self.btn_dash = self.ui.findChild(QPushButton, "btn_nav_dashboard")
        self.btn_desktops = self.ui.findChild(QPushButton, "btn_nav_desktops")
        # btn_create und btn_wallpaper werden entfernt oder ignoriert
        
        self.btn_settings = self.ui.findChild(QPushButton, "btn_nav_settings")
        
        # Pages (Existing placeholders)
        self.page_dash = self.ui.findChild(QWidget, "page_dashboard")
        
        # Dashboard Widgets
        self.text_status = self.ui.findChild(QTextEdit, "text_status_log")
        self.btn_refresh_dash = self.ui.findChild(QPushButton, "btn_refresh_dashboard")
        

    def setup_pages(self):
        """Initialisiert und fügt die dynamischen Pages hinzu."""
        if not self.stacked_widget: return

        # 1. Desktop Page (Ersetzt die alte Desktops Page + Create + Wallpaper)
        self.page_desktop_widget = DesktopPage()
        
        # Wir wollen die alte "page_desktops" aus main.ui ersetzen oder einfach
        # die neue Page hinzufügen und nutzen.
        self.stacked_widget.addWidget(self.page_desktop_widget)

    def setup_connections(self):
        if self.btn_dash: self.btn_dash.clicked.connect(self.show_dashboard)
        if self.btn_desktops: self.btn_desktops.clicked.connect(self.show_desktops)
        
        # Ignoriere alte Buttons, falls sie im UI noch existieren, um Fehler zu vermeiden
        btn_create = self.ui.findChild(QPushButton, "btn_nav_create")
        if btn_create: btn_create.setVisible(False)
        
        btn_wallpaper = self.ui.findChild(QPushButton, "btn_nav_wallpaper")
        if btn_wallpaper: btn_wallpaper.setVisible(False)
        
        if self.btn_refresh_dash: self.btn_refresh_dash.clicked.connect(self.refresh_status)

    def show_dashboard(self):
        if self.stacked_widget and self.page_dash:
            self.stacked_widget.setCurrentWidget(self.page_dash)
            self.refresh_status()

    def show_desktops(self):
        if self.stacked_widget and self.page_desktop_widget:
            self.page_desktop_widget.refresh_list()
            self.stacked_widget.setCurrentWidget(self.page_desktop_widget)

    def refresh_status(self):
        if not self.text_status: return
        
        self.text_status.clear() 
        
        try:
            # Hotkey Status
            # (Hier müssten echte Checks rein, try-except blocks)
            hotkey_pid = getattr(hotkey_manager, 'get_listener_pid', lambda: None)()
            status = f"Hotkey Listener PID: {hotkey_pid}\n" 
            
            # Tray Status
            tray_status = getattr(tray_manager, 'get_tray_status', lambda: (False, None))()
            status += f"Tray Status: {tray_status}\n"
            
            # Active Desktop
            desktops = desktop_service.get_all_desktops()
            active = next((d.name for d in desktops if d.is_active), "None")
            status += f"Active Desktop: {active}\n"
            status += f"Data Dir: {DATA_DIR}\n"
            
            self.text_status.setPlainText(status)
        except Exception as e:
            self.text_status.setPlainText(f"Error refreshing status: {e}")

    def refresh_desktops_list(self):
        if not self.list_desktops: return
        
        self.list_desktops.clear()
        try:
            desktops = desktop_service.get_all_desktops()
            for d in desktops:
                icon = "🟢" if d.is_active else "⚪"
                item_text = f"{icon} {d.name} ({d.path})"
                item = QListWidgetItem(item_text)
                self.list_desktops.addItem(item)
        except Exception as e:
            self.list_desktops.addItem(f"Error loading desktops: {e}")


def launch_gui():
    app = QApplication.instance() or QApplication(sys.argv)
    window = SmartDeskMainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    launch_gui()