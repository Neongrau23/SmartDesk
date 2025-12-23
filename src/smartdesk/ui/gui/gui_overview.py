# Dateipfad: src/smartdesk/ui/gui/gui_overview.py
import logging
import os
import sys
import threading
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QPropertyAnimation, QEasingCurve, QRect, Qt, QTimer, Signal, QObject
from PySide6.QtGui import QScreen

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
            # Blockierendes Read - wird sofort beendet, wenn stdin geschlossen wird
            while not self._stop.is_set():
                try:
                    # Versuche ein Byte zu lesen
                    data = sys.stdin.read(1)
                    if not data:  # EOF = stdin geschlossen
                        logger.debug("stdin EOF erkannt - emittiere Signal")
                        self.stdin_closed.emit()
                        break
                except Exception as e:
                    # Fehler beim Lesen = stdin ungültig/geschlossen
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
        self.load_ui()
        self.setWindowTitle("SmartDesk Overview")
        # STIL: Rahmenlos, immer oben, kein Taskleisten-Icon
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setup_positioning()
        self.setup_stdin_watcher()

    def load_ui(self):
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file_path = os.path.join(current_dir, "designer", "overview.ui")
        ui_file = QFile(ui_file_path)
        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(f"UI-Datei nicht gefunden: {ui_file_path}")
            sys.exit(-1)
        container_widget = loader.load(ui_file)
        ui_file.close()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container_widget)
        self.setLayout(layout)

    def setup_positioning(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        full_geometry = screen.geometry()
        self.adjustSize()
        self.window_width = self.width()
        self.window_height = self.height()
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
        ## AKTION: Fenster wird sichtbar.
        self.show()
        self.raise_()
        self.is_closing = False
        
        # ANIMATION: Einblenden von unten nach oben.
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(self.target_x, self.start_y, self.width(), self.height()))
        self.animation.setEndValue(QRect(self.target_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # ZIEL: Nach Animation Fokus holen.
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
        
        logger.debug("close_window() aufgerufen - Starte Animation")
        
        # Watcher stoppen
        if self.stdin_watcher:
            self.stdin_watcher.stop()
        
        # Callback 'self.close' sorgt dafür, dass Qt das Fenster zerstört
        self.animate_out(callback=self.close)

    def animate_out(self, callback=None):
        self.is_closing = True
        logger.debug("animate_out() - Starte Slide-Down Animation")
        
        # ANIMATION: Ausblenden (oben nach unten)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300) 
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(self.target_x, self.start_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        
        if callback:
            self.animation.finished.connect(callback)
        self.animation.start()

    def event(self, event):
        # Schließen bei Fokusverlust
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