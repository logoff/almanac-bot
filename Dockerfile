# base on Python 3.6 (Alpine)
FROM python:3.6-alpine

# setup app folders
RUN mkdir /almanac-bot
WORKDIR /almanac-bot
RUN mkdir logs/

# Adding requirements files before installing requirements
COPY requirements.txt dev-requirements.txt ./

# Install requirements and dev requirements through pip. Those should include
# nostest, pytest or any other test framework you use
RUN pip install -r requirements.txt -r dev-requirements.txt

# Adding the whole repository to the image
COPY . ./

ENTRYPOINT [ "python", "-m", "almanacbot.almanacbot" ]
