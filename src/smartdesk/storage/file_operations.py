import json
import os
from typing import List
from ..config import DESKTOPS_FILE, DATA_DIR
from ..models.desktop import Desktop
from ..localization import get_text # <-- NEUER IMPORT

def _ensure_data_dir():
    """Stellt sicher, dass der data Ordner existiert."""
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR)
        except OSError as e:
            # --- LOKALISIERT ---
            print(get_text("storage.error.create_dir", e=e))

def save_desktops(desktops: List[Desktop]):
    """Speichert die Liste der Desktops in die JSON-Datei."""
    _ensure_data_dir()
    try:
        with open(DESKTOPS_FILE, 'w', encoding='utf-8') as f:
            json.dump([d.to_dict() for d in desktops], f, indent=4)
    except Exception as e:
        # --- LOKALISIERT ---
        print(get_text("storage.error.save", e=e))

def load_desktops() -> List[Desktop]:
    """Lädt alle Desktops aus der JSON-Datei."""
    if not os.path.exists(DESKTOPS_FILE):
        return []
    
    try:
        with open(DESKTOPS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Desktop.from_dict(item) for item in data]
    except Exception as e:
        # --- LOKALISIERT ---
        print(get_text("storage.error.load", e=e))
        return []
    