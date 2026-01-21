# Dateipfad: tests/test_file_operations.py
"""
Unit-Tests für smartdesk.storage.file_operations

Testet:
- load_desktops(): Laden von JSON-Daten
- save_desktops(): Speichern von Desktop-Listen
- get_data_file_path(): Pfad-Ermittlung
"""

import json
from unittest.mock import patch

from smartdesk.core.storage.file_operations import load_desktops, save_desktops, get_data_file_path
from smartdesk.core.models.desktop import Desktop


class TestGetDataFilePath:
    """Tests für get_data_file_path()."""

    def test_returns_string(self):
        """Test: Funktion gibt einen String zurück."""
        result = get_data_file_path()
        assert isinstance(result, str)

    def test_ends_with_json(self):
        """Test: Pfad endet mit desktops.json."""
        result = get_data_file_path()
        assert result.endswith("desktops.json")


class TestLoadDesktops:
    """Tests für load_desktops()."""

    def test_load_empty_file_returns_empty_list(self, tmp_path):
        """Test: Leere/nicht existierende Datei gibt leere Liste."""
        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(tmp_path / "not_exists.json")):
            result = load_desktops()
            assert result == []

    def test_load_valid_json(self, tmp_path, sample_desktops_data):
        """Test: Valide JSON-Datei wird korrekt geladen."""
        json_file = tmp_path / "desktops.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(sample_desktops_data, f)

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            result = load_desktops()

            assert len(result) == 3
            assert all(isinstance(d, Desktop) for d in result)
            assert result[0].name == "Standard"
            assert result[1].name == "Arbeit"
            assert result[2].name == "Gaming"

    def test_load_corrupted_json_returns_empty_list(self, tmp_path):
        """Test: Korrupte JSON gibt leere Liste zurück."""
        json_file = tmp_path / "corrupted.json"
        with open(json_file, "w", encoding="utf-8") as f:
            f.write("{invalid json content")

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            result = load_desktops()
            assert result == []

    def test_load_empty_json_array(self, tmp_path):
        """Test: Leeres JSON-Array gibt leere Liste."""
        json_file = tmp_path / "empty.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([], f)

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            result = load_desktops()
            assert result == []

    def test_load_single_desktop(self, tmp_path, sample_desktop_data):
        """Test: Einzelner Desktop wird korrekt geladen."""
        json_file = tmp_path / "single.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([sample_desktop_data], f)

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            result = load_desktops()

            assert len(result) == 1
            assert result[0].name == "Arbeit"

    def test_load_preserves_icon_positions(self, tmp_path):
        """Test: Icon-Positionen werden korrekt geladen."""
        data = [
            {
                "name": "Test",
                "path": "C:\\Test",
                "is_active": False,
                "wallpaper_path": "",
                "icon_positionen": [
                    {"index": 0, "name": "Icon1", "x": 100, "y": 200},
                    {"index": 1, "name": "Icon2", "x": 300, "y": 400},
                ],
            }
        ]

        json_file = tmp_path / "icons.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            result = load_desktops()

            assert len(result[0].icon_positionen) == 2
            assert result[0].icon_positionen[0].x == 100
            assert result[0].icon_positionen[1].name == "Icon2"

    def test_load_unicode_content(self, tmp_path):
        """Test: Unicode-Zeichen werden korrekt geladen."""
        data = [{"name": "Büro", "path": "C:\\Users\\Müller\\Desktop", "is_active": True, "wallpaper_path": "", "icon_positionen": []}]

        json_file = tmp_path / "unicode.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            result = load_desktops()

            assert result[0].name == "Büro"
            assert "Müller" in result[0].path


class TestSaveDesktops:
    """Tests für save_desktops()."""

    def test_save_creates_file(self, tmp_path, sample_desktops):
        """Test: Datei wird erstellt."""
        json_file = tmp_path / "new_desktops.json"

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            result = save_desktops(sample_desktops)

            assert result is True
            assert json_file.exists()

    def test_save_valid_json_content(self, tmp_path, sample_desktops):
        """Test: Gespeicherte Datei enthält valides JSON."""
        json_file = tmp_path / "valid.json"

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            save_desktops(sample_desktops)

            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert len(data) == 3
            assert data[0]["name"] == "Standard"

    def test_save_creates_directory_if_missing(self, tmp_path, sample_desktops):
        """Test: Verzeichnis wird erstellt falls nicht vorhanden."""
        nested_dir = tmp_path / "nested" / "dir"
        json_file = nested_dir / "desktops.json"

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            result = save_desktops(sample_desktops)

            assert result is True
            assert nested_dir.exists()
            assert json_file.exists()

    def test_save_empty_list(self, tmp_path):
        """Test: Leere Liste speichern."""
        json_file = tmp_path / "empty.json"

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            result = save_desktops([])

            assert result is True
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data == []

    def test_save_preserves_unicode(self, tmp_path):
        """Test: Unicode wird korrekt gespeichert."""
        desktop = Desktop(name="Büro", path="C:\\Users\\Müller\\Desktop")
        json_file = tmp_path / "unicode.json"

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            save_desktops([desktop])

            with open(json_file, "r", encoding="utf-8") as f:
                content = f.read()

            assert "Büro" in content
            assert "Müller" in content

    def test_save_overwrites_existing(self, tmp_path, sample_desktops):
        """Test: Existierende Datei wird überschrieben."""
        json_file = tmp_path / "overwrite.json"

        # Erste Speicherung
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([{"name": "Alt", "path": "C:\\Alt"}], f)

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            save_desktops(sample_desktops)

            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert len(data) == 3
            assert data[0]["name"] == "Standard"

    def test_save_returns_false_on_error(self, tmp_path):
        """Test: Gibt False bei Fehler zurück."""
        # Ungültiger Pfad - Test überprüft Fehlerbehandlung
        invalid_path = "Z:\\NonExistent\\Dir\\file.json"

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=invalid_path):
            # Die Funktion sollte bei ungültigem Pfad False zurückgeben
            # oder eine Exception werfen die gefangen wird
            try:
                result = save_desktops([])
                # Wenn keine Exception, sollte False zurückkommen
                assert result is False
            except (OSError, FileNotFoundError):
                # Exception ist auch akzeptables Verhalten
                pass


class TestRoundtrip:
    """Integration Tests: Speichern und Laden."""

    def test_save_then_load(self, tmp_path, sample_desktops):
        """Test: Gespeicherte Daten können wieder geladen werden."""
        json_file = tmp_path / "roundtrip.json"

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            # Speichern
            save_desktops(sample_desktops)

            # Laden
            loaded = load_desktops()

            assert len(loaded) == len(sample_desktops)
            for orig, restored in zip(sample_desktops, loaded):
                assert orig.name == restored.name
                assert orig.path == restored.path
                assert orig.is_active == restored.is_active

    def test_multiple_save_load_cycles(self, tmp_path):
        """Test: Mehrere Speicher-Lade-Zyklen."""
        json_file = tmp_path / "cycles.json"

        with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(json_file)):
            # Zyklus 1
            desktops1 = [Desktop(name="V1", path="C:\\V1")]
            save_desktops(desktops1)
            loaded1 = load_desktops()
            assert loaded1[0].name == "V1"

            # Zyklus 2 - Änderungen
            loaded1[0].name = "V2"
            loaded1.append(Desktop(name="Neu", path="C:\\Neu"))
            save_desktops(loaded1)
            loaded2 = load_desktops()

            assert len(loaded2) == 2
            assert loaded2[0].name == "V2"
            assert loaded2[1].name == "Neu"
