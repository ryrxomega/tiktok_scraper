"""
Defines the core domain models for the TikTok domain.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Video:
    """
    Represents the core domain model for a TikTok video.

    Using a dataclass here makes the model a plain Python object, decoupling
    our core business logic from external schemas (like Pydantic).
    The `frozen=True` argument makes instances of this class immutable,
    which is a good practice for domain entities to prevent side effects.

    Attributes:
        id: The unique identifier of the video.
        webpage_url: The direct URL to the video.
        title: The title of the video.
        like_count: The number of likes the video has received.
        view_count: The number of views the video has received.
    """
    id: str
    webpage_url: str
    title: Optional[str] = None
    like_count: Optional[int] = None
    view_count: Optional[int] = None
