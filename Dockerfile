# base on Python 3.12 (Alpine)
FROM python:3.12-alpine

# upgrade pip
RUN pip install --upgrade pip

# install Poetry
RUN apk add curl gcc
RUN curl -sSL https://install.python-poetry.org | python3 - --version "1.8.5"
ENV PATH=/root/.local/bin:$PATH

# setup app folders
RUN mkdir /almanac-bot
WORKDIR /almanac-bot
RUN mkdir logs/

# copy project files and install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# Adding the whole repository to the image
COPY . ./

ENTRYPOINT [ "poetry", "run", "python", "-m", "almanacbot.almanacbot" ]
