# Alpine base image
FROM alpine:3.21

# install uv https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# setup app folders
RUN mkdir /almanac-bot
WORKDIR /almanac-bot
RUN mkdir logs/

# copy project files and install dependencies
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --python 3.13

# Adding the whole repository to the image
COPY . ./

ENTRYPOINT [ "uv", "run", "python", "-m", "almanacbot.almanacbot" ]
