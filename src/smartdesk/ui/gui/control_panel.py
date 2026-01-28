import logging
import os
import subprocess
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QTimer, QPropertyAnimation, QEasingCurve, QRect, Qt

# --- Imports & Mocking (wie im Original) ---
try:
    from .gui_create import CreateDesktopWindow
except ImportError:
    # Dummy-Klasse, falls Datei fehlt
    class CreateDesktopWindow(QWidget):
        from PySide6.QtCore import Signal

        closed = Signal()
        go_back = Signal()

        def show_animated(self):
            self.show()


try:
    from smartdesk.shared.logging_config import get_logger
    from smartdesk.shared.localization import get_text

    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    def get_text(key, **kwargs):
        return key

try:
    from smartdesk.core.services import desktop_service
    from smartdesk.hotkeys import hotkey_manager
    from smartdesk.shared.config import get_resource_path
except ImportError:
    # Mocking für Tests ohne Backend
    class FakeHotkeys:
        def start_listener(self):
            pid_path = os.path.join(os.environ.get("APPDATA", "."), "SmartDesk", "listener.pid")
            os.makedirs(os.path.dirname(pid_path), exist_ok=True)
            with open(pid_path, "w") as f:
                f.write("1234")
            logger.info("Mock: Listener gestartet")

        def stop_listener(self):
            pid_path = os.path.join(os.environ.get("APPDATA", "."), "SmartDesk", "listener.pid")
            if os.path.exists(pid_path):
                os.remove(pid_path)
            logger.info("Mock: Listener gestoppt")

    hotkey_manager = FakeHotkeys()

    class FakeDesktopService:
        def get_all_desktops(self):
            return []

    desktop_service = FakeDesktopService()

# --- PID Paths ---
PID_FILE_DIR = os.path.join(os.environ.get("APPDATA", "."), "SmartDesk")
CONTROL_PANEL_PID_PATH = os.path.join(PID_FILE_DIR, "control_panel.pid")
PID_FILE_PATH = os.path.join(PID_FILE_DIR, "listener.pid")


def cleanup_control_panel_pid():
    try:
        if CONTROL_PANEL_PID_PATH and os.path.exists(CONTROL_PANEL_PID_PATH):
            os.remove(CONTROL_PANEL_PID_PATH)
    except:
        pass


class SmartDeskControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.is_active = False
        self.is_closing = False
        self.animation = None
        self.create_window = None

        self.load_ui()
        self.load_stylesheet()  # NEU: Lädt das CSS

        self.setWindowTitle(get_text("gui.control_panel.title"))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # UI Elemente finden
        self.desktop_name_label = self.findChild(QLabel, "label_desktop_name")
        self.btn_open = self.findChild(QPushButton, "btn_gui_main")
        self.btn_create = self.findChild(QPushButton, "btn_gui_create")
        self.btn_manage = self.findChild(QPushButton, "btn_gui_manage")
        self.toggle_btn = self.findChild(QPushButton, "btn_toggle_hotkey")

        # Signale verbinden
        if self.btn_open:
            self.btn_open.clicked.connect(self.open_smartdesk)
        if self.btn_create:
            self.btn_create.clicked.connect(self.transition_to_create_desktop)
        if self.btn_manage:
            self.btn_manage.clicked.connect(self.manage_desktops)
        if self.toggle_btn:
            self.toggle_btn.clicked.connect(self.toggle_smartdesk)

        self.setup_positioning()

        # Timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.timeout.connect(self.update_active_desktop_label)
        self.status_timer.start(500)

        # Initialer Check
        self.update_status()
        self.update_active_desktop_label()

    def load_ui(self):
        loader = QUiLoader()
        # Use get_resource_path
        ui_file_path = get_resource_path("smartdesk/ui/gui/designer/control_panel.ui")

        ui_file = QFile(ui_file_path)
        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(get_text("gui.control_panel.error_ui_file", path=ui_file_path))
            sys.exit(-1)

        container_widget = loader.load(ui_file)
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container_widget)
        self.setLayout(layout)

    def load_stylesheet(self):
        """Lädt die externe QSS Datei für saubere Trennung."""
        try:
            style_path = get_resource_path("smartdesk/ui/gui/style.qss")
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            logger.warning(get_text("gui.control_panel.warn_style", e=e))

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

    # --- Fenster Animationen (unverändert) ---
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
        if self.is_closing:
            return
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
            if self.create_window and self.create_window.isVisible():
                pass
            else:
                self.close_panel()
        return super().event(event)

    def closeEvent(self, event):
        self.status_timer.stop()
        cleanup_control_panel_pid()
        super().closeEvent(event)

    # --- Logik ---

    def update_status(self):
        """Prüft Status und setzt Styles via Property."""
        if not self.toggle_btn:
            return

        is_running = PID_FILE_PATH and os.path.exists(PID_FILE_PATH)
        self.is_active = is_running

        # Text Logik
        new_text = get_text("gui.control_panel.button_hotkey_deactivate") if is_running else get_text("gui.control_panel.button_hotkey_activate")
        if self.toggle_btn.text() != new_text:
            self.toggle_btn.setText(new_text)

        # Style Logik (Dynamic Property)
        if self.toggle_btn.property("active") != is_running:
            self.toggle_btn.setProperty("active", is_running)
            # Style neu berechnen erzwingen (unpolish -> polish)
            self.toggle_btn.style().unpolish(self.toggle_btn)
            self.toggle_btn.style().polish(self.toggle_btn)

    def toggle_smartdesk(self):
        if self.is_active:
            logger.info(get_text("gui.control_panel.log_deactivate"))
            hotkey_manager.stop_listener()
        else:
            logger.info(get_text("gui.control_panel.log_activate"))
            hotkey_manager.start_listener()

        # UI sofort aktualisieren
        QTimer.singleShot(50, self.update_status)

    def update_active_desktop_label(self):
        if not self.desktop_name_label:
            return
        try:
            desktops = desktop_service.get_all_desktops()
            active_desktop = next((d for d in desktops if d.is_active), None)
            text = get_text("gui.control_panel.desktop_label_template", name=active_desktop.name) if active_desktop else get_text("gui.control_panel.desktop_label_none")
            self.desktop_name_label.setText(text)
        except Exception:
            self.desktop_name_label.setText(get_text("gui.control_panel.desktop_label_none"))

    def open_smartdesk(self):
        self._run_gui_script("gui_main.py")

    def manage_desktops(self):
        self._run_gui_script("gui_manage.py")

    def _run_gui_script(self, script_name):
        # Use sys.executable for compatibility with frozen app
        python_exe = sys.executable

        # Calculate src directory (3 levels up from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

        # Setup environment with PYTHONPATH
        env = os.environ.copy()
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = src_dir + os.pathsep + env["PYTHONPATH"]
        else:
            env["PYTHONPATH"] = src_dir

        # Construct module name: "gui_main.py" -> "smartdesk.ui.gui.gui_main"
        module_name = f"smartdesk.ui.gui.{script_name.replace('.py', '')}"

        flags = 0
        if sys.platform == "win32":
            flags = subprocess.CREATE_NO_WINDOW

        subprocess.Popen([python_exe, "-m", module_name], creationflags=flags, env=env)
        self.close_panel()

    # --- Transition Logic ---
    def transition_to_create_desktop(self):
        if self.create_window is None:
            self.create_window = CreateDesktopWindow()
            # Falls Dummy-Klasse verwendet wird, haben diese Signale keinen Effekt, crashen aber auch nicht
            try:
                self.create_window.closed.connect(self.on_create_window_closed)
                self.create_window.go_back.connect(self.on_create_window_back)
            except AttributeError:
                pass

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
