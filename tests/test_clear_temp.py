import os
from pathlib import Path

from agentom.settings import settings
from agentom.utils import clear_temp_dir


def test_clear_temp_dir_creates_and_clears(tmp_path):
    # Point the settings object at a temporary workspace so we don't modify
    # the user's real workspace. Update directories after changing the value.
    settings.WORKSPACE_DIR = Path(tmp_path)
    settings.ensure_directories()

    # settings.TEMP_DIR should point inside the workspace path
    temp_dir = settings.TEMP_DIR
    # Ensure directory exists
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Create a file inside temp dir
    test_file = temp_dir / "temp_test_file.txt"
    test_file.write_text("hello")

    assert test_file.exists()

    # Call the cleanup function — it should remove the file
    clear_temp_dir()

    # After cleanup, temp_dir should exist but the file should be gone
    assert not test_file.exists()
