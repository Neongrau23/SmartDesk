# Dateipfad: tests/test_protected_desktop.py
"""
Tests für den geschützten Original Desktop.

Testet:
- Desktop-Modell mit protected/created_at Feldern
- Löschschutz für geschützte Desktops
- Bearbeitungsschutz für geschützte Desktops
- Sortierung (geschützte Desktops zuerst)
- Original Desktop Erstellung beim Erststart
"""

import pytest
from datetime import datetime
from unittest.mock import patch
import json

from smartdesk.core.models.desktop import Desktop, IconPosition


# =============================================================================
# Desktop Model Tests - Protected Flag
# =============================================================================

class TestDesktopProtectedFlag:
    """Tests für das protected-Feld im Desktop-Modell."""

    def test_desktop_default_not_protected(self):
        """Ein neuer Desktop sollte standardmäßig nicht geschützt sein."""
        desktop = Desktop(name="Test", path="C:\\Test")
        assert desktop.protected is False

    def test_desktop_can_be_created_protected(self):
        """Ein Desktop kann als geschützt erstellt werden."""
        desktop = Desktop(
            name="🔒 Original",
            path="C:\\Users\\Test\\Desktop",
            protected=True
        )
        assert desktop.protected is True

    def test_desktop_created_at_field(self):
        """Das created_at Feld sollte gespeichert werden."""
        timestamp = datetime.now().isoformat()
        desktop = Desktop(
            name="Test",
            path="C:\\Test",
            created_at=timestamp
        )
        assert desktop.created_at == timestamp

    def test_desktop_is_protected_method(self):
        """Die is_protected() Methode sollte den protected-Status zurückgeben."""
        protected_desktop = Desktop(name="Protected", path="C:\\Test", protected=True)
        normal_desktop = Desktop(name="Normal", path="C:\\Test", protected=False)
        
        assert protected_desktop.is_protected() is True
        assert normal_desktop.is_protected() is False

    def test_protected_desktop_to_dict(self):
        """to_dict() sollte protected und created_at enthalten."""
        timestamp = "2025-12-05T10:30:00"
        desktop = Desktop(
            name="🔒 Original",
            path="C:\\Test",
            protected=True,
            created_at=timestamp
        )
        
        data = desktop.to_dict()
        
        assert data["protected"] is True
        assert data["created_at"] == timestamp

    def test_protected_desktop_from_dict(self):
        """from_dict() sollte protected und created_at korrekt laden."""
        data = {
            "name": "🔒 Original (05.12.2025)",
            "path": "C:\\Users\\Test\\Desktop",
            "is_active": True,
            "wallpaper_path": "",
            "icon_positionen": [],
            "protected": True,
            "created_at": "2025-12-05T10:30:00"
        }
        
        desktop = Desktop.from_dict(data)
        
        assert desktop.name == "🔒 Original (05.12.2025)"
        assert desktop.protected is True
        assert desktop.created_at == "2025-12-05T10:30:00"

    def test_legacy_desktop_without_protected_field(self):
        """Alte Desktop-Daten ohne protected-Feld sollten als False geladen werden."""
        legacy_data = {
            "name": "Alter Desktop",
            "path": "C:\\Test",
            "is_active": False,
            "wallpaper_path": "",
            "icon_positionen": []
            # Kein "protected" oder "created_at" Feld
        }
        
        desktop = Desktop.from_dict(legacy_data)
        
        assert desktop.protected is False
        assert desktop.created_at == ""


# =============================================================================
# Delete Protection Tests
# =============================================================================

class TestDeleteProtection:
    """Tests für den Löschschutz."""

    @pytest.fixture
    def mock_desktops_with_protected(self):
        """Desktop-Liste mit einem geschützten Original."""
        return [
            Desktop(
                name="🔒 Original (05.12.2025)",
                path="C:\\Users\\Test\\Desktop",
                is_active=False,
                protected=True,
                created_at="2025-12-05T10:30:00"
            ),
            Desktop(
                name="Arbeit",
                path="C:\\Users\\Test\\Desktop_Arbeit",
                is_active=True,
                protected=False
            ),
            Desktop(
                name="Gaming",
                path="C:\\Users\\Test\\Desktop_Gaming",
                is_active=False,
                protected=False
            ),
        ]

    @patch('smartdesk.core.services.desktop_service.get_all_desktops')
    @patch('smartdesk.core.services.desktop_service.save_desktops')
    def test_cannot_delete_protected_desktop(self, mock_save, mock_get_all, mock_desktops_with_protected, capsys):
        """Ein geschützter Desktop kann nicht gelöscht werden."""
        from smartdesk.core.services.desktop_service import delete_desktop
        
        mock_get_all.return_value = mock_desktops_with_protected
        
        result = delete_desktop("🔒 Original (05.12.2025)")
        
        assert result is False
        mock_save.assert_not_called()
        
        captured = capsys.readouterr()
        assert "geschützt" in captured.out.lower() or "protected" in captured.out.lower()

    @patch('smartdesk.core.services.desktop_service.get_all_desktops')
    @patch('smartdesk.core.services.desktop_service.save_desktops')
    @patch('builtins.input', return_value='y')
    def test_can_delete_unprotected_desktop(self, mock_input, mock_save, mock_get_all, mock_desktops_with_protected):
        """Ein nicht geschützter Desktop kann gelöscht werden."""
        from smartdesk.core.services.desktop_service import delete_desktop
        
        mock_get_all.return_value = mock_desktops_with_protected
        
        result = delete_desktop("Gaming")
        
        assert result is True
        mock_save.assert_called_once()


# =============================================================================
# Edit Protection Tests
# =============================================================================

class TestEditProtection:
    """Tests für den Bearbeitungsschutz."""

    @pytest.fixture
    def mock_desktops_with_protected(self):
        """Desktop-Liste mit einem geschützten Original."""
        return [
            Desktop(
                name="🔒 Original (05.12.2025)",
                path="C:\\Users\\Test\\Desktop",
                is_active=False,
                protected=True,
                created_at="2025-12-05T10:30:00"
            ),
            Desktop(
                name="Arbeit",
                path="C:\\Users\\Test\\Desktop_Arbeit",
                is_active=False,
                protected=False
            ),
        ]

    @patch('smartdesk.core.services.desktop_service.load_desktops')
    @patch('smartdesk.core.services.desktop_service.save_desktops')
    def test_cannot_edit_protected_desktop(self, mock_save, mock_load, mock_desktops_with_protected, capsys):
        """Ein geschützter Desktop kann nicht bearbeitet werden."""
        from smartdesk.core.services.desktop_service import update_desktop
        
        mock_load.return_value = mock_desktops_with_protected
        
        result = update_desktop(
            "🔒 Original (05.12.2025)",
            "Neuer Name",
            "C:\\Neuer\\Pfad"
        )
        
        assert result is False
        mock_save.assert_not_called()
        
        captured = capsys.readouterr()
        assert "geschützt" in captured.out.lower() or "protected" in captured.out.lower()

    @patch('smartdesk.core.services.desktop_service.load_desktops')
    @patch('smartdesk.core.services.desktop_service.save_desktops')
    @patch('os.path.exists', return_value=True)
    @patch('shutil.move')
    def test_can_edit_unprotected_desktop(self, mock_move, mock_exists, mock_save, mock_load, mock_desktops_with_protected):
        """Ein nicht geschützter Desktop kann bearbeitet werden."""
        from smartdesk.core.services.desktop_service import update_desktop
        
        mock_load.return_value = mock_desktops_with_protected
        
        result = update_desktop("Arbeit", "Arbeit Neu", "C:\\Users\\Test\\Desktop_Arbeit")
        
        assert result is True
        mock_save.assert_called_once()


# =============================================================================
# Sorting Tests
# =============================================================================

class TestDesktopSorting:
    """Tests für die Desktop-Sortierung."""

    def test_protected_desktops_sorted_first(self):
        """Geschützte Desktops sollten immer zuerst erscheinen."""
        desktops = [
            Desktop(name="Zebra", path="C:\\Z", protected=False),
            Desktop(name="Arbeit", path="C:\\A", protected=False),
            Desktop(name="🔒 Original", path="C:\\O", protected=True),
            Desktop(name="Gaming", path="C:\\G", protected=False),
        ]
        
        # Sortierung wie in get_all_desktops()
        desktops.sort(key=lambda d: (not d.protected, d.name.lower()))
        
        # Geschützter Desktop sollte zuerst sein
        assert desktops[0].protected is True
        assert desktops[0].name == "🔒 Original"
        
        # Rest alphabetisch
        assert desktops[1].name == "Arbeit"
        assert desktops[2].name == "Gaming"
        assert desktops[3].name == "Zebra"

    def test_multiple_protected_desktops_sorted_alphabetically(self):
        """Mehrere geschützte Desktops sollten untereinander alphabetisch sortiert sein."""
        desktops = [
            Desktop(name="Zebra", path="C:\\Z", protected=False),
            Desktop(name="🔒 Backup 2", path="C:\\B2", protected=True),
            Desktop(name="🔒 Backup 1", path="C:\\B1", protected=True),
        ]
        
        desktops.sort(key=lambda d: (not d.protected, d.name.lower()))
        
        assert desktops[0].name == "🔒 Backup 1"
        assert desktops[1].name == "🔒 Backup 2"
        assert desktops[2].name == "Zebra"


# =============================================================================
# Original Desktop Creation Tests
# =============================================================================

class TestOriginalDesktopCreation:
    """Tests für die Erstellung des Original Desktops."""

    @patch('smartdesk.core.services.icon_service.get_current_icon_positions')
    @patch('smartdesk.shared.first_run.get_current_wallpaper_path')
    @patch('smartdesk.shared.first_run.get_current_desktop_path')
    @patch('smartdesk.core.storage.file_operations.save_desktops')
    @patch('smartdesk.core.storage.file_operations.load_desktops')
    def test_create_original_desktop_success(
        self,
        mock_load,
        mock_save,
        mock_desktop_path,
        mock_wallpaper,
        mock_icons
    ):
        """Original Desktop sollte erfolgreich erstellt werden."""
        from smartdesk.shared.first_run import create_original_desktop
        
        mock_load.return_value = []  # Keine existierenden Desktops
        mock_desktop_path.return_value = "C:\\Users\\Test\\Desktop"
        mock_wallpaper.return_value = "C:\\Wallpaper.jpg"
        mock_icons.return_value = [
            IconPosition(index=0, name="Papierkorb", x=0, y=0)
        ]
        
        result = create_original_desktop(silent=True)
        
        assert result is True
        mock_save.assert_called_once()
        
        # Prüfe den gespeicherten Desktop
        saved_desktops = mock_save.call_args[0][0]
        assert len(saved_desktops) == 1
        
        original = saved_desktops[0]
        assert original.protected is True
        assert "Original" in original.name
        assert "🔒" in original.name
        assert original.path == "C:\\Users\\Test\\Desktop"
        assert original.wallpaper_path == "C:\\Wallpaper.jpg"
        assert len(original.icon_positionen) == 1

    @patch('smartdesk.core.storage.file_operations.save_desktops')
    @patch('smartdesk.core.storage.file_operations.load_desktops')
    def test_skip_if_protected_desktop_exists(self, mock_load, mock_save):
        """Kein neuer Original Desktop wenn bereits einer existiert."""
        from smartdesk.shared.first_run import create_original_desktop
        
        existing_original = Desktop(
            name="🔒 Original (01.12.2025)",
            path="C:\\Users\\Test\\Desktop",
            protected=True
        )
        mock_load.return_value = [existing_original]
        
        result = create_original_desktop(silent=True)
        
        assert result is True
        mock_save.assert_not_called()  # Nicht erneut speichern

    @patch('smartdesk.core.services.icon_service.get_current_icon_positions')
    @patch('smartdesk.shared.first_run.get_current_wallpaper_path')
    @patch('smartdesk.shared.first_run.get_current_desktop_path')
    @patch('smartdesk.core.storage.file_operations.save_desktops')
    @patch('smartdesk.core.storage.file_operations.load_desktops')
    def test_original_desktop_inserted_at_beginning(
        self,
        mock_load,
        mock_save,
        mock_desktop_path,
        mock_wallpaper,
        mock_icons
    ):
        """Original Desktop sollte am Anfang der Liste eingefügt werden."""
        from smartdesk.shared.first_run import create_original_desktop
        
        existing_desktop = Desktop(name="Arbeit", path="C:\\Arbeit", protected=False)
        mock_load.return_value = [existing_desktop]
        mock_desktop_path.return_value = "C:\\Users\\Test\\Desktop"
        mock_wallpaper.return_value = ""
        mock_icons.return_value = []
        
        result = create_original_desktop(silent=True)
        
        assert result is True
        
        saved_desktops = mock_save.call_args[0][0]
        assert len(saved_desktops) == 2
        assert saved_desktops[0].protected is True  # Original zuerst
        assert saved_desktops[1].name == "Arbeit"  # Bestehender danach


# =============================================================================
# Integration Test - JSON Serialization
# =============================================================================

class TestProtectedDesktopSerialization:
    """Tests für die JSON-Serialisierung geschützter Desktops."""

    def test_full_roundtrip(self):
        """Desktop mit allen Feldern sollte korrekt serialisiert/deserialisiert werden."""
        original = Desktop(
            name="🔒 Original (05.12.2025)",
            path="C:\\Users\\Test\\Desktop",
            is_active=True,
            wallpaper_path="C:\\Wallpaper.jpg",
            icon_positionen=[
                IconPosition(index=0, name="Papierkorb", x=100, y=200),
                IconPosition(index=1, name="Dokumente", x=200, y=200),
            ],
            protected=True,
            created_at="2025-12-05T10:30:00"
        )
        
        # Zu JSON und zurück
        json_str = json.dumps(original.to_dict(), ensure_ascii=False)
        loaded_data = json.loads(json_str)
        restored = Desktop.from_dict(loaded_data)
        
        assert restored.name == original.name
        assert restored.path == original.path
        assert restored.is_active == original.is_active
        assert restored.wallpaper_path == original.wallpaper_path
        assert restored.protected == original.protected
        assert restored.created_at == original.created_at
        assert len(restored.icon_positionen) == 2
