import os
from typing import Any, Literal, Optional

from googleapiclient.discovery import build

from .models import (
    Channel,
    ChannelListResponse,
    SearchListResponse,
    SearchResult,
    Video,
    VideoListResponse,
)

ORDER_CHOICE = Literal["date", "rating", "relevance", "title", "videoCount", "viewCount"]
VIDEO_DURATION_CHOICES = Literal["short", "medium", "long", "any"]


class YtInfo:
    def __init__(self, youtube: Optional[Any] = None):
        if youtube is None:
            token = os.getenv("YOUTUBE_API_KEY")
            if token is None:
                raise ValueError("YOUTUBE_API_KEY environment variable not set")
            self.youtube = build("youtube", "v3", developerKey=token)
        else:
            self.youtube = youtube
        self.search = self.youtube.search()

    def search_videos(
        self,
        query: str,
        video_duration: VIDEO_DURATION_CHOICES = "any",
        max_results: int = 50,
        order: ORDER_CHOICE = "relevance",
        part: str = "snippet",
        before: Optional[str] = None,
        after: Optional[str] = None,
        language: Optional[str] = None,
    ) -> list[SearchResult]:
        """Search for videos with query on YouTube."""
        result: list[SearchResult] = []
        next_token: Optional[str] = None
        to_search: int = max_results
        while True:
            search_list_request = self.search.list(
                q=query,
                type="video",
                part=part,
                order=order,
                videoDuration=video_duration,
                maxResults=min(to_search, 50),
                pageToken=next_token,
                publishedBefore=before,
                publishedAfter=after,
                relevanceLanguage=language,
            )
            response = search_list_request.execute()
            response = SearchListResponse.model_validate(response)
            result.extend(response.items)
            to_search -= 50
            next_token = response.next_page_token
            if not next_token or to_search <= 0:
                break

        return result

    def search_channels(
        self,
        query: str,
        max_results: int = 50,
        order: ORDER_CHOICE = "relevance",
        part: str = "snippet",
    ) -> list[SearchResult]:
        """Search for channels with query on YouTube."""
        result: list[SearchResult] = []
        next_token = None
        to_search = max_results
        while True:
            search_list_request = self.search.list(
                q=query,
                part=part,
                order=order,
                type="channel",
                maxResults=min(to_search, 50),
                pageToken=next_token,
            )
            response = search_list_request.execute()
            response = SearchListResponse.model_validate(response)
            result.extend(response.items)
            to_search -= 50
            next_token = response.next_page_token
            if not next_token or to_search <= 0:
                break

        return result

    def get_videos_from_channel(
        self,
        channel_id: str,
        max_results: Optional[int] = None,
        order: ORDER_CHOICE = "date",
        video_duration: Literal["short", "medium", "long", "any"] = "any",
        part: str = "snippet",
    ) -> list[SearchResult]:
        """
        Get videos from a specific channel.

        Args:
            channel_id: The ID of the YouTube channel
            max_results: Maximum number of results to return
                (default: None, meaning all videos)
            order: Order of the results (default: date)
            video_duration: Duration filter for videos
                (default: "any", options: "short", "medium", "long", "any")
            part: Parts to retrieve (default: snippet)

        Returns:
            List of video items from the channel
        """
        result: list[SearchResult] = []
        next_token: Optional[str] = None
        to_search = max_results or 50

        while True:
            request = self.search.list(
                channelId=channel_id,
                part=part,
                order=order,
                type="video",
                videoDuration=video_duration,
                maxResults=min(to_search, 50),
                pageToken=next_token,
            )
            response = request.execute()
            response = SearchListResponse.model_validate(response)
            result.extend(response.items)

            next_token = response.next_page_token
            if max_results is not None:
                to_search -= 50
            if not next_token or (max_results is not None and to_search <= 0):
                break

        return result

    def get_videos_from_playlist(
        self,
        playlist_id: str,
        max_results: Optional[int] = None,
        part: str = "snippet,contentDetails,status",
    ) -> list[dict]:
        """
        Get videos from a specific playlist.

        Args:
            playlist_id: The ID of the YouTube playlist
            max_results: Maximum number of results to return
                (default: None, meaning all videos)
            part: Parts to retrieve (default: snippet,contentDetails,status)

        Returns:
            List of video items from the playlist
        """
        result: list[dict] = []
        next_token: Optional[str] = None
        to_search = max_results or 50

        while True:
            request = self.youtube.playlistItems().list(
                playlistId=playlist_id,
                part=part,
                maxResults=min(to_search, 50),
                pageToken=next_token,
            )
            response = request.execute()
            result.extend(response["items"])

            next_token = response.get("nextPageToken")
            if max_results is not None:
                to_search -= 50
            if not next_token or (max_results is not None and to_search <= 0):
                break

        return result

    def videos_info(
        self,
        video_ids: list[str],
        part: str = "snippet,contentDetails,statistics,topicDetails",
    ) -> list[Video]:
        """Get information about videos."""
        result: list[Video] = []
        videos = self.youtube.videos()
        for i in range(0, len(video_ids), 50):
            request = videos.list(
                part=part,
                id=",".join(video_ids[i : i + 50]),
            )
            response = request.execute()
            response = VideoListResponse.model_validate(response)
            result.extend(response.items)
        return result

    def channels_info(self, channel_ids: list[str], part: str = "snippet,contentDetails,statistics") -> list[Channel]:
        """Get information about channels.

        Args:
            channel_ids: List of YouTube channel IDs to get info for
            part: Comma-separated list of channel resource properties to include
                 Default includes basic details, content details and statistics

        Returns:
            List of dictionaries containing the requested channel information
        """
        result: list[Channel] = []
        channels = self.youtube.channels()
        for i in range(0, len(channel_ids), 50):
            request = channels.list(
                part=part,
                id=",".join(channel_ids[i : i + 50]),
            )
            response = request.execute()
            response = ChannelListResponse.model_validate(response)
            result.extend(response.items)
        return result
