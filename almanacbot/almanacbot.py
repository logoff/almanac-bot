"""Almanac Bot module"""

import datetime
import json
import locale
import logging
import logging.config
import os
import sys
import time

import schedule

from almanacbot import config, constants
from almanacbot.ephemeris import Epehemeris
from almanacbot.mongodb_client import MongoDBClient
from almanacbot.twitter_client import TwitterClient


class AlamancBot:
    """Almanac Bot class"""

    def __init__(self):
        self.conf: config.Configuration = None
        self.twitter_client: TwitterClient = None
        self.mongodb_client: MongoDBClient = None

        # configure logger
        self._setup_logging()

        # read configuration
        logging.info("Initializing Almanac Bot...")
        try:
            self.conf = config.Configuration(constants.CONFIG_FILE_NAME)
        except ValueError:
            logging.exception("Error getting configuration.")
            sys.exit(1)

        # setup language
        try:
            locale.setlocale(locale.LC_TIME, self.conf.config["language"]["locale"])
        except locale.Error:
            logging.exception("Error setting up language.")
            sys.exit(1)

        # setup Twitter API client
        try:
            self._setup_twitter()
        except ValueError:
            logging.exception("Error setting up Twitter API client.")
            sys.exit(1)

        # setup MongoDB client
        try:
            self._setup_mongo()
        except ValueError:
            logging.exception("Error setting up MongoDB client.")
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
            consumer_key=self.conf.config["twitter"]["consumer_key"],
            consumer_secret=self.conf.config["twitter"]["consumer_secret"],
            access_token_key=self.conf.config["twitter"]["access_token_key"],
            access_token_secret=self.conf.config["twitter"]["access_token_secret"],
        )
        logging.info("Twitter API client set up.")

    def _setup_mongo(self) -> None:
        logging.info("Setting up MongoDB client...")
        self.mongodb_client: MongoDBClient = MongoDBClient(
            mongo_uri=self.conf.config["mongodb"]["uri"],
            username=self.conf.config["mongodb"]["user"],
            password=self.conf.config["mongodb"]["password"],
            db=self.conf.config["mongodb"]["database"],
            authMechanism=self.conf.config["mongodb"]["mechanism"],
            ephemeris_collection=self.conf.config["mongodb"]["ephemeris_collection"],
        )
        logging.info("MongoDB client set up.")

    def next_ephemeris(self) -> None:
        """This method obtains the next Epehemeris and publishes it arrived the moment"""
        logging.info("Getting next ephemeris...")
        now: datetime = datetime.datetime.now(datetime.timezone.utc)
        one_day: datetime.timedelta = datetime.timedelta(days=1)

        next_eph: Epehemeris = self.mongodb_client.get_next_ephemeris(now)
        logging.debug(f"Next ephemeris: {next_eph}")

        # return if not today
        eph_pub_date = self.mongodb_client.get_next_eph_datetime(next_eph, now)
        if (eph_pub_date - now) > one_day:
            logging.debug("Ephemeris not for today, skipping until tomorrow.")
            return

        # tweet ephemeris
        logging.info("Tweeting ephemeris...")
        self.twitter_client.tweet_ephemeris(next_eph)


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
            sys.exit(0)
