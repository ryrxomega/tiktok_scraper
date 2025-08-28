"""
Defines the command-line interface for the TikTok Downloader.

This module uses the `click` library to create a user-friendly CLI
and orchestrates the application's services to perform its functions.
"""
import logging
from typing import List, Optional
import click

from .domains.tiktok.models import Video
from .log import setup_logging
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
@click.option(
    '--verbose',
    '-v',
    count=True,
    help='Enable verbose logging. Use -v for INFO, -vv for DEBUG.',
)
def main(
    tiktok_url: Optional[str],
    from_file: Optional[str],
    output_path: Optional[str],
    min_likes: Optional[int],
    min_views: Optional[int],
    download_transcripts: Optional[bool],
    transcript_language: str,
    metadata_only: bool,
    verbose: int,
):
    """
    A command-line tool to download TikTok videos and their metadata
    based on user-defined filters.
    You must provide either a TIKTOK_URL or the --from-file option.
    """
    setup_logging(verbose)
    logging.debug(f"CLI arguments: {locals()}")
    try:
        if tiktok_url or from_file:
            logging.info("Fetching metadata...")

        filtered_videos = download_videos(
            tiktok_url=tiktok_url,
            from_file=from_file,
            output_path=output_path,
            min_likes=min_likes,
            min_views=min_views,
            download_transcripts=download_transcripts,
            transcript_language=transcript_language,
            metadata_only=metadata_only,
        )
        logging.info(f"Found {len(filtered_videos)} videos that match the criteria.")

        if metadata_only:
            _display_metadata(filtered_videos)
        else:
            if not filtered_videos:
                logging.info("No videos to download.")
                return
            logging.info(f"Downloading {len(filtered_videos)} video(s)...")
            logging.info("Download complete.")

    except ValueError as e:
        logging.error(f"Error: {e}")
        raise click.Abort()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise click.Abort()
