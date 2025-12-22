# Dateipfad: src/smartdesk/interfaces/cli/cli.py
# Vollständiges CLI-Interface für SmartDesk

import os
import platform
import time
import subprocess

from ...shared.logging_config import get_logger

logger = get_logger(__name__)

try:
    from ...core.services import desktop_service
    from ...core.services import system_service
    from ...hotkeys import hotkey_manager
    from ..tray import tray_manager
    from ..gui.ui_manager import launch_create_desktop_dialog
    from ...shared.config import DATA_DIR
    from ...shared.style import (
        PREFIX_ERROR,
        PREFIX_OK,
        PREFIX_WARN,
        format_status_active,
        format_status_inactive,
    )
    from ...shared.localization import get_text
except ImportError as e:
    logger.error(f"FATALER IMPORT FEHLER in cli.py: {e}")
    logger.info(
        "Stelle sicher, dass du das Skript mit 'python -m smartdesk.main' startest."
    )

    class FakeHandler:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                logger.error(f"{name} konnte nicht geladen werden!")

            return method

    desktop_service = FakeHandler()
    system_service = FakeHandler()
    hotkey_manager = FakeHandler()
    tray_manager = FakeHandler()

    def get_text(key, **kwargs):
        return key

    PREFIX_ERROR = "ERROR:"
    PREFIX_OK = "OK:"
    PREFIX_WARN = "WARN:"
    DATA_DIR = os.path.join(os.environ.get('APPDATA', '.'), 'SmartDesk')

    def format_status_active(t):
        return f"[{t}]"

    def format_status_inactive(t):
        return f"[{t}]"

    def launch_create_desktop_dialog():
        logger.error("GUI-Manager konnte nicht geladen werden.")
        return None


def clear_screen():
    """Löscht den Terminal-Bildschirm."""
    system_name = platform.system()
    if system_name == "Windows":
        os.system('cls')
    else:
        os.system('clear')


def print_main_menu():
    """Zeigt das Hauptmenü an."""
    print(get_text("logo.ascii"))
    print(get_text("ui.menu.main.separator"))
    print(f"1. {get_text('ui.menu.main.switch')}")
    print(f"2. {get_text('ui.menu.main.create')}")
    print(f"3. {get_text('ui.menu.main.settings')}")
    print(f"0. {get_text('ui.menu.main.exit')}")


def print_settings_menu():
    """Zeigt das Einstellungs-Untermenü an."""
    print(get_text("ui.menu.settings.header"))
    print(get_text("ui.menu.main.separator"))
    print(f"1. {get_text('ui.menu.settings.list')}")
    print(f"2. {get_text('ui.menu.settings.delete')}")
    print(f"3. {get_text('ui.menu.settings.save_icons')}")
    print(f"4. {get_text('ui.menu.settings.wallpaper')}")
    print(f"5. {get_text('ui.menu.settings.restart')}")
    print(f"6. {get_text('ui.menu.settings.hotkeys')}")
    print(f"7. {get_text('ui.menu.settings.tray')}")
    print(f"8. {get_text('ui.menu.settings.restore_registry')}")
    print(f"0. {get_text('ui.menu.settings.back')}")


def run_hotkey_menu():
    """Verwaltet das Hotkey-Listener Untermenü."""
    while True:
        clear_screen()
        print(get_text("ui.headings.hotkeys"))

        pid = hotkey_manager.get_listener_pid()

        if pid:
            status = format_status_active(get_text('ui.status.hotkeys_on'))
            print(f"{get_text('ui.status.hotkeys_status')} {status} (PID: {pid})")
        else:
            status = format_status_inactive(get_text('ui.status.hotkeys_off'))
            print(f"{get_text('ui.status.hotkeys_status')} {status}")

        print(get_text("ui.menu.main.separator"))
        print(get_text("ui.menu.hotkeys.manage"))
        print(get_text("ui.menu.hotkeys.debug"))
        print(f"0. {get_text('ui.menu.settings.back')}")

        choice = input(get_text("ui.prompts.choose")).strip()

        if choice == "1":
            clear_screen()
            print(get_text("ui.headings.hotkeys_manage"))

            pid = hotkey_manager.get_listener_pid()
            if pid:
                status = format_status_active(get_text('ui.status.hotkeys_on'))
                print(f"{get_text('ui.status.hotkeys_status')} {status} (PID: {pid})")
            else:
                status = format_status_inactive(get_text('ui.status.hotkeys_off'))
                print(f"{get_text('ui.status.hotkeys_status')} {status}")

            print(get_text("ui.menu.main.separator"))
            print(get_text("ui.prompts.hotkeys.start"))
            print(get_text("ui.prompts.hotkeys.stop"))
            print(get_text("ui.prompts.cancel"))

            sub_choice = input(get_text("ui.prompts.choose")).strip()

            if sub_choice == "1":
                hotkey_manager.start_listener()
            elif sub_choice == "2":
                hotkey_manager.stop_listener()

            if sub_choice in ["1", "2"]:
                input(get_text("ui.prompts.continue"))

        elif choice == "2":
            clear_screen()
            print(get_text("ui.headings.hotkeys_debug"))
            print(get_text("ui.menu.main.separator"))

            log_file = os.path.join(DATA_DIR, "listener.log")

            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        last_lines = lines[-20:] if len(lines) > 20 else lines

                        if last_lines:
                            for line in last_lines:
                                print(line.rstrip())
                        else:
                            print(get_text("ui.messages.log_empty"))
                except Exception as e:
                    print(
                        f"{PREFIX_ERROR} {get_text('ui.errors.log_read_failed', e=e)}"
                    )
            else:
                print(get_text("ui.messages.log_not_found"))
                print(f"({get_text('ui.messages.path_was')}: {log_file})")

            input(get_text("ui.prompts.continue"))

        elif choice == "0":
            break
        else:
            print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_input')}")
            time.sleep(1.5)


def run_tray_menu():
    """Verwaltet das Tray-Icon Untermenü."""
    while True:
        clear_screen()
        print(get_text("ui.headings.tray"))

        is_running, pid = tray_manager.get_tray_status()

        if is_running:
            status = format_status_active(get_text('ui.status.tray_on'))
            print(f"{get_text('ui.status.tray_status')} {status} (PID: {pid})")
        else:
            status = format_status_inactive(get_text('ui.status.tray_off'))
            print(f"{get_text('ui.status.tray_status')} {status}")

        print(get_text("ui.menu.main.separator"))
        print(get_text("ui.menu.tray.manage"))
        print(f"0. {get_text('ui.menu.settings.back')}")

        choice = input(get_text("ui.prompts.choose")).strip()

        if choice == "1":
            clear_screen()
            print(get_text("ui.headings.tray_manage"))

            is_running, pid = tray_manager.get_tray_status()
            if is_running:
                status = format_status_active(get_text('ui.status.tray_on'))
                print(f"{get_text('ui.status.tray_status')} {status} (PID: {pid})")
            else:
                status = format_status_inactive(get_text('ui.status.tray_off'))
                print(f"{get_text('ui.status.tray_status')} {status}")

            print(get_text("ui.menu.main.separator"))
            print(get_text("ui.prompts.tray.start"))
            print(get_text("ui.prompts.tray.stop"))
            print(get_text("ui.prompts.cancel"))

            sub_choice = input(get_text("ui.prompts.choose")).strip()

            if sub_choice == "1":
                tray_manager.start_tray()
            elif sub_choice == "2":
                tray_manager.stop_tray()

            if sub_choice in ["1", "2"]:
                input(get_text("ui.prompts.continue"))

        elif choice == "0":
            break
        else:
            print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_input')}")
            time.sleep(1.5)


def run_restore_registry():
    """Führt das Restore-Skript aus."""
    clear_screen()
    print(get_text("ui.headings.restore_registry"))

    if platform.system() != "Windows":
        print(f"{PREFIX_ERROR} {get_text('ui.errors.not_windows')}")
        input(get_text("ui.prompts.continue"))
        return

    script_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..', 'scripts', 'restore.bat'
        )
    )

    if not os.path.exists(script_path):
        msg = get_text('ui.errors.path_not_found', path=script_path)
        print(f"{PREFIX_ERROR} {msg}")
        input(get_text("ui.prompts.continue"))
        return

    print(get_text('ui.messages.running_restore'))
    try:
        subprocess.call(['cmd', '/c', script_path])
        print(get_text('ui.messages.restore_finished'))
    except Exception as e:
        msg = get_text('ui.errors.restore_failed', e=e)
        print(f"{PREFIX_ERROR} {msg}")

    input(get_text("ui.prompts.continue"))


def run_settings_menu():
    """Verwaltet die Schleife für das Einstellungsmenü."""
    while True:
        clear_screen()
        print_settings_menu()
        choice = input(get_text("ui.prompts.choose")).strip()

        if choice == "1":
            clear_screen()
            desktops = desktop_service.get_all_desktops()
            if not desktops:
                print(get_text("ui.messages.no_desktops"))
            else:
                print(get_text("main.info.list_header"))
                for d in desktops:
                    if d.is_active:
                        status = format_status_active(get_text("ui.status.active"))
                    else:
                        status = format_status_inactive(get_text("ui.status.inactive"))

                    wallpaper_info = ""
                    if hasattr(d, 'wallpaper_path') and d.wallpaper_path:
                        wallpaper_info = (
                            f" ({get_text('ui.status.wallpaper')}: "
                            f"{os.path.basename(d.wallpaper_path)})"
                        )

                    print(f"{status} {d.name} -> {d.path}{wallpaper_info}")

            input(get_text("ui.prompts.continue"))

        elif choice == "2":
            clear_screen()
            print(get_text("ui.headings.delete"))
            desktops = desktop_service.get_all_desktops()

            if not desktops:
                print(get_text("ui.messages.no_desktops"))
                input(get_text("ui.prompts.continue"))
                continue

            print(get_text("ui.headings.which_desktop_delete"))
            for i, d in enumerate(desktops, 1):
                if d.is_active:
                    status = format_status_active(get_text("ui.status.active"))
                else:
                    status = format_status_inactive(get_text("ui.status.inactive"))
                print(f"{i}. {status} {d.name} ({d.path})")

            print(f"\n0. {get_text('ui.prompts.cancel')}")
            selection = input(get_text("ui.prompts.choose_number")).strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1

                if 0 <= index < len(desktops):
                    target_desktop = desktops[index]

                    if target_desktop.is_active:
                        msg = get_text(
                            'desktop_handler.error.delete_active',
                            name=target_desktop.name,
                        )
                        print(f"{PREFIX_ERROR} {msg}")
                        input(get_text("ui.prompts.continue"))
                        continue

                    delete_folder_confirm = (
                        input(
                            get_text(
                                "ui.prompts.delete_folder_confirm",
                                path=target_desktop.path,
                            )
                        )
                        .strip()
                        .lower()
                    )
                    delete_folder = delete_folder_confirm == 'y'

                    desktop_service.delete_desktop(
                        target_desktop.name, delete_folder=delete_folder
                    )
                else:
                    print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            except ValueError:
                print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            input(get_text("ui.prompts.continue"))

        elif choice == "3":
            clear_screen()
            print(get_text("desktop_handler.info.reading_icons", name="..."))
            desktop_service.save_current_desktop_icons()
            input(get_text("ui.prompts.continue"))

        elif choice == "4":
            clear_screen()
            print(get_text("ui.headings.wallpaper"))
            desktops = desktop_service.get_all_desktops()

            if not desktops:
                print(get_text("ui.messages.no_desktops"))
                input(get_text("ui.prompts.continue"))
                continue

            print(get_text("ui.headings.which_desktop_wallpaper"))
            for i, d in enumerate(desktops, 1):
                status = format_status_inactive("")
                if d.is_active:
                    status = format_status_active(get_text("ui.status.active_short"))

                wallpaper_info = f" ({get_text('ui.status.wallpaper_none')})"
                if hasattr(d, 'wallpaper_path') and d.wallpaper_path:
                    wallpaper_info = (
                        f" ({get_text('ui.status.wallpaper')}: "
                        f"{os.path.basename(d.wallpaper_path)})"
                    )

                print(f"{i}. {status} {d.name}{wallpaper_info}")

            print(f"\n0. {get_text('ui.prompts.cancel')}")
            selection = input(get_text("ui.prompts.choose_number")).strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1
                if not (0 <= index < len(desktops)):
                    print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
                    input(get_text("ui.prompts.continue"))
                    continue

                target_desktop = desktops[index]
                source_path = input(get_text("ui.prompts.wallpaper_path")).strip()

                if not source_path:
                    print(get_text("ui.messages.aborted_no_path"))
                    input(get_text("ui.prompts.continue"))
                    continue

                source_path = source_path.strip('"')
                desktop_service.assign_wallpaper(target_desktop.name, source_path)

            except ValueError:
                print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")

            input(get_text("ui.prompts.continue"))

        elif choice == "5":
            clear_screen()
            system_service.restart_explorer()
            input(get_text("ui.prompts.continue"))

        elif choice == "6":
            run_hotkey_menu()

        elif choice == "7":
            run_tray_menu()

        elif choice == "8":
            run_restore_registry()

        elif choice == "0":
            break
        else:
            print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_input')}")
            time.sleep(1.5)


def run_create_desktop_menu():
    """Führt direkt den Dialog zum Erstellen eines neuen Desktops aus."""
    clear_screen()
    print(get_text("ui.headings.create"))
    name = input(get_text("ui.prompts.desktop_name")).strip()

    if not name:
        print(f"{PREFIX_ERROR} {get_text('ui.errors.name_empty')}")
        input(get_text("ui.prompts.continue"))
        return

    print(get_text("ui.prompts.folder_mode"))
    print(get_text("ui.prompts.folder_mode_1"))
    print(get_text("ui.prompts.folder_mode_2"))

    mode = input(get_text("ui.prompts.choose_1_or_2")).strip()

    if mode == "1":
        final_path_input = (
            input(get_text("ui.prompts.existing_path")).strip().strip('"')
        )
        if final_path_input:
            final_path = os.path.normpath(final_path_input)
            desktop_service.create_desktop(name, final_path, create_if_missing=False)
        else:
            print(get_text("ui.messages.aborted_no_path"))

    elif mode == "2":
        while True:
            parent_path_input = (
                input(get_text("ui.prompts.new_path_parent")).strip().strip('"')
            )

            if not parent_path_input:
                print(get_text("ui.messages.aborted_no_path"))
                break

            parent_path = os.path.normpath(parent_path_input)

            if not os.path.isabs(parent_path):
                msg = get_text('ui.errors.path_not_absolute', path=parent_path)
                print(f"{PREFIX_ERROR} {msg}")
                print(get_text("ui.prompts.path_error_menu.title"))
                print(get_text("ui.prompts.path_error_menu.abort"))
                sub_choice = input(get_text("ui.prompts.choose")).strip()
                if sub_choice == "2":
                    break
                else:
                    continue

            try:
                drive, _ = os.path.splitdrive(parent_path)
                if drive and not os.path.exists(drive):
                    msg = get_text(
                        'desktop_handler.error.path_invalid', path=parent_path
                    )
                    print(f"{PREFIX_ERROR} {msg}")
                    print(get_text("ui.prompts.path_error_menu.title"))
                    print(get_text("ui.prompts.path_error_menu.abort"))
                    sub_choice = input(get_text("ui.prompts.choose")).strip()
                    if sub_choice == "2":
                        break
                    else:
                        continue
            except Exception:
                msg = get_text('desktop_handler.error.path_invalid', path=parent_path)
                print(f"{PREFIX_ERROR} {msg}")
                print(get_text("ui.prompts.path_error_menu.title"))
                print(get_text("ui.prompts.path_error_menu.abort"))
                sub_choice = input(get_text("ui.prompts.choose")).strip()
                if sub_choice == "2":
                    break
                else:
                    continue

            if os.path.exists(parent_path) and os.path.isdir(parent_path):
                final_path = os.path.join(parent_path, name)
                msg = get_text("ui.messages.new_path_location", path=final_path)
                print(msg)
                desktop_service.create_desktop(name, final_path, create_if_missing=True)
                break
            else:
                msg = get_text('ui.prompts.parent_dir_menu.not_found', path=parent_path)
                print(f"{PREFIX_WARN} {msg}")
                print(get_text("ui.prompts.parent_dir_menu.title"))
                print(get_text("ui.prompts.parent_dir_menu.create", path=parent_path))
                print(get_text("ui.prompts.parent_dir_menu.reenter"))
                print(get_text("ui.prompts.parent_dir_menu.abort"))

                sub_choice = input(get_text("ui.prompts.choose")).strip()

                if sub_choice == "1":
                    try:
                        os.makedirs(parent_path)
                        msg = get_text('ui.messages.parent_created', path=parent_path)
                        print(f"{PREFIX_OK} {msg}")
                        final_path = os.path.join(parent_path, name)
                        msg = get_text("ui.messages.new_path_location", path=final_path)
                        print(msg)
                        desktop_service.create_desktop(
                            name, final_path, create_if_missing=True
                        )
                        break
                    except Exception as e:
                        msg = get_text(
                            'desktop_handler.error.path_invalid', path=parent_path
                        )
                        print(f"{PREFIX_ERROR} {msg}")
                        input(get_text("ui.prompts.continue"))
                        continue
                elif sub_choice == "2":
                    continue
                else:
                    print(get_text("ui.messages.aborted_no_path"))
                    break
    else:
        print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_choice')}")

    input(get_text("ui.prompts.continue"))


def run_create_desktop_gui():
    """Führt den GUI-Dialog zum Erstellen eines neuen Desktops aus."""
    result_data = launch_create_desktop_dialog()

    if result_data is None:
        return

    name = result_data["name"]
    path = result_data["path"]
    create_if_missing = result_data["create_if_missing"]

    desktop_service.create_desktop(name, path, create_if_missing)


def run():
    """Verwaltet die Schleife für das Hauptmenü."""
    while True:
        clear_screen()
        print_main_menu()
        choice = input(get_text("ui.prompts.choose")).strip()

        if choice == "1":
            clear_screen()
            desktops = desktop_service.get_all_desktops()

            if not desktops:
                print(get_text("ui.messages.no_desktops_create_first"))
                input(get_text("ui.prompts.continue"))
                continue

            print(get_text("ui.headings.which_desktop_switch"))
            for i, d in enumerate(desktops, 1):
                if d.is_active:
                    status = format_status_active(get_text("ui.status.active"))
                else:
                    status = format_status_inactive(get_text("ui.status.inactive"))
                print(f"{i}. {status} {d.name} ({d.path})")

            print(f"\n0. {get_text('ui.prompts.cancel')}")
            selection = input(get_text("ui.prompts.choose_number")).strip()

            if selection == "0":
                continue

            try:
                index = int(selection) - 1

                if 0 <= index < len(desktops):
                    target_desktop = desktops[index]

                    if desktop_service.switch_to_desktop(target_desktop.name):
                        msg = get_text(
                            "ui.messages.registry_set_success", name=target_desktop.name
                        )
                        print(msg)
                        print(get_text("ui.messages.restarting_explorer"))
                        system_service.restart_explorer()

                        print(get_text("ui.messages.waiting_for_explorer"))

                        SIGNAL_FILE_PATH = os.path.join(DATA_DIR, "fade_signal.lock")
                        try:
                            with open(SIGNAL_FILE_PATH, "w") as f:
                                f.write("done")
                        except Exception as e:
                            print(f"{PREFIX_WARN} Signaldatei Fehler: {e}")

                        print(get_text("ui.messages.syncing_icons"))
                        desktop_service.sync_desktop_state_and_apply_icons()

                        msg = get_text(
                            'ui.messages.switch_success', name=target_desktop.name
                        )
                        print(f"{PREFIX_OK} {msg}")
                else:
                    print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            except ValueError:
                print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_number')}")
            input(get_text("ui.prompts.continue"))

        elif choice == "2":
            run_create_desktop_menu()

        elif choice == "3":
            run_settings_menu()

        elif choice == "0":
            print(get_text("ui.messages.exit"))
            break
        else:
            print(f"{PREFIX_ERROR} {get_text('ui.errors.invalid_input')}")
            time.sleep(1.5)


if __name__ == "__main__":
    clear_screen()
    run()
