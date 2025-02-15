Almanac Bot
===========

[![PyPi package](https://img.shields.io/pypi/v/almanac-bot.svg)](https://pypi.python.org/pypi/almanac-bot)

Almanac bot for Twitter.

## Dependencies
* [Docker](https://www.docker.com/)
* [Python 3.12+](https://www.python.org/)
* [MongoDB 8+](https://www.mongodb.com/)
* [just](https://just.systems/)

## How to run it locally
1. Create a valid config file
```sh
cp config.ini.default config.ini
```

And fill the fields with valid values.

2. Launch it with Docker Compose
```sh
just docker-serve-site
```

Stop it with `Ctrl+C`.
