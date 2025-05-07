from unittest.mock import MagicMock
import pytest
from ytinfo.core import YtInfo


@pytest.fixture
def mock_youtube():
    mock = MagicMock()
    # Mock search response for videos
    mock.search().list().execute.return_value = {
        "items": [
            {"id": "video1", "snippet": {"title": "Test Video 1"}},
            {"id": "video2", "snippet": {"title": "Test Video 2"}},
        ]
    }
    return mock


@pytest.fixture
def mock_youtube_paginated():
    mock = MagicMock()

    # First page response
    first_response = {
        "items": [{"id": f"video{i}", "snippet": {"title": f"Video {i}"}} for i in range(1, 3)],
        "nextPageToken": "token123",
    }

    # Second page response
    second_response = {
        "items": [{"id": f"video{i}", "snippet": {"title": f"Video {i}"}} for i in range(3, 5)],
        "nextPageToken": None,
    }

    # Configure mock to return different responses
    mock_execute = MagicMock()
    mock_execute.side_effect = [first_response, second_response]
    mock.search().list().execute = mock_execute

    return mock


@pytest.fixture
def yt_info(mock_youtube):
    return YtInfo(youtube=mock_youtube)


def test_init_with_custom_youtube():
    mock = MagicMock()
    yt = YtInfo(youtube=mock)
    assert yt.youtube == mock


def test_search_video_basic(yt_info):
    """Test basic video search functionality"""
    results = yt_info.search_videos("test query")
    assert len(results) == 2
    assert results[0]["id"] == "video1"


def test_search_video_with_pagination(mock_youtube_paginated):
    """Test video search with pagination"""
    yt_info = YtInfo(youtube=mock_youtube_paginated)
    results = yt_info.search_videos("test", max_results=4)
    assert len(results) <= 4


@pytest.mark.parametrize("order", ["date", "rating", "relevance", "title", "videoCount", "viewCount"])
def test_search_video_with_order(order):
    """Test video search with different order parameters"""
    # Create mock objects once
    mock_response = {"items": [], "nextPageToken": None}
    mock_list = MagicMock()
    mock_list.execute.return_value = mock_response
    mock_search = MagicMock()
    mock_search.list.return_value = mock_list
    mock_youtube = MagicMock()
    mock_youtube.search.return_value = mock_search

    yt_info = YtInfo(youtube=mock_youtube)

    yt_info.search_videos("test", order=order)
    mock_search.list.assert_called_with(
        q="test",
        part="snippet",
        order=order,
        maxResults=50,
        pageToken=None,
        videoDuration="any",
        type="video",
    )


def test_search_channel_basic(yt_info):
    """Test basic channel search functionality"""
    results = yt_info.search_channels("test channel")
    assert len(results) == 2
    assert results[0]["id"] == "video1"


def test_get_videos_from_channel_basic(mock_youtube):
    """Test basic channel videos retrieval"""
    # Setup mock response
    mock_response = {
        "items": [
            {"id": "video1", "snippet": {"title": "Test Video 1"}},
            {"id": "video2", "snippet": {"title": "Test Video 2"}},
        ],
        "nextPageToken": None,
    }

    # Configure mock
    mock_list = MagicMock()
    mock_list.execute.return_value = mock_response
    mock_search = MagicMock()
    mock_search.list.return_value = mock_list
    mock_youtube.search.return_value = mock_search

    # Execute test
    yt_info = YtInfo(youtube=mock_youtube)
    videos = yt_info.get_videos_from_channel("UC123")

    # Verify API call
    mock_search.list.assert_called_once_with(
        part="snippet",
        channelId="UC123",
        order="date",
        type="video",
        maxResults=50,
        pageToken=None,
        videoDuration="any",
    )

    # Verify response handling
    assert isinstance(videos, list)
    assert len(videos) == 2
    assert videos[0]["id"] == "video1"
    assert videos[0]["snippet"]["title"] == "Test Video 1"
    assert videos[1]["id"] == "video2"
    assert videos[1]["snippet"]["title"] == "Test Video 2"


def test_get_videos_from_channel_with_limit(mock_youtube):
    """Test channel videos retrieval with result limit"""
    max_results = 1

    # Configure mock
    mock_response = {
        "items": [{"id": "video1", "snippet": {"title": "Test Video 1"}}],
        "nextPageToken": None,
    }
    mock_list = MagicMock()
    mock_list.execute.return_value = mock_response
    mock_search = MagicMock()
    mock_search.list.return_value = mock_list
    mock_youtube.search.return_value = mock_search

    # Execute test
    yt_info = YtInfo(youtube=mock_youtube)
    videos = yt_info.get_videos_from_channel("UC123", max_results=max_results)

    # Verify API call
    mock_search.list.assert_called_once_with(
        part="snippet",
        channelId="UC123",
        order="date",
        type="video",
        maxResults=max_results,
        pageToken=None,
        videoDuration="any",
    )

    # Verify response handling
    assert len(videos) == max_results


def test_get_videos_from_channel_pagination(mock_youtube_paginated):
    """Test channel videos retrieval with pagination"""
    yt_info = YtInfo(youtube=mock_youtube_paginated)
    videos = yt_info.get_videos_from_channel("UC123")

    assert len(videos) == 4  # Total videos from both pages
    assert videos[0]["id"] == "video1"
    assert videos[-1]["id"] == "video4"


def test_empty_search_results():
    """Test handling of empty search results"""
    mock = MagicMock()
    mock.search().list().execute.return_value = {"items": []}
    yt_info = YtInfo(youtube=mock)

    results = yt_info.search_videos("nonexistent")
    assert len(results) == 0


def test_error_handling():
    """Test error handling during API calls"""
    mock = MagicMock()
    mock.search().list().execute.side_effect = Exception("API Error")
    yt_info = YtInfo(youtube=mock)

    with pytest.raises(Exception) as exc_info:
        yt_info.search_videos("test")
    assert str(exc_info.value) == "API Error"
