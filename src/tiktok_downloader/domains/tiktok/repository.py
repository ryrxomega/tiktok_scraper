"""
Repository for the TikTok domain, handling data access and external interactions.
"""
import yt_dlp
from typing import List, Dict, Any, Optional

from .models import Video
from .schemas import VideoMetadata


class TikTokRepository:
    """
    A repository for interacting with TikTok via the yt-dlp library.

    This class encapsulates all direct calls to yt-dlp, providing a clean
    interface to the rest of the application. It is responsible for fetching
    data and converting it from external schemas to internal domain models.
    """

    def _get_ydl_opts(
        self,
        cookies: Optional[str] = None,
        cookies_from_browser: Optional[str] = None
    ) -> Dict[str, Any]:
        """Constructs the yt-dlp options dictionary."""
        opts: Dict[str, Any] = {}
        if cookies:
            opts['cookies'] = cookies
        if cookies_from_browser:
            opts['cookiesfrombrowser'] = (cookies_from_browser,)
        return opts

    def _to_domain(self, schema: VideoMetadata) -> Video:
        """Converts a Pydantic schema to a domain model."""
        return Video(
            id=schema.id,
            title=schema.title,
            like_count=schema.like_count,
            view_count=schema.view_count,
            webpage_url=schema.webpage_url,
        )

    def fetch_metadata(
        self,
        url: str,
        cookies: Optional[str] = None,
        cookies_from_browser: Optional[str] = None
    ) -> List[Video]:
        """
        Fetches video metadata from a given TikTok URL.

        This method supports user, hashtag, or single video URLs. It extracts
        the necessary information, parses it into VideoMetadata schemas, and
        then converts them into a list of Video domain models.

        Args:
            url: The TikTok URL to fetch metadata from.
            cookies: Path to a cookies file.
            cookies_from_browser: Name of the browser to use for cookies.

        Returns:
            A list of Video domain models, or an empty list if no videos are found.
        """
        ydl_opts = self._get_ydl_opts(cookies, cookies_from_browser)
        ydl_opts.update({
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
        })

        videos: List[Video] = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            video_list = info.get('entries', [])
            if not video_list and info:
                video_list = [info]

            for video_info in video_list:
                if not video_info:
                    continue
                try:
                    # First, parse into the Pydantic schema for validation
                    schema = VideoMetadata(
                        id=video_info.get('id'),
                        title=video_info.get('title'),
                        like_count=video_info.get('like_count'),
                        view_count=video_info.get('view_count'),
                        webpage_url=video_info.get('webpage_url'),
                    )
                    # Then, convert to the internal domain model
                    videos.append(self._to_domain(schema))
                except Exception:
                    # If metadata is malformed, skip it.
                    pass

        return videos

    def download_videos(
        self,
        videos: List[Video],
        output_path: str,
        transcript_language: Optional[str],
        concurrent_downloads: int = 1,
        min_sleep_interval: Optional[int] = None,
        max_sleep_interval: Optional[int] = None,
        cookies: Optional[str] = None,
        cookies_from_browser: Optional[str] = None,
    ) -> None:
        """
        Downloads the given list of videos using yt-dlp.

        Args:
            videos: A list of Video domain models to download.
            output_path: The directory where files should be saved.
            transcript_language: The language of the transcript to download.
            concurrent_downloads: The number of concurrent fragments to download.
            min_sleep_interval: Minimum time to wait between downloads.
            max_sleep_interval: Maximum time to wait between downloads.
            cookies: Path to a cookies file.
            cookies_from_browser: Name of the browser to use for cookies.
        """
        if not videos:
            return

        ydl_opts = self._get_ydl_opts(cookies, cookies_from_browser)
        ydl_opts.update({
            'outtmpl': f'{output_path}/%(title)s [%(id)s].%(ext)s',
            'writethumbnail': True,
        })

        if transcript_language:
            ydl_opts.update({
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': [transcript_language],
            })

        if concurrent_downloads > 1:
            ydl_opts['concurrent_fragment_downloads'] = concurrent_downloads
        if min_sleep_interval:
            ydl_opts['sleep_interval'] = min_sleep_interval
        if max_sleep_interval:
            ydl_opts['max_sleep_interval'] = max_sleep_interval

        video_urls = [v.webpage_url for v in videos]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(video_urls)
