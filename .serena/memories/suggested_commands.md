# Development Commands

## Testing Commands
```bash
# Run only working minimal tests
pytest tests/test_minimal_core.py -v

# Run all tests (when migrations are ready)
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=personal_finance

# Run specific test file
pytest tests/test_<component>.py -v
```

## Django Management Commands
```bash
# Create migrations for an app
python manage.py makemigrations <app_name>

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations

# Start development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser
```

## Database Commands
```bash
# Initialize database
python setup_database.py

# Run migrations programmatically (in Python)
from personal_finance.database import DatabaseManager
db = DatabaseManager()
db.run_migrations()
```

## Main Application Entry Points
```bash
# Main application
python run_finance.py

# Simple setup check
python test_simple_setup.py
```

## Linting and Formatting
```bash
# Format code with ruff
ruff format .

# Lint code with ruff
ruff check .

# Format and lint
ruff check . && ruff format .
```

## Package Management
```bash
# Install project in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```