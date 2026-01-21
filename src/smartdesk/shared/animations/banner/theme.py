# Dateipfad: src/smartdesk/shared/animations/banner/theme.py

"""
Theme-Konfiguration für das Banner.

Definiert Farben, Schriften und Icons.
Modernes Design mit Glasmorphism-Elementen.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BannerColors:
    """Farbschema für das Banner - Modern Dark Theme."""

    # Hauptfarben - Semi-transparent für Glasmorphism-Effekt
    background: str = "#1F1F23"  # Dunkler Hintergrund
    background_dark: str = "#18181B"  # Noch dunkler für Rahmen/Schatten
    surface: str = "#27272A"  # Oberfläche für Elemente

    # Akzentfarben
    accent: str = "#262729"  # Modernes Blau
    accent_hover: str = "#60A5FA"  # Helleres Blau für Hover
    accent_subtle: str = "#1E3A5F"  # Subtiles Blau für Hintergründe

    # Textfarben
    text_primary: str = "#F4F4F5"  # Fast-weiß für bessere Lesbarkeit
    text_secondary: str = "#A1A1AA"  # Gedämpftes Grau
    text_hover: str = "#FFFFFF"  # Reines Weiß für Hover
    text_muted: str = "#71717A"  # Stark gedämpft

    # Rahmen und Effekte
    border: str = "#3E4749"  # Subtiler Rahmen
    border_light: str = "#52525B"  # Hellerer Rahmen
    shadow: str = "#000000"  # Schatten

    # Status-Farben
    success: str = "#22C55E"  # Grün
    warning: str = "#F59E0B"  # Orange
    error: str = "#EF4444"  # Rot


# Alias für Kompatibilität
ColorScheme = BannerColors


@dataclass(frozen=True)
class BannerFonts:
    """Schrift-Konfiguration - Moderne Typografie."""

    primary_family: str = "Segoe UI Variable"  # Windows 11 Font
    fallback_family: str = "Segoe UI"  # Fallback für ältere Systeme
    emoji_family: str = "Segoe UI Emoji"

    # Größen
    message_size: int = 12
    message_weight: str = "bold"  # normal, bold
    icon_size: int = 1
    close_button_size: int = 1

    # Abstände
    letter_spacing: int = 0


# Alias für Kompatibilität
FontConfig = BannerFonts


@dataclass(frozen=True)
class BannerIcons:
    """Icons für das Banner - Unicode-Symbole."""

    # Seperator Icons
    separator: str = "│"  # Vertikaler Strich

    # UI Icons
    close: str = ""  # ✕ Multiplication X
    close_hover: str = ""  # ✖ Heavy Multiplication X

    # Status Icons
    info: str = ""  # ℹ Information
    warning: str = ""  # ⚠ Warning
    error: str = ""  # ✘ Heavy Ballot X
    success: str = ""  # ✔ Heavy Check Mark

    # Desktop-Status Icons
    active_marker_1: str = "●"  # ▶ Aktiver Desktop
    active_marker_2: str = ""  # ▶ Aktiver Desktop
    inactive_marker_1: str = ""  # ○ Inaktiver Desktop
    inactive_marker_2: str = ""  # ○ Inaktiver Desktop
    desktop_active: str = ""  # ■ Desktop-Icon (aktiv)
    desktop_inactive: str = ""  # □ Desktop-Icon (inaktiv)


# Alias für Kompatibilität
IconSet = BannerIcons


@dataclass(frozen=True)
class BannerTheme:
    """Vollständiges Theme für das Banner."""

    colors: BannerColors = None
    fonts: BannerFonts = None
    icons: BannerIcons = None

    def __post_init__(self):
        object.__setattr__(self, "colors", self.colors or BannerColors())
        object.__setattr__(self, "fonts", self.fonts or BannerFonts())
        object.__setattr__(self, "icons", self.icons or BannerIcons())


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
        background="#0F0F10",
        background_dark="#09090B",
        surface="#18181B",
        accent="#8B5CF6",  # Lila-Akzent
        accent_hover="#A78BFA",
        accent_subtle="#2E1065",
        text_primary="#FAFAFA",
        text_secondary="#A1A1AA",
        text_hover="#FFFFFF",
        text_muted="#52525B",
        border="#27272A",
        border_light="#3F3F46",
    ),
    fonts=BannerFonts(),
    icons=BannerIcons(),
)

LIGHT_THEME = BannerTheme(
    colors=BannerColors(
        background="#FFFFFF",
        background_dark="#F4F4F5",
        surface="#FAFAFA",
        accent="#2563EB",  # Kräftiges Blau
        accent_hover="#3B82F6",
        accent_subtle="#DBEAFE",
        text_primary="#18181B",
        text_secondary="#52525B",
        text_hover="#09090B",
        text_muted="#A1A1AA",
        border="#E4E4E7",
        border_light="#D4D4D8",
    ),
    fonts=BannerFonts(),
    icons=BannerIcons(),
)

ACCENT_THEME = BannerTheme(
    colors=BannerColors(
        background="#1E40AF",  # Tiefes Blau
        background_dark="#1E3A8A",
        surface="#2563EB",
        accent="#FFFFFF",
        accent_hover="#F0F9FF",
        accent_subtle="#3B82F6",
        text_primary="#FFFFFF",
        text_secondary="#BFDBFE",
        text_hover="#FFFFFF",
        text_muted="#93C5FD",
        border="#3B82F6",
        border_light="#60A5FA",
    ),
    fonts=BannerFonts(),
    icons=BannerIcons(),
)

# Glasmorphism Theme - Modern und subtil
GLASS_THEME = BannerTheme(
    colors=BannerColors(
        background="#1F1F23",
        background_dark="#18181B",
        surface="#27272A",
        accent="#06B6D4",  # Cyan-Akzent
        accent_hover="#22D3EE",
        accent_subtle="#164E63",
        text_primary="#F4F4F5",
        text_secondary="#A1A1AA",
        text_hover="#FFFFFF",
        text_muted="#71717A",
        border="#3F3F46",
        border_light="#52525B",
    ),
    fonts=BannerFonts(),
    icons=BannerIcons(),
)
