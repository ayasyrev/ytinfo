import unittest
from unittest.mock import MagicMock

import pytest

from ytinfo.core import YtInfo


@pytest.fixture
def mock_youtube():
    mock = MagicMock()
    mock.search().list().execute.return_value = {
        "items": [{"id": 1}, {"id": 2}],
        "nextPageToken": None,
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
    searches = yt_info.get_video_searches()

    assert len(searches) == 1
    assert len(searches[0]) == 2
    yt_info.youtube.search().list.assert_called_once_with(
        q="test query",
        part="snippet",
        order="relevance",
        maxResults=50,
        pageToken=None,
    )


def test_multiple_searches(yt_info):
    yt_info.search_video("query 1")
    yt_info.search_video("query 2")
    searches = yt_info.get_video_searches()

    assert len(searches) == 2


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
        self.assertEqual(searches["test query"][0], [{"id": 1}, {"id": 2}])

    def test_get_video_searches_empty(self):
        searches = self.yt_info.get_video_searches()
        self.assertEqual(searches, {})


if __name__ == "__main__":
    unittest.main()
