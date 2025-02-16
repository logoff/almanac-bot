import datetime
import logging
import string

import twitter

from almanacbot.ephemeris import Ephemeris


class TwitterClient:
    """Class serving as Twitter API client"""

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        access_token_key: str,
        access_token_secret: str,
    ):
        self._twitter_api: twitter.Api = twitter.Api(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_key=access_token_key,
            access_token_secret=access_token_secret,
        )

        logging.info("Verifying Twitter API client credentials...")
        self._twitter_api.VerifyCredentials()
        logging.info("Twitter API client credentials verified.")

    def tweet_ephemeris(self, eph: Ephemeris) -> None:
        logging.info(f"Tweeting ephemeris: {eph}")
        self._twitter_api.PostUpdate(
            status=TwitterClient._process_tweet_text(eph),
            latitude=eph.location.latitude if eph.location else None,
            longitude=eph.location.longitude if eph.location else None,
            display_coordinates=True if eph.location else False,
        )

    @staticmethod
    def _process_tweet_text(eph: Ephemeris) -> str:
        today = datetime.datetime.now(datetime.timezone.utc)

        logging.error(f"ephemeris type: {type(eph)}")
        logging.error(f"ephemeris dict: {eph.__dict__}")

        template = string.Template(eph.text)

        values = {
            "date": eph.date.strftime("%d de %B de %Y"),
            "years_ago": today.year - eph.date.year,
        }

        return template.substitute(values)
