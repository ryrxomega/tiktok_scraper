import pytest
from hypothesis import given, strategies as st

from tiktok_downloader.domains.tiktok.services import FilterService
from tiktok_downloader.domains.tiktok.models import Video

# Strategy for generating Video objects for Hypothesis tests
video_strategy = st.builds(
    Video,
    id=st.text(),
    title=st.text(),
    like_count=st.integers(min_value=0, max_value=1_000_000),
    view_count=st.integers(min_value=0, max_value=10_000_000),
    webpage_url=st.text(),
)

# Strategy for a list of videos
videos_strategy = st.lists(video_strategy, min_size=1)


@pytest.fixture
def sample_videos():
    """Provides a sample list of Video objects for testing."""
    return [
        Video(id='1', title='Video 1', like_count=100, view_count=1000, webpage_url='...'),
        Video(id='2', title='Video 2', like_count=200, view_count=2000, webpage_url='...'),
        Video(id='3', title='Video 3', like_count=300, view_count=3000, webpage_url='...'),
        Video(id='4', title='Video 4', like_count=400, view_count=4000, webpage_url='...'),
    ]

@given(videos=videos_strategy, min_likes=st.integers(min_value=0))
def test_apply_filters_by_min_likes_hypothesis(videos, min_likes):
    """
    GIVEN a list of videos and a min_likes filter
    WHEN apply_filters is called
    THEN it should return only videos with likes >= the filter value.
    """
    # ARRANGE
    service = FilterService()

    # ACT
    filtered_videos = service.apply_filters(videos=videos, min_likes=min_likes, min_views=None)

    # ASSERT
    for video in filtered_videos:
        assert video.like_count >= min_likes

    for video in videos:
        if video.like_count >= min_likes:
            assert video in filtered_videos
        else:
            assert video not in filtered_videos


def test_apply_filters_by_min_views(sample_videos):
    """
    GIVEN a list of videos and a min_views filter
    WHEN apply_filters is called
    THEN it should return only videos with views >= the filter value.
    """
    # ARRANGE
    service = FilterService()

    # ACT
    filtered_videos = service.apply_filters(videos=sample_videos, min_likes=None, min_views=3500)

    # ASSERT
    assert len(filtered_videos) == 1
    assert filtered_videos[0].id == '4'

def test_apply_filters_combined(sample_videos):
    """
    GIVEN a list of videos and both min_likes and min_views filters
    WHEN apply_filters is called
    THEN it should return only videos that satisfy both conditions.
    """
    # ARRANGE
    service = FilterService()

    # ACT
    # This should match videos 3 and 4
    filtered_videos = service.apply_filters(videos=sample_videos, min_likes=250, min_views=2500)

    # ASSERT
    assert len(filtered_videos) == 2
    assert filtered_videos[0].id == '3'
    assert filtered_videos[1].id == '4'

def test_apply_filters_no_matches(sample_videos):
    """
    GIVEN filters that match no videos
    WHEN apply_filters is called
    THEN it should return an empty list.
    """
    # ARRANGE
    service = FilterService()

    # ACT
    filtered_videos = service.apply_filters(videos=sample_videos, min_likes=500, min_views=None)

    # ASSERT
    assert len(filtered_videos) == 0

def test_apply_filters_no_filters(sample_videos):
    """
    GIVEN no filters are provided
    WHEN apply_filters is called
    THEN it should return the original, unmodified list of videos.
    """
    # ARRANGE
    service = FilterService()

    # ACT
    filtered_videos = service.apply_filters(videos=sample_videos, min_likes=None, min_views=None)

    # ASSERT
    assert len(filtered_videos) == 4
    assert filtered_videos == sample_videos
