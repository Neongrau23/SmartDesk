import time

# --- 1. Deine Handler importieren ---
# Wir verwenden relative Imports (..), um aus dem 'hotkeys'-Ordner
# eine Ebene nach oben ('smartdesk') und dann in die neue Struktur zu gelangen.
try:
    from ..core.services import desktop_service as desktop_handler
    from ..core.services import system_service as system_manager
    from ..shared.localization import get_text
    from ..shared.style import PREFIX_OK, PREFIX_ERROR

    # Kommentar: Hotkey-Aktionen geladen (kein print, da unsichtbar)

except ImportError as e:
    # PREFIX_ERROR muss vor der Verwendung definiert werden
    PREFIX_ERROR = "[FEHLER]"
    PREFIX_OK = "[OK]"
    print(f"{PREFIX_ERROR} Kritischer Fehler in hotkeys/actions.py: {e}")
    print(f"{PREFIX_ERROR} Konnte die SmartDesk-Handler nicht finden.")

    # Definiere Dummy-Funktionen, damit der Listener nicht abstürzt

    class FakeHandler:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                print(
                    f"{PREFIX_ERROR} Handler nicht geladen. Aktion '{name}' kann nicht ausgeführt werden."
                )

            return method

    desktop_handler = FakeHandler()
    system_manager = FakeHandler()

    def get_text(key, **kwargs):
        return key


# --- 2. Hilfsfunktionen ---
# Diese Funktion kapselt die Logik aus deiner cli.py


def _switch_to_desktop_by_index(desktop_index: int):
    """
    Holt alle Desktops, wählt einen anhand des Index (0=erster, 1=zweiter, ...)
    und wechselt zu ihm, inklusive Explorer-Neustart.
    """
    import sys
    import os
    import traceback
    log_file = os.path.join(r'C:\Users\leonp\.gemini\tmp\4b9b30c558e150c7ad00633726cd40cd860454fcba01690f0a0481ff9b34e30e', 'actions.log')

    try:
        with open(log_file, 'a', encoding='utf-8') as log:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = log
            sys.stderr = log

            try:
                log.write(f"--- Switching to desktop {desktop_index} ---\n")
                # 1. Alle Desktops laden
                desktops = desktop_handler.get_all_desktops()
                log.write(f"Found {len(desktops)} desktops.\n")

                if not desktops:
                    return

                # 2. Prüfen, ob der Index gültig ist
                if 0 <= desktop_index < len(desktops):
                    target_desktop = desktops[desktop_index]
                    log.write(f"Target desktop: {target_desktop.name}\n")

                    # 3. Zum Desktop wechseln
                    if desktop_handler.switch_to_desktop(target_desktop.name):
                        log.write("Switched to desktop successfully.\n")
                        system_manager.restart_explorer()
                        log.write("Restarted explorer.\n")
                        time.sleep(0.5)
                        desktop_handler.sync_desktop_state_and_apply_icons()
                        log.write("Synced desktop state and applied icons.\n")
            finally:
                # Stelle stdout/stderr wieder her
                sys.stdout = old_stdout
                sys.stderr = old_stderr
    except Exception as e:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Error in _switch_to_desktop_by_index: {e}\n")
            log.write(traceback.format_exc())
            log.write("\n")


def _save_icons():
    """Speichert die aktuellen Icon-Positionen."""
    import sys
    import os
    import traceback
    log_file = os.path.join(r'C:\Users\leonp\.gemini\tmp\4b9b30c558e150c7ad00633726cd40cd860454fcba01690f0a0481ff9b34e30e', 'actions.log')

    try:
        with open(log_file, 'a', encoding='utf-8') as log:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = log
            sys.stderr = log
            try:
                log.write("--- Saving icons ---\n")
                desktop_handler.save_current_desktop_icons()
                log.write("Saved icons successfully.\n")
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
    except Exception as e:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Error in _save_icons: {e}\n")
            log.write(traceback.format_exc())
            log.write("\n")


# --- 3. Zentrale Aktions-Definitionen (Die "Übersetzung") ---
# Diese Funktionen werden vom listener.py aufgerufen.
# BEARBEITE DIESE, UM DIE AKTIONEN ZU ÄNDERN.


def aktion_alt_1():
    _switch_to_desktop_by_index(0)


def aktion_alt_2():
    _switch_to_desktop_by_index(1)


def aktion_alt_3():
    _switch_to_desktop_by_index(2)


def aktion_alt_4():
    _switch_to_desktop_by_index(3)


def aktion_alt_5():
    _switch_to_desktop_by_index(4)


def aktion_alt_6():
    _switch_to_desktop_by_index(5)


def aktion_alt_7():
    _switch_to_desktop_by_index(6)


def aktion_alt_8():
    _switch_to_desktop_by_index(7)


def aktion_alt_9():
    _save_icons()
