import re
from typing import Optional


def get_id(url: str) -> Optional[str]:
    """
    Extract YouTube video, channel, or playlist ID from a string.

    Args:
        url: String containing YouTube URL or direct ID

    Returns:
        Extracted ID or None if no valid ID is found

    Examples:
        >>> get_id("dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> get_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> get_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> get_id("https://www.youtube.com/playlist?list=PLv3TTBr1W_9tppikBxAE_G6qjWdBljBHJ")
        'PLv3TTBr1W_9tppikBxAE_G6qjWdBljBHJ'
        >>> get_id("https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw")
        'UC_x5XG1OV2P6uZZ5FSM9Ttw'
    """
    # Regular expressions for different YouTube ID patterns
    patterns = {
        "video": [
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # Standard video URLs
            r"^([0-9A-Za-z_-]{11})$",  # Direct video ID
        ],
        "playlist": [
            r"(?:list=)([0-9A-Za-z_-]{34})",  # Playlist URLs
            r"^([0-9A-Za-z_-]{34})$",  # Direct playlist ID
        ],
        "channel": [
            r"(?:channel/)([0-9A-Za-z_-]{24})(?:/.*)?$",  # Channel URLs with optional path
            r"^([0-9A-Za-z_-]{24})$",  # Direct channel ID
        ],
    }

    # Clean the input URL
    url = url.strip()

    # Try each pattern type
    for patterns_list in patterns.values():
        for pattern in patterns_list:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

    return None
