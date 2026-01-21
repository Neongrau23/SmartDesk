import os
import sys
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QListWidget, QListWidgetItem, QTextEdit
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt, Slot, QTimer
from PySide6.QtGui import QFontDatabase, QFont

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
    from smartdesk.shared.config import DATA_DIR, get_resource_path
    from smartdesk.shared.localization import get_text

    # Pages
    from smartdesk.ui.gui.pages.desktop_page import DesktopPage
    from smartdesk.ui.gui.pages.settings_page import SettingsPage

    # Utils
    from smartdesk.utils.app_lock import AppLock
    from smartdesk.utils.win_utils import activate_window_by_pid

except ImportError as e:
    logger.error(f"Import Error: {e}")

    # Mocks für Standalone
    def get_text(key, **kwargs):
        return key

    class FakeService:
        def get_all_desktops(self):
            return []

    desktop_service = FakeService()
    system_service = FakeService()
    hotkey_manager = FakeService()
    tray_manager = FakeService()
    DATA_DIR = "."
    DesktopPage = QWidget
    SettingsPage = QWidget

    # Mock Utils
    class AppLock:
        def __init__(self, name):
            pass

        def try_acquire(self):
            return True

        def release(self):
            pass

    def activate_window_by_pid(pid):
        pass


class SmartDeskMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_fonts()  # Fonts laden bevor UI
        self.load_ui()
        self.load_stylesheet()  # Style laden
        self.setup_pages()
        self.setup_connections()

        # Start auf Dashboard
        self.show_dashboard()

    def load_fonts(self):
        """Lädt benutzerdefinierte Schriftarten aus dem fonts/ Ordner."""
        try:
            fonts_dir = get_resource_path("smartdesk/ui/gui/fonts")

            if not os.path.exists(fonts_dir):
                return

            loaded_families = []
            for filename in os.listdir(fonts_dir):
                if filename.lower().endswith((".ttf", ".otf")):
                    font_path = os.path.join(fonts_dir, filename)
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id != -1:
                        families = QFontDatabase.applicationFontFamilies(font_id)
                        loaded_families.extend(families)
                        logger.debug(f"Font geladen: {filename} -> {families}")
                    else:
                        logger.warning(f"Konnte Font nicht laden: {filename}")
        except Exception as e:
            logger.error(f"Error loading fonts: {e}")
            return

        # Optional: Setze globale App-Font, falls Google Sans gefunden wurde
        if "Google Sans" in loaded_families:
            app = QApplication.instance()
            app.setFont(QFont("Google Sans", 10))
        elif "Product Sans" in loaded_families:
            app = QApplication.instance()
            app.setFont(QFont("Product Sans", 10))

    def load_stylesheet(self):
        """Lädt das zentrale CSS Design."""
        try:
            style_path = get_resource_path("smartdesk/ui/gui/style.qss")
            if os.path.exists(style_path):
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            else:
                logger.warning(f"Style file not found: {style_path}")
        except Exception as e:
            logger.error(f"Error loading stylesheet: {e}")

    def load_ui(self):
        loader = QUiLoader()
        ui_path = get_resource_path("smartdesk/ui/gui/designer/main.ui")

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

        # Entfernt: btn_nav_create, btn_nav_wallpaper, btn_nav_hotkeys, btn_nav_tray

        self.btn_settings = self.ui.findChild(QPushButton, "btn_nav_settings")

        # Pages (Existing placeholders)
        self.page_dash = self.ui.findChild(QWidget, "page_dashboard")

        # Dashboard Widgets
        self.text_status = self.ui.findChild(QTextEdit, "text_status_log")
        self.btn_refresh_dash = self.ui.findChild(QPushButton, "btn_refresh_dashboard")

    def setup_pages(self):
        """Initialisiert und fügt die dynamischen Pages hinzu."""
        if not self.stacked_widget:
            return

        # 1. Desktop Page
        self.page_desktop_widget = DesktopPage()
        self.stacked_widget.addWidget(self.page_desktop_widget)

        # 2. Settings Page (enthält Hotkeys)
        self.page_settings_widget = SettingsPage()
        self.stacked_widget.addWidget(self.page_settings_widget)

    def setup_connections(self):
        if self.btn_dash:
            self.btn_dash.clicked.connect(self.show_dashboard)
        if self.btn_desktops:
            self.btn_desktops.clicked.connect(self.show_desktops)
        if self.btn_settings:
            self.btn_settings.clicked.connect(self.show_settings)

        # Aufräumen: Verstecke Buttons, die nicht mehr genutzt werden, falls sie noch im UI sind
        for btn_name in ["btn_nav_create", "btn_nav_wallpaper", "btn_nav_hotkeys", "btn_nav_tray"]:
            btn = self.ui.findChild(QPushButton, btn_name)
            if btn:
                btn.setVisible(False)

        if self.btn_refresh_dash:
            self.btn_refresh_dash.clicked.connect(self.refresh_status)

    def show_dashboard(self):
        if self.stacked_widget and self.page_dash:
            self.stacked_widget.setCurrentWidget(self.page_dash)
            self.refresh_status()

    def show_desktops(self):
        if self.stacked_widget and self.page_desktop_widget:
            self.page_desktop_widget.refresh_list()
            self.stacked_widget.setCurrentWidget(self.page_desktop_widget)

    def show_settings(self):
        if self.stacked_widget and self.page_settings_widget:
            self.page_settings_widget.refresh_hotkey_status()  # Status updaten
            self.stacked_widget.setCurrentWidget(self.page_settings_widget)

    def refresh_status(self):
        if not self.text_status:
            return

        self.text_status.clear()

        try:
            # Hotkey Status
            hotkey_pid = getattr(hotkey_manager, "get_listener_pid", lambda: None)()
            status = f"Hotkey Listener PID: {hotkey_pid}\n"

            # Tray Status
            tray_status = getattr(tray_manager, "get_tray_status", lambda: (False, None))()
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
        # Wird von DesktopPage gehandelt, hier nur Dummy falls alte Verbindungen existieren
        pass


def launch_gui():
    # Single Instance Check
    lock = AppLock("manager")
    if not lock.try_acquire():
        logger.info(f"SmartDesk Manager läuft bereits (PID {lock.existing_pid}).")
        if lock.existing_pid:
            success = activate_window_by_pid(lock.existing_pid)
            if not success:
                logger.warning("Konnte existierendes Fenster nicht aktivieren.")
        return

    app = QApplication.instance() or QApplication(sys.argv)
    window = SmartDeskMainWindow()
    window.show()

    try:
        app.exec()
    finally:
        lock.release()


if __name__ == "__main__":
    launch_gui()
