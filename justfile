set shell := ["bash", "-uc"]

project_name := "almanac-bot"
project_version := `uv version --short`
tag := project_name + ":" + project_version

# Show project version
version:
    @echo {{project_version}}

# Build Docker image
docker-build:
    docker image build --tag="{{tag}}" .

# Start all services (postgres, bot, scheduler)
docker-up:
    docker compose up -d

# Stop all services
docker-down:
    docker compose down

# Start services and follow logs
docker-serve: docker-up
    docker compose logs -f

# Load ephemeris data from CSV
docker-load-data:
    docker exec -it almanac-bot uv run python -m typer almanacbot.data_loader run

# Run the bot manually (will tweet if events exist for today)
docker-run:
    docker exec almanac-bot uv run python -m almanacbot.almanacbot

# Run in dry-run mode (shows what would be tweeted)
docker-dry-run:
    docker exec almanac-bot uv run python -m almanacbot.almanacbot --dry-run

# View bot logs
docker-logs:
    docker compose logs almanac-bot

# View scheduler logs (follow mode)
docker-logs-scheduler:
    docker compose logs ofelia -f

# Clean database volume
docker-clean-db:
    docker volume rm almanac-bot_postgres_data

# Run unit tests
test:
    uv run pytest tests/ -v --ignore=tests/test_integration.py

# Run tests with coverage
test-cov:
    uv run pytest tests/ --cov=almanacbot --cov-report=term-missing --ignore=tests/test_integration.py

# Run integration tests (requires running postgres)
test-integration: docker-up
    INTEGRATION_TESTS=1 uv run pytest tests/test_integration.py -v

# Run linter
lint:
    uv run ruff check almanacbot/ tests/

# Fix linting issues
lint-fix:
    uv run ruff check almanacbot/ tests/ --fix

# Show available commands
help:
    @just --list
