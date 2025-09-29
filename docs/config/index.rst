Configuration Reference
======================

Complete configuration reference for the Personal Finance Platform.

.. contents:: Table of Contents
   :local:
   :depth: 2

Configuration Overview
----------------------

The Personal Finance Platform uses a comprehensive configuration system organized into several key areas:

.. toctree::
   :maxdepth: 2

   environment
   django_settings
   security

Configuration Hierarchy
------------------------

The configuration system follows a clear hierarchy:

.. code-block:: text

   Environment Variables (.env files)
   ├── Core Django Settings (DJANGO_*)
   ├── Database Configuration (DATABASE_*)
   ├── Cache & Session (REDIS_*, CACHE_*)
   ├── External APIs (YAHOO_*, ALPHA_VANTAGE_*)
   ├── Email Settings (EMAIL_*)
   ├── Security Settings (SECURE_*, CSRF_*)
   └── Feature Flags (ENABLE_*)
       │
   Django Settings Modules
   ├── base.py (Common settings)
   ├── local.py (Development)
   ├── production.py (Production)
   └── test.py (Testing)
       │
   Application Configuration
   ├── Feature-specific settings
   ├── Service integrations
   └── Business logic parameters

Quick Configuration Guide
-------------------------

Basic Local Setup
~~~~~~~~~~~~~~~~~

1. **Copy Environment Template**

   .. code-block:: bash

      cp .env.example .env

2. **Edit Basic Settings**

   .. code-block:: bash

      # Required settings
      DJANGO_SECRET_KEY=your-development-secret-key
      DJANGO_SETTINGS_MODULE=config.settings.local
      DJANGO_DEBUG=True

      # Optional for full features
      REDIS_URL=redis://localhost:6379/0
      DATABASE_URL=postgresql://user:password@localhost/personal_finance

3. **Initialize Database**

   .. code-block:: bash

      python manage.py migrate
      python setup_database.py  # Optional demo data

Production Setup
~~~~~~~~~~~~~~~~

1. **Generate Secure Keys**

   .. code-block:: bash

      # Generate Django secret key
      python -c "import secrets; print('DJANGO_SECRET_KEY=' + secrets.token_urlsafe(50))"

      # Generate field encryption key
      python -c "from cryptography.fernet import Fernet; print('FIELD_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

2. **Configure Production Environment**

   .. code-block:: bash

      # Core production settings
      DJANGO_SETTINGS_MODULE=config.settings.production
      DJANGO_DEBUG=False
      DJANGO_SECRET_KEY=<generated-secret-key>
      DJANGO_ALLOWED_HOSTS=yourfinance.com,api.yourfinance.com

      # Database (PostgreSQL recommended)
      DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require

      # Cache and sessions (Redis required)
      REDIS_URL=redis://user:password@host:port/db

      # Email configuration
      EMAIL_HOST=smtp.yourprovider.com
      EMAIL_PORT=587
      EMAIL_USE_TLS=True
      EMAIL_HOST_USER=your-email@domain.com
      EMAIL_HOST_PASSWORD=your-app-password

      # Security settings
      SESSION_COOKIE_SECURE=True
      CSRF_COOKIE_SECURE=True
      SECURE_SSL_REDIRECT=True

3. **Deploy with Security**

   .. code-block:: bash

      # Validate configuration
      python manage.py check --deploy
      python manage.py check_config --env production

      # Collect static files
      python manage.py collectstatic --noinput

      # Run migrations
      python manage.py migrate

Configuration Categories
------------------------

Core Application Settings
~~~~~~~~~~~~~~~~~~~~~~~~~

These settings control fundamental application behavior:

+--------------------------------+---------------------------+------------------------------------+
| Setting                        | Default                   | Description                        |
+================================+===========================+====================================+
| DJANGO_SETTINGS_MODULE         | config.settings.local     | Django settings module             |
+--------------------------------+---------------------------+------------------------------------+
| DJANGO_SECRET_KEY              | *Required*                | Django cryptographic signing key  |
+--------------------------------+---------------------------+------------------------------------+
| DJANGO_DEBUG                   | False                     | Enable debug mode                  |
+--------------------------------+---------------------------+------------------------------------+
| DJANGO_ALLOWED_HOSTS           | []                        | Allowed hostnames                  |
+--------------------------------+---------------------------+------------------------------------+

Database Configuration
~~~~~~~~~~~~~~~~~~~~~~

Database connection and performance settings:

+--------------------------------+---------------------------+------------------------------------+
| Setting                        | Default                   | Description                        |
+================================+===========================+====================================+
| DATABASE_URL                   | sqlite:///db.sqlite3      | Primary database connection        |
+--------------------------------+---------------------------+------------------------------------+
| DATABASE_CONN_MAX_AGE          | 0                         | Connection persistence (seconds)   |
+--------------------------------+---------------------------+------------------------------------+
| DATABASE_POOL_SIZE             | 5                         | Connection pool size               |
+--------------------------------+---------------------------+------------------------------------+
| DATABASE_MAX_OVERFLOW          | 10                        | Maximum connection overflow        |
+--------------------------------+---------------------------+------------------------------------+

Cache and Session Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Caching and session management configuration:

+--------------------------------+---------------------------+------------------------------------+
| Setting                        | Default                   | Description                        |
+================================+===========================+====================================+
| REDIS_URL                      | None                      | Redis connection for cache/sessions|
+--------------------------------+---------------------------+------------------------------------+
| CACHE_TTL                      | 300                       | Default cache timeout (seconds)   |
+--------------------------------+---------------------------+------------------------------------+
| SESSION_COOKIE_AGE             | 3600                      | Session timeout (seconds)         |
+--------------------------------+---------------------------+------------------------------------+
| SESSION_COOKIE_SECURE          | True (production)         | Require HTTPS for session cookies |
+--------------------------------+---------------------------+------------------------------------+

Background Processing
~~~~~~~~~~~~~~~~~~~~~

Celery and background task configuration:

+--------------------------------+---------------------------+------------------------------------+
| Setting                        | Default                   | Description                        |
+================================+===========================+====================================+
| CELERY_BROKER_URL              | redis://localhost:6379/1  | Celery message broker              |
+--------------------------------+---------------------------+------------------------------------+
| CELERY_RESULT_BACKEND          | redis://localhost:6379/2  | Celery result storage              |
+--------------------------------+---------------------------+------------------------------------+
| CELERY_WORKER_CONCURRENCY      | CPU count                 | Number of worker processes         |
+--------------------------------+---------------------------+------------------------------------+
| CELERY_TASK_SOFT_TIME_LIMIT    | 300                       | Task soft timeout (seconds)       |
+--------------------------------+---------------------------+------------------------------------+
| CELERY_TASK_TIME_LIMIT         | 600                       | Task hard timeout (seconds)       |
+--------------------------------+---------------------------+------------------------------------+

External API Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Market data and external service settings:

+--------------------------------+---------------------------+------------------------------------+
| Setting                        | Default                   | Description                        |
+================================+===========================+====================================+
| YAHOO_FINANCE_API_KEY          | None                      | Yahoo Finance API key (optional)  |
+--------------------------------+---------------------------+------------------------------------+
| ALPHA_VANTAGE_API_KEY          | None                      | Alpha Vantage API key              |
+--------------------------------+---------------------------+------------------------------------+
| MARKET_DATA_PROVIDER           | yahoo_finance             | Primary market data provider       |
+--------------------------------+---------------------------+------------------------------------+
| API_RATE_LIMIT_PER_HOUR        | 1000                      | API requests per hour per user     |
+--------------------------------+---------------------------+------------------------------------+

Feature Flags
~~~~~~~~~~~~~

Enable or disable application features:

+--------------------------------+---------------------------+------------------------------------+
| Setting                        | Default                   | Description                        |
+================================+===========================+====================================+
| ENABLE_BACKTESTING             | True                      | Enable backtesting functionality   |
+--------------------------------+---------------------------+------------------------------------+
| ENABLE_REALTIME_UPDATES        | True                      | Enable real-time price updates     |
+--------------------------------+---------------------------+------------------------------------+
| ENABLE_TAX_CALCULATIONS        | True                      | Enable tax calculation features     |
+--------------------------------+---------------------------+------------------------------------+
| ENABLE_DATA_PROFILING          | True                      | Enable data profiling with DataProfiler|
+--------------------------------+---------------------------+------------------------------------+
| ENABLE_ADVANCED_ANALYTICS      | False                     | Enable experimental analytics       |
+--------------------------------+---------------------------+------------------------------------+
| ENABLE_ML_PREDICTIONS          | False                     | Enable ML prediction features       |
+--------------------------------+---------------------------+------------------------------------+

Security Configuration
~~~~~~~~~~~~~~~~~~~~~~~

Security and authentication settings:

+--------------------------------+---------------------------+------------------------------------+
| Setting                        | Default                   | Description                        |
+================================+===========================+====================================+
| SECURE_SSL_REDIRECT            | True (production)         | Redirect HTTP to HTTPS             |
+--------------------------------+---------------------------+------------------------------------+
| CSRF_COOKIE_SECURE             | True (production)         | Require HTTPS for CSRF cookies     |
+--------------------------------+---------------------------+------------------------------------+
| API_TOKEN_EXPIRY_HOURS         | 24                        | API token expiration time          |
+--------------------------------+---------------------------+------------------------------------+
| LOGIN_ATTEMPTS_LIMIT           | 5                         | Max login attempts before lockout  |
+--------------------------------+---------------------------+------------------------------------+
| LOGIN_LOCKOUT_MINUTES          | 30                        | Account lockout duration           |
+--------------------------------+---------------------------+------------------------------------+

Performance Settings
~~~~~~~~~~~~~~~~~~~~

Performance tuning and optimization:

+--------------------------------+---------------------------+------------------------------------+
| Setting                        | Default                   | Description                        |
+================================+===========================+====================================+
| REALTIME_UPDATE_INTERVAL       | 30                        | Price update interval (seconds)    |
+--------------------------------+---------------------------+------------------------------------+
| REALTIME_BATCH_SIZE            | 50                        | Assets to update per batch         |
+--------------------------------+---------------------------+------------------------------------+
| BACKTESTING_MAX_LOOKBACK_YEARS | 10                        | Maximum historical data years      |
+--------------------------------+---------------------------+------------------------------------+
| CACHE_MAX_ENTRIES              | 10000                     | Maximum cache entries              |
+--------------------------------+---------------------------+------------------------------------+

Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

Logging levels and destinations:

+--------------------------------+---------------------------+------------------------------------+
| Setting                        | Default                   | Description                        |
+================================+===========================+====================================+
| DJANGO_LOG_LEVEL               | INFO                      | Django framework log level         |
+--------------------------------+---------------------------+------------------------------------+
| APPLICATION_LOG_LEVEL          | INFO                      | Application code log level         |
+--------------------------------+---------------------------+------------------------------------+
| CELERY_LOG_LEVEL               | INFO                      | Celery worker log level            |
+--------------------------------+---------------------------+------------------------------------+
| LOG_TO_FILE                    | True                      | Enable file logging                |
+--------------------------------+---------------------------+------------------------------------+
| LOG_TO_CONSOLE                 | True (dev), False (prod)  | Enable console logging             |
+--------------------------------+---------------------------+------------------------------------+

Configuration Validation
------------------------

Built-in Validation
~~~~~~~~~~~~~~~~~~~

The platform includes several configuration validation mechanisms:

**Django System Checks**
   Built-in Django validation for common configuration issues.

   .. code-block:: bash

      # Run all system checks
      python manage.py check

      # Production deployment checks
      python manage.py check --deploy

**Custom Configuration Validation**
   Application-specific validation for custom settings.

   .. code-block:: bash

      # Validate current configuration
      python manage.py check_config

      # Validate specific environment
      python manage.py check_config --env production

**Environment Validation Script**
   Standalone validation script for environment setup.

   .. code-block:: python

      # config/validation.py
      from django.core.management import execute_from_command_line
      from django.core.exceptions import ImproperlyConfigured
      import os

      def validate_environment():
          \"\"\"Validate environment configuration.\"\"\"
          required_vars = [
              'DJANGO_SETTINGS_MODULE',
              'DJANGO_SECRET_KEY',
          ]

          missing = [var for var in required_vars if not os.environ.get(var)]
          if missing:
              raise ImproperlyConfigured(f\"Missing required variables: {missing}\")

          print(\"✓ Environment validation passed\")

Configuration Management Tools
------------------------------

Environment File Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Template Generation**
   Generate environment templates for different deployment scenarios.

   .. code-block:: bash

      # Generate environment template
      python manage.py generate_env_template --env production > .env.production.example

**Environment Comparison**
   Compare configurations between environments.

   .. code-block:: bash

      # Compare local vs production settings
      python manage.py compare_config local production

**Configuration Export**
   Export current configuration for documentation or backup.

   .. code-block:: bash

      # Export current configuration
      python manage.py export_config --format json > current_config.json

Docker Configuration
~~~~~~~~~~~~~~~~~~~~

**Environment Variable Injection**

   .. code-block:: yaml

      # docker-compose.yml
      version: '3.8'
      services:
        web:
          build: .
          env_file:
            - .env
            - .env.local
          environment:
            - DJANGO_SETTINGS_MODULE=config.settings.production
          volumes:
            - ./logs:/app/logs
            - static_volume:/app/staticfiles

**Configuration Validation in Docker**

   .. code-block:: dockerfile

      # Dockerfile configuration validation
      RUN python manage.py check --deploy && \\
          python manage.py check_config --env production

Secrets Management
------------------

Development Secrets
~~~~~~~~~~~~~~~~~~~

For development, store secrets in local ``.env`` files (never commit):

.. code-block:: bash

   # .env (local development)
   DJANGO_SECRET_KEY=dev-secret-key-not-for-production
   DATABASE_URL=postgresql://dev_user:dev_password@localhost/dev_db
   YAHOO_FINANCE_API_KEY=your-development-api-key

Production Secrets
~~~~~~~~~~~~~~~~~~~

For production, use environment-specific secret management:

**Environment Variables**
   Set secrets as environment variables in your deployment platform.

**External Secret Stores**
   Use dedicated secret management services:

   .. code-block:: python

      # Using AWS Secrets Manager
      import boto3

      def get_secret(secret_name):
          client = boto3.client('secretsmanager', region_name='us-east-1')
          response = client.get_secret_value(SecretId=secret_name)
          return response['SecretString']

      # In settings
      DATABASE_PASSWORD = get_secret('personal-finance/db-password')

**Docker Secrets**
   Use Docker's built-in secrets management:

   .. code-block:: yaml

      # docker-compose.yml
      version: '3.8'
      services:
        web:
          secrets:
            - django_secret_key
            - database_password

      secrets:
        django_secret_key:
          file: ./secrets/django_secret_key.txt
        database_password:
          file: ./secrets/database_password.txt

Configuration Testing
---------------------

Automated Testing
~~~~~~~~~~~~~~~~~

**Configuration Unit Tests**

   .. code-block:: python

      # tests/test_configuration.py
      import pytest
      from django.test import TestCase, override_settings
      from django.core.exceptions import ImproperlyConfigured

      class ConfigurationTestCase(TestCase):
          \"\"\"Test configuration validation.\"\"\"

          def test_required_settings_present(self):
              \"\"\"Test that required settings are present.\"\"\"
              from django.conf import settings

              required = ['SECRET_KEY', 'DATABASES', 'INSTALLED_APPS']
              for setting in required:
                  self.assertTrue(hasattr(settings, setting))

          @override_settings(DEBUG=True, ALLOWED_HOSTS=[])
          def test_debug_mode_validation(self):
              \"\"\"Test debug mode configuration.\"\"\"
              from django.core.management import call_command

              # Should warn about empty ALLOWED_HOSTS in debug mode
              with self.assertLogs('django', level='WARNING'):
                  call_command('check')

**Integration Tests**
   Test configuration with actual services:

   .. code-block:: python

      def test_database_connection(self):
          \"\"\"Test database connectivity.\"\"\"
          from django.db import connection

          with connection.cursor() as cursor:
              cursor.execute(\"SELECT 1\")
              result = cursor.fetchone()
              self.assertEqual(result[0], 1)

      def test_cache_connection(self):
          \"\"\"Test cache connectivity.\"\"\"
          from django.core.cache import cache

          cache.set('test_key', 'test_value', 30)
          self.assertEqual(cache.get('test_key'), 'test_value')

Configuration Documentation
---------------------------

Automated Documentation Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate configuration documentation from code:

.. code-block:: python

   # management/commands/generate_config_docs.py
   from django.core.management.base import BaseCommand
   from django.conf import settings

   class Command(BaseCommand):
       help = 'Generate configuration documentation'

       def handle(self, *args, **options):
           \"\"\"Generate configuration documentation.\"\"\"
           config_vars = self._extract_config_variables()
           self._generate_rst_documentation(config_vars)

       def _extract_config_variables(self):
           \"\"\"Extract configuration variables from settings.\"\"\"
           # Implementation to scan settings files
           pass

       def _generate_rst_documentation(self, variables):
           \"\"\"Generate reStructuredText documentation.\"\"\"
           # Implementation to generate docs
           pass

Configuration Change Management
-------------------------------

Version Control for Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Configuration History**
   Track configuration changes over time:

   .. code-block:: bash

      # Track configuration in version control
      git add config/settings/
      git commit -m \"feat(config): add new market data provider settings\"

**Configuration Migrations**
   Handle configuration changes during deployments:

   .. code-block:: python

      # config/migrations/001_add_new_provider.py
      def migrate_config():
          \"\"\"Migrate configuration for new market data provider.\"\"\"
          # Implementation to handle config migration
          pass

Environment-Specific Overrides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handle environment-specific configuration cleanly:

.. code-block:: python

   # config/settings/base.py
   # Base configuration

   # config/settings/local.py
   from .base import *

   # Development overrides
   DEBUG = True
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

   # config/settings/production.py
   from .base import *

   # Production overrides
   DEBUG = False
   SECURE_SSL_REDIRECT = True

Troubleshooting Configuration
-----------------------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Environment Variables Not Loading**

   .. code-block:: bash

      # Check if .env file exists and is readable
      ls -la .env

      # Verify environment variables are set
      python -c \"import os; print(os.environ.get('DJANGO_SECRET_KEY'))\"

      # Check django-environ loading
      python manage.py shell -c \"from django.conf import settings; print(settings.SECRET_KEY)\"

**Database Connection Issues**

   .. code-block:: bash

      # Test database connectivity
      python manage.py dbshell

      # Check database settings
      python manage.py diffsettings | grep DATABASE

**Cache Configuration Problems**

   .. code-block:: bash

      # Test cache connectivity
      python manage.py shell -c \"from django.core.cache import cache; cache.set('test', 1); print(cache.get('test'))\"

**SSL/HTTPS Issues**

   .. code-block:: bash

      # Check security settings
      python manage.py check --deploy

Configuration Debugging
~~~~~~~~~~~~~~~~~~~~~~~~

**Debug Configuration Loading**

   .. code-block:: python

      # config/settings/debug.py
      import logging

      # Enable debug logging for configuration
      logging.basicConfig(level=logging.DEBUG)

      logger = logging.getLogger(__name__)
      logger.debug(f\"Loading settings from {__file__}\")

**Configuration Inspection**

   .. code-block:: bash

      # Show all settings differences from defaults
      python manage.py diffsettings

      # Show specific setting values
      python manage.py shell -c \"from django.conf import settings; print(settings.DATABASES)\"

Best Practices
--------------

Configuration Security
~~~~~~~~~~~~~~~~~~~~~~~

1. **Never commit secrets** to version control
2. **Use different secrets** for each environment
3. **Rotate secrets regularly** (especially API keys)
4. **Validate configuration** before deployment
5. **Use least-privilege access** for service accounts

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

1. **Document all settings** with purpose and default values
2. **Use environment-specific overrides** instead of separate files
3. **Validate configuration** programmatically
4. **Version control configuration** templates
5. **Test configuration changes** in staging first

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

1. **Cache configuration** where appropriate
2. **Use connection pooling** for databases
3. **Optimize background task** settings
4. **Monitor configuration impact** on performance
5. **Tune settings based on usage patterns**

See Also
--------

* :doc:`environment` - Detailed environment variable reference
* :doc:`django_settings` - Complete Django settings documentation
* :doc:`security` - Security configuration best practices
* :doc:`../deployment/docker` - Docker deployment configuration
* :doc:`../api/authentication` - API configuration details
