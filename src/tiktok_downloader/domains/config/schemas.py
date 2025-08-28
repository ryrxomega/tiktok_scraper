"""
Defines the Pydantic models for the configuration domain.
"""
from typing import Optional

from pydantic import BaseModel


class Config(BaseModel):
    """
    Represents the application's configuration settings.

    Attributes:
        output_path: The default directory to save downloaded files.
        min_likes: The default minimum likes filter.
        min_views: The default minimum views filter.
        transcripts: The default setting for downloading transcripts.
    """
    output_path: Optional[str] = None
    min_likes: Optional[int] = None
    min_views: Optional[int] = None
    transcripts: Optional[bool] = None
    transcript_language: Optional[str] = None
