"""Tests for PostgreSQL client."""

import datetime
from unittest.mock import MagicMock, patch

import pytest

from almanacbot.ephemeris import Ephemeris
from almanacbot.postgresql_client import PostgreSQLClient


class TestGetUntweetedTodayEphemeris:
    """Tests for month+day matching and idempotency."""

    @pytest.fixture
    def client(self):
        """Create a PostgreSQLClient with mocked engine."""
        with patch("almanacbot.postgresql_client.create_engine"):
            client = PostgreSQLClient(
                user="test",
                password="test",
                hostname="localhost",
                database="test",
                ephemeris_table="ephemeris",
                logging_echo=False,
            )
            return client

    def test_returns_ephemeris_matching_today(self, client):
        """Should return ephemeris where month+day matches today."""
        now = datetime.datetime.now(datetime.timezone.utc)
        matching_eph = Ephemeris(
            id=1,
            date=datetime.datetime(
                1950, now.month, now.day, 12, 0, tzinfo=datetime.timezone.utc
            ),
            text="Test",
            media_path=None,
            last_tweeted_at=None,
        )

        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.scalars.return_value.all.return_value = [matching_eph]

        with patch("almanacbot.postgresql_client.Session", return_value=mock_session):
            result = client.get_untweeted_today_ephemeris()

        assert len(result) == 1
        assert result[0].id == 1

    def test_returns_empty_when_no_matches(self, client):
        """Should return empty list when no ephemeris matches today."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.scalars.return_value.all.return_value = []

        with patch("almanacbot.postgresql_client.Session", return_value=mock_session):
            result = client.get_untweeted_today_ephemeris()

        assert result == []


class TestMarkAsTweeted:
    """Tests for idempotency marking."""

    @pytest.fixture
    def client(self):
        """Create a PostgreSQLClient with mocked engine."""
        with patch("almanacbot.postgresql_client.create_engine"):
            client = PostgreSQLClient(
                user="test",
                password="test",
                hostname="localhost",
                database="test",
                ephemeris_table="ephemeris",
                logging_echo=False,
            )
            return client

    def test_updates_last_tweeted_at(self, client):
        """Should set last_tweeted_at to current UTC time."""
        mock_eph = MagicMock()
        mock_eph.last_tweeted_at = None

        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.get.return_value = mock_eph

        with patch("almanacbot.postgresql_client.Session", return_value=mock_session):
            client.mark_as_tweeted(1)

        assert mock_eph.last_tweeted_at is not None
        mock_session.commit.assert_called_once()

    def test_handles_missing_ephemeris(self, client):
        """Should handle non-existent ephemeris ID gracefully."""
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.get.return_value = None

        with patch("almanacbot.postgresql_client.Session", return_value=mock_session):
            # Should not raise an exception
            client.mark_as_tweeted(999)

        mock_session.commit.assert_not_called()


class TestGetTodayEphemeris:
    """Tests for the get_today_ephemeris method."""

    @pytest.fixture
    def client(self):
        """Create a PostgreSQLClient with mocked engine."""
        with patch("almanacbot.postgresql_client.create_engine"):
            client = PostgreSQLClient(
                user="test",
                password="test",
                hostname="localhost",
                database="test",
                ephemeris_table="ephemeris",
                logging_echo=False,
            )
            return client

    def test_returns_all_today_ephemeris(self, client):
        """Should return all ephemeris for today regardless of tweet status."""
        now = datetime.datetime.now(datetime.timezone.utc)
        ephemerides = [
            Ephemeris(
                id=1,
                date=datetime.datetime(
                    1950, now.month, now.day, 12, 0, tzinfo=datetime.timezone.utc
                ),
                text="Event 1",
                media_path=None,
                last_tweeted_at=None,
            ),
            Ephemeris(
                id=2,
                date=datetime.datetime(
                    1960, now.month, now.day, 12, 0, tzinfo=datetime.timezone.utc
                ),
                text="Event 2",
                media_path=None,
                last_tweeted_at=now,  # Already tweeted
            ),
        ]

        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.scalars.return_value.all.return_value = ephemerides

        with patch("almanacbot.postgresql_client.Session", return_value=mock_session):
            result = client.get_today_ephemeris()

        assert len(result) == 2
