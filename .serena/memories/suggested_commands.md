# Development Commands and Guidelines

## Essential Commands

### Testing
```bash
# Run minimal working tests
python -m pytest tests/test_minimal_core.py -v

# Run all active tests (avoids *.disabled files)
python -m pytest tests/ -v --ignore-glob="*/*.disabled"

# Run Django tests directly
python manage.py test

# Run with coverage
python -m pytest tests/ --cov=personal_finance --cov-report=html
```

### Django Development
```bash
# Start development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations  
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

### Database Setup
```bash
# Initialize database (handles PostgreSQL or SQLite fallback)
python setup_database.py

# Run migrations programmatically
python -c "from personal_finance.database import DatabaseManager; db = DatabaseManager(); db.run_migrations()"
```

### Package Management
```bash
# Install project in development mode
pip install -e .

# Install dev dependencies
pip install -r requirements/local.txt
```

### Code Quality
```bash
# Linting with ruff
ruff check .
ruff format .

# Pre-commit hooks
pre-commit run --all-files
```

## Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with database credentials
DATABASE_URL=postgresql://user:password@localhost/personal_finance
```

## Docker Development
```bash
# Start with Docker Compose
docker-compose -f local.yml up

# Build containers
docker-compose -f local.yml build
```