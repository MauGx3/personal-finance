Development Guide
================

Comprehensive guide for setting up the development environment and contributing to the Personal Finance application.

.. contents:: Table of Contents
   :local:
   :depth: 3

.. toctree::
   :maxdepth: 2

   Local Setup <development/local_setup>
   Testing <development/testing>
   Code Style <development/code_style>
   Database <development/database>
   API Development <development/api>

Development Environment Setup
-----------------------------

Quick Start
~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yourusername/personal-finance.git
   cd personal-finance

   # Create virtual environment with uv (recommended)
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # or .venv\\Scripts\\activate  # Windows

   # Install dependencies
   uv pip install -r requirements-dev.txt

   # Copy environment template
   cp .env.example .env

   # Setup database
   python manage.py migrate
   python manage.py loaddata fixtures/sample_data.json

   # Create superuser
   python manage.py createsuperuser

   # Run development server
   python manage.py runserver

System Requirements
~~~~~~~~~~~~~~~~~~~

**Required Software:**

+------------------+------------------+------------------------------------------+
| Software         | Version          | Installation                             |
+==================+==================+==========================================+
| Python           | 3.11+            | https://python.org                       |
+------------------+------------------+------------------------------------------+
| PostgreSQL       | 13+              | https://postgresql.org                   |
+------------------+------------------+------------------------------------------+
| Redis            | 6+               | https://redis.io                         |
+------------------+------------------+------------------------------------------+
| uv               | latest           | ``curl -LsSf https://astral.sh/uv/install.sh | sh`` |
+------------------+------------------+------------------------------------------+
| Git              | 2.30+            | https://git-scm.com                      |
+------------------+------------------+------------------------------------------+

**Optional Tools:**

- **pre-commit**: Code quality automation
- **Docker**: Containerized development environment
- **VS Code**: Recommended IDE with Python extensions
- **PostgreSQL GUI**: pgAdmin, DBeaver, or similar

Virtual Environment Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Using uv (Recommended):**

.. code-block:: bash

   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment
   uv venv

   # Activate virtual environment
   source .venv/bin/activate  # Linux/macOS
   .venv\\Scripts\\activate   # Windows

   # Install development dependencies
   uv pip install -r requirements-dev.txt

   # Verify installation
   uv pip list

**Using Traditional venv:**

.. code-block:: bash

   # Create virtual environment
   python3.11 -m venv venv

   # Activate virtual environment
   source venv/bin/activate  # Linux/macOS
   venv\\Scripts\\activate   # Windows

   # Upgrade pip
   pip install --upgrade pip

   # Install dependencies
   pip install -r requirements-dev.txt

Database Setup
--------------

PostgreSQL Local Development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install PostgreSQL (Ubuntu/Debian)
   sudo apt update
   sudo apt install postgresql postgresql-contrib

   # Install PostgreSQL (macOS with Homebrew)
   brew install postgresql
   brew services start postgresql

   # Create development database
   sudo -u postgres createdb personal_finance_dev

   # Create database user
   sudo -u postgres createuser --interactive dev_user
   # Choose options: superuser=no, create databases=yes, create roles=no

   # Set password for user
   sudo -u postgres psql
   \\password dev_user
   # Enter password when prompted
   \\q

Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env file for development
   DJANGO_SETTINGS_MODULE=config.settings.local
   DJANGO_DEBUG=True
   DJANGO_SECRET_KEY=dev-secret-key-not-for-production

   # Database
   DATABASE_URL=postgresql://dev_user:password@localhost:5432/personal_finance_dev

   # Redis (optional for development)
   REDIS_URL=redis://localhost:6379/0

   # API Keys (optional for development)
   ALPHA_VANTAGE_API_KEY=your-dev-api-key
   YAHOO_FINANCE_API_KEY=your-dev-api-key

   # Email (optional for development)
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

Run Initial Migrations
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Apply database migrations
   python manage.py migrate

   # Load sample data (optional)
   python manage.py loaddata fixtures/sample_data.json

   # Create superuser for admin access
   python manage.py createsuperuser

   # Collect static files (if needed)
   python manage.py collectstatic --noinput

Docker Development Environment
------------------------------

Using Docker Compose
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start development environment
   docker-compose -f docker-compose.local.yml up -d

   # View logs
   docker-compose -f docker-compose.local.yml logs -f

   # Run commands in container
   docker-compose -f docker-compose.local.yml exec web python manage.py migrate

   # Stop environment
   docker-compose -f docker-compose.local.yml down

**docker-compose.local.yml:**

.. code-block:: yaml

   version: '3.8'

   services:
     web:
       build:
         context: .
         dockerfile: Dockerfile.dev
       ports:
         - \"8000:8000\"
       volumes:
         - .:/app
         - /app/.venv  # Exclude virtual environment
       environment:
         - DJANGO_SETTINGS_MODULE=config.settings.local
         - DATABASE_URL=postgresql://postgres:password@postgres:5432/personal_finance
         - REDIS_URL=redis://redis:6379/0
       depends_on:
         - postgres
         - redis
       command: python manage.py runserver 0.0.0.0:8000

     postgres:
       image: postgres:15
       environment:
         POSTGRES_DB: personal_finance
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: password
       volumes:
         - postgres_dev_data:/var/lib/postgresql/data
       ports:
         - \"5432:5432\"

     redis:
       image: redis:7-alpine
       ports:
         - \"6379:6379\"
       volumes:
         - redis_dev_data:/data

   volumes:
     postgres_dev_data:
     redis_dev_data:

Development Dockerfile
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   # Dockerfile.dev
   FROM python:3.11-slim

   ENV PYTHONDONTWRITEBYTECODE=1
   ENV PYTHONUNBUFFERED=1
   ENV DJANGO_SETTINGS_MODULE=config.settings.local

   # Install system dependencies
   RUN apt-get update && apt-get install -y \\
       build-essential \\
       libpq-dev \\
       curl \\
       && rm -rf /var/lib/apt/lists/*

   WORKDIR /app

   # Install uv
   RUN pip install uv

   # Copy requirements
   COPY requirements-dev.txt .

   # Install Python dependencies
   RUN uv pip install --system -r requirements-dev.txt

   # Copy application code
   COPY . .

   EXPOSE 8000

   CMD [\"python\", \"manage.py\", \"runserver\", \"0.0.0.0:8000\"]

IDE Configuration
-----------------

VS Code Setup
~~~~~~~~~~~~~

**Recommended Extensions:**

.. code-block:: json

   // .vscode/extensions.json
   {
     \"recommendations\": [
       \"ms-python.python\",
       \"ms-python.black-formatter\",
       \"ms-python.isort\",
       \"charliermarsh.ruff\",
       \"ms-python.pylint\",
       \"ms-toolsai.jupyter\",
       \"bradlc.vscode-tailwindcss\",
       \"ms-vscode.vscode-json\",
       \"redhat.vscode-yaml\",
       \"ms-vscode-remote.remote-containers\"
     ]
   }

**Workspace Settings:**

.. code-block:: json

   // .vscode/settings.json
   {
     \"python.defaultInterpreterPath\": \"./.venv/bin/python\",
     \"python.linting.enabled\": true,
     \"python.linting.ruffEnabled\": true,
     \"python.linting.pylintEnabled\": true,
     \"python.formatting.provider\": \"black\",
     \"python.sortImports.args\": [\"--profile\", \"black\"],
     \"editor.formatOnSave\": true,
     \"editor.codeActionsOnSave\": {
       \"source.organizeImports\": true
     },
     \"files.exclude\": {
       \"**/__pycache__\": true,
       \"**/.pytest_cache\": true,
       \"**/node_modules\": true
     }
   }

**Launch Configuration:**

.. code-block:: json

   // .vscode/launch.json
   {
     \"version\": \"0.2.0\",
     \"configurations\": [
       {
         \"name\": \"Django: Debug\",
         \"type\": \"python\",
         \"request\": \"launch\",
         \"program\": \"${workspaceFolder}/manage.py\",
         \"args\": [\"runserver\", \"--noreload\"],
         \"django\": true,
         \"justMyCode\": false,
         \"envFile\": \"${workspaceFolder}/.env\"
       },
       {
         \"name\": \"Django: Test\",
         \"type\": \"python\",
         \"request\": \"launch\",
         \"module\": \"pytest\",
         \"args\": [\"-v\", \"--tb=short\"],
         \"console\": \"integratedTerminal\",
         \"envFile\": \"${workspaceFolder}/.env\"
       }
     ]
   }

PyCharm Setup
~~~~~~~~~~~~~

1. **Project Interpreter**: Set to ``.venv/bin/python``
2. **Django Configuration**:
   - Django project root: project root directory
   - Settings: ``config.settings.local``
   - Manage script: ``manage.py``
3. **Database**: Configure PostgreSQL connection
4. **Code Style**: Set to Black with line length 88
5. **Run Configurations**: Create Django server and test configurations

Code Quality Setup
------------------

Pre-commit Hooks
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install pre-commit
   pip install pre-commit

   # Install hooks
   pre-commit install

   # Run hooks manually
   pre-commit run --all-files

**.pre-commit-config.yaml:**

.. code-block:: yaml

   repos:
   - repo: https://github.com/pre-commit/pre-commit-hooks
     rev: v4.4.0
     hooks:
     - id: trailing-whitespace
     - id: end-of-file-fixer
     - id: check-yaml
     - id: check-added-large-files
     - id: check-merge-conflict

   - repo: https://github.com/psf/black
     rev: 23.3.0
     hooks:
     - id: black
       language_version: python3.11

   - repo: https://github.com/pycqa/isort
     rev: 5.12.0
     hooks:
     - id: isort
       args: [--profile, black]

   - repo: https://github.com/astral-sh/ruff-pre-commit
     rev: v0.0.270
     hooks:
     - id: ruff
       args: [--fix, --exit-non-zero-on-fix]

   - repo: https://github.com/pycqa/flake8
     rev: 6.0.0
     hooks:
     - id: flake8
       additional_dependencies: [flake8-docstrings]

   - repo: https://github.com/pre-commit/mirrors-mypy
     rev: v1.3.0
     hooks:
     - id: mypy
       additional_dependencies: [types-requests]

Code Formatting Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**pyproject.toml:**

.. code-block:: toml

   [tool.black]
   line-length = 88
   target-version = ['py311']
   include = '\\.pyi?$'
   extend-exclude = '''
   /(
     migrations/
   )/
   '''

   [tool.isort]
   profile = \"black\"
   multi_line_output = 3
   line_length = 88
   known_django = \"django\"
   known_first_party = \"personal_finance\"
   sections = [\"FUTURE\", \"STDLIB\", \"THIRDPARTY\", \"DJANGO\", \"FIRSTPARTY\", \"LOCALFOLDER\"]

   [tool.ruff]
   target-version = \"py311\"
   line-length = 88
   select = [
     \"E\",  # pycodestyle errors
     \"W\",  # pycodestyle warnings
     \"F\",  # pyflakes
     \"I\",  # isort
     \"B\",  # flake8-bugbear
     \"C4\", # flake8-comprehensions
     \"UP\", # pyupgrade
   ]
   ignore = [
     \"E501\",  # line too long, handled by black
     \"B008\",  # do not perform function calls in argument defaults
     \"C901\",  # too complex
   ]
   exclude = [
     \"migrations\",
     \"__pycache__\",
     \"manage.py\",
     \"settings\",
     \"env\",
     \".env\",
     \"venv\",
     \".venv\",
   ]

   [tool.mypy]
   python_version = \"3.11\"
   check_untyped_defs = true
   ignore_missing_imports = true
   warn_unused_ignores = true
   warn_redundant_casts = true
   warn_unused_configs = true

Testing Framework
-----------------

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   python manage.py test

   # Run with pytest (recommended)
   pytest

   # Run specific test module
   pytest tests/test_portfolio.py

   # Run with coverage
   pytest --cov=personal_finance --cov-report=html

   # Run specific test case
   pytest tests/test_portfolio.py::TestPortfolioModel::test_portfolio_creation

   # Run tests in parallel
   pytest -n auto

Test Configuration
~~~~~~~~~~~~~~~~~~

**pytest.ini:**

.. code-block:: ini

   [tool:pytest]
   DJANGO_SETTINGS_MODULE = config.settings.test
   python_files = tests.py test_*.py *_tests.py
   python_classes = Test*
   python_functions = test_*
   addopts =
       --tb=short
       --strict-markers
       --strict-config
       --cov=personal_finance
       --cov-branch
       --cov-report=term-missing:skip-covered
       --cov-report=html:htmlcov
       --cov-fail-under=80
   markers =
       slow: marks tests as slow (deselect with '-m \"not slow\"')
       integration: marks tests as integration tests
       unit: marks tests as unit tests

**conftest.py:**

.. code-block:: python

   # conftest.py
   import pytest
   from django.contrib.auth import get_user_model
   from django.test import Client
   from rest_framework.test import APIClient
   from decimal import Decimal

   from personal_finance.portfolio.models import Portfolio, Asset, Position
   from personal_finance.accounts.models import User

   User = get_user_model()

   @pytest.fixture
   def user():
       \"\"\"Create a test user.\"\"\"
       return User.objects.create_user(
           email='test@example.com',
           password='testpass123',
           first_name='Test',
           last_name='User'
       )

   @pytest.fixture
   def admin_user():
       \"\"\"Create an admin user.\"\"\"
       return User.objects.create_superuser(
           email='admin@example.com',
           password='adminpass123',
           first_name='Admin',
           last_name='User'
       )

   @pytest.fixture
   def client():
       \"\"\"Django test client.\"\"\"
       return Client()

   @pytest.fixture
   def api_client():
       \"\"\"DRF API test client.\"\"\"
       return APIClient()

   @pytest.fixture
   def authenticated_client(client, user):
       \"\"\"Authenticated Django client.\"\"\"
       client.force_login(user)
       return client

   @pytest.fixture
   def authenticated_api_client(api_client, user):
       \"\"\"Authenticated API client.\"\"\"
       api_client.force_authenticate(user=user)
       return api_client

   @pytest.fixture
   def asset():
       \"\"\"Create a test asset.\"\"\"
       return Asset.objects.create(
           symbol='AAPL',
           name='Apple Inc.',
           asset_type='stock',
           exchange='NASDAQ',
           currency='USD',
           current_price=Decimal('150.00')
       )

   @pytest.fixture
   def portfolio(user):
       \"\"\"Create a test portfolio.\"\"\"
       return Portfolio.objects.create(
           user=user,
           name='Test Portfolio',
           description='A test portfolio',
           portfolio_type='growth'
       )

   @pytest.fixture
   def position(portfolio, asset):
       \"\"\"Create a test position.\"\"\"
       return Position.objects.create(
           portfolio=portfolio,
           asset=asset,
           quantity=Decimal('10'),
           purchase_price=Decimal('140.00'),
           purchase_date='2024-01-01'
       )

Writing Tests
~~~~~~~~~~~~~

**Model Tests:**

.. code-block:: python

   # tests/test_models.py
   import pytest
   from decimal import Decimal
   from django.core.exceptions import ValidationError
   from personal_finance.portfolio.models import Portfolio, Position

   @pytest.mark.django_db
   class TestPortfolioModel:
       \"\"\"Test Portfolio model functionality.\"\"\"

       def test_portfolio_creation(self, user):
           \"\"\"Test basic portfolio creation.\"\"\"
           portfolio = Portfolio.objects.create(
               user=user,
               name='Growth Portfolio',
               description='Long-term growth investments',
               portfolio_type='growth'
           )

           assert portfolio.name == 'Growth Portfolio'
           assert portfolio.user == user
           assert portfolio.portfolio_type == 'growth'
           assert portfolio.total_value == Decimal('0.00')

       def test_portfolio_str_representation(self, portfolio):
           \"\"\"Test portfolio string representation.\"\"\"
           assert str(portfolio) == f\"{portfolio.user.email} - {portfolio.name}\"

       def test_portfolio_total_value_calculation(self, portfolio, position):
           \"\"\"Test portfolio total value calculation.\"\"\"
           # Position has quantity=10, current_price=150.00
           expected_value = Decimal('10') * Decimal('150.00')
           assert portfolio.total_value == expected_value

       def test_portfolio_performance_metrics(self, portfolio, position):
           \"\"\"Test portfolio performance calculations.\"\"\"
           metrics = portfolio.get_performance_metrics()

           assert 'total_value' in metrics
           assert 'total_return' in metrics
           assert 'total_return_percent' in metrics
           assert 'daily_change' in metrics

**View Tests:**

.. code-block:: python

   # tests/test_views.py
   import pytest
   from django.urls import reverse
   from django.contrib.auth import get_user_model

   User = get_user_model()

   @pytest.mark.django_db
   class TestPortfolioViews:
       \"\"\"Test portfolio view functionality.\"\"\"

       def test_portfolio_list_view_authenticated(self, authenticated_client, portfolio):
           \"\"\"Test portfolio list view for authenticated users.\"\"\"
           url = reverse('portfolio:list')
           response = authenticated_client.get(url)

           assert response.status_code == 200
           assert portfolio.name in response.content.decode()

       def test_portfolio_list_view_unauthenticated(self, client):
           \"\"\"Test portfolio list view redirects unauthenticated users.\"\"\"
           url = reverse('portfolio:list')
           response = client.get(url)

           assert response.status_code == 302  # Redirect to login

       def test_portfolio_detail_view(self, authenticated_client, portfolio):
           \"\"\"Test portfolio detail view.\"\"\"
           url = reverse('portfolio:detail', kwargs={'pk': portfolio.pk})
           response = authenticated_client.get(url)

           assert response.status_code == 200
           assert portfolio.name in response.content.decode()

       def test_portfolio_create_view(self, authenticated_client, user):
           \"\"\"Test portfolio creation via view.\"\"\"
           url = reverse('portfolio:create')
           data = {
               'name': 'New Portfolio',
               'description': 'Test portfolio creation',
               'portfolio_type': 'balanced'
           }
           response = authenticated_client.post(url, data)

           assert response.status_code == 302  # Redirect after creation
           assert Portfolio.objects.filter(user=user, name='New Portfolio').exists()

**API Tests:**

.. code-block:: python

   # tests/test_api.py
   import pytest
   from django.urls import reverse
   from rest_framework import status

   @pytest.mark.django_db
   class TestPortfolioAPI:
       \"\"\"Test Portfolio API endpoints.\"\"\"

       def test_portfolio_list_api(self, authenticated_api_client, portfolio):
           \"\"\"Test portfolio list API endpoint.\"\"\"
           url = reverse('api:portfolio-list')
           response = authenticated_api_client.get(url)

           assert response.status_code == status.HTTP_200_OK
           assert len(response.data['results']) == 1
           assert response.data['results'][0]['name'] == portfolio.name

       def test_portfolio_create_api(self, authenticated_api_client, user):
           \"\"\"Test portfolio creation via API.\"\"\"
           url = reverse('api:portfolio-list')
           data = {
               'name': 'API Test Portfolio',
               'description': 'Created via API',
               'portfolio_type': 'growth'
           }
           response = authenticated_api_client.post(url, data)

           assert response.status_code == status.HTTP_201_CREATED
           assert response.data['name'] == 'API Test Portfolio'

       def test_portfolio_update_api(self, authenticated_api_client, portfolio):
           \"\"\"Test portfolio update via API.\"\"\"
           url = reverse('api:portfolio-detail', kwargs={'pk': portfolio.pk})
           data = {
               'name': 'Updated Portfolio Name',
               'description': portfolio.description,
               'portfolio_type': portfolio.portfolio_type
           }
           response = authenticated_api_client.patch(url, data)

           assert response.status_code == status.HTTP_200_OK
           assert response.data['name'] == 'Updated Portfolio Name'

       def test_portfolio_delete_api(self, authenticated_api_client, portfolio):
           \"\"\"Test portfolio deletion via API.\"\"\"
           url = reverse('api:portfolio-detail', kwargs={'pk': portfolio.pk})
           response = authenticated_api_client.delete(url)

           assert response.status_code == status.HTTP_204_NO_CONTENT

**Integration Tests:**

.. code-block:: python

   # tests/test_integration.py
   import pytest
   from decimal import Decimal
   from personal_finance.portfolio.services import PortfolioService
   from personal_finance.market_data.services import MarketDataService

   @pytest.mark.integration
   @pytest.mark.django_db
   class TestPortfolioIntegration:
       \"\"\"Integration tests for portfolio functionality.\"\"\"

       def test_portfolio_with_market_data_update(self, portfolio, position):
           \"\"\"Test portfolio value updates with market data.\"\"\"
           # Mock market data service
           service = PortfolioService()

           # Update asset prices
           new_price = Decimal('160.00')
           position.asset.current_price = new_price
           position.asset.save()

           # Recalculate portfolio value
           updated_value = service.calculate_portfolio_value(portfolio)
           expected_value = position.quantity * new_price

           assert updated_value == expected_value

Database Operations
-------------------

Migrations
~~~~~~~~~~

.. code-block:: bash

   # Create new migration
   python manage.py makemigrations

   # Apply migrations
   python manage.py migrate

   # Show migration status
   python manage.py showmigrations

   # Reverse migration
   python manage.py migrate app_name 0001_initial

   # Create empty migration
   python manage.py makemigrations --empty app_name

   # Squash migrations
   python manage.py squashmigrations app_name 0001 0005

Custom Management Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/portfolio/management/commands/import_sample_data.py
   from django.core.management.base import BaseCommand
   from personal_finance.portfolio.models import Asset
   from decimal import Decimal
   import json

   class Command(BaseCommand):
       help = 'Import sample asset data for development'

       def add_arguments(self, parser):
           parser.add_argument(
               '--file',
               type=str,
               default='fixtures/sample_assets.json',
               help='Path to sample data file'
           )

       def handle(self, *args, **options):
           file_path = options['file']

           try:
               with open(file_path, 'r') as f:
                   data = json.load(f)

               created_count = 0
               for item in data:
                   asset, created = Asset.objects.get_or_create(
                       symbol=item['symbol'],
                       defaults={
                           'name': item['name'],
                           'asset_type': item['type'],
                           'exchange': item['exchange'],
                           'currency': item['currency'],
                           'current_price': Decimal(str(item['price']))
                       }
                   )
                   if created:
                       created_count += 1

               self.stdout.write(
                   self.style.SUCCESS(f'Successfully imported {created_count} assets')
               )

           except FileNotFoundError:
               self.stdout.write(
                   self.style.ERROR(f'File not found: {file_path}')
               )
           except Exception as e:
               self.stdout.write(
                   self.style.ERROR(f'Error importing data: {str(e)}')
               )

Development Utilities
---------------------

Django Shell Plus
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install django-extensions
   pip install django-extensions

   # Add to INSTALLED_APPS in settings/local.py
   INSTALLED_APPS = [
       # ... other apps
       'django_extensions',
   ]

   # Use enhanced shell
   python manage.py shell_plus

   # Auto-import models and utilities
   python manage.py shell_plus --print-sql

Debug Toolbar
~~~~~~~~~~~~~

.. code-block:: python

   # Add to settings/local.py
   INSTALLED_APPS = [
       # ... other apps
       'debug_toolbar',
   ]

   MIDDLEWARE = [
       'debug_toolbar.middleware.DebugToolbarMiddleware',
       # ... other middleware
   ]

   INTERNAL_IPS = [
       '127.0.0.1',
   ]

   # Add to urls.py
   if settings.DEBUG:
       import debug_toolbar
       urlpatterns = [
           path('__debug__/', include(debug_toolbar.urls)),
       ] + urlpatterns

Development Workflows
--------------------

Feature Development Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Create feature branch
   git checkout -b feature/portfolio-analytics

   # 2. Make changes and commit frequently
   git add .
   git commit -m \"feat(portfolio): add basic analytics calculations\"

   # 3. Run tests
   pytest

   # 4. Run code quality checks
   pre-commit run --all-files

   # 5. Push branch
   git push origin feature/portfolio-analytics

   # 6. Create pull request
   # Use GitHub/GitLab interface

   # 7. After review and merge
   git checkout main
   git pull origin main
   git branch -d feature/portfolio-analytics

Testing Workflow
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Write tests first (TDD approach)
   # 1. Write failing test
   pytest tests/test_new_feature.py::test_new_functionality -v

   # 2. Implement minimum code to pass
   # Edit source files...

   # 3. Run specific test
   pytest tests/test_new_feature.py::test_new_functionality -v

   # 4. Refactor and ensure all tests pass
   pytest

   # 5. Check coverage
   pytest --cov=personal_finance --cov-report=html

Database Schema Changes
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Modify models
   # Edit models.py files...

   # 2. Create migration
   python manage.py makemigrations

   # 3. Review migration file
   cat personal_finance/app_name/migrations/0002_add_new_field.py

   # 4. Test migration
   python manage.py migrate

   # 5. Test reverse migration
   python manage.py migrate app_name 0001_initial
   python manage.py migrate  # Forward again

   # 6. Update fixtures if needed
   python manage.py dumpdata app_name > fixtures/updated_data.json

Debugging Techniques
--------------------

Using pdb
~~~~~~~~~

.. code-block:: python

   # Add breakpoint in code
   import pdb; pdb.set_trace()

   # Or use built-in breakpoint() (Python 3.7+)
   breakpoint()

   # Common pdb commands:
   # n - next line
   # s - step into function
   # c - continue execution
   # l - list current location
   # p variable_name - print variable
   # pp variable_name - pretty print variable
   # h - help

Django Debug Techniques
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Log database queries
   import logging
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger('django.db.backends')
   logger.setLevel(logging.DEBUG)

   # Print all SQL queries
   from django.db import connection
   print(connection.queries)

   # Debug view context
   from django.shortcuts import render
   def debug_view(request):
       context = {
           'user': request.user,
           'debug_info': {
               'method': request.method,
               'path': request.path,
               'GET': dict(request.GET),
               'POST': dict(request.POST),
           }
       }
       return render(request, 'debug.html', context)

API Development
---------------

API Testing with HTTPie
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install HTTPie
   pip install httpie

   # Test API endpoints
   http GET localhost:8000/api/v1/portfolios/ Authorization:\"Bearer your-token\"

   # POST request
   http POST localhost:8000/api/v1/portfolios/ \\
       name=\"Test Portfolio\" \\
       description=\"API Test\" \\
       portfolio_type=\"growth\" \\
       Authorization:\"Bearer your-token\"

   # PATCH request
   http PATCH localhost:8000/api/v1/portfolios/1/ \\
       name=\"Updated Name\" \\
       Authorization:\"Bearer your-token\"

API Documentation
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Install drf-spectacular for OpenAPI docs
   pip install drf-spectacular

   # Add to settings.py
   INSTALLED_APPS = [
       # ... other apps
       'drf_spectacular',
   ]

   REST_FRAMEWORK = {
       # ... other settings
       'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
   }

   SPECTACULAR_SETTINGS = {
       'TITLE': 'Personal Finance API',
       'DESCRIPTION': 'API for personal finance management',
       'VERSION': '1.0.0',
   }

   # Add to urls.py
   from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

   urlpatterns = [
       # ... other patterns
       path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
       path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
   ]

Performance Profiling
---------------------

Django Silk
~~~~~~~~~~~

.. code-block:: bash

   # Install django-silk
   pip install django-silk

   # Add to settings/local.py
   INSTALLED_APPS = [
       # ... other apps
       'silk',
   ]

   MIDDLEWARE = [
       'silk.middleware.SilkyMiddleware',
       # ... other middleware
   ]

   # Add to urls.py
   if settings.DEBUG:
       urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

   # Access profiler at http://localhost:8000/silk/

Memory Profiling
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Using memory_profiler
   pip install memory-profiler

   # Decorate functions to profile
   from memory_profiler import profile

   @profile
   def memory_intensive_function():
       # Your code here
       pass

   # Run with line profiling
   python -m memory_profiler your_script.py

Contributing Guidelines
-----------------------

Code Style
~~~~~~~~~~

1. **Follow PEP 8** with Black formatting
2. **Use type hints** for function signatures
3. **Write descriptive docstrings** for all classes and functions
4. **Keep functions small** and focused on single responsibility
5. **Use meaningful variable names** that describe the data

Documentation
~~~~~~~~~~~~~

1. **Update docstrings** when modifying functions
2. **Add comments** for complex business logic
3. **Update README** for major feature changes
4. **Write migration notes** for database changes
5. **Document API changes** in OpenAPI schema

Testing Requirements
~~~~~~~~~~~~~~~~~~~

1. **Write tests** for all new functionality
2. **Maintain 80%+ code coverage**
3. **Include integration tests** for critical paths
4. **Test edge cases** and error conditions
5. **Mock external services** in unit tests

Commit Message Format
~~~~~~~~~~~~~~~~~~~~

Follow Conventional Commits specification:

.. code-block:: text

   <type>[optional scope]: <description>

   [optional body]

   [optional footer(s)]

**Examples:**

.. code-block:: text

   feat(portfolio): add portfolio performance analytics
   fix(api): resolve authentication token expiry issue
   docs(readme): update installation instructions
   test(portfolio): add unit tests for portfolio calculations
   refactor(models): simplify asset price update logic

Troubleshooting
---------------

Common Development Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

**Virtual Environment Issues:**

.. code-block:: bash

   # Recreate virtual environment
   rm -rf .venv/
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements-dev.txt

**Database Connection Issues:**

.. code-block:: bash

   # Check PostgreSQL status
   sudo systemctl status postgresql

   # Restart PostgreSQL
   sudo systemctl restart postgresql

   # Test connection
   psql -h localhost -U dev_user -d personal_finance_dev

**Migration Issues:**

.. code-block:: bash

   # Reset migrations (development only)
   python manage.py migrate app_name zero
   rm app_name/migrations/0*.py
   python manage.py makemigrations app_name
   python manage.py migrate

**Import Issues:**

.. code-block:: python

   # Check PYTHONPATH
   import sys
   print(sys.path)

   # Add project root to path if needed
   import os
   import sys
   sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

See Also
--------

* :doc:`../deployment/index` - Production deployment guide
* :doc:`../config/django_settings` - Django configuration reference
* :doc:`../api/rest_endpoints` - API development reference
* :doc:`../modules/index` - Feature modules documentation

**Confidence: 96%**. I've created comprehensive development documentation covering all major aspects of the development workflow. Is there any specific area you'd like me to expand on or any particular development workflow you'd like more detail about?
