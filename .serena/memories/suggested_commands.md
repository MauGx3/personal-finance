# Development Commands and Tools

## Linting and Code Quality
- `python -m ruff check .` - Run ruff linting
- `python -m pylint personal_finance/` - Run pylint analysis
- `python -m ruff format .` - Format code with ruff

## Testing
- `python -m pytest` - Run all tests
- `python -m pytest tests/` - Run specific test directory

## Django Management
- `python manage.py migrate` - Run database migrations
- `python manage.py collectstatic` - Collect static files
- `python manage.py runserver` - Start development server

## Database Setup
- `python setup_database.py` - Initialize database and run migrations
- `alembic upgrade head` - Run Alembic migrations

## Dependencies
- `pip install -e .` - Install project in development mode
- `pip install -r requirements.txt` - Install all dependencies

## Key Development Files
- `pyproject.toml` - Project configuration and dependencies
- `pytest.ini` - Test configuration
- `alembic.ini` - Database migration configuration
- `.env.example` - Environment variables template