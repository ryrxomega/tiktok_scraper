"""
The core application logic for the TikTok Downloader.

This module is responsible for orchestrating the fetching, filtering, and
downloading of TikTok videos. It is designed to be used both by the CLI
and as a library in other Python applications.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .domains.config.repository import ConfigRepository
from .domains.config.schemas import Config
from .domains.config.services import ConfigService
from .domains.tiktok.models import Video
from .domains.tiktok.repository import TikTokRepository
from .domains.tiktok.services import FilterService

logger = logging.getLogger(__name__)


def _resolve_archive_path(
    download_archive: Optional[str],
    config_archive: Optional[str],
    output_path: str,
) -> str:
    """Resolves the path for the download archive."""
    if download_archive:
        return download_archive
    if config_archive:
        return config_archive
    return str(Path(output_path) / ".tiktok-downloader-archive.txt")


def _resolve_settings(
    config: Config,
    output_path: Optional[str],
    min_likes: Optional[int],
    min_views: Optional[int],
    download_transcripts: Optional[bool],
    transcript_language: str,
    concurrent_downloads: int,
    min_sleep_interval: Optional[int],
    max_sleep_interval: Optional[int],
    cookies_from_browser: Optional[str],
    cookies_file: Optional[str],
    download_archive: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Merges settings from the config file and CLI options.

    CLI options always take precedence over settings from the config file.
    """
    resolved_settings = {
        'output_path': output_path or config.output_path or '.',
        'min_likes': min_likes if min_likes is not None else config.min_likes,
        'min_views': min_views if min_views is not None else config.min_views,
        'concurrent_downloads': concurrent_downloads if concurrent_downloads is not None else config.concurrent_downloads,
        'min_sleep_interval': min_sleep_interval if min_sleep_interval is not None else config.min_sleep_interval,
        'max_sleep_interval': max_sleep_interval if max_sleep_interval is not None else config.max_sleep_interval,
        'cookies_from_browser': cookies_from_browser or config.cookies_from_browser,
        'cookies_file': cookies_file or config.cookies_file,
    }

    # Determine if transcripts should be downloaded
    transcripts_enabled = download_transcripts if download_transcripts is not None else config.transcripts
    if transcripts_enabled:
        resolved_settings['transcript_language'] = transcript_language or config.transcript_language
    else:
        resolved_settings['transcript_language'] = None

    # Resolve download archive path
    resolved_settings['download_archive'] = _resolve_archive_path(
        download_archive,
        config.download_archive,
        str(resolved_settings['output_path'])
    )

    logger.debug("Resolved settings: %s", resolved_settings)
    return resolved_settings


def _get_urls_to_process(tiktok_url: Optional[str], from_file: Optional[str]) -> List[str]:
    """
    Gets a list of URLs to process from the arguments.
    """
    urls_to_process: List[str] = []
    if from_file:
        logger.info("Reading URLs from file: %s", from_file)
        with open(from_file, 'r') as f:
            urls_from_file = [line.strip() for line in f if line.strip()]
            urls_to_process.extend(urls_from_file)
        logger.debug("Found %d URLs in %s", len(urls_from_file), from_file)
    if tiktok_url:
        logger.info("Adding URL from argument: %s", tiktok_url)
        urls_to_process.append(tiktok_url)

    if not urls_to_process:
        logger.error("No URLs provided via --from-file or argument.")
        raise ValueError("You must provide either a tiktok_url or from_file.")

    logger.info("Total URLs to process: %d", len(urls_to_process))
    return urls_to_process


def download_videos(
    tiktok_url: Optional[str] = None,
    from_file: Optional[str] = None,
    output_path: Optional[str] = None,
    min_likes: Optional[int] = None,
    min_views: Optional[int] = None,
    download_transcripts: Optional[bool] = None,
    transcript_language: str = 'en-US',
    metadata_only: bool = False,
    config_path: str = "config.ini",
    concurrent_downloads: int = 1,
    min_sleep_interval: Optional[int] = None,
    max_sleep_interval: Optional[int] = None,
    cookies_from_browser: Optional[str] = None,
    cookies_file: Optional[str] = None,
    download_archive: Optional[str] = None,
) -> List[Video]:
    """
    The main entry point for the TikTok Downloader application.

    This function orchestrates the process of fetching, filtering, and
    downloading TikTok videos based on the provided parameters.

    Args:
        tiktok_url: A single TikTok URL.
        from_file: Path to a file containing one TikTok URL per line.
        output_path: The directory to save the downloaded videos.
        min_likes: Filter for videos with at least this many likes.
        min_views: Filter for videos with at least this many views.
        download_transcripts: Whether to download transcripts.
        transcript_language: The language for the transcript.
        metadata_only: If True, only fetch and return metadata without downloading.
        config_path: Path to the
        configuration file.
        cookies_from_browser: The browser to extract cookies from.
        cookies_file: The path to a file containing cookies.
        download_archive: Path to the download archive file.

    Returns:
        A list of `Video` objects that match the criteria.

    Raises:
        ValueError: If no URLs are provided.
    """
    # 1. Setup
    logger.info("Initializing services...")
    config_repo = ConfigRepository()
    config_service = ConfigService(repository=config_repo)
    repo = TikTokRepository()
    filter_service = FilterService()
    logger.debug("Services initialized.")

    # 2. Configuration & URL processing
    logger.info("Loading configuration from %s.", config_path)
    config = config_service.load_config(Path(config_path))
    logger.debug("Loaded config: %s", config)

    settings = _resolve_settings(
        config,
        output_path,
        min_likes,
        min_views,
        download_transcripts,
        transcript_language,
        concurrent_downloads,
        min_sleep_interval,
        max_sleep_interval,
        cookies_from_browser,
        cookies_file,
        download_archive,
    )
    urls = _get_urls_to_process(tiktok_url, from_file)

    # 3. Core Logic: Fetch and Filter
    logger.info("Fetching metadata for %d URL(s)...", len(urls))
    all_videos: List[Video] = []
    for url in urls:
        logger.debug("Fetching from URL: %s", url)
        try:
            all_videos.extend(
                repo.fetch_metadata(
                    url=url,
                    cookies_from_browser=settings['cookies_from_browser'],
                    cookies_file=settings['cookies_file'],
                )
            )
        except Exception as exc:
            logger.error("Error fetching metadata from URL %s: %s", url, exc)
    logger.info("Fetched metadata for a total of %d video(s).", len(all_videos))

    logger.info("Applying filters...")
    filtered_videos = filter_service.apply_filters(
        videos=all_videos,
        min_likes=settings['min_likes'],
        min_views=settings['min_views']
    )
    logger.info("Found %d video(s) matching the criteria.", len(filtered_videos))

    # 4. Output / Action
    if metadata_only:
        logger.info("Metadata only mode enabled. Skipping download.")
    elif filtered_videos:
        logger.info("Downloading %d video(s)...", len(filtered_videos))
        repo.download_videos(
            videos=filtered_videos,
            output_path=settings['output_path'],
            transcript_language=settings['transcript_language'],
            concurrent_downloads=settings.get('concurrent_downloads', 1),
            min_sleep_interval=settings['min_sleep_interval'],
            max_sleep_interval=settings['max_sleep_interval'],
            cookies_from_browser=settings['cookies_from_browser'],
            cookies_file=settings['cookies_file'],
            download_archive_path=settings['download_archive'],
        )
        logger.info("Download complete.")
    else:
        logger.info("No videos to download.")

    return filtered_videos
