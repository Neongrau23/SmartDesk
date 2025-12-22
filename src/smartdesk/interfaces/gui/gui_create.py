import os
import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QWidget, QFileDialog, QMessageBox,
    QLineEdit, QPushButton, QRadioButton, QLabel, QVBoxLayout
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt, Signal, QPropertyAnimation, QEasingCurve, QRect

# --- Pfad-Hack für direkten Aufruf ---
if __name__ == "__main__" or __package__ is None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    interfaces_dir = os.path.dirname(current_dir)
    smartdesk_dir = os.path.dirname(interfaces_dir)
    src_dir = os.path.dirname(smartdesk_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

try:
    from smartdesk.core.services import desktop_service
    from smartdesk.shared.localization import get_text
except ImportError:
    def get_text(key, **kwargs): return key.split('.')[-1]
    class FakeDesktopService:
        def create_desktop(self, *args, **kwargs): return False
    desktop_service = FakeDesktopService()


class CreateDesktopWindow(QWidget):
    closed = Signal()

    def __init__(self):
        super().__init__()
        self.load_ui()

        # Konfiguration
        self.setWindowTitle("Desktop erstellen")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # UI Elemente
        self.name_entry = self.findChild(QLineEdit, "lineEdit_name")
        self.path_entry = self.findChild(QLineEdit, "lineEdit_path")
        self.btn_browse = self.findChild(QPushButton, "btn_browse")
        self.btn_create = self.findChild(QPushButton, "btn_create")
        self.btn_cancel = self.findChild(QPushButton, "btn_cancel")
        self.radio_existing = self.findChild(QRadioButton, "radioButton_existing")
        self.radio_new = self.findChild(QRadioButton, "radioButton_new")
        self.label_path = self.findChild(QLabel, "label_path")

        # Signale
        if self.btn_browse: self.btn_browse.clicked.connect(self.browse_folder)
        if self.btn_create: self.btn_create.clicked.connect(self.create_desktop)
        # Cancel animiert raus
        if self.btn_cancel: self.btn_cancel.clicked.connect(self.close_panel_animated)
        
        if self.radio_existing: self.radio_existing.toggled.connect(self.on_mode_change)
        if self.radio_new: self.radio_new.toggled.connect(self.on_mode_change)

        if self.radio_existing: self.on_mode_change()
        if self.name_entry: self.name_entry.setFocus()
        
        self.is_closing = False
        self.setup_positioning()

    def load_ui(self):
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file_path = os.path.join(current_dir, "smartdesk_create.ui")
        ui_file = QFile(ui_file_path)

        if not ui_file.open(QIODevice.ReadOnly):
            sys.exit(-1)
        
        # WICHTIG: load(ui_file) OHNE parent, dann manuell ins Layout
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
        padding_y = 60
        
        self.target_x = screen_geometry.width() - self.window_width - padding_x
        self.target_y = screen_geometry.height() - self.window_height - padding_y
        self.start_x = screen_geometry.width()

        # Startet draußen
        self.setGeometry(self.start_x, self.target_y, self.window_width, self.window_height)

    def show_animated(self):
        self.show()
        self.is_closing = False
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(self.start_x, self.target_y, self.width(), self.height()))
        self.animation.setEndValue(QRect(self.target_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def close_panel_animated(self):
        if self.is_closing: return
        self.is_closing = True
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(self.start_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        self.animation.finished.connect(self.close)
        self.animation.start()

    def event(self, event):
        # Optional: Auto-Close bei Fokusverlust
        if event.type() == event.Type.WindowDeactivate and not self.is_closing:
             # Um sicherzugehen, dass wir keine Dialoge (File Picker) killen:
             if not self.isActiveWindow(): 
                self.close_panel_animated()
        return super().event(event)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    # --- Logik ---
    def on_mode_change(self):
        if self.radio_existing.isChecked():
            self.label_path.setText(get_text("gui.create_dialog.label_path_existing"))
        else:
            self.label_path.setText(get_text("gui.create_dialog.label_path_new"))
    
    def browse_folder(self):
        title = "Ordner wählen"
        folder = QFileDialog.getExistingDirectory(self, title)
        if folder:
            self.path_entry.setText(folder)

    def create_desktop(self):
        name = self.name_entry.text().strip()
        path = self.path_entry.text().strip().strip('"')

        if not name or not path: return

        create_if_missing = self.radio_new.isChecked()
        final_path = os.path.join(path, name) if create_if_missing else path
        path = os.path.normpath(path)

        success = desktop_service.create_desktop(name, final_path, create_if_missing=create_if_missing)

        if success:
            self.close_panel_animated()
        else:
            QMessageBox.critical(self, "Fehler", "Konnte Desktop nicht erstellen.")

def show_create_desktop_window():
    app = QApplication.instance() or QApplication(sys.argv)
    window = CreateDesktopWindow()
    window.show_animated()
    app.exec()

if __name__ == "__main__":
    show_create_desktop_window()