import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
import threading
import time
import logging

# --- Pfad-Hack für direkten Aufruf ---
if __name__ == "__main__" or __package__ is None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    interfaces_dir = os.path.dirname(current_dir)
    smartdesk_dir = os.path.dirname(interfaces_dir)
    src_dir = os.path.dirname(smartdesk_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

# --- Logger Setup ---
try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback: Standard-Logger
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

# --- Abgerundete Ecken (nur Windows) ---
try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    logger.info("Hinweis: 'pywin32' nicht gefunden. Ecken werden nicht abgerundet.")

# --- Projekt-Imports ---
try:
    from smartdesk.core.services import desktop_service
    from smartdesk.shared.localization import get_text
    from smartdesk.hotkeys import hotkey_manager
    desktop_handler = desktop_service
except ImportError as e:
    logger.error(f"FATALER FEHLER: {e}")
    
    def get_text(key, **kwargs):
        return key.split('.')[-1]
    
    class FakeHotkeys:
        def start_listener(self): pass
        def stop_listener(self): pass
    hotkey_manager = FakeHotkeys()


# --- PID-Datei-Pfad ---
try:
    PID_FILE_DIR = os.path.join(os.environ['APPDATA'], 'SmartDesk')
    PID_FILE_PATH = os.path.join(PID_FILE_DIR, 'listener.pid')
    CONTROL_PANEL_PID_PATH = os.path.join(PID_FILE_DIR, 'control_panel.pid')
    GUI_MAIN_PID_PATH = os.path.join(PID_FILE_DIR, 'gui_main.pid')
except Exception as e:
    logger.error(f"Konnte APPDATA-Pfad nicht finden: {e}")
    PID_FILE_PATH = None
    CONTROL_PANEL_PID_PATH = None
    GUI_MAIN_PID_PATH = None


def cleanup_control_panel_pid():
    """Entfernt die Control Panel PID-Datei beim Schließen."""
    try:
        if CONTROL_PANEL_PID_PATH and os.path.exists(CONTROL_PANEL_PID_PATH):
            os.remove(CONTROL_PANEL_PID_PATH)
            logger.debug("PID-Datei entfernt")
    except Exception as e:
        logger.error(f"Fehler beim Entfernen der PID-Datei: {e}")


class SmartDeskControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartDesk Control")
        
        # Fenster initial verstecken für die Animation
        self.root.withdraw()
        
        self.window_width = 420
        self.window_height = 294
        
        # Bildschirmabmessungen ermitteln
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Position für unten rechts berechnen
        padding_x = 20
        padding_y = 60
        
        self.target_x = screen_width - self.window_width - padding_x
        self.y_pos = screen_height - self.window_height - padding_y
        
        self.start_x = screen_width
        self.current_x = float(self.start_x)
        self.is_animating = True
        self.is_closing = False
        
        self.root.geometry(f"{self.window_width}x{self.window_height}+{int(self.current_x)}+{self.y_pos}")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        
        # --- Farben (KEIN Transparenz-Hack mehr) ---
        self.bg_dark = "#2b2b2b"
        
        self.root.configure(bg=self.bg_dark)
        
        self.bg_input = "#3c3c3c"
        self.fg_primary = "#ffffff"
        self.fg_label = "#cccccc"
        self.accent_green = "#14a085"
        self.accent_green_hover = "#0d7377"
        self.accent_red = "#d9534f"
        self.accent_red_hover = "#c9302c"
        self.button_bg = "#3c3c3c"
        self.button_hover = "#4a4a4a"
        
        # Status-Variable
        self.is_active = False
        
        # Hauptframe (mit mehr Padding)
        main_frame = tk.Frame(root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Titel mit Status
        title_frame = tk.Frame(main_frame, bg=self.bg_dark)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        title = tk.Label(title_frame, text="SmartDesk", 
                         font=('Segoe UI', 12, 'bold'),
                         bg=self.bg_dark, fg=self.fg_primary,
                         anchor='w')
        title.pack(side=tk.LEFT)
        
        # Status-Indikator
        self.status_indicator = tk.Label(title_frame, text="●", 
                                        font=('Segoe UI', 16),
                                        bg=self.bg_dark, fg="#666666",
                                        anchor='e')
        self.status_indicator.pack(side=tk.RIGHT)
        
        # Status-Text
        self.status_label = tk.Label(main_frame, text="Inaktiv", 
                                     font=('Segoe UI', 9),
                                     bg=self.bg_dark, fg=self.fg_label,
                                     anchor='w')
        self.status_label.pack(fill=tk.X, pady=(0, 20))
        
        # --- Toggle Button ---
        
        self.toggle_btn = tk.Button(main_frame, text="🟢 Aktivieren",
                                    font=('Segoe UI', 10, 'bold'),
                                    bg=self.accent_green, fg="#ffffff",
                                    activebackground=self.accent_green_hover,
                                    activeforeground="#ffffff",
                                    relief=tk.FLAT, bd=0,
                                    padx=20, pady=12, cursor="hand2",
                                    command=self.toggle_smartdesk)
        self.toggle_btn.pack(fill=tk.X, pady=(0, 15))
        
        # Separator
        separator = tk.Frame(main_frame, bg=self.bg_input, height=1)
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # SmartDesk Öffnen Button
        open_btn = tk.Button(main_frame, text="📂 SmartDesk Öffnen",
                            font=('Segoe UI', 9),
                            bg=self.button_bg, fg=self.fg_primary,
                            activebackground=self.button_hover,
                            activeforeground=self.fg_primary,
                            relief=tk.FLAT, bd=0,
                            padx=20, pady=8, cursor="hand2",
                            command=self.open_smartdesk)
        open_btn.pack(fill=tk.X, pady=(0, 6))
        
        # Desktop Erstellen Button
        create_btn = tk.Button(main_frame, text="➕ Desktop Erstellen",
                              font=('Segoe UI', 9),
                              bg=self.button_bg, fg=self.fg_primary,
                              activebackground=self.button_hover,
                              activeforeground=self.fg_primary,
                              relief=tk.FLAT, bd=0,
                              padx=20, pady=8, cursor="hand2",
                              command=self.create_desktop)
        create_btn.pack(fill=tk.X, pady=(0, 15))
        
        # Separator
        separator2 = tk.Frame(main_frame, bg=self.bg_input, height=1)
        separator2.pack(fill=tk.X, pady=(0, 15))
        
        # Schließen Button
        close_btn = tk.Button(main_frame, text="✕ Schließen",
                             font=('Segoe UI', 9),
                             bg=self.button_bg, fg=self.fg_primary,
                             activebackground=self.button_hover,
                             activeforeground=self.fg_primary,
                             relief=tk.FLAT, bd=0,
                             padx=20, pady=8, cursor="hand2",
                             command=self.close_panel)
        close_btn.pack(fill=tk.X)
        
        # Fenster anzeigen und Animation starten
        self.root.deiconify()
        self.animate_slide_in_from_right()
        
        # Abgerundete Ecken anwenden
        self.root.after(0, self.apply_rounded_corners)
        
        # Focus-Lost Event: Schließen wenn Fokus verloren geht
        self.root.bind('<FocusOut>', self.on_focus_lost)
        
        # Status-Update-Thread starten
        self.update_running = True
        self.update_thread = threading.Thread(target=self.update_status_loop, daemon=True)
        self.update_thread.start()
        
        # Initial Status aktualisieren
        self.update_status()
    
    def on_focus_lost(self, event):
        """Schließt das Panel wenn der Fokus verloren geht."""
        # Nur reagieren wenn das Hauptfenster den Fokus verliert
        # und wir nicht bereits schließen
        if not self.is_closing and not self.is_animating:
            # Kurze Verzögerung um sicherzustellen, dass der Fokus
            # wirklich woanders hingegangen ist
            self.root.after(100, self.check_focus_and_close)
    
    def check_focus_and_close(self):
        """Prüft ob der Fokus wirklich weg ist und schließt dann."""
        if self.is_closing:
            return
        try:
            # Prüfe ob das Fenster noch den Fokus hat
            focused = self.root.focus_get()
            if focused is None:
                self.close_panel()
        except Exception:
            pass
    
    def apply_rounded_corners(self):
        """Wendet abgerundete Ecken an (nur Windows)."""
        if win32gui:
            try:
                hwnd = self.root.winfo_id()
                radius = 20
                # WICHTIG: +1 bei width und height für korrekte Darstellung aller Ecken
                hrgn = win32gui.CreateRoundRectRgn(
                    0, 0, 
                    self.window_width + 1, 
                    self.window_height + 1, 
                    radius, radius
                )
                win32gui.SetWindowRgn(hwnd, hrgn, True)
                logger.debug("Abgerundete Ecken erfolgreich angewendet")
            except Exception as e:
                logger.warning(f"Fehler beim Anwenden der abgerundeten Ecken: {e}")
    
    def animate_slide_in_from_right(self):
        if not self.is_animating:
            return
        
        delay_ms = 10
        move_fraction = 0.15
        distance_to_go = self.current_x - self.target_x

        if distance_to_go <= 0.5:
            self.current_x = self.target_x
            self.is_animating = False
            self.root.geometry(f"{self.window_width}x{self.window_height}+{self.target_x}+{self.y_pos}")
        else:
            step = max(1, distance_to_go * move_fraction)
            self.current_x -= step
            self.root.geometry(f"{self.window_width}x{self.window_height}+{int(self.current_x)}+{self.y_pos}")
            self.root.after(delay_ms, self.animate_slide_in_from_right)
    
    def update_status_loop(self):
        """Überwacht die PID-Datei und das Schließ-Signal."""
        while self.update_running:
            try:
                # Prüfe auf Schließ-Signal vom Tray-Icon
                if CONTROL_PANEL_PID_PATH:
                    signal_file = CONTROL_PANEL_PID_PATH + '.close'
                    if os.path.exists(signal_file):
                        os.remove(signal_file)
                        self.root.after(0, self.close_panel)
                        break
                
                self.root.after(0, self.update_status)
            except:
                break
            time.sleep(0.5)
    
    def update_status(self):
        """Aktualisiert den Status basierend auf der PID-Datei."""
        try:
            if PID_FILE_PATH and os.path.exists(PID_FILE_PATH):
                self.is_active = True
                self.status_label.config(text="Aktiv", fg="#14a085")
                self.status_indicator.config(fg="#14a085")
                # Toggle Button auf "Deaktivieren" setzen
                self.toggle_btn.config(
                    text="🔴 Deaktivieren",
                    bg=self.accent_red,
                    activebackground=self.accent_red_hover
                )
            else:
                self.is_active = False
                self.status_label.config(text="Inaktiv", fg="#666666")
                self.status_indicator.config(fg="#666666")
                # Toggle Button auf "Aktivieren" setzen
                self.toggle_btn.config(
                    text="🟢 Aktivieren",
                    bg=self.accent_green,
                    activebackground=self.accent_green_hover
                )
        except Exception as e:
            logger.error(f"Fehler beim Status-Update: {e}")
    
    def toggle_smartdesk(self):
        """Toggle zwischen Aktivieren und Deaktivieren."""
        if self.is_active:
            self.deactivate_smartdesk()
        else:
            self.activate_smartdesk()
    
    def activate_smartdesk(self):
        """Aktiviert SmartDesk (startet Hotkey-Listener)."""
        try:
            logger.info("Aktiviere SmartDesk...")
            hotkey_manager.start_listener()
            self.root.after(500, self.update_status)
        except Exception as e:
            logger.error(f"Fehler beim Aktivieren: {e}")
            messagebox.showerror("Fehler", f"SmartDesk konnte nicht aktiviert werden:\n{e}")
    
    def deactivate_smartdesk(self):
        """Deaktiviert SmartDesk (stoppt Hotkey-Listener)."""
        try:
            logger.info("Deaktiviere SmartDesk...")
            hotkey_manager.stop_listener()
            self.root.after(500, self.update_status)
        except Exception as e:
            logger.error(f"Fehler beim Deaktivieren: {e}")
            messagebox.showerror("Fehler", f"SmartDesk konnte nicht deaktiviert werden:\n{e}")
    
    def open_smartdesk(self):
        """Öffnet die SmartDesk GUI (gui_main) als eigenen Prozess."""
        try:
            logger.info("Öffne SmartDesk GUI...")
            
            # Prüfe ob GUI bereits läuft
            if GUI_MAIN_PID_PATH and os.path.exists(GUI_MAIN_PID_PATH):
                try:
                    with open(GUI_MAIN_PID_PATH, 'r') as f:
                        pid = int(f.read().strip())
                    # Prüfe ob Prozess noch läuft
                    import psutil
                    if psutil.pid_exists(pid):
                        proc = psutil.Process(pid)
                        if proc.is_running():
                            logger.debug("GUI läuft bereits")
                            # Fenster in den Vordergrund bringen
                            try:
                                import win32gui
                                import win32con
                                def callback(hwnd, hwnds):
                                    if win32gui.IsWindowVisible(hwnd):
                                        title = win32gui.GetWindowText(hwnd)
                                        if "SmartDesk" in title:
                                            hwnds.append(hwnd)
                                    return True
                                hwnds = []
                                win32gui.EnumWindows(callback, hwnds)
                                if hwnds:
                                    win32gui.SetForegroundWindow(hwnds[0])
                            except Exception:
                                pass
                            return
                except Exception as e:
                    logger.warning(f"Fehler beim PID-Check: {e}")
                    # PID-Datei ungültig, löschen
                    os.remove(GUI_MAIN_PID_PATH)
            
            # Finde pythonw.exe (ohne Terminal-Fenster)
            pythonw_executable = sys.executable
            if "python.exe" in pythonw_executable.lower():
                pythonw_executable = pythonw_executable.replace(
                    "python.exe", "pythonw.exe"
                )
            
            # Finde gui_main.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            gui_main_py = os.path.join(current_dir, 'gui_main.py')
            
            logger.debug(f"Starte: {pythonw_executable} {gui_main_py}")
            
            # Starte ohne Terminal-Fenster
            proc = subprocess.Popen(
                [pythonw_executable, gui_main_py],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # PID speichern
            if GUI_MAIN_PID_PATH:
                os.makedirs(PID_FILE_DIR, exist_ok=True)
                with open(GUI_MAIN_PID_PATH, 'w') as f:
                    f.write(str(proc.pid))
                logger.debug(f"GUI PID gespeichert: {proc.pid}")
            
            # Control Panel schließen nach dem Öffnen der GUI
            self.close_panel()
            
        except Exception as e:
            logger.error(f"Fehler beim Öffnen: {e}")
            messagebox.showerror(
                "Fehler",
                f"SmartDesk GUI konnte nicht geöffnet werden:\n{e}"
            )
    
    def create_desktop(self):
        """Startet die GUI-Version für Desktop-Erstellung ohne Konsole."""
        try:
            logger.info("Starte Desktop-Erstellung GUI...")
            
            # Finde pythonw.exe (windowless)
            pythonw_executable = sys.executable
            if "python.exe" in pythonw_executable.lower():
                pythonw_executable = pythonw_executable.replace("python.exe", "pythonw.exe")
            
            # Finde gui_create.py direkt
            current_dir = os.path.dirname(os.path.abspath(__file__))
            gui_create_py = os.path.join(current_dir, 'gui_create.py')
            
            logger.debug(f"Starte: {pythonw_executable} {gui_create_py}")
            
            subprocess.Popen(
                [pythonw_executable, gui_create_py],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der GUI: {e}")
            messagebox.showerror("Fehler", f"Desktop-Erstellung konnte nicht gestartet werden:\n{e}")

    def close_panel(self):
        """Schließt das Control Panel mit Slide-Out-Animation."""
        self.update_running = False
        self.is_closing = True
        self.animate_slide_out_to_right()
    
    def animate_slide_out_to_right(self):
        """Animiert das Fenster nach rechts aus dem Bildschirm."""
        if not self.is_closing:
            return
        
        screen_width = self.root.winfo_screenwidth()
        delay_ms = 10
        move_fraction = 0.2
        
        if self.current_x >= screen_width:
            # Animation fertig, jetzt wirklich schließen
            cleanup_control_panel_pid()
            self.root.quit()
        else:
            distance_to_go = screen_width - self.current_x
            step = max(2, distance_to_go * move_fraction)
            self.current_x += step
            self.root.geometry(
                f"{self.window_width}x{self.window_height}"
                f"+{int(self.current_x)}+{self.y_pos}"
            )
            self.root.after(delay_ms, self.animate_slide_out_to_right)


def show_control_panel():
    """Hauptfunktion zum Starten der Tkinter-App."""
    try:
        root = tk.Tk()
        app = SmartDeskControlPanel(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"Fehler beim Starten: {e}")
        logger.info("Stellen Sie sicher, dass eine Desktop-Umgebung verfügbar ist.")


# Zum direkten Testen dieser Datei
if __name__ == "__main__":
    logger.info("Starte Control Panel im Testmodus...")
    show_control_panel()