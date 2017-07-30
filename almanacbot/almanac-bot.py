import json
import logging
import logging.config
import os
import sys

import twitter
from pymongo import MongoClient

import config
import constants

conf = None
twitter_api = None
mongo_client = None


def _setup_logging(
        path='logging.json',
        log_level=logging.DEBUG,
        env_key='LOG_CFG'
):
    env_path = os.getenv(env_key, None)
    if env_path:
        path = env_path
    if os.path.exists(path):
        with open(path, 'rt') as f:
            log_conf = json.load(f)
        logging.config.dictConfig(log_conf)
    else:
        logging.basicConfig(level=log_level)


def _setup_twitter():
    logging.info("Setting up Twitter API client...")

    global twitter_api
    twitter_api = twitter.Api(
        consumer_key=conf.config["twitter"]["consumer_key"],
        consumer_secret=conf.config["twitter"]["consumer_secret"],
        access_token_key=conf.config["twitter"]["access_token_key"],
        access_token_secret=conf.config["twitter"]["access_token_secret"])

    logging.info("Verifying Twitter API client credentials...")
    twitter_api.VerifyCredentials()
    logging.info("Twitter API client credentials verified.")

    logging.info("Twitter API client set up.")


def _setup_mongo():
    logging.info("Setting up MongoDB client...")

    global mongo_client
    mongo_client = MongoClient(conf.config["mongodb"]["uri"])

    logging.info("Verifying MongoDB client credentials...")
    db = mongo_client[conf.config["mongodb"]["database"]]
    db.authenticate(
        conf.config["mongodb"]["user"],
        conf.config["mongodb"]["password"],
        mechanism=conf.config["mongodb"]["mechanism"])
    logging.info("MongoDB client credentials verified.")

    logging.info("MongoDB client set up.")


def main():
    # configure logger
    _setup_logging()

    # read configuration
    global conf
    try:
        conf = config.Configuration(constants.CONFIG_FILE_NAME)
    except Exception as exc:
        logging.error("Error getting configuration.", exc)
        sys.exit(1)

    # setup Twitter API client
    try:
        _setup_twitter()
    except Exception as exc:
        logging.error("Error setting up Twitter API client.", exc)
        sys.exit(1)

    # setup MongoDB client
    try:
        _setup_mongo()
    except Exception as exc:
        logging.error("Error setting up MongoDB client.", exc)
        sys.exit(1)


if __name__ == '__main__':
    main()
