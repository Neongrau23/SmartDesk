import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Importiere die Lokalisierungsfunktion deines Projekts
from smartdesk.shared.localization import get_text


class DesktopCreatorGUI:
    def __init__(self, root):
        self.root = root
        # Das Ergebnis, das wir an die CLI zurückgeben
        self.result = None

        # --- LOKALISIERUNG ---
        self.root.title(get_text("gui.create.title"))

        # Fenster initial verstecken für die Animation
        self.root.withdraw()

        self.window_width = 420
        self.window_height = 294

        # Bildschirmabmessungen ermitteln
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Position für unten rechts berechnen (mit etwas Abstand)
        padding_x = 20  # Abstand vom rechten Rand
        padding_y = 60  # Abstand vom unteren Rand (um Taskleiste zu meiden)

        # Ziel-Position (Endposition der Animation)
        self.target_x = screen_width - self.window_width - padding_x
        self.y_pos = screen_height - self.window_height - padding_y

        # Startposition (rechts, außerhalb des Bildschirms)
        self.start_x = screen_width
        self.current_x = float(self.start_x)  # Als float für präzises Easing

        self.is_animating = True  # Flag, um Animation zu stoppen

        # Setze initiale Geometrie (außerhalb des Bildschirms)
        self.root.geometry(
            f"{self.window_width}x{self.window_height}+{int(self.current_x)}+{self.y_pos}"
        )

        self.root.resizable(False, False)
        self.root.overrideredirect(True)  # Entfernt die Titelleiste

        # Exakte Farben vom Screenshot
        self.bg_dark = "#2b2b2b"
        self.bg_input = "#3c3c3c"
        self.fg_primary = "#ffffff"
        self.fg_label = "#cccccc"
        self.accent = "#14a085"
        self.accent_hover = "#0d7377"
        self.button_bg = "#3c3c3c"
        self.button_hover = "#4a4a4a"

        self.root.configure(bg=self.bg_dark)

        # Hauptframe
        main_frame = tk.Frame(root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titel (Lokalisiert)
        title = tk.Label(
            main_frame,
            text=get_text("gui.create.title"),
            font=('Segoe UI', 11),
            bg=self.bg_dark,
            fg=self.fg_primary,
            anchor='w',
        )
        title.pack(fill=tk.X, pady=(0, 20))

        # Name Label (Lokalisiert)
        name_label = tk.Label(
            main_frame,
            text=get_text("gui.create.label_name"),
            font=('Segoe UI', 9),
            bg=self.bg_dark,
            fg=self.fg_label,
            anchor='w',
        )
        name_label.pack(fill=tk.X, pady=(0, 5))

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
        self.name_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))

        # Pfad Label (Lokalisiert) - dynamisch je nach Modus
        self.pfad_label = tk.Label(
            main_frame,
            text="Pfad zum vorhandenen Ordner:",
            font=('Segoe UI', 9),
            bg=self.bg_dark,
            fg=self.fg_label,
            anchor='w',
        )
        self.pfad_label.pack(fill=tk.X, pady=(0, 5))

        # Pfad Input Container
        pfad_container = tk.Frame(main_frame, bg=self.bg_dark)
        pfad_container.pack(fill=tk.X, pady=(0, 20))

        self.path_entry = tk.Entry(
            pfad_container,
            font=('Segoe UI', 10),
            bg=self.bg_input,
            fg=self.fg_primary,
            insertbackground=self.fg_primary,
            relief=tk.FLAT,
            bd=0,
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8)

        browse_btn = tk.Button(
            pfad_container,
            text=get_text("gui.create.button_browse"),
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
        browse_btn.pack(side=tk.LEFT, padx=(5, 0), ipady=8)

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
            text=get_text("gui.create.radio_existing"),  # Lokalisiert
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
        rb1.pack(side=tk.LEFT, padx=(0, 10))

        rb2 = tk.Radiobutton(
            radio_frame,
            text=get_text("gui.create.radio_new"),  # Lokalisiert
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
            text=get_text("gui.create.button_create"),  # Lokalisiert
            font=('Segoe UI', 9),
            bg=self.accent,
            fg="#ffffff",
            activebackground=self.accent_hover,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=6,
            cursor="hand2",
            command=self.submit_data,
        )  # Geändert
        create_btn.pack(side=tk.LEFT, padx=(0, 5))

        cancel_btn = tk.Button(
            button_frame,
            text=get_text("gui.create.button_cancel"),  # Lokalisiert
            font=('Segoe UI', 9),
            bg=self.button_bg,
            fg=self.fg_primary,
            activebackground=self.button_hover,
            activeforeground=self.fg_primary,
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=6,
            cursor="hand2",
            command=self.cancel_and_close,
        )  # Geändert
        cancel_btn.pack(side=tk.LEFT)

        # Fenster anzeigen und Animation starten
        self.root.deiconify()
        self.animate_slide_in_from_right()

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

    def animate_slide_in_from_right(self):
        """Animiert das Fenster von rechts nach links mit 'ease-out'-Effekt."""
        if not self.is_animating:
            return  # Animation wurde durch Benutzerinteraktion gestoppt

        delay_ms = 10  # Zeit zwischen Frames (ms)
        move_fraction = 0.15  # Easing-Faktor (15% der Restdistanz pro Frame)

        distance_to_go = self.current_x - self.target_x

        if distance_to_go <= 0.5:  # Nahezu am Ziel (Puffer für float-Ungenauigkeit)
            # Am Ziel ankommen und Animation stoppen
            self.current_x = self.target_x
            self.is_animating = False
            self.root.geometry(
                f"{self.window_width}x{self.window_height}+{self.target_x}+{self.y_pos}"
            )
        else:
            # Berechne den Schritt (mindestens 1 Pixel, um voranzukommen)
            step = max(1, distance_to_go * move_fraction)

            # Aktualisiere die X-Position
            self.current_x -= step

            # Aktualisiere die Fenstergeometrie (als int)
            self.root.geometry(
                f"{self.window_width}x{self.window_height}+{int(self.current_x)}+{self.y_pos}"
            )

            # Plane den nächsten Animationsschritt
            self.root.after(delay_ms, self.animate_slide_in_from_right)

    def animate_slide_out_to_right(self):
        """Animiert das Fenster nach rechts hinaus ('ease-out') und beendet die App."""

        # Stoppt die "Slide-In"-Animation, falls sie noch läuft
        self.is_animating = False

        delay_ms = 10  # Zeit zwischen Frames (ms)
        move_fraction = 0.15  # Easing-Faktor

        # Distanz zum Ziel (self.start_x ist die Position außerhalb des Bildschirms)
        distance_to_go = self.start_x - self.current_x

        if distance_to_go <= 0.5:  # Nahezu am Ziel
            # Am Ziel ankommen und Fenster zerstören
            self.root.destroy()  # <-- WICHTIG: Beendet die mainloop
        else:
            # Berechne den Schritt (mindestens 1 Pixel)
            step = max(1, distance_to_go * move_fraction)

            # Aktualisiere die X-Position (nach rechts)
            self.current_x += step

            # Aktualisiere die Fenstergeometrie (als int)
            self.root.geometry(
                f"{self.window_width}x{self.window_height}+{int(self.current_x)}+{self.y_pos}"
            )

            # Plane den nächsten Animationsschritt
            self.root.after(delay_ms, self.animate_slide_out_to_right)

    def browse_folder(self):
        folder = filedialog.askdirectory(
            title=get_text("gui.create.browse_title")
        )  # Titel lokalisiert
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def cancel_and_close(self):
        """Wird beim Klick auf "Abbrechen" aufgerufen."""
        self.result = None  # Signalisiert Abbruch
        self.animate_slide_out_to_right()

    def submit_data(self):
        """
        Validiert die Eingaben und schließt das Fenster.
        Die Logik (Ordner erstellen) wird NICHT mehr hier ausgeführt.
        """
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip().strip('"')
        mode = self.mode_var.get()

        # --- Nur Validierung ---
        if not name:
            messagebox.showerror(
                get_text("gui.create.error_title"), get_text("gui.create.error_no_name")
            )
            return

        if not path:
            messagebox.showerror(
                get_text("gui.create.error_title"), get_text("gui.create.error_no_path")
            )
            return

        path = os.path.normpath(path)

        if not os.path.isabs(path):
            messagebox.showerror(
                get_text("gui.create.error_title"),
                get_text("gui.create.error_path_not_absolute", path=path),
            )
            return

        # --- KORREKTUR: Bei Modus 2 den finalen Pfad erstellen ---
        if mode == "2":
            # Bei "Neu erstellen": Hänge den Namen an den übergeordneten Pfad
            final_path = os.path.join(path, name)
        else:
            # Bei "Vorhanden": Der Pfad ist bereits der finale Ordner
            final_path = path

        # --- Daten für die Rückgabe speichern ---
        self.result = {
            "name": name,
            "path": final_path,  # <-- Jetzt korrekt: finaler Pfad
            "create_if_missing": (mode == "2"),
        }

        # Fenster schließen
        self.animate_slide_out_to_right()


# --- Dies ist die "Brücken"-Funktion, die cli.py aufruft ---


def launch_create_desktop_dialog() -> dict | None:
    """
    Startet die Tkinter-GUI als blockierenden Dialog.
    Gibt die gesammelten Daten zurück oder None bei Abbruch.
    """
    try:
        root = tk.Tk()
        app = DesktopCreatorGUI(root)
        # mainloop() blockiert, bis root.destroy() aufgerufen wird
        root.mainloop()
        # Nach dem Schließen geben wir das Ergebnis zurück
        return app.result
    except Exception as e:
        print(f"Schwerwiegender GUI-Fehler: {e}")
        # Fallback auf Konsoleneingabe, falls Tkinter fehlschlägt
        # (Hier ausgelassen, um es einfach zu halten, aber cli.py könnte dies prüfen)
        return None
