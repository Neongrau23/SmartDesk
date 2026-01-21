# Dateipfad: src/smartdesk/core/utils/path_validator.py

import os

from ...shared.style import PREFIX_ERROR
from ...shared.localization import get_text


def ensure_directory_exists(path: str) -> bool:
    """
    Prüft, ob ein Verzeichnis existiert, und erstellt es gegebenenfalls.
    Gibt True zurück, wenn das Verzeichnis verfügbar ist.
    """
    if not path:
        return False

    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except OSError as e:
        print(f"{PREFIX_ERROR} {get_text('path_validator.error.create_dir', path=path, e=e)}")
        return False
