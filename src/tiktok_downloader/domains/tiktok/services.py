"""
Provides services for the TikTok domain, encapsulating business logic.
"""
from datetime import date
from typing import List, Optional

from .models import Video


class FilterService:
    """
    A service for applying filtering logic to a list of videos.

    This keeps the business logic of filtering separate from other concerns,
    operating on core domain models.
    """

    def apply_filters(
        self,
        videos: List[Video],
        min_likes: Optional[int],
        min_views: Optional[int],
        process_after_date: Optional[date] = None,
    ) -> List[Video]:
        """
        Filters a list of videos based on specified criteria.

        The filtering is conjunctive (i.e., "AND"). A video must meet all
        specified criteria to be included in the result. If a video is missing
        a piece of metadata (e.g., `like_count` is None), it will be excluded
        by any filter that acts on that metadata.

        Args:
            videos: The list of Video objects to filter.
            min_likes: If provided, videos must have at least this many likes.
            min_views: If provided, videos must have at least this many views.
            process_after_date: If provided, videos must have been uploaded on or after this date.

        Returns:
            A new list of Video objects that meet all the criteria.
        """
        # Start with the full list of videos. We will progressively narrow it down.
        filtered_videos = videos

        if min_likes is not None:
            filtered_videos = [
                video for video in filtered_videos
                if video.like_count is not None and video.like_count >= min_likes
            ]

        if min_views is not None:
            filtered_videos = [
                video for video in filtered_videos
                if video.view_count is not None and video.view_count >= min_views
            ]

        if process_after_date is not None:
            filtered_videos = [
                video for video in filtered_videos
                if video.upload_date is not None and video.upload_date >= process_after_date
            ]

        return filtered_videos
