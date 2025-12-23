import logging
import os
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QPropertyAnimation, QEasingCurve, QRect, Qt, QTimer
from PySide6.QtGui import QScreen

# --- Logger Setup ---
try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

class OverviewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.is_closing = False
        self.animation = None
        
        self.load_ui()
        
        self.setWindowTitle("SmartDesk Overview")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.setup_positioning()
        
    def load_ui(self):
        """Lädt die designer/overview.ui Datei."""
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Pfad zu designer/overview.ui
        ui_file_path = os.path.join(current_dir, "designer", "overview.ui")
        
        ui_file = QFile(ui_file_path)
        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(f"UI-Datei nicht gefunden: {ui_file_path}")
            # Fallback: Versuche im gleichen Ordner
            ui_file_path = os.path.join(current_dir, "overview.ui")
            ui_file = QFile(ui_file_path)
            if not ui_file.open(QIODevice.ReadOnly):
                logger.error(f"UI-Datei auch nicht gefunden unter: {ui_file_path}")
                sys.exit(-1)
            
        container_widget = loader.load(ui_file)
        ui_file.close()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container_widget)
        self.setLayout(layout)
    
    def setup_positioning(self):
        """Positioniert das Fenster mittig über der Taskleiste."""
        # Primären Bildschirm holen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()  # Bereich ohne Taskleiste
        full_geometry = screen.geometry()  # Voller Bildschirm inkl. Taskleiste
        
        # Fenstergröße aus UI übernehmen
        self.adjustSize()
        self.window_width = self.width()
        self.window_height = self.height()
        
        # Taskleisten-Höhe berechnen
        taskbar_height = full_geometry.height() - screen_geometry.height()
        
        # Mittige Position über der Taskleiste berechnen
        # X: Horizontal zentriert
        self.target_x = (full_geometry.width() - self.window_width) // 2
        
        # Y: Direkt über der Taskleiste mit kleinem Abstand
        padding_bottom = 10  # Abstand zur Taskleiste
        self.target_y = screen_geometry.height() - self.window_height - padding_bottom
        
        # Start-Position (außerhalb des Bildschirms unten)
        self.start_y = full_geometry.height()
        
        # Initiale Position setzen (außerhalb sichtbar)
        self.setGeometry(self.target_x, self.start_y, self.window_width, self.window_height)
        
        logger.debug(f"Fenster: {self.window_width}x{self.window_height}")
        logger.debug(f"Zielposition: ({self.target_x}, {self.target_y})")
        logger.debug(f"Startposition: ({self.target_x}, {self.start_y})")
    
    def show_animated(self):
        """Zeigt das Fenster mit Slide-Up Animation."""
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        self.is_closing = False
        
        # Animation von unten nach oben
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(400)  # 400ms für sanfte Animation
        self.animation.setStartValue(QRect(self.target_x, self.start_y, self.width(), self.height()))
        self.animation.setEndValue(QRect(self.target_x, self.target_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
    
    def close_window(self):
        """Schließt das Fenster mit Animation."""
        if self.is_closing:
            return
        self.animate_out(callback=self.close)
    
    def animate_out(self, callback=None):
        """Animiert das Fenster nach unten aus dem Bildschirm."""
        self.is_closing = True
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(self.target_x, self.start_y, self.width(), self.height()))
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        
        if callback:
            self.animation.finished.connect(callback)
        
        self.animation.start()
    
    def event(self, event):
        """Schließt das Fenster bei Fokus-Verlust."""
        if event.type() == event.Type.WindowDeactivate and not self.is_closing:
            # Kurze Verzögerung, damit Click-Events noch verarbeitet werden
            QTimer.singleShot(100, self.close_window)
        return super().event(event)
    
    def keyPressEvent(self, event):
        """Schließt bei ESC-Taste."""
        if event.key() == Qt.Key_Escape:
            self.close_window()
        else:
            super().keyPressEvent(event)

def show_overview():
    """Hauptfunktion zum Starten des Overview-Fensters."""
    app = QApplication.instance() or QApplication(sys.argv)
    
    window = OverviewWindow()
    window.show_animated()
    
    app.exec()

if __name__ == "__main__":
    show_overview()
