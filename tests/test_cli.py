from unittest.mock import patch
from click.testing import CliRunner

from tiktok_downloader.cli import main
from tiktok_downloader.domains.tiktok.schemas import VideoMetadata

@patch('tiktok_downloader.cli.FilterService')
@patch('tiktok_downloader.cli.TikTokRepository')
@patch('tiktok_downloader.cli.ConfigService')
def test_cli_metadata_only_success(MockConfigService, MockTikTokRepository, MockFilterService):
    """
    GIVEN a URL and the --metadata-only flag
    WHEN the CLI is invoked
    THEN it should print the metadata of the videos and not attempt to download.
    """
    # ARRANGE
    # Mock the ConfigService to return an empty config dictionary
    mock_config_instance = MockConfigService.return_value
    mock_config_instance.load_config.return_value = {}

    # Mock the TikTokRepository to return some sample videos
    mock_repo_instance = MockTikTokRepository.return_value
    sample_videos = [
        VideoMetadata(id='123', title='Video 1', like_count=10, view_count=100, webpage_url='...'),
        VideoMetadata(id='456', title='Video 2', like_count=20, view_count=200, webpage_url='...')
    ]
    mock_repo_instance.fetch_metadata.return_value = sample_videos

    # Mock the FilterService to return the videos as-is
    mock_filter_instance = MockFilterService.return_value
    mock_filter_instance.apply_filters.return_value = sample_videos

    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    result = runner.invoke(main, [url, '--metadata-only'])

    # ASSERT
    assert result.exit_code == 0
    assert "Found 2 videos that match the criteria." in result.output
    assert "ID:          123" in result.output
    assert "Title:       Video 1" in result.output
    assert "Likes:       10" in result.output
    assert "Views:       100" in result.output
    assert "URL:         ..." in result.output
    assert "ID:          456" in result.output

    # Check that download was NOT called
    mock_repo_instance.download_videos.assert_not_called()
    # Check that fetch_metadata was called
    mock_repo_instance.fetch_metadata.assert_called_once_with(url)


@patch('tiktok_downloader.cli.FilterService')
@patch('tiktok_downloader.cli.TikTokRepository')
@patch('tiktok_downloader.cli.ConfigService')
def test_cli_filtering_options(MockConfigService, MockTikTokRepository, MockFilterService):
    """
    GIVEN --min-likes and --min-views options
    WHEN the CLI is invoked
    THEN it should call the FilterService with the correct filter values.
    """
    # ARRANGE
    mock_config_instance = MockConfigService.return_value
    mock_config_instance.load_config.return_value = {}

    mock_repo_instance = MockTikTokRepository.return_value
    # We don't need to return any videos for this test, just an empty list.
    sample_videos = [
        VideoMetadata(id='123', title='Video 1', like_count=10, view_count=100, webpage_url='...'),
    ]
    mock_repo_instance.fetch_metadata.return_value = sample_videos

    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    result = runner.invoke(main, [url, '--min-likes', '100', '--min-views', '1000', '--metadata-only'])

    # ASSERT
    assert result.exit_code == 0

    # Check that apply_filters was called with the correct integer values
    MockFilterService.return_value.apply_filters.assert_called_once_with(
        videos=sample_videos,
        min_likes=100,
        min_views=1000
    )


@patch('tiktok_downloader.cli.FilterService')
@patch('tiktok_downloader.cli.TikTokRepository')
@patch('tiktok_downloader.cli.ConfigService')
def test_cli_from_file(MockConfigService, MockTikTokRepository, MockFilterService):
    """
    GIVEN a file with multiple URLs and the --from-file option
    WHEN the CLI is invoked
    THEN it should call fetch_metadata for each URL in the file.
    """
    # ARRANGE
    mock_config_instance = MockConfigService.return_value
    mock_config_instance.load_config.return_value = {}

    mock_repo_instance = MockTikTokRepository.return_value
    mock_repo_instance.fetch_metadata.return_value = []

    runner = CliRunner()
    urls = [
        "http://tiktok.com/@user1",
        "http://tiktok.com/video/123",
    ]

    with runner.isolated_filesystem():
        with open("urls.txt", "w") as f:
            f.write("\n".join(urls))

        # ACT
        result = runner.invoke(main, ['--from-file', 'urls.txt', '--metadata-only'])

        # ASSERT
        assert result.exit_code == 0

        # Check that fetch_metadata was called for each URL
        assert mock_repo_instance.fetch_metadata.call_count == 2
        mock_repo_instance.fetch_metadata.assert_any_call(urls[0])
        mock_repo_instance.fetch_metadata.assert_any_call(urls[1])


@patch('tiktok_downloader.cli.FilterService')
@patch('tiktok_downloader.cli.TikTokRepository')
@patch('tiktok_downloader.cli.ConfigService')
def test_cli_config_file_integration(MockConfigService, MockTikTokRepository, MockFilterService):
    """
    GIVEN a config file with default settings
    WHEN the CLI is invoked without overriding options
    THEN it should use the settings from the config file.
    """
    # ARRANGE
    mock_config_instance = MockConfigService.return_value
    config_settings = {
        'min_likes': 500,
        'min_views': 5000,
        'output_path': '/config/path',
        'transcripts': True
    }
    mock_config_instance.load_config.return_value = config_settings

    mock_repo_instance = MockTikTokRepository.return_value
    mock_repo_instance.fetch_metadata.return_value = []

    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    # Invoke with no options, so config values should be used
    result = runner.invoke(main, [url, '--metadata-only'])

    # ASSERT
    assert result.exit_code == 0

    # Check that services were called with config values
    MockFilterService.return_value.apply_filters.assert_called_once_with(
        videos=[],
        min_likes=500,
        min_views=5000
    )


@patch('tiktok_downloader.cli.FilterService')
@patch('tiktok_downloader.cli.TikTokRepository')
@patch('tiktok_downloader.cli.ConfigService')
def test_cli_download_workflow(MockConfigService, MockTikTokRepository, MockFilterService):
    """
    GIVEN a URL and no --metadata-only flag
    WHEN the CLI is invoked
    THEN it should download the filtered videos.
    """
    # ARRANGE
    mock_config_instance = MockConfigService.return_value
    mock_config_instance.load_config.return_value = {}

    mock_repo_instance = MockTikTokRepository.return_value
    sample_videos = [
        VideoMetadata(id='123', title='Video 1', like_count=10, view_count=100, webpage_url='url1'),
    ]
    mock_repo_instance.fetch_metadata.return_value = sample_videos

    mock_filter_instance = MockFilterService.return_value
    mock_filter_instance.apply_filters.return_value = sample_videos

    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    result = runner.invoke(main, [url, '--output-path', '/my/downloads', '--transcripts'])

    # ASSERT
    assert result.exit_code == 0
    assert "Downloading 1 video(s) to /my/downloads..." in result.output

    # Check that download_videos was called correctly
    mock_repo_instance.download_videos.assert_called_once_with(
        videos=sample_videos,
        output_path='/my/downloads',
        download_transcripts=True
    )


def test_cli_no_input_fails():
    """
    GIVEN no URL or --from-file option
    WHEN the CLI is invoked
    THEN it should exit with an error.
    """
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code != 0
    assert "Error: You must provide either a TIKTOK_URL or use the --from-file option." in result.output


@patch('tiktok_downloader.cli.FilterService')
@patch('tiktok_downloader.cli.TikTokRepository')
@patch('tiktok_downloader.cli.ConfigService')
def test_cli_metadata_only_no_videos(MockConfigService, MockTikTokRepository, MockFilterService):
    """
    GIVEN the --metadata-only flag and no videos are found
    WHEN the CLI is invoked
    THEN it should print a 'no videos' message.
    """
    # ARRANGE
    mock_config_instance = MockConfigService.return_value
    mock_config_instance.load_config.return_value = {}

    mock_repo_instance = MockTikTokRepository.return_value
    mock_repo_instance.fetch_metadata.return_value = []

    mock_filter_instance = MockFilterService.return_value
    mock_filter_instance.apply_filters.return_value = []

    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    result = runner.invoke(main, [url, '--metadata-only'])

    # ASSERT
    assert result.exit_code == 0
    assert "No videos to display." in result.output


@patch('tiktok_downloader.cli.TikTokRepository')
@patch('tiktok_downloader.cli.ConfigService')
def test_cli_download_no_videos(MockConfigService, MockTikTokRepository):
    """
    GIVEN no videos are found after filtering
    WHEN the CLI is invoked for download
    THEN it should print a 'no videos' message and not download.
    """
    # ARRANGE
    mock_config_instance = MockConfigService.return_value
    mock_config_instance.load_config.return_value = {}

    mock_repo_instance = MockTikTokRepository.return_value
    mock_repo_instance.fetch_metadata.return_value = []

    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    result = runner.invoke(main, [url]) # No --metadata-only

    # ASSERT
    assert result.exit_code == 0
    assert "No videos to download." in result.output
    mock_repo_instance.download_videos.assert_not_called()
