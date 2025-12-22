import logging
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

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
    import ctypes

    import win32gui
except ImportError:
    win32gui = None
    ctypes = None
    logger.info("Hinweis: 'pywin32' nicht gefunden.")

# --- Projekt-Imports ---
try:
    from smartdesk.core.services import desktop_service
    from smartdesk.hotkeys import hotkey_manager
    from smartdesk.shared.localization import get_text

    desktop_handler = desktop_service
except ImportError as e:
    logger.error(f"FATALER FEHLER: {e}")

    def get_text(key, **kwargs):
        return key.split('.')[-1]

    class FakeHotkeys:
        def start_listener(self):
            pass

        def stop_listener(self):
            pass

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
        self.root.title(get_text("gui.control_panel.title"))

        # Fenster initial verstecken für die Animation
        self.root.withdraw()

        self.window_width = 420
        self.window_height = 294

        # Bildschirmabmessungen sicher ermitteln
        try:
            # Update um sicherzustellen, dass die Werte korrekt sind
            self.root.update_idletasks()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Fallback für ungültige Werte
            if screen_width <= 0 or screen_height <= 0:
                screen_width = 1920
                screen_height = 1080
                logger.warning(
                    "Bildschirmabmessungen ungültig, verwende Fallback 1920x1080"
                )
        except Exception as e:
            logger.warning(f"Fehler beim Ermitteln der Bildschirmgröße: {e}")
            screen_width = 1920
            screen_height = 1080

        self.screen_width = screen_width
        self.screen_height = screen_height

        # Position für unten rechts berechnen
        padding_x = 20
        padding_y = 60

        self.target_x = max(0, screen_width - self.window_width - padding_x)
        self.y_pos = max(0, screen_height - self.window_height - padding_y)

        # Integer-Werte für Animation (keine Float-Rundungsprobleme)
        self.start_x = screen_width
        self.current_x = self.start_x
        self.is_animating = True
        self.is_closing = False
        self._animation_id = None  # Für Animation-Cancellation

        self.root.geometry(
            f"{self.window_width}x{self.window_height}+{self.current_x}+{self.y_pos}"
        )
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

        # Hauptframe
        main_frame = tk.Frame(root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- Header ---
        header_frame = tk.Frame(main_frame, bg=self.bg_dark)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        # Title "Control Panel"
        tk.Label(
            header_frame,
            text=get_text("gui.control_panel.header"),
            font=('Segoe UI', 12),
            bg=self.bg_dark,
            fg=self.fg_primary,
            anchor='w'
        ).pack(side=tk.LEFT)

        # Desktop Name "Desktop: ..."
        self.desktop_name_label = tk.Label(
            header_frame,
            text=get_text("gui.control_panel.desktop_label_none"),
            font=('Segoe UI', 12),
            bg=self.bg_dark,
            fg=self.fg_primary,
            anchor='e'
        )
        self.desktop_name_label.pack(side=tk.RIGHT)

        # Separator Line
        tk.Frame(main_frame, bg="#666666", height=1).pack(fill=tk.X, pady=(0, 15))

        # --- Grid Area ---
        grid_frame = tk.Frame(main_frame, bg=self.bg_dark)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # Button Styles
        btn_opts = {
            'font': ('Segoe UI', 10),
            'relief': tk.FLAT,
            'bd': 0,
            'cursor': "hand2",
            'pady': 10
        }

        # -- Left Column --
        
        # 1. SmartDesk Öffnen
        self.btn_open = tk.Button(
            grid_frame,
            text=get_text("gui.control_panel.button_open"),
            bg=self.button_bg,
            fg=self.fg_primary,
            activebackground=self.button_hover,
            activeforeground=self.fg_primary,
            command=self.open_smartdesk,
            **btn_opts
        )
        self.btn_open.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=(0, 10))

        # 2. Desktop Erstellen
        self.btn_create = tk.Button(
            grid_frame,
            text=get_text("gui.control_panel.button_create"),
            bg=self.button_bg,
            fg=self.fg_primary,
            activebackground=self.button_hover,
            activeforeground=self.fg_primary,
            command=self.create_desktop,
            **btn_opts
        )
        self.btn_create.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(0, 10))

        # 3. Desktops Verwalten
        self.btn_manage = tk.Button(
            grid_frame,
            text=get_text("gui.control_panel.button_manage"),
            bg=self.button_bg,
            fg=self.fg_primary,
            activebackground=self.button_hover,
            activeforeground=self.fg_primary,
            command=self.manage_desktops,
            **btn_opts
        )
        self.btn_manage.grid(row=2, column=0, sticky="ew", padx=(0, 5), pady=(0, 0))

        # -- Right Column --

        # 1. Hotkey Toggle
        self.toggle_btn = tk.Button(
            grid_frame,
            text=get_text("gui.control_panel.button_hotkey_activate"),
            bg=self.button_bg, # Initial color, will be updated
            fg=self.fg_primary,
            activebackground=self.button_hover,
            activeforeground=self.fg_primary,
            command=self.toggle_smartdesk,
            **btn_opts
        )
        self.toggle_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=(0, 10))

        # Placeholders
        for r in [1, 2]:
            empty_btn = tk.Button(
                grid_frame,
                state=tk.DISABLED,
                bg=self.button_bg,
                relief=tk.FLAT,
                bd=0
            )
            empty_btn.grid(row=r, column=1, sticky="nsew", padx=(5, 0), pady=(0, 10 if r==1 else 0))


        # Fenster anzeigen und Animation starten
        self.root.deiconify()
        self.root.update_idletasks()  # Wichtig: Fenster vollständig initialisieren
        self._animation_id = self.root.after(50, self.animate_slide_in_from_right)

        # Abgerundete Ecken verzögert anwenden (Fenster muss existieren)
        self.root.after(100, self.apply_rounded_corners)

        # Focus-Lost Event: Schließen wenn Fokus verloren geht
        # Verzögert binden, damit Initialisierung abgeschlossen ist
        self.root.after(500, self._bind_focus_events)

        # Status-Update mit Tkinter-after statt Thread (Thread-Safety)
        self.update_running = True
        self._schedule_status_update()

        # Initial Status aktualisieren
        self.update_status()
        self.update_active_desktop_label()

    def _bind_focus_events(self):
        """Bindet Focus-Events nach der Animation."""
        if not self.is_closing:
            self.root.bind('<FocusOut>', self.on_focus_lost)

    def _schedule_status_update(self):
        """Plant das nächste Status-Update (Thread-sicher via after)."""
        if self.update_running and not self.is_closing:
            try:
                self._check_close_signal()
                self.update_status()
                self.update_active_desktop_label()
            except Exception as e:
                logger.debug(f"Status-Update übersprungen: {e}")
            # Nächstes Update in 500ms
            self.root.after(500, self._schedule_status_update)

    def _check_close_signal(self):
        """Prüft auf Schließ-Signal vom Tray-Icon."""
        if CONTROL_PANEL_PID_PATH:
            signal_file = CONTROL_PANEL_PID_PATH + '.close'
            if os.path.exists(signal_file):
                try:
                    os.remove(signal_file)
                except Exception:
                    pass
                self.close_panel()

    def on_focus_lost(self, event):
        """Schließt das Panel wenn der Fokus verloren geht."""
        # Nur reagieren wenn das Hauptfenster den Fokus verliert
        # und wir nicht bereits schließen oder animieren
        if self.is_closing or self.is_animating:
            return

        # Ignoriere Focus-Verlust an Kind-Widgets (Buttons etc.)
        if event.widget != self.root:
            return

        # Kurze Verzögerung um sicherzustellen, dass der Fokus
        # wirklich woanders hingegangen ist (nicht nur Button-Klick)
        self.root.after(150, self.check_focus_and_close)

    def check_focus_and_close(self):
        """Prüft ob der Fokus wirklich weg ist und schließt dann."""
        if self.is_closing:
            return
        try:
            # Prüfe ob das Fenster noch den Fokus hat
            focused = self.root.focus_get()
            # Wenn kein Widget in diesem Fenster den Fokus hat, schließen
            if focused is None:
                # Zusätzliche Prüfung: Ist das Fenster noch aktiv?
                try:
                    if not self.root.winfo_exists():
                        return
                except Exception:
                    return
                self.close_panel()
        except tk.TclError:
            # Fenster wurde bereits zerstört
            pass
        except Exception as e:
            logger.debug(f"Focus-Check Fehler (ignoriert): {e}")

    def apply_rounded_corners(self):
        """Wendet abgerundete Ecken an (nur Windows)."""
        if not win32gui:
            return

        try:
            # Warte bis Fenster vollständig gerendert ist
            self.root.update_idletasks()

            # Hole das echte Top-Level Window Handle
            frame_hwnd = self.root.winfo_id()
            hwnd = win32gui.GetParent(frame_hwnd)
            if not hwnd:
                hwnd = frame_hwnd

            # Methode 1: Windows 11+ DWM API für native runde Ecken
            if self._try_dwm_rounded_corners(hwnd):
                logger.debug("DWM runde Ecken angewendet (Windows 11+)")
                return

            # Methode 2: Fallback mit Region (ältere Windows-Versionen)
            self._apply_region_rounded_corners(hwnd)

        except Exception as e:
            logger.warning(f"Fehler bei abgerundeten Ecken: {e}")

    def _try_dwm_rounded_corners(self, hwnd):
        """Versucht Windows 11 DWM API für runde Ecken zu nutzen."""
        if not ctypes:
            return False
        try:
            # DWMWA_WINDOW_CORNER_PREFERENCE = 33
            # DWMWCP_ROUND = 2 (runde Ecken)
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2

            dwmapi = ctypes.windll.dwmapi
            preference = ctypes.c_int(DWMWCP_ROUND)
            result = dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(preference),
                ctypes.sizeof(preference),
            )
            return result == 0  # S_OK
        except Exception:
            return False

    def _apply_region_rounded_corners(self, hwnd):
        """Wendet abgerundete Ecken via Window Region an."""
        try:
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]

            radius = 20

            # CreateRoundRectRgn: rechts/unten sind exklusiv
            hrgn = win32gui.CreateRoundRectRgn(
                0, 0, width + 1, height + 1, radius, radius
            )

            if win32gui.SetWindowRgn(hwnd, hrgn, True):
                logger.debug("Region runde Ecken angewendet")
            else:
                logger.warning("SetWindowRgn fehlgeschlagen")
        except Exception as e:
            logger.warning(f"Region Fehler: {e}")

    def animate_slide_in_from_right(self):
        """Animiert das Fenster von rechts herein."""
        if not self.is_animating or self.is_closing:
            return

        try:
            # Prüfe ob Fenster noch existiert
            if not self.root.winfo_exists():
                return
        except tk.TclError:
            return

        delay_ms = 10  # ~60 FPS
        ease_factor = 0.20  # Easing für flüssigere Animation
        distance_to_go = self.current_x - self.target_x

        if distance_to_go <= 1:
            # Animation abgeschlossen
            self.current_x = self.target_x
            self.is_animating = False
            self._set_geometry(self.target_x)
            self._animation_id = None
        else:
            # Easing: Langsamer werden je näher am Ziel
            step = max(1, int(distance_to_go * ease_factor))
            self.current_x -= step
            self._set_geometry(self.current_x)
            self._animation_id = self.root.after(
                delay_ms, self.animate_slide_in_from_right
            )

    def _set_geometry(self, x_pos):
        """Setzt die Fensterposition sicher."""
        try:
            x = max(0, int(x_pos))
            y = max(0, int(self.y_pos))
            self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        except tk.TclError:
            # Fenster wurde geschlossen
            pass
        except Exception as e:
            logger.debug(f"Geometry-Fehler: {e}")

    def update_status_loop(self):
        """DEPRECATED - Wird nicht mehr verwendet. Status-Update läuft via _schedule_status_update."""
        pass

    def update_status(self):
        """Aktualisiert den Status basierend auf der PID-Datei."""
        try:
            if PID_FILE_PATH and os.path.exists(PID_FILE_PATH):
                self.is_active = True
                # Toggle Button auf "Deaktivieren" setzen
                if hasattr(self, 'toggle_btn'):
                    self.toggle_btn.config(
                        text=get_text("gui.control_panel.button_hotkey_deactivate"),
                        bg=self.accent_red,
                        activebackground=self.accent_red_hover,
                    )
            else:
                self.is_active = False
                # Toggle Button auf "Aktivieren" setzen
                if hasattr(self, 'toggle_btn'):
                    self.toggle_btn.config(
                        text=get_text("gui.control_panel.button_hotkey_activate"),
                        bg=self.button_bg,
                        activebackground=self.button_hover,
                    )
        except Exception as e:
            logger.error(f"Fehler beim Status-Update: {e}")

    def update_active_desktop_label(self):
        """Aktualisiert das Label mit dem aktuellen Desktop-Namen."""
        if not hasattr(self, 'desktop_name_label'):
            return
        try:
            desktops = desktop_service.get_all_desktops()
            active_desktop = next((d for d in desktops if d.is_active), None)
            if active_desktop:
                self.desktop_name_label.config(text=get_text("gui.control_panel.desktop_label_template", name=active_desktop.name))
            else:
                self.desktop_name_label.config(text=get_text("gui.control_panel.desktop_label_none"))
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Desktops: {e}")
            self.desktop_name_label.config(text=get_text("gui.control_panel.desktop_label_error"))

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
            messagebox.showerror(
                get_text("gui.common.error_title"), get_text("gui.control_panel.error_activation_failed", e=e)
            )

    def deactivate_smartdesk(self):
        """Deaktiviert SmartDesk (stoppt Hotkey-Listener)."""
        try:
            logger.info("Deaktiviere SmartDesk...")
            hotkey_manager.stop_listener()
            self.root.after(500, self.update_status)
        except Exception as e:
            logger.error(f"Fehler beim Deaktivieren: {e}")
            messagebox.showerror(
                get_text("gui.common.error_title"), get_text("gui.control_panel.error_deactivation_failed", e=e)
            )

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
                creationflags=subprocess.CREATE_NO_WINDOW,
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
                get_text("gui.common.error_title"), get_text("gui.control_panel.error_open_gui_failed", e=e)
            )

    def create_desktop(self):
        """Startet die GUI-Version für Desktop-Erstellung ohne Konsole."""
        try:
            logger.info("Starte Desktop-Erstellung GUI...")

            # Finde pythonw.exe (windowless)
            pythonw_executable = sys.executable
            if "python.exe" in pythonw_executable.lower():
                pythonw_executable = pythonw_executable.replace(
                    "python.exe", "pythonw.exe"
                )

            # Finde gui_create.py direkt
            current_dir = os.path.dirname(os.path.abspath(__file__))
            gui_create_py = os.path.join(current_dir, 'gui_create.py')

            logger.debug(f"Starte: {pythonw_executable} {gui_create_py}")

            subprocess.Popen(
                [pythonw_executable, gui_create_py],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            # Control Panel schließen, damit gui_create den Fokus bekommt
            self.close_panel()

        except Exception as e:
            logger.error(f"Fehler beim Erstellen der GUI: {e}")
            messagebox.showerror(
                get_text("gui.common.error_title"), get_text("gui.control_panel.error_create_gui_failed", e=e)
            )

    def manage_desktops(self):
        """Startet die GUI-Version für Desktop-Verwaltung ohne Konsole."""
        try:
            logger.info("Starte Desktop-Verwaltung GUI...")

            # Finde pythonw.exe (windowless)
            pythonw_executable = sys.executable
            if "python.exe" in pythonw_executable.lower():
                pythonw_executable = pythonw_executable.replace(
                    "python.exe", "pythonw.exe"
                )

            # Finde gui_manage.py direkt
            current_dir = os.path.dirname(os.path.abspath(__file__))
            gui_manage_py = os.path.join(current_dir, 'gui_manage.py')

            logger.debug(f"Starte: {pythonw_executable} {gui_manage_py}")

            subprocess.Popen(
                [pythonw_executable, gui_manage_py],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            # Control Panel schließen
            self.close_panel()

        except Exception as e:
            logger.error(f"Fehler beim Starten der Verwaltung: {e}")
            messagebox.showerror(
                get_text("gui.common.error_title"), get_text("gui.control_panel.error_manage_gui_failed", e=e)
            )

    def close_panel(self):
        """Schließt das Control Panel mit Slide-Out-Animation."""
        if self.is_closing:
            return  # Bereits am Schließen

        self.update_running = False
        self.is_closing = True
        self.is_animating = False

        # Laufende Animation abbrechen
        if self._animation_id:
            try:
                self.root.after_cancel(self._animation_id)
            except Exception:
                pass
            self._animation_id = None

        self.animate_slide_out_to_right()

    def animate_slide_out_to_right(self):
        """Animiert das Fenster nach rechts aus dem Bildschirm."""
        if not self.is_closing:
            return

        try:
            if not self.root.winfo_exists():
                self._final_cleanup()
                return
        except tk.TclError:
            self._final_cleanup()
            return

        delay_ms = 10  # ~60 FPS
        ease_factor = 0.20  # Schneller raus als rein

        if self.current_x >= self.screen_width:
            # Animation fertig, jetzt wirklich schließen
            self._final_cleanup()
        else:
            distance_to_go = self.screen_width - self.current_x
            step = max(3, int(distance_to_go * ease_factor))
            self.current_x += step
            self._set_geometry(self.current_x)
            self.root.after(delay_ms, self.animate_slide_out_to_right)

    def _final_cleanup(self):
        """Räumt auf und schließt das Fenster."""
        try:
            cleanup_control_panel_pid()
        except Exception as e:
            logger.debug(f"PID Cleanup Fehler: {e}")

        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass


def show_control_panel():
    """Hauptfunktion zum Starten der Tkinter-App."""
    try:
        root = tk.Tk()
        SmartDeskControlPanel(root)
        root.mainloop()
    except tk.TclError as e:
        logger.error(f"Tkinter-Fehler: {e}")
        logger.info("Desktop-Umgebung verfügbar?")
    except Exception as e:
        logger.error(f"Fehler beim Starten: {e}")


# Zum direkten Testen dieser Datei
if __name__ == "__main__":
    logger.info("Starte Control Panel im Testmodus...")
    show_control_panel()
