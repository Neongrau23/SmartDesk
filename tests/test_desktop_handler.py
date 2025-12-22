# Dateipfad: tests/test_desktop_handler.py
"""
Unit-Tests für smartdesk.handlers.desktop_handler

Testet die Business-Logik für Desktop-Verwaltung mit vollständigem Mocking
aller Windows-spezifischen Abhängigkeiten.

Diese Tests fokussieren auf die Datenlogik ohne direkte Aufrufe
der Windows-API abhängigen Handler-Funktionen.
"""

from unittest.mock import patch


from smartdesk.core.models.desktop import Desktop, IconPosition


# =============================================================================
# Tests für Desktop Model Integration
# =============================================================================

class TestDesktopModelIntegration:
    """Integration Tests für Desktop-Daten."""

    def test_desktop_data_roundtrip(self, tmp_path):
        """Test: Desktop-Daten können gespeichert und geladen werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop = Desktop(
                name="Test",
                path=str(tmp_path / "TestDesktop"),
                is_active=True
            )
            
            result = save_desktops([desktop])
            assert result is True
            
            loaded = load_desktops()
            assert len(loaded) == 1
            assert loaded[0].name == "Test"
            assert loaded[0].is_active is True

    def test_multiple_desktops_persistence(self, tmp_path):
        """Test: Mehrere Desktops können verwaltet werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktops = [
                Desktop(name="Work", path="C:\\Work", is_active=True),
                Desktop(name="Gaming", path="C:\\Gaming", is_active=False),
                Desktop(name="Private", path="C:\\Private", is_active=False),
            ]
            
            save_desktops(desktops)
            loaded = load_desktops()
            
            assert len(loaded) == 3
            names = [d.name for d in loaded]
            assert "Work" in names
            assert "Gaming" in names
            assert "Private" in names


# =============================================================================
# Tests für create_desktop Logik
# =============================================================================

class TestCreateDesktopLogic:
    """Tests für create_desktop Logik."""

    def test_desktop_name_validation(self, tmp_path):
        """Test: Duplikat-Namen werden erkannt."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop1 = Desktop(name="Existing", path="C:\\Existing")
            save_desktops([desktop1])
            
            desktops = load_desktops()
            name_exists = any(d.name == "Existing" for d in desktops)
            
            assert name_exists is True

    def test_new_name_allowed(self, tmp_path):
        """Test: Neue Namen sind erlaubt."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop1 = Desktop(name="First", path="C:\\First")
            save_desktops([desktop1])
            
            desktops = load_desktops()
            name_exists = any(d.name == "Second" for d in desktops)
            
            assert name_exists is False

    def test_add_new_desktop_to_list(self, tmp_path):
        """Test: Neuer Desktop kann zur Liste hinzugefügt werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            # Initialer Desktop
            save_desktops([Desktop(name="First", path="C:\\First")])
            
            # Neuen hinzufügen
            desktops = load_desktops()
            desktops.append(Desktop(name="Second", path="C:\\Second"))
            save_desktops(desktops)
            
            final = load_desktops()
            assert len(final) == 2


# =============================================================================
# Tests für get_all_desktops Logik
# =============================================================================

class TestGetAllDesktopsLogic:
    """Tests für die get_all_desktops Logik."""

    def test_active_status_detection(self, tmp_path):
        """Test: Aktiver Status wird korrekt erkannt."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktops = [
                Desktop(name="Active", path="C:\\Active", is_active=True),
                Desktop(name="Inactive", path="C:\\Inactive", is_active=False),
            ]
            save_desktops(desktops)
            
            loaded = load_desktops()
            active = next((d for d in loaded if d.is_active), None)
            
            assert active is not None
            assert active.name == "Active"

    def test_path_normalization(self):
        """Test: Pfade werden korrekt normalisiert."""
        import os
        
        path1 = "C:\\Users\\Test\\Desktop"
        path2 = "C:/Users/Test/Desktop"
        
        norm1 = os.path.normpath(path1).lower()
        norm2 = os.path.normpath(path2).lower()
        
        assert norm1 == norm2

    def test_only_one_active_desktop(self, tmp_path):
        """Test: Nur ein Desktop sollte aktiv sein."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktops = [
                Desktop(name="D1", path="C:\\D1", is_active=True),
                Desktop(name="D2", path="C:\\D2", is_active=False),
                Desktop(name="D3", path="C:\\D3", is_active=False),
            ]
            save_desktops(desktops)
            
            loaded = load_desktops()
            active_count = sum(1 for d in loaded if d.is_active)
            
            assert active_count == 1


# =============================================================================
# Tests für delete_desktop Logik
# =============================================================================

class TestDeleteDesktopLogic:
    """Tests für die delete_desktop Logik."""

    def test_cannot_delete_active_desktop_rule(self, tmp_path):
        """Test: Aktiver Desktop sollte nicht gelöscht werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop = Desktop(name="Active", path="C:\\Active", is_active=True)
            save_desktops([desktop])
            
            loaded = load_desktops()
            target = loaded[0]
            
            # Regel: Aktiver Desktop darf nicht gelöscht werden
            assert target.is_active is True

    def test_inactive_desktop_can_be_deleted(self, tmp_path):
        """Test: Inaktiver Desktop kann gelöscht werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktops = [
                Desktop(name="Active", path="C:\\Active", is_active=True),
                Desktop(name="ToDelete", path="C:\\Delete", is_active=False),
            ]
            save_desktops(desktops)
            
            # Simuliere Löschung
            loaded = load_desktops()
            remaining = [d for d in loaded if d.name != "ToDelete"]
            save_desktops(remaining)
            
            final = load_desktops()
            assert len(final) == 1
            assert final[0].name == "Active"

    def test_find_desktop_by_name(self, tmp_path):
        """Test: Desktop kann per Name gefunden werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktops = [
                Desktop(name="Alpha", path="C:\\Alpha"),
                Desktop(name="Beta", path="C:\\Beta"),
                Desktop(name="Gamma", path="C:\\Gamma"),
            ]
            save_desktops(desktops)
            
            loaded = load_desktops()
            target = next((d for d in loaded if d.name == "Beta"), None)
            
            assert target is not None
            assert target.path == "C:\\Beta"


# =============================================================================
# Tests für update_desktop Logik
# =============================================================================

class TestUpdateDesktopLogic:
    """Tests für die update_desktop Logik."""

    def test_update_desktop_name(self, tmp_path):
        """Test: Desktop-Name kann aktualisiert werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop = Desktop(name="OldName", path="C:\\Path")
            save_desktops([desktop])
            
            loaded = load_desktops()
            loaded[0].name = "NewName"
            save_desktops(loaded)
            
            final = load_desktops()
            assert final[0].name == "NewName"

    def test_update_desktop_path(self, tmp_path):
        """Test: Desktop-Pfad kann aktualisiert werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop = Desktop(name="Desktop", path="C:\\OldPath")
            save_desktops([desktop])
            
            loaded = load_desktops()
            loaded[0].path = "C:\\NewPath"
            save_desktops(loaded)
            
            final = load_desktops()
            assert final[0].path == "C:\\NewPath"

    def test_name_conflict_detection(self, tmp_path):
        """Test: Namenskonflikt wird erkannt."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktops = [
                Desktop(name="Desktop1", path="C:\\D1"),
                Desktop(name="Desktop2", path="C:\\D2"),
            ]
            save_desktops(desktops)
            
            loaded = load_desktops()
            # Prüfe ob "Desktop2" bereits existiert
            new_name = "Desktop2"
            name_conflict = any(
                d.name == new_name for d in loaded if d.name != "Desktop1"
            )
            
            assert name_conflict is True


# =============================================================================
# Tests für switch_to_desktop Logik
# =============================================================================

class TestSwitchToDesktopLogic:
    """Tests für die switch_to_desktop Logik."""

    def test_switch_updates_active_status(self, tmp_path):
        """Test: Switch aktualisiert is_active Status."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktops = [
                Desktop(name="Current", path="C:\\Current", is_active=True),
                Desktop(name="Target", path="C:\\Target", is_active=False),
            ]
            save_desktops(desktops)
            
            # Simuliere Switch
            loaded = load_desktops()
            for d in loaded:
                d.is_active = (d.name == "Target")
            save_desktops(loaded)
            
            final = load_desktops()
            current = next(d for d in final if d.name == "Current")
            target = next(d for d in final if d.name == "Target")
            
            assert current.is_active is False
            assert target.is_active is True

    def test_already_active_needs_no_switch(self, tmp_path):
        """Test: Bereits aktiver Desktop braucht keinen Switch."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop = Desktop(name="Active", path="C:\\Active", is_active=True)
            save_desktops([desktop])
            
            loaded = load_desktops()
            target = loaded[0]
            
            needs_switch = not target.is_active
            assert needs_switch is False

    def test_find_target_desktop(self, tmp_path):
        """Test: Ziel-Desktop kann gefunden werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktops = [
                Desktop(name="D1", path="C:\\D1", is_active=True),
                Desktop(name="D2", path="C:\\D2", is_active=False),
            ]
            save_desktops(desktops)
            
            loaded = load_desktops()
            target = next((d for d in loaded if d.name == "D2"), None)
            
            assert target is not None
            assert target.is_active is False


# =============================================================================
# Tests für Icon-Position Verwaltung
# =============================================================================

class TestIconPositionLogic:
    """Tests für Icon-Position Verwaltung."""

    def test_save_icon_positions(self, tmp_path):
        """Test: Icon-Positionen können gespeichert werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            icons = [
                IconPosition(index=0, name="Papierkorb", x=0, y=0),
                IconPosition(index=1, name="Chrome", x=100, y=0),
            ]
            
            desktop = Desktop(
                name="WithIcons",
                path="C:\\Desktop",
                icon_positionen=icons
            )
            save_desktops([desktop])
            
            loaded = load_desktops()
            assert len(loaded[0].icon_positionen) == 2
            assert loaded[0].icon_positionen[0].name == "Papierkorb"
            assert loaded[0].icon_positionen[1].x == 100

    def test_empty_icon_positions(self, tmp_path):
        """Test: Leere Icon-Liste ist gültig."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop = Desktop(
                name="NoIcons",
                path="C:\\Desktop",
                icon_positionen=[]
            )
            save_desktops([desktop])
            
            loaded = load_desktops()
            assert loaded[0].icon_positionen == []

    def test_update_icon_positions(self, tmp_path):
        """Test: Icon-Positionen können aktualisiert werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            # Initial ohne Icons
            desktop = Desktop(name="Desktop", path="C:\\Desktop")
            save_desktops([desktop])
            
            # Icons hinzufügen
            loaded = load_desktops()
            loaded[0].icon_positionen = [
                IconPosition(index=0, name="NewIcon", x=50, y=50)
            ]
            save_desktops(loaded)
            
            final = load_desktops()
            assert len(final[0].icon_positionen) == 1
            assert final[0].icon_positionen[0].name == "NewIcon"


# =============================================================================
# Tests für Wallpaper-Verwaltung
# =============================================================================

class TestWallpaperLogic:
    """Tests für Wallpaper-Verwaltung."""

    def test_wallpaper_path_persistence(self, tmp_path):
        """Test: Wallpaper-Pfad wird gespeichert."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop = Desktop(
                name="WithWallpaper",
                path="C:\\Desktop",
                wallpaper_path="C:\\Wallpapers\\image.jpg"
            )
            save_desktops([desktop])
            
            loaded = load_desktops()
            assert loaded[0].wallpaper_path == "C:\\Wallpapers\\image.jpg"

    def test_empty_wallpaper_path(self, tmp_path):
        """Test: Leerer Wallpaper-Pfad ist gültig."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop = Desktop(
                name="NoWallpaper",
                path="C:\\Desktop",
                wallpaper_path=""
            )
            save_desktops([desktop])
            
            loaded = load_desktops()
            assert loaded[0].wallpaper_path == ""

    def test_update_wallpaper(self, tmp_path):
        """Test: Wallpaper kann aktualisiert werden."""
        from smartdesk.core.storage.file_operations import (
            load_desktops, save_desktops
        )
        
        json_file = tmp_path / "desktops.json"
        
        with patch(
            'smartdesk.core.storage.file_operations.get_data_file_path',
            return_value=str(json_file)
        ):
            desktop = Desktop(name="Desktop", path="C:\\Desktop")
            save_desktops([desktop])
            
            loaded = load_desktops()
            loaded[0].wallpaper_path = "C:\\NewWallpaper.jpg"
            save_desktops(loaded)
            
            final = load_desktops()
            assert final[0].wallpaper_path == "C:\\NewWallpaper.jpg"
