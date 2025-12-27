"""Shared test fixtures for almanac-bot tests."""

import datetime

import pytest

from almanacbot.ephemeris import Ephemeris, Location


@pytest.fixture
def sample_ephemeris() -> Ephemeris:
    """Sample ephemeris for testing."""
    return Ephemeris(
        id=1,
        date=datetime.datetime(1899, 11, 29, 12, 0, tzinfo=datetime.timezone.utc),
        text="El ${date}, avui fa ${years_ago} anys, va passar algo.",
        location=Location(41.38, 2.17),
        last_tweeted_at=None,
    )


@pytest.fixture
def feb_29_ephemeris() -> Ephemeris:
    """Leap year ephemeris for testing."""
    return Ephemeris(
        id=2,
        date=datetime.datetime(2000, 2, 29, 12, 0, tzinfo=datetime.timezone.utc),
        text="Leap year event ${years_ago} years ago.",
        location=None,
        last_tweeted_at=None,
    )


@pytest.fixture
def today_ephemeris() -> Ephemeris:
    """Ephemeris for today's date (for testing matching)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return Ephemeris(
        id=3,
        date=datetime.datetime(
            1950, now.month, now.day, 12, 0, tzinfo=datetime.timezone.utc
        ),
        text="Today's historical event from ${years_ago} years ago.",
        location=None,
        last_tweeted_at=None,
    )


@pytest.fixture
def already_tweeted_ephemeris() -> Ephemeris:
    """Ephemeris that was already tweeted today."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return Ephemeris(
        id=4,
        date=datetime.datetime(
            1960, now.month, now.day, 12, 0, tzinfo=datetime.timezone.utc
        ),
        text="Already tweeted event.",
        location=None,
        last_tweeted_at=now,
    )
