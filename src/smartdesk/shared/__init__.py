# SmartDesk Shared Resources
from .config import (
    KEY_USER_SHELL,
    KEY_LEGACY_SHELL,
    VALUE_NAME,
    DATA_DIR,
    DESKTOPS_FILE,
    WALLPAPERS_DIR,
    BASE_DIR,
    AnimationConfig,
)
from .localization import get_text
from .style import (
    PREFIX_OK,
    PREFIX_ERROR,
    PREFIX_WARN,
    format_status_active,
    format_status_inactive,
)

__all__ = [
    'KEY_USER_SHELL',
    'KEY_LEGACY_SHELL',
    'VALUE_NAME',
    'DATA_DIR',
    'DESKTOPS_FILE',
    'WALLPAPERS_DIR',
    'BASE_DIR',
    'AnimationConfig',
    'get_text',
    'PREFIX_OK',
    'PREFIX_ERROR',
    'PREFIX_WARN',
    'format_status_active',
    'format_status_inactive',
]
