"""
Unit tests for the main application logic in `tiktok_downloader.main`.
"""
import pytest
from unittest.mock import patch

from tiktok_downloader.main import download_videos, _resolve_settings
from tiktok_downloader.domains.tiktok.models import Video
from tiktok_downloader.domains.config.schemas import Config


@pytest.fixture
def mock_video():
    """Fixture for a mock Video object."""
    return Video(
        id="12345",
        title="Test Video",
        like_count=100,
        view_count=1000,
        webpage_url="http://tiktok.com/testvideo"
    )


@patch('tiktok_downloader.main.ConfigRepository')
@patch('tiktok_downloader.main.ConfigService')
@patch('tiktok_downloader.main.TikTokRepository')
@patch('tiktok_downloader.main.FilterService')
def test_download_videos_success(
    mock_filter_service,
    mock_tiktok_repo,
    mock_config_service,
    mock_config_repo,
    mock_video,
):
    """
    Test that `download_videos` orchestrates the services correctly
    for a successful download.
    """
    # Arrange
    mock_repo_instance = mock_tiktok_repo.return_value
    mock_repo_instance.fetch_metadata.return_value = [mock_video]
    mock_filter_instance = mock_filter_service.return_value
    mock_filter_instance.apply_filters.return_value = [mock_video]

    # Act
    result = download_videos(
        tiktok_url="http://tiktok.com/testvideo",
    )

    # Assert
    assert result == [mock_video]
    mock_repo_instance.fetch_metadata.assert_called_once()
    mock_filter_instance.apply_filters.assert_called_once()
    mock_repo_instance.download_videos.assert_called_once()


@patch('tiktok_downloader.main.ConfigRepository')
@patch('tiktok_downloader.main.ConfigService')
@patch('tiktok_downloader.main.TikTokRepository')
@patch('tiktok_downloader.main.FilterService')
def test_download_videos_metadata_only(
    mock_filter_service,
    mock_tiktok_repo,
    mock_config_service,
    mock_config_repo,
    mock_video,
):
    """
    Test that `download_videos` does not call download_videos when
    `metadata_only` is True.
    """
    # Arrange
    mock_repo_instance = mock_tiktok_repo.return_value
    mock_repo_instance.fetch_metadata.return_value = [mock_video]
    mock_filter_instance = mock_filter_service.return_value
    mock_filter_instance.apply_filters.return_value = [mock_video]

    # Act
    result = download_videos(
        tiktok_url="http://tiktok.com/testvideo",
        metadata_only=True,
    )

    # Assert
    assert result == [mock_video]
    mock_repo_instance.fetch_metadata.assert_called_once()
    mock_filter_instance.apply_filters.assert_called_once()
    mock_repo_instance.download_videos.assert_not_called()


def test_download_videos_no_url_raises_error():
    """
    Test that `download_videos` raises a ValueError if no URL or file is provided.
    """
    with pytest.raises(ValueError, match="You must provide either a tiktok_url or from_file."):
        download_videos()


@patch('tiktok_downloader.main.logger')
@patch('builtins.open')
@patch('tiktok_downloader.main.ConfigRepository')
@patch('tiktok_downloader.main.ConfigService')
@patch('tiktok_downloader.main.TikTokRepository')
@patch('tiktok_downloader.main.FilterService')
def test_download_videos_from_file_and_download(
    mock_filter_service,
    mock_tiktok_repo,
    mock_config_service,
    mock_config_repo,
    mock_open,
    mock_logger,
    mock_video,
):
    """
    Test that `download_videos` correctly processes a file of URLs and calls
    the download method, covering the log messages.
    """
    # Arrange
    mock_open.return_value.__enter__.return_value.__iter__.return_value = ["http://fake.url/1\n"]
    mock_repo_instance = mock_tiktok_repo.return_value
    mock_repo_instance.fetch_metadata.return_value = [mock_video]
    mock_filter_instance = mock_filter_service.return_value
    mock_filter_instance.apply_filters.return_value = [mock_video]

    # Act
    result = download_videos(from_file="urls.txt")

    # Assert
    assert result == [mock_video]
    mock_open.assert_called_once_with("urls.txt", 'r')
    mock_repo_instance.fetch_metadata.assert_called_once()
    mock_filter_instance.apply_filters.assert_called_once()
    mock_repo_instance.download_videos.assert_called_once()
    mock_logger.info.assert_any_call("Download complete.")


def test_resolve_settings_cli_overrides_config():
    """
    Test that CLI arguments take precedence over config file settings.
    """
    # Arrange
    config = Config(min_likes=10, output_path="/config/path")
    cli_args = {'min_likes': 100, 'output_path': None}

    # Act
    settings = _resolve_settings(config, cli_args)

    # Assert
    assert settings['min_likes'] == 100
    assert settings['output_path'] == "/config/path"


def test_resolve_settings_uses_defaults():
    """
    Test that default values are used when no CLI or config values are provided.
    """
    # Arrange
    config = Config()
    cli_args = {}

    # Act
    settings = _resolve_settings(config, cli_args)

    # Assert
    assert settings['output_path'] == '.'
    assert settings['concurrent_downloads'] == 1
    assert settings['min_likes'] is None


def test_resolve_settings_transcript_logic():
    """
    Test the logic for resolving transcript settings.
    """
    # Case 1: CLI enables transcripts
    config = Config(transcripts=False, transcript_language='en')
    cli_args = {'download_transcripts': True, 'transcript_language': 'es'}
    settings = _resolve_settings(config, cli_args)
    assert settings['transcript_language'] == 'es'

    # Case 2: CLI disables transcripts
    config = Config(transcripts=True)
    cli_args = {'download_transcripts': False}
    settings = _resolve_settings(config, cli_args)
    assert settings['transcript_language'] is None

    # Case 3: Config enables transcripts, CLI is silent
    config = Config(transcripts=True, transcript_language='fr')
    cli_args = {}
    settings = _resolve_settings(config, cli_args)
    assert settings['transcript_language'] == 'fr'

    # Case 4: Everything is off
    config = Config(transcripts=False)
    cli_args = {}
    settings = _resolve_settings(config, cli_args)
    assert settings['transcript_language'] is None
