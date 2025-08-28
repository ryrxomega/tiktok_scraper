from pydantic import BaseModel
from typing import Optional

class VideoMetadata(BaseModel):
    """
    A Pydantic model to represent the metadata of a TikTok video.

    This provides a clear data structure and type validation for the
    information retrieved from yt-dlp. It ensures that any data
    representing a video within the application conforms to this schema.

    The `id` and `webpage_url` are required, as they are essential for
    identifying and downloading the video. Other fields are optional to
    gracefully handle cases where yt-dlp cannot retrieve all metadata.
    """
    id: str
    webpage_url: str
    title: Optional[str] = None
    like_count: Optional[int] = None
    view_count: Optional[int] = None
