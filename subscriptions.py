import googleapiclient.discovery
import os

class YoutubeSubscriptionFetcher:
    def __init__(self, api_key=None):
        # Attempt to read API key from environment variable first
        self.api_key = os.environ.get("YOUTUBE_API_KEY", api_key)

        if not self.api_key:
            raise ValueError("YouTube API key not provided. Set the YOUTUBE_API_KEY environment variable or pass it as an argument.")

        self.youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=self.api_key)

    def fetch_subscriptions(self):
        """Fetches the subscriptions of the authenticated user."""
        subscriptions = []
        next_page_token = None

        while True:
            request = self.youtube.subscriptions().list(
                part="snippet",
                mine=True,
                maxResults=50,  # Adjust maxResults as needed (up to 50)
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response.get("items", []):
                subscription_info = {
                    "title": item["snippet"]["title"],
                    "channelId": item["snippet"]["resourceId"]["channelId"],
                    "thumbnails": item["snippet"]["thumbnails"]
                }
                subscriptions.append(subscription_info)

            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break
        return subscriptions

if __name__ == '__main__':

    fetcher = YoutubeSubscriptionFetcher()
    subscriptions_list = fetcher.fetch_subscriptions()

    if subscriptions_list:
        print(f"Subscriptions for channel ID {channel_id}:")
        for subscription in subscriptions_list:
            print(f"- {subscription['title']} (ID: {subscription['channelId']})")
    else:
        print("Could not fetch subscriptions.")