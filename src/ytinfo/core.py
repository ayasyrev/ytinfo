from collections import defaultdict
import os
from typing import Optional

from dotenv import load_dotenv
from googleapiclient.discovery import build
from typing import Literal


ORDER_VIDEO = Literal["date", "rating", "relevance", "title", "videoCount", "viewCount"]
ORDER_CHANNEL = Literal[
    "date", "rating", "relevance", "title", "videoCount", "viewCount"
]

load_dotenv()
TOKEN = os.getenv("YT_DEV_KEY")


class YtInfo:
    def __init__(self, youtube: Optional[any] = None):
        if youtube is None:
            self.youtube = build("youtube", "v3", developerKey=TOKEN)
        else:
            self.youtube = youtube
        self._video_searches: dict[str, list] = defaultdict(list)
        self._channel_searches: dict[str, list] = defaultdict(list)

    def search_video(
        self,
        query: str,
        max_results: int = 50,
        order: ORDER_VIDEO = "relevance",
        part: str = "snippet",
    ) -> None:
        """Search for videos with query on YouTube."""
        result: list[dict] = []
        next_token: Optional[str] = None
        to_search: int = max_results
        while True:
            search_list = self.youtube.search().list(
                q=query,
                part=part,
                order=order,
                maxResults=min(to_search, 50),
                pageToken=next_token,
            )
            response = search_list.execute()
            result.extend(response["items"])
            to_search -= 50
            next_token = response.get("nextPageToken")
            if not next_token or to_search <= 0:
                break
        self._video_searches[query].append(result)

    def get_video_searches(self) -> list:
        """Return the list of video searches."""
        return list(self._video_searches.keys())

    def get_video_search_results(self, query: str) -> list:
        """Return the search results for a given query."""
        return self._video_searches[query]

    def search_channel(
        self,
        query: str,
        max_results: int = 50,
        order: ORDER_CHANNEL = "relevance",
        part: str = "snippet",
    ) -> None:
        """Search for channels with query on YouTube."""
        result = []
        next_token = None
        to_search = max_results
        while True:
            search_list = self.youtube.search().list(
                q=query,
                part=part,
                order=order,
                type="channel",
                maxResults=min(to_search, 50),
                pageToken=next_token,
            )
            response = search_list.execute()
            result.extend(response["items"])
            to_search -= 50
            next_token = response.get("nextPageToken")
            if not next_token or to_search <= 0:
                break
        self._channel_searches[query].append(result)

    def get_channel_searches(self) -> list:
        """Return the list of channel searches."""
        return list(self._channel_searches.keys())

    def get_channel_search_results(self, query: str) -> list:
        """Return the channel search results for a given query."""
        return self._channel_searches[query]
