# Dateipfad: tests/test_registry_operations.py
"""
Unit-Tests für smartdesk.utils.registry_operations

Testet mit MagicMock:
- update_registry_key(): Registry-Werte setzen
- get_registry_value(): Registry-Werte lesen
- save_tray_pid() / get_tray_pid(): PID-Management
- is_process_running(): Prozess-Status prüfen
- cleanup_tray_pid(): PID aufräumen
"""

import psutil
from unittest.mock import patch, MagicMock


class TestUpdateRegistryKey:
    """Tests für update_registry_key()."""

    def test_successful_update(self):
        """Test: Erfolgreicher Registry-Update gibt True zurück."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            # Setup
            mock_winreg.HKEY_CURRENT_USER = 0x80000001
            mock_winreg.KEY_SET_VALUE = 0x0002
            mock_winreg.REG_SZ = 1

            mock_key = MagicMock()
            mock_winreg.OpenKey.return_value.__enter__ = MagicMock(
                return_value=mock_key
            )
            mock_winreg.OpenKey.return_value.__exit__ = MagicMock(
                return_value=False
            )

            from smartdesk.core.utils.registry_operations import update_registry_key

            result = update_registry_key(
                "Software\\Test",
                "TestValue",
                "TestData"
            )

            assert result is True
            mock_winreg.SetValueEx.assert_called_once()

    def test_update_with_reg_expand_sz(self):
        """Test: Update mit REG_EXPAND_SZ Typ."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            mock_winreg.HKEY_CURRENT_USER = 0x80000001
            mock_winreg.KEY_SET_VALUE = 0x0002
            mock_winreg.REG_EXPAND_SZ = 2

            mock_key = MagicMock()
            mock_winreg.OpenKey.return_value.__enter__ = MagicMock(
                return_value=mock_key
            )
            mock_winreg.OpenKey.return_value.__exit__ = MagicMock(
                return_value=False
            )

            from smartdesk.core.utils.registry_operations import update_registry_key

            result = update_registry_key(
                "Software\\Test",
                "Path",
                "%USERPROFILE%\\Desktop",
                mock_winreg.REG_EXPAND_SZ
            )

            assert result is True

    def test_update_returns_false_on_error(self):
        """Test: Gibt False bei WindowsError zurück."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            mock_winreg.HKEY_CURRENT_USER = 0x80000001
            mock_winreg.KEY_SET_VALUE = 0x0002

            # Simuliere Fehler
            mock_winreg.OpenKey.side_effect = WindowsError(5, "Access denied")

            # Mock get_text um Fehlerausgabe zu verhindern
            with patch(
                'smartdesk.core.utils.registry_operations.get_text',
                return_value="Error"
            ):
                from smartdesk.core.utils.registry_operations import (
                    update_registry_key
                )

                result = update_registry_key(
                    "Software\\Protected",
                    "Value",
                    "Data"
                )

                assert result is False


class TestGetRegistryValue:
    """Tests für get_registry_value()."""

    def test_get_existing_value(self):
        """Test: Existierenden Wert lesen."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            mock_winreg.HKEY_CURRENT_USER = 0x80000001
            mock_winreg.KEY_READ = 0x20019

            mock_key = MagicMock()
            mock_winreg.OpenKey.return_value.__enter__ = MagicMock(
                return_value=mock_key
            )
            mock_winreg.OpenKey.return_value.__exit__ = MagicMock(
                return_value=False
            )
            mock_winreg.QueryValueEx.return_value = (
                "C:\\Users\\Test\\Desktop",
                1
            )

            from smartdesk.core.utils.registry_operations import get_registry_value

            result = get_registry_value("Software\\Test", "Desktop")

            assert result == "C:\\Users\\Test\\Desktop"

    def test_get_missing_value_returns_empty(self):
        """Test: Fehlender Wert gibt leeren String zurück."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            mock_winreg.HKEY_CURRENT_USER = 0x80000001
            mock_winreg.KEY_READ = 0x20019

            # Simuliere FileNotFoundError
            mock_winreg.OpenKey.side_effect = WindowsError(
                2,
                "Key not found"
            )

            from smartdesk.core.utils.registry_operations import get_registry_value

            result = get_registry_value("Software\\NotExists", "Value")

            assert result == ""

    def test_get_value_with_expand_sz(self):
        """Test: REG_EXPAND_SZ Wert lesen."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            mock_winreg.HKEY_CURRENT_USER = 0x80000001
            mock_winreg.KEY_READ = 0x20019
            mock_winreg.REG_EXPAND_SZ = 2

            mock_key = MagicMock()
            mock_winreg.OpenKey.return_value.__enter__ = MagicMock(
                return_value=mock_key
            )
            mock_winreg.OpenKey.return_value.__exit__ = MagicMock(
                return_value=False
            )
            mock_winreg.QueryValueEx.return_value = (
                "%USERPROFILE%\\Desktop",
                mock_winreg.REG_EXPAND_SZ
            )

            from smartdesk.core.utils.registry_operations import get_registry_value

            result = get_registry_value("Software\\Shell", "Desktop")

            assert "%USERPROFILE%" in result


class TestTrayPidManagement:
    """Tests für Tray-PID Funktionen."""

    def test_save_tray_pid(self):
        """Test: PID speichern."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            mock_winreg.HKEY_CURRENT_USER = 0x80000001
            mock_winreg.REG_DWORD = 4

            mock_key = MagicMock()
            mock_winreg.CreateKey.return_value = mock_key

            from smartdesk.core.utils.registry_operations import save_tray_pid

            save_tray_pid(12345)

            mock_winreg.CreateKey.assert_called_once()
            mock_winreg.SetValueEx.assert_called_once_with(
                mock_key,
                "TrayPID",
                0,
                mock_winreg.REG_DWORD,
                12345
            )
            mock_winreg.CloseKey.assert_called_once_with(mock_key)

    def test_get_tray_pid_exists(self):
        """Test: Existierende PID lesen."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            mock_winreg.HKEY_CURRENT_USER = 0x80000001

            mock_key = MagicMock()
            mock_winreg.OpenKey.return_value = mock_key
            mock_winreg.QueryValueEx.return_value = (12345, 4)

            from smartdesk.core.utils.registry_operations import get_tray_pid

            result = get_tray_pid()

            assert result == 12345

    def test_get_tray_pid_not_exists(self):
        """Test: Keine PID vorhanden gibt None zurück."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            mock_winreg.OpenKey.side_effect = FileNotFoundError()

            from smartdesk.core.utils.registry_operations import get_tray_pid

            result = get_tray_pid()

            assert result is None

    def test_cleanup_tray_pid(self):
        """Test: PID löschen."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            mock_winreg.HKEY_CURRENT_USER = 0x80000001
            mock_winreg.KEY_SET_VALUE = 0x0002

            mock_key = MagicMock()
            mock_winreg.OpenKey.return_value = mock_key

            from smartdesk.core.utils.registry_operations import cleanup_tray_pid

            cleanup_tray_pid()

            mock_winreg.DeleteValue.assert_called_once_with(mock_key, "TrayPID")

    def test_cleanup_tray_pid_handles_missing(self):
        """Test: Cleanup ignoriert fehlende PID."""
        with patch(
            'smartdesk.core.utils.registry_operations.winreg'
        ) as mock_winreg:
            mock_winreg.OpenKey.side_effect = FileNotFoundError()

            from smartdesk.core.utils.registry_operations import cleanup_tray_pid

            # Sollte keine Exception werfen
            cleanup_tray_pid()


class TestIsProcessRunning:
    """Tests für is_process_running()."""

    def test_process_exists_and_running_python(self):
        """Test: Laufender Python-Prozess gibt True zurück."""
        with patch(
            'smartdesk.core.utils.registry_operations.psutil'
        ) as mock_psutil:
            mock_psutil.pid_exists.return_value = True
            mock_process = MagicMock()
            mock_process.is_running.return_value = True
            mock_process.name.return_value = "python.exe"
            mock_process.cmdline.return_value = ["python.exe", "tray_icon.py"]
            mock_psutil.Process.return_value = mock_process
            mock_psutil.NoSuchProcess = psutil.NoSuchProcess
            mock_psutil.AccessDenied = psutil.AccessDenied

            from smartdesk.core.utils.registry_operations import is_process_running

            result = is_process_running(12345)

            assert result is True
            mock_psutil.pid_exists.assert_called_once_with(12345)

    def test_process_exists_and_running_pythonw(self):
        """Test: Laufender pythonw-Prozess gibt True zurück."""
        with patch(
            'smartdesk.core.utils.registry_operations.psutil'
        ) as mock_psutil:
            mock_psutil.pid_exists.return_value = True
            mock_process = MagicMock()
            mock_process.is_running.return_value = True
            mock_process.name.return_value = "pythonw.exe"
            mock_process.cmdline.return_value = ["pythonw.exe", "tray_icon.py"]
            mock_psutil.Process.return_value = mock_process
            mock_psutil.NoSuchProcess = psutil.NoSuchProcess
            mock_psutil.AccessDenied = psutil.AccessDenied

            from smartdesk.core.utils.registry_operations import is_process_running

            result = is_process_running(12345)

            assert result is True

    def test_process_exists_but_not_python(self):
        """Test: Laufender nicht-Python-Prozess gibt False zurück."""
        with patch(
            'smartdesk.core.utils.registry_operations.psutil'
        ) as mock_psutil:
            mock_psutil.pid_exists.return_value = True
            mock_process = MagicMock()
            mock_process.is_running.return_value = True
            mock_process.name.return_value = "notepad.exe"
            mock_psutil.Process.return_value = mock_process

            from smartdesk.core.utils.registry_operations import is_process_running

            result = is_process_running(12345)

            assert result is False

    def test_process_not_exists(self):
        """Test: Nicht existierender Prozess gibt False zurück."""
        with patch(
            'smartdesk.core.utils.registry_operations.psutil'
        ) as mock_psutil:
            mock_psutil.pid_exists.return_value = False

            from smartdesk.core.utils.registry_operations import is_process_running

            result = is_process_running(99999)

            assert result is False

    def test_process_exists_but_not_running(self):
        """Test: Beendeter Prozess gibt False zurück."""
        with patch(
            'smartdesk.core.utils.registry_operations.psutil'
        ) as mock_psutil:
            mock_psutil.pid_exists.return_value = True
            mock_process = MagicMock()
            mock_process.is_running.return_value = False
            mock_psutil.Process.return_value = mock_process

            from smartdesk.core.utils.registry_operations import is_process_running

            result = is_process_running(12345)

            assert result is False

    def test_handles_no_such_process(self):
        """Test: NoSuchProcess Exception wird gefangen."""
        with patch(
            'smartdesk.core.utils.registry_operations.psutil'
        ) as mock_psutil:
            import psutil as real_psutil

            mock_psutil.pid_exists.return_value = True
            mock_psutil.NoSuchProcess = real_psutil.NoSuchProcess
            mock_psutil.AccessDenied = real_psutil.AccessDenied
            mock_psutil.Process.side_effect = real_psutil.NoSuchProcess(12345)

            from smartdesk.core.utils.registry_operations import is_process_running

            result = is_process_running(12345)

            assert result is False

    def test_handles_access_denied_returns_true(self):
        """Test: AccessDenied Exception gibt True zurück (konservative Annahme)."""
        with patch(
            'smartdesk.core.utils.registry_operations.psutil'
        ) as mock_psutil:
            import psutil as real_psutil

            mock_psutil.pid_exists.return_value = True
            mock_psutil.NoSuchProcess = real_psutil.NoSuchProcess
            mock_psutil.AccessDenied = real_psutil.AccessDenied
            mock_psutil.Process.side_effect = real_psutil.AccessDenied(12345)

            from smartdesk.core.utils.registry_operations import is_process_running

            result = is_process_running(12345)

            # Bei AccessDenied nehmen wir konservativ an, dass der Prozess läuft
            assert result is True

    def test_cmdline_access_denied_still_returns_true_for_python(self):
        """Test: Python-Prozess mit cmdline-Zugriffsfehler gibt True zurück."""
        with patch(
            'smartdesk.core.utils.registry_operations.psutil'
        ) as mock_psutil:
            import psutil as real_psutil

            mock_psutil.pid_exists.return_value = True
            mock_psutil.NoSuchProcess = real_psutil.NoSuchProcess
            mock_psutil.AccessDenied = real_psutil.AccessDenied
            mock_process = MagicMock()
            mock_process.is_running.return_value = True
            mock_process.name.return_value = "python.exe"
            mock_process.cmdline.side_effect = real_psutil.AccessDenied(12345)
            mock_psutil.Process.return_value = mock_process

            from smartdesk.core.utils.registry_operations import is_process_running

            result = is_process_running(12345)

            # Bei Python-Prozess mit cmdline-Zugriffsfehler: True
            assert result is True
