import json
import os
import time
import pytest
from unittest.mock import patch, MagicMock

# Mock dependencies
import sys
sys.modules["winreg"] = MagicMock()
sys.modules["ctypes"] = MagicMock()
sys.modules["psutil"] = MagicMock()
sys.modules["pystray"] = MagicMock()
sys.modules["pynput"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["PySide6"] = MagicMock()
sys.modules["colorama"] = MagicMock()

# Set APPDATA
os.environ["APPDATA"] = "/tmp"

from smartdesk.core.storage import file_operations
from smartdesk.core.models.desktop import Desktop

@pytest.fixture
def clean_cache():
    # Reset cache before each test
    file_operations._json_cache = {}
    file_operations._cache_mtime = {}
    yield
    file_operations._json_cache = {}
    file_operations._cache_mtime = {}

@pytest.fixture
def setup_file(tmp_path):
    # Create a temporary desktops.json
    file_path = tmp_path / "desktops.json"
    lock_path = tmp_path / "desktops.lock"

    data = [{"name": "CacheTest", "path": "C:\\CacheTest", "is_active": True}]
    with open(file_path, "w") as f:
        json.dump(data, f)

    # Patch the paths in file_operations
    with patch("smartdesk.core.storage.file_operations.get_data_file_path", return_value=str(file_path)), \
         patch("smartdesk.core.storage.file_operations.LOCK_FILE_PATH", str(lock_path)):
        yield file_path

def test_cache_miss_and_hit(clean_cache, setup_file):
    # 1. First load: Should hit the file (Cache Miss)
    with patch("smartdesk.core.storage.file_operations.file_lock") as mock_lock:
        desktops = file_operations.load_desktops()
        assert len(desktops) == 1
        assert desktops[0].name == "CacheTest"
        assert mock_lock.called, "Should assume lock was used on first load"

    # 2. Second load: Should hit the cache (Cache Hit)
    with patch("smartdesk.core.storage.file_operations.file_lock") as mock_lock:
        desktops = file_operations.load_desktops()
        assert len(desktops) == 1
        assert not mock_lock.called, "Should NOT use lock on cache hit"

def test_external_modification_invalidation(clean_cache, setup_file):
    # 1. Load to cache
    file_operations.load_desktops()

    # 2. Modify file externally
    # Sleep to ensure mtime changes (filesystems have limited resolution)
    time.sleep(0.01) # If this is too fast for FS resolution, test might fail.
                     # But usually touching it updates mtime.

    # Force mtime update
    new_data = [{"name": "Modified", "path": "C:\\Mod", "is_active": False}]
    with open(setup_file, "w") as f:
        json.dump(new_data, f)

    # Ensure mtime is definitely different (manual check for test robustness)
    old_mtime = file_operations._cache_mtime[str(setup_file)]
    current_mtime = os.path.getmtime(setup_file)
    if old_mtime == current_mtime:
        # Force mtime forward if FS resolution is low
        os.utime(setup_file, (current_mtime + 1, current_mtime + 1))

    # 3. Reload: Should see change
    with patch("smartdesk.core.storage.file_operations.file_lock") as mock_lock:
        desktops = file_operations.load_desktops()
        assert desktops[0].name == "Modified"
        assert mock_lock.called, "Should reload from file"

def test_save_updates_cache(clean_cache, setup_file):
    # 1. Load initial
    file_operations.load_desktops()

    # 2. Save new data via save_desktops
    new_desktops = [Desktop(name="Saved", path="C:\\Saved")]
    file_operations.save_desktops(new_desktops)

    # 3. Load again: Should use cache (no lock/read) but return new data
    # We spy on open to ensure no read happened (save_desktops writes, but load shouldn't read)
    # Actually, save_desktops uses open('w'). We want to ensure load_desktops doesn't use open('r').

    with patch("smartdesk.core.storage.file_operations.file_lock") as mock_lock:
        desktops = file_operations.load_desktops()
        assert desktops[0].name == "Saved"
        # Ideally, mock_lock shouldn't be called because save_desktops updated the cache
        # AND the mtime.
        assert not mock_lock.called, "Should use updated cache after save"

def test_isolation(clean_cache, setup_file):
    # 1. Load
    desktops1 = file_operations.load_desktops()
    d1 = desktops1[0]

    # 2. Modify object
    d1.name = "Mutated"

    # 3. Load again
    desktops2 = file_operations.load_desktops()
    d2 = desktops2[0]

    assert d2.name == "CacheTest", "Second load should return fresh object, not mutated one"
    assert d1.name == "Mutated"
