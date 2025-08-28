import tempfile
from pathlib import Path

from tiktok_downloader.domains.config.repository import ConfigRepository


def test_load_from_path_with_cookies():
    """
    GIVEN a config file with a cookies path
    WHEN the load_from_path method is called
    THEN it should return a Config object with the correct cookies path.
    """
    # ARRANGE
    config_content = """
[defaults]
cookies = /path/to/cookies.txt
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ini") as tmp_file:
        tmp_file.write(config_content)
        tmp_file_path = Path(tmp_file.name)

    repo = ConfigRepository()

    # ACT
    config = repo.load_from_path(tmp_file_path)

    # ASSERT
    assert config.cookies == "/path/to/cookies.txt"

    # CLEANUP
    tmp_file_path.unlink()


def test_load_from_path_with_cookies_from_browser():
    """
    GIVEN a config file with a cookies_from_browser value
    WHEN the load_from_path method is called
    THEN it should return a Config object with the correct cookies_from_browser value.
    """
    # ARRANGE
    config_content = """
[defaults]
cookies_from_browser = chrome
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ini") as tmp_file:
        tmp_file.write(config_content)
        tmp_file_path = Path(tmp_file.name)

    repo = ConfigRepository()

    # ACT
    config = repo.load_from_path(tmp_file_path)

    # ASSERT
    assert config.cookies_from_browser == "chrome"

    # CLEANUP
    tmp_file_path.unlink()
