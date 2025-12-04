import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
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
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

# --- Abgerundete Ecken (nur Windows) ---
try:
    import win32gui
    import ctypes
except ImportError:
    win32gui = None
    ctypes = None
    logger.info("'pywin32' nicht gefunden.")

# --- Projekt-Imports ---
try:
    from smartdesk.core.services import desktop_service
    from smartdesk.shared.localization import get_text

    desktop_handler = desktop_service
except ImportError as e:
    logger.error(f"FATALER FEHLER: {e}")

    def get_text(key, **kwargs):
        return key.split('.')[-1]

    class FakeHandler:
        def create_desktop(*args, **kwargs):
            return False

    desktop_handler = FakeHandler()


class DesktopCreatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(get_text("ui.headings.create"))

        # Fenster initial verstecken für die Animation
        self.root.withdraw()

        self.window_width = 420
        self.window_height = 294

        # Bildschirmabmessungen sicher ermitteln
        try:
            self.root.update_idletasks()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            if screen_width <= 0 or screen_height <= 0:
                screen_width = 1920
                screen_height = 1080
                logger.warning("Bildschirmabmessungen ungültig, Fallback")
        except Exception as e:
            logger.warning(f"Bildschirmgröße Fehler: {e}")
            screen_width = 1920
            screen_height = 1080

        self.screen_width = screen_width
        self.screen_height = screen_height

        # Position für unten rechts berechnen
        padding_x = 20
        padding_y = 60

        self.target_x = max(0, screen_width - self.window_width - padding_x)
        self.y_pos = max(0, screen_height - self.window_height - padding_y)

        # Integer-Werte für Animation
        self.start_x = screen_width
        self.current_x = self.start_x
        self.is_animating = True
        self.is_closing = False
        self._animation_id = None

        self.root.geometry(
            f"{self.window_width}x{self.window_height}+{self.current_x}+{self.y_pos}"
        )
        self.root.resizable(False, False)
        self.root.overrideredirect(True)

        # --- Farben (KEIN Transparenz-Hack mehr) ---
        self.bg_dark = "#2b2b2b"

        self.root.configure(bg=self.bg_dark)
        # --- Ende Transparenz-Hack ---

        self.bg_input = "#3c3c3c"
        self.fg_primary = "#ffffff"
        self.fg_label = "#cccccc"
        self.accent = "#14a085"
        self.accent_hover = "#0d7377"
        self.button_bg = "#3c3c3c"
        self.button_hover = "#4a4a4a"

        # Hauptframe (dieser bekommt die ECHTE Hintergrundfarbe)
        main_frame = tk.Frame(root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Titel
        title = tk.Label(
            main_frame,
            text="SmartDesk - Desktop erstellen",
            font=('Segoe UI', 11),
            bg=self.bg_dark,
            fg=self.fg_primary,
            anchor='w',
        )
        title.pack(fill=tk.X, pady=(0, 15))

        # Name Label
        name_label = tk.Label(
            main_frame,
            text="Name",
            font=('Segoe UI', 9),
            bg=self.bg_dark,
            fg=self.fg_label,
            anchor='w',
        )
        name_label.pack(fill=tk.X, pady=(0, 3))

        # Name Input
        self.name_entry = tk.Entry(
            main_frame,
            font=('Segoe UI', 10),
            bg=self.bg_input,
            fg=self.fg_primary,
            insertbackground=self.fg_primary,
            relief=tk.FLAT,
            bd=0,
        )
        self.name_entry.pack(fill=tk.X, ipady=6, pady=(0, 10))

        # Pfad Label - dynamisch je nach Modus
        self.pfad_label = tk.Label(
            main_frame,
            text="Pfad zum vorhandenen Ordner:",
            font=('Segoe UI', 9),
            bg=self.bg_dark,
            fg=self.fg_label,
            anchor='w',
        )
        self.pfad_label.pack(fill=tk.X, pady=(0, 3))

        # Pfad Input Container
        pfad_container = tk.Frame(main_frame, bg=self.bg_dark)
        pfad_container.pack(fill=tk.X, pady=(0, 15))

        self.path_entry = tk.Entry(
            pfad_container,
            font=('Segoe UI', 10),
            bg=self.bg_input,
            fg=self.fg_primary,
            insertbackground=self.fg_primary,
            relief=tk.FLAT,
            bd=0,
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=6)

        browse_btn = tk.Button(
            pfad_container,
            text="...",
            font=('Segoe UI', 10),
            bg=self.bg_input,
            fg=self.fg_primary,
            activebackground=self.button_hover,
            activeforeground=self.fg_primary,
            relief=tk.FLAT,
            bd=0,
            width=4,
            cursor="hand2",
            command=self.browse_folder,
        )
        browse_btn.pack(side=tk.LEFT, padx=(5, 0), ipady=6)

        # Bottom Container
        bottom = tk.Frame(main_frame, bg=self.bg_dark)
        bottom.pack(fill=tk.X)

        # Radio Buttons (links)
        radio_frame = tk.Frame(bottom, bg=self.bg_dark)
        radio_frame.pack(side=tk.LEFT)

        self.mode_var = tk.StringVar(value="1")
        self.mode_var.trace_add("write", self.on_mode_change)

        rb1 = tk.Radiobutton(
            radio_frame,
            text="Vorhanden",
            variable=self.mode_var,
            value="1",
            font=('Segoe UI', 9),
            bg=self.bg_dark,
            fg=self.fg_primary,
            selectcolor=self.bg_input,
            activebackground=self.bg_dark,
            activeforeground=self.fg_primary,
            relief=tk.FLAT,
            cursor="hand2",
        )
        rb1.pack(side=tk.LEFT, padx=(0, 5))

        rb2 = tk.Radiobutton(
            radio_frame,
            text="Neu erstellen",
            variable=self.mode_var,
            value="2",
            font=('Segoe UI', 9),
            bg=self.bg_dark,
            fg=self.fg_primary,
            selectcolor=self.bg_input,
            activebackground=self.bg_dark,
            activeforeground=self.fg_primary,
            relief=tk.FLAT,
            cursor="hand2",
        )
        rb2.pack(side=tk.LEFT)

        # Buttons (rechts)
        button_frame = tk.Frame(bottom, bg=self.bg_dark)
        button_frame.pack(side=tk.RIGHT)

        create_btn = tk.Button(
            button_frame,
            text="Erstellen",
            font=('Segoe UI', 9),
            bg=self.accent,
            fg="#ffffff",
            activebackground=self.accent_hover,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.create_desktop,
        )
        create_btn.pack(side=tk.LEFT, padx=(0, 5))

        cancel_btn = tk.Button(
            button_frame,
            text="Abbrechen",
            font=('Segoe UI', 9),
            bg=self.button_bg,
            fg=self.fg_primary,
            activebackground=self.button_hover,
            activeforeground=self.fg_primary,
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.close_window,
        )
        cancel_btn.pack(side=tk.LEFT)

        # Fenster anzeigen und Animation starten
        self.root.deiconify()
        self.root.update_idletasks()
        self._animation_id = self.root.after(50, self.animate_slide_in_from_right)

        # Abgerundete Ecken verzögert anwenden
        self.root.after(100, self.apply_rounded_corners)

        # Fokus auf dieses Fenster setzen (wenn von Control Panel gestartet)
        self.root.after(200, self._request_focus)

    def _request_focus(self):
        """Fordert den Fokus für dieses Fenster an."""
        try:
            self.root.lift()
            self.root.focus_force()
            self.name_entry.focus_set()

            # Windows-spezifisch: Fenster in den Vordergrund bringen
            if win32gui:
                try:
                    frame_hwnd = self.root.winfo_id()
                    hwnd = win32gui.GetParent(frame_hwnd)
                    if not hwnd:
                        hwnd = frame_hwnd
                    win32gui.SetForegroundWindow(hwnd)
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Fokus-Anforderung fehlgeschlagen: {e}")

    def apply_rounded_corners(self):
        """Wendet abgerundete Ecken an (nur Windows)."""
        if not win32gui:
            return

        try:
            self.root.update_idletasks()

            # Hole das echte Top-Level Window Handle
            frame_hwnd = self.root.winfo_id()
            hwnd = win32gui.GetParent(frame_hwnd)
            if not hwnd:
                hwnd = frame_hwnd

            # Methode 1: Windows 11+ DWM API
            if self._try_dwm_rounded_corners(hwnd):
                logger.debug("DWM runde Ecken angewendet")
                return

            # Methode 2: Fallback mit Region
            self._apply_region_rounded_corners(hwnd)

        except Exception as e:
            logger.warning(f"Fehler bei abgerundeten Ecken: {e}")

    def _try_dwm_rounded_corners(self, hwnd):
        """Versucht Windows 11 DWM API für runde Ecken."""
        if not ctypes:
            return False
        try:
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
            return result == 0
        except Exception:
            return False

    def _apply_region_rounded_corners(self, hwnd):
        """Wendet abgerundete Ecken via Window Region an."""
        try:
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]

            radius = 20
            hrgn = win32gui.CreateRoundRectRgn(
                0, 0, width + 1, height + 1, radius, radius
            )

            if win32gui.SetWindowRgn(hwnd, hrgn, True):
                logger.debug("Region runde Ecken angewendet")
        except Exception as e:
            logger.warning(f"Region Fehler: {e}")

    def on_mode_change(self, *args):
        """Wird aufgerufen, wenn der Modus geändert wird."""
        if self.mode_var.get() == "1":
            # Vorhanden: Pfad zum existierenden Ordner
            self.pfad_label.config(text="Pfad zum vorhandenen Ordner:")
        else:
            # Neu erstellen: Pfad wo der neue Ordner erstellt werden soll
            self.pfad_label.config(
                text="Übergeordneter Pfad (Ordner wird hier erstellt):"
            )

    def close_window(self):
        """Schließt das Fenster mit Slide-Out-Animation."""
        if self.is_closing:
            return

        self.is_closing = True
        self.is_animating = False

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

        delay_ms = 10
        ease_factor = 0.20

        if self.current_x >= self.screen_width:
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
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass

    def animate_slide_in_from_right(self):
        """Animiert das Fenster von rechts herein."""
        if not self.is_animating or self.is_closing:
            return

        try:
            if not self.root.winfo_exists():
                return
        except tk.TclError:
            return

        delay_ms = 10
        ease_factor = 0.20
        distance_to_go = self.current_x - self.target_x

        if distance_to_go <= 1:
            self.current_x = self.target_x
            self.is_animating = False
            self._set_geometry(self.target_x)
            self._animation_id = None
        else:
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
            pass
        except Exception as e:
            logger.debug(f"Geometry-Fehler: {e}")

    def browse_folder(self):
        # Ändert den Titel je nach Modus
        if self.mode_var.get() == "2":
            title = get_text(
                "gui.create.browse_title_parent", "Übergeordneten Ordner auswählen"
            )
        else:
            title = get_text(
                "gui.create.browse_title_existing", "Vorhandenen Ordner auswählen"
            )

        folder = filedialog.askdirectory(title=title)

        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def create_desktop(self):
        """Ruft den desktop_handler auf, anstatt die Logik selbst auszuführen."""
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip().strip('"')
        mode = self.mode_var.get()

        if not name:
            messagebox.showerror(
                get_text("ui.errors.invalid_input"), get_text("ui.errors.name_empty")
            )
            return

        if not path:
            messagebox.showerror(
                get_text("ui.errors.invalid_input"),
                get_text("ui.messages.aborted_no_path"),
            )
            return

        path = os.path.normpath(path)

        if not os.path.isabs(path):
            messagebox.showerror(
                get_text("ui.errors.invalid_input"),
                get_text("ui.errors.path_not_absolute", path=path),
            )
            return

        # Modus "Neu erstellen" = True, "Vorhanden" = False
        create_if_missing = mode == "2"

        # --- KORREKTUR: Bei Modus 2 den finalen Pfad erstellen ---
        if create_if_missing:
            # Bei "Neu erstellen": Hänge den Namen an den übergeordneten Pfad
            final_path = os.path.join(path, name)
        else:
            # Bei "Vorhanden": Der Pfad ist bereits der finale Ordner
            final_path = path

        success = desktop_handler.create_desktop(
            name,
            final_path,  # <-- Jetzt korrekt: finaler Pfad
            create_if_missing=create_if_missing,
        )

        if success:
            messagebox.showinfo(
                get_text("desktop_handler.success.create", name=name),
                f"{get_text('ui.messages.new_path_location', path=final_path)}",
            )
            self.root.quit()
        else:
            messagebox.showerror(
                get_text("ui.errors.invalid_input", "Fehler"),
                "Desktop konnte nicht erstellt werden.\n\nMögliche Gründe:\n"
                "- Der Name ist bereits vergeben.\n"
                "- Der Pfad ist ungültig.\n"
                "- Der Ordner existiert nicht (im 'Vorhanden'-Modus).\n"
                "- Fehlende Berechtigungen.",
            )


def show_create_desktop_window():
    """Hauptfunktion zum Starten der Tkinter-App."""
    try:
        root = tk.Tk()
        DesktopCreatorGUI(root)
        root.mainloop()
    except tk.TclError as e:
        logger.error(f"Tkinter-Fehler: {e}")
    except Exception as e:
        logger.error(f"Fehler beim Starten: {e}")


# Zum direkten Testen dieser Datei
if __name__ == "__main__":
    logger.info("Starte GUI im Testmodus...")
    show_create_desktop_window()
