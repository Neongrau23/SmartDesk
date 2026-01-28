# Dateipfad: tests/conftest.py
"""
Zentrale pytest-Fixtures für SmartDesk Tests.

Dieses Modul enthält wiederverwendbare Fixtures für:
- Windows Registry Mocking (winreg)
- Filesystem Mocking (os.path, os.makedirs, shutil)
- Temporäre Testverzeichnisse
- Sample Desktop-Objekte
"""

import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any

# Projekt-Root zum Path hinzufügen für Imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Mock winreg before any imports that depend on it (for non-Windows platforms)
if "winreg" not in sys.modules:
    mock_winreg = MagicMock()
    mock_winreg.HKEY_CURRENT_USER = 0x80000001
    mock_winreg.KEY_READ = 0x20019
    mock_winreg.KEY_SET_VALUE = 0x0002
    mock_winreg.REG_SZ = 1
    mock_winreg.REG_EXPAND_SZ = 2
    mock_winreg.REG_DWORD = 4
    sys.modules["winreg"] = mock_winreg

# Mock win32 libraries and PySide6 and others
for lib in ["win32gui", "win32con", "win32api", "win32process", "ctypes", "ctypes.wintypes", "PySide6", "PySide6.QtWidgets", "PySide6.QtGui", "PySide6.QtCore", "colorama", "psutil", "pynput", "pystray", "PIL", "PIL.Image", "customtkinter"]:
    if lib not in sys.modules:
        sys.modules[lib] = MagicMock()

from smartdesk.core.models.desktop import Desktop, IconPosition


# =============================================================================
# Sample Data Fixtures
# =============================================================================


@pytest.fixture
def sample_icon_data() -> Dict[str, Any]:
    """Beispiel-Daten für ein einzelnes Icon."""
    return {"index": 0, "name": "Papierkorb", "x": 100, "y": 200}


@pytest.fixture
def sample_icon(sample_icon_data) -> IconPosition:
    """Ein einzelnes IconPosition-Objekt."""
    return IconPosition.from_dict(sample_icon_data)


@pytest.fixture
def sample_icons_data() -> List[Dict[str, Any]]:
    """Liste von Beispiel-Icon-Daten."""
    return [
        {"index": 0, "name": "Papierkorb", "x": 0, "y": 0},
        {"index": 1, "name": "Dieser PC", "x": 100, "y": 0},
        {"index": 2, "name": "Dokumente", "x": 200, "y": 0},
    ]


@pytest.fixture
def sample_icons(sample_icons_data) -> List[IconPosition]:
    """Liste von IconPosition-Objekten."""
    return [IconPosition.from_dict(data) for data in sample_icons_data]


@pytest.fixture
def sample_desktop_data() -> Dict[str, Any]:
    """Beispiel-Daten für einen einzelnen Desktop."""
    return {
        "name": "Arbeit",
        "path": "C:\\Users\\Test\\Desktop_Arbeit",
        "is_active": False,
        "wallpaper_path": "",
        "icon_positionen": [
            {"index": 0, "name": "Papierkorb", "x": 0, "y": 0},
            {"index": 1, "name": "Projekt.docx", "x": 100, "y": 0},
        ],
    }


@pytest.fixture
def sample_desktop(sample_desktop_data) -> Desktop:
    """Ein einzelnes Desktop-Objekt."""
    return Desktop.from_dict(sample_desktop_data)


@pytest.fixture
def sample_desktops_data() -> List[Dict[str, Any]]:
    """Liste von Beispiel-Desktop-Daten (wie in desktops.json)."""
    return [
        {
            "name": "Standard",
            "path": "C:\\Users\\Test\\Desktop",
            "is_active": True,
            "wallpaper_path": "",
            "icon_positionen": [
                {"index": 0, "name": "Papierkorb", "x": 0, "y": 0},
            ],
        },
        {
            "name": "Arbeit",
            "path": "C:\\Users\\Test\\Desktop_Arbeit",
            "is_active": False,
            "wallpaper_path": "C:\\AppData\\SmartDesk\\wallpapers\\arbeit.jpg",
            "icon_positionen": [
                {"index": 0, "name": "Papierkorb", "x": 0, "y": 0},
                {"index": 1, "name": "Projekt.docx", "x": 100, "y": 0},
            ],
        },
        {"name": "Gaming", "path": "C:\\Users\\Test\\Desktop_Gaming", "is_active": False, "wallpaper_path": "", "icon_positionen": []},
    ]


@pytest.fixture
def sample_desktops(sample_desktops_data) -> List[Desktop]:
    """Liste von Desktop-Objekten."""
    return [Desktop.from_dict(data) for data in sample_desktops_data]


# =============================================================================
# Temporary Directory Fixtures
# =============================================================================


@pytest.fixture
def temp_data_dir(tmp_path):
    """
    Erstellt ein temporäres Datenverzeichnis für Tests.
    Patcht config.DATA_DIR auf dieses Verzeichnis.
    """
    data_dir = tmp_path / "smartdesk_data"
    data_dir.mkdir()

    with patch("smartdesk.shared.config.DATA_DIR", str(data_dir)):
        with patch("smartdesk.shared.config.DESKTOPS_FILE", str(data_dir / "desktops.json")):
            with patch("smartdesk.shared.config.WALLPAPERS_DIR", str(data_dir / "wallpapers")):
                yield data_dir


@pytest.fixture
def temp_desktops_file(temp_data_dir, sample_desktops_data):
    """
    Erstellt eine temporäre desktops.json mit Beispieldaten.
    """
    desktops_file = temp_data_dir / "desktops.json"
    with open(desktops_file, "w", encoding="utf-8") as f:
        json.dump(sample_desktops_data, f, indent=4, ensure_ascii=False)
    return desktops_file


# =============================================================================
# Windows Registry Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_winreg():
    """
    Mock für das winreg-Modul.
    Simuliert erfolgreiche Registry-Operationen.
    """
    with patch("smartdesk.core.utils.registry_operations.winreg") as mock:
        # Konstanten definieren
        mock.HKEY_CURRENT_USER = 0x80000001
        mock.KEY_READ = 0x20019
        mock.KEY_SET_VALUE = 0x0002
        mock.REG_SZ = 1
        mock.REG_EXPAND_SZ = 2
        mock.REG_DWORD = 4

        # Context Manager für OpenKey simulieren
        mock_key = MagicMock()
        mock.OpenKey.return_value.__enter__ = MagicMock(return_value=mock_key)
        mock.OpenKey.return_value.__exit__ = MagicMock(return_value=False)

        # CreateKey simulieren
        mock.CreateKey.return_value = mock_key

        # Standard-Rückgabewerte
        mock.QueryValueEx.return_value = ("C:\\Users\\Test\\Desktop", mock.REG_EXPAND_SZ)

        yield mock


@pytest.fixture
def mock_winreg_failure():
    """
    Mock für winreg mit simulierten Fehlern.
    """
    with patch("smartdesk.core.utils.registry_operations.winreg") as mock:
        mock.HKEY_CURRENT_USER = 0x80000001
        mock.KEY_READ = 0x20019
        mock.KEY_SET_VALUE = 0x0002

        # Simuliere WindowsError
        mock.OpenKey.side_effect = WindowsError(5, "Zugriff verweigert")
        mock.CreateKey.side_effect = WindowsError(5, "Zugriff verweigert")

        yield mock


# =============================================================================
# Filesystem Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_filesystem():
    """
    Mock für Filesystem-Operationen.
    Simuliert ein virtuelles Dateisystem.
    """
    existing_paths = {
        "C:\\Users\\Test\\Desktop",
        "C:\\Users\\Test\\Desktop_Arbeit",
    }

    def mock_exists(path):
        return os.path.normpath(path) in existing_paths or path in existing_paths

    def mock_isdir(path):
        return mock_exists(path)

    with patch("os.path.exists", side_effect=mock_exists):
        with patch("os.path.isdir", side_effect=mock_isdir):
            with patch("os.makedirs") as mock_makedirs:
                with patch("shutil.rmtree") as mock_rmtree:
                    with patch("shutil.move") as mock_move:
                        yield {
                            "exists": mock_exists,
                            "makedirs": mock_makedirs,
                            "rmtree": mock_rmtree,
                            "move": mock_move,
                            "existing_paths": existing_paths,
                        }


@pytest.fixture
def mock_filesystem_failure():
    """
    Mock für Filesystem mit simulierten Fehlern.
    """
    with patch("os.path.exists", return_value=False):
        with patch("os.makedirs", side_effect=OSError(13, "Permission denied")):
            yield


# =============================================================================
# Combined Fixtures für Integration Tests
# =============================================================================


@pytest.fixture
def mock_all(mock_winreg, mock_filesystem, temp_data_dir):
    """
    Kombinierte Fixture für alle Mocks.
    Ideal für Integration-Tests des desktop_handler.
    """
    return {
        "winreg": mock_winreg,
        "filesystem": mock_filesystem,
        "data_dir": temp_data_dir,
    }


# =============================================================================
# psutil Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_psutil():
    """
    Mock für psutil (Prozess-Management).
    """
    with patch("smartdesk.core.utils.registry_operations.psutil") as mock:
        mock.pid_exists.return_value = True
        mock_process = MagicMock()
        mock_process.is_running.return_value = True
        mock.Process.return_value = mock_process
        yield mock


@pytest.fixture
def mock_psutil_no_process():
    """
    Mock für psutil wenn Prozess nicht existiert.
    """
    with patch("smartdesk.core.utils.registry_operations.psutil") as mock:
        mock.pid_exists.return_value = False
        yield mock


# =============================================================================
# Localization Mock
# =============================================================================


@pytest.fixture
def mock_localization():
    """
    Mock für get_text Funktion.
    Gibt den Key als Text zurück für einfaches Testen.
    """

    def mock_get_text(key, **kwargs):
        return f"[{key}]"

    with patch("smartdesk.shared.localization.get_text", side_effect=mock_get_text):
        yield mock_get_text


# =============================================================================
# Helper Functions
# =============================================================================


def create_temp_desktops_json(directory, desktops_data):
    """
    Hilfsfunktion zum Erstellen einer temporären desktops.json.

    Args:
        directory: Pfad zum Verzeichnis
        desktops_data: Liste von Desktop-Dicts

    Returns:
        Pfad zur erstellten Datei
    """
    file_path = os.path.join(directory, "desktops.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(desktops_data, f, indent=4, ensure_ascii=False)
    return file_path
