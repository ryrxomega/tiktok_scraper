"""
The core application logic for the TikTok Downloader.

This module is responsible for orchestrating the fetching, filtering, and
downloading of TikTok videos. It is designed to be used both by the CLI
and as a library in other Python applications.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .domains.config.repository import ConfigRepository
from .domains.config.schemas import Config
from .domains.config.services import ConfigService
from .domains.tiktok.models import Video
from .domains.tiktok.repository import TikTokRepository
from .domains.tiktok.services import FilterService

logger = logging.getLogger(__name__)


def _resolve_settings(
    config: Config,
    cli_args: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merges settings from the config file and CLI options.

    CLI options always take precedence over settings from the config file.
    """
    resolved_settings: Dict[str, Any] = {}

    # Define settings to be resolved, mapping CLI arg name to config name
    # and providing a default value if neither is present.
    setting_definitions: List[Tuple[str, str, Any]] = [
        ('output_path', 'output_path', '.'),
        ('min_likes', 'min_likes', None),
        ('min_views', 'min_views', None),
        ('concurrent_downloads', 'concurrent_downloads', 1),
        ('min_sleep_interval', 'min_sleep_interval', None),
        ('max_sleep_interval', 'max_sleep_interval', None),
        ('cookies_from_browser', 'cookies_from_browser', None),
        ('cookies_file', 'cookies_file', None),
        ('date_after', 'date_after', None),
    ]

    for cli_key, config_key, default in setting_definitions:
        cli_value = cli_args.get(cli_key)
        config_value = getattr(config, config_key, None)

        if cli_value is not None:
            resolved_settings[cli_key] = cli_value
        else:
            resolved_settings[cli_key] = config_value if config_value is not None else default

    # Special handling for transcripts
    download_transcripts = cli_args.get('download_transcripts')
    if download_transcripts is not None:
        transcripts_enabled = download_transcripts
    else:
        transcripts_enabled = config.transcripts or False

    if transcripts_enabled:
        transcript_language = cli_args.get('transcript_language') or config.transcript_language or 'en-US'
        resolved_settings['transcript_language'] = transcript_language
    else:
        resolved_settings['transcript_language'] = None

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
    **kwargs: Any,
) -> List[Video]:
    """
    The main entry point for the TikTok Downloader application.

    This function orchestrates the process of fetching, filtering, and
    downloading TikTok videos based on the provided parameters.
    """
    # 1. Setup
    logger.info("Initializing services...")
    config_repo = ConfigRepository()
    config_service = ConfigService(repository=config_repo)
    repo = TikTokRepository()
    filter_service = FilterService()
    logger.debug("Services initialized.")

    # 2. Configuration & URL processing
    config_path = kwargs.get('config_path', "config.ini")
    logger.info("Loading configuration from %s.", config_path)
    config = config_service.load_config(Path(config_path))
    logger.debug("Loaded config: %s", config)

    settings = _resolve_settings(config, kwargs)
    urls = _get_urls_to_process(kwargs.get('tiktok_url'), kwargs.get('from_file'))

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
                    date_after=settings['date_after'],
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
    if kwargs.get('metadata_only'):
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
        )
        logger.info("Download complete.")
    else:
        logger.info("No videos to download.")

    return filtered_videos
