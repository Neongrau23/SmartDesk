# Dateipfad: tests/test_models.py
"""
Unit-Tests für smartdesk.models.desktop

Testet die Serialisierung und Deserialisierung von:
- IconPosition
- Desktop
"""

from smartdesk.core.models.desktop import Desktop, IconPosition


class TestIconPosition:
    """Tests für die IconPosition Dataclass."""

    def test_create_icon_position(self):
        """Test: IconPosition kann erstellt werden."""
        icon = IconPosition(index=0, name="Papierkorb", x=100, y=200)
        
        assert icon.index == 0
        assert icon.name == "Papierkorb"
        assert icon.x == 100
        assert icon.y == 200

    def test_icon_to_dict(self, sample_icon):
        """Test: IconPosition kann zu Dict konvertiert werden."""
        result = sample_icon.to_dict()
        
        assert isinstance(result, dict)
        assert result["index"] == sample_icon.index
        assert result["name"] == sample_icon.name
        assert result["x"] == sample_icon.x
        assert result["y"] == sample_icon.y

    def test_icon_from_dict(self, sample_icon_data):
        """Test: IconPosition kann aus Dict erstellt werden."""
        icon = IconPosition.from_dict(sample_icon_data)
        
        assert icon.index == sample_icon_data["index"]
        assert icon.name == sample_icon_data["name"]
        assert icon.x == sample_icon_data["x"]
        assert icon.y == sample_icon_data["y"]

    def test_icon_roundtrip(self, sample_icon):
        """Test: to_dict -> from_dict ergibt gleiches Objekt."""
        data = sample_icon.to_dict()
        restored = IconPosition.from_dict(data)
        
        assert restored.index == sample_icon.index
        assert restored.name == sample_icon.name
        assert restored.x == sample_icon.x
        assert restored.y == sample_icon.y

    def test_icon_from_dict_missing_index(self):
        """Test: Fehlender Index wird auf 0 gesetzt."""
        data = {"name": "Test", "x": 50, "y": 50}
        icon = IconPosition.from_dict(data)
        
        assert icon.index == 0
        assert icon.name == "Test"

    def test_icon_negative_coordinates(self):
        """Test: Negative Koordinaten sind erlaubt."""
        icon = IconPosition(index=0, name="Test", x=-100, y=-50)
        
        assert icon.x == -100
        assert icon.y == -50


class TestDesktop:
    """Tests für die Desktop Dataclass."""

    def test_create_desktop_minimal(self):
        """Test: Desktop mit minimalen Parametern erstellen."""
        desktop = Desktop(name="Test", path="C:\\Test")
        
        assert desktop.name == "Test"
        assert desktop.path == "C:\\Test"
        assert desktop.is_active is False
        assert desktop.wallpaper_path == ""
        assert desktop.icon_positionen == []

    def test_create_desktop_full(self, sample_icons):
        """Test: Desktop mit allen Parametern erstellen."""
        desktop = Desktop(
            name="Arbeit",
            path="C:\\Desktop_Arbeit",
            is_active=True,
            wallpaper_path="C:\\wallpaper.jpg",
            icon_positionen=sample_icons
        )
        
        assert desktop.name == "Arbeit"
        assert desktop.is_active is True
        assert desktop.wallpaper_path == "C:\\wallpaper.jpg"
        assert len(desktop.icon_positionen) == 3

    def test_desktop_to_dict(self, sample_desktop):
        """Test: Desktop kann zu Dict konvertiert werden."""
        result = sample_desktop.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == sample_desktop.name
        assert result["path"] == sample_desktop.path
        assert result["is_active"] == sample_desktop.is_active
        assert result["wallpaper_path"] == sample_desktop.wallpaper_path
        assert isinstance(result["icon_positionen"], list)

    def test_desktop_from_dict(self, sample_desktop_data):
        """Test: Desktop kann aus Dict erstellt werden."""
        desktop = Desktop.from_dict(sample_desktop_data)
        
        assert desktop.name == sample_desktop_data["name"]
        assert desktop.path == sample_desktop_data["path"]
        assert desktop.is_active == sample_desktop_data["is_active"]
        assert len(desktop.icon_positionen) == 2

    def test_desktop_roundtrip(self, sample_desktop):
        """Test: to_dict -> from_dict ergibt gleiches Objekt."""
        data = sample_desktop.to_dict()
        restored = Desktop.from_dict(data)
        
        assert restored.name == sample_desktop.name
        assert restored.path == sample_desktop.path
        assert restored.is_active == sample_desktop.is_active
        assert restored.wallpaper_path == sample_desktop.wallpaper_path
        assert len(restored.icon_positionen) == len(sample_desktop.icon_positionen)

    def test_desktop_from_dict_defaults(self):
        """Test: Fehlende optionale Felder bekommen Standardwerte."""
        minimal_data = {
            "name": "Minimal",
            "path": "C:\\Minimal"
        }
        desktop = Desktop.from_dict(minimal_data)
        
        assert desktop.name == "Minimal"
        assert desktop.path == "C:\\Minimal"
        assert desktop.is_active is False
        assert desktop.wallpaper_path == ""
        assert desktop.icon_positionen == []

    def test_desktop_from_dict_backward_compatible(self):
        """Test: Alte JSON ohne wallpaper_path wird korrekt geladen."""
        old_format_data = {
            "name": "Alt",
            "path": "C:\\Alt",
            "is_active": True,
            "icon_positionen": []
            # wallpaper_path fehlt (alte Version)
        }
        desktop = Desktop.from_dict(old_format_data)
        
        assert desktop.wallpaper_path == ""

    def test_desktop_empty_icons(self):
        """Test: Desktop mit leerer Icon-Liste."""
        data = {
            "name": "Leer",
            "path": "C:\\Leer",
            "is_active": False,
            "wallpaper_path": "",
            "icon_positionen": []
        }
        desktop = Desktop.from_dict(data)
        
        assert desktop.icon_positionen == []

    def test_desktop_icons_are_icon_position_objects(self, sample_desktop):
        """Test: Icons sind tatsächlich IconPosition-Objekte."""
        for icon in sample_desktop.icon_positionen:
            assert isinstance(icon, IconPosition)

    def test_desktop_special_characters_in_name(self):
        """Test: Sonderzeichen im Namen."""
        desktop = Desktop(
            name="Arbeit & Privat (2024)",
            path="C:\\Desktop_Special"
        )
        
        assert desktop.name == "Arbeit & Privat (2024)"
        
        # Roundtrip Test
        data = desktop.to_dict()
        restored = Desktop.from_dict(data)
        assert restored.name == "Arbeit & Privat (2024)"

    def test_desktop_unicode_in_path(self):
        """Test: Unicode-Zeichen im Pfad."""
        desktop = Desktop(
            name="Büro",
            path="C:\\Users\\Müller\\Desktop_Büro"
        )
        
        assert "Müller" in desktop.path
        assert "Büro" in desktop.path

    def test_multiple_desktops_serialization(self, sample_desktops):
        """Test: Mehrere Desktops serialisieren und deserialisieren."""
        # Alle zu Dict konvertieren
        data_list = [d.to_dict() for d in sample_desktops]
        
        assert len(data_list) == 3
        
        # Alle zurück konvertieren
        restored = [Desktop.from_dict(d) for d in data_list]
        
        assert len(restored) == 3
        assert restored[0].name == "Standard"
        assert restored[1].name == "Arbeit"
        assert restored[2].name == "Gaming"

    def test_only_one_desktop_active(self, sample_desktops):
        """Test: Nur ein Desktop sollte aktiv sein."""
        active_count = sum(1 for d in sample_desktops if d.is_active)
        assert active_count == 1
