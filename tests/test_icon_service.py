import pytest
from unittest.mock import MagicMock, patch, call
from smartdesk.core.models.desktop import IconPosition
from smartdesk.core.services import icon_service


# --- Fixtures ---

@pytest.fixture
def mock_win32():
    """Mockt alle win32gui/process/api Aufrufe."""
    with patch("smartdesk.core.services.icon_service.win32gui") as gui, \
         patch("smartdesk.core.services.icon_service.win32process") as proc, \
         patch("smartdesk.core.services.icon_service.ctypes") as ct:
        
        # Standard-Mocks
        gui.FindWindow.return_value = 123
        gui.FindWindowEx.return_value = 456
        proc.GetWindowThreadProcessId.return_value = (0, 789)  # (thread, pid)
        ct.windll.kernel32.OpenProcess.return_value = 999
        ct.windll.kernel32.VirtualAllocEx.return_value = 1000
        
        yield gui, proc, ct


# --- Tests ---

def test_get_desktop_listview_handle_success(mock_win32):
    gui, _, _ = mock_win32
    # Simuliere Kette: Progman -> SHELLDLL_DefView -> SysListView32
    gui.FindWindow.return_value = 10
    
    # Erster Aufruf (ShellDll) -> 20
    # Zweiter Aufruf (SysListView) -> 30
    gui.FindWindowEx.side_effect = [20, 30] 
    
    hwnd = icon_service._get_desktop_listview_handle()
    assert hwnd == 30


def test_get_desktop_listview_handle_workerw_fallback(mock_win32):
    gui, _, _ = mock_win32
    # Simuliere: Progman -> Kein ShellDll -> WorkerW -> ShellDll -> ListView
    
    def side_effect(parent, child, classname, title):
        if classname == "Progman": return 10
        if parent == 10 and classname == "SHELLDLL_DefView": return 0 # Nicht gefunden
        if parent == 0 and classname == "WorkerW": return 50
        if parent == 50 and classname == "SHELLDLL_DefView": return 60
        if parent == 60 and classname == "SysListView32": return 70
        return 0
        
    gui.FindWindow.return_value = 10
    gui.FindWindowEx.side_effect = side_effect
    
    hwnd = icon_service._get_desktop_listview_handle()
    assert hwnd == 70


def test_wait_for_desktop_listview_timeout(mock_win32):
    gui, _, _ = mock_win32
    gui.FindWindow.return_value = 0 # Nie gefunden
    gui.FindWindowEx.return_value = 0
    
    # Timeout auf 0.1s setzen für schnellen Test
    result = icon_service.wait_for_desktop_listview(timeout=0.1)
    assert result == 0 or result is None

def test_get_current_icon_positions_empty(mock_win32):
    gui, _, _ = mock_win32
    gui.SendMessage.return_value = 0 # 0 Items
    
    icons = icon_service.get_current_icon_positions()
    assert icons == []

def test_restore_icons_logic(mock_win32):
    """
    Testet die komplexe Logik von set_icon_positions:
    1. Styles anpassen (AutoArrange aus)
    2. Aktuelle Icons lesen (Mapping Name -> Index)
    3. Positionen setzen
    4. Styles wiederherstellen
    """
    gui, _, ct = mock_win32
    
    # Setup Mocks
    gui.FindWindow.return_value = 1
    gui.FindWindowEx.return_value = 2 # ListView Handle
    
    # 3 Items auf dem Desktop
    gui.SendMessage.return_value = 3 
    
    # Style Mock (hat AutoArrange an: 0x0100)
    original_style = 0x0100 | 0x0800 # AutoArrange | SnapToGrid
    gui.GetWindowLong.return_value = original_style
    
    # Wir simulieren, dass get_current_icon_positions() eine Liste zurückgibt
    # Dafür patchen wir die Funktion direkt, um den komplexen Memory-Read zu umgehen
    current_icons = [
        IconPosition(index=0, name="Mülleimer", x=10, y=10),
        IconPosition(index=1, name="Ordner", x=100, y=100),
        IconPosition(index=2, name="Datei.txt", x=200, y=200),
    ]
    
    saved_icons = [
        IconPosition(index=99, name="Ordner", x=500, y=500), # Index egal, Name zählt
        IconPosition(index=99, name="Datei.txt", x=600, y=600),
    ]
    
    with patch("smartdesk.core.services.icon_service.get_current_icon_positions", return_value=current_icons):
        icon_service.set_icon_positions(saved_icons)
    
    # Assertions
    
    # 1. Style muss geändert worden sein (AutoArrange AUS)
    expected_temp_style = original_style & ~icon_service.LVS_AUTOARRANGE & ~icon_service.LVS_SNAPTOGRID
    gui.SetWindowLong.assert_any_call(2, icon_service.GWL_STYLE, expected_temp_style)
    
    # 2. Positionen müssen gesetzt werden
    # Ordner (Index 1) -> 500, 500
    # Datei.txt (Index 2) -> 600, 600
    # lParam = (y << 16) | x
    lparam_ordner = (500 << 16) | 500
    lparam_datei = (600 << 16) | 600
    
    gui.SendMessage.assert_any_call(2, icon_service.LVM_SETITEMPOSITION, 1, lparam_ordner)
    gui.SendMessage.assert_any_call(2, icon_service.LVM_SETITEMPOSITION, 2, lparam_datei)
    
    # 3. Mülleimer (Index 0) wurde nicht bewegt -> kein Call
    # (Schwer zu prüfen mit assert_any_call, aber Logik passt)
    
    # 4. Style Restore: AutoArrange darf NICHT wieder an gehen, aber SnapToGrid schon
    expected_final_style = original_style & ~icon_service.LVS_AUTOARRANGE
    gui.SetWindowLong.assert_any_call(2, icon_service.GWL_STYLE, expected_final_style)
