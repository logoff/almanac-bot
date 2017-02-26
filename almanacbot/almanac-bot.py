import json
import logging
import logging.config
import os
import sys

import config
import constants


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


if __name__ == '__main__':
    # configure logger
    setup_logging()

    # read configuration
    try:
        configuration = config.Configuration(constants.CONFIG_FILE_NAME)
    except Exception as exc:
        logging.error("Error getting configuration.", exc)
        sys.exit(1)
