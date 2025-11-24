import os

# Registry Keys (Bestehend)
KEY_USER_SHELL = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
KEY_LEGACY_SHELL = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
VALUE_NAME = "Desktop"

# Geht zurück zum Projekt-Root (unter der Annahme: src/smartdesk/config.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
DESKTOPS_FILE = os.path.join(DATA_DIR, "desktops.json")