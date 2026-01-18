"""
Tests für die switch_to_desktop Funktion in smartdesk.core.services.desktop_service.
Testet den kompletten Ablauf inkl. Animation, Registry, Restart und Sync.
"""

import pytest
from unittest.mock import patch, MagicMock, call, mock_open
import os
import sys

from smartdesk.core.models.desktop import Desktop, IconPosition

# Dummy Desktop Daten
@pytest.fixture
def mock_desktops():
    return [
        Desktop(name="Current", path="C:\\Current", is_active=True),
        Desktop(name="Target", path="C:\\Target", is_active=False),
        Desktop(name="Other", path="C:\\Other", is_active=False),
    ]

@pytest.fixture
def mock_dependencies():
    """Sammelt alle Mocks, die für switch_to_desktop nötig sind."""
    mocks = {}
    
    # Storage & Model
    mocks['get_all'] = patch('smartdesk.core.services.desktop_service.get_all_desktops').start()
    mocks['save'] = patch('smartdesk.core.services.desktop_service.save_desktops').start()
    mocks['get_icons'] = patch('smartdesk.core.services.desktop_service.get_current_icon_positions').start()
    
    # System / OS
    mocks['reg_update'] = patch('smartdesk.core.services.desktop_service.update_registry_key').start()
    mocks['restart_explorer'] = patch('smartdesk.core.services.desktop_service.restart_explorer').start()
    mocks['sync'] = patch('smartdesk.core.services.desktop_service.sync_desktop_state_and_apply_icons').start()
    mocks['popen'] = patch('smartdesk.core.services.desktop_service.subprocess.Popen').start()
    mocks['tempdir'] = patch('smartdesk.core.services.desktop_service.tempfile.gettempdir').start()
    mocks['path_exists'] = patch('smartdesk.core.services.desktop_service.os.path.exists').start()
    mocks['remove'] = patch('smartdesk.core.services.desktop_service.os.remove').start()
    mocks['backup'] = patch('smartdesk.core.utils.backup_service.create_backup_before_switch').start()
    
    # Defaults
    mocks['get_icons'].return_value = []
    mocks['reg_update'].return_value = True
    mocks['tempdir'].return_value = "C:\\Temp"
    mocks['path_exists'].return_value = True # Standardmäßig existiert alles (Skript, Zielpfad)
    
    yield mocks
    
    patch.stopall()

class TestSwitchToDesktop:
    
    def test_switch_success_flow(self, mock_desktops, mock_dependencies):
        """
        Prüft den Happy Path: 
        1. Lockfile erstellt
        2. Animation gestartet
        3. Registry Update
        4. Explorer Restart
        5. Sync
        6. Lockfile gelöscht
        """
        from smartdesk.core.services.desktop_service import switch_to_desktop
        
        mock_dependencies['get_all'].return_value = mock_desktops
        
        # Mock file open für Lock-File
        m_open = mock_open()
        with patch('builtins.open', m_open):
            result = switch_to_desktop("Target")
        
        assert result is True
        
        # 1. Lock-File erstellt?
        expected_lock_file = os.path.join("C:\\Temp", "smartdesk_switch.lock")
        m_open.assert_called_with(expected_lock_file, 'w')
        
        # 2. Animation gestartet mit Lock-File Argument?
        assert mock_dependencies['popen'].called
        args, _ = mock_dependencies['popen'].call_args
        cmd_args = args[0]
        assert "screen_fade.py" in cmd_args[1]
        assert cmd_args[2] == expected_lock_file
        
        # 3. Registry Updates? (Shell und Legacy Shell)
        assert mock_dependencies['reg_update'].call_count == 2
        
        # 4. Explorer Restart?
        mock_dependencies['restart_explorer'].assert_called_once()
        
        # 5. Sync?
        mock_dependencies['sync'].assert_called_once()
        
        # 6. Lock-File gelöscht?
        mock_dependencies['remove'].assert_called_with(expected_lock_file)
        
        # 7. Daten gespeichert (Icons gesichert)?
        mock_dependencies['save'].assert_called()

    def test_switch_target_not_found(self, mock_desktops, mock_dependencies):
        """Wenn Ziel-Desktop nicht existiert, Abbruch."""
        from smartdesk.core.services.desktop_service import switch_to_desktop
        mock_dependencies['get_all'].return_value = mock_desktops
        
        result = switch_to_desktop("NonExistent")
        
        assert result is False
        mock_dependencies['reg_update'].assert_not_called()
        mock_dependencies['restart_explorer'].assert_not_called()

    def test_switch_already_active(self, mock_desktops, mock_dependencies):
        """Wenn Ziel-Desktop schon aktiv ist, Abbruch."""
        from smartdesk.core.services.desktop_service import switch_to_desktop
        mock_dependencies['get_all'].return_value = mock_desktops
        
        result = switch_to_desktop("Current") # Current ist active=True
        
        assert result is False
        mock_dependencies['reg_update'].assert_not_called()

    def test_registry_update_fails(self, mock_desktops, mock_dependencies):
        """Wenn Registry-Update fehlschlägt -> Rollback und Abbruch."""
        from smartdesk.core.services.desktop_service import switch_to_desktop
        mock_dependencies['get_all'].return_value = mock_desktops
        
        # Simuliere Fehler beim Registry Update
        mock_dependencies['reg_update'].return_value = False
        
        # Mock file open für Lock-File
        with patch('builtins.open', mock_open()):
            result = switch_to_desktop("Target")
        
        assert result is False
        
        # Kein Explorer Restart!
        mock_dependencies['restart_explorer'].assert_not_called()
        
        # Lockfile sollte trotzdem aufgeräumt werden
        expected_lock_file = os.path.join("C:\\Temp", "smartdesk_switch.lock")
        mock_dependencies['remove'].assert_called_with(expected_lock_file)
        
        # Rollback: Active Desktop wiederherstellen
        # save_desktops sollte aufgerufen werden, um is_active=True für 'Current' zu sichern
        # (Nachdem es vorher auf False gesetzt wurde)
        assert mock_dependencies['save'].call_count >= 2 

    def test_animation_script_missing(self, mock_desktops, mock_dependencies):
        """Wenn Animations-Skript fehlt, trotzdem weitermachen."""
        from smartdesk.core.services.desktop_service import switch_to_desktop
        mock_dependencies['get_all'].return_value = mock_desktops
        
        # Simuliere: Skript existiert nicht, aber Zielpfad schon
        def side_effect(path):
            if "screen_fade.py" in path:
                return False
            return True
        mock_dependencies['path_exists'].side_effect = side_effect
        
        with patch('builtins.open', mock_open()):
            result = switch_to_desktop("Target")
        
        assert result is True
        
        # Popen nicht aufgerufen
        mock_dependencies['popen'].assert_not_called()
        
        # Aber der Rest muss laufen
        mock_dependencies['restart_explorer'].assert_called_once()

    def test_target_path_not_found_dialog(self, mock_desktops, mock_dependencies):
        """Wenn Ziel-Ordner fehlt, Dialog anzeigen (hier: Abbruch simulieren)."""
        from smartdesk.core.services.desktop_service import switch_to_desktop
        mock_dependencies['get_all'].return_value = mock_desktops
        
        # Simuliere: Zielpfad existiert nicht
        mock_dependencies['path_exists'].return_value = False
        
        with patch('smartdesk.core.services.desktop_service.show_choice_dialog') as mock_dialog:
            # Simuliere User wählt "Abbrechen" (oder nichts)
            mock_dialog.return_value = None 
            
            result = switch_to_desktop("Target")
            
            assert result is False
            mock_dialog.assert_called_once()
            mock_dependencies['restart_explorer'].assert_not_called()

    def test_target_path_recreate(self, mock_desktops, mock_dependencies):
        """Wenn Ziel-Ordner fehlt und User 'Neu erstellen' wählt."""
        from smartdesk.core.services.desktop_service import switch_to_desktop
        from smartdesk.shared.localization import get_text
        
        mock_dependencies['get_all'].return_value = mock_desktops
        
        # Pfad existiert nicht
        mock_dependencies['path_exists'].return_value = False 
        
        with patch('smartdesk.core.services.desktop_service.show_choice_dialog') as mock_dialog, \
             patch('smartdesk.core.services.desktop_service.ensure_directory_exists') as mock_ensure, \
             patch('builtins.open', mock_open()):
            
            # User wählt "Neu erstellen"
            # Achtung: get_text liefert den Key zurück, wenn keine Übersetzung geladen ist (Mock-Umgebung?)
            # Da wir aber localization importieren, liefert es echte Werte oder Keys.
            # Wir müssen wissen, was show_choice_dialog zurückgibt.
            # Es gibt den Text des Buttons zurück.
            
            # Wir mocken get_text, damit wir stabile Strings haben
            with patch('smartdesk.core.services.desktop_service.get_text') as mock_get_text:
                mock_get_text.side_effect = lambda k, **kw: k # Key als Text
                
                mock_dialog.return_value = "desktop_handler.prompts.path_recreate"
                mock_ensure.return_value = True
                
                result = switch_to_desktop("Target")
                
                assert result is True
                mock_ensure.assert_called()
                mock_dependencies['restart_explorer'].assert_called()

