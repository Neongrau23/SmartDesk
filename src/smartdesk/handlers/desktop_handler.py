# Dateipfad: src/smartdesk/handlers/desktop_handler.py
# (Aktualisiert, um die neue localization.py zu verwenden)

import winreg
import os
import shutil
import sys
import subprocess
from typing import List, Optional

from ..config import KEY_USER_SHELL, KEY_LEGACY_SHELL, VALUE_NAME
from ..utils.registry_operations import update_registry_key, get_registry_value
from ..utils.path_validator import ensure_directory_exists
from ..models.desktop import Desktop
from ..storage.file_operations import load_desktops, save_desktops
from ..localization import get_text # <-- NEUER IMPORT
# --- NEUE IMPORTS ---
from ..ui.style import PREFIX_ERROR, PREFIX_WARN, PREFIX_OK
from .icon_manager import get_current_icon_positions, set_icon_positions
# --- HIER NEU: Import für Wallpaper Manager ---
from . import wallpaper_manager


def create_desktop(name: str, path: str, create_if_missing: bool = True) -> bool:
    """
    Erstellt einen neuen Desktop und speichert ihn.
    
    Args:
        name (str): Name des Desktops.
        path (str): Pfad zum Desktop-Ordner.
        create_if_missing (bool): 
            True (Modus 2): Erstellt den Ordner, falls er nicht existiert.
            False (Modus 1): Prüft, ob der Ordner existiert, und schlägt fehl, wenn nicht.
    """
    
    # --- START ÄNDERUNG: Pfad-Logik basierend auf Modus ---
    if create_if_missing:
        # Modus 2: "Einen neuen Ordner erstellen"
        # Nutzt die bisherige Logik: Erstellen, wenn nicht vorhanden.
        if not ensure_directory_exists(path):
            # --- LOKALISIERT & GEFÄRBT ---
            print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.path_invalid', path=path)}")
            return False
    else:
        # Modus 1: "Einen existierenden Ordner verwenden"
        # Prüft nur, ob der Pfad existiert UND ein Verzeichnis ist.
        if not os.path.exists(path) or not os.path.isdir(path):
            # --- LOKALISIERT & GEFÄRBT ---
            print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.path_not_found_or_not_dir', path=path)}")
            return False
    # --- ENDE ÄNDERUNG ---


    desktops = load_desktops()
    
    if any(d.name == name for d in desktops):
        # --- LOKALISIERT & GEFÄRBT ---
        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.name_exists', name=name)}")
        return False

    new_desktop = Desktop(name=name, path=path)
    desktops.append(new_desktop)
    save_desktops(desktops)
    # --- LOKALISIERT (OK-Präfix hinzugefügt) ---
    print(f"{PREFIX_OK} {get_text('desktop_handler.success.create', name=name)}")
    return True

# --- (Funktion update_desktop bleibt unverändert) ---
def update_desktop(old_name: str, new_name: str, new_path: str) -> bool:
    """Aktualisiert Name und Pfad eines existierenden Desktops."""
    desktops = load_desktops()
    target_desktop = next((d for d in desktops if d.name == old_name), None)

    if not target_desktop:
        # --- LOKALISIERT & GEFÄRBT ---
        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.not_found', old_name=old_name)}")
        return False

    if new_name != old_name and any(d.name == new_name for d in desktops):
        # --- LOKALISIERT & GEFÄRBT ---
        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.new_name_exists', new_name=new_name)}")
        return False

    if new_path != target_desktop.path:
        old_path_exists = os.path.exists(target_desktop.path)
        
        if old_path_exists:
            try:
                if os.path.exists(new_path):
                     # --- LOKALISIERT & GEFÄRBT (Warnung) ---
                     print(f"{PREFIX_WARN} {get_text('desktop_handler.warn.target_path_exists', path=new_path)}")
                
                shutil.move(target_desktop.path, new_path)
                # --- LOKALISIERT ---
                print(get_text("desktop_handler.info.folder_moved", old_path=target_desktop.path, new_path=new_path))
                
            except Exception as e:
                # --- LOKALISIERT & GEFÄRBT ---
                print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.folder_move', e=e)}")
                return False
        else:
            if not ensure_directory_exists(new_path):
                # --- LOKALISIERT & GEFÄRBT ---
                print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.new_path_create', path=new_path)}")
                return False

    target_desktop.name = new_name
    target_desktop.path = new_path
    
    save_desktops(desktops)
    # --- LOKALISIERT (OK-Präfix hinzugefügt) ---
    print(f"{PREFIX_OK} {get_text('desktop_handler.success.update', old_name=old_name, new_name=new_name)}")
    return True

# --- (Funktion delete_desktop bleibt unverändert) ---
def delete_desktop(name: str, delete_folder: bool = False) -> bool:
    """
    Löscht einen Desktop aus der Datenbank, inkl. Bestätigungsabfrage.
    """
    desktops = get_all_desktops()
    
    target_desktop = next((d for d in desktops if d.name == name), None)

    if not target_desktop:
        # --- LOKALISIERT & GEFÄRBT ---
        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.not_found_delete', name=name)}")
        return False

    try:
        # --- LOKALISIERT ---
        confirm = input(get_text("desktop_handler.prompts.delete_confirm", name=name)).strip().lower()
    except EOFError: 
        # --- LOKALISIERT ---
        print(get_text("desktop_handler.info.delete_aborted"))
        return False
        
    if confirm != 'y':
        # --- LOKALISIERT ---
        print(get_text("desktop_handler.info.delete_aborted"))
        return False

    if target_desktop.is_active:
        # --- LOKALISIERT & GEFÄRBT ---
        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.delete_active', name=name)}")
        return False

    real_registry_path = get_registry_value(KEY_USER_SHELL, VALUE_NAME)
    
    if real_registry_path:
        norm_target = os.path.normpath(target_desktop.path).lower()
        norm_registry = os.path.normpath(os.path.expandvars(real_registry_path)).lower()

        if norm_registry == norm_target:
            # --- LOKALISIERT & GEFÄRBT ---
            print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.delete_critical', path=target_desktop.path)}")
            print(get_text("desktop_handler.info.delete_denied"))
            return False

    if delete_folder:
        if os.path.exists(target_desktop.path):
            try:
                shutil.rmtree(target_desktop.path)
                # --- LOKALISIERT (OK-Präfix hinzugefügt) ---
                print(f"{PREFIX_OK} {get_text('desktop_handler.success.folder_delete', path=target_desktop.path)}")
            except Exception as e:
                # --- LOKALISIERT & GEFÄRBT ---
                print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.folder_delete', e=e)}")
        else:
            # --- LOKALISIERT ---
            print(get_text("desktop_handler.info.folder_not_found", path=target_desktop.path))

    # --- NEU: Lösche das zugehörige Hintergrundbild, wenn es existiert ---
    if target_desktop.wallpaper_path and os.path.exists(target_desktop.wallpaper_path):
        try:
            os.remove(target_desktop.wallpaper_path)
            print(f"{PREFIX_OK} {get_text('desktop_handler.success.wallpaper_delete', path=target_desktop.wallpaper_path)}")
        except Exception as e:
            print(f"{PREFIX_WARN} {get_text('desktop_handler.warn.wallpaper_delete', e=e)}")
    # --- ENDE NEU ---

    desktops.remove(target_desktop)
    save_desktops(desktops)
    
    # --- LOKALISIERT (OK-Präfix hinzugefügt) ---
    print(f"{PREFIX_OK} {get_text('desktop_handler.success.delete', name=name)}")
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
        # --- LOKALISIERT & GEFÄRBT (Warnung) ---
        print(f"{PREFIX_WARN} {get_text('desktop_handler.warn.sync_failed', e=e)}")

    return desktops

# --- FUNKTION switch_to_desktop STARK AKTUALISIERT (BUGFIX & LOKALISIERUNG & ANIMATION) ---
def switch_to_desktop(desktop_name: str) -> bool:
    """
    Bereitet den Desktop-Wechsel vor.
    """
    desktops = get_all_desktops()
    
    target_desktop = next((d for d in desktops if d.name == desktop_name), None)
    if not target_desktop:
        # --- LOKALISIERT & GEFÄRBT ---
        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.switch_not_found', name=desktop_name)}")
        return False
    
    # ===== ANIMATION SOFORT STARTEN =====
    try:
        animation_script = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'animations', 
            'screen_fade.py'
        )
        subprocess.Popen(
            [sys.executable, animation_script],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except (OSError, ValueError) as e:
        print(f"{PREFIX_WARN} Animation konnte nicht gestartet werden: {e}")
    # ===== ANIMATION ENDE =====

    target_path = os.path.normpath(os.path.expandvars(target_desktop.path))

    # Prüfe, ob Desktop bereits aktiv ist
    # (nach Registry-Sync durch get_all_desktops())
    if target_desktop.is_active:
        # --- LOKALISIERT ---
        print(
            get_text(
                "desktop_handler.info.already_active",
                name=desktop_name
            )
        )
        return True

    # --- START LOKALISIERUNG BUGFIX ---
    if not os.path.exists(target_path):
        # --- LOKALISIERT & GEFÄRBT (Warnung) ---
        print(
            f"{PREFIX_WARN} "
            f"{get_text('desktop_handler.warn.path_not_found', name=desktop_name)}"
        )
        print(get_text("desktop_handler.info.path_is", path=target_path))
        print(get_text("desktop_handler.prompts.path_not_found_title"))
        print(get_text("desktop_handler.prompts.path_recreate"))
        print(get_text("desktop_handler.prompts.path_remove"))
        print(get_text("desktop_handler.prompts.path_abort"))

        try:
            choice = input(
                get_text("desktop_handler.prompts.your_choice")
            ).strip()
        except EOFError:
            choice = "j"

        if choice == '1':
            print(
                get_text(
                    "desktop_handler.info.recreating_folder",
                    path=target_path
                )
            )
            if ensure_directory_exists(target_path):
                # --- LOKALISIERT (OK-Präfix hinzugefügt) ---
                print(
                    f"{PREFIX_OK} "
                    f"{get_text('desktop_handler.success.recreating_folder')}"
                )
            else:
                # --- LOKALISIERT & GEFÄRBT ---
                print(
                    f"{PREFIX_ERROR} "
                    f"{get_text('desktop_handler.error.recreating_folder')}"
                )
                print(get_text("desktop_handler.info.aborting_switch"))
                return False

        elif choice == '2':
            print(
                get_text(
                    "desktop_handler.info.removing_config",
                    name=desktop_name
                )
            )
            try:
                desktops.remove(target_desktop)
                save_desktops(desktops)
                # --- LOKALISIERT (OK-Präfix hinzugefügt) ---
                msg = get_text(
                    'desktop_handler.success.removing_config',
                    name=desktop_name
                )
                print(f"{PREFIX_OK} {msg}")
            except (ValueError, OSError) as e:
                # --- LOKALISIERT & GEFÄRBT ---
                print(
                    f"{PREFIX_ERROR} "
                    f"{get_text('desktop_handler.error.removing_config', e=e)}"
                )

            print(get_text("desktop_handler.info.aborting_switch"))
            return False

        else:
            print(get_text("desktop_handler.info.aborting_switch"))
            return False
    # --- ENDE LOKALISIERUNG BUGFIX ---

    active_desktop = next((d for d in desktops if d.is_active), None)
    if active_desktop:
        # --- LOKALISIERT ---
        print(
            get_text(
                "desktop_handler.info.saving_icons",
                name=active_desktop.name
            )
        )
        try:
            # Timeout von 3 Sekunden für Icon-Lesen
            active_desktop.icon_positionen = get_current_icon_positions(
                timeout_seconds=3
            )
            active_desktop.is_active = False
            save_desktops(desktops)
            # --- LOKALISIERT (OK-Präfix hinzugefügt) ---
            print(
                f"{PREFIX_OK} "
                f"{get_text('desktop_handler.success.db_update')}"
            )
        except Exception as e:
            print(
                f"{PREFIX_WARN} Icon-Speicherung fehlgeschlagen: {e}"
            )
            # Wechsel trotzdem fortsetzen
            active_desktop.is_active = False
            save_desktops(desktops)
    else:
        # --- LOKALISIERT & GEFÄRBT (Warnung) ---
        msg = get_text('desktop_handler.warn.no_active_desktop')
        print(f"{PREFIX_WARN} {msg}")

    # --- LOKALISIERT ---
    print(
        get_text(
            "desktop_handler.info.switching_registry",
            name=target_desktop.name,
            path=target_desktop.path
        )
    )
    reg_success = True
    if not update_registry_key(
        KEY_USER_SHELL,
        VALUE_NAME,
        target_desktop.path,
        winreg.REG_EXPAND_SZ
    ):
        reg_success = False
    if not update_registry_key(
        KEY_LEGACY_SHELL,
        VALUE_NAME,
        target_desktop.path,
        winreg.REG_SZ
    ):
        reg_success = False

    if not reg_success:
        # --- LOKALISIERT & GEFÄRBT ---
        msg = get_text('desktop_handler.error.registry_update_failed')
        print(f"{PREFIX_ERROR} {msg}")
        if active_desktop:
            active_desktop.is_active = True
            save_desktops(desktops)
        return False

    # --- LOKALISIERT ---
    print(get_text("desktop_handler.info.registry_success"))
    return True


def sync_desktop_state_and_apply_icons():
    """
    Führt die Aktionen *nach* dem Explorer-Neustart aus.
    """
    # --- LOKALISIERT ---
    print(get_text("desktop_handler.info.sync_after_restart"))
    
    desktops = get_all_desktops()
    
    new_active_desktop = next((d for d in desktops if d.is_active), None)

    if not new_active_desktop:
        # --- LOKALISIERT & GEFÄRBT ---
        msg1 = get_text('desktop_handler.error.sync_no_active')
        print(f"{PREFIX_ERROR} {msg1}")
        # --- LOKALISIERT & GEFÄRBT (Warnung) ---
        msg2 = get_text('desktop_handler.warn.sync_path_not_registered')
        print(f"{PREFIX_WARN} {msg2}")
        return

    # --- LOKALISIERT ---
    print(
        get_text(
            "desktop_handler.info.sync_path_found",
            path=new_active_desktop.path
        )
    )
    print(
        get_text(
            "desktop_handler.info.sync_desktop_active",
            name=new_active_desktop.name
        )
    )
    
    # --- NEU: HINTERGRUNDBILD SETZEN ---
    if new_active_desktop.wallpaper_path:
        print(get_text("desktop_handler.info.setting_wallpaper"))
        wallpaper_manager.set_wallpaper(new_active_desktop.wallpaper_path)
    # --- ENDE NEU ---

    print(
        get_text(
            "desktop_handler.info.sync_restoring_icons",
            name=new_active_desktop.name
        )
    )
    set_icon_positions(new_active_desktop.icon_positionen)
    # --- LOKALISIERT ---
    print(get_text("desktop_handler.info.sync_icons_done"))


def save_current_desktop_icons() -> bool:
    """
    Findet den aktuell aktiven Desktop, liest seine
    Icon-Positionen aus und speichert sie in der Datenbank.
    """
    desktops = get_all_desktops()
    
    active_desktop = next((d for d in desktops if d.is_active), None)
    
    if not active_desktop:
        # --- LOKALISIERT & GEFÄRBT ---
        msg1 = get_text('desktop_handler.error.save_icons_no_active')
        print(f"{PREFIX_ERROR} {msg1}")
        # --- LOKALISIERT & GEFÄRBT (Warnung) ---
        msg2 = get_text('desktop_handler.warn.save_icons_not_registered')
        print(f"{PREFIX_WARN} {msg2}")
        return False

    try:
        # --- LOKALISIERT ---
        print(
            get_text(
                "desktop_handler.info.reading_icons",
                name=active_desktop.name
            )
        )
        active_desktop.icon_positionen = get_current_icon_positions()

        save_desktops(desktops)
        # --- LOKALISIERT (OK-Präfix hinzugefügt) ---
        msg3 = get_text(
            'desktop_handler.success.save_icons',
            name=active_desktop.name
        )
        print(f"{PREFIX_OK} {msg3}")
        return True
    except Exception as e:
        # --- LOKALISIERT & GEFÄRBT ---
        msg4 = get_text('desktop_handler.error.save_icons', e=e)
        print(f"{PREFIX_ERROR} {msg4}")
        return False


# --- NEUE FUNKTION FÜR HINTERGRUNDBILDER ---
def assign_wallpaper(desktop_name: str, source_image_path: str) -> bool:
    """
    Weist einem Desktop ein Hintergrundbild zu.
    Kopiert das Bild in den data-Ordner und speichert den Pfad.
    """
    if not os.path.exists(source_image_path):
        print(f"{PREFIX_ERROR} {get_text('wallpaper_manager.error.source_not_found', path=source_image_path)}")
        return False
        
    desktops = get_all_desktops()
    target_desktop = next((d for d in desktops if d.name == desktop_name), None)
    
    if not target_desktop:
        print(f"{PREFIX_ERROR} {get_text('desktop_handler.error.not_found', old_name=desktop_name)}")
        return False

    # 1. Altes Bild löschen, falls vorhanden
    if target_desktop.wallpaper_path and os.path.exists(target_desktop.wallpaper_path):
        try:
            os.remove(target_desktop.wallpaper_path)
            print(get_text("desktop_handler.info.old_wallpaper_removed"))
        except Exception as e:
            print(f"{PREFIX_WARN} {get_text('desktop_handler.warn.wallpaper_delete', e=e)}")

    # 2. Neues Bild in den data-Ordner kopieren
    new_path = wallpaper_manager.copy_wallpaper_to_datadir(
        source_image_path,
        target_desktop.name
    )
    
    if not new_path:
        # copy_wallpaper_to_datadir gibt bereits eine Fehlermeldung aus
        return False
        
    # 3. Pfad in der Datenbank speichern
    target_desktop.wallpaper_path = new_path
    save_desktops(desktops)
    
    print(f"{PREFIX_OK} {get_text('desktop_handler.success.wallpaper_assigned', name=desktop_name)}")
    
    # 4. Wenn der Desktop aktiv ist, Hintergrundbild sofort setzen
    if target_desktop.is_active:
        print(get_text("desktop_handler.info.setting_wallpaper_now"))
        wallpaper_manager.set_wallpaper(new_path)
        
    return True
