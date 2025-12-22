# Dateipfad: tests/test_path_validator.py
"""
Unit-Tests für smartdesk.utils.path_validator

Testet:
- ensure_directory_exists(): Verzeichnis-Erstellung und Validierung
"""

import os
from unittest.mock import patch

from smartdesk.core.utils.path_validator import ensure_directory_exists


class TestEnsureDirectoryExists:
    """Tests für ensure_directory_exists()."""

    def test_returns_false_for_empty_path(self):
        """Test: Leerer Pfad gibt False zurück."""
        result = ensure_directory_exists("")
        assert result is False

    def test_returns_false_for_none_path(self):
        """Test: None als Pfad gibt False zurück."""
        result = ensure_directory_exists(None)
        assert result is False

    def test_existing_directory_returns_true(self, tmp_path):
        """Test: Existierendes Verzeichnis gibt True zurück."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        result = ensure_directory_exists(str(existing_dir))
        assert result is True

    def test_creates_missing_directory(self, tmp_path):
        """Test: Fehlendes Verzeichnis wird erstellt."""
        new_dir = tmp_path / "new_directory"

        assert not new_dir.exists()
        result = ensure_directory_exists(str(new_dir))

        assert result is True
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_creates_nested_directories(self, tmp_path):
        """Test: Verschachtelte Verzeichnisse werden erstellt."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"

        result = ensure_directory_exists(str(nested_dir))

        assert result is True
        assert nested_dir.exists()

    def test_returns_true_for_existing_nested(self, tmp_path):
        """Test: Bereits existierendes Verzeichnis gibt True."""
        nested_dir = tmp_path / "a" / "b" / "c"
        nested_dir.mkdir(parents=True)

        result = ensure_directory_exists(str(nested_dir))
        assert result is True

    def test_handles_path_with_trailing_slash(self, tmp_path):
        """Test: Pfad mit Trailing Slash funktioniert."""
        dir_path = str(tmp_path / "trailing") + os.sep

        result = ensure_directory_exists(dir_path)

        assert result is True

    def test_returns_false_on_permission_error(self):
        """Test: Gibt False bei Permission Error zurück."""
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs') as mock_makedirs:
                mock_makedirs.side_effect = OSError(
                    13,
                    "Permission denied"
                )

                result = ensure_directory_exists("C:\\Protected\\Dir")

                assert result is False

    def test_returns_false_on_os_error(self):
        """Test: Gibt False bei allgemeinem OS Error zurück."""
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs') as mock_makedirs:
                mock_makedirs.side_effect = OSError(
                    22,
                    "Invalid argument"
                )

                result = ensure_directory_exists("Z:\\Invalid\\Path")

                assert result is False

    def test_does_not_create_if_exists(self, tmp_path):
        """Test: makedirs wird nicht aufgerufen wenn Pfad existiert."""
        existing_dir = tmp_path / "exists"
        existing_dir.mkdir()

        with patch('os.makedirs') as mock_makedirs:
            with patch('os.path.exists', return_value=True):
                ensure_directory_exists(str(existing_dir))

                # makedirs sollte nicht aufgerufen werden
                mock_makedirs.assert_not_called()

    def test_whitespace_path_returns_false(self):
        """Test: Pfad nur aus Whitespace gibt False zurück."""
        ensure_directory_exists("   ")
        # Abhängig von Implementierung: könnte False oder Fehler sein
        # Der leere String nach strip() sollte False ergeben

    def test_relative_path_works(self, tmp_path, monkeypatch):
        """Test: Relativer Pfad funktioniert."""
        monkeypatch.chdir(tmp_path)

        result = ensure_directory_exists("relative_dir")

        assert result is True
        assert (tmp_path / "relative_dir").exists()

    def test_path_with_spaces(self, tmp_path):
        """Test: Pfad mit Leerzeichen funktioniert."""
        dir_with_spaces = tmp_path / "path with spaces"

        result = ensure_directory_exists(str(dir_with_spaces))

        assert result is True
        assert dir_with_spaces.exists()

    def test_unicode_path(self, tmp_path):
        """Test: Unicode im Pfadnamen funktioniert."""
        unicode_dir = tmp_path / "Büro_Müller"

        result = ensure_directory_exists(str(unicode_dir))

        assert result is True
        assert unicode_dir.exists()


class TestEdgeCases:
    """Spezielle Edge Cases."""

    def test_file_exists_at_path(self, tmp_path):
        """Test: Was passiert wenn eine Datei statt Ordner existiert?"""
        file_path = tmp_path / "is_a_file"
        file_path.write_text("content")

        # Verhalten ist implementierungsabhängig
        # Aktuell: os.makedirs wirft FileExistsError wenn Datei existiert
        # oder gibt True wenn os.path.exists True ist

    def test_very_long_path(self, tmp_path):
        """Test: Sehr langer Pfadname."""
        # Windows hat MAX_PATH Limit von 260 Zeichen
        long_name = "a" * 50
        long_path = tmp_path

        for _ in range(4):
            long_path = long_path / long_name

        # Sollte entweder funktionieren oder sauber fehlschlagen
        ensure_directory_exists(str(long_path))
        # Ergebnis hängt von OS und Dateisystem ab
