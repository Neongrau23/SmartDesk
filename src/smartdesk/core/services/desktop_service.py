# Dateipfad: src/smartdesk/core/services/desktop_service.py

import winreg
import os
import shutil
import sys
import time
import subprocess
from typing import List

from ...shared.config import KEY_USER_SHELL, KEY_LEGACY_SHELL, VALUE_NAME
from ..utils.registry_operations import update_registry_key, get_registry_value
from ..utils.path_validator import ensure_directory_exists
from ..models.desktop import Desktop
from ..storage.file_operations import load_desktops, save_desktops
from ...shared.localization import get_text
from ...shared.logging_config import get_logger
from .icon_service import get_current_icon_positions, set_icon_positions
from . import wallpaper_service

logger = get_logger(__name__)


def create_desktop(name: str, path: str, create_if_missing: bool = True) -> bool:
    """
    Erstellt einen neuen Desktop und speichert ihn.
    """
    if create_if_missing:
        if not ensure_directory_exists(path):
            return False
    else:
        if not os.path.exists(path) or not os.path.isdir(path):
            msg = get_text('desktop_handler.error.path_not_found_or_not_dir', path=path)
            logger.error(msg)
            return False

    desktops = load_desktops()

    if any(d.name == name for d in desktops):
        msg = get_text('desktop_handler.error.name_exists', name=name)
        logger.error(msg)
        return False

    new_desktop = Desktop(name=name, path=path)
    desktops.append(new_desktop)
    save_desktops(desktops)

    msg = get_text('desktop_handler.success.create', name=name)
    logger.info(msg)
    return True


def update_desktop(old_name: str, new_name: str, new_path: str) -> bool:
    """Aktualisiert Name und Pfad eines existierenden Desktops."""
    desktops = load_desktops()
    target_desktop = next((d for d in desktops if d.name == old_name), None)

    if not target_desktop:
        msg = get_text('desktop_handler.error.not_found', old_name=old_name)
        logger.error(msg)
        return False

    # Geschützte Desktops können nicht bearbeitet werden
    if target_desktop.protected:
        msg = get_text('desktop_handler.error.protected_edit', name=old_name)
        logger.error(msg)
        return False

    if new_name != old_name and any(d.name == new_name for d in desktops):
        msg = get_text('desktop_handler.error.new_name_exists', new_name=new_name)
        logger.error(msg)
        return False

    if new_path != target_desktop.path:
        old_path_exists = os.path.exists(target_desktop.path)

        if old_path_exists:
            try:
                if os.path.exists(new_path):
                    msg = get_text(
                        'desktop_handler.warn.target_path_exists', path=new_path
                    )
                    logger.warning(msg)

                shutil.move(target_desktop.path, new_path)
                msg = get_text(
                    "desktop_handler.info.folder_moved",
                    old_path=target_desktop.path,
                    new_path=new_path,
                )
                logger.info(msg)
            except Exception as e:
                msg = get_text('desktop_handler.error.folder_move', e=e)
                logger.error(msg)
                return False
        else:
            if not ensure_directory_exists(new_path):
                msg = get_text('desktop_handler.error.new_path_create', path=new_path)
                logger.error(msg)
                return False

    target_desktop.name = new_name
    target_desktop.path = new_path

    save_desktops(desktops)
    msg = get_text(
        'desktop_handler.success.update', old_name=old_name, new_name=new_name
    )
    logger.info(msg)
    return True


def delete_desktop(name: str, delete_folder: bool = False, skip_confirm: bool = False) -> bool:
    """
    Löscht einen Desktop aus der Datenbank, inkl. Bestätigungsabfrage.
    Geschützte Desktops (z.B. Original) können nicht gelöscht werden.
    """
    desktops = get_all_desktops()
    target_desktop = next((d for d in desktops if d.name == name), None)

    if not target_desktop:
        msg = get_text('desktop_handler.error.not_found_delete', name=name)
        logger.error(msg)
        return False

    # Geschützte Desktops können nicht gelöscht werden
    if target_desktop.protected:
        msg = get_text('desktop_handler.error.protected_delete', name=name)
        logger.error(msg)
        return False

    if not skip_confirm:
        # Warnung: input() ist problematisch in GUI-Umgebungen.
        # Sollte durch GUI-Dialoge und skip_confirm=True ersetzt werden.
        try:
            confirm = (
                input(get_text("desktop_handler.prompts.delete_confirm", name=name))
                .strip()
                .lower()
            )
        except (EOFError, OSError):
            logger.warning(get_text("desktop_handler.info.delete_aborted") + " (No Input)")
            return False

        if confirm != 'y':
            logger.info(get_text("desktop_handler.info.delete_aborted"))
            return False

    if target_desktop.is_active:
        msg = get_text('desktop_handler.error.delete_active', name=name)
        logger.error(msg)
        return False

    real_registry_path = get_registry_value(KEY_USER_SHELL, VALUE_NAME)

    if real_registry_path:
        norm_target = os.path.normpath(target_desktop.path).lower()
        norm_registry = os.path.normpath(os.path.expandvars(real_registry_path)).lower()

        if norm_registry == norm_target:
            msg = get_text(
                'desktop_handler.error.delete_critical', path=target_desktop.path
            )
            logger.error(msg)
            logger.info(get_text("desktop_handler.info.delete_denied"))
            return False

    if delete_folder:
        if os.path.exists(target_desktop.path):
            try:
                shutil.rmtree(target_desktop.path)
                msg = get_text(
                    'desktop_handler.success.folder_delete', path=target_desktop.path
                )
                logger.info(msg)
            except Exception as e:
                msg = get_text('desktop_handler.error.folder_delete', e=e)
                logger.error(msg)
        else:
            msg = get_text(
                "desktop_handler.info.folder_not_found", path=target_desktop.path
            )
            logger.info(msg)

    # Lösche das zugehörige Hintergrundbild
    if target_desktop.wallpaper_path and os.path.exists(target_desktop.wallpaper_path):
        try:
            os.remove(target_desktop.wallpaper_path)
            msg = get_text(
                'desktop_handler.success.wallpaper_delete',
                path=target_desktop.wallpaper_path,
            )
            logger.info(msg)
        except Exception as e:
            msg = get_text('desktop_handler.warn.wallpaper_delete', e=e)
            logger.warning(msg)

    desktops.remove(target_desktop)
    save_desktops(desktops)

    msg = get_text('desktop_handler.success.delete', name=name)
    logger.info(msg)
    return True


def get_all_desktops() -> List[Desktop]:
    """
    Gibt eine Liste aller Desktops zurück.
    Synchronisiert dabei automatisch den 'is_active' Status mit der Registry.
    Geschützte Desktops werden immer zuerst angezeigt.
    """
    desktops = load_desktops()

    try:
        real_registry_path = get_registry_value(KEY_USER_SHELL, VALUE_NAME)

        if real_registry_path:
            norm_registry = os.path.normpath(
                os.path.expandvars(real_registry_path)
            ).lower()
            data_changed = False

            for d in desktops:
                norm_desktop = os.path.normpath(os.path.expandvars(d.path)).lower()
                should_be_active = norm_desktop == norm_registry

                if d.is_active != should_be_active:
                    d.is_active = should_be_active
                    data_changed = True

            if data_changed:
                save_desktops(desktops)

    except Exception as e:
        msg = get_text('desktop_handler.warn.sync_failed', e=e)
        logger.warning(msg)

    # Sortierung: Geschützte Desktops zuerst, dann alphabetisch
    desktops.sort(key=lambda d: (not d.protected, d.name.lower()))
    
    return desktops


def switch_to_desktop(desktop_name: str) -> bool:
    """
    Bereitet den Desktop-Wechsel vor.
    Gibt True zurück, wenn ein Explorer-Neustart NÖTIG ist.
    """
    from ..utils.backup_service import create_backup_before_switch

    desktops = get_all_desktops()

    target_desktop = next((d for d in desktops if d.name == desktop_name), None)
    if not target_desktop:
        msg = get_text('desktop_handler.error.switch_not_found', name=desktop_name)
        logger.error(msg)
        return False

    if target_desktop.is_active:
        msg = get_text("desktop_handler.info.already_active", name=desktop_name)
        logger.info(msg)
        return False

    # Automatisches Backup vor dem Wechsel
    backup_path = create_backup_before_switch()
    if backup_path:
        logger.info("Registry-Backup erstellt")

    target_path = os.path.normpath(os.path.expandvars(target_desktop.path))

    if not os.path.exists(target_path):
        msg = get_text('desktop_handler.warn.path_not_found', name=desktop_name)
        logger.warning(msg)
        logger.info(get_text("desktop_handler.info.path_is", path=target_path))
        
        # Interaktive Abfrage vermeiden, wenn möglich, oder loggen.
        # Hier ist ein potenzielles Problem für GUI, ähnlich wie bei delete_desktop.
        # Aber switch_to_desktop wird meist via Hotkey oder CLI aufgerufen.
        # Via GUI (Tray) wird es auch aufgerufen.
        
        print(get_text("desktop_handler.prompts.path_not_found_title")) # TODO: Refactor input
        print(get_text("desktop_handler.prompts.path_recreate"))
        print(get_text("desktop_handler.prompts.path_remove"))
        print(get_text("desktop_handler.prompts.path_abort"))

        try:
            choice = input(get_text("desktop_handler.prompts.your_choice")).strip()
        except (EOFError, OSError):
            choice = "j" # Default fallback? Oder Abort?

        if choice == '1':
            msg = get_text("desktop_handler.info.recreating_folder", path=target_path)
            logger.info(msg)
            if ensure_directory_exists(target_path):
                msg = get_text('desktop_handler.success.recreating_folder')
                logger.info(msg)
            else:
                msg = get_text('desktop_handler.error.recreating_folder')
                logger.error(msg)
                logger.info(get_text("desktop_handler.info.aborting_switch"))
                return False

        elif choice == '2':
            msg = get_text("desktop_handler.info.removing_config", name=desktop_name)
            logger.info(msg)
            try:
                desktops.remove(target_desktop)
                save_desktops(desktops)
                msg = get_text(
                    'desktop_handler.success.removing_config', name=desktop_name
                )
                logger.info(msg)
            except (ValueError, OSError) as e:
                msg = get_text('desktop_handler.error.removing_config', e=e)
                logger.error(msg)

            logger.info(get_text("desktop_handler.info.aborting_switch"))
            return False
        else:
            logger.info(get_text("desktop_handler.info.aborting_switch"))
            return False

    # Animation starten
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        animation_script = os.path.join(
            base_dir, '..', 'shared', 'animations', 'screen_fade.py'
        )

        if not os.path.exists(animation_script):
            logger.warning("Animationsskript nicht gefunden")
        else:
            subprocess.Popen(
                [sys.executable, animation_script],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(0.5)
    except (OSError, ValueError, FileNotFoundError) as e:
        logger.warning(f"Animation konnte nicht gestartet werden: {e}")

    # Eigentlicher Wechselprozess
    active_desktop = next((d for d in desktops if d.is_active), None)
    if active_desktop:
        msg = get_text("desktop_handler.info.saving_icons", name=active_desktop.name)
        logger.info(msg)
        try:
            active_desktop.icon_positionen = get_current_icon_positions(
                timeout_seconds=3
            )
            active_desktop.is_active = False
            save_desktops(desktops)
            msg = get_text('desktop_handler.success.db_update')
            logger.info(msg)
        except Exception as e:
            logger.warning(f"Icon-Speicherung fehlgeschlagen: {e}")
            active_desktop.is_active = False
            save_desktops(desktops)
    else:
        msg = get_text('desktop_handler.warn.no_active_desktop')
        logger.warning(msg)

    msg = get_text(
        "desktop_handler.info.switching_registry",
        name=target_desktop.name,
        path=target_desktop.path,
    )
    logger.info(msg)

    reg_success = True
    if not update_registry_key(
        KEY_USER_SHELL, VALUE_NAME, target_desktop.path, winreg.REG_EXPAND_SZ
    ):
        reg_success = False
    if not update_registry_key(
        KEY_LEGACY_SHELL, VALUE_NAME, target_desktop.path, winreg.REG_SZ
    ):
        reg_success = False

    if not reg_success:
        msg = get_text('desktop_handler.error.registry_update_failed')
        logger.error(msg)
        if active_desktop:
            active_desktop.is_active = True
            save_desktops(desktops)
        return False

    logger.info(get_text("desktop_handler.info.registry_success"))
    return True


def sync_desktop_state_and_apply_icons():
    """
    Führt die Aktionen *nach* dem Explorer-Neustart aus.
    """
    logger.info(get_text("desktop_handler.info.sync_after_restart"))

    desktops = get_all_desktops()
    new_active_desktop = next((d for d in desktops if d.is_active), None)

    if not new_active_desktop:
        msg = get_text('desktop_handler.error.sync_no_active')
        logger.error(msg)
        msg = get_text('desktop_handler.warn.sync_path_not_registered')
        logger.warning(msg)
        return

    msg = get_text("desktop_handler.info.sync_path_found", path=new_active_desktop.path)
    logger.info(msg)
    msg = get_text(
        "desktop_handler.info.sync_desktop_active", name=new_active_desktop.name
    )
    logger.info(msg)

    if new_active_desktop.wallpaper_path:
        logger.info(get_text("desktop_handler.info.setting_wallpaper"))
        wallpaper_service.set_wallpaper(new_active_desktop.wallpaper_path)

    msg = get_text(
        "desktop_handler.info.sync_restoring_icons", name=new_active_desktop.name
    )
    logger.info(msg)
    set_icon_positions(new_active_desktop.icon_positionen)
    logger.info(get_text("desktop_handler.info.sync_icons_done"))


def save_current_desktop_icons() -> bool:
    """
    Findet den aktuell aktiven Desktop, liest seine
    Icon-Positionen aus und speichert sie.
    """
    desktops = get_all_desktops()
    active_desktop = next((d for d in desktops if d.is_active), None)

    if not active_desktop:
        msg = get_text('desktop_handler.error.save_icons_no_active')
        logger.error(msg)
        msg = get_text('desktop_handler.warn.save_icons_not_registered')
        logger.warning(msg)
        return False

    try:
        msg = get_text("desktop_handler.info.reading_icons", name=active_desktop.name)
        logger.info(msg)
        active_desktop.icon_positionen = get_current_icon_positions()
        save_desktops(desktops)

        msg = get_text('desktop_handler.success.save_icons', name=active_desktop.name)
        logger.info(msg)
        return True
    except Exception as e:
        msg = get_text('desktop_handler.error.save_icons', e=e)
        logger.error(msg)
        return False


def assign_wallpaper(desktop_name: str, source_image_path: str) -> bool:
    """
    Weist einem Desktop ein Hintergrundbild zu.
    """
    if not os.path.exists(source_image_path):
        msg = get_text(
            'wallpaper_manager.error.source_not_found', path=source_image_path
        )
        logger.error(msg)
        return False

    desktops = get_all_desktops()
    target_desktop = next((d for d in desktops if d.name == desktop_name), None)

    if not target_desktop:
        msg = get_text('desktop_handler.error.not_found', old_name=desktop_name)
        logger.error(msg)
        return False

    # Altes Bild löschen
    if target_desktop.wallpaper_path and os.path.exists(target_desktop.wallpaper_path):
        try:
            os.remove(target_desktop.wallpaper_path)
            logger.info(get_text("desktop_handler.info.old_wallpaper_removed"))
        except Exception as e:
            msg = get_text('desktop_handler.warn.wallpaper_delete', e=e)
            logger.warning(msg)

    new_path = wallpaper_service.copy_wallpaper_to_datadir(
        source_image_path, target_desktop.name
    )

    if not new_path:
        return False

    target_desktop.wallpaper_path = new_path
    save_desktops(desktops)

    msg = get_text('desktop_handler.success.wallpaper_assigned', name=desktop_name)
    logger.info(msg)

    if target_desktop.is_active:
        logger.info(get_text("desktop_handler.info.setting_wallpaper_now"))
        wallpaper_service.set_wallpaper(new_path)

    return True