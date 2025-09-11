from unittest.mock import MagicMock
import pytest
from ytinfo.core import YtInfo


@pytest.fixture
def mock_youtube():
    mock = MagicMock()
    # Mock search response for videos
    mock.search().list().execute.return_value = {
        "kind": "youtube#searchListResponse",
        "etag": "test_etag",
        "items": [
            {
                "kind": "youtube#searchResult",
                "etag": "item1_etag",
                "id": {"kind": "youtube#video", "videoId": "video1"},
                "snippet": {
                    "title": "Test Video 1",
                    "description": "Test description 1",
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "channelId": "UC123",
                    "channelTitle": "Test Channel",
                    "liveBroadcastContent": "none",
                    "thumbnails": {},
                },
            },
            {
                "kind": "youtube#searchResult",
                "etag": "item2_etag",
                "id": {"kind": "youtube#video", "videoId": "video2"},
                "snippet": {
                    "title": "Test Video 2",
                    "description": "Test description 2",
                    "publishedAt": "2023-01-02T00:00:00Z",
                    "channelId": "UC456",
                    "channelTitle": "Test Channel 2",
                    "liveBroadcastContent": "none",
                    "thumbnails": {},
                },
            },
        ],
        "pageInfo": {"totalResults": 2, "resultsPerPage": 2},
    }
    return mock


@pytest.fixture
def mock_youtube_paginated():
    mock = MagicMock()

    # First page response
    first_response = {
        "kind": "youtube#searchListResponse",
        "etag": "page1_etag",
        "items": [
            {
                "kind": "youtube#searchResult",
                "etag": f"item{i}_etag",
                "id": {"kind": "youtube#video", "videoId": f"video{i}"},
                "snippet": {
                    "title": f"Video {i}",
                    "description": f"Description {i}",
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "channelId": "UC123",
                    "channelTitle": "Test Channel",
                    "liveBroadcastContent": "none",
                    "thumbnails": {},
                },
            }
            for i in range(1, 3)
        ],
        "nextPageToken": "token123",
        "pageInfo": {"totalResults": 4, "resultsPerPage": 2},
    }

    # Second page response
    second_response = {
        "kind": "youtube#searchListResponse",
        "etag": "page2_etag",
        "items": [
            {
                "kind": "youtube#searchResult",
                "etag": f"item{i}_etag",
                "id": {"kind": "youtube#video", "videoId": f"video{i}"},
                "snippet": {
                    "title": f"Video {i}",
                    "description": f"Description {i}",
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "channelId": "UC123",
                    "channelTitle": "Test Channel",
                    "liveBroadcastContent": "none",
                    "thumbnails": {},
                },
            }
            for i in range(3, 5)
        ],
        "nextPageToken": None,
        "pageInfo": {"totalResults": 4, "resultsPerPage": 2},
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
    assert results[0].get_id() == "video1"


def test_search_video_with_pagination(mock_youtube_paginated):
    """Test video search with pagination"""
    yt_info = YtInfo(youtube=mock_youtube_paginated)
    results = yt_info.search_videos("test", max_results=4)
    assert len(results) <= 4


@pytest.mark.parametrize("order", ["date", "rating", "relevance", "title", "videoCount", "viewCount"])
def test_search_video_with_order(order):
    """Test video search with different order parameters"""
    # Create mock objects once
    mock_response = {
        "kind": "youtube#searchListResponse",
        "etag": "test_etag",
        "items": [],
        "pageInfo": {"totalResults": 0, "resultsPerPage": 0},
    }
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
        publishedBefore=None,
        publishedAfter=None,
        relevanceLanguage=None,
    )


def test_search_channel_basic(yt_info):
    """Test basic channel search functionality"""
    results = yt_info.search_channels("test channel")
    assert len(results) == 2
    assert results[0].get_id() == "video1"


def test_get_videos_from_channel_basic(mock_youtube):
    """Test basic channel videos retrieval"""
    # Setup mock response
    mock_response = {
        "kind": "youtube#searchListResponse",
        "etag": "test_etag",
        "items": [
            {
                "kind": "youtube#searchResult",
                "etag": "item1_etag",
                "id": {"kind": "youtube#video", "videoId": "video1"},
                "snippet": {
                    "title": "Test Video 1",
                    "description": "Test description 1",
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "channelId": "UC123",
                    "channelTitle": "Test Channel",
                    "liveBroadcastContent": "none",
                    "thumbnails": {},
                },
            },
            {
                "kind": "youtube#searchResult",
                "etag": "item2_etag",
                "id": {"kind": "youtube#video", "videoId": "video2"},
                "snippet": {
                    "title": "Test Video 2",
                    "description": "Test description 2",
                    "publishedAt": "2023-01-02T00:00:00Z",
                    "channelId": "UC123",
                    "channelTitle": "Test Channel",
                    "liveBroadcastContent": "none",
                    "thumbnails": {},
                },
            },
        ],
        "nextPageToken": None,
        "pageInfo": {"totalResults": 2, "resultsPerPage": 2},
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
    assert videos[0].get_id() == "video1"
    assert videos[0].snippet.title == "Test Video 1"
    assert videos[1].get_id() == "video2"
    assert videos[1].snippet.title == "Test Video 2"


def test_get_videos_from_channel_with_limit(mock_youtube):
    """Test channel videos retrieval with result limit"""
    max_results = 1

    # Configure mock
    mock_response = {
        "kind": "youtube#searchListResponse",
        "etag": "test_etag",
        "items": [
            {
                "kind": "youtube#searchResult",
                "etag": "item1_etag",
                "id": {"kind": "youtube#video", "videoId": "video1"},
                "snippet": {
                    "title": "Test Video 1",
                    "description": "Test description 1",
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "channelId": "UC123",
                    "channelTitle": "Test Channel",
                    "liveBroadcastContent": "none",
                    "thumbnails": {},
                },
            }
        ],
        "nextPageToken": None,
        "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
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
    assert videos[0].get_id() == "video1"
    assert videos[-1].get_id() == "video4"


def test_empty_search_results():
    """Test handling of empty search results"""
    mock = MagicMock()
    mock.search().list().execute.return_value = {
        "kind": "youtube#searchListResponse",
        "etag": "test_etag",
        "items": [],
        "pageInfo": {"totalResults": 0, "resultsPerPage": 0},
    }
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


def test_get_videos_from_playlist_basic(mock_youtube):
    """Test basic playlist videos retrieval"""
    # Setup mock response for playlist items
    mock_playlist_response = {
        "kind": "youtube#playlistItemListResponse",
        "etag": "test_etag",
        "items": [
            {
                "kind": "youtube#playlistItem",
                "etag": "item1_etag",
                "id": "PLitem1",
                "snippet": {
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "channelId": "UC123",
                    "title": "Test Video 1",
                    "description": "Test description 1",
                    "thumbnails": {},
                    "channelTitle": "Test Channel",
                    "playlistId": "PLtest123",
                    "position": 0,
                    "resourceId": {"kind": "youtube#video", "videoId": "video1"},
                },
                "contentDetails": {"videoId": "video1", "videoPublishedAt": "2023-01-01T00:00:00Z"},
                "status": {"privacyStatus": "public"},
            },
            {
                "kind": "youtube#playlistItem",
                "etag": "item2_etag",
                "id": "PLitem2",
                "snippet": {
                    "publishedAt": "2023-01-02T00:00:00Z",
                    "channelId": "UC123",
                    "title": "Test Video 2",
                    "description": "Test description 2",
                    "thumbnails": {},
                    "channelTitle": "Test Channel",
                    "playlistId": "PLtest123",
                    "position": 1,
                    "resourceId": {"kind": "youtube#video", "videoId": "video2"},
                },
                "contentDetails": {"videoId": "video2", "videoPublishedAt": "2023-01-02T00:00:00Z"},
                "status": {"privacyStatus": "public"},
            },
        ],
        "nextPageToken": None,
        "pageInfo": {"totalResults": 2, "resultsPerPage": 2},
    }

    # Configure mock
    mock_list = MagicMock()
    mock_list.execute.return_value = mock_playlist_response
    mock_playlist_items = MagicMock()
    mock_playlist_items.list.return_value = mock_list
    mock_youtube.playlistItems.return_value = mock_playlist_items

    # Execute test
    yt_info = YtInfo(youtube=mock_youtube)
    playlist_items = yt_info.get_videos_from_playlist("PLtest123")

    # Verify API call
    mock_playlist_items.list.assert_called_once_with(
        playlistId="PLtest123",
        part="snippet,contentDetails,status",
        maxResults=50,
        pageToken=None,
    )

    # Verify response handling
    assert isinstance(playlist_items, list)
    assert len(playlist_items) == 2

    # Verify the items are PlaylistItem instances, not raw dicts
    from ytinfo.models import PlaylistItem

    assert isinstance(playlist_items[0], PlaylistItem)
    assert isinstance(playlist_items[1], PlaylistItem)

    # Verify content
    assert playlist_items[0].id == "PLitem1"
    assert playlist_items[0].snippet is not None
    assert playlist_items[0].snippet.title == "Test Video 1"
    assert playlist_items[0].snippet.resource_id.video_id == "video1"
    assert playlist_items[0].content_details is not None
    assert playlist_items[0].content_details.video_id == "video1"
    assert playlist_items[0].status is not None
    assert playlist_items[0].status.privacy_status == "public"

    assert playlist_items[1].id == "PLitem2"
    assert playlist_items[1].snippet is not None
    assert playlist_items[1].snippet.title == "Test Video 2"
    assert playlist_items[1].snippet.resource_id.video_id == "video2"


def test_get_videos_from_playlist_with_limit(mock_youtube):
    """Test playlist videos retrieval with result limit"""
    max_results = 1

    # Setup mock response
    mock_playlist_response = {
        "kind": "youtube#playlistItemListResponse",
        "etag": "test_etag",
        "items": [
            {
                "kind": "youtube#playlistItem",
                "etag": "item1_etag",
                "id": "PLitem1",
                "snippet": {
                    "publishedAt": "2023-01-01T00:00:00Z",
                    "channelId": "UC123",
                    "title": "Test Video 1",
                    "description": "Test description 1",
                    "thumbnails": {},
                    "channelTitle": "Test Channel",
                    "playlistId": "PLtest123",
                    "position": 0,
                    "resourceId": {"kind": "youtube#video", "videoId": "video1"},
                },
                "contentDetails": {"videoId": "video1"},
                "status": {"privacyStatus": "public"},
            }
        ],
        "nextPageToken": None,
        "pageInfo": {"totalResults": 1, "resultsPerPage": 1},
    }

    # Configure mock
    mock_list = MagicMock()
    mock_list.execute.return_value = mock_playlist_response
    mock_playlist_items = MagicMock()
    mock_playlist_items.list.return_value = mock_list
    mock_youtube.playlistItems.return_value = mock_playlist_items

    # Execute test
    yt_info = YtInfo(youtube=mock_youtube)
    playlist_items = yt_info.get_videos_from_playlist("PLtest123", max_results=max_results)

    # Verify API call
    mock_playlist_items.list.assert_called_once_with(
        playlistId="PLtest123",
        part="snippet,contentDetails,status",
        maxResults=max_results,
        pageToken=None,
    )

    # Verify response handling
    assert len(playlist_items) == max_results
    from ytinfo.models import PlaylistItem

    assert isinstance(playlist_items[0], PlaylistItem)
