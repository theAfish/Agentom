from pathlib import Path
import json

from agentom.settings import Settings, CONFIG_FILE


def test_output_archive_dir_from_config():
    # repo root is parents[3] from test file location
    repo_root = Path(__file__).resolve().parents[3]
    assert CONFIG_FILE.exists(), f"Expected CONFIG_FILE to exist at {CONFIG_FILE}"

    with open(repo_root / "config" / "config.json", 'r') as f:
        config = json.load(f)

    config_output_dir = config.get('OUTPUT_ARCHIVE_DIR', 'outputs_archive')
    expected = (repo_root / config_output_dir).resolve()

    settings = Settings()
    assert settings.OUTPUT_ARCHIVE_DIR.resolve() == expected
