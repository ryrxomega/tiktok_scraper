from typing import List, Optional

from .schemas import VideoMetadata

class FilterService:
    """
    A service for applying filtering logic to a list of videos.
    This keeps the business logic of filtering separate from other concerns.
    """

    def apply_filters(
        self,
        videos: List[VideoMetadata],
        min_likes: Optional[int],
        min_views: Optional[int],
    ) -> List[VideoMetadata]:
        """
        Filters a list of videos based on specified criteria.

        The filtering is conjunctive (i.e., "AND"). A video must meet all
        specified criteria to be included in the result.

        Args:
            videos: The list of VideoMetadata objects to filter.
            min_likes: If provided, videos must have at least this many likes.
            min_views: If provided, videos must have at least this many views.

        Returns:
            A new list of VideoMetadata objects that meet all the criteria.
        """
        # Start with the full list of videos. We will progressively narrow it down.
        filtered_videos = videos

        if min_likes is not None:
            filtered_videos = [
                video for video in filtered_videos if video.like_count >= min_likes
            ]

        if min_views is not None:
            filtered_videos = [
                video for video in filtered_videos if video.view_count >= min_views
            ]

        return filtered_videos
