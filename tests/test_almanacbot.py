"""Tests for the AlmanacBot main module."""

import datetime
from unittest.mock import MagicMock, patch

import pytest
from babel import Locale

from almanacbot.almanacbot import AlmanacBot
from almanacbot.ephemeris import Ephemeris


class TestRun:
    """Tests for the main run() method."""

    @pytest.fixture
    def bot_with_mocks(self):
        """Create an AlmanacBot instance with mocked dependencies."""
        with patch.object(AlmanacBot, "__init__", lambda x: None):
            bot = AlmanacBot()
            bot.postgresql_client = MagicMock()
            bot.twitter_client = MagicMock()
            bot.locale = Locale.parse("ca_ES")
            yield bot

    def test_returns_zero_when_no_ephemeris(self, bot_with_mocks):
        """Should return 0 when no ephemeris for today."""
        bot_with_mocks.postgresql_client.get_untweeted_today_ephemeris.return_value = []

        result = bot_with_mocks.run()

        assert result == 0
        bot_with_mocks.twitter_client.tweet_ephemeris.assert_not_called()

    def test_tweets_all_ephemeris(self, bot_with_mocks):
        """Should tweet each ephemeris and mark as tweeted."""
        mock_eph = MagicMock(spec=Ephemeris)
        mock_eph.id = 1
        bot_with_mocks.postgresql_client.get_untweeted_today_ephemeris.return_value = [
            mock_eph
        ]

        result = bot_with_mocks.run()

        assert result == 1
        bot_with_mocks.twitter_client.tweet_ephemeris.assert_called_once_with(mock_eph)
        bot_with_mocks.postgresql_client.mark_as_tweeted.assert_called_once_with(1)

    def test_tweets_multiple_ephemeris(self, bot_with_mocks):
        """Should tweet all ephemeris entries for the day."""
        mock_eph1 = MagicMock(spec=Ephemeris)
        mock_eph1.id = 1
        mock_eph2 = MagicMock(spec=Ephemeris)
        mock_eph2.id = 2
        mock_eph3 = MagicMock(spec=Ephemeris)
        mock_eph3.id = 3

        bot_with_mocks.postgresql_client.get_untweeted_today_ephemeris.return_value = [
            mock_eph1,
            mock_eph2,
            mock_eph3,
        ]

        result = bot_with_mocks.run()

        assert result == 3
        assert bot_with_mocks.twitter_client.tweet_ephemeris.call_count == 3
        assert bot_with_mocks.postgresql_client.mark_as_tweeted.call_count == 3

    def test_dry_run_does_not_tweet(self, bot_with_mocks):
        """Dry run should log but not tweet or mark as tweeted."""
        mock_eph = Ephemeris(
            id=1,
            date=datetime.datetime(1950, 12, 23, 12, 0, tzinfo=datetime.timezone.utc),
            text="Test event ${years_ago} years ago.",
            media_path=None,
            last_tweeted_at=None,
        )
        bot_with_mocks.postgresql_client.get_untweeted_today_ephemeris.return_value = [
            mock_eph
        ]

        result = bot_with_mocks.run(dry_run=True)

        assert result == 1
        bot_with_mocks.twitter_client.tweet_ephemeris.assert_not_called()
        bot_with_mocks.postgresql_client.mark_as_tweeted.assert_not_called()

    def test_continues_on_tweet_failure(self, bot_with_mocks):
        """Should continue with next ephemeris if one fails."""
        mock_eph1 = MagicMock(spec=Ephemeris)
        mock_eph1.id = 1
        mock_eph2 = MagicMock(spec=Ephemeris)
        mock_eph2.id = 2

        bot_with_mocks.postgresql_client.get_untweeted_today_ephemeris.return_value = [
            mock_eph1,
            mock_eph2,
        ]
        bot_with_mocks.twitter_client.tweet_ephemeris.side_effect = [
            Exception("API error"),
            None,
        ]

        result = bot_with_mocks.run()

        # Only the second succeeded
        assert result == 1
        assert bot_with_mocks.postgresql_client.mark_as_tweeted.call_count == 1
        bot_with_mocks.postgresql_client.mark_as_tweeted.assert_called_once_with(2)

    def test_does_not_mark_failed_tweet(self, bot_with_mocks):
        """Should not mark as tweeted if the tweet fails."""
        mock_eph = MagicMock(spec=Ephemeris)
        mock_eph.id = 1

        bot_with_mocks.postgresql_client.get_untweeted_today_ephemeris.return_value = [
            mock_eph
        ]
        bot_with_mocks.twitter_client.tweet_ephemeris.side_effect = Exception(
            "API error"
        )

        result = bot_with_mocks.run()

        assert result == 0
        bot_with_mocks.postgresql_client.mark_as_tweeted.assert_not_called()


class TestDryRunOutput:
    """Tests for dry-run mode output."""

    @pytest.fixture
    def bot_with_mocks(self):
        """Create an AlmanacBot instance with mocked dependencies."""
        with patch.object(AlmanacBot, "__init__", lambda x: None):
            bot = AlmanacBot()
            bot.postgresql_client = MagicMock()
            bot.twitter_client = MagicMock()
            bot.locale = Locale.parse("ca_ES")
            yield bot

    def test_dry_run_processes_template(self, bot_with_mocks, caplog):
        """Dry run should process the tweet template correctly."""
        import logging

        caplog.set_level(logging.INFO)

        mock_eph = Ephemeris(
            id=1,
            date=datetime.datetime(1950, 12, 23, 12, 0, tzinfo=datetime.timezone.utc),
            text="El ${date}, fa ${years_ago} anys.",
            media_path=None,
            last_tweeted_at=None,
        )
        bot_with_mocks.postgresql_client.get_untweeted_today_ephemeris.return_value = [
            mock_eph
        ]

        bot_with_mocks.run(dry_run=True)

        # Check that dry-run logged something
        assert any("[DRY-RUN]" in record.message for record in caplog.records)


class TestIdempotency:
    """Tests for idempotency behavior."""

    @pytest.fixture
    def bot_with_mocks(self):
        """Create an AlmanacBot instance with mocked dependencies."""
        with patch.object(AlmanacBot, "__init__", lambda x: None):
            bot = AlmanacBot()
            bot.postgresql_client = MagicMock()
            bot.twitter_client = MagicMock()
            bot.locale = Locale.parse("ca_ES")
            yield bot

    def test_second_run_finds_no_ephemeris(self, bot_with_mocks):
        """Second run should find no untweeted ephemeris after first run."""
        mock_eph = MagicMock(spec=Ephemeris)
        mock_eph.id = 1

        # First run returns ephemeris
        bot_with_mocks.postgresql_client.get_untweeted_today_ephemeris.return_value = [
            mock_eph
        ]
        first_result = bot_with_mocks.run()
        assert first_result == 1

        # Second run returns empty (simulating database state after marking)
        bot_with_mocks.postgresql_client.get_untweeted_today_ephemeris.return_value = []
        second_result = bot_with_mocks.run()
        assert second_result == 0
