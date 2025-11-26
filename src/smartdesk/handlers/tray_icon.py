"""
Statusanzeige mit eigenen Icon-Dateien
Benötigt: pip install pystray pillow
"""

# --- NEUER CODE-BLOCK START ---
import sys
import os

try:
    # 1. Finde den Pfad zur Datei: ...\src\smartdesk\handlers\tray_icon.py
    current_file_path = os.path.abspath(__file__)
    # 2. Gehe zum 'handlers'-Ordner: ...\src\smartdesk\handlers
    handlers_dir = os.path.dirname(current_file_path)
    # 3. Gehe zum 'smartdesk'-Ordner: ...\src\smartdesk
    smartdesk_dir = os.path.dirname(handlers_dir)
    # 4. Gehe zum 'src'-Ordner: ...\src
    src_dir = os.path.dirname(smartdesk_dir)

    # 5. Füge den 'src'-Ordner zum Python-Pfad hinzu
    if src_dir not in sys.path:
        sys.path.append(src_dir)
        print(f"[DEBUG] 'src' Verzeichnis zum Pfad hinzugefügt: {src_dir}")
except Exception as e:
    print(f"[DEBUG] FEHLER im Path Hack: {e}")
    # Beende sofort, wenn der Pfad nicht gesetzt werden kann
    sys.exit(1)
# --- KORRIGIERTER PATH HACK ENDE ---


# Alle anderen Importe kommen erst DANACH
import pystray
from PIL import Image
import threading
import time
from smartdesk.hotkeys import hotkey_manager
import subprocess

# --- NEU: Definition des PID-Datei-Pfads ---
try:
    # Stellt sicher, dass der Pfad benutzerunabhängig ist
    PID_FILE_DIR = os.path.join(os.environ['APPDATA'], 'SmartDesk')
    PID_FILE_PATH = os.path.join(PID_FILE_DIR, 'listener.pid')
    print(f"[DEBUG] Überwache PID-Datei: {PID_FILE_PATH}")
except Exception as e:
    print(f"[DEBUG] FEHLER: Konnte APPDATA-Pfad nicht finden: {e}")
    PID_FILE_PATH = None


def load_icon(filepath):
    """Lädt ein Icon aus einer Datei"""
    print(f"[DEBUG] Versuche Icon zu laden: {filepath}")
    try:
        if os.path.exists(filepath):
            print(f"[DEBUG] Datei gefunden: {filepath}")
            image = Image.open(filepath)
            image = image.resize((64, 64), Image.Resampling.LANCZOS)
            print("[DEBUG] Icon erfolgreich geladen und skaliert")
            return image
        else:
            print(f"[DEBUG] FEHLER - Datei nicht gefunden: {filepath}")
            return create_fallback_icon()
    except Exception as e:
        print(f"[DEBUG] FEHLER beim Laden: {e}")
        return create_fallback_icon()


def create_fallback_icon(color="gray"):
    """Fallback wenn Datei nicht gefunden wird"""
    image = Image.new('RGB', (64, 64), color)
    return image


class StatusMonitor:
    def __init__(self, active_icon_path, idle_icon_path):
        self.is_active = False
        self.active_icon = load_icon(active_icon_path)
        self.idle_icon = load_icon(idle_icon_path)
        
    def set_active(self):
        self.is_active = True
        
    def set_idle(self):
        self.is_active = False
            
    def get_current_icon(self):
        return self.active_icon if self.is_active else self.idle_icon


ACTIVE_ICON = r"C:\Users\leonp\AppData\Roaming\SmartDesk\ico\activ_icon.png"
IDLE_ICON = r"C:\Users\leonp\AppData\Roaming\SmartDesk\ico\idle_icon.png"

status = StatusMonitor(ACTIVE_ICON, IDLE_ICON)


def update_icon(icon):
    """Aktualisiert das Icon basierend auf der Existenz der listener.pid"""
    print("[DEBUG] Update-Thread (PID-Überwachung) gestartet")

    if not PID_FILE_PATH:
        print("[DEBUG] FEHLER: PID_FILE_PATH ist nicht gesetzt.")
        return

    while True:
        try:
            old_state = status.is_active
            
            if os.path.exists(PID_FILE_PATH):
                status.set_active()
            else:
                status.set_idle()
                
            icon.icon = status.get_current_icon()
            
            if status.is_active:
                icon.title = "SmartDesk (Aktiv)"
            else:
                icon.title = "SmartDesk (Inaktiv)"
            
            if old_state != status.is_active:
                new_status = "AKTIV" if status.is_active else "INAKTIV"
                print(f"[DEBUG] Status geändert: {new_status}")
        
        except Exception as e:
            print(f"[DEBUG] FEHLER im Update-Thread: {e}")
            
        time.sleep(1)


def create_desktop(icon, item):
    print("[DEBUG] 'Desktop Erstellen' geklickt.")
    try:
        smartdesk_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_py = os.path.join(smartdesk_dir, 'main.py')
        
        subprocess.Popen(
            ['powershell', '-NoExit', '-Command', f'python "{main_py}" create'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        print(f"[DEBUG] FEHLER beim Erstellen: {e}")


def set_active(icon, item):
    print("[DEBUG] 'Aktivieren' geklickt.")
    hotkey_manager.start_listener()


def set_inactiv(icon, item):
    print("[DEBUG] 'Deaktivieren' geklickt.")
    hotkey_manager.stop_listener()


def on_primary_click(icon, item):
    print("[DEBUG] Primär-Klick erkannt.")


def open_smart_desk(icon, item):
    print("[DEBUG] 'SmartDesk Öffnen' geklickt")
    try:
        smartdesk_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_py = os.path.join(smartdesk_dir, 'main.py')
        
        subprocess.Popen(
            ['powershell', '-NoExit', '-Command', f'python "{main_py}"'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        print(f"[DEBUG] FEHLER beim Öffnen: {e}")


def stop_smartdesk(icon, item):
    print("[DEBUG] 'Beenden' geklickt.")
    
    try:
        from smartdesk.utils.registry_operations import cleanup_tray_pid
        cleanup_tray_pid()
        print("[DEBUG] Tray-PID aus Registry entfernt")
    except Exception as e:
        print(f"[DEBUG] Fehler beim Cleanup: {e}")
    
    icon.stop()


icon = pystray.Icon(
    "status_indicator",
    status.get_current_icon(),
    "○ Bereit",
    menu=pystray.Menu(
        pystray.MenuItem(
            "Primary Action",
            on_primary_click,
            default=True,
            visible=False
        ),
        pystray.MenuItem("SmartDesk Öffnen", open_smart_desk), 
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Desktop Erstellen", create_desktop),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Aktivieren", set_active),
        pystray.MenuItem("Deaktivieren", set_inactiv),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Beenden", stop_smartdesk)
    ),
)

update_thread = threading.Thread(target=update_icon, args=(icon,), daemon=True)
update_thread.start()

print("[DEBUG] Starte Tray-Icon...")
icon.run()
