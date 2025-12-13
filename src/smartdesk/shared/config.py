# Dateipfad: src/smartdesk/shared/config.py

import os

# Registry Keys (Bestehend)
KEY_USER_SHELL = (
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
)
KEY_LEGACY_SHELL = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
VALUE_NAME = "Desktop"

# AppData-Pfad für Benutzerdaten (empfohlen für installierte Programme)
APPDATA_DIR = os.path.join(os.environ['APPDATA'], 'SmartDesk')
DATA_DIR = APPDATA_DIR
DESKTOPS_FILE = os.path.join(DATA_DIR, "desktops.json")
WALLPAPERS_DIR = os.path.join(DATA_DIR, "wallpapers")

# Ordner erstellen, falls nicht vorhanden
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(WALLPAPERS_DIR, exist_ok=True)

# Alternativ: Projekt-Root für Entwicklung/Portable Version
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
DEV_DATA_DIR = os.path.join(BASE_DIR, "data")
DEV_DESKTOPS_FILE = os.path.join(DEV_DATA_DIR, "desktops.json")
DEV_WALLPAPERS_DIR = os.path.join(DEV_DATA_DIR, "wallpapers")


# =============================================================================
# Animation Configuration
# =============================================================================
class AnimationConfig:
    """
    Zentrale Konfiguration für Desktop-Switch Animationen.
    """

    # Fade-Einstellungen
    FADE_IN_DURATION = 0.1
    FADE_OUT_DURATION = 0.1
    VISIBLE_DURATION = 2.5
    FADE_STEPS = 100

    # Anzeigeeinstellungen
    BACKGROUND_COLOR = 'Black'
    TEXT_COLOR = 'white'
    SHOW_LOGO = True
    HIDE_CURSOR = True
    TOPMOST = True

    # Wartezeit
    INITIAL_DELAY = 0

    # Debug-Modus
    DEBUG = False
    ALLOW_ESC_EXIT = True
