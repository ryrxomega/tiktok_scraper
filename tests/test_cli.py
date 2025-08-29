import logging
import pathlib
from unittest.mock import patch

from click.testing import CliRunner

from tiktok_downloader.cli import main
from tiktok_downloader.domains.tiktok.models import Video


@patch('tiktok_downloader.cli.download_videos')
def test_cli_metadata_only_success(mock_download_videos):
    """
    GIVEN a URL and the --metadata-only flag
    WHEN the CLI is invoked
    THEN it should call the download_videos function and print the metadata.
    """
    # ARRANGE
    sample_videos = [
        Video(id='123', title='Video 1', like_count=10, view_count=100, webpage_url='...'),
        Video(id='456', title='Video 2', like_count=20, view_count=200, webpage_url='...')
    ]
    mock_download_videos.return_value = sample_videos

    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    result = runner.invoke(main, [url, '--metadata-only'])

    # ASSERT
    assert result.exit_code == 0
    mock_download_videos.assert_called_once_with(
        tiktok_url=url,
        from_file=None,
        output_path=None,
        min_likes=None,
        min_views=None,
        download_transcripts=None,
        transcript_language='en-US',
        metadata_only=True,
        save_metadata_path=None,
        concurrent_downloads=1,
        min_sleep_interval=None,
        max_sleep_interval=None,
        cookies_from_browser=None,
        cookies_file=None,
    )
    assert "Found 2 videos that match the criteria." in result.output
    assert "ID:          123" in result.output
    assert "Title:       Video 1" in result.output


@patch('tiktok_downloader.cli.download_videos')
def test_cli_filtering_options(mock_download_videos):
    """
    GIVEN --min-likes and --min-views options
    WHEN the CLI is invoked
    THEN it should call download_videos with the correct filter values.
    """
    # ARRANGE
    mock_download_videos.return_value = []
    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    result = runner.invoke(main, [url, '--min-likes', '100', '--min-views', '1000'])

    # ASSERT
    assert result.exit_code == 0
    mock_download_videos.assert_called_once_with(
        tiktok_url=url,
        from_file=None,
        output_path=None,
        min_likes=100,
        min_views=1000,
        download_transcripts=None,
        transcript_language='en-US',
        metadata_only=False,
        save_metadata_path=None,
        concurrent_downloads=1,
        min_sleep_interval=None,
        max_sleep_interval=None,
        cookies_from_browser=None,
        cookies_file=None,
    )


@patch('tiktok_downloader.cli.download_videos')
def test_cli_from_file(mock_download_videos):
    """
    GIVEN a file with multiple URLs and the --from-file option
    WHEN the CLI is invoked
    THEN it should call download_videos with the file path.
    """
    # ARRANGE
    mock_download_videos.return_value = []
    runner = CliRunner()

    with runner.isolated_filesystem() as fs:
        file_path = f"{fs}/urls.txt"
        with open(file_path, "w") as f:
            f.write("test")

        result = runner.invoke(main, ['--from-file', file_path, '--metadata-only'])

        assert result.exit_code == 0
        mock_download_videos.assert_called_once_with(
            tiktok_url=None,
            from_file=file_path,
            output_path=None,
            min_likes=None,
            min_views=None,
            download_transcripts=None,
            transcript_language='en-US',
            metadata_only=True,
            save_metadata_path=None,
            concurrent_downloads=1,
            min_sleep_interval=None,
            max_sleep_interval=None,
            cookies_from_browser=None,
            cookies_file=None,
        )


@patch('tiktok_downloader.cli.download_videos')
def test_cli_download_workflow_with_language(mock_download_videos):
    """
    GIVEN a URL and transcript options
    WHEN the CLI is invoked
    THEN it should call download_videos with the correct transcript settings.
    """
    # ARRANGE
    sample_videos = [
        Video(id='123', title='Video 1', like_count=10, view_count=100, webpage_url='url1'),
    ]
    mock_download_videos.return_value = sample_videos
    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    result = runner.invoke(main, [
        url,
        '--output-path', '/my/downloads',
        '--transcripts',
        '--transcript-language', 'es'
    ])

    # ASSERT
    assert result.exit_code == 0
    assert "Downloading 1 video(s)..." in result.output
    mock_download_videos.assert_called_once_with(
        tiktok_url=url,
        from_file=None,
        output_path='/my/downloads',
        min_likes=None,
        min_views=None,
        download_transcripts=True,
        transcript_language='es',
        metadata_only=False,
        save_metadata_path=None,
        concurrent_downloads=1,
        min_sleep_interval=None,
        max_sleep_interval=None,
        cookies_from_browser=None,
        cookies_file=None,
    )


@patch('tiktok_downloader.cli.download_videos', side_effect=ValueError("Test error"))
def test_cli_handles_value_error(mock_download_videos):
    """
    GIVEN the core logic raises a ValueError
    WHEN the CLI is invoked
    THEN it should print the error message and exit.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["some_url"])

    assert result.exit_code != 0
    assert "Error: Test error" in result.output


@patch('tiktok_downloader.cli.download_videos', side_effect=Exception("Generic error"))
def test_cli_handles_generic_exception(mock_download_videos):
    """
    GIVEN the core logic raises a generic Exception
    WHEN the CLI is invoked
    THEN it should print a generic error message and exit.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["some_url"])

    assert result.exit_code != 0
    assert "An unexpected error occurred: Generic error" in result.output


def test_cli_no_input_fails():
    """
    GIVEN no URL or --from-file option
    WHEN the CLI is invoked
    THEN it should exit with an error.
    """
    runner = CliRunner()
    # We patch the function to avoid running it, but we expect the CLI to handle
    # the error before the function is even called.
    with patch('tiktok_downloader.cli.download_videos') as mock_call:
        mock_call.side_effect = ValueError("You must provide either a tiktok_url or from_file.")
        result = runner.invoke(main, [])

    assert result.exit_code != 0
    assert "Error: You must provide either a tiktok_url or from_file." in result.output


@patch('tiktok_downloader.cli.download_videos')
def test_cli_metadata_only_no_videos(mock_download_videos):
    """
    GIVEN the --metadata-only flag and no videos are found
    WHEN the CLI is invoked
    THEN it should print a 'no videos' message.
    """
    # ARRANGE
    mock_download_videos.return_value = []
    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    result = runner.invoke(main, [url, '--metadata-only'])

    # ASSERT
    assert result.exit_code == 0
    assert "No videos to display." in result.output


@patch('tiktok_downloader.cli.download_videos')
def test_cli_download_no_videos(mock_download_videos):
    """
    GIVEN no videos are found after filtering
    WHEN the CLI is invoked for download
    THEN it should print a 'no videos' message and not download.
    """
    # ARRANGE
    mock_download_videos.return_value = []
    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT
    result = runner.invoke(main, [url]) # No --metadata-only

    # ASSERT
    assert result.exit_code == 0
    assert "No videos to download." in result.output


@patch('tiktok_downloader.cli.setup_logging')
@patch('tiktok_downloader.cli.download_videos')
def test_logging_verbose_flags(mock_download_videos, mock_setup_logging):
    """
    GIVEN the -v or -vv flags
    WHEN the CLI is invoked
    THEN it should call setup_logging with the correct logging level.
    """
    # ARRANGE
    mock_download_videos.return_value = []
    runner = CliRunner()
    url = "http://tiktok.com/@testuser"

    # ACT & ASSERT for no verbose flag (default)
    runner.invoke(main, [url])
    mock_setup_logging.assert_called_with(logging.WARNING)

    # ACT & ASSERT for -v
    runner.invoke(main, [url, '-v'])
    mock_setup_logging.assert_called_with(logging.INFO)

    # ACT & ASSERT for --verbose
    runner.invoke(main, [url, '--verbose'])
    mock_setup_logging.assert_called_with(logging.INFO)

    # ACT & ASSERT for -vv
    runner.invoke(main, [url, '-vv'])
    mock_setup_logging.assert_called_with(logging.DEBUG)

    # ACT & ASSERT for -vvv (should still be DEBUG)
    runner.invoke(main, [url, '-vvv'])
    mock_setup_logging.assert_called_with(logging.DEBUG)


@patch('tiktok_downloader.cli.download_videos')
def test_cli_cookie_options(mock_download_videos):
    """
    GIVEN --cookies-from-browser and --cookies-file options
    WHEN the CLI is invoked
    THEN it should call download_videos with the correct cookie values.
    """
    # ARRANGE
    mock_download_videos.return_value = []
    runner = CliRunner()
    url = "http://tiktok.com/@testuser"
    browser = "chrome"

    with runner.isolated_filesystem() as fs:
        cookie_file = f"{fs}/cookies.txt"
        with open(cookie_file, "w") as f:
            f.write("test")

        # ACT
        result = runner.invoke(main, [
            url,
            '--cookies-from-browser', browser,
            '--cookies-file', cookie_file,
        ])

        # ASSERT
        assert result.exit_code == 0
        mock_download_videos.assert_called_once_with(
            tiktok_url=url,
            from_file=None,
            output_path=None,
            min_likes=None,
            min_views=None,
            download_transcripts=None,
            transcript_language='en-US',
            metadata_only=False,
            save_metadata_path=None,
            concurrent_downloads=1,
            min_sleep_interval=None,
            max_sleep_interval=None,
            cookies_from_browser=browser,
            cookies_file=cookie_file,
        )


@patch('tiktok_downloader.cli.download_videos')
def test_cli_save_metadata(mock_download_videos):
    """
    GIVEN a URL and the --save-metadata flag
    WHEN the CLI is invoked
    THEN it should call the download_videos function and inform the user.
    """
    # ARRANGE
    mock_download_videos.return_value = []
    runner = CliRunner()
    url = "http://tiktok.com/@testuser"
    filepath = "/tmp/metadata.csv"

    # ACT
    result = runner.invoke(main, [url, '--save-metadata', filepath])

    # ASSERT
    assert result.exit_code == 0
    assert f"Metadata saved to {filepath}" in result.output
    mock_download_videos.assert_called_once_with(
        tiktok_url=url,
        from_file=None,
        output_path=None,
        min_likes=None,
        min_views=None,
        download_transcripts=None,
        transcript_language='en-US',
        metadata_only=False,
        save_metadata_path=pathlib.Path(filepath),
        concurrent_downloads=1,
        min_sleep_interval=None,
        max_sleep_interval=None,
        cookies_from_browser=None,
        cookies_file=None,
    )
