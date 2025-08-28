from pathlib import Path
from tiktok_downloader.domains.config.services import ConfigService

def test_load_config_success(tmp_path: Path):
    """
    GIVEN a valid config.ini file
    WHEN the load_config method is called
    THEN it should return a dictionary with the correct settings, parsing types correctly.
    """
    # ARRANGE
    config_content = """
[defaults]
output_path = /test/downloads
min_likes = 100
min_views = 5000
transcripts = false
"""
    config_file = tmp_path / "config.ini"
    config_file.write_text(config_content)

    # ACT
    config_service = ConfigService()
    settings = config_service.load_config(config_file)

    # ASSERT
    assert settings["output_path"] == "/test/downloads"
    assert settings["min_likes"] == 100
    assert settings["min_views"] == 5000
    assert settings["transcripts"] is False


def test_load_config_missing_file(tmp_path: Path):
    """
    GIVEN a path to a config file that does not exist
    WHEN the load_config method is called
    THEN it should return an empty dictionary without raising an error.
    """
    # ARRANGE
    config_file = tmp_path / "non_existent_config.ini"

    # ACT
    config_service = ConfigService()
    settings = config_service.load_config(config_file)

    # ASSERT
    assert settings == {}


def test_load_config_missing_defaults_section(tmp_path: Path):
    """
    GIVEN a config file that is missing the [defaults] section
    WHEN the load_config method is called
    THEN it should return an empty dictionary.
    """
    # ARRANGE
    config_content = """
[another_section]
key = value
"""
    config_file = tmp_path / "config.ini"
    config_file.write_text(config_content)

    # ACT
    config_service = ConfigService()
    settings = config_service.load_config(config_file)

    # ASSERT
    assert settings == {}


def test_load_config_missing_key(tmp_path: Path):
    """
    GIVEN a config file with a [defaults] section but a missing key
    WHEN the load_config method is called
    THEN it should return a dictionary with only the keys that were present.
    """
    # ARRANGE
    config_content = """
[defaults]
output_path = /some/path
"""
    config_file = tmp_path / "config.ini"
    config_file.write_text(config_content)

    # ACT
    config_service = ConfigService()
    settings = config_service.load_config(config_file)

    # ASSERT
    assert "output_path" in settings
    assert settings["output_path"] == "/some/path"
    assert "min_likes" not in settings
    assert "min_views" not in settings
    assert "transcripts" not in settings
