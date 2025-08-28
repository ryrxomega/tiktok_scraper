import yt_dlp
from typing import List, Dict, Any

from .schemas import VideoMetadata

class TikTokRepository:
    """
    A repository for interacting with TikTok via the yt-dlp library.
    This class encapsulates all direct calls to yt-dlp, providing a clean
    interface to the rest of the application.
    """

    def fetch_metadata(self, url: str) -> List[VideoMetadata]:
        """
        Fetches video metadata from a given TikTok URL.

        This method supports user, hashtag, or single video URLs. It extracts
        the necessary information and parses it into a list of VideoMetadata objects.

        Args:
            url: The TikTok URL to fetch metadata from.

        Returns:
            A list of VideoMetadata objects, or an empty list if no videos are found.
        """
        # These options are chosen to efficiently fetch metadata without downloading.
        # 'quiet': Suppresses console output from yt-dlp.
        # 'extract_flat': Fetches the metadata for all videos in a playlist/user page
        #                 in a single batch, which is much faster than one by one.
        # 'force_generic_extractor': Ensures consistent behavior across different URL types.
        ydl_opts: Dict[str, Any] = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
        }

        videos = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # yt-dlp returns a dict with an 'entries' key for multiple videos (e.g., user page)
            # or just a single dict for a single video URL. We handle both cases.
            video_list = info.get('entries', [])
            if not video_list and info:
                # It's likely a single video URL.
                video_list = [info]

            for video_info in video_list:
                if not video_info:
                    continue
                # We use .get() for safety, but Pydantic will enforce that
                # the required fields are present and of the correct type.
                try:
                    videos.append(
                        VideoMetadata(
                            id=video_info.get('id'),
                            title=video_info.get('title'),
                            like_count=video_info.get('like_count'),
                            view_count=video_info.get('view_count'),
                            webpage_url=video_info.get('webpage_url'),
                        )
                    )
                except Exception:
                    # If a video's metadata is malformed and fails Pydantic validation,
                    # we'll skip it and continue with the rest.
                    # AICODE-NOTE: In a real-world scenario, we might want to log this event.
                    pass

        return videos

    def download_videos(
        self,
        videos: List[VideoMetadata],
        output_path: str,
        download_transcripts: bool,
    ) -> None:
        """
        Downloads the given list of videos using yt-dlp.

        Args:
            videos: A list of VideoMetadata objects to download.
            output_path: The directory where files should be saved.
            download_transcripts: Whether to download subtitles/transcripts.
        """
        if not videos:
            return

        ydl_opts: Dict[str, Any] = {
            # Define the output template for filenames.
            'outtmpl': f'{output_path}/%(title)s [%(id)s].%(ext)s',
            # Also download the video thumbnail.
            'writethumbnail': True,
        }

        if download_transcripts:
            ydl_opts.update({
                'writesubtitles': True,      # For manually created subtitles
                'writeautomaticsub': True, # For auto-generated subtitles
                'subtitleslangs': ['en'],    # Specify English transcripts
            })

        # Extract the URLs from the metadata objects.
        video_urls = [v.webpage_url for v in videos]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # This call will download the videos specified in the list.
            ydl.download(video_urls)
