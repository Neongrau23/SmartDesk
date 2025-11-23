# Dateipfad: src/smartdesk/handlers/desktop_handler.py
# (Aktualisiert mit Bestätigungsabfrage und Beispiel-Ausgaben)

import winreg
import os
import shutil
from typing import List, Optional

from ..config import KEY_USER_SHELL, KEY_LEGACY_SHELL, VALUE_NAME
from ..utils.registry_operations import update_registry_key, get_registry_value
from ..utils.path_validator import ensure_directory_exists
from ..models.desktop import Desktop
from ..storage.file_operations import load_desktops, save_desktops

from .icon_manager import get_current_icon_positions, set_icon_positions
from .wallpaper_manager import set_wallpaper, save_current_wallpaper_to_desktop


def create_desktop(name: str, path: str) -> bool:
    """Erstellt einen neuen Desktop und speichert ihn."""
    if not ensure_directory_exists(path):
        print(f"✗ Fehler: Pfad '{path}' ist ungültig oder konnte nicht erstellt werden.")
        return False

    desktops = load_desktops()
    
    if any(d.name == name for d in desktops):
        print(f"✗ Fehler: Ein Desktop mit dem Namen '{name}' existiert bereits.")
        return False

    new_desktop = Desktop(name=name, path=path)
    desktops.append(new_desktop)
    save_desktops(desktops)
    print(f"✓ Desktop '{name}' erfolgreich angelegt.")
    return True

# --- (Funktion update_desktop bleibt unverändert) ---
def update_desktop(old_name: str, new_name: str, new_path: str) -> bool:
    """Aktualisiert Name und Pfad eines existierenden Desktops."""
    desktops = load_desktops()
    target_desktop = next((d for d in desktops if d.name == old_name), None)

    if not target_desktop:
        print(f"✗ Fehler: Desktop '{old_name}' nicht gefunden.")
        return False

    if new_name != old_name and any(d.name == new_name for d in desktops):
        print(f"✗ Fehler: Der Name '{new_name}' ist bereits vergeben.")
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
                print(f"✗ Fehler beim Verschieben des Ordners: {e}")
                return False
        else:
            if not ensure_directory_exists(new_path):
                print(f"✗ Fehler: Neuer Pfad '{new_path}' konnte nicht erstellt werden.")
                return False

    target_desktop.name = new_name
    target_desktop.path = new_path
    
    save_desktops(desktops)
    print(f"✓ Desktop '{old_name}' wurde aktualisiert zu '{new_name}'.")
    return True

# --- FUNKTION delete_desktop STARK AKTUALISIERT ---
def delete_desktop(name: str, delete_folder: bool = False) -> bool:
    """
    Löscht einen Desktop aus der Datenbank, inkl. Bestätigungsabfrage.
    """
    # get_all_desktops() synchronisiert den Status, falls wir 'is_active' prüfen
    desktops = get_all_desktops()
    
    target_desktop = next((d for d in desktops if d.name == name), None)

    if not target_desktop:
        # Erfüllt Akzeptanzkriterium: Fehlermeldung bei nicht existierendem Desktop
        print(f"✗ Fehler: Desktop '{name}' existiert nicht")
        return False

    # --- NEU: Akzeptanzkriterium: Bestätigungsabfrage ---
    try:
        confirm = input(f"Desktop '{name}' wirklich löschen? (y/n): ").strip().lower()
    except EOFError: # Verhindert Absturz bei direktem Aufruf (z.B. in Tests oder Pipes)
        print("Löschvorgang abgebrochen.")
        return False
        
    if confirm != 'y':
        print("Löschvorgang abgebrochen.")
        return False
    # --- ENDE NEU ---

    # Sicherheitsprüfung: Aktiven Desktop nicht löschen
    if target_desktop.is_active:
        print(f"✗ Fehler: Desktop '{name}' ist aktiv. Bitte wechseln Sie vorher den Desktop.")
        return False

    # Sicherheitsprüfung: Vergleiche mit realem Registry-Pfad
    real_registry_path = get_registry_value(KEY_USER_SHELL, VALUE_NAME)
    
    if real_registry_path:
        norm_target = os.path.normpath(target_desktop.path).lower()
        norm_registry = os.path.normpath(os.path.expandvars(real_registry_path)).lower()

        if norm_registry == norm_target:
            print(f"✗ KRITISCHER FEHLER: Windows Registry meldet, dass '{target_desktop.path}' der aktive Desktop ist!")
            print("Löschen verweigert, um Datenverlust zu verhindern.")
            return False

    # Physisches Löschen des Ordners (optional)
    if delete_folder:
        if os.path.exists(target_desktop.path):
            try:
                shutil.rmtree(target_desktop.path)
                print(f"✓ Ordner '{target_desktop.path}' wurde physisch gelöscht.")
            except Exception as e:
                print(f"✗ Fehler beim Löschen des Ordners: {e}")
                # Wir brechen hier nicht ab, der Eintrag soll trotzdem entfernt werden
        else:
            print(f"Hinweis: Ordner '{target_desktop.path}' existierte nicht mehr.")

    # Erfüllt Akzeptanzkriterium: Entfernt Desktop aus desktops.json
    desktops.remove(target_desktop)
    save_desktops(desktops)
    
    # Erfüllt Akzeptanzkriterium: Success-Message
    print(f"✓ Desktop '{name}' erfolgreich gelöscht")
    return True

def get_all_desktops() -> List[Desktop]:
    """
    (Schritt 4, 5, 6)
    Gibt eine Liste aller Desktops zurück.
    Synchronisiert dabei automatisch den 'is_active' Status mit der Windows Registry.
    """
    desktops = load_desktops()
    
    try:
        real_registry_path = get_registry_value(KEY_USER_SHELL, VALUE_NAME)
        
        if real_registry_path:
            # (Schritt 4: Registry prüfen)
            norm_registry = os.path.normpath(os.path.expandvars(real_registry_path)).lower()
            data_changed = False
            
            for d in desktops:
                # (Schritt 5: Registry-Pfad in JSON suchen)
                norm_desktop = os.path.normpath(os.path.expandvars(d.path)).lower()
                should_be_active = (norm_desktop == norm_registry)
                
                if d.is_active != should_be_active:
                    # (Schritt 6: Desktop auf "AKTIV" stellen)
                    d.is_active = should_be_active
                    data_changed = True
            
            if data_changed:
                save_desktops(desktops)
                
    except Exception as e:
        print(f"Warnung: Konnte Status nicht mit Registry synchronisieren: {e}")

    return desktops

def switch_to_desktop(desktop_name: str) -> bool:
    """
    (Schritt 1 & 2)
    Bereitet den Desktop-Wechsel vor:
    1. Speichert Icons des alten Desktops.
    2. Ändert den Registry-Pfad.
    Gibt True zurück, wenn der Explorer neugestartet werden kann.
    """
    # Lade Desktops *ohne* Sync, da wir den *alten* aktiven Desktop finden wollen
    desktops = load_desktops()
    
    target_desktop = next((d for d in desktops if d.name == desktop_name), None)
    if not target_desktop:
        print(f"✗ Fehler: Desktop '{desktop_name}' nicht gefunden.")
        return False
        
    # Prüfe, ob der *eigentlich* aktive Desktop (laut Registry) bereits das Ziel ist
    current_active_desktops = get_all_desktops()
    current_active = next((d for d in current_active_desktops if d.is_active), None)
    if current_active and current_active.name == desktop_name:
        print(f"'{desktop_name}' ist bereits aktiv.")
        return False # False signalisiert "kein Neustart nötig"

    # (Schritt 1: Icon Position von Desktop1 (alt) speichern)
    # Wir nutzen die nicht-synchronisierte Liste, um den *alten* aktiven Desktop zu finden
    active_desktop = next((d for d in desktops if d.is_active), None)
    if active_desktop:
        print(f"Speichere Icon-Positionen und Hintergrund für '{active_desktop.name}'...")
        active_desktop.icon_positionen = get_current_icon_positions()
        
        # Speichere aktuellen Wallpaper, falls noch nicht gesetzt
        if not active_desktop.wallpaper_path:
            save_current_wallpaper_to_desktop(active_desktop)
        
        active_desktop.is_active = False # Flag in lokaler Kopie setzen
        # Speichere die *gesamte* Liste (inkl. der neuen Icons und Wallpaper)
        save_desktops(desktops)
        print("Datenbank (Icon-Speicherung und Wallpaper) aktualisiert.")
    else:
        print("Warnung: Es wurde kein als 'aktiv' markierter Desktop gefunden. Überspringe Speichern der Icons.")

    # (Schritt 2: Änderung in der Registry vornehmen)
    print(f"Wechsle Registry zu Desktop: {target_desktop.name} ({target_desktop.path})...")
    reg_success = True
    if not update_registry_key(KEY_USER_SHELL, VALUE_NAME, target_desktop.path, winreg.REG_EXPAND_SZ):
        reg_success = False
    if not update_registry_key(KEY_LEGACY_SHELL, VALUE_NAME, target_desktop.path, winreg.REG_SZ):
        reg_success = False

    if not reg_success:
        print("✗ FEHLER: Konnte Registry nicht aktualisieren. Wechsel wird abgebrochen.")
        # Rollback: setze das 'is_active' Flag zurück, das wir lokal geändert haben
        if active_desktop:
            active_desktop.is_active = True
            save_desktops(desktops) # Speichern, um den Rollback zu vollziehen
        return False
    
    print("Registry-Änderung erfolgreich. Neustart des Explorers erforderlich.")
    return True # Signal an CLI, dass der Neustart erfolgen kann

# --- NEUE FUNKTION HINZUGEFÜGT ---
def sync_desktop_state_and_apply_icons():
    """
    (Schritt 4, 5, 6, 7)
    Führt die Aktionen *nach* dem Explorer-Neustart aus.
    - Synchronisiert DB-Status mit Registry (get_all_desktops)
    - Stellt Icons des neuen aktiven Desktops wieder her
    """
    print("Synchronisiere Status nach Neustart...")
    
    # (Schritt 4, 5, 6: get_all_desktops() prüft Registry, findet Pfad, setzt 'is_active')
    desktops = get_all_desktops()
    
    new_active_desktop = next((d for d in desktops if d.is_active), None)
    
    if not new_active_desktop:
        print("✗ FEHLER: Konnte nach Neustart keinen aktiven Desktop in der DB finden.")
        print("Möglicherweise ist der Registry-Pfad in der desktops.json nicht registriert.")
        return

    print(f"Registry-Pfad '{new_active_desktop.path}' gefunden.")
    print(f"Desktop '{new_active_desktop.name}' ist jetzt aktiv.")
    
    # Wallpaper wiederherstellen, falls konfiguriert
    if new_active_desktop.wallpaper_path:
        print(f"Stelle Hintergrundbild für '{new_active_desktop.name}' wieder her...")
        set_wallpaper(new_active_desktop.wallpaper_path)
    else:
        print(f"Kein individueller Hintergrund für '{new_active_desktop.name}' konfiguriert.")
    
    # (Schritt 7: Desktop icons des aktiven Desktops (Desktop2) an Position verschieben)
    print(f"Stelle Icon-Positionen für '{new_active_desktop.name}' wieder her...")
    set_icon_positions(new_active_desktop.icon_positionen)
    print("Icon-Wiederherstellung abgeschlossen.")


def save_current_desktop_icons() -> bool:
    """
    Findet den aktuell aktiven Desktop, liest seine
    Icon-Positionen aus und speichert sie in der Datenbank.
    """
    # get_all_desktops() synchronisiert erst den Status
    desktops = get_all_desktops()
    
    active_desktop = next((d for d in desktops if d.is_active), None)
    
    if not active_desktop:
        print("✗ Fehler: Konnte keinen aktiven Desktop finden.")
        print("Möglicherweise ist der in Windows eingestellte Pfad")
        print("in SmartDesk nicht registriert.")
        return False
        
    try:
        print(f"Lese aktuelle Icon-Positionen für '{active_desktop.name}'...")
        active_desktop.icon_positionen = get_current_icon_positions()
        
        save_desktops(desktops)
        print(f"✓ Icon-Positionen für '{active_desktop.name}' erfolgreich gespeichert.")
        return True
    except Exception as e:
        print(f"✗ Fehler beim Speichern der Icons: {e}")
        return False


def set_desktop_wallpaper(desktop_name: str, wallpaper_path: str) -> bool:
    """
    Setzt den Hintergrund für einen bestimmten Desktop.
    
    Args:
        desktop_name: Name des Desktops
        wallpaper_path: Vollständiger Pfad zum Hintergrundbild
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    desktops = load_desktops()
    target_desktop = next((d for d in desktops if d.name == desktop_name), None)
    
    if not target_desktop:
        print(f"✗ Fehler: Desktop '{desktop_name}' nicht gefunden.")
        return False
    
    # Pfad erweitern und prüfen
    expanded_path = os.path.expandvars(wallpaper_path)
    if not os.path.exists(expanded_path):
        print(f"✗ Fehler: Hintergrundbild nicht gefunden: {expanded_path}")
        return False
    
    # Speichere Wallpaper-Pfad im Desktop
    target_desktop.wallpaper_path = wallpaper_path
    save_desktops(desktops)
    
    print(f"✓ Hintergrund für Desktop '{desktop_name}' gesetzt: {wallpaper_path}")
    
    # Wenn der Desktop aktiv ist, wende das Wallpaper sofort an
    if target_desktop.is_active:
        print("Desktop ist aktiv. Wende Hintergrund sofort an...")
        return set_wallpaper(wallpaper_path)
    
    return True


def clear_desktop_wallpaper(desktop_name: str) -> bool:
    """
    Entfernt die Wallpaper-Konfiguration für einen Desktop.
    
    Args:
        desktop_name: Name des Desktops
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    desktops = load_desktops()
    target_desktop = next((d for d in desktops if d.name == desktop_name), None)
    
    if not target_desktop:
        print(f"✗ Fehler: Desktop '{desktop_name}' nicht gefunden.")
        return False
    
    target_desktop.wallpaper_path = ""
    save_desktops(desktops)
    
    print(f"✓ Hintergrund-Konfiguration für Desktop '{desktop_name}' entfernt.")
    return True
    
