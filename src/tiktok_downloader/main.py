"""
The core application logic for the TikTok Downloader.

This module is responsible for orchestrating the fetching, filtering, and
downloading of TikTok videos. It is designed to be used both by the CLI
and as a library in other Python applications.
"""
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from .domains.config.repository import ConfigRepository
from .domains.config.schemas import Config
from .domains.config.services import ConfigService
from .domains.tiktok.models import Video
from .domains.tiktok.repository import TikTokRepository
from .domains.tiktok.services import FilterService


def _resolve_settings(
    config: Config,
    output_path: Optional[str],
    min_likes: Optional[int],
    min_views: Optional[int],
    download_transcripts: Optional[bool],
    transcript_language: str,
) -> Dict[str, Any]:
    """
    Merges settings from the config file and CLI options.

    CLI options always take precedence over settings from the config file.
    """
    logging.debug(f"Resolving settings. Initial config: {config}")
    logging.debug(f"CLI options: output_path={output_path}, min_likes={min_likes}, min_views={min_views}, download_transcripts={download_transcripts}, transcript_language={transcript_language}")

    resolved_settings = {
        'output_path': output_path or config.output_path or '.',
        'min_likes': min_likes if min_likes is not None else config.min_likes,
        'min_views': min_views if min_views is not None else config.min_views,
    }

    # Determine if transcripts should be downloaded
    if download_transcripts is not None:
        transcripts_enabled = download_transcripts
    else:
        transcripts_enabled = config.transcripts or False

    # Set transcript language if enabled
    if transcripts_enabled:
        resolved_settings['transcript_language'] = transcript_language or config.transcript_language
    else:
        resolved_settings['transcript_language'] = None

    logging.debug(f"Resolved settings: {resolved_settings}")
    return resolved_settings


def _get_urls_to_process(tiktok_url: Optional[str], from_file: Optional[str]) -> List[str]:
    """
    Gets a list of URLs to process from the arguments.
    """
    urls_to_process: List[str] = []
    if from_file:
        logging.info(f"Reading URLs from file: {from_file}")
        with open(from_file, 'r') as f:
            urls_to_process.extend(line.strip() for line in f if line.strip())
    if tiktok_url:
        urls_to_process.append(tiktok_url)

    if not urls_to_process:
        raise ValueError("You must provide either a tiktok_url or from_file.")
    logging.debug(f"URLs to process: {urls_to_process}")
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

    Returns:
        A list of `Video` objects that match the criteria.

    Raises:
        ValueError: If no URLs are provided.
    """
    # 1. Setup
    logging.info("Initializing services...")
    config_repo = ConfigRepository()
    config_service = ConfigService(repository=config_repo)
    repo = TikTokRepository()
    filter_service = FilterService()

    # 2. Configuration & URL processing
    logging.info(f"Loading configuration from {config_path}")
    config = config_service.load_config(Path(config_path))
    settings = _resolve_settings(
        config, output_path, min_likes, min_views, download_transcripts, transcript_language
    )
    urls = _get_urls_to_process(tiktok_url, from_file)

    # 3. Core Logic: Fetch and Filter
    logging.info(f"Fetching metadata for {len(urls)} URL(s)...")
    all_videos: List[Video] = []
    for url in urls:
        logging.debug(f"Fetching metadata for URL: {url}")
        all_videos.extend(repo.fetch_metadata(url))
    logging.info(f"Fetched metadata for {len(all_videos)} total videos.")

    logging.info("Applying filters...")
    filtered_videos = filter_service.apply_filters(
        videos=all_videos,
        min_likes=settings['min_likes'],
        min_views=settings['min_views']
    )
    logging.debug(f"Filtered down to {len(filtered_videos)} videos.")

    # 4. Output / Action
    if not metadata_only and filtered_videos:
        logging.info(f"Triggering download for {len(filtered_videos)} videos.")
        repo.download_videos(
            videos=filtered_videos,
            output_path=settings['output_path'],
            transcript_language=settings['transcript_language'],
        )

    return filtered_videos
