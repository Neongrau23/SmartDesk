# Dateipfad: src/smartdesk/storage/file_operations.py

import json
import os
from typing import List
from ..models.desktop import Desktop
from ..config import DATA_DIR


def get_data_file_path() -> str:
    """Gibt den Pfad zur desktops.json Datei zurück."""
    return os.path.join(DATA_DIR, "desktops.json")


def load_desktops() -> List[Desktop]:
    """
    Lädt alle Desktops aus der desktops.json Datei.
    Gibt eine leere Liste zurück, wenn die Datei nicht existiert.
    """
    data_file = get_data_file_path()
    
    if not os.path.exists(data_file):
        return []
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            desktops = []
            for item in data:
                # Verwende die from_dict Methode der Desktop-Klasse
                desktop = Desktop.from_dict(item)
                desktops.append(desktop)
            return desktops
    except Exception as e:
        print(f"Fehler beim Laden der Desktops: {e}")
        return []


def save_desktops(desktops: List[Desktop]) -> bool:
    """
    Speichert alle Desktops in die desktops.json Datei.
    
    Args:
        desktops: Liste der zu speichernden Desktop-Objekte
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    data_file = get_data_file_path()
    
    # Stelle sicher, dass das Verzeichnis existiert
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    
    try:
        data = []
        for desktop in desktops:
            # Verwende die to_dict Methode der Desktop-Klasse
            data.append(desktop.to_dict())
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Fehler beim Speichern der Desktops: {e}")
        return False
