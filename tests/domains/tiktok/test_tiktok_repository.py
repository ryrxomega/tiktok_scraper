from unittest.mock import patch, MagicMock

from tiktok_downloader.domains.tiktok.repository import TikTokRepository
from tiktok_downloader.domains.tiktok.models import Video


@patch('yt_dlp.YoutubeDL')
def test_fetch_metadata_success(MockYoutubeDL):
    """
    GIVEN a URL
    WHEN fetch_metadata is called
    THEN it should use yt-dlp to fetch info and return a list of Video domain models.
    """
    # ARRANGE
    mock_yt_dlp_output = {
        'entries': [
            {
                'id': '12345',
                'title': 'Test Video 1',
                'like_count': 100,
                'view_count': 1000,
                'webpage_url': 'http://tiktok.com/video/12345'
            },
            {
                'id': '67890',
                'title': 'Test Video 2',
                'like_count': 200,
                'view_count': 2000,
                'webpage_url': 'http://tiktok.com/video/67890'
            }
        ]
    }

    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = mock_yt_dlp_output
    MockYoutubeDL.return_value.__enter__.return_value = mock_instance

    repo = TikTokRepository()
    url = "http://tiktok.com/@testuser"

    # ACT
    videos = repo.fetch_metadata(url, cookies=None, cookies_from_browser=None)

    # ASSERT
    assert len(videos) == 2
    assert isinstance(videos[0], Video)
    assert videos[0].id == '12345'
    assert videos[0].like_count == 100
    assert videos[1].id == '67890'
    assert videos[1].view_count == 2000

    MockYoutubeDL.assert_called_once_with({
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    })
    mock_instance.extract_info.assert_called_once_with(url, download=False)


@patch('yt_dlp.YoutubeDL')
def test_download_videos_with_transcript_language(MockYoutubeDL):
    """
    GIVEN a list of Video models and a transcript language
    WHEN download_videos is called
    THEN it should call yt-dlp with the correct subtitle options.
    """
    # ARRANGE
    videos_to_download = [
        Video(id='12345', title='Video 1', webpage_url='http://.../12345'),
    ]
    output_path = "/fake/path"
    transcript_language = 'es'

    mock_instance = MagicMock()
    MockYoutubeDL.return_value.__enter__.return_value = mock_instance
    repo = TikTokRepository()

    # ACT
    repo.download_videos(
        videos=videos_to_download,
        output_path=output_path,
        transcript_language=transcript_language,
        cookies=None,
        cookies_from_browser=None
    )

    # ASSERT
    expected_ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s [%(id)s].%(ext)s',
        'writethumbnail': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [transcript_language],
    }
    MockYoutubeDL.assert_called_once_with(expected_ydl_opts)
    mock_instance.download.assert_called_once_with([v.webpage_url for v in videos_to_download])


@patch('yt_dlp.YoutubeDL')
def test_download_videos_without_transcripts(MockYoutubeDL):
    """
    GIVEN a list of Video models and transcript_language is None
    WHEN download_videos is called
    THEN it should call yt-dlp without any subtitle options.
    """
    # ARRANGE
    videos_to_download = [
        Video(id='12345', title='Video 1', webpage_url='http://.../12345'),
    ]
    output_path = "/fake/path"

    mock_instance = MagicMock()
    MockYoutubeDL.return_value.__enter__.return_value = mock_instance
    repo = TikTokRepository()

    # ACT
    repo.download_videos(
        videos=videos_to_download,
        output_path=output_path,
        transcript_language=None,
        cookies=None,
        cookies_from_browser=None
    )

    # ASSERT
    expected_ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s [%(id)s].%(ext)s',
        'writethumbnail': True,
    }
    MockYoutubeDL.assert_called_once_with(expected_ydl_opts)
    mock_instance.download.assert_called_once_with([v.webpage_url for v in videos_to_download])


@patch('yt_dlp.YoutubeDL')
def test_fetch_metadata_single_video(MockYoutubeDL):
    """
    GIVEN a URL for a single video
    WHEN fetch_metadata is called
    THEN it should correctly handle the non-list output from yt-dlp.
    """
    # ARRANGE
    mock_video_info = {
        'id': '98765',
        'title': 'Single Test Video',
        'like_count': 99,
        'view_count': 999,
        'webpage_url': 'http://tiktok.com/video/98765'
    }
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = mock_video_info
    MockYoutubeDL.return_value.__enter__.return_value = mock_instance

    repo = TikTokRepository()
    url = "http://tiktok.com/video/98765"

    # ACT
    videos = repo.fetch_metadata(url, cookies=None, cookies_from_browser=None)

    # ASSERT
    assert len(videos) == 1
    assert isinstance(videos[0], Video)
    assert videos[0].id == '98765'


@patch('yt_dlp.YoutubeDL')
def test_fetch_metadata_malformed_entry(MockYoutubeDL):
    """
    GIVEN yt-dlp returns an entry with missing required fields
    WHEN fetch_metadata is called
    THEN it should skip the malformed entry and continue processing others.
    """
    # ARRANGE
    mock_yt_dlp_output = {
        'entries': [
            {'id': '123', 'title': 'Good Video', 'like_count': 1, 'view_count': 1, 'webpage_url': '...'},
            {'id': '456', 'title': 'Malformed Video'}, # Missing fields
            {'id': '789', 'title': 'Another Good Video', 'like_count': 2, 'view_count': 2, 'webpage_url': '...'}
        ]
    }
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = mock_yt_dlp_output
    MockYoutubeDL.return_value.__enter__.return_value = mock_instance

    repo = TikTokRepository()

    # ACT
    videos = repo.fetch_metadata("http://tiktok.com/@testuser", cookies=None, cookies_from_browser=None)

    # ASSERT
    assert len(videos) == 2
    assert videos[0].id == '123'
    assert videos[1].id == '789'


@patch('yt_dlp.YoutubeDL')
def test_download_videos_with_cookies_from_browser(MockYoutubeDL):
    """
    GIVEN a list of Video models and a browser name
    WHEN download_videos is called
    THEN it should call yt-dlp with the correct cookies_from_browser option.
    """
    # ARRANGE
    videos_to_download = [
        Video(id='12345', title='Video 1', webpage_url='http://.../12345'),
    ]
    output_path = "/fake/path"

    mock_instance = MagicMock()
    MockYoutubeDL.return_value.__enter__.return_value = mock_instance
    repo = TikTokRepository()

    # ACT
    repo.download_videos(
        videos=videos_to_download,
        output_path=output_path,
        transcript_language=None,
        cookies=None,
        cookies_from_browser="chrome",
    )

    # ASSERT
    expected_ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s [%(id)s].%(ext)s',
        'writethumbnail': True,
        'cookiesfrombrowser': ("chrome",),
    }
    MockYoutubeDL.assert_called_once_with(expected_ydl_opts)


@patch('yt_dlp.YoutubeDL')
def test_fetch_metadata_with_cookies_from_browser(MockYoutubeDL):
    """
    GIVEN a URL and a browser name
    WHEN fetch_metadata is called
    THEN it should call yt-dlp with the correct cookies_from_browser option.
    """
    # ARRANGE
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = {}
    MockYoutubeDL.return_value.__enter__.return_value = mock_instance

    repo = TikTokRepository()
    url = "http://tiktok.com/@testuser"

    # ACT
    repo.fetch_metadata(url, cookies=None, cookies_from_browser="chrome")

    # ASSERT
    expected_ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'cookiesfrombrowser': ("chrome",),
    }
    MockYoutubeDL.assert_called_once_with(expected_ydl_opts)


@patch('yt_dlp.YoutubeDL')
def test_download_videos_with_cookies(MockYoutubeDL):
    """
    GIVEN a list of Video models and a cookies path
    WHEN download_videos is called
    THEN it should call yt-dlp with the correct cookie option.
    """
    # ARRANGE
    videos_to_download = [
        Video(id='12345', title='Video 1', webpage_url='http://.../12345'),
    ]
    output_path = "/fake/path"
    cookies_path = "/path/to/cookies.txt"

    mock_instance = MagicMock()
    MockYoutubeDL.return_value.__enter__.return_value = mock_instance
    repo = TikTokRepository()

    # ACT
    repo.download_videos(
        videos=videos_to_download,
        output_path=output_path,
        transcript_language=None,
        cookies=cookies_path,
        cookies_from_browser=None,
    )

    # ASSERT
    expected_ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s [%(id)s].%(ext)s',
        'writethumbnail': True,
        'cookiefile': cookies_path,
    }
    MockYoutubeDL.assert_called_once_with(expected_ydl_opts)


@patch('yt_dlp.YoutubeDL')
def test_fetch_metadata_with_cookies(MockYoutubeDL):
    """
    GIVEN a URL and a cookies path
    WHEN fetch_metadata is called
    THEN it should call yt-dlp with the correct cookie option.
    """
    # ARRANGE
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = {}
    MockYoutubeDL.return_value.__enter__.return_value = mock_instance

    repo = TikTokRepository()
    url = "http://tiktok.com/@testuser"
    cookies_path = "/path/to/cookies.txt"

    # ACT
    repo.fetch_metadata(url, cookies=cookies_path, cookies_from_browser=None)

    # ASSERT
    expected_ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'cookiefile': cookies_path,
    }
    MockYoutubeDL.assert_called_once_with(expected_ydl_opts)


@patch('yt_dlp.YoutubeDL')
def test_download_videos_empty_list(MockYoutubeDL):
    """
    GIVEN an empty list of videos
    WHEN download_videos is called
    THEN it should not call yt-dlp and exit gracefully.
    """
    # ARRANGE
    repo = TikTokRepository()

    # ACT
    repo.download_videos(videos=[], output_path="/tmp", transcript_language=None, cookies=None, cookies_from_browser=None)

    # ASSERT
    MockYoutubeDL.assert_not_called()


@patch('yt_dlp.YoutubeDL')
def test_fetch_metadata_with_empty_entry(MockYoutubeDL):
    """
    GIVEN yt-dlp returns a list with a None entry
    WHEN fetch_metadata is called
    THEN it should skip the empty entry and continue processing others.
    """
    # ARRANGE
    mock_yt_dlp_output = {
        'entries': [
            {'id': '123', 'title': 'Good Video', 'like_count': 1, 'view_count': 1, 'webpage_url': '...'},
            None,  # Simulate an empty or problematic entry
            {'id': '789', 'title': 'Another Good Video', 'like_count': 2, 'view_count': 2, 'webpage_url': '...'}
        ]
    }
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = mock_yt_dlp_output
    MockYoutubeDL.return_value.__enter__.return_value = mock_instance

    repo = TikTokRepository()

    # ACT
    videos = repo.fetch_metadata("http://tiktok.com/@testuser", cookies=None, cookies_from_browser=None)

    # ASSERT
    assert len(videos) == 2
    assert videos[0].id == '123'
    assert videos[1].id == '789'
