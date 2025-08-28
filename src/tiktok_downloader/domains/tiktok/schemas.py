from pydantic import BaseModel

class VideoMetadata(BaseModel):
    """
    A Pydantic model to represent the metadata of a TikTok video.

    This provides a clear data structure and type validation for the
    information retrieved from yt-dlp. It ensures that any data
    representing a video within the application conforms to this schema.
    """
    id: str
    title: str
    like_count: int
    view_count: int
    webpage_url: str
