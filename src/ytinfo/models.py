from pydantic import BaseModel, Field
from typing import Optional, Dict


class ResponseModel(BaseModel):
    kind: str
    etag: str
    items: list


class PageInfo(BaseModel):
    total_results: int = Field(
        alias="totalResults",
        description="The total number of results in the result set.",
    )
    results_per_page: int = Field(
        alias="resultsPerPage",
        description="The number of results included in this response.",
    )


class Thumbnail(BaseModel):
    url: str
    width: Optional[int] = None
    height: Optional[int] = None


class Snippet(BaseModel):
    published_at: str = Field(alias="publishedAt")
    channel_id: str = Field(alias="channelId")
    title: str
    description: str
    thumbnails: Dict[str, Thumbnail]
    channel_title: str = Field(alias="channelTitle")
    live_broadcast_content: str = Field(alias="liveBroadcastContent")


class IdModel(BaseModel):
    kind: str
    video_id: Optional[str] = Field(default=None, alias="videoId")
    channel_id: Optional[str] = Field(default=None, alias="channelId")
    playlist_id: Optional[str] = Field(default=None, alias="playlistId")


class SearchResult(BaseModel):
    # "youtube#searchResult"
    kind: str
    etag: str
    id: IdModel
    snippet: Snippet


class SearchListResponse(ResponseModel):
    # kind: str = Literal["youtube#searchListResponse"]
    # etag: str
    items: list[SearchResult]
    prev_page_token: Optional[str] = Field(
        alias="prevPageToken",
        default=None,
        description="Token for the previous page of results.",
    )
    next_page_token: str = Field(
        alias="nextPageToken",
        default=None,
        description="Token for the next page of results.",
    )
    region_code: str = Field(
        alias="regionCode",
        default=None,
        description="The region code for the results.",
    )
    page_info: PageInfo = Field(
        alias="pageInfo",
        description="Information about the current page of results.",
    )
