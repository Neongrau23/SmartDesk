import os
import sys
import logging
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QLineEdit, QPushButton, QRadioButton, QLabel, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt, Signal, QPropertyAnimation, QEasingCurve, QRect, QTimer, QEvent

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
    from smartdesk.shared.localization import get_text
    from smartdesk.shared.config import get_resource_path
except ImportError:

    def get_text(key, **kwargs):
        return key.split(".")[-1]

    class FakeDesktopService:
        def create_desktop(self, *args, **kwargs):
            return False

    desktop_service = FakeDesktopService()


class CreateDesktopWindow(QWidget):
    closed = Signal()
    go_back = Signal()

    def __init__(self):
        super().__init__()

        # Initialisiere Variablen BEVOR UI geladen wird
        self.wants_to_go_back = False
        self.is_browsing = False
        self.ignore_focus_loss = True  # Startet mit Schutz
        self.is_closing = False

        self.load_ui()

        # Konfiguration
        self.setWindowTitle(get_text("gui.create_dialog.title"))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # UI Elemente finden
        self.name_entry = self.findChild(QLineEdit, "lineEdit_name")
        self.path_entry = self.findChild(QLineEdit, "lineEdit_path")
        self.btn_browse = self.findChild(QPushButton, "btn_browse")
        self.btn_create = self.findChild(QPushButton, "btn_create")
        self.btn_cancel = self.findChild(QPushButton, "btn_cancel")
        self.radio_existing = self.findChild(QRadioButton, "radioButton_existing")
        self.radio_new = self.findChild(QRadioButton, "radioButton_new")
        self.label_path = self.findChild(QLabel, "label_path")

        # Signale verbinden
        if self.btn_browse:
            self.btn_browse.clicked.connect(self.browse_folder)
        if self.btn_create:
            self.btn_create.clicked.connect(self.create_desktop)
        if self.btn_cancel:
            self.btn_cancel.clicked.connect(self.handle_cancel)
        if self.radio_existing:
            self.radio_existing.toggled.connect(self.on_mode_change)
        if self.radio_new:
            self.radio_new.toggled.connect(self.on_mode_change)

        if self.radio_existing:
            self.on_mode_change()
        if self.name_entry:
            self.name_entry.setFocus()

        self.setup_positioning()

    def load_ui(self):
        loader = QUiLoader()
        ui_file_path = get_resource_path("smartdesk/ui/gui/designer/create.ui")
        ui_file = QFile(ui_file_path)

        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(get_text("gui.create_dialog.error_ui_file", error=ui_file.errorString()))
            sys.exit(-1)

        container_widget = loader.load(ui_file)
        ui_file.close()
        
        # Load Stylesheet
        try:
            style_path = get_resource_path("smartdesk/ui/gui/style.qss")
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            logger.warning(get_text("gui.create_dialog.warn_style", e=e))

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

    def show_animated(self):
        # 1. Schutz aktivieren: Fokusverlust für 500ms ignorieren
        self.ignore_focus_loss = True

        # 2. Fenster anzeigen und fokussieren
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

        # 3. Timer starten, um Schutz nach 500ms aufzuheben
        QTimer.singleShot(500, self.enable_auto_close)

        self.is_closing = False
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(self.start_x, self.target_y, self.width(), self.height()))
        self.animation.setEndValue(QRect(self.target_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def enable_auto_close(self):
        """Aktiviert das automatische Schließen bei Fokusverlust wieder."""
        self.ignore_focus_loss = False

    def close_panel_animated(self):
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

    def handle_cancel(self):
        self.wants_to_go_back = True
        self.close_panel_animated()

    def event(self, event):
        try:
            # 1. Schutzmechanismus: Ignorieren beim Browsen oder Starten (Grace Period)
            if self.is_browsing or self.ignore_focus_loss:
                return super().event(event)

            # 2. Prüfen auf Deaktivierung (Fokusverlust)
            # Verwende QEvent.Type.WindowDeactivate für PySide6 Kompatibilität
            if event.type() == QEvent.Type.WindowDeactivate:
                if not self.is_closing and not self.isActiveWindow():
                    self.close_panel_animated()

        except Exception as e:
            # Sicherheitsnetz: Fehler loggen, aber nicht abstürzen
            logger.error(f"Fehler im Event-Handler: {e}")

        return super().event(event)

    def closeEvent(self, event):
        if self.wants_to_go_back:
            self.go_back.emit()
        self.closed.emit()
        super().closeEvent(event)

    def on_mode_change(self):
        if self.radio_existing.isChecked():
            self.label_path.setText(get_text("gui.create_dialog.label_path_existing"))
        else:
            self.label_path.setText(get_text("gui.create_dialog.label_path_new"))

    def browse_folder(self):
        # Schutz AN
        self.is_browsing = True

        title = get_text("gui.create_dialog.browse_folder_title")
        folder = QFileDialog.getExistingDirectory(self, title)

        # Schutz AUS
        self.is_browsing = False

        # Fokus explizit zurückholen
        self.activateWindow()
        self.raise_()
        self.setFocus()

        if folder:
            self.path_entry.setText(folder)

    def create_desktop(self):
        name = self.name_entry.text().strip()
        path = self.path_entry.text().strip().strip('"')

        if not name or not path:
            return

        create_if_missing = self.radio_new.isChecked()
        final_path = os.path.join(path, name) if create_if_missing else path
        path = os.path.normpath(path)

        success = desktop_service.create_desktop(name, final_path, create_if_missing=create_if_missing)

        if success:
            self.close_panel_animated()
        else:
            QMessageBox.critical(self, get_text("gui.common.error_title"), get_text("gui.create_dialog.msg_error_create"))


def show_create_desktop_window():
    app = QApplication.instance() or QApplication(sys.argv)
    window = CreateDesktopWindow()
    window.show_animated()
    app.exec()


if __name__ == "__main__":
    logger.info(get_text("gui.create_dialog.log_test_mode"))
    show_create_desktop_window()
