"""
The root package for the TikTok Downloader application.

This package contains the core logic, domain models, and command-line
interface for the application.
"""
from .main import download_videos

__all__ = ["download_videos"]
