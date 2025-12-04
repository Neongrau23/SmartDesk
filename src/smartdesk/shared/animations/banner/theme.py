# Dateipfad: src/smartdesk/shared/animations/banner/theme.py
"""
Theme-Definitionen für das TaskbarBanner.

Hier werden alle visuellen Aspekte definiert:
- Farben
- Schriftarten
- Icons/Emojis

Um das Design anzupassen, bearbeite diese Datei.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class BannerColors:
    """Farbschema für das Banner."""
    
    # Hintergrund
    background: str = "#1a1a1a"
    background_dark: str = "#000000"
    
    # Akzent (oberer Streifen)
    accent: str = "#0078d4"
    
    # Text
    text_primary: str = "#ffffff"
    text_secondary: str = "#8a8a8a"
    text_hover: str = "#ffffff"
    
    # Rahmen
    border: str = "#404040"
    
    # Status-Farben
    success: str = "#4caf50"
    warning: str = "#ff9800"
    error: str = "#f44336"
    info: str = "#2196f3"


@dataclass
class BannerFonts:
    """Schriftarten für das Banner."""
    
    # Font-Familien
    primary_family: str = "Segoe UI"
    emoji_family: str = "Segoe UI Emoji"
    
    # Größen
    message_size: int = 11
    icon_size: int = 18
    close_button_size: int = 12


@dataclass
class BannerIcons:
    """Icons/Emojis für verschiedene Status."""
    
    # Standard-Icons
    info: str = "ℹ"
    success: str = "✓"
    warning: str = "⚠"
    error: str = "❌"
    
    # Desktop-Status
    desktop_active: str = "💻"
    desktop_inactive: str = "🔔"
    
    # UI-Elemente
    close: str = "✕"
    
    # Marker für aktive/inaktive Desktops
    active_marker: str = "▶"
    inactive_marker: str = "•"


@dataclass
class BannerTheme:
    """
    Komplettes Theme für das Banner.
    
    Verwendung:
        theme = BannerTheme()  # Standard-Theme
        
        # Oder angepasst:
        theme = BannerTheme(
            colors=BannerColors(accent="#ff5722"),
            fonts=BannerFonts(message_size=14)
        )
    """
    colors: BannerColors = field(default_factory=BannerColors)
    fonts: BannerFonts = field(default_factory=BannerFonts)
    icons: BannerIcons = field(default_factory=BannerIcons)


# =============================================================================
# Vordefinierte Themes
# =============================================================================

# Standard-Theme (Windows 11 inspiriert)
DEFAULT_THEME = BannerTheme()

# Dunkles Theme
DARK_THEME = BannerTheme(
    colors=BannerColors(
        background="#0d0d0d",
        accent="#0078d4",
        border="#333333"
    )
)

# Helles Theme
LIGHT_THEME = BannerTheme(
    colors=BannerColors(
        background="#f5f5f5",
        background_dark="#ffffff",
        text_primary="#000000",
        text_secondary="#666666",
        border="#cccccc"
    )
)

# Akzent-Theme (Orange)
ACCENT_THEME = BannerTheme(
    colors=BannerColors(
        accent="#ff5722",
        background="#1a1a1a"
    )
)
