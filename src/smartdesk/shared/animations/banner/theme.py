# Dateipfad: src/smartdesk/shared/animations/banner/theme.py

"""
Theme-Konfiguration für das Banner.

Definiert Farben, Schriften und Icons.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BannerColors:
    """Farbschema für das Banner."""

    background: str = "#2D2D30"       # Dunkler Hintergrund
    background_dark: str = "#1E1E1E"  # Noch dunkler für Rahmen
    accent: str = "#0078D4"           # Windows-Blau
    text_primary: str = "#FFFFFF"     # Weißer Text
    text_secondary: str = "#808080"   # Grauer Text
    text_hover: str = "#FFFFFF"       # Hover-Farbe
    border: str = "#3F3F46"           # Rahmenfarbe


# Alias für Kompatibilität
ColorScheme = BannerColors


@dataclass(frozen=True)
class BannerFonts:
    """Schrift-Konfiguration."""

    primary_family: str = "Segoe UI"
    emoji_family: str = "Segoe UI Emoji"
    message_size: int = 11
    icon_size: int = 16
    close_button_size: int = 12


# Alias für Kompatibilität
FontConfig = BannerFonts


@dataclass(frozen=True)
class BannerIcons:
    """Icons für das Banner."""

    close: str = "X"              # Schließen-Button
    info: str = "i"               # Info-Icon
    warning: str = "!"            # Warnung
    error: str = "X"              # Fehler
    success: str = "OK"           # Erfolg
    # Desktop-Status Icons
    active_marker: str = ">"      # Aktiver Desktop
    inactive_marker: str = "-"    # Inaktiver Desktop
    desktop_active: str = "D"     # Desktop-Icon (aktiv)
    desktop_inactive: str = "D"   # Desktop-Icon (inaktiv)


# Alias für Kompatibilität
IconSet = BannerIcons


@dataclass(frozen=True)
class BannerTheme:
    """Vollständiges Theme für das Banner."""

    colors: BannerColors = None
    fonts: BannerFonts = None
    icons: BannerIcons = None

    def __post_init__(self):
        object.__setattr__(self, 'colors', self.colors or BannerColors())
        object.__setattr__(self, 'fonts', self.fonts or BannerFonts())
        object.__setattr__(self, 'icons', self.icons or BannerIcons())


# =============================================================================
# Vordefinierte Themes
# =============================================================================

DEFAULT_THEME = BannerTheme(
    colors=BannerColors(),
    fonts=BannerFonts(),
    icons=BannerIcons(),
)

DARK_THEME = BannerTheme(
    colors=BannerColors(
        background="#1E1E1E",
        background_dark="#141414",
        accent="#0078D4",
        text_primary="#FFFFFF",
        text_secondary="#808080",
        border="#2D2D30",
    ),
    fonts=BannerFonts(),
    icons=BannerIcons(),
)

LIGHT_THEME = BannerTheme(
    colors=BannerColors(
        background="#F3F3F3",
        background_dark="#E5E5E5",
        accent="#0078D4",
        text_primary="#1E1E1E",
        text_secondary="#666666",
        text_hover="#000000",
        border="#CCCCCC",
    ),
    fonts=BannerFonts(),
    icons=BannerIcons(),
)

ACCENT_THEME = BannerTheme(
    colors=BannerColors(
        background="#0078D4",
        background_dark="#005A9E",
        accent="#FFFFFF",
        text_primary="#FFFFFF",
        text_secondary="#B3D7F2",
        text_hover="#FFFFFF",
        border="#005A9E",
    ),
    fonts=BannerFonts(),
    icons=BannerIcons(),
)
