"""
Defines the command-line interface for the TikTok Downloader.

This module uses the `click` library to create a user-friendly CLI
and orchestrates the application's services to perform its functions.
"""
import logging
from typing import List, Any

import click

from .domains.tiktok.models import Video
from .logging import setup_logging
from .main import download_videos


def _display_metadata(videos: List[Video]):
    """
    Prints formatted metadata for a list of videos to the console.

    Args:
        videos: A list of Video objects whose metadata should be displayed.
    """
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


@click.command()
@click.argument('tiktok_url', required=False)
@click.option('--from-file', type=click.Path(exists=True, dir_okay=False, resolve_path=True), help='Path to a text file containing one TikTok URL per line.')
@click.option('--output-path', type=click.Path(file_okay=False, writable=True, resolve_path=True), help='Specify the download directory.')
@click.option('--min-likes', type=int, help='Filter videos with at least this many likes.')
@click.option('--min-views', type=int, help='Filter videos with at least this many views.')
@click.option('--transcripts/--no-transcripts', 'download_transcripts', default=None, help='Enable or disable transcript downloads.')
@click.option('--transcript-language', default='en-US', help='The language of the transcript to download.')
@click.option('--metadata-only', is_flag=True, help='Fetch and display metadata without downloading videos.')
@click.option('--concurrent-downloads', type=int, default=1, help='Number of concurrent downloads.')
@click.option('--min-sleep-interval', type=int, help='Minimum time to wait between downloads.')
@click.option('--max-sleep-interval', type=int, help='Maximum time to wait between downloads.')
@click.option('--cookies-from-browser', help='The browser to extract cookies from (e.g., chrome, firefox).')
@click.option('--cookies-file', type=click.Path(exists=True, dir_okay=False, resolve_path=True), help='Path to a file containing cookies.')
@click.option('--date-after', help='Download videos uploaded on or after this date (YYYYMMDD).')
@click.option('-v', '--verbose', count=True, help='Enable verbose logging. Use -vv for debug level.')
def main(**kwargs: Any):
    """
    A command-line tool to download TikTok videos and their metadata
    based on user-defined filters.
    You must provide either a TIKTOK_URL or the --from-file option.
    """
    # 1. Configure logging
    verbose = kwargs.get('verbose', 0)
    if verbose == 1:
        log_level = logging.INFO
    elif verbose >= 2:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING
    setup_logging(log_level)

    try:
        if kwargs.get('tiktok_url') or kwargs.get('from_file'):
            click.echo("Fetching metadata...")

        filtered_videos = download_videos(**kwargs)

        click.echo(f"Found {len(filtered_videos)} videos that match the criteria.")

        if kwargs.get('metadata_only'):
            _display_metadata(filtered_videos)
        else:
            if not filtered_videos:
                click.echo("No videos to download.")
                return
            click.echo(f"Downloading {len(filtered_videos)} video(s)...")
            click.echo("Download complete.")

    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
        raise click.Abort()
