set shell := ["bash", "-uc"]

project_name := "almanac-bot"
project_version := `poetry version --short`
tag := project_name + ":" + project_version

version:
  @echo {{project_version}}

docker-build:
	docker image build --tag="{{tag}}" .

docker-serve-site: docker-build
  docker compose up --build && \
  docker compose down

docker-clean-db:
  docker volume rm almanac-bot_mongo_data
