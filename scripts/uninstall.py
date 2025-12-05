#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SmartDesk Deinstallations-Skript

Dieses Skript führt eine saubere Deinstallation durch:
1. Wechselt zum Original Desktop (stellt Ausgangszustand wieder her)
2. Stoppt alle laufenden Dienste (Listener, Tray)
3. Löscht optional den SmartDesk-Ordner in AppData

Verwendung:
    python scripts/uninstall.py
    python scripts/uninstall.py --keep-data    # Behält AppData-Ordner
    python scripts/uninstall.py --force        # Keine Bestätigungen
"""

import os
import sys
import shutil
import time

# Projekt-Root zum Path hinzufügen
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))


def print_header():
    """Zeigt den Header an."""
    print()
    print("=" * 60)
    print("  🗑️  SmartDesk - Deinstallation")
    print("=" * 60)
    print()


def print_step(step: int, total: int, message: str):
    """Zeigt einen Schritt an."""
    print(f"[{step}/{total}] {message}")


def print_success(message: str):
    """Zeigt eine Erfolgsmeldung an."""
    print(f"  ✅ {message}")


def print_warning(message: str):
    """Zeigt eine Warnung an."""
    print(f"  ⚠️  {message}")


def print_error(message: str):
    """Zeigt einen Fehler an."""
    print(f"  ❌ {message}")


def print_info(message: str):
    """Zeigt eine Info an."""
    print(f"  ℹ️  {message}")


def confirm(message: str, default: bool = False) -> bool:
    """Fragt den Benutzer um Bestätigung."""
    suffix = " [J/n]: " if default else " [j/N]: "
    try:
        response = input(message + suffix).strip().lower()
        if not response:
            return default
        return response in ('j', 'ja', 'y', 'yes')
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def switch_to_original_desktop() -> bool:
    """Wechselt zum Original Desktop."""
    try:
        from smartdesk.core.services.desktop_service import (
            get_all_desktops, 
            switch_to_desktop,
            sync_desktop_state_and_apply_icons
        )
        from smartdesk.core.services.system_service import restart_explorer
        from smartdesk.core.storage.file_operations import load_desktops, save_desktops
        
        desktops = get_all_desktops()
        
        # Finde den geschützten Original Desktop
        original = next((d for d in desktops if d.protected), None)
        
        if not original:
            print_warning("Kein Original Desktop gefunden.")
            print_info("Registry-Einstellungen werden nicht zurückgesetzt.")
            return True  # Kein Fehler, aber auch kein Original
        
        if original.is_active:
            print_success(f"Original Desktop '{original.name}' ist bereits aktiv.")
            return True
        
        print_info(f"Wechsle zu '{original.name}'...")
        
        # Desktop wechseln (Registry-Update)
        needs_restart = switch_to_desktop(original.name)
        
        if needs_restart:
            # Neuen Desktop als aktiv markieren
            all_desktops = load_desktops()
            for d in all_desktops:
                if d.name == original.name:
                    d.is_active = True
                else:
                    d.is_active = False
            save_desktops(all_desktops)
            
            print_info("Starte Explorer neu...")
            restart_explorer()
            time.sleep(2)  # Kurz warten bis Explorer bereit ist
            
            # Wallpaper und Icons anwenden
            print_info("Wende Wallpaper und Icons an...")
            sync_desktop_state_and_apply_icons()
        
        print_success("Original Desktop aktiviert - System ist im Ausgangszustand.")
        return True
        
    except ImportError as e:
        print_error(f"SmartDesk-Module nicht gefunden: {e}")
        print_info("Bitte führen Sie das Skript vom Projektverzeichnis aus.")
        return False
    except Exception as e:
        print_error(f"Fehler beim Desktop-Wechsel: {e}")
        return False


def stop_services() -> bool:
    """Stoppt alle laufenden SmartDesk-Dienste."""
    success = True
    
    # Listener stoppen
    try:
        from smartdesk.hotkeys.hotkey_manager import stop_listener
        
        print_info("Stoppe Hotkey-Listener...")
        if stop_listener():
            print_success("Hotkey-Listener gestoppt.")
        else:
            print_warning("Listener war nicht aktiv oder konnte nicht gestoppt werden.")
    except ImportError as e:
        print_warning(f"Listener-Modul nicht gefunden: {e}")
    except Exception as e:
        print_warning(f"Fehler beim Stoppen des Listeners: {e}")
    
    # Tray stoppen
    try:
        from smartdesk.interfaces.tray.tray_manager import stop_tray
        
        print_info("Stoppe Tray-Icon...")
        if stop_tray():
            print_success("Tray-Icon gestoppt.")
        else:
            print_warning("Tray war nicht aktiv oder konnte nicht gestoppt werden.")
    except ImportError as e:
        print_warning(f"Tray-Modul nicht gefunden: {e}")
    except Exception as e:
        print_warning(f"Fehler beim Stoppen des Trays: {e}")
    
    # Control Panel PID-Datei prüfen und beenden
    try:
        appdata = os.environ.get('APPDATA', '')
        control_panel_pid_file = os.path.join(appdata, 'SmartDesk', 'control_panel.pid')
        
        if os.path.exists(control_panel_pid_file):
            import psutil
            
            try:
                with open(control_panel_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    print_info(f"Stoppe Control Panel (PID {pid})...")
                    proc = psutil.Process(pid)
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    print_success("Control Panel gestoppt.")
                
                # PID-Datei löschen
                os.remove(control_panel_pid_file)
            except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
                # PID-Datei ist ungültig oder Prozess existiert nicht
                try:
                    os.remove(control_panel_pid_file)
                except OSError:
                    pass
    except Exception as e:
        print_warning(f"Control Panel konnte nicht gestoppt werden: {e}")
    
    # Zusätzlich: Alle Python-Prozesse mit SmartDesk beenden (Fallback)
    try:
        import psutil
        
        current_pid = os.getpid()
        killed_count = 0
        
        # Keywords, die SmartDesk-Prozesse identifizieren
        smartdesk_keywords = [
            'tray', 'listener', 'actions', 'control_panel', 'gui_main',
            'main.py', 'tray_icon.py', 'screen_fade.py'
        ]
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['pid'] == current_pid:
                    continue
                    
                cmdline = proc.info.get('cmdline') or []
                cmdline_str = ' '.join(cmdline).lower()
                
                # Suche nach SmartDesk-Prozessen
                if 'smartdesk' in cmdline_str and any(x in cmdline_str for x in smartdesk_keywords):
                    print_info(f"Beende Prozess {proc.info['pid']}: {proc.info['name']}")
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    killed_count += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_count > 0:
            print_success(f"{killed_count} zusätzliche SmartDesk-Prozesse beendet.")
            
    except ImportError:
        print_warning("psutil nicht verfügbar - manuelle Prozessbereinigung nicht möglich.")
    except Exception as e:
        print_warning(f"Fehler bei Prozessbereinigung: {e}")
    
    # Kurz warten, damit Datei-Handles freigegeben werden
    time.sleep(1)
    
    # Logging-Handler schließen (falls durch Imports initialisiert)
    try:
        import logging
        
        # Alle Handler von allen Loggern schließen
        for name in list(logging.Logger.manager.loggerDict.keys()) + ['']:
            logger_instance = logging.getLogger(name)
            for handler in logger_instance.handlers[:]:
                try:
                    handler.close()
                    logger_instance.removeHandler(handler)
                except Exception:
                    pass
        
        # Root-Logger auch
        root = logging.getLogger()
        for handler in root.handlers[:]:
            try:
                handler.close()
                root.removeHandler(handler)
            except Exception:
                pass
                
        # Kurz warten
        time.sleep(0.5)
    except Exception:
        pass
    
    return success


def delete_appdata_folder() -> bool:
    """Löscht den SmartDesk-Ordner in AppData."""
    appdata_path = os.path.join(os.environ.get('APPDATA', ''), 'SmartDesk')
    
    if not os.path.exists(appdata_path):
        print_info("SmartDesk-Ordner existiert nicht.")
        return True
    
    # Mehrere Versuche, falls Dateien noch gesperrt sind
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Zeige was gelöscht wird (nur beim ersten Versuch)
            if attempt == 0:
                print_info(f"Ordner: {appdata_path}")
                
                # Größe berechnen
                total_size = 0
                file_count = 0
                for root, dirs, files in os.walk(appdata_path):
                    for f in files:
                        try:
                            total_size += os.path.getsize(os.path.join(root, f))
                            file_count += 1
                        except OSError:
                            file_count += 1
                
                size_mb = total_size / (1024 * 1024)
                print_info(f"Enthält {file_count} Dateien ({size_mb:.2f} MB)")
            
            # Löschen
            shutil.rmtree(appdata_path)
            print_success("SmartDesk-Ordner gelöscht.")
            return True
            
        except PermissionError:
            if attempt < max_retries - 1:
                print_info(f"Dateien noch gesperrt, warte... (Versuch {attempt + 2}/{max_retries})")
                time.sleep(2)
            else:
                print_error("Zugriff verweigert - sind noch Dienste aktiv?")
                print_info("Tipp: Schließen Sie alle SmartDesk-Fenster und versuchen Sie es erneut.")
                return False
        except Exception as e:
            print_error(f"Fehler beim Löschen: {e}")
            return False
    
    return False


def main():
    """Hauptfunktion."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SmartDesk Deinstallation')
    parser.add_argument('--keep-data', action='store_true', 
                        help='Behält den AppData-Ordner')
    parser.add_argument('--force', '-f', action='store_true',
                        help='Keine Bestätigungen erfragen')
    args = parser.parse_args()
    
    print_header()
    
    # Warnung anzeigen
    print("Dieses Skript wird:")
    print("  1. Zum Original Desktop wechseln (Ausgangszustand)")
    print("  2. Alle SmartDesk-Dienste stoppen")
    if not args.keep_data:
        print("  3. Den SmartDesk-Ordner in AppData löschen")
    print()
    
    if not args.force:
        if not confirm("Möchten Sie fortfahren?", default=False):
            print("\nDeinstallation abgebrochen.")
            return 0
    
    print()
    total_steps = 3 if not args.keep_data else 2
    current_step = 0
    errors = 0
    
    # Schritt 1: Zum Original Desktop wechseln
    current_step += 1
    print_step(current_step, total_steps, "Original Desktop aktivieren...")
    if not switch_to_original_desktop():
        errors += 1
        if not args.force:
            if not confirm("Trotz Fehler fortfahren?", default=False):
                print("\nDeinstallation abgebrochen.")
                return 1
    print()
    
    # Schritt 2: Dienste stoppen
    current_step += 1
    print_step(current_step, total_steps, "Dienste stoppen...")
    stop_services()
    print()
    
    # Schritt 3: AppData löschen (optional)
    if not args.keep_data:
        current_step += 1
        print_step(current_step, total_steps, "SmartDesk-Ordner löschen...")
        
        if not args.force:
            if not confirm("AppData-Ordner wirklich löschen?", default=True):
                print_info("Ordner wird beibehalten.")
            else:
                if not delete_appdata_folder():
                    errors += 1
        else:
            if not delete_appdata_folder():
                errors += 1
        print()
    
    # Zusammenfassung
    print("=" * 60)
    if errors == 0:
        print("  ✅ Deinstallation erfolgreich abgeschlossen!")
        print()
        print("  Ihr System ist wieder im Ausgangszustand.")
        print("  Sie können nun den Projektordner löschen.")
    else:
        print(f"  ⚠️  Deinstallation mit {errors} Warnung(en) abgeschlossen.")
        print()
        print("  Bitte prüfen Sie die obigen Meldungen.")
    print("=" * 60)
    print()
    
    return 0 if errors == 0 else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAbgebrochen.")
        sys.exit(1)
