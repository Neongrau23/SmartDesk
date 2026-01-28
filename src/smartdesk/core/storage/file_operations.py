# Dateipfad: src/smartdesk/core/storage/file_operations.py

import json
import os
import random
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
    Uses exponential backoff to reduce polling frequency.
    """
    start_time = time.time()
    sleep_time = 0.001  # Start with 1ms
    max_sleep = 0.1  # Cap at 100ms

    while True:
        try:
            # Try to create the lock file in exclusive mode
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.time() - start_time >= timeout:
                raise TimeoutError("Could not acquire lock within the specified timeout.")

            # Add jitter to prevent thundering herd
            jitter = random.uniform(0, sleep_time * 0.1)
            time.sleep(sleep_time + jitter)

            # Exponential backoff: double the wait time, but cap it
            sleep_time = min(sleep_time * 2, max_sleep)

    try:
        yield
    finally:
        # Remove the lock file
        try:
            os.remove(lock_file)
        except OSError:
            # Ignore errors during removal (e.g. if file was already removed)
            pass


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
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Desktop.from_dict(item) for item in data]
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

            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Fehler beim Speichern der Desktops: {e}")
        return False
