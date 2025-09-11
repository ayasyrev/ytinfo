"""
ytinfo - A Python library for YouTube Data API v3

Provides a clean interface to retrieve information about YouTube videos, channels, and playlists.
"""

from .core import YtInfo, ORDER_CHOICE, VIDEO_DURATION_CHOICES
from .models import (
    Video,
    Channel,
    SearchResult,
    VideoListResponse,
    ChannelListResponse,
    SearchListResponse,
)
from .tools import get_id

__version__ = "0.1.3"
__all__ = [
    # Main class
    "YtInfo",
    # Core models
    "Video",
    "Channel",
    "SearchResult",
    # Response models
    "VideoListResponse",
    "ChannelListResponse",
    "SearchListResponse",
    # Utility functions
    "get_id",
    # Type hints
    "ORDER_CHOICE",
    "VIDEO_DURATION_CHOICES",
]
