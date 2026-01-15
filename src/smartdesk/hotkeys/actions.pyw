import time
import sys
import os
import traceback

# --- 1. Deine Handler importieren ---
try:
    from ..core.services import desktop_service as desktop_handler
    from ..core.services import system_service as system_manager
    from ..shared.localization import get_text
    from ..shared.style import PREFIX_OK, PREFIX_ERROR
    from ..shared.config import DATA_DIR
except ImportError as e:
    # Fallback, falls Imports fehlschlagen
    PREFIX_ERROR = "[FEHLER]"
    PREFIX_OK = "[OK]"
    print(f"{PREFIX_ERROR} Kritischer Fehler in hotkeys/actions.py: {e}")
    
    # Versuche DATA_DIR zu erraten, falls Import fehlgeschlagen
    try:
        DATA_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except:
        DATA_DIR = "."

    class FakeHandler:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                print(f"{PREFIX_ERROR} Handler nicht geladen. Aktion '{name}' kann nicht ausgeführt werden.")
            return method

    desktop_handler = FakeHandler()
    system_manager = FakeHandler()

    def get_text(key, **kwargs):
        return key


# --- 2. Hilfsfunktionen ---

def _switch_to_desktop_by_index(desktop_index: int):
    """
    Holt alle Desktops, wählt einen anhand des Index (0=erster, 1=zweiter, ...)
    und wechselt zu ihm, inklusive Explorer-Neustart.
    """
    log_file = os.path.join(DATA_DIR, 'actions.log')

    try:
        with open(log_file, 'a', encoding='utf-8') as log:
            # Wir leiten stdout/stderr nur um, wenn wir wirklich loggen wollen.
            # Aber Vorsicht: Wenn das hier abstürzt, bleibt stdout umgeleitet.
            # Besser: explizit in log schreiben.
            
            log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] --- Switching to desktop {desktop_index} ---
")
            
            # 1. Alle Desktops laden
            try:
                desktops = desktop_handler.get_all_desktops()
            except Exception as e:
                log.write(f"Error getting desktops: {e}\n")
                return

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
                    try:
                        system_manager.restart_explorer()
                        log.write("Restarted explorer.\n")
                    except Exception as e:
                        log.write(f"Error restarting explorer: {e}\n")
                    
                    time.sleep(0.5)
                    
                    try:
                        desktop_handler.sync_desktop_state_and_apply_icons()
                        log.write("Synced desktop state and applied icons.\n")
                    except Exception as e:
                        log.write(f"Error syncing state: {e}\n")
            else:
                log.write(f"Invalid desktop index: {desktop_index}\n")

    except Exception as e:
        # Fallback logging to stderr if file fails
        sys.stderr.write(f"Error in _switch_to_desktop_by_index: {e}\n")


def _save_icons():
    """Speichert die aktuellen Icon-Positionen."""
    log_file = os.path.join(DATA_DIR, 'actions.log')

    try:
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] --- Saving icons ---
")
            try:
                desktop_handler.save_current_desktop_icons()
                log.write("Saved icons successfully.\n")
            except Exception as e:
                log.write(f"Error saving icons: {e}\n")
                log.write(traceback.format_exc())
    except Exception as e:
        sys.stderr.write(f"Error in _save_icons: {e}\n")


# --- 3. Zentrale Aktions-Definitionen ---

def aktion_alt_1(): _switch_to_desktop_by_index(0)
def aktion_alt_2(): _switch_to_desktop_by_index(1)
def aktion_alt_3(): _switch_to_desktop_by_index(2)
def aktion_alt_4(): _switch_to_desktop_by_index(3)
def aktion_alt_5(): _switch_to_desktop_by_index(4)
def aktion_alt_6(): _switch_to_desktop_by_index(5)
def aktion_alt_7(): _switch_to_desktop_by_index(6)
def aktion_alt_8(): _switch_to_desktop_by_index(7)
def aktion_alt_9(): _save_icons()