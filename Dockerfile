# base on Python 3.5 (Alpine)
FROM python:3.5-alpine

# setup app folders
RUN mkdir /almanac-bot
WORKDIR /almanac-bot

# Adding requirements files before installing requirements
COPY requirements.txt dev-requirements.txt ./

# Install requirements and dev requirements through pip. Those should include
# nostest, pytest or any other test framework you use
RUN pip install -r requirements.txt -r dev-requirements.txt

# Adding the whole repository to the image
COPY . ./