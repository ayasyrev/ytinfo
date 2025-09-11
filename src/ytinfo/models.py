from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict, model_validator
from typing import Any, List, Optional, Dict

from warnings import warn


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )

    @model_validator(mode="after")
    def check_extra(self) -> "BaseModel":
        if self.model_extra:
            warn_message = f"Extra fields found in {self.__class__.__name__}: {self.model_extra}"
            warn(warn_message, UserWarning, 2)
        return self


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
    publish_time: Optional[str] = Field(alias="publishTime", default=None)


class ChannelSnippet(Snippet):
    custom_url: Optional[str] = Field(alias="customUrl", default=None)
    default_language: Optional[str] = Field(alias="defaultLanguage", default=None)
    localized: Optional["Localized"] = None
    country: Optional[str] = None


class VideoSnippet(Snippet):
    channel_id: str = Field(alias="channelId")
    channel_title: str = Field(alias="channelTitle")
    tags: Optional[List[str]] = None
    category_id: Optional[str] = Field(alias="categoryId", default=None)
    live_broadcast_content: str = Field(alias="liveBroadcastContent")
    default_language: Optional[str] = Field(alias="defaultLanguage", default=None)
    default_audio_language: Optional[str] = Field(alias="defaultAudioLanguage", default=None)
    localized: Optional["Localized"] = None


class SearchId(BaseModel):
    kind: str
    video_id: Optional[str] = Field(default=None, alias="videoId")
    channel_id: Optional[str] = Field(default=None, alias="channelId")
    playlist_id: Optional[str] = Field(default=None, alias="playlistId")

    @model_validator(mode="after")
    def check_ids(self) -> "SearchId":
        if not self.video_id and not self.playlist_id and not self.channel_id:
            raise ValueError("At least one of video_id, playlist_id, or channel_id is required")
        return self


class BaseResult(BaseModel):
    kind: str
    etag: str
    snippet: Any


class SearchResult(BaseResult):
    # "youtube#searchResult"
    snippet: SearchSnippet
    id: SearchId

    def get_id(self) -> str:
        return self.id.video_id or self.id.playlist_id or self.id.channel_id or ""


class ListResponse(ResponseModel):
    # kind: str = Literal["youtube#searchListResponse"]
    items: list[Any]
    prev_page_token: Optional[str] = Field(
        alias="prevPageToken",
        default=None,
        description="Token for the previous page of results.",
    )
    next_page_token: Optional[str] = Field(
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
    region_code: Optional[str] = Field(
        alias="regionCode",
        default=None,
        description="The region code for the results.",
    )


class Localized(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


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
    tracking_analytics_account_id: Optional[str] = Field(alias="trackingAnalyticsAccountId", default=None)
    unsubscribed_trailer: Optional[str] = Field(alias="unsubscribedTrailer", default=None)
    default_language: Optional[str] = Field(alias="defaultLanguage", default=None)
    country: Optional[str] = None


class WatchSettings(BaseModel):
    text_color: Optional[str] = Field(alias="textColor", default=None)
    background_color: Optional[str] = Field(alias="backgroundColor", default=None)
    featured_playlist_id: Optional[str] = Field(alias="featuredPlaylistId", default=None)


class BrandingSettings(BaseModel):
    channel: ChannelSettings
    watch: Optional[WatchSettings] = None


class AuditDetails(BaseModel):
    overall_good_standing: bool = Field(alias="overallGoodStanding")
    community_guidelines_good_standing: bool = Field(alias="communityGuidelinesGoodStanding")
    copyright_strikes_good_standing: bool = Field(alias="copyrightStrikesGoodStanding")
    content_id_claims_good_standing: bool = Field(alias="contentIdClaimsGoodStanding")


class ContentOwnerDetails(BaseModel):
    content_owner: Optional[str] = Field(alias="contentOwner", default=None)
    time_linked: Optional[str] = Field(alias="timeLinked", default=None)


class Channel(BaseResult):
    # "youtube#channel"
    snippet: Optional[ChannelSnippet] = None
    content_details: Optional[ContentDetails] = Field(alias="contentDetails", default=None)
    statistics: Optional[Statistics] = None
    topic_details: Optional[TopicDetails] = Field(alias="topicDetails", default=None)
    status: Optional[Status] = None
    branding_settings: Optional[List[BrandingSettings]] = Field(alias="brandingSettings", default=None)
    audit_details: Optional[AuditDetails] = Field(alias="auditDetails", default=None)
    content_owner_details: Optional[ContentOwnerDetails] = Field(alias="contentOwnerDetails", default=None)
    localizations: Optional[Dict[str, Localized]] = None
    id: str


class ChannelListResponse(ListResponse):
    items: list[Channel]


class ContentDetailsVideo(BaseModel):
    duration: Optional[str] = None
    dimension: Optional[str] = None
    definition: Optional[str] = None
    caption: Optional[str] = None
    licensed_content: Optional[bool] = Field(default=None, alias="licensedContent")
    region_restriction: Optional[Dict[str, Any]] = Field(default=None, alias="regionRestriction")
    content_rating: Optional[Dict[str, Any]] = Field(default=None, alias="contentRating")
    projection: Optional[str] = None
    has_custom_thumbnail: Optional[bool] = Field(default=None, alias="hasCustomThumbnail")


class StatusVideo(BaseModel):
    upload_status: Optional[str] = Field(default=None, alias="uploadStatus")
    failure_reason: Optional[str] = Field(default=None, alias="failureReason")
    rejection_reason: Optional[str] = Field(default=None, alias="rejectionReason")
    privacy_status: Optional[str] = Field(default=None, alias="privacyStatus")
    publish_at: Optional[str] = Field(default=None, alias="publishAt")
    license: Optional[str] = None
    embeddable: Optional[bool] = None
    public_stats_viewable: Optional[bool] = Field(default=None, alias="publicStatsViewable")
    made_for_kids: Optional[bool] = Field(default=None, alias="madeForKids")
    self_declared_made_for_kids: Optional[bool] = Field(default=None, alias="selfDeclaredMadeForKids")
    contains_synthetic_media: Optional[bool] = Field(default=None, alias="containsSyntheticMedia")


class StatisticsVideo(BaseModel):
    view_count: Optional[str] = Field(default=None, alias="viewCount")
    like_count: Optional[str] = Field(default=None, alias="likeCount")
    dislike_count: Optional[str] = Field(default=None, alias="dislikeCount")
    favorite_count: Optional[str] = Field(default=None, alias="favoriteCount")
    comment_count: Optional[str] = Field(default=None, alias="commentCount")


class PaidProductPlacementDetails(BaseModel):
    has_paid_product_placement: Optional[bool] = Field(default=None, alias="hasPaidProductPlacement")


class Player(BaseModel):
    embed_html: Optional[str] = Field(default=None, alias="embedHtml")
    embed_height: Optional[str] = Field(default=None, alias="embedHeight")
    embed_width: Optional[str] = Field(default=None, alias="embedWidth")


class TopicDetailsVideo(BaseModel):
    topic_ids: Optional[List[str]] = Field(default=None, alias="topicIds")
    relevant_topic_ids: Optional[List[str]] = Field(default=None, alias="relevantTopicIds")
    topic_categories: Optional[List[str]] = Field(default=None, alias="topicCategories")


class RecordingDetails(BaseModel):
    recording_date: Optional[str] = Field(default=None, alias="recordingDate")


class VideoStream(BaseModel):
    width_pixels: Optional[int] = Field(default=None, alias="widthPixels")
    height_pixels: Optional[int] = Field(default=None, alias="heightPixels")
    frame_rate_fps: Optional[float] = Field(default=None, alias="frameRateFps")
    aspect_ratio: Optional[float] = Field(default=None, alias="aspectRatio")
    codec: Optional[str] = None
    bitrate_bps: Optional[int] = Field(default=None, alias="bitrateBps")
    rotation: Optional[str] = None
    vendor: Optional[str] = None


class AudioStream(BaseModel):
    channel_count: Optional[int] = Field(default=None, alias="channelCount")
    codec: Optional[str] = None
    bitrate_bps: Optional[int] = Field(default=None, alias="bitrateBps")
    vendor: Optional[str] = None


class FileDetails(BaseModel):
    file_name: Optional[str] = Field(default=None, alias="fileName")
    file_size: Optional[int] = Field(default=None, alias="fileSize")
    file_type: Optional[str] = Field(default=None, alias="fileType")
    container: Optional[str] = None
    video_streams: Optional[List[VideoStream]] = Field(default=None, alias="videoStreams")
    audio_streams: Optional[List[AudioStream]] = Field(default=None, alias="audioStreams")
    duration_ms: Optional[int] = Field(default=None, alias="durationMs")
    bitrate_bps: Optional[int] = Field(default=None, alias="bitrateBps")
    creation_time: Optional[str] = Field(default=None, alias="creationTime")


class ProcessingProgress(BaseModel):
    parts_total: Optional[int] = Field(default=None, alias="partsTotal")
    parts_processed: Optional[int] = Field(default=None, alias="partsProcessed")
    time_left_ms: Optional[int] = Field(default=None, alias="timeLeftMs")


class ProcessingDetails(BaseModel):
    processing_status: Optional[str] = Field(default=None, alias="processingStatus")
    processing_progress: Optional[ProcessingProgress] = Field(default=None, alias="processingProgress")
    processing_failure_reason: Optional[str] = Field(default=None, alias="processingFailureReason")
    file_details_availability: Optional[str] = Field(default=None, alias="fileDetailsAvailability")
    processing_issues_availability: Optional[str] = Field(default=None, alias="processingIssuesAvailability")
    tag_suggestions_availability: Optional[str] = Field(default=None, alias="tagSuggestionsAvailability")
    editor_suggestions_availability: Optional[str] = Field(default=None, alias="editorSuggestionsAvailability")
    thumbnails_availability: Optional[str] = Field(default=None, alias="thumbnailsAvailability")


class TagSuggestion(BaseModel):
    tag: Optional[str] = None
    category_restricts: Optional[List[str]] = Field(default=None, alias="categoryRestricts")


class Suggestions(BaseModel):
    processing_errors: Optional[List[str]] = Field(default=None, alias="processingErrors")
    processing_warnings: Optional[List[str]] = Field(default=None, alias="processingWarnings")
    processing_hints: Optional[List[str]] = Field(default=None, alias="processingHints")
    tag_suggestions: Optional[List[TagSuggestion]] = Field(default=None, alias="tagSuggestions")
    editor_suggestions: Optional[List[str]] = Field(default=None, alias="editorSuggestions")


class LiveStreamingDetails(BaseModel):
    actual_start_time: Optional[str] = Field(default=None, alias="actualStartTime")
    actual_end_time: Optional[str] = Field(default=None, alias="actualEndTime")
    scheduled_start_time: Optional[str] = Field(default=None, alias="scheduledStartTime")
    scheduled_end_time: Optional[str] = Field(default=None, alias="scheduledEndTime")
    concurrent_viewers: Optional[int] = Field(default=None, alias="concurrentViewers")
    active_live_chat_id: Optional[str] = Field(default=None, alias="activeLiveChatId")


class LocalizationsVideo(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class Video(BaseResult):
    # "youtube#video"
    id: str
    snippet: Optional[VideoSnippet] = None
    content_details: Optional[ContentDetailsVideo] = Field(default=None, alias="contentDetails")
    status: Optional[StatusVideo] = Field(default=None, alias="status")
    statistics: Optional[StatisticsVideo] = Field(default=None, alias="statistics")
    player: Optional[Player] = Field(default=None, alias="player")
    topic_details: Optional[TopicDetailsVideo] = Field(default=None, alias="topicDetails")
    recording_details: Optional[RecordingDetails] = Field(default=None, alias="recordingDetails")
    file_details: Optional[FileDetails] = Field(default=None, alias="fileDetails")
    processing_details: Optional[ProcessingDetails] = Field(default=None, alias="processingDetails")
    suggestions: Optional[Suggestions] = Field(default=None, alias="suggestions")
    live_streaming_details: Optional[LiveStreamingDetails] = Field(default=None, alias="liveStreamingDetails")
    localizations: Optional[Dict[str, LocalizationsVideo]] = Field(default=None, alias="localizations")


class VideoListResponse(ListResponse):
    # "kind": "youtube#videoListResponse"
    items: list[Video]


class PlaylistItemSnippet(BaseModel):
    published_at: str = Field(alias="publishedAt")
    channel_id: str = Field(alias="channelId")
    title: str
    description: str
    thumbnails: Dict[str, Thumbnail]
    channel_title: str = Field(alias="channelTitle")
    video_owner_channel_title: Optional[str] = Field(alias="videoOwnerChannelTitle", default=None)
    video_owner_channel_id: Optional[str] = Field(alias="videoOwnerChannelId", default=None)
    playlist_id: str = Field(alias="playlistId")
    position: int
    resource_id: "PlaylistItemResourceId" = Field(alias="resourceId")


class PlaylistItemResourceId(BaseModel):
    kind: str
    video_id: str = Field(alias="videoId")


class PlaylistItemContentDetails(BaseModel):
    video_id: str = Field(alias="videoId")
    start_at: Optional[str] = Field(alias="startAt", default=None)
    end_at: Optional[str] = Field(alias="endAt", default=None)
    note: Optional[str] = None
    video_published_at: Optional[str] = Field(alias="videoPublishedAt", default=None)


class PlaylistItemStatus(BaseModel):
    privacy_status: str = Field(alias="privacyStatus")


class PlaylistItem(BaseResult):
    # "youtube#playlistItem"
    id: str
    snippet: Optional[PlaylistItemSnippet] = None
    content_details: Optional[PlaylistItemContentDetails] = Field(alias="contentDetails", default=None)
    status: Optional[PlaylistItemStatus] = None


class PlaylistItemListResponse(ListResponse):
    # "kind": "youtube#playlistItemListResponse"
    items: list[PlaylistItem]
