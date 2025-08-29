"""
This module contains functions for exporting video metadata to various formats.
"""
import csv
import logging
from pathlib import Path
from typing import List

from .domains.tiktok.models import Video

logger = logging.getLogger(__name__)


def save_videos_to_csv(videos: List[Video], filepath: Path):
    """
    Saves a list of Video objects to a CSV file.

    Args:
        videos: A list of Video objects to save.
        filepath: The path to the CSV file to be created.
    """
    if not videos:
        logger.info("No videos to save.")
        return

    # Ensure the directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'webpage_url', 'title', 'like_count', 'view_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for video in videos:
                writer.writerow({
                    'id': video.id,
                    'webpage_url': video.webpage_url,
                    'title': video.title,
                    'like_count': video.like_count,
                    'view_count': video.view_count,
                })
        logger.info("Successfully saved metadata for %d videos to %s", len(videos), filepath)
    except IOError as e:
        logger.error("Error writing to CSV file %s: %s", filepath, e)
        raise
