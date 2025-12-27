"""Tests for the TwitterClient module."""

import datetime
from unittest.mock import MagicMock, patch

import pytest
from babel import Locale

from almanacbot.ephemeris import Ephemeris
from almanacbot.twitter_client import TwitterClient


@pytest.fixture
def mock_tweepy():
    """Mock tweepy Client and API."""
    with patch("almanacbot.twitter_client.tweepy") as mock:
        mock_client = MagicMock()
        mock_api = MagicMock()
        mock.Client.return_value = mock_client
        mock.API.return_value = mock_api
        mock.OAuth1UserHandler.return_value = MagicMock()
        yield {
            "module": mock,
            "client_v2": mock_client,
            "api_v1": mock_api,
        }


@pytest.fixture
def twitter_client(mock_tweepy):
    """Create a TwitterClient with mocked tweepy."""
    return TwitterClient(
        bearer_token="test_bearer",
        consumer_key="test_consumer_key",
        consumer_secret="test_consumer_secret",
        access_token_key="test_access_token",
        access_token_secret="test_access_secret",
        locale=Locale.parse("ca_ES"),
        media_base_path="/tmp/media",
    )


class TestTweetEphemeris:
    """Tests for tweet_ephemeris method."""

    def test_simple_tweet_uses_v2(self, twitter_client, mock_tweepy):
        """Simple tweet without media should use v2 API."""
        eph = Ephemeris(
            id=1,
            date=datetime.datetime(1950, 12, 23, 12, 0, tzinfo=datetime.timezone.utc),
            text="Test tweet",
            media_path=None,
            last_tweeted_at=None,
        )

        twitter_client.tweet_ephemeris(eph)

        mock_tweepy["client_v2"].create_tweet.assert_called_once()
        mock_tweepy["api_v1"].update_status.assert_not_called()

    def test_tweet_with_media_uploads_v1_tweets_v2(
        self, twitter_client, mock_tweepy, tmp_path
    ):
        """Tweet with media should upload via v1.1 and create tweet via v2."""
        # Create a test image file
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake image data")

        # Update client to use tmp_path as media base
        twitter_client.media_base_path = str(tmp_path)

        # Mock media upload response
        mock_media = MagicMock()
        mock_media.media_id = 123456789
        mock_tweepy["api_v1"].media_upload.return_value = mock_media

        eph = Ephemeris(
            id=1,
            date=datetime.datetime(1950, 12, 23, 12, 0, tzinfo=datetime.timezone.utc),
            text="Test tweet",
            media_path="test.jpg",
            last_tweeted_at=None,
        )

        twitter_client.tweet_ephemeris(eph)

        # Media uploaded via v1.1
        mock_tweepy["api_v1"].media_upload.assert_called_once_with(
            filename=str(test_image)
        )
        # Tweet created via v2 with media_ids
        mock_tweepy["client_v2"].create_tweet.assert_called_once()
        call_kwargs = mock_tweepy["client_v2"].create_tweet.call_args[1]
        assert call_kwargs["media_ids"] == [123456789]
        mock_tweepy["api_v1"].update_status.assert_not_called()

    def test_missing_media_file_logs_warning(self, twitter_client, mock_tweepy, caplog):
        """Missing media file should log warning and tweet without media."""
        import logging

        caplog.set_level(logging.WARNING)

        eph = Ephemeris(
            id=1,
            date=datetime.datetime(1950, 12, 23, 12, 0, tzinfo=datetime.timezone.utc),
            text="Test tweet",
            media_path="nonexistent.jpg",
            last_tweeted_at=None,
        )

        twitter_client.tweet_ephemeris(eph)

        # Should warn about missing file
        assert any("not found" in record.message for record in caplog.records)
        # Should still tweet (via v2 since no media uploaded)
        mock_tweepy["client_v2"].create_tweet.assert_called_once()
        mock_tweepy["api_v1"].media_upload.assert_not_called()


class TestProcessTweetText:
    """Tests for _process_tweet_text static method."""

    def test_processes_date_template(self):
        """Should replace ${date} with localized date."""
        eph = Ephemeris(
            id=1,
            date=datetime.datetime(1950, 12, 23, 12, 0, tzinfo=datetime.timezone.utc),
            text="El ${date} va passar.",
            media_path=None,
            last_tweeted_at=None,
        )
        locale = Locale.parse("ca_ES")

        result = TwitterClient._process_tweet_text(eph, locale)

        assert "dissabte" in result.lower() or "desembre" in result.lower()
        assert "${date}" not in result

    def test_processes_years_ago_template(self):
        """Should replace ${years_ago} with calculated years."""
        current_year = datetime.datetime.now().year
        eph = Ephemeris(
            id=1,
            date=datetime.datetime(1950, 12, 23, 12, 0, tzinfo=datetime.timezone.utc),
            text="Fa ${years_ago} anys.",
            media_path=None,
            last_tweeted_at=None,
        )
        locale = Locale.parse("ca_ES")

        result = TwitterClient._process_tweet_text(eph, locale)

        expected_years = current_year - 1950
        assert str(expected_years) in result
        assert "${years_ago}" not in result
