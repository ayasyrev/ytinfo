import unittest
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
        "items": [
            {"id": f"video{i}", "snippet": {"title": f"Video {i}"}} for i in range(1, 3)
        ],
        "nextPageToken": "token123",
    }

    # Second page response
    second_response = {
        "items": [
            {"id": f"video{i}", "snippet": {"title": f"Video {i}"}} for i in range(3, 5)
        ],
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
    yt_info.search_video("test query")
    results = yt_info.get_video_search_results("test query")
    assert len(results) == 1
    assert len(results[0]) == 2
    assert results[0][0]["id"] == "video1"


def test_search_video_with_pagination(mock_youtube_paginated):
    """Test video search with pagination"""
    yt_info = YtInfo(youtube=mock_youtube_paginated)
    yt_info.search_video("test", max_results=4)
    results = yt_info.get_video_search_results("test")
    assert len(results) == 1
    assert len(results[0]) <= 4


def test_search_video_with_order():
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

    orders = ["date", "rating", "relevance", "title", "videoCount", "viewCount"]
    for order in orders:
        yt_info.search_video("test", order=order)
        mock_search.list.assert_called_with(
            q="test",
            part="snippet",
            order=order,
            maxResults=50,
            pageToken=None,
        )


def test_search_channel_basic(yt_info):
    """Test basic channel search functionality"""
    yt_info.search_channel("test channel")
    results = yt_info.get_channel_search_results("test channel")
    assert len(results) == 1
    assert len(results[0]) == 2
    assert results[0][0]["id"] == "video1"


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
    mock_search.list.assert_called_with(
        channelId="UC123",
        part="snippet",
        order="date",
        type="video",
        maxResults=50,
        pageToken=None,
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
    yt_info = YtInfo(youtube=mock_youtube)
    max_results = 1
    videos = yt_info.get_videos_from_channel("UC123", max_results=max_results)

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

    yt_info.search_video("nonexistent")
    results = yt_info.get_video_search_results("nonexistent")
    assert len(results) == 1
    assert len(results[0]) == 0


def test_error_handling():
    """Test error handling during API calls"""
    mock = MagicMock()
    mock.search().list().execute.side_effect = Exception("API Error")
    yt_info = YtInfo(youtube=mock)

    with pytest.raises(Exception) as exc_info:
        yt_info.search_video("test")
    assert str(exc_info.value) == "API Error"


def test_multiple_searches(yt_info):
    """Test multiple search queries are stored separately"""
    yt_info.search_video("query1")
    yt_info.search_video("query2")
    searches = yt_info.get_video_searches()

    assert len(searches) == 2
    assert "query1" in searches
    assert "query2" in searches


def test_get_searches_empty():
    """Test getting searches when none exist"""
    mock = MagicMock()
    yt_info = YtInfo(youtube=mock)

    assert len(yt_info.get_video_searches()) == 0
    assert len(yt_info.get_channel_searches()) == 0

    result = yt_info.get_video_search_results("nonexistent")
    assert len(result) == 0


class TestYtInfo(unittest.TestCase):
    def setUp(self):
        self.mock_youtube = MagicMock()
        self.yt_info = YtInfo(youtube=self.mock_youtube)

    def test_search_video(self):
        # Mock response data
        mock_response = {"items": [{"id": 1}, {"id": 2}], "nextPageToken": None}

        # Setup mock
        mock_search = MagicMock()
        mock_list = MagicMock()
        mock_list.execute.return_value = mock_response
        mock_search.list.return_value = mock_list
        self.mock_youtube.search.return_value = mock_search

        # Execute search
        self.yt_info.search_video("test query", max_results=2)

        # Verify search was called with correct parameters
        mock_search.list.assert_called_with(
            q="test query",
            part="snippet",
            order="relevance",
            maxResults=2,
            pageToken=None,
        )

        # Verify results were stored
        searches = self.yt_info.get_video_searches()
        self.assertIn("test query", searches)
        self.assertEqual(
            self.yt_info.get_video_search_results("test query")[0],
            [{"id": 1}, {"id": 2}],
        )


def test_get_videos_from_playlist_basic(mock_youtube):
    """Test basic playlist videos retrieval"""
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
    mock_playlist_items = MagicMock()
    mock_playlist_items.list.return_value = mock_list
    mock_youtube.playlistItems.return_value = mock_playlist_items

    # Execute test
    yt_info = YtInfo(youtube=mock_youtube)
    videos = yt_info.get_videos_from_playlist("PL123")

    # Verify API call
    mock_playlist_items.list.assert_called_with(
        playlistId="PL123",
        part="snippet",
        maxResults=50,
        pageToken=None,
    )

    # Verify response handling
    assert isinstance(videos, list)
    assert len(videos) == 2
    assert videos[0]["id"] == "video1"
    assert videos[0]["snippet"]["title"] == "Test Video 1"
    assert videos[1]["id"] == "video2"
    assert videos[1]["snippet"]["title"] == "Test Video 2"


def test_get_videos_from_playlist_with_limit(mock_youtube):
    """Test playlist videos retrieval with result limit"""
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
    mock_playlist_items = MagicMock()
    mock_playlist_items.list.return_value = mock_list
    mock_youtube.playlistItems.return_value = mock_playlist_items

    # Execute test
    yt_info = YtInfo(youtube=mock_youtube)
    max_results = 1
    videos = yt_info.get_videos_from_playlist("PL123", max_results=max_results)

    # Verify result limit
    assert len(videos) == max_results
    assert videos[0]["id"] == "video1"


def test_get_videos_from_playlist_pagination():
    """Test playlist videos retrieval with pagination"""
    # Setup mock responses for pagination
    mock_responses = [
        {
            "items": [
                {"id": f"video{i}", "snippet": {"title": f"Video {i}"}}
                for i in range(1, 3)
            ],
            "nextPageToken": "token123",
        },
        {
            "items": [
                {"id": f"video{i}", "snippet": {"title": f"Video {i}"}}
                for i in range(3, 5)
            ],
            "nextPageToken": None,
        },
    ]

    # Configure mock
    mock = MagicMock()
    mock_execute = MagicMock()
    mock_execute.side_effect = mock_responses
    mock_list = MagicMock()
    mock_list.execute = mock_execute
    mock_playlist_items = MagicMock()
    mock_playlist_items.list.return_value = mock_list
    mock.playlistItems.return_value = mock_playlist_items

    # Execute test
    yt_info = YtInfo(youtube=mock)
    videos = yt_info.get_videos_from_playlist("PL123", max_results=4)

    # Verify pagination results
    assert len(videos) == 4
    assert videos[0]["id"] == "video1"
    assert videos[-1]["id"] == "video4"

    # Verify API calls
    calls = mock_playlist_items.list.call_args_list
    assert len(calls) == 2
    assert calls[0].kwargs["pageToken"] is None
    assert calls[1].kwargs["pageToken"] == "token123"


def test_get_videos_from_playlist_empty():
    """Test handling of empty playlist"""
    # Setup mock with empty response
    mock = MagicMock()
    mock.playlistItems().list().execute.return_value = {"items": []}

    # Execute test
    yt_info = YtInfo(youtube=mock)
    videos = yt_info.get_videos_from_playlist("PL123")

    # Verify empty result handling
    assert isinstance(videos, list)
    assert len(videos) == 0


def test_get_videos_from_playlist_error():
    """Test error handling for playlist retrieval"""
    # Setup mock to raise exception
    mock = MagicMock()
    mock.playlistItems().list().execute.side_effect = Exception("API Error")

    # Execute test
    yt_info = YtInfo(youtube=mock)
    with pytest.raises(Exception) as exc_info:
        yt_info.get_videos_from_playlist("PL123")
    assert str(exc_info.value) == "API Error"
