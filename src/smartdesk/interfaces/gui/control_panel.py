import logging
import os
import subprocess
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QTimer, QPropertyAnimation, QEasingCurve, QRect, Qt
from .gui_create import CreateDesktopWindow
from PySide6.QtGui import QScreen

# --- Pfad-Hack für direkten Aufruf ---
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
    from smartdesk.hotkeys import hotkey_manager
    from smartdesk.shared.localization import get_text
except ImportError as e:
    logger.error(f"FATALER FEHLER: {e}")
    def get_text(key, **kwargs): return key.split('.')[-1]
    class FakeHotkeys:
        def start_listener(self): pass
        def stop_listener(self): pass
    hotkey_manager = FakeHotkeys()
    class FakeDesktopService:
        def get_all_desktops(self): return []
    desktop_service = FakeDesktopService()


# --- PID-Datei-Pfad ---
try:
    PID_FILE_DIR = os.path.join(os.environ['APPDATA'], 'SmartDesk')
    PID_FILE_PATH = os.path.join(PID_FILE_DIR, 'listener.pid')
    CONTROL_PANEL_PID_PATH = os.path.join(PID_FILE_DIR, 'control_panel.pid')
    GUI_MAIN_PID_PATH = os.path.join(PID_FILE_DIR, 'gui_main.pid')
except Exception as e:
    logger.error(f"Konnte APPDATA-Pfad nicht finden: {e}")
    PID_FILE_PATH = None
    CONTROL_PANEL_PID_PATH = None
    GUI_MAIN_PID_PATH = None


def cleanup_control_panel_pid():
    """Entfernt die Control Panel PID-Datei beim Schließen."""
    try:
        if CONTROL_PANEL_PID_PATH and os.path.exists(CONTROL_PANEL_PID_PATH):
            os.remove(CONTROL_PANEL_PID_PATH)
            logger.debug("PID-Datei entfernt")
    except Exception as e:
        logger.error(f"Fehler beim Entfernen der PID-Datei: {e}")


class SmartDeskControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.is_active = False
        self.is_closing = False
        self.animation = None
        self.create_window = None

        # UI aus .ui-Datei laden
        self.load_ui()

        # Fensterkonfiguration
        self.setWindowTitle(get_text("gui.control_panel.title"))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # UI-Elemente zuordnen
        self.desktop_name_label = self.findChild(QLabel, "label_desktop_name")
        self.btn_open = self.findChild(QPushButton, "btn_gui_main")
        self.btn_create = self.findChild(QPushButton, "btn_gui_create")
        self.btn_manage = self.findChild(QPushButton, "btn_gui_manage")
        self.toggle_btn = self.findChild(QPushButton, "btn_toggle_hotkey")

        # Stylesheets für Buttons
        self.active_style = "background-color: #d9534f; color: white;"
        self.inactive_style = "background-color: #3c3c3c; color: white;"
        self.hover_active_style = "background-color: #c9302c; color: white;"
        self.hover_inactive_style = "background-color: #4a4a4a; color: white;"

        # Signale verbinden
        self.btn_open.clicked.connect(self.open_smartdesk)
        self.btn_create.clicked.connect(self.create_desktop)
        self.btn_manage.clicked.connect(self.manage_desktops)
        self.toggle_btn.clicked.connect(self.toggle_smartdesk)

        # Position und Animation vorbereiten
        self.setup_positioning()
        
        # Status-Updates
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.timeout.connect(self.update_active_desktop_label)
        self.status_timer.start(500)
        self.update_status()
        self.update_active_desktop_label()

    def load_ui(self):
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file_path = os.path.join(current_dir, "control_panel.ui")
        ui_file = QFile(ui_file_path)

        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(f"Cannot open UI file: {ui_file.errorString()}")
            sys.exit(-1)

        # Lädt die UI in dieses Widget als Parent
        loader.load(ui_file, self)
        ui_file.close()

    def setup_positioning(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        self.window_width = self.frameGeometry().width()
        self.window_height = self.frameGeometry().height()
        
        padding_x = -200
        padding_y = -170
        
        self.target_x = screen_geometry.width() - self.window_width - padding_x
        self.target_y = screen_geometry.height() - self.window_height - padding_y
        self.start_x = screen_geometry.width()

        self.setGeometry(self.start_x, self.target_y, self.window_width, self.window_height)

    def enterEvent(self, event):
        """Wird aufgerufen, wenn die Maus das Fenster betritt."""
        super().enterEvent(event)
        self.update_button_styles_on_hover(True)

    def leaveEvent(self, event):
        """Wird aufgerufen, wenn die Maus das Fenster verlässt."""
        super().leaveEvent(event)
        self.update_button_styles_on_hover(False)

    def update_button_styles_on_hover(self, is_hovering):
        """Aktualisiert den Button-Stil basierend auf dem Hover-Zustand."""
        if self.is_active:
            self.toggle_btn.setStyleSheet(self.hover_active_style if is_hovering else self.active_style)
        else:
            self.toggle_btn.setStyleSheet(self.hover_inactive_style if is_hovering else self.inactive_style)

    def show_animated(self):
        self.show()
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(self.start_x, self.target_y, self.width(), self.height()))
        self.animation.setEndValue(QRect(self.target_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def close_panel(self):
        if self.is_closing:
            return
        self.is_closing = True
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(self.start_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        self.animation.finished.connect(self.close)
        self.animation.start()

    def event(self, event):
        # Schließen, wenn das Fenster den Fokus verliert
        if event.type() == event.Type.WindowDeactivate and not self.is_closing:
             self.close_panel()
        return super().event(event)
    
    def closeEvent(self, event):
        self.status_timer.stop()
        cleanup_control_panel_pid()
        super().closeEvent(event)

    def update_status(self):
        if PID_FILE_PATH and os.path.exists(PID_FILE_PATH):
            if not self.is_active:
                self.is_active = True
                self.toggle_btn.setText(get_text("gui.control_panel.button_hotkey_deactivate"))
                self.toggle_btn.setStyleSheet(self.active_style)
        else:
            if self.is_active:
                self.is_active = False
                self.toggle_btn.setText(get_text("gui.control_panel.button_hotkey_activate"))
                self.toggle_btn.setStyleSheet(self.inactive_style)

    def update_active_desktop_label(self):
        if not self.desktop_name_label: return
        try:
            desktops = desktop_service.get_all_desktops()
            active_desktop = next((d for d in desktops if d.is_active), None)
            if active_desktop:
                self.desktop_name_label.setText(get_text("gui.control_panel.desktop_label_template", name=active_desktop.name))
            else:
                self.desktop_name_label.setText(get_text("gui.control_panel.desktop_label_none"))
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Desktops: {e}")
            self.desktop_name_label.setText(get_text("gui.control_panel.desktop_label_error"))

    def toggle_smartdesk(self):
        if self.is_active: self.deactivate_smartdesk()
        else: self.activate_smartdesk()

    def activate_smartdesk(self):
        logger.info("Aktiviere SmartDesk...")
        hotkey_manager.start_listener()
        QTimer.singleShot(500, self.update_status)

    def deactivate_smartdesk(self):
        logger.info("Deaktiviere SmartDesk...")
        hotkey_manager.stop_listener()
        QTimer.singleShot(500, self.update_status)

    def _run_gui_script(self, script_name):
        try:
            logger.info(f"Starte {script_name} GUI...")
            pythonw_executable = sys.executable.replace("python.exe", "pythonw.exe")
            script_path = os.path.join(os.path.dirname(__file__), script_name)
            
            subprocess.Popen([pythonw_executable, script_path], creationflags=subprocess.CREATE_NO_WINDOW)
            self.close_panel()
        except Exception as e:
            logger.error(f"Fehler beim Starten von {script_name}: {e}")

    def open_smartdesk(self):
        self._run_gui_script('gui_main.py')

    def create_desktop(self):
        self.create_window = CreateDesktopWindow()
        self.create_window.show()
        self.close_panel()

    def manage_desktops(self):
        self._run_gui_script('gui_manage.py')


def show_control_panel():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    panel = SmartDeskControlPanel()
    panel.show_animated()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    logger.info("Starte Control Panel im Testmodus...")
    show_control_panel()