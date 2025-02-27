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
    # Clean the input URL
    url = url.strip()

    # ID length validation patterns
    id_patterns = {
        "video": r"^[0-9A-Za-z_-]{11}$",
        "playlist": r"^[0-9A-Za-z_-]{34}$",
        "channel": r"^UC[0-9A-Za-z_-]{22}$",
    }

    # First check if the input is a direct ID
    for pattern in id_patterns.values():
        if re.match(pattern, url):
            return url

    # URL extraction patterns
    url_patterns = {
        "video": r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:[\?&]|$)",
        "playlist": r"list=([0-9A-Za-z_-]{34})(?:[\?&]|$)",
        "channel": r"channel\/(UC[0-9A-Za-z_-]{22})(?:[\?&\/]|$)",
    }

    # Try each URL pattern type
    for pattern in url_patterns.values():
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None
