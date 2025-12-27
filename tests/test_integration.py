"""Integration tests using real PostgreSQL container.

Run with: INTEGRATION_TESTS=1 pytest tests/test_integration.py -v

Requires a running PostgreSQL container:
    docker compose up -d postgres
"""

import datetime
import os

import pytest

# Skip all tests in this module unless INTEGRATION_TESTS is set
pytestmark = pytest.mark.skipif(
    os.environ.get("INTEGRATION_TESTS") != "1",
    reason="Set INTEGRATION_TESTS=1 to run integration tests",
)


@pytest.fixture(scope="module")
def db_client():
    """Create a PostgreSQL client connected to the test database."""
    from almanacbot.postgresql_client import PostgreSQLClient

    client = PostgreSQLClient(
        user=os.environ.get("POSTGRES_USER", "almanac"),
        password=os.environ.get("POSTGRES_PASSWORD", "almanac"),
        hostname=os.environ.get("POSTGRES_HOST", "localhost"),
        database=os.environ.get("POSTGRES_DB", "almanac"),
        ephemeris_table="ephemeris",
        logging_echo=False,
    )
    yield client


@pytest.fixture
def clean_db(db_client):
    """Clean the database before and after each test."""
    from sqlalchemy import text
    from sqlalchemy.orm import Session

    with Session(db_client.engine) as session:
        session.execute(text("DELETE FROM almanac.ephemeris"))
        session.commit()

    yield

    with Session(db_client.engine) as session:
        session.execute(text("DELETE FROM almanac.ephemeris"))
        session.commit()


class TestDatabaseIntegration:
    """Tests against real PostgreSQL."""

    def test_insert_and_retrieve_ephemeris(self, db_client, clean_db):
        """Should insert and retrieve ephemeris correctly."""
        from almanacbot.ephemeris import Ephemeris, Location

        now = datetime.datetime.now(datetime.timezone.utc)
        eph = Ephemeris(
            date=datetime.datetime(
                1950, now.month, now.day, 12, 0, tzinfo=datetime.timezone.utc
            ),
            text="Test event ${years_ago} years ago.",
            location=Location(41.38, 2.17),
        )

        db_client.insert_ephemeris(eph)
        result = db_client.get_today_ephemeris()

        assert len(result) == 1
        assert result[0].text == "Test event ${years_ago} years ago."

    def test_get_untweeted_excludes_already_tweeted(self, db_client, clean_db):
        """Should not return ephemeris that was already tweeted today."""
        from sqlalchemy import text
        from sqlalchemy.orm import Session

        now = datetime.datetime.now(datetime.timezone.utc)

        # Insert ephemeris directly with last_tweeted_at set to today
        with Session(db_client.engine) as session:
            session.execute(
                text(
                    """
                INSERT INTO almanac.ephemeris (date, text, last_tweeted_at)
                VALUES (:date, :text, :last_tweeted)
            """
                ),
                {
                    "date": datetime.datetime(
                        1950, now.month, now.day, 12, 0, tzinfo=datetime.timezone.utc
                    ),
                    "text": "Already tweeted event.",
                    "last_tweeted": now,
                },
            )
            session.commit()

        result = db_client.get_untweeted_today_ephemeris()
        assert len(result) == 0

    def test_get_untweeted_includes_never_tweeted(self, db_client, clean_db):
        """Should return ephemeris that was never tweeted."""
        from almanacbot.ephemeris import Ephemeris

        now = datetime.datetime.now(datetime.timezone.utc)
        eph = Ephemeris(
            date=datetime.datetime(
                1950, now.month, now.day, 12, 0, tzinfo=datetime.timezone.utc
            ),
            text="Never tweeted event.",
            location=None,
        )

        db_client.insert_ephemeris(eph)
        result = db_client.get_untweeted_today_ephemeris()

        assert len(result) == 1

    def test_mark_as_tweeted_persists(self, db_client, clean_db):
        """Should persist the last_tweeted_at timestamp."""
        from almanacbot.ephemeris import Ephemeris

        now = datetime.datetime.now(datetime.timezone.utc)
        eph = Ephemeris(
            date=datetime.datetime(
                1950, now.month, now.day, 12, 0, tzinfo=datetime.timezone.utc
            ),
            text="Test event.",
            location=None,
        )

        db_client.insert_ephemeris(eph)

        # Get the inserted ephemeris
        result = db_client.get_untweeted_today_ephemeris()
        assert len(result) == 1
        eph_id = result[0].id

        # Mark as tweeted
        db_client.mark_as_tweeted(eph_id)

        # Verify it's no longer returned as untweeted
        result_after = db_client.get_untweeted_today_ephemeris()
        assert len(result_after) == 0

        # But still returned by get_today_ephemeris
        all_today = db_client.get_today_ephemeris()
        assert len(all_today) == 1

    def test_month_day_matching_ignores_year(self, db_client, clean_db):
        """Should match ephemeris by month and day regardless of year."""
        from almanacbot.ephemeris import Ephemeris

        now = datetime.datetime.now(datetime.timezone.utc)

        # Insert ephemeris from different years but same month/day
        for year in [1900, 1950, 2000]:
            eph = Ephemeris(
                date=datetime.datetime(
                    year, now.month, now.day, 12, 0, tzinfo=datetime.timezone.utc
                ),
                text=f"Event from {year}.",
                location=None,
            )
            db_client.insert_ephemeris(eph)

        result = db_client.get_today_ephemeris()
        assert len(result) == 3

    def test_different_day_not_matched(self, db_client, clean_db):
        """Should not match ephemeris from different days."""
        from almanacbot.ephemeris import Ephemeris

        now = datetime.datetime.now(datetime.timezone.utc)

        # Insert ephemeris for yesterday
        yesterday = now - datetime.timedelta(days=1)
        eph = Ephemeris(
            date=datetime.datetime(
                1950,
                yesterday.month,
                yesterday.day,
                12,
                0,
                tzinfo=datetime.timezone.utc,
            ),
            text="Yesterday's event.",
            location=None,
        )
        db_client.insert_ephemeris(eph)

        result = db_client.get_today_ephemeris()
        assert len(result) == 0
