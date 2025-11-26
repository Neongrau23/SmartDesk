# SmartDesk Animationen
from .screen_fade import MultiMonitorFade
# AnimationConfig wird jetzt aus config.py importiert
from ..config import AnimationConfig

# Behalte FadeConfig für Rückwärtskompatibilität (Alias)
FadeConfig = AnimationConfig

__all__ = ['MultiMonitorFade', 'AnimationConfig', 'FadeConfig']
