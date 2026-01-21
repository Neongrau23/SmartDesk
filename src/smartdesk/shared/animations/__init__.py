# SmartDesk Animationen
from .screen_fade import MultiMonitorFade

# AnimationConfig wird jetzt aus config.py importiert
from ..config import AnimationConfig

# Taskbar Banner (aus neuem modularen Aufbau)
from .banner import (
    TaskbarBanner,
    BannerConfig,
    BannerTheme,
    show_desktop_status,
    show_notification,
    DEFAULT_THEME,
    DARK_THEME,
    FAST_CONFIG,
    SLOW_CONFIG,
)

# Behalte FadeConfig für Rückwärtskompatibilität (Alias)
FadeConfig = AnimationConfig

__all__ = [
    "MultiMonitorFade",
    "AnimationConfig",
    "FadeConfig",
    # Banner
    "TaskbarBanner",
    "BannerConfig",
    "BannerTheme",
    "show_desktop_status",
    "show_notification",
    "DEFAULT_THEME",
    "DARK_THEME",
    "FAST_CONFIG",
    "SLOW_CONFIG",
]
