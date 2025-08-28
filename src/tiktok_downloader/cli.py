from typing import List, Optional, Dict, Any
import click
from pathlib import Path

from .domains.config.services import ConfigService
from .domains.tiktok.repository import TikTokRepository
from .domains.tiktok.services import FilterService
from .domains.tiktok.schemas import VideoMetadata

# --- Helper Functions for CLI Logic ---

def _resolve_settings(
    config: Dict[str, Any],
    output_path: Optional[str],
    min_likes: Optional[int],
    min_views: Optional[int],
    download_transcripts: Optional[bool],
) -> Dict[str, Any]:
    """Merges settings from config file and CLI options."""
    resolved_settings = {
        'output_path': output_path or config.get('output_path', '.'),
        'min_likes': min_likes if min_likes is not None else config.get('min_likes'),
        'min_views': min_views if min_views is not None else config.get('min_views'),
    }

    if download_transcripts is not None:
        resolved_settings['transcripts'] = download_transcripts
    else:
        resolved_settings['transcripts'] = config.get('transcripts', False)

    return resolved_settings

def _get_urls_to_process(tiktok_url: Optional[str], from_file: Optional[str]) -> List[str]:
    """Gets a list of URLs from the CLI arguments."""
    urls_to_process: List[str] = []
    if from_file:
        with open(from_file, 'r') as f:
            urls_to_process.extend(line.strip() for line in f if line.strip())
    if tiktok_url:
        urls_to_process.append(tiktok_url)

    if not urls_to_process:
        click.echo("Error: You must provide either a TIKTOK_URL or use the --from-file option.", err=True)
        raise click.Abort()
    return urls_to_process

def _display_metadata(videos: List[VideoMetadata]):
    """Prints formatted metadata for a list of videos."""
    if not videos:
        click.echo("No videos to display.")
        return
    for video in videos:
        click.echo("-" * 20)
        click.echo(f"ID:          {video.id}")
        click.echo(f"Title:       {video.title}")
        click.echo(f"Likes:       {video.like_count}")
        click.echo(f"Views:       {video.view_count}")
        click.echo(f"URL:         {video.webpage_url}")

# --- Main CLI Command ---

@click.command()
@click.argument('tiktok_url', required=False)
@click.option('--from-file', type=click.Path(exists=True, dir_okay=False, resolve_path=True), help='Path to a text file containing one TikTok URL per line.')
@click.option('--output-path', type=click.Path(file_okay=False, writable=True, resolve_path=True), help='Specify the download directory.')
@click.option('--min-likes', type=int, help='Filter videos with at least this many likes.')
@click.option('--min-views', type=int, help='Filter videos with at least this many views.')
@click.option('--transcripts/--no-transcripts', 'download_transcripts', default=None, help='Enable or disable transcript downloads.')
@click.option('--metadata-only', is_flag=True, help='Fetch and display metadata without downloading videos.')
def main(
    tiktok_url: Optional[str],
    from_file: Optional[str],
    output_path: Optional[str],
    min_likes: Optional[int],
    min_views: Optional[int],
    download_transcripts: Optional[bool],
    metadata_only: bool,
):
    """
    A command-line tool to download TikTok videos and their metadata
    based on user-defined filters.
    You must provide either a TIKTOK_URL or the --from-file option.
    """
    # 1. Setup
    config_service = ConfigService()
    repo = TikTokRepository()
    filter_service = FilterService()

    # 2. Configuration & URL processing
    config = config_service.load_config(Path("config.ini"))
    settings = _resolve_settings(config, output_path, min_likes, min_views, download_transcripts)
    urls = _get_urls_to_process(tiktok_url, from_file)

    # 3. Core Logic: Fetch and Filter
    all_videos: List[VideoMetadata] = []
    for url in urls:
        click.echo(f"Fetching metadata from {url}...")
        all_videos.extend(repo.fetch_metadata(url))

    filtered_videos = filter_service.apply_filters(
        videos=all_videos,
        min_likes=settings['min_likes'],
        min_views=settings['min_views']
    )
    click.echo(f"Found {len(filtered_videos)} videos that match the criteria.")

    # 4. Output / Action
    if metadata_only:
        _display_metadata(filtered_videos)
    else:
        if not filtered_videos:
            click.echo("No videos to download.")
            return
        click.echo(f"Downloading {len(filtered_videos)} video(s) to {settings['output_path']}...")
        repo.download_videos(
            videos=filtered_videos,
            output_path=settings['output_path'],
            download_transcripts=settings['transcripts'],
        )
        click.echo("Download complete.")
