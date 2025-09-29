Quick Start Guide
=================

This guide gets you up and running with the Personal Finance Platform quickly.

.. note::
   This is a quick reference. For detailed installation and configuration, see the respective sections.

Prerequisites
-------------

* Python 3.10 – 3.13 with pip
* PostgreSQL (optional; falls back to SQLite)
* Redis (required for Celery, optional for simple local runs)
* Docker + Docker Compose (optional, but recommended for parity)

Local Development Setup
-----------------------

1. **Clone and Environment Setup**

   .. code-block:: bash

      git clone https://github.com/MauGx3/personal-finance.git
      cd personal-finance
      python -m venv .venv
      source .venv/bin/activate  # Linux/macOS
      # .venv\Scripts\activate   # Windows

2. **Install Dependencies**

   .. code-block:: bash

      python -m pip install --upgrade pip
      pip install -r requirements.txt
      pip install -r requirements-dev.txt

3. **Configure Environment**

   .. code-block:: bash

      cp .env.example .env
      # Edit .env to set DATABASE_URL, REDIS_URL, DJANGO_SECRET_KEY, etc.

4. **Initialize Database**

   .. code-block:: bash

      python manage.py migrate
      python manage.py collectstatic --noinput

5. **Start Development Server**

   .. code-block:: bash

      python manage.py runserver

Docker Compose Setup
--------------------

For a complete development environment:

.. code-block:: bash

   just up          # or: docker compose -f docker-compose.local.yml up -d
   just logs django # view container logs
   just down        # or: docker compose down

Essential Commands
------------------

.. code-block:: bash

   # Django management
   python manage.py check                    # Validate configuration
   python manage.py shell                    # Interactive shell
   python manage.py createsuperuser          # Create admin user

   # Database operations
   python manage.py makemigrations           # Create migrations
   python manage.py migrate                  # Apply migrations
   alembic upgrade head                      # Apply Alembic migrations

   # Background services
   celery -A config worker -l info           # Start Celery worker
   python run_finance.py                     # Run ETL/backtesting

   # Quality checks
   pytest -q                                 # Run tests
   ruff check .                              # Lint code
   black .                                   # Format code

Next Steps
----------

* :doc:`installation` - Detailed installation instructions
* :doc:`configuration` - Environment and configuration reference
* :doc:`development/setup` - Complete development environment setup
* :doc:`deployment/docker` - Production deployment with Docker
