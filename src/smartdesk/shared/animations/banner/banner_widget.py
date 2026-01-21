# Dateipfad: src/smartdesk/shared/animations/banner/banner_widget.py

"""

UI-Widget für das TaskbarBanner.

Enthält nur die visuelle Darstellung (Tkinter-Komponenten).
Keine Logik, nur UI-Aufbau.
"""

import tkinter as tk
import tkinter.font as tkFont
import sys
from typing import Optional, Callable

from .theme import BannerTheme, DEFAULT_THEME
from .config import BannerConfig, DEFAULT_CONFIG


class BannerWidget:
    """
    Reine UI-Komponente für das Banner.

    Verantwortlich für:
    - Fenster-Erstellung
    - UI-Layout
    - Visuelle Darstellung

    NICHT verantwortlich für:
    - Animationen
    - Geschäftslogik
    - Event-Handling (außer Close-Button)
    """

    def __init__(
        self,
        message: str = "Benachrichtigung",
        icon: str = "i",
        theme: Optional[BannerTheme] = None,
        config: Optional[BannerConfig] = None,
        on_close: Optional[Callable[[], None]] = None,
        parent: Optional[tk.Tk] = None,
    ):
        self.message = message
        self.icon = icon
        self.theme = theme or DEFAULT_THEME
        self.config = config or DEFAULT_CONFIG
        self.on_close_callback = on_close

        # Root-Fenster
        if parent:
            self.root = tk.Toplevel(parent)
            self._owns_root = False
        else:
            self.root = tk.Tk()
            self.root.withdraw()
            self._owns_root = True

        # UI-Referenzen
        self.message_label: Optional[tk.Label] = None
        self.icon_label: Optional[tk.Label] = None
        self.message_font: Optional[tkFont.Font] = None

        self._setup_window()
        self._create_ui()

    def _setup_window(self) -> None:
        """Konfiguriert das Fenster."""
        self.root.title("")
        self.root.overrideredirect(True)
        self.root.configure(bg=self.theme.colors.background_dark)

        if sys.platform == "win32":
            if self.config.behavior.always_on_top:
                self.root.wm_attributes("-topmost", 1)
            if self.config.behavior.tool_window:
                self.root.attributes("-toolwindow", True)
        else:
            if self.config.behavior.always_on_top:
                self.root.attributes("-topmost", True)

        # Starte unsichtbar
        self.root.attributes("-alpha", 0.0)

    def _create_ui(self) -> None:
        """Erstellt die UI-Elemente mit modernem Design."""
        theme = self.theme
        cfg = self.config.size

        # Hole Farben mit Fallbacks für Kompatibilität
        bg_color = theme.colors.background
        surface_color = getattr(theme.colors, "surface", theme.colors.background)
        accent_color = theme.colors.accent
        border_color = theme.colors.border

        # Äußerer Frame für Schatten-Effekt (dunklerer Rand)
        shadow_frame = tk.Frame(
            self.root,
            bg=theme.colors.background_dark,
        )
        shadow_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Hauptframe mit feinem Rahmen
        main_frame = tk.Frame(
            shadow_frame,
            bg=bg_color,
            highlightbackground=border_color,
            highlightthickness=1,
        )
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Dezenter Akzent-Streifen am linken Rand (moderner als oben)
        accent_stripe = tk.Frame(
            main_frame,
            bg=accent_color,
            width=3,  # Schmal und elegant
        )
        accent_stripe.pack(side=tk.LEFT, fill=tk.Y)

        # Content-Frame mit etwas mehr Padding
        content_frame = tk.Frame(main_frame, bg=bg_color)
        content_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=(cfg.content_padding_x, cfg.content_padding_x),
            pady=cfg.content_padding_y,
        )

        # Icon-Container mit modernem rundem Design
        icon_size = 26
        icon_frame = tk.Frame(
            content_frame,
            bg=accent_color,
            width=icon_size,
            height=icon_size,
        )
        icon_frame.pack(side=tk.LEFT, padx=(0, cfg.icon_padding_right))
        icon_frame.pack_propagate(False)

        # Icon zentriert im Container
        self.icon_label = tk.Label(
            icon_frame,
            text=self.icon,
            font=(theme.fonts.primary_family, theme.fonts.icon_size),
            fg=theme.colors.text_primary,
            bg=accent_color,
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Nachricht mit verbesserter Typografie
        font_family = theme.fonts.primary_family
        fallback = getattr(theme.fonts, "fallback_family", "Segoe UI")

        self.message_font = tkFont.Font(
            family=font_family,
            size=theme.fonts.message_size,
        )

        self.message_label = tk.Label(
            content_frame,
            text=self.message,
            font=self.message_font,
            fg=theme.colors.text_primary,
            bg=bg_color,
            anchor="w",
        )
        self.message_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Moderner Schließen-Button mit Hover-Effekt
        close_btn_bg = bg_color
        close_btn = tk.Label(
            content_frame,
            text=theme.icons.close,
            font=(theme.fonts.primary_family, theme.fonts.close_button_size),
            fg=theme.colors.text_secondary,
            bg=close_btn_bg,
            cursor="hand2",
            padx=8,
            pady=4,
        )
        close_btn.pack(side=tk.RIGHT)

        # Speichere Referenz für Hover
        self._close_btn = close_btn
        self._close_btn_bg = close_btn_bg

        # Hover-Effekte
        def on_enter(e):
            close_btn.config(
                fg=theme.colors.text_hover,
                bg=getattr(theme.colors, "surface", bg_color),
            )

        def on_leave(e):
            close_btn.config(
                fg=theme.colors.text_secondary,
                bg=close_btn_bg,
            )

        close_btn.bind("<Button-1>", lambda e: self._on_close_click())
        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)

    def _on_close_click(self) -> None:
        """Handler für Schließen-Button."""
        if self.on_close_callback:
            self.on_close_callback()

    def calculate_geometry(self) -> tuple:
        """
        Berechnet Fensterposition und -größe.

        Returns:
            Tuple (window_width, window_height, x_pos, target_y, start_y)
        """
        cfg_size = self.config.size
        cfg_pos = self.config.position

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Breite basierend auf Text + mehr Padding für modernes Aussehen
        text_width = self.message_font.measure(self.message)
        static_width = 40 + cfg_size.content_padding_x * 2 + cfg_size.close_button_padding_x * 2 + 30  # Icon + Padding  # Extra Breathing Room
        calculated_width = text_width + static_width

        max_width = screen_width - cfg_size.max_width_margin * 2
        window_width = max(cfg_size.min_width, min(calculated_width, max_width))
        window_height = cfg_size.height

        # Horizontale Position
        if cfg_pos.horizontal_align == "left":
            x_pos = cfg_pos.margin_horizontal
        elif cfg_pos.horizontal_align == "right":
            x_pos = screen_width - window_width - cfg_pos.margin_horizontal
        else:  # center
            x_pos = (screen_width - window_width) // 2

        # Vertikale Position - etwas höher für bessere Sichtbarkeit
        target_y = screen_height - window_height - cfg_pos.margin_bottom
        start_y = screen_height + 10  # Etwas unterhalb

        return window_width, window_height, x_pos, target_y, start_y

    def set_geometry(self, width: int, height: int, x: int, y: int) -> None:
        """Setzt die Fenstergeometrie."""
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def update_message(self, message: str, icon: Optional[str] = None) -> None:
        """Aktualisiert den angezeigten Text."""
        self.message = message
        if self.message_label:
            self.message_label.config(text=message)

        if icon and self.icon_label:
            self.icon = icon
            self.icon_label.config(text=icon)

    def show(self) -> None:
        """Zeigt das Fenster an (ohne Animation)."""
        self.root.deiconify()
        self.root.update()
        self.root.lift()

    def hide(self) -> None:
        """Versteckt das Fenster."""
        self.root.withdraw()

    def destroy(self) -> None:
        """Zerstört das Fenster."""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    @property
    def window(self) -> tk.Toplevel:
        """Gibt das Tkinter-Fenster zurück."""
        return self.root
