import pytest
from unittest.mock import MagicMock
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
