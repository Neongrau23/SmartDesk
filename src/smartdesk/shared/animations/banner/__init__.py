# Dateipfad: src/smartdesk/shared/animations/banner/__init__.py
"""
Banner-Modul für SmartDesk.

Stellt animierte Taskbar-Benachrichtigungen bereit.

Struktur:
- theme.py      - Farben, Fonts, Icons
- config.py     - Größen, Positionen, Timing
- animations.py - Slide/Fade Animationen
- banner_widget.py - Reine UI-Komponente
- banner.py     - Hauptklasse (Orchestrierung)

Verwendung:
    from smartdesk.shared.animations.banner import (
        TaskbarBanner,
        show_notification,
        show_desktop_status
    )

    # Einfache Benachrichtigung
    show_notification("Hallo Welt!", icon="🎉", auto_close_ms=3000)

    # Mit Theme
    from smartdesk.shared.animations.banner import DARK_THEME
    banner = TaskbarBanner(message="Dunkel", theme=DARK_THEME)
    banner.show()
"""

# Haupt-API
from .banner import TaskbarBanner, show_desktop_status, show_notification

# Theme
from .theme import (
    BannerTheme,
    BannerColors,
    BannerFonts,
    BannerIcons,
    DEFAULT_THEME,
    DARK_THEME,
    LIGHT_THEME,
    ACCENT_THEME,
    GLASS_THEME,
)

# Config
from .config import (
    BannerConfig,
    BannerSize,
    BannerPosition,
    BannerAnimation,
    BannerBehavior,
    DEFAULT_CONFIG,
    FAST_CONFIG,
    SLOW_CONFIG,
    LARGE_CONFIG,
    COMPACT_CONFIG,
)

# Animationen (für erweiterte Nutzung)
from .animations import BannerAnimator, SlideAnimator, FadeAnimator

# Widget (für erweiterte Nutzung)
from .banner_widget import BannerWidget

__all__ = [
    # Haupt-API
    'TaskbarBanner',
    'show_desktop_status',
    'show_notification',
    # Theme
    'BannerTheme',
    'BannerColors',
    'BannerFonts',
    'BannerIcons',
    'DEFAULT_THEME',
    'DARK_THEME',
    'LIGHT_THEME',
    'ACCENT_THEME',
    'GLASS_THEME',
    # Config
    'BannerConfig',
    'BannerSize',
    'BannerPosition',
    'BannerAnimation',
    'BannerBehavior',
    'DEFAULT_CONFIG',
    'FAST_CONFIG',
    'SLOW_CONFIG',
    'LARGE_CONFIG',
    'COMPACT_CONFIG',
    # Animationen
    'BannerAnimator',
    'SlideAnimator',
    'FadeAnimator',
    # Widget
    'BannerWidget',
]
