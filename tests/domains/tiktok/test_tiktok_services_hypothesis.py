from hypothesis import given, strategies as st
from tiktok_downloader.domains.tiktok.schemas import VideoMetadata
from tiktok_downloader.domains.tiktok.services import FilterService

# Strategy for generating VideoMetadata objects
video_metadata_strategy = st.builds(
    VideoMetadata,
    id=st.text(min_size=1, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
    title=st.text(),
    like_count=st.integers(min_value=0),
    view_count=st.integers(min_value=0),
    webpage_url=st.text(),
)

# Strategy for a list of videos
videos_strategy = st.lists(video_metadata_strategy).map(
    # Ensure uniqueness of IDs for hashing
    lambda l: list({v.id: v for v in l}.values())
)


def _check_video_in_filtered_list(video, filtered_ids, min_likes, min_views):
    """Helper function to check if a video should be in the filtered list."""
    meets_likes = min_likes is None or video.like_count >= min_likes
    meets_views = min_views is None or video.view_count >= min_views
    should_be_in = meets_likes and meets_views

    if should_be_in:
        assert video.id in filtered_ids, f"Video {video.id} should be in filtered list"
    else:
        assert video.id not in filtered_ids, f"Video {video.id} should not be in filtered list"


class TestFilterServiceWithHypothesis:
    @given(
        videos=videos_strategy,
        min_likes=st.one_of(st.none(), st.integers(min_value=0)),
        min_views=st.one_of(st.none(), st.integers(min_value=0)),
    )
    def test_apply_filters_properties(self, videos, min_likes, min_views):
        """
        Test that the FilterService's apply_filters method adheres to its properties.
        """
        # ARRANGE
        service = FilterService()

        # ACT
        filtered_videos = service.apply_filters(
            videos=videos,
            min_likes=min_likes,
            min_views=min_views,
        )

        # ASSERT
        filtered_ids = {v.id for v in filtered_videos}
        original_ids = {v.id for v in videos}

        assert filtered_ids.issubset(original_ids)

        for video in videos:
            _check_video_in_filtered_list(video, filtered_ids, min_likes, min_views)
