import datetime
import logging
import os
import string

from babel import Locale
from babel.dates import format_date
import tweepy

from almanacbot.ephemeris import Ephemeris

logger = logging.getLogger(__name__)


class TwitterClient:
    """Class serving as Twitter API client"""

    def __init__(
        self,
        bearer_token: str,
        consumer_key: str,
        consumer_secret: str,
        access_token_key: str,
        access_token_secret: str,
        locale: Locale,
        media_base_path: str = "",
    ):
        self.locale = locale
        self.media_base_path = media_base_path

        # Twitter API v2 client
        self._client_v2: tweepy.Client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token_key,
            access_token_secret=access_token_secret,
        )

        # Twitter API v1.1 client (for media upload)
        auth = tweepy.OAuth1UserHandler(
            consumer_key,
            consumer_secret,
            access_token_key,
            access_token_secret,
        )
        self._api_v1: tweepy.API = tweepy.API(auth)

    def tweet_ephemeris(self, eph: Ephemeris) -> None:
        text = TwitterClient._process_tweet_text(eph, self.locale)
        media_ids: list[int] = []

        # Upload media if present (uses v1.1 API)
        if eph.media_path:
            full_path = os.path.join(self.media_base_path, eph.media_path)
            if os.path.exists(full_path):
                logger.info(f"Uploading media: {full_path}")
                media = self._api_v1.media_upload(filename=full_path)
                media_ids.append(media.media_id)
            else:
                logger.warning(f"Media file not found: {full_path}")

        # Create tweet via v2 API (media uploaded via v1.1)
        logger.info(f"Tweeting ephemeris: {eph}")
        self._client_v2.create_tweet(
            text=text,
            media_ids=media_ids if media_ids else None,
        )

    @staticmethod
    def _process_tweet_text(eph: Ephemeris, locale: Locale) -> str:
        today = datetime.datetime.now(datetime.timezone.utc)
        template = string.Template(eph.text)

        values = {
            "date": format_date(date=eph.date.date(), format="full", locale=locale),
            "years_ago": today.year - eph.date.year,
        }

        logger.debug(f"Processed ephemeris text: {template.substitute(values)}")

        return template.substitute(values)
