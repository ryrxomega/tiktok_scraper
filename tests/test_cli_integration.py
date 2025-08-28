import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from tiktok_downloader.cli import main
from tiktok_downloader.domains.config.schemas import Config

VIDEO_URL = "https://www.tiktok.com/@anyuser/video/12345"
VIDEO_ID = "12345"

# This is a realistic mock of the data structure yt-dlp returns
# for a TikTok user page (which is treated as a playlist).
MOCK_METADATA = {
    '_type': 'playlist',
    'id': 'anyuser',
    'title': 'anyuser',
    'entries': [
        {
            'id': VIDEO_ID,
            'title': 'A test video title',
            'like_count': 100,
            'view_count': 1000,
            'webpage_url': VIDEO_URL,
        }
    ]
}

@pytest.mark.integration
@patch('tiktok_downloader.main.ConfigService')
@patch('tiktok_downloader.domains.tiktok.repository.yt_dlp.YoutubeDL')
def test_cli_integration_metadata_only(MockYoutubeDL, MockConfigService):
    """
    GIVEN a mocked yt-dlp response
    WHEN the CLI is invoked with --metadata-only and no filters
    THEN it should correctly parse and display the video's metadata.
    """
    # ARRANGE
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = MOCK_METADATA
    MockYoutubeDL.return_value.__enter__.return_value = mock_ydl_instance
    MockConfigService.return_value.load_config.return_value = Config()

    runner = CliRunner()

    # ACT
    result = runner.invoke(main, [VIDEO_URL, '--metadata-only'])

    # ASSERT
    assert result.exit_code == 0, result.output
    assert "Fetching metadata..." in result.output
    assert "Found 1 videos that match the criteria." in result.output
    assert f"ID:          {VIDEO_ID}" in result.output
    assert "Title:       A test video title" in result.output
    assert "Likes:       100" in result.output
    assert "Views:       1000" in result.output
    assert f"URL:         {VIDEO_URL}" in result.output
    mock_ydl_instance.download.assert_not_called()


@pytest.mark.integration
@patch('tiktok_downloader.main.ConfigService')
@patch('tiktok_downloader.domains.tiktok.repository.yt_dlp.YoutubeDL')
def test_cli_integration_download(MockYoutubeDL, MockConfigService):
    """
    GIVEN a mocked yt-dlp response
    WHEN the CLI is invoked for download with no filters
    THEN it should attempt to download the video.
    """
    # ARRANGE
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = MOCK_METADATA
    mock_ydl_instance.download.return_value = 0
    MockYoutubeDL.return_value.__enter__.return_value = mock_ydl_instance
    MockConfigService.return_value.load_config.return_value = Config()

    runner = CliRunner()

    # ACT
    result = runner.invoke(main, [VIDEO_URL, '--output-path', '/tmp/downloads'])

    # ASSERT
    assert result.exit_code == 0, result.output
    assert "Downloading 1 video(s)..." in result.output
    assert "Download complete." in result.output
    mock_ydl_instance.download.assert_called_once_with([VIDEO_URL])


@pytest.mark.integration
@patch('tiktok_downloader.main.ConfigService')
@patch('tiktok_downloader.domains.tiktok.repository.yt_dlp.YoutubeDL')
def test_cli_integration_download_with_transcripts(MockYoutubeDL, MockConfigService):
    """
    GIVEN a mocked yt-dlp response
    WHEN the CLI is invoked for download with transcript options
    THEN it should call yt-dlp with the correct options.
    """
    # ARRANGE
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = MOCK_METADATA
    mock_ydl_instance.download.return_value = 0
    MockYoutubeDL.return_value.__enter__.return_value = mock_ydl_instance
    MockConfigService.return_value.load_config.return_value = Config()

    runner = CliRunner()

    # ACT
    result = runner.invoke(main, [
        VIDEO_URL,
        '--output-path', '/tmp/downloads',
        '--transcripts',
        '--transcript-language', 'es'
    ])

    # ASSERT
    assert result.exit_code == 0, result.output
    assert "Downloading 1 video(s)..." in result.output

    expected_opts = {
        'outtmpl': '/tmp/downloads/%(title)s [%(id)s].%(ext)s',
        'writethumbnail': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['es'],
    }
    MockYoutubeDL.assert_called_with(expected_opts)


@pytest.mark.integration
@patch('tiktok_downloader.main.ConfigService')
@patch('tiktok_downloader.domains.tiktok.repository.yt_dlp.YoutubeDL')
def test_cli_handles_partial_metadata(MockYoutubeDL, MockConfigService):
    """
    GIVEN a video with missing (but not essential) metadata
    WHEN the CLI is invoked
    THEN it should still process the video and display "None" for missing fields.
    """
    # ARRANGE
    MOCK_PARTIAL_METADATA = {
        '_type': 'playlist',
        'id': 'anyuser',
        'entries': [
            {
                'id': VIDEO_ID,
                'view_count': 1000,
                'webpage_url': VIDEO_URL,
            }
        ]
    }
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = MOCK_PARTIAL_METADATA
    MockYoutubeDL.return_value.__enter__.return_value = mock_ydl_instance
    MockConfigService.return_value.load_config.return_value = Config()

    runner = CliRunner()

    # ACT (no filters)
    result = runner.invoke(main, [VIDEO_URL, '--metadata-only'])

    # ASSERT (no filters)
    assert result.exit_code == 0, result.output
    assert "Found 1 videos that match the criteria." in result.output
    assert f"ID:          {VIDEO_ID}" in result.output
    assert "Title:       None" in result.output
    assert "Likes:       None" in result.output
    assert "Views:       1000" in result.output

    # ACT (with like filter)
    result_filtered = runner.invoke(main, [VIDEO_URL, '--metadata-only', '--min-likes', '1'])

    # ASSERT (with like filter)
    assert result_filtered.exit_code == 0, result_filtered.output
    assert "Found 0 videos that match the criteria." in result_filtered.output


@pytest.mark.integration
@patch('tiktok_downloader.main.ConfigService')
@patch('tiktok_downloader.domains.tiktok.repository.yt_dlp.YoutubeDL')
def test_cli_integration_with_cookies(MockYoutubeDL, MockConfigService):
    """
    GIVEN mocked yt-dlp and cookie CLI arguments
    WHEN the CLI is invoked
    THEN it should call yt-dlp with the correct cookie options.
    """
    # ARRANGE
    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = MOCK_METADATA
    MockYoutubeDL.return_value.__enter__.return_value = mock_ydl_instance
    MockConfigService.return_value.load_config.return_value = Config()

    runner = CliRunner()
    browser = "chrome"

    with runner.isolated_filesystem() as fs:
        cookies_file = f"{fs}/cookies.txt"
        with open(cookies_file, "w") as f:
            f.write("# Netscape HTTP Cookie File")

        # ACT
        result = runner.invoke(main, [
            VIDEO_URL,
            '--metadata-only',
            '--cookies', cookies_file,
            '--cookies-from-browser', browser,
        ])

        # ASSERT
        assert result.exit_code == 0, result.output

    # Check that fetch_metadata was called with cookie options
    expected_fetch_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'cookies': cookies_file,
        'cookiesfrombrowser': (browser,),
    }
    # The mock was called twice: once for fetch_metadata, once for download_videos
    # Since we are in metadata_only mode, download_videos is not called.
    # So we check the first call.
    MockYoutubeDL.assert_called_with(expected_fetch_opts)
