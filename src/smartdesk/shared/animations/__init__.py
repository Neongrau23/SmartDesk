# SmartDesk Animationen
from .screen_fade import MultiMonitorFade
# AnimationConfig wird jetzt aus config.py importiert
from ..config import AnimationConfig

# Taskbar Banner
from .taskbar_banner import TaskbarBanner, BannerConfig, show_desktop_status, show_notification

# Behalte FadeConfig für Rückwärtskompatibilität (Alias)
FadeConfig = AnimationConfig

__all__ = [
    'MultiMonitorFade', 
    'AnimationConfig', 
    'FadeConfig',
    'TaskbarBanner',
    'BannerConfig',
    'show_desktop_status',
    'show_notification',
]
