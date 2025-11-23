# Dateipfad: src/smartdesk/handlers/desktop_handler.py
# (Aktualisiert, um die neue localization.py zu verwenden)

import winreg
import os
import shutil
from typing import List, Optional

from ..config import KEY_USER_SHELL, KEY_LEGACY_SHELL, VALUE_NAME
from ..utils.registry_operations import update_registry_key, get_registry_value
from ..utils.path_validator import ensure_directory_exists
from ..models.desktop import Desktop
from ..storage.file_operations import load_desktops, save_desktops
from ..localization import get_text # <-- NEUER IMPORT

from .icon_manager import get_current_icon_positions, set_icon_positions


def create_desktop(name: str, path: str) -> bool:
    """Erstellt einen neuen Desktop und speichert ihn."""
    if not ensure_directory_exists(path):
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_PATH_INVALID", path=path))
        return False

    desktops = load_desktops()
    
    if any(d.name == name for d in desktops):
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_NAME_EXISTS", name=name))
        return False

    new_desktop = Desktop(name=name, path=path)
    desktops.append(new_desktop)
    save_desktops(desktops)
    # --- LOKALISIERT ---
    print(get_text("DH_SUCCESS_CREATE", name=name))
    return True

# --- (Funktion update_desktop bleibt unverändert) ---
def update_desktop(old_name: str, new_name: str, new_path: str) -> bool:
    """Aktualisiert Name und Pfad eines existierenden Desktops."""
    desktops = load_desktops()
    target_desktop = next((d for d in desktops if d.name == old_name), None)

    if not target_desktop:
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_NOT_FOUND", old_name=old_name))
        return False

    if new_name != old_name and any(d.name == new_name for d in desktops):
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_NEW_NAME_EXISTS", new_name=new_name))
        return False

    if new_path != target_desktop.path:
        old_path_exists = os.path.exists(target_desktop.path)
        
        if old_path_exists:
            try:
                if os.path.exists(new_path):
                     # --- LOKALISIERT ---
                     print(get_text("DH_WARN_TARGET_PATH_EXISTS", path=new_path))
                
                shutil.move(target_desktop.path, new_path)
                # --- LOKALISIERT ---
                print(get_text("DH_INFO_FOLDER_MOVED", old_path=target_desktop.path, new_path=new_path))
                
            except Exception as e:
                # --- LOKALISIERT ---
                print(get_text("DH_ERROR_FOLDER_MOVE", e=e))
                return False
        else:
            if not ensure_directory_exists(new_path):
                # --- LOKALISIERT ---
                print(get_text("DH_ERROR_NEW_PATH_CREATE", path=new_path))
                return False

    target_desktop.name = new_name
    target_desktop.path = new_path
    
    save_desktops(desktops)
    # --- LOKALISIERT ---
    print(get_text("DH_SUCCESS_UPDATE", old_name=old_name, new_name=new_name))
    return True

# --- (Funktion delete_desktop bleibt unverändert) ---
def delete_desktop(name: str, delete_folder: bool = False) -> bool:
    """
    Löscht einen Desktop aus der Datenbank, inkl. Bestätigungsabfrage.
    """
    desktops = get_all_desktops()
    
    target_desktop = next((d for d in desktops if d.name == name), None)

    if not target_desktop:
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_NOT_FOUND_DELETE", name=name))
        return False

    try:
        # --- LOKALISIERT ---
        confirm = input(get_text("DH_PROMPT_DELETE_CONFIRM", name=name)).strip().lower()
    except EOFError: 
        # --- LOKALISIERT ---
        print(get_text("DH_INFO_DELETE_ABORTED"))
        return False
        
    if confirm != 'y':
        # --- LOKALISIERT ---
        print(get_text("DH_INFO_DELETE_ABORTED"))
        return False

    if target_desktop.is_active:
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_DELETE_ACTIVE", name=name))
        return False

    real_registry_path = get_registry_value(KEY_USER_SHELL, VALUE_NAME)
    
    if real_registry_path:
        norm_target = os.path.normpath(target_desktop.path).lower()
        norm_registry = os.path.normpath(os.path.expandvars(real_registry_path)).lower()

        if norm_registry == norm_target:
            # --- LOKALISIERT ---
            print(get_text("DH_ERROR_DELETE_CRITICAL", path=target_desktop.path))
            print(get_text("DH_INFO_DELETE_DENIED"))
            return False

    if delete_folder:
        if os.path.exists(target_desktop.path):
            try:
                shutil.rmtree(target_desktop.path)
                # --- LOKALISIERT ---
                print(get_text("DH_SUCCESS_FOLDER_DELETE", path=target_desktop.path))
            except Exception as e:
                # --- LOKALISIERT ---
                print(get_text("DH_ERROR_FOLDER_DELETE", e=e))
        else:
            # --- LOKALISIERT ---
            print(get_text("DH_INFO_FOLDER_NOT_FOUND", path=target_desktop.path))

    desktops.remove(target_desktop)
    save_desktops(desktops)
    
    # --- LOKALISIERT ---
    print(get_text("DH_SUCCESS_DELETE", name=name))
    return True

# --- (Funktion get_all_desktops bleibt unverändert) ---
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
        # --- LOKALISIERT ---
        print(get_text("DH_WARN_SYNC_FAILED", e=e))

    return desktops

# --- FUNKTION switch_to_desktop STARK AKTUALISIERT (BUGFIX & LOKALISIERUNG) ---
def switch_to_desktop(desktop_name: str) -> bool:
    """
    Bereitet den Desktop-Wechsel vor.
    """
    desktops = load_desktops()
    
    target_desktop = next((d for d in desktops if d.name == desktop_name), None)
    if not target_desktop:
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_SWITCH_NOT_FOUND", name=desktop_name))
        return False
        
    target_path = os.path.normpath(os.path.expandvars(target_desktop.path))
    
    # --- START LOKALISIERUNG BUGFIX ---
    if not os.path.exists(target_path):
        print(get_text("DH_WARN_PATH_NOT_FOUND", name=desktop_name))
        print(get_text("DH_INFO_PATH_IS", path=target_path))
        print(get_text("DH_PROMPT_PATH_NOT_FOUND_TITLE"))
        print(get_text("DH_PROMPT_PATH_RECREATE"))
        print(get_text("DH_PROMPT_PATH_REMOVE"))
        print(get_text("DH_PROMPT_PATH_ABORT"))
        
        try:
            choice = input(get_text("DH_PROMPT_YOUR_CHOICE")).strip()
        except EOFError:
            choice = "j"
            
        if choice == '1':
            print(get_text("DH_INFO_RECREATING_FOLDER", path=target_path))
            if ensure_directory_exists(target_path):
                print(get_text("DH_SUCCESS_RECREATING_FOLDER"))
            else:
                print(get_text("DH_ERROR_RECREATING_FOLDER"))
                print(get_text("DH_INFO_ABORTING_SWITCH"))
                return False 
                
        elif choice == '2':
            print(get_text("DH_INFO_REMOVING_CONFIG", name=desktop_name))
            try:
                desktops.remove(target_desktop)
                save_desktops(desktops)
                print(get_text("DH_SUCCESS_REMOVING_CONFIG"))
            except Exception as e:
                print(get_text("DH_ERROR_REMOVING_CONFIG", e=e))
            
            print(get_text("DH_INFO_ABORTING_SWITCH"))
            return False 
            
        else:
            print(get_text("DH_INFO_ABORTING_SWITCH"))
            return False 
    # --- ENDE LOKALISIERUNG BUGFIX ---

    current_active_desktops = get_all_desktops()
    current_active = next((d for d in current_active_desktops if d.is_active), None)
    if current_active and current_active.name == desktop_name:
        # --- LOKALISIERT ---
        print(get_text("DH_INFO_ALREADY_ACTIVE", name=desktop_name))
        return False 

    active_desktop = next((d for d in desktops if d.is_active), None)
    if active_desktop:
        # --- LOKALISIERT ---
        print(get_text("DH_INFO_SAVING_ICONS", name=active_desktop.name))
        active_desktop.icon_positionen = get_current_icon_positions()
        active_desktop.is_active = False 
        save_desktops(desktops)
        # --- LOKALISIERT ---
        print(get_text("DH_SUCCESS_DB_UPDATE"))
    else:
        # --- LOKALISIERT ---
        print(get_text("DH_WARN_NO_ACTIVE_DESKTOP"))

    # --- LOKALISIERT ---
    print(get_text("DH_INFO_SWITCHING_REGISTRY", name=target_desktop.name, path=target_desktop.path))
    reg_success = True
    if not update_registry_key(KEY_USER_SHELL, VALUE_NAME, target_desktop.path, winreg.REG_EXPAND_SZ):
        reg_success = False
    if not update_registry_key(KEY_LEGACY_SHELL, VALUE_NAME, target_desktop.path, winreg.REG_SZ):
        reg_success = False

    if not reg_success:
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_REGISTRY_UPDATE_FAILED"))
        if active_desktop:
            active_desktop.is_active = True
            save_desktops(desktops)
        return False
    
    # --- LOKALISIERT ---
    print(get_text("DH_INFO_REGISTRY_SUCCESS"))
    return True 

# --- (Funktion sync_desktop_state_and_apply_icons bleibt unverändert) ---
def sync_desktop_state_and_apply_icons():
    """
    Führt die Aktionen *nach* dem Explorer-Neustart aus.
    """
    # --- LOKALISIERT ---
    print(get_text("DH_INFO_SYNC_AFTER_RESTART"))
    
    desktops = get_all_desktops()
    
    new_active_desktop = next((d for d in desktops if d.is_active), None)
    
    if not new_active_desktop:
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_SYNC_NO_ACTIVE"))
        print(get_text("DH_ERROR_SYNC_PATH_NOT_REGISTERED"))
        return

    # --- LOKALISIERT ---
    print(get_text("DH_INFO_SYNC_PATH_FOUND", path=new_active_desktop.path))
    print(get_text("DH_INFO_SYNC_DESKTOP_ACTIVE", name=new_active_desktop.name))
    
    print(get_text("DH_INFO_SYNC_RESTORING_ICONS", name=new_active_desktop.name))
    set_icon_positions(new_active_desktop.icon_positionen)
    # --- LOKALISIERT ---
    print(get_text("DH_INFO_SYNC_ICONS_DONE"))

# --- (Funktion save_current_desktop_icons bleibt unverändert) ---
def save_current_desktop_icons() -> bool:
    """
    Findet den aktuell aktiven Desktop, liest seine
    Icon-Positionen aus und speichert sie in der Datenbank.
    """
    desktops = get_all_desktops()
    
    active_desktop = next((d for d in desktops if d.is_active), None)
    
    if not active_desktop:
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_SAVE_ICONS_NO_ACTIVE"))
        print(get_text("DH_ERROR_SAVE_ICONS_NOT_REGISTERED"))
        return False
        
    try:
        # --- LOKALISIERT ---
        print(get_text("DH_INFO_READING_ICONS", name=active_desktop.name))
        active_desktop.icon_positionen = get_current_icon_positions()
        
        save_desktops(desktops)
        # --- LOKALISIERT ---
        print(get_text("DH_SUCCESS_SAVE_ICONS", name=active_desktop.name))
        return True
    except Exception as e:
        # --- LOKALISIERT ---
        print(get_text("DH_ERROR_SAVE_ICONS", e=e))
        return False
    