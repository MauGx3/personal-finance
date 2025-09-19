# Suggested Commands for Development

## Setup and Installation
```bash
# Install dependencies
pip install -e .
pip install -r requirements.txt

# Setup database
python setup_database.py
```

## Development Server
```bash
# Local development (Django)
python manage.py runserver
python manage.py runserver 127.0.0.1:8000  # Secure localhost binding

# Run with Uvicorn (FastAPI-style)
uvicorn personal_finance.web_gui:app --reload --host 127.0.0.1 --port 8000
```

## Testing
```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m financial

# Run with verbose output
pytest -v
```

## Linting and Formatting
```bash
# Run Ruff linter
ruff check .

# Run Ruff formatter
ruff format .

# Run pre-commit hooks manually
pre-commit run --all-files
```

## Docker Development
```bash
# Using just (recommended)
just build    # Build containers
just up       # Start containers
just down     # Stop containers
just logs     # View logs

# Direct docker-compose
docker-compose -f docker-compose.local.yml up
```

## Database Management
```bash
# Django migrations
python manage.py makemigrations
python manage.py migrate

# Alembic migrations (alternative)
alembic upgrade head
alembic revision --autogenerate -m "description"
```

## Production Commands
```bash
# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn --bind 127.0.0.1:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker config.asgi:application
```