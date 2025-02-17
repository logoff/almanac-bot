"""Almanac Bot module"""

import json
import logging
import logging.config
import os
import sys
import time
from typing import List

from babel import Locale, UnknownLocaleError
import schedule

from almanacbot import config, constants
from almanacbot.ephemeris import Ephemeris
from almanacbot.postgresql_client import PostgreSQLClient
from almanacbot.twitter_client import TwitterClient


class AlamancBot:
    """Almanac Bot class"""

    def __init__(self):
        self.conf: config.Configuration = None
        self.twitter_client: TwitterClient = None
        self.postgresql_client: PostgreSQLClient = None

        # configure logger
        self._setup_logging()

        # read configuration
        logging.info("Initializing Almanac Bot...")
        try:
            self.conf = config.Configuration(constants.CONFIG_FILE_NAME)
        except ValueError:
            logging.exception("Error getting configuration.")
            sys.exit(1)

        # setup locale
        try:
            self.locale: Locale = Locale.parse(self.conf.config["language"]["locale"])
            logging.info(f"Locale set to: {self.locale}")
        except (ValueError, UnknownLocaleError):
            logging.exception("Error setting up locale.")
            sys.exit(1)

        # setup Twitter API client
        try:
            self._setup_twitter()
        except ValueError:
            logging.exception("Error setting up Twitter API client.")
            sys.exit(1)

        # setup PostgreSQL client
        try:
            self._setup_postgresql()
        except ValueError:
            logging.exception("Error setting up PostgreSQL client.")
            sys.exit(1)

        logging.info("Almanac Bot properly initialized.")

    def _setup_logging(
        self, path="logging.json", log_level=logging.DEBUG, env_key="LOG_CFG"
    ) -> None:
        env_path: str = os.getenv(env_key, None)
        if env_path:
            path = env_path
        if os.path.exists(path):
            with open(path, "rt", encoding="UTF-8") as f:
                log_conf = json.load(f)
            logging.config.dictConfig(log_conf)
        else:
            logging.basicConfig(level=log_level)

    def _setup_twitter(self) -> None:
        logging.info("Setting up Twitter API client...")
        self.twitter_client = TwitterClient(
            bearer_token=self.conf.config["twitter"]["bearer_token"],
            consumer_key=self.conf.config["twitter"]["consumer_key"],
            consumer_secret=self.conf.config["twitter"]["consumer_secret"],
            access_token_key=self.conf.config["twitter"]["access_token_key"],
            access_token_secret=self.conf.config["twitter"]["access_token_secret"],
            locale=self.locale,
        )
        logging.info("Twitter API client set up.")

    def _setup_postgresql(self) -> None:
        logging.info("Setting up PostgreSQL client...")
        self.postgresql_client: PostgreSQLClient = PostgreSQLClient(
            user=self.conf.config["postgresql"]["user"],
            password=self.conf.config["postgresql"]["password"],
            hostname=self.conf.config["postgresql"]["hostname"],
            database=self.conf.config["postgresql"]["database"],
            ephemeris_table=self.conf.config["postgresql"]["ephemeris_table"],
        )
        logging.info("PostgreSQL client set up.")

    def next_ephemeris(self) -> None:
        """This method obtains the next Epehemeris and publishes it arrived the moment"""
        logging.info("Getting today's ephemeris...")
        today_ephs: List[Ephemeris] = self.postgresql_client.get_today_ephemeris()
        logging.debug(f"Today's ephemeris: {today_ephs}")

        # tweet ephemeris
        logging.info("Tweeting ephemeris...")
        for today_eph in today_ephs:
            self.twitter_client.tweet_ephemeris(today_eph)


if __name__ == "__main__":
    ab: AlamancBot = AlamancBot()

    # schedule the daily job
    logging.info("Scheduling job...")
    schedule.every(1).days.do(ab.next_ephemeris)
    logging.info("Job scheduled.")

    # loop over ephemeris
    logging.info("Running all jobs...")
    schedule.run_all()
    logging.info("All jobs run.")
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            logging.warning("Waiting time has been interrupted. Exiting!")
            del ab
            sys.exit(0)
