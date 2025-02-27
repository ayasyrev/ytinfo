import pytest
from ytinfo.tools import get_id


@pytest.mark.parametrize(
    "input_url,expected_id",
    [
        # Video URLs
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),  # Direct video ID
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),  # Standard URL
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),  # Short URL
        (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123",
            "dQw4w9WgXcQ",
        ),  # With timestamp
        # Playlist URLs
        (
            "PLv3TTBr1W_9tppikBxAE_G6qjWdBljBHJ",
            "PLv3TTBr1W_9tppikBxAE_G6qjWdBljBHJ",
        ),  # Direct playlist ID
        (
            "https://www.youtube.com/playlist?list=PLv3TTBr1W_9tppikBxAE_G6qjWdBljBHJ",
            "PLv3TTBr1W_9tppikBxAE_G6qjWdBljBHJ",
        ),  # Playlist URL
        # Channel URLs
        (
            "UC_x5XG1OV2P6uZZ5FSM9Ttw",
            "UC_x5XG1OV2P6uZZ5FSM9Ttw",
        ),  # Direct channel ID
        (
            "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw",
            "UC_x5XG1OV2P6uZZ5FSM9Ttw",
        ),  # Channel URL
        (
            "https://www.youtube.com/playlist?list=PLcfpQ4tk2k0VetQVGT1EqTbcr-qcgbfFs",
            "PLcfpQ4tk2k0VetQVGT1EqTbcr-qcgbfFs",
        ),  # Playlist URL
    ],
)
def test_get_id_valid_inputs(input_url: str, expected_id: str) -> None:
    """Test get_id function with valid inputs."""
    assert get_id(input_url) == expected_id


@pytest.mark.parametrize(
    "invalid_input",
    [
        "",  # Empty string
        "   ",  # Whitespace
        "not_a_youtube_url",  # Random text
        "https://example.com",  # Non-YouTube URL
        "https://youtube.com",  # YouTube URL without ID
        "abc",  # Too short ID
        "a" * 50,  # Too long ID
    ],
)
def test_get_id_invalid_inputs(invalid_input: str) -> None:
    """Test get_id function with invalid inputs."""
    assert get_id(invalid_input) is None
