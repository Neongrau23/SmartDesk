import os
import logging
from PySide6.QtWidgets import QWidget, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton, QComboBox, QDoubleSpinBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt, QTimer

from smartdesk.hotkeys import hotkey_manager
from smartdesk.core.services.settings_service import get_setting, set_setting

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
        self.load_config_to_ui()
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

        # Config Elemente
        self.combo_activation = self.ui.findChild(QComboBox, "combo_activation")
        self.combo_action = self.ui.findChild(QComboBox, "combo_action")
        self.spin_hold_duration = self.ui.findChild(QDoubleSpinBox, "spin_hold_duration")
        self.btn_save_config = self.ui.findChild(QPushButton, "btn_save_config")

    def setup_connections(self):
        if self.btn_start:
            self.btn_start.clicked.connect(self.action_start)
        if self.btn_stop:
            self.btn_stop.clicked.connect(self.action_stop)
        if self.btn_restart:
            self.btn_restart.clicked.connect(self.action_restart)
        if self.btn_save_config:
            self.btn_save_config.clicked.connect(self.save_config)

    def setup_table(self):
        if not self.table:
            return
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

    def load_config_to_ui(self):
        """Lädt die aktuellen Settings in die ComboBoxen."""
        act_key = get_setting("activation_keys", "Ctrl+Shift")
        act_mod = get_setting("action_modifier", "Alt")
        duration = get_setting("hold_duration", 0.5)

        if self.combo_activation:
            self.combo_activation.setCurrentText(act_key)
        if self.combo_action:
            self.combo_action.setCurrentText(act_mod)
        if self.spin_hold_duration:
            self.spin_hold_duration.setValue(float(duration))

    def save_config(self):
        """Speichert die Settings und startet den Listener neu."""
        if not self.combo_activation or not self.combo_action:
            return

        new_act = self.combo_activation.currentText()
        new_mod = self.combo_action.currentText()
        new_duration = 0.5
        if self.spin_hold_duration:
            new_duration = self.spin_hold_duration.value()

        set_setting("activation_keys", new_act)
        set_setting("action_modifier", new_mod)
        set_setting("hold_duration", new_duration)

        self.show_message("Konfiguration gespeichert. Starte Listener neu...", success=True)

        # UI Update (Tabelle)
        self.load_hotkeys()

        # Neustart erzwingen
        hotkey_manager.restart_listener()
        self.refresh_status()

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
        if not self.table:
            return
        self.table.setRowCount(0)

        # Aktions-Key aus Settings laden für die Anzeige
        mod = get_setting("action_modifier", "Alt")

        hotkeys = [
            (f"{mod} + 1", "Wechsel zu Desktop 1"),
            (f"{mod} + 2", "Wechsel zu Desktop 2"),
            (f"{mod} + 3", "Wechsel zu Desktop 3"),
            (f"{mod} + 4", "Wechsel zu Desktop 4"),
            (f"{mod} + 5", "Wechsel zu Desktop 5"),
            (f"{mod} + 6", "Wechsel zu Desktop 6"),
            (f"{mod} + 7", "Wechsel zu Desktop 7"),
            (f"{mod} + 8", "Wechsel zu Desktop 8"),
            (f"{mod} + 9", "Speichere aktuelle Icon-Positionen"),
        ]

        self.table.setRowCount(len(hotkeys))
        for row, (keys, action) in enumerate(hotkeys):
            self.table.setItem(row, 0, QTableWidgetItem(keys))
            self.table.setItem(row, 1, QTableWidgetItem(action))

    def show_message(self, text, success=True):
        if not self.lbl_message:
            return

        status = "success" if success else "error"
        self.lbl_message.setText(text)
        self.lbl_message.setProperty("status", status)
        
        # Force style refresh
        self.lbl_message.style().unpolish(self.lbl_message)
        self.lbl_message.style().polish(self.lbl_message)

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
