# Dateipfad: src/smartdesk/core/storage/file_operations.py

import json
import os
import time
from contextlib import contextmanager
from typing import List

from ..models.desktop import Desktop
from ...shared.config import DATA_DIR

DATA_FILE_PATH = os.path.join(DATA_DIR, "desktops.json")
LOCK_FILE_PATH = os.path.join(DATA_DIR, "desktops.lock")

@contextmanager
def file_lock(lock_file, timeout=10):
    """
    A context manager for file-based locking.
    """
    start_time = time.time()
    while True:
        try:
            # Try to create the lock file in exclusive mode
            with open(lock_file, 'x'):
                break
        except FileExistsError:
            if time.time() - start_time >= timeout:
                raise TimeoutError("Could not acquire lock within the specified timeout.")
            time.sleep(0.1)

    try:
        yield
    finally:
        # Remove the lock file
        os.remove(lock_file)


def get_data_file_path() -> str:
    """Gibt den Pfad zur desktops.json Datei zurück."""
    return DATA_FILE_PATH


def load_desktops() -> List[Desktop]:
    """
    Lädt alle Desktops aus der desktops.json Datei.
    Gibt eine leere Liste zurück, wenn die Datei nicht existiert.
    """
    data_file = get_data_file_path()

    if not os.path.exists(data_file):
        return []

    try:
        with file_lock(LOCK_FILE_PATH):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                desktops = []
                for item in data:
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
        with file_lock(LOCK_FILE_PATH):
            data = []
            for desktop in desktops:
                data.append(desktop.to_dict())

            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Fehler beim Speichern der Desktops: {e}")
        return False
