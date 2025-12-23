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
from PySide6.QtCore import QFile, QIODevice, QPropertyAnimation, QEasingCurve, QRect, Qt, QTimer, Signal, QObject
from PySide6.QtGui import QScreen, QFont

# --- Optional Imports ---
try:
    from smartdesk.core.utils.win_utils import release_taskbar_from_top, ensure_taskbar_on_top
except ImportError:
    def release_taskbar_from_top(): pass
    def ensure_taskbar_on_top(): pass

# --- Logger Setup ---
try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)


class StdinWatcher(QObject):
    """Signal-Emitter für stdin-Close-Events."""
    stdin_closed = Signal()
    
    def __init__(self):
        super().__init__()
        self._stop = threading.Event()
        self._thread = None
    
    def start(self):
        """Startet den Watch-Thread."""
        self._thread = threading.Thread(target=self._watch_stdin, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stoppt den Watch-Thread."""
        self._stop.set()
    
    def _watch_stdin(self):
        """Überwacht stdin auf Schließen."""
        try:
            while not self._stop.is_set():
                try:
                    data = sys.stdin.read(1)
                    if not data:
                        logger.debug("stdin EOF erkannt - emittiere Signal")
                        self.stdin_closed.emit()
                        break
                except Exception as e:
                    logger.debug(f"stdin Lesefehler: {e}")
                    self.stdin_closed.emit()
                    break
        except Exception as e:
            logger.debug(f"Watcher-Thread Fehler: {e}")


class OverviewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.is_closing = False
        self.animation = None
        self.stdin_watcher = None
        self.desktops_data: List[Dict] = []
        self.desktop_labels: List[QLabel] = []
        
        # Hauptcontainer aus UI laden
        self.load_ui()
        
        self.setWindowTitle("SmartDesk Overview")
        
        # STIL: Rahmenlos, immer oben, kein Taskleisten-Icon
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # Desktop-Liste laden und anzeigen
        self.load_desktops()
        self.populate_desktop_list()
        
        self.setup_positioning()
        self.setup_stdin_watcher()

    def get_desktops_file_path(self) -> Path:
        """
        Ermittelt den Pfad zur desktops.json Datei.
        
        Returns:
            Path: Pfad zur JSON-Datei
        """
        appdata = os.getenv('APPDATA')
        if not appdata:
            logger.error("APPDATA Umgebungsvariable nicht gefunden")
            return Path()
        
        return Path(appdata) / "SmartDesk" / "desktops.json"

    def load_desktops(self) -> bool:
        """
        Lädt die Desktop-Konfigurationen aus der JSON-Datei.
        
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        json_path = self.get_desktops_file_path()
        
        try:
            if not json_path.exists():
                logger.warning(f"Desktop-Datei nicht gefunden: {json_path}")
                self.desktops_data = []
                return False
            
            with open(json_path, 'r', encoding='utf-8') as f:
                self.desktops_data = json.load(f)
            
            logger.info(f"{len(self.desktops_data)} Desktops geladen")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Fehler beim Parsen der JSON-Datei: {e}")
            self.desktops_data = []
            return False
        except Exception as e:
            logger.error(f"Fehler beim Laden der Desktops: {e}")
            self.desktops_data = []
            return False

    def populate_desktop_list(self):
        """
        Erstellt Labels für jeden Desktop im horizontalen Layout.
        Hebt den aktiven Desktop visuell hervor.
        """
        try:
            # Container-Widget finden
            container = self.findChild(QWidget, "desktops_container")
            if not container:
                logger.error("desktops_container Widget nicht gefunden")
                return
            
            # Altes Layout leeren
            if container.layout():
                while container.layout().count():
                    item = container.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            else:
                # Neues horizontales Layout erstellen
                layout = QHBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(12)
            
            self.desktop_labels.clear()
            
            if not self.desktops_data:
                # Platzhalter bei leerer Liste
                label = self._create_desktop_label("Keine Desktops", is_active=False, is_placeholder=True)
                container.layout().addWidget(label)
                return
            
            # Desktop-Labels erstellen
            for desktop in self.desktops_data:
                desktop_name = desktop.get("name", "Unbenannt")
                is_active = desktop.get("is_active", False)
                
                label = self._create_desktop_label(desktop_name, is_active)
                self.desktop_labels.append(label)
                container.layout().addWidget(label)
            
            # Stretch am Ende für linksbündige Ausrichtung
            container.layout().addStretch()
            
            logger.debug(f"{len(self.desktop_labels)} Desktop-Labels erstellt")
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Desktop-Labels: {e}")

    def _create_desktop_label(self, text: str, is_active: bool = False, is_placeholder: bool = False) -> QLabel:
        """
        Erstellt ein gestyltes Label für einen Desktop.
        
        Args:
            text: Desktop-Name
            is_active: Ob dieser Desktop aktiv ist
            is_placeholder: Ob dies ein Platzhalter ist
            
        Returns:
            QLabel: Gestyltes Label
        """
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        
        # Font
        font = QFont("Segoe UI", 10)
        if is_active:
            font.setWeight(QFont.DemiBold)
        label.setFont(font)
        
        # Styling
        if is_placeholder:
            label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: #888888;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-style: italic;
                }
            """)
        elif is_active:
            # Aktiver Desktop: Dezentes Grün
            label.setStyleSheet("""
                QLabel {
                    background-color: rgba(20, 160, 133, 0.15);
                    color: #1abc9c;
                    padding: 8px 16px;
                    border: 1px solid rgba(20, 160, 133, 0.4);
                    border-radius: 8px;
                }
            """)
        else:
            # Inaktiver Desktop
            label.setStyleSheet("""
                QLabel {
                    background-color: rgba(60, 60, 60, 0.6);
                    color: #cccccc;
                    padding: 8px 16px;
                    border: 1px solid rgba(80, 80, 80, 0.5);
                    border-radius: 8px;
                }
            """)
        
        return label

    def refresh_desktop_list(self):
        """
        Aktualisiert die Desktop-Liste durch erneutes Laden der Datei.
        """
        if self.load_desktops():
            self.populate_desktop_list()
            logger.info("Desktop-Liste aktualisiert")

    def load_ui(self):
        """Lädt die UI-Datei und erstellt das Hauptlayout."""
        # Manuell ein Container-Widget erstellen, da wir das Layout selbst verwalten
        main_widget = QWidget()
        main_widget.setObjectName("Form")
        main_widget.setStyleSheet("""
            #Form {
                background-color: #2b2b2b;
                border: 1px solid #454545;
                border-radius: 15px;
            }
            QWidget {
                color: #ffffff;
            }
        """)
        
        # Hauptlayout
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)
        
        # Container für Desktop-Labels
        desktops_container = QWidget()
        desktops_container.setObjectName("desktops_container")
        main_layout.addWidget(desktops_container)
        
        # Fenster-Layout
        window_layout = QHBoxLayout(self)
        window_layout.setContentsMargins(10, 0, 0, 0)
        window_layout.addWidget(main_widget)
        
        # Feste Höhe, flexible Breite
        self.setMinimumSize(300, 70)
        self.setMaximumHeight(70)

    def setup_positioning(self):
        """Positioniert das Fenster am unteren Bildschirmrand."""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        full_geometry = screen.geometry()
        
        self.adjustSize()
        self.window_width = self.width()
        self.window_height = 80  # Feste Höhe
        self.target_x = (full_geometry.width() - self.window_width) // 2
        
        # Positionierung
        self.target_y = screen_geometry.height() - self.window_height
        self.start_y = full_geometry.height()
        self.setGeometry(self.target_x, self.start_y, self.window_width, self.window_height)

    def setup_stdin_watcher(self):
        """Startet den stdin-Watcher mit Signal/Slot."""
        self.stdin_watcher = StdinWatcher()
        self.stdin_watcher.stdin_closed.connect(self.on_stdin_closed)
        self.stdin_watcher.start()

    def on_stdin_closed(self):
        """Wird aufgerufen, wenn stdin geschlossen wurde."""
        logger.debug("on_stdin_closed() - Starte Schließen")
        if not self.is_closing:
            self.close_window()

    def show_animated(self):
        """Zeigt das Fenster mit Einblend-Animation."""
        
        self.show()
        self.raise_()
        self.is_closing = False
        
        ensure_taskbar_on_top()
        
        # Animation: Einblenden von unten
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(self.target_x, self.start_y, self.width(), self.height()))
        self.animation.setEndValue(QRect(self.target_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.animation.finished.connect(self._set_focus_after_animation)
        self.animation.start()

    def _set_focus_after_animation(self):
        if not self.is_closing:
            release_taskbar_from_top()
            self.activateWindow()
            self.setFocus()

    def close_window(self):
        if self.is_closing:
            return
        
        logger.debug("close_window() aufgerufen")
        
        if self.stdin_watcher:
            self.stdin_watcher.stop()
        
        self.animate_out(callback=self.close)

    def animate_out(self, callback=None):
        self.is_closing = True
        logger.debug("animate_out() - Starte Slide-Down Animation")
        
        ensure_taskbar_on_top()
        
        # Animation: Ausblenden nach unten
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300) 
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(self.target_x, self.start_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        
        if callback:
            self.animation.finished.connect(callback)
        self.animation.start()

    def event(self, event):
        if event.type() == event.Type.WindowDeactivate and not self.is_closing:
            logger.debug("WindowDeactivate Event - Schließe Fenster")
            self.close_window()
        return super().event(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_window()
        else:
            super().keyPressEvent(event)


def show_overview():
    app = QApplication.instance() or QApplication(sys.argv)
    window = OverviewWindow()
    
    window.show_animated()
    app.exec()


if __name__ == "__main__":
    show_overview()