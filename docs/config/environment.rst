Environment Configuration Reference
====================================

Complete reference for environment variables and configuration options.

.. contents:: Table of Contents
   :local:
   :depth: 2

Configuration Overview
----------------------

The Personal Finance Platform uses a multi-layered configuration system:

1. **Environment Variables** - Runtime configuration via ``.env`` files
2. **Django Settings** - Application configuration in ``config/settings/``
3. **Feature Flags** - Runtime feature toggles
4. **Service Configuration** - External service credentials and options

Environment Files
------------------

File Hierarchy
~~~~~~~~~~~~~~

.. code-block:: text

   .env.example          # Template with all available variables
   .env                  # Local development (gitignored)
   .envs/                # Environment-specific files
   ├── .local/           # Local development overrides
   ├── .production/      # Production environment
   └── .staging/         # Staging environment

Example .env Structure
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Core Django Settings
   DJANGO_SETTINGS_MODULE=config.settings.local
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

   # Database Configuration
   DATABASE_URL=postgresql://user:password@localhost:5432/personal_finance

   # Cache & Session Store
   REDIS_URL=redis://localhost:6379/0

   # Celery Configuration
   CELERY_BROKER_URL=redis://localhost:6379/1
   CELERY_RESULT_BACKEND=redis://localhost:6379/2

   # External APIs
   YAHOO_FINANCE_API_KEY=optional-api-key
   ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key

   # Email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   EMAIL_USE_TLS=True

Core Configuration Variables
-----------------------------

Django Core Settings
~~~~~~~~~~~~~~~~~~~~

.. envvar:: DJANGO_SETTINGS_MODULE

   Django settings module to use.

   :Default: ``config.settings.local``
   :Options:
      - ``config.settings.local`` - Development
      - ``config.settings.production`` - Production
      - ``config.settings.test`` - Testing

.. envvar:: DJANGO_SECRET_KEY

   Django secret key for cryptographic signing.

   :Required: Yes
   :Example: ``django-insecure-your-secret-key-here``
   :Security: Must be kept secret, different per environment

.. envvar:: DJANGO_DEBUG

   Enable Django debug mode.

   :Default: ``False``
   :Options: ``True``, ``False``
   :Warning: Never enable in production

.. envvar:: DJANGO_ALLOWED_HOSTS

   Comma-separated list of allowed hostnames.

   :Default: ``localhost,127.0.0.1``
   :Example: ``localhost,127.0.0.1,mysite.com,*.mysite.com``
   :Production: Must include your domain

Database Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. envvar:: DATABASE_URL

   Primary database connection string.

   :Default: SQLite fallback if unset
   :Format: ``postgresql://user:password@host:port/database``
   :Examples:
      - ``postgresql://postgres:password@localhost:5432/personal_finance``
      - ``sqlite:///db.sqlite3`` (fallback)

.. envvar:: DATABASE_CONN_MAX_AGE

   Database connection max age in seconds.

   :Default: ``0`` (no persistence)
   :Recommended: ``300`` (5 minutes) for production

Cache & Session Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. envvar:: REDIS_URL

   Redis connection for caching and sessions.

   :Default: No Redis (Django cache fallback)
   :Format: ``redis://[:password]@host:port/db``
   :Examples:
      - ``redis://localhost:6379/0``
      - ``redis://:password@redis-server:6379/0``

.. envvar:: CACHE_TTL

   Default cache timeout in seconds.

   :Default: ``300`` (5 minutes)
   :Range: ``60`` - ``3600``

Background Processing
~~~~~~~~~~~~~~~~~~~~~

.. envvar:: CELERY_BROKER_URL

   Celery message broker URL.

   :Default: Same as ``REDIS_URL``
   :Required: For background tasks
   :Format: ``redis://host:port/db``

.. envvar:: CELERY_RESULT_BACKEND

   Celery result backend URL.

   :Default: Same as ``CELERY_BROKER_URL``
   :Format: ``redis://host:port/db``

.. envvar:: CELERY_TASK_ALWAYS_EAGER

   Execute Celery tasks synchronously.

   :Default: ``False``
   :Options: ``True`` (for testing), ``False`` (production)

Real-time Configuration
~~~~~~~~~~~~~~~~~~~~~~~

.. envvar:: REALTIME_UPDATE_INTERVAL

   Price update interval in seconds.

   :Default: ``30``
   :Range: ``10`` - ``300``
   :Note: Lower values increase API usage

.. envvar:: REALTIME_BATCH_SIZE

   Number of assets to update per batch.

   :Default: ``50``
   :Range: ``10`` - ``100``

.. envvar:: WEBSOCKET_TIMEOUT

   WebSocket connection timeout in seconds.

   :Default: ``300`` (5 minutes)
   :Range: ``60`` - ``3600``

External API Configuration
--------------------------

Market Data APIs
~~~~~~~~~~~~~~~~

.. envvar:: YAHOO_FINANCE_API_KEY

   Yahoo Finance API key (optional).

   :Default: None (uses free tier)
   :Note: Increases rate limits when provided

.. envvar:: ALPHA_VANTAGE_API_KEY

   Alpha Vantage API key for additional data.

   :Default: None
   :Required: For extended market data features
   :Get Key: https://www.alphavantage.co/support/#api-key

.. envvar:: MARKET_DATA_PROVIDER

   Primary market data provider.

   :Default: ``yahoo_finance``
   :Options: ``yahoo_finance``, ``alpha_vantage``

API Rate Limiting
~~~~~~~~~~~~~~~~~

.. envvar:: API_RATE_LIMIT_PER_HOUR

   API requests per hour per user.

   :Default: ``1000``
   :Range: ``100`` - ``10000``

.. envvar:: YAHOO_FINANCE_RATE_LIMIT

   Yahoo Finance API rate limit.

   :Default: ``2000`` requests/hour
   :Note: Varies by API key tier

Email Configuration
-------------------

SMTP Settings
~~~~~~~~~~~~~

.. envvar:: EMAIL_HOST

   SMTP server hostname.

   :Default: ``localhost``
   :Examples: ``smtp.gmail.com``, ``smtp.mailgun.org``

.. envvar:: EMAIL_PORT

   SMTP server port.

   :Default: ``25``
   :Common Ports:
      - ``25`` - Standard SMTP
      - ``587`` - SMTP with STARTTLS
      - ``465`` - SMTP with SSL

.. envvar:: EMAIL_HOST_USER

   SMTP authentication username.

   :Default: None
   :Example: ``your-email@gmail.com``

.. envvar:: EMAIL_HOST_PASSWORD

   SMTP authentication password.

   :Default: None
   :Security: Use app-specific passwords for Gmail

.. envvar:: EMAIL_USE_TLS

   Enable STARTTLS encryption.

   :Default: ``False``
   :Recommended: ``True`` for port 587

.. envvar:: EMAIL_USE_SSL

   Enable SSL encryption.

   :Default: ``False``
   :Note: Use for port 465

Email Addresses
~~~~~~~~~~~~~~~

.. envvar:: DEFAULT_FROM_EMAIL

   Default sender email address.

   :Default: ``webmaster@localhost``
   :Example: ``noreply@yourfinance.com``

.. envvar:: ADMIN_EMAIL

   Administrator email for notifications.

   :Default: None
   :Example: ``admin@yourfinance.com``

Security Configuration
----------------------

Authentication & Authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. envvar:: SESSION_COOKIE_SECURE

   Require HTTPS for session cookies.

   :Default: ``False`` (local), ``True`` (production)
   :Production: Must be ``True``

.. envvar:: CSRF_COOKIE_SECURE

   Require HTTPS for CSRF cookies.

   :Default: ``False`` (local), ``True`` (production)
   :Production: Must be ``True``

.. envvar:: SECURE_SSL_REDIRECT

   Redirect HTTP to HTTPS.

   :Default: ``False`` (local), ``True`` (production)
   :Production: Should be ``True``

API Security
~~~~~~~~~~~~

.. envvar:: API_TOKEN_EXPIRY_HOURS

   API token expiration time in hours.

   :Default: ``24`` (1 day)
   :Range: ``1`` - ``168`` (1 week)

.. envvar:: LOGIN_ATTEMPTS_LIMIT

   Maximum login attempts before lockout.

   :Default: ``5``
   :Range: ``3`` - ``10``

.. envvar:: LOGIN_LOCKOUT_MINUTES

   Account lockout duration in minutes.

   :Default: ``30``
   :Range: ``5`` - ``120``

Data Protection
~~~~~~~~~~~~~~~

.. envvar:: ENCRYPT_API_KEYS

   Encrypt API keys in database.

   :Default: ``True``
   :Production: Must be ``True``

.. envvar:: LOG_SENSITIVE_DATA

   Include sensitive data in logs.

   :Default: ``False``
   :Warning: Never enable in production

Logging Configuration
---------------------

Log Levels
~~~~~~~~~~

.. envvar:: DJANGO_LOG_LEVEL

   Django framework log level.

   :Default: ``INFO``
   :Options: ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``

.. envvar:: APPLICATION_LOG_LEVEL

   Application code log level.

   :Default: ``INFO``
   :Debug: Use ``DEBUG`` for development

.. envvar:: CELERY_LOG_LEVEL

   Celery worker log level.

   :Default: ``INFO``
   :Options: Same as Django levels

Log Destinations
~~~~~~~~~~~~~~~~

.. envvar:: LOG_TO_FILE

   Enable file logging.

   :Default: ``True``
   :File Location: ``logs/`` directory

.. envvar:: LOG_TO_CONSOLE

   Enable console logging.

   :Default: ``True`` (development), ``False`` (production)

.. envvar:: LOG_FILE_MAX_SIZE

   Maximum log file size in MB.

   :Default: ``10``
   :Range: ``1`` - ``100``

.. envvar:: LOG_FILE_BACKUP_COUNT

   Number of rotated log files to keep.

   :Default: ``5``
   :Range: ``1`` - ``20``

Feature Flags
-------------

Application Features
~~~~~~~~~~~~~~~~~~~~

.. envvar:: ENABLE_BACKTESTING

   Enable backtesting functionality.

   :Default: ``True``
   :Note: Can disable to reduce resource usage

.. envvar:: ENABLE_REALTIME_UPDATES

   Enable real-time price updates.

   :Default: ``True``
   :Dependencies: Requires Redis and Celery

.. envvar:: ENABLE_TAX_CALCULATIONS

   Enable tax calculation features.

   :Default: ``True``
   :Note: US tax calculations only

.. envvar:: ENABLE_DATA_PROFILING

   Enable data profiling with DataProfiler.

   :Default: ``True``
   :Dependencies: Requires dataprofiler package

Experimental Features
~~~~~~~~~~~~~~~~~~~~~

.. envvar:: ENABLE_ADVANCED_ANALYTICS

   Enable experimental analytics features.

   :Default: ``False``
   :Warning: Beta functionality

.. envvar:: ENABLE_ML_PREDICTIONS

   Enable machine learning predictions.

   :Default: ``False``
   :Dependencies: Requires scikit-learn

Performance Configuration
-------------------------

Database Optimization
~~~~~~~~~~~~~~~~~~~~~

.. envvar:: DATABASE_POOL_SIZE

   Database connection pool size.

   :Default: ``5``
   :Range: ``2`` - ``20``
   :Note: Higher values for high-concurrency

.. envvar:: DATABASE_MAX_OVERFLOW

   Maximum connection overflow.

   :Default: ``10``
   :Range: ``5`` - ``50``

Cache Configuration
~~~~~~~~~~~~~~~~~~~

.. envvar:: CACHE_DEFAULT_TIMEOUT

   Default cache timeout in seconds.

   :Default: ``300`` (5 minutes)
   :Range: ``60`` - ``3600``

.. envvar:: CACHE_MAX_ENTRIES

   Maximum cache entries.

   :Default: ``10000``
   :Range: ``1000`` - ``100000``

Background Tasks
~~~~~~~~~~~~~~~~

.. envvar:: CELERY_WORKER_CONCURRENCY

   Number of Celery worker processes.

   :Default: CPU count
   :Range: ``1`` - ``16``
   :Note: Adjust based on server capacity

.. envvar:: CELERY_TASK_TIMEOUT

   Task timeout in seconds.

   :Default: ``300`` (5 minutes)
   :Range: ``60`` - ``3600``

Environment-Specific Settings
-----------------------------

Development (.env.local)
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   DJANGO_SETTINGS_MODULE=config.settings.local
   DJANGO_DEBUG=True
   DJANGO_SECRET_KEY=dev-secret-key-not-for-production

   # Use SQLite for simplicity
   # DATABASE_URL=sqlite:///dev.db

   # Local Redis
   REDIS_URL=redis://localhost:6379/0

   # Disable external APIs in development
   ENABLE_REALTIME_UPDATES=False

   # Debug logging
   DJANGO_LOG_LEVEL=DEBUG
   APPLICATION_LOG_LEVEL=DEBUG

Production (.env.production)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   DJANGO_SETTINGS_MODULE=config.settings.production
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=${SECRET_KEY_FROM_VAULT}
   DJANGO_ALLOWED_HOSTS=yourfinance.com,api.yourfinance.com

   # Production database
   DATABASE_URL=${DATABASE_URL_FROM_VAULT}
   DATABASE_CONN_MAX_AGE=300

   # Production Redis
   REDIS_URL=${REDIS_URL_FROM_VAULT}

   # Security settings
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   SECURE_SSL_REDIRECT=True

   # Performance settings
   DATABASE_POOL_SIZE=10
   CELERY_WORKER_CONCURRENCY=4

   # Production logging
   DJANGO_LOG_LEVEL=INFO
   LOG_TO_CONSOLE=False

Testing (.env.test)
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   DJANGO_SETTINGS_MODULE=config.settings.test
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=test-secret-key

   # In-memory database for tests
   DATABASE_URL=sqlite:///:memory:

   # Disable external services in tests
   CELERY_TASK_ALWAYS_EAGER=True
   ENABLE_REALTIME_UPDATES=False

   # Disable logging in tests
   LOG_TO_CONSOLE=False
   LOG_TO_FILE=False

Configuration Validation
-------------------------

Required Variables Checker
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # config/settings/base.py
   import os
   from django.core.exceptions import ImproperlyConfigured

   def get_env_variable(var_name, default=None, required=True):
       \"\"\"Get environment variable or raise exception.\"\"\"
       value = os.environ.get(var_name, default)

       if required and value is None:
           error_msg = f\"Set the {var_name} environment variable\"
           raise ImproperlyConfigured(error_msg)

       return value

   # Usage
   SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY')
   DEBUG = get_env_variable('DJANGO_DEBUG', 'False').lower() == 'true'

Environment Validation Command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Validate current environment configuration
   python manage.py check_config

   # Check specific environment
   python manage.py check_config --env production

Configuration Management
-------------------------

Environment File Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``.env.example`` as a template:

.. code-block:: bash

   # Copy template
   cp .env.example .env

   # Edit with your values
   vim .env

Docker Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   # Dockerfile - Environment handling
   FROM python:3.11

   # Set environment variables
   ENV PYTHONDONTWRITEBYTECODE=1
   ENV PYTHONUNBUFFERED=1
   ENV DJANGO_SETTINGS_MODULE=config.settings.production

   # Copy environment file
   COPY .env.production /app/.env

   WORKDIR /app
   COPY . /app/

Secrets Management
~~~~~~~~~~~~~~~~~~

For production deployments:

.. code-block:: bash

   # Use external secret management
   export DJANGO_SECRET_KEY=$(vault kv get -field=secret_key secret/finance/django)
   export DATABASE_URL=$(vault kv get -field=url secret/finance/database)

   # Or use Docker secrets
   export DJANGO_SECRET_KEY_FILE=/run/secrets/django_secret_key

Troubleshooting
---------------

Common Configuration Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Configuration Not Loading**
  - Check ``.env`` file location (should be in project root)
  - Verify file permissions (readable by application user)
  - Check for syntax errors in environment files

**Database Connection Issues**
  - Validate ``DATABASE_URL`` format
  - Test database connectivity manually
  - Check firewall and network settings

**Redis Connection Issues**
  - Verify ``REDIS_URL`` is correct
  - Check Redis server status
  - Test connection with redis-cli

**Email Configuration Problems**
  - Test SMTP settings with telnet
  - Check firewall rules for email ports
  - Verify authentication credentials

Debug Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Debug current configuration
   python manage.py shell

   >>> from django.conf import settings
   >>> print(f\"DEBUG: {settings.DEBUG}\")
   >>> print(f\"DATABASE: {settings.DATABASES['default']['ENGINE']}\")
   >>> print(f\"CACHE: {settings.CACHES['default']['BACKEND']}\")

Configuration Testing
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Test configuration values
   python manage.py check --deploy  # Production readiness check
   python manage.py check_config    # Custom configuration validation

See Also
--------

* :doc:`django_settings` - Django settings reference
* :doc:`security` - Security configuration details
* :doc:`../deployment/docker` - Docker deployment configuration
* :doc:`../development/setup` - Development environment setup
