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
def yt_info(mock_youtube):
    return YtInfo(youtube=mock_youtube)


def test_init_with_custom_youtube():
    mock = MagicMock()
    yt = YtInfo(youtube=mock)
    assert yt.youtube == mock


def test_search_video(yt_info):
    yt_info.search_video("test query")
    results = yt_info.get_video_search_results("test query")
    assert len(results) == 1
    assert len(results[0]) == 2
    assert results[0][0]["id"] == "video1"


def test_search_channel(yt_info):
    yt_info.search_channel("test channel")
    results = yt_info.get_channel_search_results("test channel")
    assert len(results) == 1
    assert len(results[0]) == 2
    assert results[0][0]["id"] == "video1"


def test_get_video_searches(yt_info):
    yt_info.search_video("query1")
    yt_info.search_video("query2")
    searches = yt_info.get_video_searches()
    assert len(searches) == 2
    assert "query1" in searches
    assert "query2" in searches


def test_get_channel_searches(yt_info):
    yt_info.search_channel("channel1")
    yt_info.search_channel("channel2")
    searches = yt_info.get_channel_searches()
    assert len(searches) == 2
    assert "channel1" in searches
    assert "channel2" in searches


def test_multiple_searches(yt_info):
    yt_info.search_video("query 1")
    yt_info.search_video("query 2")
    searches = yt_info.get_video_searches()

    assert len(searches) == 2
    assert "query 1" in searches
    assert "query 2" in searches


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

    def test_get_video_searches_empty(self):
        searches = self.yt_info.get_video_searches()
        self.assertEqual(searches, [])
        result = self.yt_info.get_video_search_results("query")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
