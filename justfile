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
  docker volume rm almanac-bot_postgres_data

docker-load-db-data:
  docker container exec -it almanac-bot sh -c "poetry run python -m typer almanacbot.data_loader run"
