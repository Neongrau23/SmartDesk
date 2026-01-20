import os
import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, 
    QMessageBox, QFileDialog, QInputDialog, QMenu
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt, Signal, QPropertyAnimation, QEasingCurve, QRect, QTimer, QEvent

# --- Pfad-Hack ---
if __name__ == "__main__" or __package__ is None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    interfaces_dir = os.path.dirname(current_dir)
    smartdesk_dir = os.path.dirname(interfaces_dir)
    src_dir = os.path.dirname(smartdesk_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

# --- Logger & Services ---
try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

try:
    from smartdesk.core.services import desktop_service
    from smartdesk.shared.localization import get_text
    from smartdesk.shared.config import get_resource_path
except ImportError:
    # Mocks für Standalone-Test
    def get_text(key, **kwargs): return key.split('.')[-1]
    class FakeService:
        def get_all_desktops(self): 
            class D: 
                def __init__(self, n, a): self.name=n; self.is_active=a; self.protected=False; self.wallpaper_path=""
            return [D("Default", True), D("Gaming", False), D("Work", False)]
        def update_desktop(self, old, new, path): return True
        def assign_wallpaper(self, name, path): return True
        def delete_desktop(self, name, delete_folder=False): return True
    desktop_service = FakeService()


class ManageDesktopsWindow(QWidget):
    # Signale für Kommunikation
    closed = Signal()
    
    def __init__(self):
        super().__init__()
        self.is_closing = False
        self.selected_desktop = None
        self.desktop_buttons = [] # Speichert Referenzen zu Buttons
        self.block_close_on_blur = False # Verhindert Schließen bei Dialogen

        self.load_ui()
        self.load_stylesheet()

        # Fenster-Settings
        self.setWindowTitle("Desktops verwalten")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # UI Elemente finden
        self.layout_desktops = self.findChild(QVBoxLayout, "verticalLayout_desktops")
        
        self.btn_rename = self.findChild(QPushButton, "btn_rename")
        self.btn_wallpaper = self.findChild(QPushButton, "btn_wallpaper")
        self.btn_more = self.findChild(QPushButton, "btn_more_options")
        self.btn_close = self.findChild(QPushButton, "btn_close")

        # Buttons deaktivieren bis Auswahl
        self._set_actions_enabled(False)

        # Signale verbinden
        if self.btn_close: self.btn_close.clicked.connect(self.close_panel_animated)
        if self.btn_rename: self.btn_rename.clicked.connect(self.action_rename)
        if self.btn_wallpaper: self.btn_wallpaper.clicked.connect(self.action_wallpaper)
        if self.btn_more: self.btn_more.clicked.connect(self.action_more_options)

        # Liste füllen
        self.refresh_list()
        self.setup_positioning()

    def load_ui(self):
        loader = QUiLoader()
        ui_path = get_resource_path("smartdesk/ui/gui/designer/manage.ui")

        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            logger.error(f"UI nicht gefunden: {ui_path}")
            sys.exit(-1)
        
        container = loader.load(ui_file)
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)
        self.setLayout(layout)

    def load_stylesheet(self):
        try:
            style_path = get_resource_path("smartdesk/ui/gui/style.qss")
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception: pass

    def setup_positioning(self):
        screen = QApplication.primaryScreen()
        geo = screen.availableGeometry()
        self.adjustSize()
        self.resize(420, 350) # Etwas höher für die Liste
        
        padding = 20
        self.target_x = geo.width() - self.width() - padding
        self.target_y = geo.height() - self.height() - padding
        self.start_x = geo.width() # Animation von rechts

        self.setGeometry(self.start_x, self.target_y, self.width(), self.height())

    def refresh_list(self):
        """Leert die Liste und füllt sie neu."""
        # 1. Layout leeren
        while self.layout_desktops.count():
            item = self.layout_desktops.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.desktop_buttons = []
        self.selected_desktop = None
        self._set_actions_enabled(False)

        # 2. Desktops laden
        desktops = desktop_service.get_all_desktops()
        
        # 3. Buttons erstellen
        for d in desktops:
            display_text = f"🖥️ {d.name}"
            if d.is_active: display_text += " (Aktiv)"
            
            btn = QPushButton(display_text)
            btn.setCheckable(True)
            btn.setAutoExclusive(True) # Nur einer gleichzeitig wählbar
            btn.setProperty("class", "desktop_item") # Für QSS Styling
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            
            # Desktop-Objekt am Button speichern (Trick)
            btn.desktop_data = d 
            
            btn.clicked.connect(lambda checked=False, b=btn: self.on_desktop_selected(b))
            
            self.layout_desktops.addWidget(btn)
            self.desktop_buttons.append(btn)
        
        # Spacer am Ende, damit items oben bleiben
        self.layout_desktops.addStretch()

    def on_desktop_selected(self, btn):
        self.selected_desktop = btn.desktop_data
        
        # Buttons aktivieren
        # (Schutz: Aktiven oder geschützten Desktop nicht voll bearbeitbar machen, Logik hier vereinfacht)
        self._set_actions_enabled(True)
        
        logger.debug(f"Gewählt: {self.selected_desktop.name}")

    def _set_actions_enabled(self, enabled):
        if self.btn_rename: self.btn_rename.setEnabled(enabled)
        if self.btn_wallpaper: self.btn_wallpaper.setEnabled(enabled)
        if self.btn_more: self.btn_more.setEnabled(enabled)

    # --- Actions ---

    def action_rename(self):
        if not self.selected_desktop: return
        
        self.block_close_on_blur = True
        new_name, ok = QInputDialog.getText(
            self, "Umbenennen", 
            f"Neuer Name für '{self.selected_desktop.name}':",
            text=self.selected_desktop.name
        )
        self.block_close_on_blur = False
        
        if ok and new_name and new_name != self.selected_desktop.name:
            success = desktop_service.update_desktop(self.selected_desktop.name, new_name, self.selected_desktop.path) # Pfad lassen
            if success:
                self.refresh_list()
            else:
                QMessageBox.warning(self, "Fehler", "Konnte Desktop nicht umbenennen.")

    def action_wallpaper(self):
        if not self.selected_desktop: return
        
        self.block_close_on_blur = True
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Hintergrundbild wählen", "", "Bilder (*.png *.jpg *.jpeg *.bmp)"
        )
        self.block_close_on_blur = False
        
        if file_path:
            desktop_service.assign_wallpaper(self.selected_desktop.name, file_path)
            QMessageBox.information(self, "Erfolg", "Hintergrundbild zugewiesen.")

    def action_more_options(self):
        """Zeigt ein Kontextmenü für Löschen etc."""
        if not self.selected_desktop: return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #3c3c3c; color: white; border: 1px solid #555; }
            QMenu::item:selected { background-color: #d9534f; }
        """)
        
        action_delete = menu.addAction("🗑️ Löschen")
        
        # Zeige Menü unter dem Button
        self.block_close_on_blur = True
        pos = self.btn_more.mapToGlobal(self.btn_more.rect().bottomLeft())
        selected_action = menu.exec(pos)
        self.block_close_on_blur = False
        
        if selected_action == action_delete:
            self._delete_current()

    def _delete_current(self):
        d = self.selected_desktop
        if d.is_active:
            self.block_close_on_blur = True
            QMessageBox.warning(self, "Stopp", "Der aktive Desktop kann nicht gelöscht werden.")
            self.block_close_on_blur = False
            return

        self.block_close_on_blur = True
        confirm = QMessageBox.question(
            self, "Löschen", 
            f"Soll '{d.name}' wirklich gelöscht werden?",
            QMessageBox.Yes | QMessageBox.No
        )
        self.block_close_on_blur = False
        
        if confirm == QMessageBox.Yes:
            desktop_service.delete_desktop(d.name, skip_confirm=True)
            self.refresh_list()

    # --- Animation (Kopie von Control Panel) ---

    def show_animated(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.is_closing = False
        
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(self.start_x, self.target_y, self.width(), self.height()))
        self.anim.setEndValue(QRect(self.target_x, self.target_y, self.width(), self.height()))
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def close_panel_animated(self):
        if self.is_closing: return
        self.is_closing = True
        
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(QRect(self.start_x, self.target_y, self.width(), self.height()))
        self.anim.setEasingCurve(QEasingCurve.InCubic)
        self.anim.finished.connect(self.close)
        self.anim.start()

    def event(self, event):
        # Schließen bei Fokusverlust
        if event.type() == QEvent.Type.WindowDeactivate and not self.is_closing:
            if self.block_close_on_blur:
                return True # Event ignorieren
                
            # Kurzer Check ob Dialoge offen sind (optional), hier einfach schließen
            if not self.isActiveWindow():
                self.close_panel_animated()
        return super().event(event)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ManageDesktopsWindow()
    win.show_animated()
    app.exec()