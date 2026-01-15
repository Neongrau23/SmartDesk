import os
import logging
from PySide6.QtWidgets import (
    QWidget, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt, QTimer

from smartdesk.hotkeys import hotkey_manager

# Logger Setup
try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

class HotkeyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_connections()
        self.setup_table()
        
        # Initialer Status
        self.refresh_status()
        self.load_hotkeys()
        
        # Timer für Status-Updates (alle 2 Sekunden)
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.refresh_status)
        self.status_timer.start(2000)
        
        # Timer für Nachrichten (Einmalig)
        self.msg_timer = QTimer(self)
        self.msg_timer.setSingleShot(True)
        self.msg_timer.timeout.connect(self.clear_message)

    def load_ui(self):
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "ui", "hotkey_page.ui")
        
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(f"UI file not found: {ui_path}")
            return
            
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        layout = self.layout()
        if not layout:
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self)
            self.setLayout(layout)
            
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # UI Elemente finden
        self.lbl_status_icon = self.ui.findChild(QLabel, "lbl_status_icon")
        self.lbl_status_text = self.ui.findChild(QLabel, "lbl_status_text")
        self.lbl_message = self.ui.findChild(QLabel, "lbl_message")
        self.btn_start = self.ui.findChild(QPushButton, "btn_start")
        self.btn_stop = self.ui.findChild(QPushButton, "btn_stop")
        self.btn_restart = self.ui.findChild(QPushButton, "btn_restart")
        self.table = self.ui.findChild(QTableWidget, "table_hotkeys")

    def setup_connections(self):
        if self.btn_start: self.btn_start.clicked.connect(self.action_start)
        if self.btn_stop: self.btn_stop.clicked.connect(self.action_stop)
        if self.btn_restart: self.btn_restart.clicked.connect(self.action_restart)

    def setup_table(self):
        if not self.table: return
        # Header anpassen
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

    def refresh_status(self):
        try:
            is_running = hotkey_manager.is_listener_running()
            pid = hotkey_manager.get_listener_pid()
            
            if is_running:
                self.lbl_status_icon.setText("🟢")
                self.lbl_status_text.setText(f"Läuft (PID: {pid})")
                self.btn_start.setEnabled(False)
                self.btn_stop.setEnabled(True)
            else:
                self.lbl_status_icon.setText("🔴")
                self.lbl_status_text.setText("Gestoppt")
                self.btn_start.setEnabled(True)
                self.btn_stop.setEnabled(False)
                
        except Exception as e:
            logger.error(f"Error refreshing status: {e}")
            self.lbl_status_text.setText("Fehler bei Statusabfrage")

    def load_hotkeys(self):
        if not self.table: return
        self.table.setRowCount(0)
        
        # Aktuell hardcoded, später aus Config laden
        hotkeys = [
            ("Alt + 1", "Wechsel zu Desktop 1"),
            ("Alt + 2", "Wechsel zu Desktop 2"),
            ("Alt + 3", "Wechsel zu Desktop 3"),
            ("Alt + 4", "Wechsel zu Desktop 4"),
            ("Alt + 5", "Wechsel zu Desktop 5"),
            ("Alt + 6", "Wechsel zu Desktop 6"),
            ("Alt + 7", "Wechsel zu Desktop 7"),
            ("Alt + 8", "Wechsel zu Desktop 8"),
            ("Alt + 9", "Speichere aktuelle Icon-Positionen"),
        ]
        
        self.table.setRowCount(len(hotkeys))
        for row, (keys, action) in enumerate(hotkeys):
            self.table.setItem(row, 0, QTableWidgetItem(keys))
            self.table.setItem(row, 1, QTableWidgetItem(action))

    def show_message(self, text, success=True):
        if not self.lbl_message: return
        
        color = "#1a7a65" if success else "#cc4444" # Grün oder Rot
        self.lbl_message.setText(text)
        self.lbl_message.setStyleSheet(f"color: {color}; font-weight: bold; margin-top: 5px;")
        
        # Timer starten zum Löschen (3 Sekunden)
        self.msg_timer.start(3000)

    def clear_message(self):
        if self.lbl_message:
            self.lbl_message.clear()

    def action_start(self):
        if hotkey_manager.start_listener():
            self.refresh_status()
            self.show_message("Listener erfolgreich gestartet.", success=True)
        else:
            self.show_message("Konnte Listener nicht starten.", success=False)

    def action_stop(self):
        if hotkey_manager.stop_listener():
            self.refresh_status()
            self.show_message("Listener gestoppt.", success=True)
        else:
            self.show_message("Konnte Listener nicht stoppen.", success=False)

    def action_restart(self):
        if hotkey_manager.restart_listener():
            self.refresh_status()
            self.show_message("Listener neu gestartet.", success=True)
        else:
            self.show_message("Neustart fehlgeschlagen.", success=False)
