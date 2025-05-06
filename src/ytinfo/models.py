from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict


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
    title: str
    description: str

    published_at: str = Field(alias="publishedAt")
    thumbnails: Dict[str, Thumbnail]


class SearchSnippet(Snippet):
    channel_id: str = Field(alias="channelId")
    channel_title: str = Field(alias="channelTitle")
    live_broadcast_content: str = Field(alias="liveBroadcastContent")


class IdModel(BaseModel):
    kind: str
    video_id: Optional[str] = Field(default=None, alias="videoId")
    channel_id: Optional[str] = Field(default=None, alias="channelId")
    playlist_id: Optional[str] = Field(default=None, alias="playlistId")


class BaseResult(BaseModel):
    kind: str
    etag: str
    snippet: Any


class SearchResult(BaseResult):
    # "youtube#searchResult"
    snippet: SearchSnippet
    id: IdModel


class ListResponse(ResponseModel):
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

    page_info: PageInfo = Field(
        alias="pageInfo",
        description="Information about the current page of results.",
    )


class SearchListResponse(ListResponse):
    items: list[SearchResult]
    region_code: str = Field(
        alias="regionCode",
        default=None,
        description="The region code for the results.",
    )


class Localized(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ChannelSnippet(Snippet):
    custom_url: Optional[str] = Field(alias="customUrl", default=None)
    default_language: Optional[str] = Field(alias="defaultLanguage", default=None)
    localized: Optional[Localized] = None
    country: Optional[str] = None


class RelatedPlaylists(BaseModel):
    likes: Optional[str] = None
    favorites: Optional[str] = None
    uploads: Optional[str] = None


class ContentDetails(BaseModel):
    related_playlists: RelatedPlaylists = Field(alias="relatedPlaylists")


class Statistics(BaseModel):
    view_count: int = Field(alias="viewCount")
    subscriber_count: int = Field(alias="subscriberCount")
    hidden_subscriber_count: bool = Field(alias="hiddenSubscriberCount")
    video_count: int = Field(alias="videoCount")


class TopicDetails(BaseModel):
    topic_ids: Optional[List[str]] = Field(alias="topicIds", default=None)
    topic_categories: Optional[List[str]] = Field(alias="topicCategories", default=None)


class Status(BaseModel):
    privacy_status: str = Field(alias="privacyStatus")
    is_linked: bool = Field(alias="isLinked")
    long_uploads_status: str = Field(alias="longUploadsStatus")
    made_for_kids: bool = Field(alias="madeForKids")
    self_declared_made_for_kids: bool = Field(alias="selfDeclaredMadeForKids")


class ChannelSettings(BaseModel):
    title: str
    description: str
    keywords: Optional[str] = None
    tracking_analytics_account_id: Optional[str] = Field(
        alias="trackingAnalyticsAccountId", default=None
    )
    unsubscribed_trailer: Optional[str] = Field(
        alias="unsubscribedTrailer", default=None
    )
    default_language: Optional[str] = Field(alias="defaultLanguage", default=None)
    country: Optional[str] = None


class WatchSettings(BaseModel):
    text_color: Optional[str] = Field(alias="textColor", default=None)
    background_color: Optional[str] = Field(alias="backgroundColor", default=None)
    featured_playlist_id: Optional[str] = Field(
        alias="featuredPlaylistId", default=None
    )


class BrandingSettings(BaseModel):
    channel: ChannelSettings
    watch: Optional[WatchSettings] = None


class AuditDetails(BaseModel):
    overall_good_standing: bool = Field(alias="overallGoodStanding")
    community_guidelines_good_standing: bool = Field(
        alias="communityGuidelinesGoodStanding"
    )
    copyright_strikes_good_standing: bool = Field(alias="copyrightStrikesGoodStanding")
    content_id_claims_good_standing: bool = Field(alias="contentIdClaimsGoodStanding")


class ContentOwnerDetails(BaseModel):
    content_owner: Optional[str] = Field(alias="contentOwner", default=None)
    time_linked: Optional[str] = Field(alias="timeLinked", default=None)


class ChannelResult(BaseResult):
    # "youtube#channel"
    snippet: Optional[ChannelSnippet] = None
    content_details: Optional[ContentDetails] = Field(
        alias="contentDetails", default=None
    )
    statistics: Optional[Statistics] = None
    topic_details: Optional[TopicDetails] = Field(alias="topicDetails", default=None)
    status: Optional[Status] = None
    branding_settings: Optional[List[BrandingSettings]] = Field(
        alias="brandingSettings", default=None
    )
    audit_details: Optional[AuditDetails] = Field(alias="auditDetails", default=None)
    content_owner_details: Optional[ContentOwnerDetails] = Field(
        alias="contentOwnerDetails", default=None
    )
    localizations: Optional[Dict[str, Localized]] = None
    id: str


class ChannelListResponse(ResponseModel):
    items: list[ChannelResult]
