"""config module"""

import configparser
import logging


class Configuration:
    """Class containing all the configuration parameters of the program"""

    def __init__(self, config_file_path):
        self._config: dict = {}
        self._config_parser: configparser = configparser.ConfigParser()

        try:
            with open(config_file_path, "r", encoding="UTF-8") as config_file:
                self._config_parser.read_file(config_file)
        except (OSError, IOError) as e:
            err_msg = f"Error reading configuration from file {config_file_path}"
            raise ValueError(err_msg, e) from e

        try:
            logging.info("Reading configuration...")
            self.__read_language_configuration()
            self.__read_twitter_configuration()
            self.__read_postgresql_configuration()
            logging.info("Configuration read correctly.")
        except Exception as e:
            err_msg = (
                f"Error reading configuration parameters from file {config_file_path}"
            )
            raise ValueError(err_msg, e) from e

    def __read_language_configuration(self):
        logging.debug("Reading language configuration...")

        lang_conf = self._config["language"] = {}

        lang_conf["locale"] = self._config_parser.get("language", "locale")

        logging.debug("Language configuration correctly read.")

    def __read_twitter_configuration(self):
        logging.debug("Reading Twitter configuration...")

        twitter_conf = self._config["twitter"] = {}

        twitter_conf["bearer_token"] = self._config_parser.get(
            "twitter", "bearer_token"
        )
        twitter_conf["consumer_key"] = self._config_parser.get(
            "twitter", "consumer_key"
        )
        twitter_conf["consumer_secret"] = self._config_parser.get(
            "twitter", "consumer_secret"
        )
        twitter_conf["access_token_key"] = self._config_parser.get(
            "twitter", "access_token_key"
        )
        twitter_conf["access_token_secret"] = self._config_parser.get(
            "twitter", "access_token_secret"
        )

        logging.debug("Twitter configuration correctly read.")

    def __read_postgresql_configuration(self):
        logging.debug("Reading PostgreSQL configuration...")

        postgresql_conf = self._config["postgresql"] = {}

        postgresql_conf["user"] = self._config_parser.get("postgresql", "user")
        postgresql_conf["password"] = self._config_parser.get("postgresql", "password")
        postgresql_conf["hostname"] = self._config_parser.get("postgresql", "hostname")
        postgresql_conf["database"] = self._config_parser.get("postgresql", "database")
        postgresql_conf["ephemeris_table"] = self._config_parser.get(
            "postgresql", "ephemeris_table"
        )

        logging.debug("PostgreSQL configuration correctly read.")

    @property
    def config(self):
        """Returns current config"""
        return self._config
