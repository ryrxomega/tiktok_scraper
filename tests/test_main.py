"""
Unit tests for the main application logic in `tiktok_downloader.main`.
"""
import pytest
from unittest.mock import patch

from tiktok_downloader.main import download_videos
from tiktok_downloader.domains.tiktok.models import Video


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
    result = download_videos(tiktok_url="http://tiktok.com/testvideo")

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
    result = download_videos(tiktok_url="http://tiktok.com/testvideo", metadata_only=True)

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
