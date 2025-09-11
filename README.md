# ytinfo

A Python library that provides a clean interface to the YouTube Data API v3 for retrieving information about YouTube videos, channels, and playlists.

## Installation

```bash
pip install ytinfo
```

## Setup

You need a YouTube Data API v3 key. Get one from the [Google Cloud Console](https://console.cloud.google.com/).

Set your API key as an environment variable:

```bash
export YOUTUBE_API_KEY="your_api_key_here"
```

## Quick Start

```python
from ytinfo import YtInfo, get_id

# Initialize client
yt = YtInfo()

# Search for videos
videos = yt.search_videos("python tutorial", max_results=5)
for video in videos:
    print(f"{video.snippet.title} - {video.id}")

# Get video information from URL
video_id = get_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
video_info = yt.videos_info([video_id])
print(video_info[0].snippet.title)

# Get all videos from a channel
channel_videos = yt.get_videos_from_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw")
```

## Key Features

- **Video Search**: Search YouTube videos with various filters (duration, date, language, etc.)
- **Channel Information**: Get detailed channel data and all videos from channels
- **Playlist Support**: Extract videos from playlists
- **URL Parsing**: Extract YouTube IDs from any YouTube URL format
- **Type Safety**: Full Pydantic models with type hints
- **Automatic Pagination**: Handles large result sets automatically

## API Reference

### YtInfo Class

Main interface to YouTube API:

- `search_videos(query, max_results=50, order="relevance", ...)` - Search for videos
- `search_channels(query, max_results=50, ...)` - Search for channels
- `get_videos_from_channel(channel_id, max_results=50, ...)` - Get channel videos
- `get_videos_from_playlist(playlist_id, max_results=50, ...)` - Get playlist videos
- `videos_info(video_ids, part="snippet,contentDetails,statistics")` - Get video details
- `channels_info(channel_ids, part="snippet,contentDetails,statistics")` - Get channel details

### Utility Functions

- `get_id(url)` - Extract YouTube video/channel/playlist ID from URL or validate direct ID

### Models

Key data models:
- `Video` - Video information and metadata
- `Channel` - Channel information and metadata
- `SearchResult` - Search result with video/channel data

## Advanced Usage

### Search with filters

```python
# Search short videos in Spanish from last week
videos = yt.search_videos(
    "receta cocina",
    video_duration="short",
    language="es",
    after="2024-01-01T00:00:00Z",
    max_results=20
)
```

### Type hints

```python
from ytinfo import ORDER_CHOICE, VIDEO_DURATION_CHOICES

def search_with_typing(
    query: str,
    duration: VIDEO_DURATION_CHOICES = "any",
    order: ORDER_CHOICE = "relevance"
):
    return yt.search_videos(query, video_duration=duration, order=order)
```

## Requirements

- Python 3.8+
- google-api-python-client
- pydantic
- python-dotenv (for .env support)

## License

MIT License
