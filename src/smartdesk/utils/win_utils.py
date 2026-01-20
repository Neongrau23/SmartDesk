import win32gui
import win32process
import win32con
import logging

logger = logging.getLogger(__name__)

def activate_window_by_pid(pid):
    """
    Sucht das Hauptfenster eines Prozesses und bringt es in den Vordergrund.
    """
    def callback(hwnd, hwnds):
        try:
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                # Wir suchen nur sichtbare Fenster, die einen Titel haben (meist das Hauptfenster)
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    hwnds.append(hwnd)
        except Exception:
            pass
        return True

    hwnds = []
    try:
        win32gui.EnumWindows(callback, hwnds)
    except Exception as e:
        logger.error(f"Fehler bei EnumWindows: {e}")
        return False

    for hwnd in hwnds:
        try:
            # Falls minimiert, wiederherstellen
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # In den Vordergrund zwingen
            # Unter Windows 10/11 ist das manchmal blockiert. 
            # Ein Trick ist das Senden eines Hotkeys oder AttachThreadInput, aber SetForegroundWindow ist der erste Schritt.
            try:
                win32gui.SetForegroundWindow(hwnd)
            except Exception as e:
                logger.warning(f"Konnte Fenster nicht in den Vordergrund setzen (Windows Restriction): {e}")
                # Fallback: Flash Window?
                pass
                
            return True
        except Exception as e:
            logger.error(f"Fehler beim Aktivieren des Fensters: {e}")
    
    return False
