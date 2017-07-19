import json
import logging
import logging.config
import os
import sys

import config
import constants
import twitter

conf = None
twitter_api = None


def setup_logging(
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


def setup_twitter():
    logging.info("Setting up Twitter API client...")

    twitter_api = twitter.Api(
        consumer_key=conf.config["twitter"]["consumer_key"],
        consumer_secret=conf.config["twitter"]["consumer_secret"],
        access_token_key=conf.config["twitter"]["access_token_key"],
        access_token_secret=conf.config["twitter"]["access_token_secret"])

    logging.info("Verifying Twitter API client credentials...")
    twitter_api.VerifyCredentials()
    logging.info("Twitter API client credentials verified.")

    logging.info("Twitter API client set up.")

if __name__ == '__main__':
    # configure logger
    setup_logging()

    # read configuration
    try:
        conf = config.Configuration(constants.CONFIG_FILE_NAME)
    except Exception as exc:
        logging.error("Error getting configuration.", exc)
        sys.exit(1)

    try:
        setup_twitter()
    except Exception as exc:
        logging.error("Error setting up Twitter API client.", exc)
        sys.exit(1)
