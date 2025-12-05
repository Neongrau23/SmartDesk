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
        from smartdesk.core.services.desktop_service import get_all_desktops, switch_to_desktop
        from smartdesk.core.services.system_service import restart_explorer
        
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
        
        # Desktop wechseln
        needs_restart = switch_to_desktop(original.name)
        
        if needs_restart:
            print_info("Starte Explorer neu...")
            restart_explorer()
            time.sleep(2)  # Kurz warten
        
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
    
    try:
        from smartdesk.hotkeys.listener_manager import stop_listener
        from smartdesk.interfaces.tray.tray_manager import stop_tray
        
        # Listener stoppen
        try:
            stop_listener()
            print_success("Hotkey-Listener gestoppt.")
        except Exception as e:
            print_warning(f"Listener konnte nicht gestoppt werden: {e}")
        
        # Tray stoppen
        try:
            stop_tray()
            print_success("Tray-Icon gestoppt.")
        except Exception as e:
            print_warning(f"Tray konnte nicht gestoppt werden: {e}")
        
    except ImportError:
        print_warning("Dienste-Module nicht gefunden - möglicherweise bereits gestoppt.")
    except Exception as e:
        print_warning(f"Fehler beim Stoppen der Dienste: {e}")
    
    return success

def delete_appdata_folder() -> bool:
    """Löscht den SmartDesk-Ordner in AppData."""
    appdata_path = os.path.join(os.environ.get('APPDATA', ''), 'SmartDesk')
    
    if not os.path.exists(appdata_path):
        print_info("SmartDesk-Ordner existiert nicht.")
        return True
    
    try:
        # Zeige was gelöscht wird
        print_info(f"Ordner: {appdata_path}")
        
        # Größe berechnen
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(appdata_path):
            for f in files:
                total_size += os.path.getsize(os.path.join(root, f))
                file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        print_info(f"Enthält {file_count} Dateien ({size_mb:.2f} MB)")
        
        # Löschen
        shutil.rmtree(appdata_path)
        print_success("SmartDesk-Ordner gelöscht.")
        return True
        
    except PermissionError:
        print_error("Zugriff verweigert - sind noch Dienste aktiv?")
        return False
    except Exception as e:
        print_error(f"Fehler beim Löschen: {e}")
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
