import os
from typing import Optional

from dotenv import load_dotenv
from googleapiclient.discovery import build


load_dotenv()
TOKEN = os.getenv("YT_DEV_KEY")


class YtInfo:
    def __init__(self, youtube: Optional[any] = None):
        if youtube is None:
            self.youtube = build("youtube", "v3", developerKey=TOKEN)
        else:
            self.youtube = youtube
        self._video_searches = []

    def search_video(
        self,
        query: str,
        max_results: int = 50,
        order: str = "relevance",
        part: str = "snippet",
    ) -> None:
        """Search for videos with query on YouTube."""
        result = []
        next_token = None
        to_search = max_results
        while True:
            search_list = self.youtube.search().list(
                q=query,
                part=part,
                order=order,
                maxResults=max(to_search, 50),
                pageToken=next_token,
            )
            response = search_list.execute()
            result.extend(response["items"])
            to_search -= 50
            next_token = response.get("nextPageToken")
            if not next_token or to_search <= 0:
                break
        self._video_searches.append(result)

    def get_video_searches(self) -> list:
        """Return the list of video searches."""
        return self._video_searches
