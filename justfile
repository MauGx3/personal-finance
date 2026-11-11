# Common tasks. Run `just` to list them.
default:
    @just --list

install:
    uv sync

dev:
    uv run python manage.py migrate
    uv run python manage.py runserver

test *args:
    uv run pytest {{args}}

lint:
    uv run ruff check .
    uv run ruff format --check .

format:
    uv run ruff check --fix .
    uv run ruff format .

check: lint test
    uv run python manage.py makemigrations --check --dry-run

prices:
    uv run python manage.py sync_prices

up:
    docker compose up -d --build

down:
    docker compose down
