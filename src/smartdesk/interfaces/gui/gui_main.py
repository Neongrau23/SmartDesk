# Dateipfad: src/smartdesk/interfaces/gui/gui_main.py
# Moderne GUI für SmartDesk mit CustomTkinter

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import logging
import sys

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

# --- Projekt-Imports ---
try:
    from smartdesk.core.services import desktop_service
    from smartdesk.core.services import system_service
    from smartdesk.hotkeys import hotkey_manager
    from smartdesk.interfaces.tray import tray_manager
    from smartdesk.shared.config import DATA_DIR
    from smartdesk.shared.localization import get_text
    from smartdesk.shared.style import PREFIX_ERROR, PREFIX_OK, PREFIX_WARN

    desktop_handler = desktop_service
    system_manager = system_service
except ImportError as e:
    logger.error(f"FATALER IMPORT FEHLER: {e}")

    class FakeHandler:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                logger.debug(f"DEMO: {name} aufgerufen")
                return True

            return method

    desktop_handler = FakeHandler()
    desktop_service = FakeHandler()
    system_manager = FakeHandler()
    system_service = FakeHandler()
    hotkey_manager = FakeHandler()
    tray_manager = FakeHandler()

    def get_text(key, **kwargs):
        return key.split('.')[-1].replace('_', ' ').title()

    DATA_DIR = os.path.expanduser("~/SmartDesk")
    PREFIX_ERROR = "❌"
    PREFIX_OK = "✓"
    PREFIX_WARN = "⚠"

# Theme konfigurieren
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SmartDeskGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Fenster-Konfiguration
        self.title("SmartDesk Manager")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # Grid-Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Aktuelle Ansicht
        self.current_view = None

        # Sidebar erstellen
        self.create_sidebar()

        # Main Content Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Standard-Ansicht laden
        self.show_dashboard()

    def create_sidebar(self):
        """Erstellt die Sidebar mit Navigation"""
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        # Logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🖥️ SmartDesk",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Desktop Manager",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 30))

        # Navigation Buttons
        self.nav_buttons = {}

        nav_items = [
            ("dashboard", "📊 Dashboard", self.show_dashboard),
            ("desktops", "💻 Desktops", self.show_desktops),
            ("create", "➕ Neu erstellen", self.show_create),
            ("wallpaper", "🖼️ Wallpaper", self.show_wallpaper),
            ("hotkeys", "⌨️ Hotkeys", self.show_hotkeys),
            ("tray", "📌 Tray Icon", self.show_tray),
            ("settings", "⚙️ Einstellungen", self.show_settings),
        ]

        for idx, (key, text, command) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                command=command,
                height=45,
                font=ctk.CTkFont(size=14),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
            )
            btn.grid(row=idx, column=0, padx=15, pady=5, sticky="ew")
            self.nav_buttons[key] = btn

        # Theme Toggle (unten)
        self.theme_label = ctk.CTkLabel(
            self.sidebar_frame, text="Theme:", font=ctk.CTkFont(size=12)
        )
        self.theme_label.grid(row=9, column=0, padx=20, pady=(20, 5))

        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Dark", "Light", "System"],
            command=self.change_theme,
            width=200,
        )
        self.theme_menu.grid(row=10, column=0, padx=20, pady=(0, 30))
        self.theme_menu.set("Dark")

    def clear_main_frame(self):
        """Löscht den Hauptinhalt"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def highlight_nav_button(self, key):
        """Hebt den aktiven Navigation-Button hervor"""
        for btn_key, btn in self.nav_buttons.items():
            if btn_key == key:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

    def change_theme(self, mode):
        """Ändert das Theme"""
        ctk.set_appearance_mode(mode.lower())

    # --- DASHBOARD ANSICHT ---
    def show_dashboard(self):
        """Zeigt die Dashboard-Ansicht"""
        self.clear_main_frame()
        self.highlight_nav_button("dashboard")
        self.current_view = "dashboard"

        # Header
        header = ctk.CTkLabel(
            self.main_frame,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        header.grid(row=0, column=0, columnspan=3, padx=20, pady=(0, 30), sticky="w")

        # Statistik-Karten
        try:
            desktops = desktop_handler.get_all_desktops()
            total = len(desktops)
            active = sum(1 for d in desktops if d.is_active)
            inactive = total - active
        except:
            total, active, inactive = 0, 0, 0

        self.create_stat_card(
            self.main_frame, 1, 0, "Gesamt Desktops", str(total), "💻"
        )
        self.create_stat_card(self.main_frame, 1, 1, "Aktiv", str(active), "✓")
        self.create_stat_card(self.main_frame, 1, 2, "Inaktiv", str(inactive), "○")

        # Quick Actions Frame
        actions_frame = ctk.CTkFrame(self.main_frame)
        actions_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=20, sticky="ew")

        actions_title = ctk.CTkLabel(
            actions_frame,
            text="Schnellaktionen",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        actions_title.pack(padx=20, pady=(20, 10), anchor="w")

        # Quick Action Buttons
        btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        btn_frame.pack(padx=20, pady=(0, 20), fill="x")

        quick_actions = [
            ("➕ Neuer Desktop", self.show_create),
            ("🔄 Icons speichern", self.save_icons_action),
            ("🔁 Explorer neustarten", self.restart_explorer_action),
        ]

        for idx, (text, command) in enumerate(quick_actions):
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                height=50,
                font=ctk.CTkFont(size=14),
            )
            btn.grid(row=0, column=idx, padx=10, sticky="ew")
            btn_frame.grid_columnconfigure(idx, weight=1)

        # Status-Bereich
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.grid(
            row=3, column=0, columnspan=3, padx=20, pady=20, sticky="nsew"
        )
        self.main_frame.grid_rowconfigure(3, weight=1)

        status_title = ctk.CTkLabel(
            status_frame, text="System Status", font=ctk.CTkFont(size=18, weight="bold")
        )
        status_title.pack(padx=20, pady=(20, 10), anchor="w")

        # Status-Informationen
        self.status_text = ctk.CTkTextbox(
            status_frame, height=150, font=ctk.CTkFont(size=12)
        )
        self.status_text.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        self.update_status_info()

    def update_status_info(self):
        """Aktualisiert die Status-Informationen"""
        if not hasattr(self, 'status_text'):
            return

        self.status_text.delete("0.0", "end")

        try:
            # Hotkey Status
            hotkey_pid = hotkey_manager.get_listener_pid()
            hotkey_status = (
                f"✓ Aktiv (PID: {hotkey_pid})" if hotkey_pid else "○ Inaktiv"
            )

            # Tray Status
            tray_running, tray_pid = tray_manager.get_tray_status()
            tray_status = f"✓ Aktiv (PID: {tray_pid})" if tray_running else "○ Inaktiv"

            # Aktiver Desktop
            desktops = desktop_handler.get_all_desktops()
            active_desktop = next(
                (d.name for d in desktops if d.is_active), "Kein aktiver Desktop"
            )

            info = f"""Hotkey-Listener: {hotkey_status}
Tray-Icon: {tray_status}
Aktiver Desktop: {active_desktop}
Daten-Verzeichnis: {DATA_DIR}
"""
            self.status_text.insert("0.0", info)
        except Exception as e:
            self.status_text.insert(
                "0.0", f"Fehler beim Laden der Status-Informationen: {e}"
            )

    def create_stat_card(self, parent, row, col, title, value, icon):
        """Erstellt eine Statistik-Karte"""
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=36))
        icon_label.pack(padx=20, pady=(20, 5))

        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14))
        title_label.pack(padx=20, pady=5)

        value_label = ctk.CTkLabel(
            card, text=value, font=ctk.CTkFont(size=32, weight="bold")
        )
        value_label.pack(padx=20, pady=(5, 20))

    # --- DESKTOPS ANSICHT ---
    def show_desktops(self):
        """Zeigt die Desktop-Verwaltung"""
        self.clear_main_frame()
        self.highlight_nav_button("desktops")
        self.current_view = "desktops"

        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            header_frame,
            text="💻 Desktop-Verwaltung",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w")

        refresh_btn = ctk.CTkButton(
            header_frame, text="🔄 Aktualisieren", command=self.show_desktops, width=150
        )
        refresh_btn.grid(row=0, column=1, padx=10)

        # Desktop-Liste
        list_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Alle Desktops")
        list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)

        try:
            desktops = desktop_handler.get_all_desktops()

            if not desktops:
                no_data = ctk.CTkLabel(
                    list_frame,
                    text="Keine Desktops gefunden.\nErstelle einen neuen Desktop!",
                    font=ctk.CTkFont(size=16),
                    text_color="gray",
                )
                no_data.pack(pady=50)
            else:
                for desktop in desktops:
                    self.create_desktop_card(list_frame, desktop)
        except Exception as e:
            error_label = ctk.CTkLabel(
                list_frame, text=f"Fehler beim Laden: {e}", text_color="red"
            )
            error_label.pack(pady=20)

    def create_desktop_card(self, parent, desktop):
        """Erstellt eine Desktop-Karte"""
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", padx=10, pady=5)

        # Info-Bereich
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        # Name und Status
        name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_frame.pack(anchor="w")

        status_icon = "✓" if desktop.is_active else "○"
        status_color = "green" if desktop.is_active else "gray"

        status_label = ctk.CTkLabel(
            name_frame,
            text=status_icon,
            font=ctk.CTkFont(size=20),
            text_color=status_color,
        )
        status_label.pack(side="left", padx=(0, 10))

        name_label = ctk.CTkLabel(
            name_frame, text=desktop.name, font=ctk.CTkFont(size=18, weight="bold")
        )
        name_label.pack(side="left")

        # Pfad
        path_label = ctk.CTkLabel(
            info_frame,
            text=f"📁 {desktop.path}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        path_label.pack(anchor="w", pady=(5, 0))

        # Wallpaper Info
        if hasattr(desktop, 'wallpaper_path') and desktop.wallpaper_path:
            wallpaper_label = ctk.CTkLabel(
                info_frame,
                text=f"🖼️ {os.path.basename(desktop.wallpaper_path)}",
                font=ctk.CTkFont(size=12),
                text_color="gray",
            )
            wallpaper_label.pack(anchor="w", pady=(2, 0))

        # Button-Bereich
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=10)

        # Switch Button
        if not desktop.is_active:
            switch_btn = ctk.CTkButton(
                btn_frame,
                text="Wechseln",
                command=lambda d=desktop: self.switch_desktop(d.name),
                width=100,
                fg_color="green",
                hover_color="darkgreen",
            )
            switch_btn.pack(pady=2)

        # Delete Button
        if not desktop.is_active:
            delete_btn = ctk.CTkButton(
                btn_frame,
                text="Löschen",
                command=lambda d=desktop: self.delete_desktop(d.name),
                width=100,
                fg_color="red",
                hover_color="darkred",
            )
            delete_btn.pack(pady=2)

    def switch_desktop(self, name):
        """Wechselt zu einem Desktop"""
        if messagebox.askyesno(
            "Desktop wechseln",
            f"Möchtest du zu '{name}' wechseln?\n\nDer Explorer wird neu gestartet.",
        ):
            try:
                if desktop_handler.switch_to_desktop(name):
                    system_manager.restart_explorer()
                    messagebox.showinfo("Erfolg", f"Desktop '{name}' wurde aktiviert!")
                    self.show_desktops()
                else:
                    messagebox.showerror(
                        "Fehler", "Desktop konnte nicht gewechselt werden."
                    )
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Wechseln: {e}")

    def delete_desktop(self, name):
        """Löscht einen Desktop"""
        desktop = next(
            (d for d in desktop_handler.get_all_desktops() if d.name == name), None
        )
        if not desktop:
            return

        result = messagebox.askyesnocancel(
            "Desktop löschen",
            f"Desktop '{name}' löschen?\n\n"
            f"Pfad: {desktop.path}\n\n"
            f"Ja = Nur Eintrag löschen\n"
            f"Nein = Eintrag + Ordner löschen\n"
            f"Abbrechen = Nichts tun",
        )

        if result is None:  # Abbrechen
            return

        delete_folder = result is False  # Nein = Ordner löschen

        try:
            desktop_handler.delete_desktop(name, delete_folder=delete_folder)
            messagebox.showinfo("Erfolg", f"Desktop '{name}' wurde gelöscht.")
            self.show_desktops()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen: {e}")

    # --- DESKTOP ERSTELLEN ---
    def show_create(self):
        """Zeigt die Desktop-Erstellung"""
        self.clear_main_frame()
        self.highlight_nav_button("create")
        self.current_view = "create"

        # Header
        header = ctk.CTkLabel(
            self.main_frame,
            text="➕ Neuen Desktop erstellen",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(0, 30), sticky="w")

        # Formular
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        # Name
        name_label = ctk.CTkLabel(
            form_frame, text="Desktop-Name:", font=ctk.CTkFont(size=16, weight="bold")
        )
        name_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        self.create_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="z.B. Arbeit, Gaming, Privat",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        self.create_name_entry.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)

        # Modus-Auswahl
        mode_label = ctk.CTkLabel(
            form_frame,
            text="Modus auswählen:",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        mode_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")

        self.create_mode = ctk.StringVar(value="existing")

        mode_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        mode_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        existing_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Vorhandenen Ordner verwenden",
            variable=self.create_mode,
            value="existing",
            font=ctk.CTkFont(size=14),
            command=self.update_create_mode,
        )
        existing_radio.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        new_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Neuen Ordner erstellen",
            variable=self.create_mode,
            value="new",
            font=ctk.CTkFont(size=14),
            command=self.update_create_mode,
        )
        new_radio.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Pfad-Eingabe
        path_label = ctk.CTkLabel(
            form_frame, text="Pfad:", font=ctk.CTkFont(size=16, weight="bold")
        )
        path_label.grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")

        path_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        path_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        path_frame.grid_columnconfigure(0, weight=1)

        self.create_path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="Ordner-Pfad auswählen",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        self.create_path_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        browse_btn = ctk.CTkButton(
            path_frame,
            text="📁 Durchsuchen",
            command=self.browse_folder,
            width=150,
            height=40,
        )
        browse_btn.grid(row=0, column=1)

        # Hinweis-Text
        self.create_hint = ctk.CTkLabel(
            form_frame,
            text="Wähle einen vorhandenen Ordner aus",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.create_hint.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="w")

        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=7, column=0, padx=20, pady=(10, 20), sticky="ew")

        create_btn = ctk.CTkButton(
            btn_frame,
            text="✓ Desktop erstellen",
            command=self.create_desktop_action,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen",
        )
        create_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="✕ Abbrechen",
            command=self.show_dashboard,
            height=50,
            font=ctk.CTkFont(size=16),
            fg_color="gray",
            hover_color="darkgray",
        )
        cancel_btn.pack(side="left", fill="x", expand=True)

    def update_create_mode(self):
        """Aktualisiert die Hinweise basierend auf dem gewählten Modus"""
        if self.create_mode.get() == "existing":
            self.create_hint.configure(text="Wähle einen vorhandenen Ordner aus")
        else:
            self.create_hint.configure(
                text="Wähle einen übergeordneten Ordner, in dem der neue Ordner erstellt wird"
            )

    def browse_folder(self):
        """Öffnet einen Ordner-Browser"""
        folder = filedialog.askdirectory(title="Ordner auswählen")
        if folder:
            self.create_path_entry.delete(0, "end")
            self.create_path_entry.insert(0, folder)

    def create_desktop_action(self):
        """Erstellt einen neuen Desktop"""
        name = self.create_name_entry.get().strip()
        path = self.create_path_entry.get().strip()

        if not name:
            messagebox.showerror("Fehler", "Bitte gib einen Namen ein!")
            return

        if not path:
            messagebox.showerror("Fehler", "Bitte wähle einen Pfad aus!")
            return

        try:
            if self.create_mode.get() == "existing":
                # Vorhandener Ordner
                if not os.path.exists(path):
                    messagebox.showerror(
                        "Fehler", "Der ausgewählte Ordner existiert nicht!"
                    )
                    return
                desktop_handler.create_desktop(name, path, create_if_missing=False)
            else:
                # Neuer Ordner
                final_path = os.path.join(path, name)
                desktop_handler.create_desktop(name, final_path, create_if_missing=True)

            messagebox.showinfo("Erfolg", f"Desktop '{name}' wurde erstellt!")
            self.show_desktops()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen: {e}")

    # --- WALLPAPER ANSICHT ---
    def show_wallpaper(self):
        """Zeigt die Wallpaper-Verwaltung"""
        self.clear_main_frame()
        self.highlight_nav_button("wallpaper")
        self.current_view = "wallpaper"

        # Header
        header = ctk.CTkLabel(
            self.main_frame,
            text="🖼️ Wallpaper-Verwaltung",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(0, 30), sticky="w")

        # Desktop-Auswahl
        select_frame = ctk.CTkFrame(self.main_frame)
        select_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        select_label = ctk.CTkLabel(
            select_frame,
            text="Desktop auswählen:",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        select_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        try:
            desktops = desktop_handler.get_all_desktops()
            desktop_names = [d.name for d in desktops]
        except:
            desktop_names = []

        if not desktop_names:
            no_desktop = ctk.CTkLabel(
                select_frame, text="Keine Desktops vorhanden", text_color="gray"
            )
            no_desktop.grid(row=1, column=0, padx=20, pady=(0, 20))
            return

        self.wallpaper_desktop_var = ctk.StringVar(value=desktop_names[0])
        desktop_menu = ctk.CTkOptionMenu(
            select_frame,
            variable=self.wallpaper_desktop_var,
            values=desktop_names,
            width=300,
            height=35,
            font=ctk.CTkFont(size=14),
        )
        desktop_menu.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Wallpaper-Datei
        file_label = ctk.CTkLabel(
            select_frame,
            text="Wallpaper-Datei:",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        file_label.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="w")

        file_frame = ctk.CTkFrame(select_frame, fg_color="transparent")
        file_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        select_frame.grid_columnconfigure(0, weight=1)
        file_frame.grid_columnconfigure(0, weight=1)

        self.wallpaper_path_entry = ctk.CTkEntry(
            file_frame,
            placeholder_text="Wallpaper auswählen (JPG, PNG, BMP)",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        self.wallpaper_path_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        browse_btn = ctk.CTkButton(
            file_frame,
            text="📁 Durchsuchen",
            command=self.browse_wallpaper,
            width=150,
            height=40,
        )
        browse_btn.grid(row=0, column=1)

        # Button
        assign_btn = ctk.CTkButton(
            select_frame,
            text="✓ Wallpaper zuweisen",
            command=self.assign_wallpaper_action,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        assign_btn.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")

    def browse_wallpaper(self):
        """Öffnet einen Datei-Browser für Wallpaper"""
        file = filedialog.askopenfilename(
            title="Wallpaper auswählen",
            filetypes=[("Bilder", "*.jpg *.jpeg *.png *.bmp"), ("Alle Dateien", "*.*")],
        )
        if file:
            self.wallpaper_path_entry.delete(0, "end")
            self.wallpaper_path_entry.insert(0, file)

    def assign_wallpaper_action(self):
        """Weist einem Desktop ein Wallpaper zu"""
        desktop_name = self.wallpaper_desktop_var.get()
        wallpaper_path = self.wallpaper_path_entry.get().strip()

        if not wallpaper_path:
            messagebox.showerror("Fehler", "Bitte wähle eine Wallpaper-Datei aus!")
            return

        if not os.path.exists(wallpaper_path):
            messagebox.showerror("Fehler", "Die ausgewählte Datei existiert nicht!")
            return

        try:
            desktop_handler.assign_wallpaper(desktop_name, wallpaper_path)
            messagebox.showinfo(
                "Erfolg", f"Wallpaper wurde '{desktop_name}' zugewiesen!"
            )
            self.wallpaper_path_entry.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Zuweisen: {e}")

    # --- HOTKEYS ANSICHT ---
    def show_hotkeys(self):
        """Zeigt die Hotkey-Verwaltung"""
        self.clear_main_frame()
        self.highlight_nav_button("hotkeys")
        self.current_view = "hotkeys"

        # Header
        header = ctk.CTkLabel(
            self.main_frame,
            text="⌨️ Hotkey-Verwaltung",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(0, 30), sticky="w")

        # Status
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        try:
            pid = hotkey_manager.get_listener_pid()
            is_active = pid is not None
            status_text = f"✓ Aktiv (PID: {pid})" if is_active else "○ Inaktiv"
            status_color = "green" if is_active else "gray"
        except:
            status_text = "○ Status unbekannt"
            status_color = "gray"
            is_active = False

        status_label = ctk.CTkLabel(
            status_frame,
            text=f"Status: {status_text}",
            font=ctk.CTkFont(size=18),
            text_color=status_color,
        )
        status_label.pack(padx=20, pady=20)

        # Buttons
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        if is_active:
            stop_btn = ctk.CTkButton(
                btn_frame,
                text="⏹️ Listener stoppen",
                command=self.stop_hotkeys,
                height=50,
                font=ctk.CTkFont(size=16),
                fg_color="red",
                hover_color="darkred",
            )
            stop_btn.pack(fill="x", pady=5)
        else:
            start_btn = ctk.CTkButton(
                btn_frame,
                text="▶️ Listener starten",
                command=self.start_hotkeys,
                height=50,
                font=ctk.CTkFont(size=16),
                fg_color="green",
                hover_color="darkgreen",
            )
            start_btn.pack(fill="x", pady=5)

        log_btn = ctk.CTkButton(
            btn_frame,
            text="📋 Log anzeigen",
            command=self.show_hotkey_log,
            height=50,
            font=ctk.CTkFont(size=16),
        )
        log_btn.pack(fill="x", pady=5)

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Status aktualisieren",
            command=self.show_hotkeys,
            height=50,
            font=ctk.CTkFont(size=16),
            fg_color="gray",
            hover_color="darkgray",
        )
        refresh_btn.pack(fill="x", pady=5)

    def start_hotkeys(self):
        """Startet den Hotkey-Listener"""
        try:
            hotkey_manager.start_listener()
            messagebox.showinfo("Erfolg", "Hotkey-Listener wurde gestartet!")
            self.show_hotkeys()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Starten: {e}")

    def stop_hotkeys(self):
        """Stoppt den Hotkey-Listener"""
        try:
            hotkey_manager.stop_listener()
            messagebox.showinfo("Erfolg", "Hotkey-Listener wurde gestoppt!")
            self.show_hotkeys()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Stoppen: {e}")

    def show_hotkey_log(self):
        """Zeigt das Hotkey-Log"""
        log_file = os.path.join(DATA_DIR, "listener.log")

        if not os.path.exists(log_file):
            messagebox.showinfo("Info", "Keine Log-Datei gefunden.")
            return

        # Log-Fenster
        log_window = ctk.CTkToplevel(self)
        log_window.title("Hotkey-Log")
        log_window.geometry("800x600")

        log_text = ctk.CTkTextbox(
            log_window, font=ctk.CTkFont(family="Courier", size=12)
        )
        log_text.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                log_text.insert("0.0", content)
        except Exception as e:
            log_text.insert("0.0", f"Fehler beim Lesen: {e}")

    # --- TRAY ANSICHT ---
    def show_tray(self):
        """Zeigt die Tray-Verwaltung"""
        self.clear_main_frame()
        self.highlight_nav_button("tray")
        self.current_view = "tray"

        # Header
        header = ctk.CTkLabel(
            self.main_frame,
            text="📌 Tray Icon-Verwaltung",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(0, 30), sticky="w")

        # Status
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        try:
            is_running, pid = tray_manager.get_tray_status()
            status_text = f"✓ Aktiv (PID: {pid})" if is_running else "○ Inaktiv"
            status_color = "green" if is_running else "gray"
        except:
            status_text = "○ Status unbekannt"
            status_color = "gray"
            is_running = False

        status_label = ctk.CTkLabel(
            status_frame,
            text=f"Status: {status_text}",
            font=ctk.CTkFont(size=18),
            text_color=status_color,
        )
        status_label.pack(padx=20, pady=20)

        # Buttons
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        if is_running:
            stop_btn = ctk.CTkButton(
                btn_frame,
                text="⏹️ Tray Icon stoppen",
                command=self.stop_tray,
                height=50,
                font=ctk.CTkFont(size=16),
                fg_color="red",
                hover_color="darkred",
            )
            stop_btn.pack(fill="x", pady=5)
        else:
            start_btn = ctk.CTkButton(
                btn_frame,
                text="▶️ Tray Icon starten",
                command=self.start_tray,
                height=50,
                font=ctk.CTkFont(size=16),
                fg_color="green",
                hover_color="darkgreen",
            )
            start_btn.pack(fill="x", pady=5)

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Status aktualisieren",
            command=self.show_tray,
            height=50,
            font=ctk.CTkFont(size=16),
            fg_color="gray",
            hover_color="darkgray",
        )
        refresh_btn.pack(fill="x", pady=5)

    def start_tray(self):
        """Startet das Tray Icon"""
        try:
            tray_manager.start_tray()
            messagebox.showinfo("Erfolg", "Tray Icon wurde gestartet!")
            self.show_tray()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Starten: {e}")

    def stop_tray(self):
        """Stoppt das Tray Icon"""
        try:
            tray_manager.stop_tray()
            messagebox.showinfo("Erfolg", "Tray Icon wurde gestoppt!")
            self.show_tray()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Stoppen: {e}")

    # --- EINSTELLUNGEN ANSICHT ---
    def show_settings(self):
        """Zeigt die Einstellungen"""
        self.clear_main_frame()
        self.highlight_nav_button("settings")
        self.current_view = "settings"

        # Header
        header = ctk.CTkLabel(
            self.main_frame,
            text="⚙️ Einstellungen",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(0, 30), sticky="w")

        # Buttons-Container
        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)

        settings_actions = [
            (
                "🔄 Icons speichern",
                self.save_icons_action,
                "Speichert die aktuelle Icon-Position",
            ),
            (
                "🔁 Explorer neustarten",
                self.restart_explorer_action,
                "Startet den Windows Explorer neu",
            ),
            (
                "🔧 Registry wiederherstellen",
                self.restore_registry_action,
                "Stellt Registry-Pfade wieder her",
            ),
        ]

        for idx, (text, command, description) in enumerate(settings_actions):
            btn_container = ctk.CTkFrame(settings_frame)
            btn_container.pack(fill="x", padx=20, pady=10)

            btn = ctk.CTkButton(
                btn_container,
                text=text,
                command=command,
                height=50,
                font=ctk.CTkFont(size=16),
                anchor="w",
            )
            btn.pack(fill="x", padx=10, pady=(10, 5))

            desc = ctk.CTkLabel(
                btn_container,
                text=description,
                font=ctk.CTkFont(size=12),
                text_color="gray",
            )
            desc.pack(anchor="w", padx=10, pady=(0, 10))

        # Info-Bereich
        info_frame = ctk.CTkFrame(settings_frame)
        info_frame.pack(fill="x", padx=20, pady=20)

        info_label = ctk.CTkLabel(
            info_frame,
            text=f"Daten-Verzeichnis:\n{DATA_DIR}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        info_label.pack(padx=20, pady=20)

    def save_icons_action(self):
        """Speichert die aktuellen Desktop-Icons"""
        try:
            desktop_handler.save_current_desktop_icons()
            messagebox.showinfo("Erfolg", "Desktop-Icons wurden gespeichert!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def restart_explorer_action(self):
        """Startet den Explorer neu"""
        if messagebox.askyesno(
            "Explorer neustarten",
            "Möchtest du den Windows Explorer wirklich neu starten?",
        ):
            try:
                system_manager.restart_explorer()
                messagebox.showinfo("Erfolg", "Explorer wurde neu gestartet!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Neustart: {e}")

    def restore_registry_action(self):
        """Stellt die Registry wieder her"""
        if messagebox.askyesno(
            "Registry wiederherstellen",
            "Möchtest du die Registry-Pfade wirklich wiederherstellen?",
        ):
            try:
                import subprocess
                import platform

                if platform.system() != "Windows":
                    messagebox.showerror("Fehler", "Nur unter Windows verfügbar!")
                    return

                script_path = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        '..',
                        '..',
                        '..',
                        'scripts',
                        'restore.bat',
                    )
                )

                if not os.path.exists(script_path):
                    messagebox.showerror(
                        "Fehler", f"Skript nicht gefunden:\n{script_path}"
                    )
                    return

                subprocess.call(['cmd', '/c', script_path])
                messagebox.showinfo(
                    "Erfolg", "Registry-Wiederherstellung abgeschlossen!"
                )
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler bei der Wiederherstellung: {e}")


def launch_gui():
    """Startet die GUI-Anwendung mit PID-Management."""
    # PID-Datei Pfad
    try:
        pid_dir = os.path.join(os.environ['APPDATA'], 'SmartDesk')
        pid_file = os.path.join(pid_dir, 'gui_main.pid')
        os.makedirs(pid_dir, exist_ok=True)

        # Eigene PID speichern
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
    except Exception as e:
        logger.error(f"Fehler beim Speichern der PID: {e}")
        pid_file = None

    def cleanup_pid():
        """Räumt die PID-Datei beim Beenden auf."""
        try:
            if pid_file and os.path.exists(pid_file):
                os.remove(pid_file)
                logger.debug("PID-Datei entfernt")
        except Exception:
            pass

    # Cleanup registrieren
    import atexit

    atexit.register(cleanup_pid)

    app = SmartDeskGUI()
    app.mainloop()

    # Cleanup nach mainloop
    cleanup_pid()


if __name__ == "__main__":
    launch_gui()
