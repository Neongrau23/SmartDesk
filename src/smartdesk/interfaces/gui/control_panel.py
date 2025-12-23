import logging
import os
import subprocess
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QTimer, QPropertyAnimation, QEasingCurve, QRect, Qt

try:
    from .gui_create import CreateDesktopWindow
except ImportError:
    from gui_create import CreateDesktopWindow

# --- Logger Setup ---
try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

# --- Projekt-Imports & Mocking ---
try:
    from smartdesk.core.services import desktop_service
    from smartdesk.hotkeys import hotkey_manager
    from smartdesk.shared.localization import get_text
except ImportError:
    # Verbesserter Mock für Texte
    def get_text(key, **kwargs): 
        return key.split('.')[-1].replace('_', ' ').title()
    
    class FakeHotkeys:
        def start_listener(self): 
            # Simuliere Starten durch Erstellen der PID Datei für Tests
            pid_path = os.path.join(os.environ.get('APPDATA', '.'), 'SmartDesk', 'listener.pid')
            with open(pid_path, 'w') as f: f.write("1234")
            logger.info("Mock: Listener gestartet")

        def stop_listener(self): 
            # Simuliere Stoppen
            pid_path = os.path.join(os.environ.get('APPDATA', '.'), 'SmartDesk', 'listener.pid')
            if os.path.exists(pid_path): os.remove(pid_path)
            logger.info("Mock: Listener gestoppt")

    hotkey_manager = FakeHotkeys()
    class FakeDesktopService:
        def get_all_desktops(self): return []
    desktop_service = FakeDesktopService()

# --- PID Paths ---
PID_FILE_DIR = os.path.join(os.environ.get('APPDATA', '.'), 'SmartDesk')
CONTROL_PANEL_PID_PATH = os.path.join(PID_FILE_DIR, 'control_panel.pid')
PID_FILE_PATH = os.path.join(PID_FILE_DIR, 'listener.pid') # WICHTIG: Pfad wieder hinzugefügt

def cleanup_control_panel_pid():
    try:
        if CONTROL_PANEL_PID_PATH and os.path.exists(CONTROL_PANEL_PID_PATH):
            os.remove(CONTROL_PANEL_PID_PATH)
    except: pass

class SmartDeskControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.is_active = False # Interner Status
        self.is_closing = False
        self.animation = None
        self.create_window = None 

        self.load_ui()

        self.setWindowTitle("Control Panel")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.desktop_name_label = self.findChild(QLabel, "label_desktop_name")
        self.btn_open = self.findChild(QPushButton, "btn_gui_main")
        self.btn_create = self.findChild(QPushButton, "btn_gui_create")
        self.btn_manage = self.findChild(QPushButton, "btn_gui_manage")
        self.toggle_btn = self.findChild(QPushButton, "btn_toggle_hotkey")

        # Styles
        self.active_style = "background-color: #d9534f; color: white;"
        self.inactive_style = "background-color: #3c3c3c; color: white;"
        self.hover_active_style = "background-color: #c9302c; color: white;"
        self.hover_inactive_style = "background-color: #4a4a4a; color: white;"

        # Signale
        if self.btn_open: self.btn_open.clicked.connect(self.open_smartdesk)
        if self.btn_create: self.btn_create.clicked.connect(self.transition_to_create_desktop)
        if self.btn_manage: self.btn_manage.clicked.connect(self.manage_desktops)
        if self.toggle_btn: self.toggle_btn.clicked.connect(self.toggle_smartdesk)

        self.setup_positioning()
        
        # Timer prüft regelmäßig den Status (falls Hotkey extern beendet wird)
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
        if not ui_file.open(QIODevice.ReadOnly): sys.exit(-1)
        container_widget = loader.load(ui_file)
        ui_file.close()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container_widget)
        self.setLayout(layout)

    def setup_positioning(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.adjustSize()
        self.window_width = 420
        self.window_height = 294
        self.resize(self.window_width, self.window_height)
        padding_x = 20
        padding_y = 20
        self.target_x = screen_geometry.width() - self.window_width - padding_x
        self.target_y = screen_geometry.height() - self.window_height - padding_y
        self.start_x = screen_geometry.width()
        self.setGeometry(self.start_x, self.target_y, self.window_width, self.window_height)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.update_button_styles_on_hover(True)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.update_button_styles_on_hover(False)

    def update_button_styles_on_hover(self, is_hovering):
        if not self.toggle_btn: return
        style = (self.hover_active_style if is_hovering else self.active_style) if self.is_active else (self.hover_inactive_style if is_hovering else self.inactive_style)
        self.toggle_btn.setStyleSheet(style)

    def show_animated(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        self.is_closing = False
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(self.start_x, self.target_y, self.width(), self.height()))
        self.animation.setEndValue(QRect(self.target_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def close_panel(self):
        if self.is_closing: return
        if self.create_window and self.create_window.isVisible(): return
        self.animate_out(callback=self.close)

    def animate_out(self, callback=None):
        self.is_closing = True
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(self.start_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        if callback:
            self.animation.finished.connect(callback)
        self.animation.start()

    def event(self, event):
        if event.type() == event.Type.WindowDeactivate and not self.is_closing:
             if self.create_window and self.create_window.isVisible(): pass 
             else: self.close_panel()
        return super().event(event)
    
    def closeEvent(self, event):
        self.status_timer.stop()
        cleanup_control_panel_pid()
        super().closeEvent(event)

    # --- WIEDERHERGESTELLTE LOGIK ---

    def update_status(self):
        """Prüft PID Datei und aktualisiert Button."""
        if not self.toggle_btn: return

        # Prüfen ob listener.pid existiert
        if PID_FILE_PATH and os.path.exists(PID_FILE_PATH):
            # Läuft (Aktiv)
            if not self.is_active:
                self.is_active = True
                self.toggle_btn.setText("Hotkey Deaktivieren") 
                self.toggle_btn.setStyleSheet(self.active_style)
        else:
            # Läuft nicht (Inaktiv)
            if self.is_active:
                self.is_active = False
                self.toggle_btn.setText("Hotkey Aktivieren")
                self.toggle_btn.setStyleSheet(self.inactive_style)
                
        # Fallback für Initialzustand
        if self.toggle_btn.text() == "Hotkey Aktivieren" and self.is_active:
             self.toggle_btn.setText("Hotkey Deaktivieren")
             self.toggle_btn.setStyleSheet(self.active_style)

    def toggle_smartdesk(self):
        """Schaltet den Listener an oder aus."""
        if self.is_active:
            self.deactivate_smartdesk()
        else:
            self.activate_smartdesk()

    def activate_smartdesk(self):
        logger.info("Aktiviere SmartDesk...")
        hotkey_manager.start_listener()
        # Timer updated UI, aber wir erzwingen ein kurzes Update für Responsivität
        QTimer.singleShot(100, self.update_status)

    def deactivate_smartdesk(self):
        logger.info("Deaktiviere SmartDesk...")
        hotkey_manager.stop_listener()
        QTimer.singleShot(100, self.update_status)

    def update_active_desktop_label(self):
        if not self.desktop_name_label: return
        try:
            desktops = desktop_service.get_all_desktops()
            active_desktop = next((d for d in desktops if d.is_active), None)
            if active_desktop:
                self.desktop_name_label.setText(f"Desktop: {active_desktop.name}")
            else:
                self.desktop_name_label.setText("Desktop: -")
        except Exception:
            self.desktop_name_label.setText("Desktop: Fehler")

    def open_smartdesk(self):
        self._run_gui_script('gui_main.py')

    def manage_desktops(self):
        self._run_gui_script('gui_manage.py')

    def _run_gui_script(self, script_name):
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        script = os.path.join(os.path.dirname(__file__), script_name)
        subprocess.Popen([pythonw, script], creationflags=subprocess.CREATE_NO_WINDOW)
        self.close_panel()

    # --- Transition Logic ---
    def transition_to_create_desktop(self):
        if self.create_window is None:
            self.create_window = CreateDesktopWindow()
            self.create_window.closed.connect(self.on_create_window_closed)
            self.create_window.go_back.connect(self.on_create_window_back)
        self.animate_out(callback=self.finish_transition_to_create)

    def finish_transition_to_create(self):
        self.hide()
        if self.create_window:
            self.create_window.show_animated()

    def on_create_window_back(self):
        self.show_animated()

    def on_create_window_closed(self):
        self.create_window = None
        if self.isHidden():
            self.close()

def show_control_panel():
    app = QApplication.instance() or QApplication(sys.argv)
    panel = SmartDeskControlPanel()
    panel.show_animated()
    app.exec()

if __name__ == "__main__":
    show_control_panel()