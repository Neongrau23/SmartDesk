import os
import logging
from PySide6.QtWidgets import (
    QWidget, QFileDialog, QMessageBox, QListWidget, QListWidgetItem, 
    QLabel, QPushButton, QStackedWidget, QLineEdit, QRadioButton,
    QInputDialog, QGroupBox, QHBoxLayout, QVBoxLayout
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt, QSize
from PySide6.QtGui import QPixmap, QIcon

from smartdesk.core.services import desktop_service
from smartdesk.core.services.auto_switch_service import AutoSwitchService
from smartdesk.shared.localization import get_text

# Logger Setup
try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

class DesktopPage(QWidget):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_connections()
        self.refresh_list()
        
        # Startzustand: Leer
        self.stack_content.setCurrentIndex(0) # page_empty

    def load_ui(self):
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "ui", "desktop_page.ui")
        
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
        self.list_desktops = self.ui.findChild(QListWidget, "list_desktops")
        self.btn_add = self.ui.findChild(QPushButton, "btn_add_desktop")
        self.stack_content = self.ui.findChild(QStackedWidget, "stack_content")
        
        # Details Page Elements
        self.lbl_name = self.ui.findChild(QLabel, "label_desktop_name")
        self.btn_edit_name = self.ui.findChild(QPushButton, "btn_edit_name")
        self.lbl_path = self.ui.findChild(QLabel, "label_desktop_path")
        self.lbl_status = self.ui.findChild(QLabel, "label_status_badge")
        self.img_preview = self.ui.findChild(QLabel, "img_wallpaper_preview")
        self.btn_change_wp = self.ui.findChild(QPushButton, "btn_change_wallpaper")
        self.btn_activate = self.ui.findChild(QPushButton, "btn_activate_desktop")
        self.btn_delete = self.ui.findChild(QPushButton, "btn_delete_desktop")
        
        # Create Page Elements
        self.inp_name = self.ui.findChild(QLineEdit, "inp_create_name")
        self.inp_path = self.ui.findChild(QLineEdit, "inp_create_path")
        self.btn_browse = self.ui.findChild(QPushButton, "btn_browse_path")
        self.btn_confirm_create = self.ui.findChild(QPushButton, "btn_confirm_create")
        self.btn_cancel_create = self.ui.findChild(QPushButton, "btn_cancel_create")
        self.radio_existing = self.ui.findChild(QRadioButton, "radio_existing")
        self.radio_new = self.ui.findChild(QRadioButton, "radio_new")

        # Auto Switch UI Injection
        self.layout_info = self.ui.findChild(QVBoxLayout, "layout_info_container")
        self.setup_auto_switch_ui()

    def setup_auto_switch_ui(self):
        if not self.layout_info: return
        
        # GroupBox
        self.group_rules = QGroupBox("VERKNÜPFTE PROGRAMME (AUTO-SWITCH)")
        self.group_rules.setStyleSheet("QGroupBox { font-weight: bold; color: #00b4d8; margin-top: 10px; }")
        layout_rules = QVBoxLayout()
        
        # List
        self.list_programs = QListWidget()
        self.list_programs.setMaximumHeight(100)
        self.list_programs.setToolTip("Programme, die diesen Desktop automatisch aktivieren")
        layout_rules.addWidget(self.list_programs)
        
        # Controls
        hl_controls = QHBoxLayout()
        self.inp_program = QLineEdit()
        self.inp_program.setPlaceholderText("Prozessname (z.B. code.exe) oder leer lassen für Auswahl")
        
        self.btn_add_prog = QPushButton("+")
        self.btn_add_prog.setFixedWidth(40)
        self.btn_add_prog.setToolTip("Hinzufügen")
        self.btn_add_prog.clicked.connect(self.action_add_program)
        
        self.btn_del_prog = QPushButton("-")
        self.btn_del_prog.setFixedWidth(40)
        self.btn_del_prog.setToolTip("Entfernen")
        self.btn_del_prog.clicked.connect(self.action_remove_program)
        
        hl_controls.addWidget(self.inp_program)
        hl_controls.addWidget(self.btn_add_prog)
        hl_controls.addWidget(self.btn_del_prog)
        
        layout_rules.addLayout(hl_controls)
        self.group_rules.setLayout(layout_rules)
        
        # Insert at index 2 (after Title and Path Card)
        self.layout_info.insertWidget(2, self.group_rules)

    def refresh_linked_programs(self, desktop_name):
        if not hasattr(self, 'list_programs'): return
        self.list_programs.clear()
        
        # Service Instanz nur zum Lesen/Schreiben der JSON nutzen
        svc = AutoSwitchService() 
        rules = svc.get_rules()
        
        for proc, desk in rules.items():
            if desk == desktop_name:
                item = QListWidgetItem(proc)
                self.list_programs.addItem(item)

    def action_add_program(self):
        if not hasattr(self, 'current_desktop') or not self.current_desktop: return
        
        proc_name = self.inp_program.text().strip()
        if not proc_name:
            # File Dialog
            file_path, _ = QFileDialog.getOpenFileName(self, "Programm wählen", "", "Executable (*.exe);;All Files (*)")
            if file_path:
                proc_name = os.path.basename(file_path)
            else:
                return

        svc = AutoSwitchService()
        svc.add_rule(proc_name, self.current_desktop.name)
        
        self.inp_program.clear()
        self.refresh_linked_programs(self.current_desktop.name)
        
    def action_remove_program(self):
        if not hasattr(self, 'current_desktop') or not self.current_desktop: return
        
        selected = self.list_programs.currentItem()
        if not selected: return
        
        proc_name = selected.text()
        
        svc = AutoSwitchService()
        svc.delete_rule(proc_name)
        
        self.refresh_linked_programs(self.current_desktop.name)

    def setup_connections(self):
        # Sidebar
        if self.list_desktops: self.list_desktops.itemSelectionChanged.connect(self.on_selection_changed)
        if self.btn_add: self.btn_add.clicked.connect(self.show_create_view)
        
        # Details Actions
        if self.btn_edit_name: self.btn_edit_name.clicked.connect(self.action_rename_desktop)
        
        if self.btn_change_wp:
            self.btn_change_wp.clicked.connect(self.action_change_wallpaper)
        else:
            logger.error("UI Error: 'btn_change_wallpaper' not found via findChild!")

        if self.btn_activate: self.btn_activate.clicked.connect(self.action_activate_desktop)
        if self.btn_delete: self.btn_delete.clicked.connect(self.action_delete_desktop)
        
        # Create Actions
        if self.btn_browse: self.btn_browse.clicked.connect(self.action_browse_folder)
        if self.btn_confirm_create: self.btn_confirm_create.clicked.connect(self.action_create_desktop)
        if self.btn_cancel_create: self.btn_cancel_create.clicked.connect(lambda: self.stack_content.setCurrentIndex(0)) # Zurück zu Empty oder Last

    def refresh_list(self):
        self.list_desktops.clear()
        active_item = None

        try:
            desktops = desktop_service.get_all_desktops(sync_registry=True)
            for d in desktops:
                # Icon basierend auf Status
                display_text = f"  {d.name}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, d.name)
                
                # Visual Indicator für Active (optional via Font oder Color, hier simpel Text)
                if d.is_active:
                    item.setText(f"🟢 {d.name}")
                    item.setToolTip("Aktiver Desktop")
                    active_item = item # Merke das aktive Item
                else:
                    item.setText(f"⚪ {d.name}")
                
                self.list_desktops.addItem(item)
            
            # Automatisch den aktiven Desktop selektieren, wenn keiner selektiert ist
            # oder wenn wir gerade erst geladen haben
            if active_item and not self.list_desktops.selectedItems():
                self.list_desktops.setCurrentItem(active_item)

        except Exception as e:
            logger.error(f"Error loading desktops: {e}")

    def on_selection_changed(self):
        selected = self.list_desktops.selectedItems()
        if not selected:
            # Wenn wir nicht gerade im Create Modus sind, zeige Empty
            if self.stack_content.currentIndex() != 2:
                self.stack_content.setCurrentIndex(0)
            return
            
        name = selected[0].data(Qt.UserRole)
        self.load_details(name)
        self.stack_content.setCurrentIndex(1) # Show Details Page

    def load_details(self, name):
        try:
            desktops = desktop_service.get_all_desktops(sync_registry=True)
            desktop = next((d for d in desktops if d.name == name), None)
            
            if not desktop: return
            
            self.current_desktop = desktop # Speichern für Aktionen
            
            self.lbl_name.setText(desktop.name)
            self.lbl_path.setText(desktop.path)
            
            # Disable Edit Button for protected desktops
            if self.btn_edit_name:
                self.btn_edit_name.setEnabled(not desktop.protected)
                if desktop.protected:
                    self.btn_edit_name.setToolTip("Dieser Desktop kann nicht umbenannt werden.")
                else:
                    self.btn_edit_name.setToolTip("Namen ändern")

            if desktop.is_active:
                self.lbl_status.setVisible(True)
                self.lbl_status.setText("AKTIV")
                self.lbl_status.setStyleSheet("background-color: #1a7a65; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold;")
                self.btn_activate.setEnabled(False)
                self.btn_activate.setText("Bereits aktiv")
                self.btn_delete.setEnabled(False) # Aktive Desktops nicht löschen
            else:
                self.lbl_status.setVisible(False)
                self.btn_activate.setEnabled(True)
                self.btn_activate.setText("Zu diesem Desktop wechseln")
                self.btn_delete.setEnabled(not desktop.protected)

            # Wallpaper Preview
            if desktop.wallpaper_path and os.path.exists(desktop.wallpaper_path):
                pixmap = QPixmap(desktop.wallpaper_path)
                if not pixmap.isNull():
                    w = self.img_preview.width()
                    h = self.img_preview.height()
                    self.img_preview.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.img_preview.setText("Bildfehler")
            else:
                self.img_preview.setText("Kein Wallpaper gesetzt")
                self.img_preview.setPixmap(QPixmap()) # Clear

            # Refresh Rules
            self.refresh_linked_programs(name)

        except Exception as e:
            logger.error(f"Error loading details: {e}")

    # --- ACTIONS ---

    def action_rename_desktop(self):
        if not hasattr(self, 'current_desktop') or not self.current_desktop: return
        
        old_name = self.current_desktop.name
        
        new_name, ok = QInputDialog.getText(
            self, "Desktop umbenennen", 
            f"Neuer Name für '{old_name}':",
            QLineEdit.Normal, old_name
        )
        
        if ok and new_name and new_name != old_name:
            # Wir behalten den alten Pfad, benennen nur logisch um
            current_path = self.current_desktop.path
            
            if desktop_service.update_desktop(old_name, new_name, current_path):
                self.refresh_list()
                
                # Versuche den umbenannten Desktop wieder zu selektieren
                items = self.list_desktops.findItems(f"⚪ {new_name}", Qt.MatchContains)
                if not items: 
                     items = self.list_desktops.findItems(new_name, Qt.MatchContains)
                
                if items:
                    self.list_desktops.setCurrentItem(items[0])
                
                QMessageBox.information(self, "Erfolg", "Name geändert.")
            else:
                QMessageBox.warning(self, "Fehler", "Konnte Namen nicht ändern (ggf. existiert er schon).")

    def show_create_view(self):
        self.list_desktops.clearSelection() # Deselektieren
        self.inp_name.clear()
        self.inp_path.clear()
        self.stack_content.setCurrentIndex(2) # Show Create Page

    def action_browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Ordner wählen")
        if folder:
            self.inp_path.setText(folder)

    def action_create_desktop(self):
        name = self.inp_name.text().strip()
        path = self.inp_path.text().strip().strip('"')

        if not name or not path:
            QMessageBox.warning(self, "Fehlende Eingabe", "Bitte Name und Pfad angeben.")
            return

        create_if_missing = self.radio_new.isChecked()
        final_path = os.path.join(path, name) if create_if_missing else path
        path = os.path.normpath(path)

        try:
            success = desktop_service.create_desktop(name, final_path, create_if_missing=create_if_missing)
            if success:
                QMessageBox.information(self, "Erfolg", f"Desktop '{name}' erstellt.")
                self.refresh_list()
                # Selektiere den neuen Desktop
                items = self.list_desktops.findItems(f"⚪ {name}", Qt.MatchContains)
                if not items: 
                     items = self.list_desktops.findItems(name, Qt.MatchContains)
                
                if items:
                    self.list_desktops.setCurrentItem(items[0])
            else:
                QMessageBox.critical(self, "Fehler", "Konnte Desktop nicht erstellen.")
        except Exception as e:
            logger.error(f"Create Error: {e}")
            QMessageBox.critical(self, "Fehler", str(e))

    def action_change_wallpaper(self):
        logger.debug("Action: Wallpaper ändern ausgelöst.")
        
        if not hasattr(self, 'current_desktop') or not self.current_desktop: 
            logger.warning("Kein Desktop ausgewählt.")
            return

        try:
            # File Dialog Optionen
            options = QFileDialog.Options()
            # Falls native Dialoge Probleme machen, kann man das hier einkommentieren:
            # options |= QFileDialog.DontUseNativeDialog
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Wallpaper auswählen", 
                "", 
                "Bilder (*.png *.jpg *.jpeg *.bmp)",
                options=options
            )
            
            logger.debug(f"Dialog Ergebnis: {file_path}")

            if file_path:
                if desktop_service.assign_wallpaper(self.current_desktop.name, file_path):
                    self.load_details(self.current_desktop.name) # Refresh
                    QMessageBox.information(self, "Erfolg", "Wallpaper wurde aktualisiert.")
                else:
                    logger.error("Service lieferte False zurück.")
                    QMessageBox.warning(self, "Fehler", "Konnte Wallpaper nicht setzen.")
        except Exception as e:
            logger.error(f"Exception in action_change_wallpaper: {e}", exc_info=True)
            QMessageBox.critical(self, "Fehler", f"Ein Fehler ist aufgetreten:\n{e}")

    def action_activate_desktop(self):
        if not hasattr(self, 'current_desktop'): return
        
        reply = QMessageBox.question(
            self, "Bestätigung", 
            f"Möchten Sie wirklich zu '{self.current_desktop.name}' wechseln?\nDer Explorer wird neu gestartet.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = desktop_service.switch_to_desktop(self.current_desktop.name, parent=self)
            
            if success:
                self.refresh_list()
                self.load_details(self.current_desktop.name)
                QMessageBox.information(self, "Erfolg", "Desktop gewechselt.")
            else:
                QMessageBox.warning(self, "Hinweis", "Wechsel nicht durchgeführt (siehe Logs).")

    def action_delete_desktop(self):
        if not hasattr(self, 'current_desktop'): return
        
        name = self.current_desktop.name
        
        if desktop_service.delete_desktop(name, parent=self):
            self.refresh_list()
            self.stack_content.setCurrentIndex(0) # Empty
            QMessageBox.information(self, "Gelöscht", f"Desktop '{name}' wurde entfernt.")
        else:
            QMessageBox.warning(self, "Fehler", "Konnte Desktop nicht löschen (ggf. aktiv oder geschützt).")