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

    try:
        # Unterdrücke alle Ausgaben (auch von desktop_handler)
        devnull = open(os.devnull, 'w', encoding='utf-8')
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull

        try:
            # 1. Alle Desktops laden
            desktops = desktop_handler.get_all_desktops()

            if not desktops:
                return

            # 2. Prüfen, ob der Index gültig ist
            if 0 <= desktop_index < len(desktops):
                target_desktop = desktops[desktop_index]

                # 3. Zum Desktop wechseln
                if desktop_handler.switch_to_desktop(target_desktop.name):
                    system_manager.restart_explorer()
                    time.sleep(0.5)
                    desktop_handler.sync_desktop_state_and_apply_icons()
        finally:
            # Stelle stdout/stderr wieder her
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
    except Exception:
        # Fehler ignorieren, um Listener nicht zu crashen
        pass


def _save_icons():
    """Speichert die aktuellen Icon-Positionen."""
    import sys
    import os

    try:
        # Unterdrücke alle Ausgaben
        devnull = open(os.devnull, 'w', encoding='utf-8')
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull

        try:
            desktop_handler.save_current_desktop_icons()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
    except Exception:
        pass


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
