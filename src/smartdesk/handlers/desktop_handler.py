# Dateipfad: src/smartdesk/handlers/desktop_handler.py
# (Vollständige, korrigierte Datei)

import winreg
import os
import shutil
from typing import List, Optional

from ..config import KEY_USER_SHELL, KEY_LEGACY_SHELL, VALUE_NAME
from ..utils.registry_operations import update_registry_key, get_registry_value
from ..utils.path_validator import ensure_directory_exists
from ..models.desktop import Desktop
from ..storage.file_operations import load_desktops, save_desktops

# --- KORREKTUR HIER ---
# Da icon_manager.py im selben Ordner (handlers) wie diese Datei liegt,
# verwenden wir einen einzelnen Punkt (.) für einen relativen Import.
from .icon_manager import get_current_icon_positions, set_icon_positions
# --- ENDE KORREKTUR ---


def create_desktop(name: str, path: str) -> bool:
    """Erstellt einen neuen Desktop und speichert ihn."""
    if not ensure_directory_exists(path):
        print(f"Fehler: Pfad '{path}' ist ungültig oder konnte nicht erstellt werden.")
        return False

    desktops = load_desktops()
    
    if any(d.name == name for d in desktops):
        print(f"Fehler: Ein Desktop mit dem Namen '{name}' existiert bereits.")
        return False

    new_desktop = Desktop(name=name, path=path)
    desktops.append(new_desktop)
    save_desktops(desktops)
    print(f"Desktop '{name}' erfolgreich angelegt.")
    return True

def update_desktop(old_name: str, new_name: str, new_path: str) -> bool:
    """Aktualisiert Name und Pfad eines existierenden Desktops."""
    desktops = load_desktops()
    target_desktop = next((d for d in desktops if d.name == old_name), None)

    if not target_desktop:
        print(f"Fehler: Desktop '{old_name}' nicht gefunden.")
        return False

    if new_name != old_name and any(d.name == new_name for d in desktops):
        print(f"Fehler: Der Name '{new_name}' ist bereits vergeben.")
        return False

    if new_path != target_desktop.path:
        old_path_exists = os.path.exists(target_desktop.path)
        
        if old_path_exists:
            try:
                if os.path.exists(new_path):
                     print(f"Warnung: Zielpfad '{new_path}' existiert bereits. Versuche Inhalt zu integrieren...")
                
                shutil.move(target_desktop.path, new_path)
                print(f"Ordner physisch verschoben von '{target_desktop.path}' nach '{new_path}'.")
                
            except Exception as e:
                print(f"Fehler beim Verschieben des Ordners: {e}")
                return False
        else:
            if not ensure_directory_exists(new_path):
                print(f"Fehler: Neuer Pfad '{new_path}' konnte nicht erstellt werden.")
                return False

    target_desktop.name = new_name
    target_desktop.path = new_path
    
    save_desktops(desktops)
    print(f"Desktop '{old_name}' wurde aktualisiert zu '{new_name}'.")
    return True

def delete_desktop(name: str, delete_folder: bool = False) -> bool:
    """Löscht einen Desktop aus der Datenbank."""
    desktops = get_all_desktops()
    
    target_desktop = next((d for d in desktops if d.name == name), None)

    if not target_desktop:
        print(f"Fehler: Desktop '{name}' nicht gefunden.")
        return False

    if target_desktop.is_active:
        print(f"Fehler: Laut Datenbank (synchronisiert) ist '{name}' aktiv. Bitte wechseln Sie vorher den Desktop.")
        return False

    real_registry_path = get_registry_value(KEY_USER_SHELL, VALUE_NAME)
    
    if real_registry_path:
        norm_target = os.path.normpath(target_desktop.path).lower()
        norm_registry = os.path.normpath(real_registry_path).lower()
        norm_registry = os.path.normpath(os.path.expandvars(norm_registry)).lower()

        if norm_registry == norm_target:
            print(f"KRITISCHER FEHLER: Windows Registry meldet, dass '{target_desktop.path}' der aktive Desktop ist!")
            print("Löschen verweigert, um Datenverlust zu verhindern.")
            return False

    if delete_folder:
        if os.path.exists(target_desktop.path):
            try:
                shutil.rmtree(target_desktop.path) 
                print(f"Ordner '{target_desktop.path}' wurde vollständig gelöscht.")
            except Exception as e:
                print(f"Fehler beim Löschen des Ordners: {e}")
                return False
        else:
            print(f"Hinweis: Ordner '{target_desktop.path}' existierte nicht mehr.")

    desktops.remove(target_desktop)
    save_desktops(desktops)
    print(f"Desktop '{name}' wurde gelöscht.")
    return True

def get_all_desktops() -> List[Desktop]:
    """
    Gibt eine Liste aller Desktops zurück.
    Synchronisiert dabei automatisch den 'is_active' Status mit der Windows Registry.
    """
    desktops = load_desktops()
    
    try:
        real_registry_path = get_registry_value(KEY_USER_SHELL, VALUE_NAME)
        
        if real_registry_path:
            norm_registry = os.path.normpath(os.path.expandvars(real_registry_path)).lower()
            data_changed = False
            
            for d in desktops:
                norm_desktop = os.path.normpath(os.path.expandvars(d.path)).lower()
                should_be_active = (norm_desktop == norm_registry)
                
                if d.is_active != should_be_active:
                    d.is_active = should_be_active
                    data_changed = True
            
            if data_changed:
                save_desktops(desktops)
                
    except Exception as e:
        print(f"Warnung: Konnte Status nicht mit Registry synchronisieren: {e}")

    return desktops

def switch_to_desktop(desktop_name: str) -> bool:
    """
    Aktiviert einen Desktop anhand des Namens.
    Speichert die Icons des alten Desktops und lädt die Icons des neuen.
    """
    desktops = load_desktops()
    
    target_desktop = next((d for d in desktops if d.name == desktop_name), None)

    if not target_desktop:
        print(f"Fehler: Desktop '{desktop_name}' nicht gefunden.")
        return False
        
    if target_desktop.is_active:
        print(f"'{desktop_name}' ist bereits aktiv.")
        return True

    active_desktop = next((d for d in desktops if d.is_active), None)

    if active_desktop:
        print(f"Speichere Icon-Positionen für '{active_desktop.name}'...")
        active_desktop.icon_positionen = get_current_icon_positions()
        active_desktop.is_active = False
    else:
        print("Warnung: Es wurde kein aktiver Desktop gefunden. Überspringe Speichern der Icons.")

    print(f"Wechsle zu Desktop: {target_desktop.name} ({target_desktop.path})...")

    reg_success = True
    if not update_registry_key(KEY_USER_SHELL, VALUE_NAME, target_desktop.path, winreg.REG_EXPAND_SZ):
        reg_success = False
    
    if not update_registry_key(KEY_LEGACY_SHELL, VALUE_NAME, target_desktop.path, winreg.REG_SZ):
        reg_success = False

    if not reg_success:
        print("FEHLER: Konnte Registry nicht aktualisieren. Wechsel wird abgebrochen.")
        if active_desktop:
            active_desktop.is_active = True
        return False

    target_desktop.is_active = True
    save_desktops(desktops)
    print("Datenbank aktualisiert.")

    print(f"Stelle Icon-Positionen für '{target_desktop.name}' wieder her...")
    set_icon_positions(target_desktop.icon_positionen)
    
    return True

def save_current_desktop_icons() -> bool:
    """
    Findet den aktuell aktiven Desktop, liest seine
    Icon-Positionen aus und speichert sie in der Datenbank.
    """
    desktops = get_all_desktops()
    
    active_desktop = next((d for d in desktops if d.is_active), None)
    
    if not active_desktop:
        print("Fehler: Konnte keinen aktiven Desktop finden.")
        print("Möglicherweise ist der in Windows eingestellte Pfad")
        print("in SmartDesk nicht registriert.")
        return False
        
    try:
        print(f"Lese aktuelle Icon-Positionen für '{active_desktop.name}'...")
        active_desktop.icon_positionen = get_current_icon_positions()
        
        save_desktops(desktops)
        print(f"Icon-Positionen für '{active_desktop.name}' erfolgreich gespeichert.")
        return True
    except Exception as e:
        print(f"Fehler beim Speichern der Icons: {e}")
        return False
    