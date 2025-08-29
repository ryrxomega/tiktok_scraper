"""
Repository for the TikTok domain, handling data access and external interactions.
"""
import yt_dlp
from datetime import datetime
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

    def _to_domain(self, schema: VideoMetadata) -> Video:
        """Converts a Pydantic schema to a domain model."""
        upload_date = None
        if schema.upload_date:
            upload_date = datetime.strptime(schema.upload_date, '%Y%m%d').date()
        return Video(
            id=schema.id,
            title=schema.title,
            like_count=schema.like_count,
            view_count=schema.view_count,
            webpage_url=schema.webpage_url,
            upload_date=upload_date,
        )

    def _get_ydl_opts(
        self,
        cookies_from_browser: Optional[str] = None,
        cookies_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Builds the base options dictionary for yt-dlp."""
        ydl_opts: Dict[str, Any] = {
            'quiet': True,
        }
        if cookies_from_browser:
            ydl_opts['cookies_from_browser'] = cookies_from_browser
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file
        return ydl_opts

    def fetch_metadata(
        self,
        url: str,
        cookies_from_browser: Optional[str] = None,
        cookies_file: Optional[str] = None,
    ) -> List[Video]:
        """
        Fetches video metadata from a given TikTok URL.

        This method supports user, hashtag, or single video URLs. It extracts
        the necessary information, parses it into VideoMetadata schemas, and
        then converts them into a list of Video domain models.

        Args:
            url: The TikTok URL to fetch metadata from.
            cookies_from_browser: The browser to extract cookies from.
            cookies_file: The path to a file containing cookies.

        Returns:
            A list of Video domain models, or an empty list if no videos are found.
        """
        ydl_opts = self._get_ydl_opts(
            cookies_from_browser=cookies_from_browser,
            cookies_file=cookies_file,
        )
        ydl_opts.update({
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
                        upload_date=video_info.get('upload_date'),
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
        cookies_from_browser: Optional[str] = None,
        cookies_file: Optional[str] = None,
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
            cookies_from_browser: The browser to extract cookies from.
            cookies_file: The path to a file containing cookies.
        """
        if not videos:
            return

        ydl_opts = self._get_ydl_opts(
            cookies_from_browser=cookies_from_browser,
            cookies_file=cookies_file,
        )
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
