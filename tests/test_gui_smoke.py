import pytest
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Stelle sicher, dass wir 'offscreen' nutzen (wird auch via ENV in CI gesetzt)
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Imports der GUIs
from smartdesk.ui.gui.gui_create import CreateDesktopWindow
from smartdesk.ui.gui.gui_manage import ManageDesktopsWindow
from smartdesk.ui.gui.gui_main import SmartDeskMainWindow


@pytest.fixture(scope="session")
def qapp():
    """Erstellt eine QApplication für die gesamte Test-Session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Kein app.exec() oder quit() nötig im Test


def test_create_window_smoke(qapp):
    """Prüft, ob sich der 'Erstellen'-Dialog öffnen lässt."""
    window = CreateDesktopWindow()
    assert window is not None
    assert window.windowTitle() != ""
    
    # Widgets prüfen
    assert window.name_entry is not None
    assert window.btn_create is not None
    
    window.close()


def test_manage_window_smoke(qapp):
    """Prüft, ob sich der 'Verwalten'-Dialog öffnen lässt."""
    window = ManageDesktopsWindow()
    assert window is not None
    assert window.windowTitle() != ""
    
    # Liste prüfen
    assert window.layout_desktops is not None
    
    window.close()


def test_main_window_smoke(qapp):
    """Prüft, ob sich das Hauptfenster öffnen lässt."""
    window = SmartDeskMainWindow()
    assert window is not None
    assert window.windowTitle() != ""
    
    # Stacked Widget prüfen
    assert window.stacked_widget is not None
    assert window.stacked_widget.count() >= 2 # Dashboard + Desktops (+ Settings)
    
    window.close()
