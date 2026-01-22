# Dateipfad: src/smartdesk/ui/gui/gui_overview.py
import logging
import os
import sys
import threading
import json
from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QPropertyAnimation, QEasingCurve, QRect, Qt, QTimer, Signal, QObject, Slot
from PySide6.QtGui import QScreen, QFont

# --- Optional Imports ---
try:
    from smartdesk.core.utils.win_utils import release_taskbar_from_top, ensure_taskbar_on_top
except ImportError:

    def release_taskbar_from_top():
        pass

    def ensure_taskbar_on_top():
        pass


# --- Logger Setup ---
try:
    from smartdesk.shared.logging_config import get_logger
    from smartdesk.shared.localization import get_text

    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    def get_text(key, **kwargs):
        return key


class CommandWatcher(QObject):
    """Liest Befehle von stdin (SHOW, HIDE, QUIT)."""

    command_received = Signal(str)

    def __init__(self):
        super().__init__()
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._watch_stdin, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _watch_stdin(self):
        try:
            while not self._stop.is_set():
                # Blockierendes Lesen einer Zeile
                line = sys.stdin.readline()
                if not line:  # EOF
                    self.command_received.emit("QUIT")
                    break

                cmd = line.strip().upper()
                if cmd:
                    logger.debug(get_text("gui.overview.command_received", cmd=cmd))
                    self.command_received.emit(cmd)
        except Exception as e:
            logger.error(get_text("gui.overview.watcher_error", e=e))
            self.command_received.emit("QUIT")


class OverviewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.is_animating = False
        self.is_visible = False
        self.animation = None
        self.desktops_data: List[Dict] = []
        self.desktop_labels: List[QLabel] = []
        self._last_mtime = 0

        # Hauptcontainer aus UI laden
        self.load_ui()

        self.setWindowTitle(get_text("gui.overview.title"))

        # STIL: Rahmenlos, immer oben, kein Taskleisten-Icon
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Desktop-Liste laden und anzeigen
        self.load_desktops()
        self.populate_desktop_list()

        # Initial verstecken (wird via SHOW angezeigt)
        self.setup_positioning()

        # Command Watcher
        self.watcher = CommandWatcher()
        self.watcher.command_received.connect(self.handle_command)
        self.watcher.start()

        logger.info(get_text("gui.overview.ready"))

    @Slot(str)
    def handle_command(self, cmd):
        if cmd == "SHOW":
            # Liste neu laden vor dem Anzeigen, falls sich was geändert hat
            self.refresh_desktop_list()
            self.show_animated()
        elif cmd == "HIDE":
            self.animate_out()
        elif cmd == "QUIT":
            self.close()
            QApplication.quit()

    def get_desktops_file_path(self) -> Path:
        appdata = os.getenv("APPDATA")
        if not appdata:
            return Path()
        return Path(appdata) / "SmartDesk" / "desktops.json"

    def load_desktops(self) -> bool:
        json_path = self.get_desktops_file_path()
        try:
            if not json_path.exists():
                self.desktops_data = []
                self._last_mtime = 0
                return False

            # Check modification time
            current_mtime = json_path.stat().st_mtime
            if current_mtime == self._last_mtime:
                return False

            with open(json_path, "r", encoding="utf-8") as f:
                self.desktops_data = json.load(f)

            self._last_mtime = current_mtime
            return True
        except Exception as e:
            logger.error(get_text("gui.overview.load_error", e=e))
            self.desktops_data = []
            self._last_mtime = 0
            return False

    def populate_desktop_list(self):
        try:
            container = self.findChild(QWidget, "desktops_container")
            if not container:
                return

            if container.layout():
                while container.layout().count():
                    item = container.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            else:
                layout = QHBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(12)

            self.desktop_labels.clear()

            if not self.desktops_data:
                label = self._create_desktop_label(get_text("gui.overview.no_desktops"), is_active=False, is_placeholder=True)
                container.layout().addWidget(label)
                return

            for desktop in self.desktops_data:
                desktop_name = desktop.get("name", get_text("gui.overview.unnamed"))
                is_active = desktop.get("is_active", False)
                label = self._create_desktop_label(desktop_name, is_active)
                self.desktop_labels.append(label)
                container.layout().addWidget(label)

            container.layout().addStretch()
        except Exception as e:
            logger.error(get_text("gui.overview.label_error", e=e))

    def _create_desktop_label(self, text: str, is_active: bool = False, is_placeholder: bool = False) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        font = QFont("Segoe UI", 10)
        if is_active:
            font.setWeight(QFont.DemiBold)
        label.setFont(font)

        if is_placeholder:
            label.setProperty("overview_type", "placeholder")
        elif is_active:
            label.setProperty("overview_type", "active")
        else:
            label.setProperty("overview_type", "normal")
        
        # Style Update erzwingen
        label.style().unpolish(label)
        label.style().polish(label)
        
        return label

    def refresh_desktop_list(self):
        if self.load_desktops():
            self.populate_desktop_list()

    def load_ui(self):
        main_widget = QWidget()
        main_widget.setObjectName("Form")
        main_widget.setProperty("window_type", "overview") # Für CSS Selektor
        
        # Lade Style.qss
        try:
            from smartdesk.shared.config import get_resource_path
            style_path = get_resource_path("smartdesk/ui/gui/style.qss")
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            logger.warning(get_text("gui.overview.style_warn", e=e))

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)

        desktops_container = QWidget()
        desktops_container.setObjectName("desktops_container")
        main_layout.addWidget(desktops_container)

        window_layout = QHBoxLayout(self)
        window_layout.setContentsMargins(10, 0, 0, 0)
        window_layout.addWidget(main_widget)

        self.setMinimumSize(300, 70)
        self.setMaximumHeight(70)

    def setup_positioning(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        full_geometry = screen.geometry()

        self.adjustSize()
        self.window_width = self.width()
        self.window_height = 80
        self.target_x = (full_geometry.width() - self.window_width) // 2
        self.target_y = screen_geometry.height() - self.window_height
        self.start_y = full_geometry.height()
        self.setGeometry(self.target_x, self.start_y, self.window_width, self.window_height)

    def show_animated(self):
        if self.is_visible:
            return  # Schon sichtbar

        self.is_visible = True
        self.show()
        self.raise_()
        ensure_taskbar_on_top()

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(450)
        self.animation.setStartValue(QRect(self.target_x, self.start_y, self.width(), self.height()))
        self.animation.setEndValue(QRect(self.target_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.finished.connect(self._on_shown)
        self.animation.start()

    def _on_shown(self):
        release_taskbar_from_top()
        self.activateWindow()
        self.setFocus()

    def animate_out(self):
        if not self.is_visible:
            return

        self.is_visible = False
        ensure_taskbar_on_top()

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(450)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(self.target_x, self.start_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        self.animation.finished.connect(self.hide)  # Nur verstecken, nicht schließen
        self.animation.start()

    def event(self, event):
        # Optional: Deaktivierung schließt Fenster?
        # Hier besser: HIDE senden, wenn Fokus verloren geht?
        # Vorerst lassen wir das, da Controller "HIDE" sendet wenn Taste losgelassen wird.
        return super().event(event)


def start_gui():
    app = QApplication.instance() or QApplication(sys.argv)
    window = OverviewWindow()
    # window wird durch CommandWatcher gesteuert
    sys.exit(app.exec())


if __name__ == "__main__":
    start_gui()
