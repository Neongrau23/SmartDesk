import pytest
import sys
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication, QMenu
from smartdesk.ui.tray.tray_manager import TrayManager
from smartdesk.core.models.desktop import Desktop


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_services():
    with patch("smartdesk.ui.tray.tray_manager.desktop_service") as ds, \
         patch("smartdesk.ui.tray.tray_manager.hotkey_manager") as hm:
        
        # Standard Desktops
        ds.get_all_desktops.return_value = [
            Desktop(name="Default", path="C:\\Desktop1", is_active=True, protected=True),
            Desktop(name="Gaming", path="C:\\Desktop2", is_active=False)
        ]
        
        hm.is_listener_running.return_value = True
        
        yield ds, hm


def test_tray_menu_structure(qapp, mock_services):
    """Testet, ob das Kontextmenü korrekt aufgebaut wird."""
    ds, _ = mock_services
    
    manager = TrayManager(MagicMock()) # Parent Mock
    menu = manager.create_context_menu()
    
    assert isinstance(menu, QMenu)
    actions = menu.actions()
    
    # Wir erwarten:
    # 1. Default (Active)
    # 2. Gaming
    # 3. Separator
    # 4. Settings/Tools...
    # 5. Quit
    
    # Prüfe Desktop Einträge
    assert len(actions) > 3
    
    # Prüfe ob Desktops da sind
    desktop_actions = [a for a in actions if hasattr(a, "data") and a.data() == "desktop_switch"]
    assert len(desktop_actions) == 2
    assert "Default" in desktop_actions[0].text()
    assert "Gaming" in desktop_actions[1].text()
    
    # Prüfe Checkmark beim aktiven Desktop
    assert desktop_actions[0].isChecked()
    assert not desktop_actions[1].isChecked()


def test_tray_menu_updates(qapp, mock_services):
    """Testet Updates des Menüs."""
    ds, _ = mock_services
    
    manager = TrayManager(MagicMock())
    
    # Initial
    menu1 = manager.create_context_menu()
    assert len([a for a in menu1.actions() if hasattr(a, "data") and a.data() == "desktop_switch"]) == 2
    
    # Update: Neuer Desktop
    ds.get_all_desktops.return_value.append(
        Desktop(name="Work", path="C:\\Desktop3", is_active=False)
    )
    
    menu2 = manager.create_context_menu()
    desktop_actions = [a for a in menu2.actions() if hasattr(a, "data") and a.data() == "desktop_switch"]
    assert len(desktop_actions) == 3
    assert "Work" in desktop_actions[2].text()
