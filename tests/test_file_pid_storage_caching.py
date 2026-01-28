import os
import sys
import pytest

# Ensure src is in pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from smartdesk.hotkeys.implementations import FilePidStorage

def test_cache_logic(tmp_path):
    pid_file = tmp_path / "test_cache.pid"
    storage = FilePidStorage(str(pid_file))

    # 1. Write PID
    assert storage.write(123) is True

    # 2. Read (should load cache)
    assert storage.read() == 123

    # 3. Modify file externally
    with open(pid_file, "w") as f:
        f.write("999")

    # 4. Read again (should still be 123 due to cache)
    assert storage.read() == 123

    # 5. Delete file externally
    os.remove(pid_file)
    assert not pid_file.exists()

    # 6. Read again (should still be 123 due to cache)
    assert storage.read() == 123

    # 7. Write new value via storage (updates cache)
    assert storage.write(456) is True
    assert storage.read() == 456

    # Verify file content
    with open(pid_file, "r") as f:
        assert f.read() == "456"

    # 8. Delete via storage (clears cache)
    assert storage.delete() is True
    assert storage.read() is None

    # 9. Verify file gone
    assert not pid_file.exists()

def test_cache_missing_file(tmp_path):
    pid_file = tmp_path / "missing.pid"
    storage = FilePidStorage(str(pid_file))

    # 1. Read missing (should cache None)
    assert storage.read() is None

    # 2. Create file externally
    with open(pid_file, "w") as f:
        f.write("777")

    # 3. Read again (should still be None due to cache)
    assert storage.read() is None

    # 4. Write via storage (updates cache)
    assert storage.write(888) is True
    assert storage.read() == 888
