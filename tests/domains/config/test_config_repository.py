from pathlib import Path
from tiktok_downloader.domains.config.repository import ConfigRepository

def test_load_from_path_with_all_options(tmp_path: Path):
    # Arrange
    config_content = """
[defaults]
output_path = /downloads
min_likes = 100
min_views = 1000
transcripts = true
transcript_language = fr
concurrent_downloads = 5
min_sleep_interval = 10
max_sleep_interval = 20
"""
    config_file = tmp_path / "config.ini"
    config_file.write_text(config_content)
    repo = ConfigRepository()

    # Act
    config = repo.load_from_path(config_file)

    # Assert
    assert config.output_path == "/downloads"
    assert config.min_likes == 100
    assert config.min_views == 1000
    assert config.transcripts is True
    assert config.transcript_language == "fr"
    assert config.concurrent_downloads == 5
    assert config.min_sleep_interval == 10
    assert config.max_sleep_interval == 20

def test_load_from_path_with_missing_options(tmp_path: Path):
    # Arrange
    config_content = """
[defaults]
output_path = /downloads
"""
    config_file = tmp_path / "config.ini"
    config_file.write_text(config_content)
    repo = ConfigRepository()

    # Act
    config = repo.load_from_path(config_file)

    # Assert
    assert config.output_path == "/downloads"
    assert config.min_likes is None
    assert config.min_views is None
    assert config.transcripts is None
    assert config.transcript_language is None
    assert config.concurrent_downloads is None
    assert config.min_sleep_interval is None
    assert config.max_sleep_interval is None


def test_load_from_path_with_no_defaults_section(tmp_path: Path):
    # Arrange
    config_content = "[other_section]\nkey=value\n"
    config_file = tmp_path / "config.ini"
    config_file.write_text(config_content)
    repo = ConfigRepository()

    # Act
    config = repo.load_from_path(config_file)

    # Assert
    assert config.output_path is None
    assert config.min_likes is None
    assert config.min_views is None
    assert config.transcripts is None
    assert config.transcript_language is None
    assert config.concurrent_downloads is None
    assert config.min_sleep_interval is None
    assert config.max_sleep_interval is None
