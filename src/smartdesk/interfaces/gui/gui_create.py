import os
import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QWidget, QFileDialog, QMessageBox,
    QLineEdit, QPushButton, QRadioButton
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt

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
except ImportError as e:
    logger.error(f"FATALER FEHLER: {e}")
    def get_text(key, **kwargs): return key.split('.')[-1]
    class FakeDesktopService:
        def create_desktop(self, *args, **kwargs): return False
    desktop_service = FakeDesktopService()


class CreateDesktopWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.load_ui()

        # Fensterkonfiguration
        self.setWindowTitle(get_text("gui.create_dialog.title"))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # UI-Elemente finden
        self.name_entry = self.findChild(QLineEdit, "lineEdit_name")
        self.path_entry = self.findChild(QLineEdit, "lineEdit_path")
        self.btn_browse = self.findChild(QPushButton, "btn_browse")
        self.btn_create = self.findChild(QPushButton, "btn_create")
        self.btn_cancel = self.findChild(QPushButton, "btn_cancel")
        self.radio_existing = self.findChild(QRadioButton, "radioButton_existing")
        self.radio_new = self.findChild(QRadioButton, "radioButton_new")
        self.label_path = self.findChild(QLabel, "label_path")

        # Signale verbinden
        self.btn_browse.clicked.connect(self.browse_folder)
        self.btn_create.clicked.connect(self.create_desktop)
        self.btn_cancel.clicked.connect(self.close)
        self.radio_existing.toggled.connect(self.on_mode_change)
        self.radio_new.toggled.connect(self.on_mode_change)

        # Initialen Status setzen
        self.on_mode_change()
        self.name_entry.setFocus()


    def load_ui(self):
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file_path = os.path.join(current_dir, "smartdesk_create.ui")
        ui_file = QFile(ui_file_path)

        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(f"Cannot open UI file: {ui_file.errorString()}")
            sys.exit(-1)
        
        # Widget aus UI-Datei laden und dem aktuellen Widget hinzufügen
        container_widget = loader.load(ui_file, self)
        ui_file.close()

    def on_mode_change(self):
        if self.radio_existing.isChecked():
            self.label_path.setText(get_text("gui.create_dialog.label_path_existing"))
            self.path_entry.setEnabled(True)
            self.btn_browse.setEnabled(True)
        else:
            self.label_path.setText(get_text("gui.create_dialog.label_path_new"))
            self.path_entry.setEnabled(True)
            self.btn_browse.setEnabled(True)
    
    def browse_folder(self):
        title = (
            get_text("gui.create_dialog.browse_title_parent") 
            if self.radio_new.isChecked() 
            else get_text("gui.create_dialog.browse_title_existing")
        )
        folder = QFileDialog.getExistingDirectory(self, title)
        if folder:
            self.path_entry.setText(folder)

    def create_desktop(self):
        name = self.name_entry.text().strip()
        path = self.path_entry.text().strip().strip('"')

        if not name:
            QMessageBox.critical(self, get_text("gui.common.error_title"), get_text("gui.create_dialog.error_no_name"))
            return
        if not path:
            QMessageBox.critical(self, get_text("gui.common.error_title"), get_text("gui.create_dialog.error_no_path"))
            return

        path = os.path.normpath(path)
        if not os.path.isabs(path):
            QMessageBox.critical(self, get_text("gui.common.error_title"), get_text("gui.create_dialog.error_path_not_absolute", path=path))
            return

        create_if_missing = self.radio_new.isChecked()
        final_path = os.path.join(path, name) if create_if_missing else path

        success = desktop_service.create_desktop(
            name,
            final_path,
            create_if_missing=create_if_missing,
        )

        if success:
            QMessageBox.information(self, get_text("gui.create_dialog.success_creation", name=name),
                                    get_text('gui.create_dialog.new_path_location', path=final_path))
            self.close()
        else:
            QMessageBox.critical(self, get_text("gui.common.error_title"), get_text("gui.create_dialog.error_creation_failed"))


def show_create_desktop_window():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = CreateDesktopWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    logger.info("Starte Create Desktop GUI im Testmodus...")
    show_create_desktop_window()