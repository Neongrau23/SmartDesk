"""
Windows-spezifische Hilfsfunktionen.
"""

import win32gui
import win32con
import logging
from ...shared.localization import get_text

# Logger einrichten
logger = logging.getLogger(__name__)


def ensure_taskbar_on_top():
    """
    Findet die Windows-Taskleiste und zwingt sie, über allen anderen
    Fenstern zu liegen (HWND_TOPMOST).
    """
    try:
        hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        if hwnd:
            # Setzt die Taskleiste an die Spitze der Z-Ordnung und gibt ihr den Fokus.
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetForegroundWindow(hwnd)
            logger.debug(get_text("win_utils.debug.taskbar_top", hwnd=hwnd))
            return True
        else:
            logger.warning(get_text("win_utils.warn.taskbar_not_found"))
            return False
    except Exception as e:
        logger.error(get_text("win_utils.error.top_failed", e=e))
        return False


def release_taskbar_from_top():
    """
    Setzt die Taskleiste in ihren normalen Zustand zurück (HWND_NOTOPMOST).
    """
    try:
        hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        if hwnd:
            # Entfernt das "TOPMOST"-Flag von der Taskleiste.
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            logger.debug(get_text("win_utils.debug.taskbar_released", hwnd=hwnd))
            return True
        else:
            logger.warning(get_text("win_utils.warn.taskbar_not_found"))
            return False
    except Exception as e:
        logger.error(get_text("win_utils.error.release_failed", e=e))
        return False


if __name__ == "__main__":
    import time

    logging.basicConfig(level=logging.DEBUG)
    logger.info("Teste: Taskleiste für 3 Sekunden in den Vordergrund zwingen...")
    if ensure_taskbar_on_top():
        time.sleep(3)
        logger.info("Teste: Taskleiste wieder freigeben...")
        release_taskbar_from_top()
        logger.info("Test abgeschlossen.")
    else:
        logger.error("Test fehlgeschlagen.")
