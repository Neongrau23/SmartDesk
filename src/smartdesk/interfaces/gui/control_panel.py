import logging
import os
import subprocess
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QTimer, QPropertyAnimation, QEasingCurve, QRect, Qt

# Versuche Import, Fallback für Standalone-Test
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

# --- Dummy Services/Imports ---
try:
    from smartdesk.core.services import desktop_service
    from smartdesk.hotkeys import hotkey_manager
    from smartdesk.shared.localization import get_text
except ImportError:
    def get_text(key, **kwargs): return key.split('.')[-1]
    class FakeHotkeys:
        def start_listener(self): pass
        def stop_listener(self): pass
    hotkey_manager = FakeHotkeys()
    class FakeDesktopService:
        def get_all_desktops(self): return []
    desktop_service = FakeDesktopService()

# --- PID Paths ---
PID_FILE_DIR = os.path.join(os.environ.get('APPDATA', '.'), 'SmartDesk')
CONTROL_PANEL_PID_PATH = os.path.join(PID_FILE_DIR, 'control_panel.pid')

def cleanup_control_panel_pid():
    try:
        if CONTROL_PANEL_PID_PATH and os.path.exists(CONTROL_PANEL_PID_PATH):
            os.remove(CONTROL_PANEL_PID_PATH)
    except: pass

class SmartDeskControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.is_active = False
        self.is_closing = False
        self.animation = None
        self.create_window = None 

        self.load_ui()

        # Fensterkonfiguration
        self.setWindowTitle("Control Panel")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # UI-Elemente
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
        
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(500)
        self.update_status()

    def load_ui(self):
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file_path = os.path.join(current_dir, "control_panel.ui")
        ui_file = QFile(ui_file_path)
        if not ui_file.open(QIODevice.ReadOnly): sys.exit(-1)
        
        # WICHTIG: Kein Parent (self) beim Laden übergeben, sonst doppeltes Layout
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
        
        self.window_width = 420  # Fixe Breite aus UI
        self.window_height = 294 # Fixe Höhe aus UI
        self.resize(self.window_width, self.window_height)
        
        padding_x = 20
        padding_y = 60
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
        self.is_closing = False
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(self.start_x, self.target_y, self.width(), self.height()))
        self.animation.setEndValue(QRect(self.target_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def close_panel(self):
        """Normales Schließen (z.B. Fokusverlust)"""
        if self.is_closing: return
        # Wenn Create Window offen ist, CP nicht schließen (es ist eh hidden)
        if self.create_window and self.create_window.isVisible():
            return
            
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
             # Nicht schließen, wenn wir zum Create-Fenster wechseln
             if self.create_window and self.create_window.isVisible():
                 pass 
             else:
                 self.close_panel()
        return super().event(event)
    
    def closeEvent(self, event):
        self.status_timer.stop()
        cleanup_control_panel_pid()
        super().closeEvent(event)

    # --- Actions ---
    def update_status(self):
        # Dummy Status Update
        pass 

    def toggle_smartdesk(self):
        self.is_active = not self.is_active
        self.update_status()

    def open_smartdesk(self):
        self._run_gui_script('gui_main.py')

    def manage_desktops(self):
        self._run_gui_script('gui_manage.py')

    def _run_gui_script(self, script_name):
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        script = os.path.join(os.path.dirname(__file__), script_name)
        subprocess.Popen([pythonw, script], creationflags=subprocess.CREATE_NO_WINDOW)
        self.close_panel()

    # --- TRANSITION LOGIC ---
    def transition_to_create_desktop(self):
        """Startet den Wechsel: CP raus, Create rein."""
        if self.create_window is None:
            self.create_window = CreateDesktopWindow()
            self.create_window.closed.connect(self.on_create_window_closed)

        # CP raus animieren, DANN finish_transition aufrufen
        self.animate_out(callback=self.finish_transition_to_create)

    def finish_transition_to_create(self):
        """Wird aufgerufen, wenn CP draußen ist."""
        # WICHTIG: self.hide() statt self.close()!
        # Wenn wir close() rufen, wird 'self' zerstört und damit auch 'self.create_window'.
        self.hide()
        
        # Jetzt das andere Fenster reinholen
        if self.create_window:
            self.create_window.show_animated()

    def on_create_window_closed(self):
        """Wenn das Create-Fenster geschlossen wurde."""
        self.create_window = None
        # Wenn CP versteckt ist und Create zugeht, ist die Interaktion vorbei -> App zu.
        if self.isHidden():
            self.close()

def show_control_panel():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    panel = SmartDeskControlPanel()
    panel.show_animated()
    
    app.exec()

if __name__ == "__main__":
    show_control_panel()