Django Settings Reference
========================

Complete reference for Django settings configuration.

.. contents:: Table of Contents
   :local:
   :depth: 2

Settings Structure
------------------

The Django settings are organized in a modular structure:

.. code-block:: text

   config/settings/
   ├── __init__.py          # Settings module marker
   ├── base.py              # Base settings (common to all environments)
   ├── local.py             # Local development settings
   ├── production.py        # Production settings
   └── test.py              # Test settings

Base Settings (base.py)
-----------------------

Core Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Base Django configuration
   BASE_DIR = Path(__file__).resolve().parent.parent.parent

   # Application definition
   DJANGO_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'django.contrib.sites',
   ]

   THIRD_PARTY_APPS = [
       'rest_framework',
       'rest_framework.authtoken',
       'corsheaders',
       'django_extensions',
       'channels',
       'celery',
       'django_celery_beat',
       'django_celery_results',
   ]

   LOCAL_APPS = [
       'personal_finance.analytics',
       'personal_finance.assets',
       'personal_finance.backtesting',
       'personal_finance.portfolio',
       'personal_finance.realtime',
       'personal_finance.tax',
       'personal_finance.users',
       'personal_finance.core',
   ]

   INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

Application Settings
~~~~~~~~~~~~~~~~~~~~

**SITE_ID**
   Site framework identifier.

   :Default: ``1``
   :Type: int

**ROOT_URLCONF**
   Root URL configuration module.

   :Default: ``'config.urls'``
   :Type: str

**WSGI_APPLICATION**
   WSGI application path.

   :Default: ``'config.wsgi.application'``
   :Type: str

**ASGI_APPLICATION**
   ASGI application for WebSocket support.

   :Default: ``'config.asgi.application'``
   :Type: str

Middleware Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   MIDDLEWARE = [
       'corsheaders.middleware.CorsMiddleware',
       'django.middleware.security.SecurityMiddleware',
       'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
       'django.contrib.sessions.middleware.SessionMiddleware',
       'django.middleware.common.CommonMiddleware',
       'django.middleware.csrf.CsrfViewMiddleware',
       'django.contrib.auth.middleware.AuthenticationMiddleware',
       'django.contrib.messages.middleware.MessageMiddleware',
       'django.middleware.clickjacking.XFrameOptionsMiddleware',
       'personal_finance.core.middleware.RequestLoggingMiddleware',
       'personal_finance.core.middleware.ErrorHandlingMiddleware',
   ]

Custom Middleware
~~~~~~~~~~~~~~~~~

**RequestLoggingMiddleware**
   Logs incoming requests and responses.

   :Location: ``personal_finance.core.middleware.RequestLoggingMiddleware``
   :Settings: Configured via ``LOGGING`` settings

**ErrorHandlingMiddleware**
   Handles application errors and provides consistent responses.

   :Location: ``personal_finance.core.middleware.ErrorHandlingMiddleware``
   :Settings: Uses ``DEBUG`` setting for error detail level

Template Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [BASE_DIR / 'templates'],
           'APP_DIRS': True,
           'OPTIONS': {
               'context_processors': [
                   'django.template.context_processors.debug',
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages',
                   'personal_finance.core.context_processors.site_settings',
               ],
           },
       },
   ]

Template Context Processors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**site_settings**
   Adds site-wide configuration to template context.

   :Location: ``personal_finance.core.context_processors.site_settings``
   :Variables: ``SITE_NAME``, ``SITE_VERSION``, ``ENABLE_*`` feature flags

Database Configuration
----------------------

Default Database Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Database configuration
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
           'OPTIONS': {
               'timeout': 20,
               'init_command': 'PRAGMA foreign_keys=ON;',
           }
       }
   }

   # Database connection age
   CONN_MAX_AGE = 0  # Override in production

PostgreSQL Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # PostgreSQL settings (production.py)
   import dj_database_url

   DATABASES = {
       'default': dj_database_url.config(
           default='postgresql://localhost:5432/personal_finance',
           conn_max_age=int(env('DATABASE_CONN_MAX_AGE', 300))
       )
   }

Database Connection Pooling
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**CONN_MAX_AGE**
   Database connection persistence in seconds.

   :Default: ``0`` (no persistence)
   :Production: ``300`` (5 minutes)
   :Range: ``0`` - ``3600``

**DATABASE_OPTIONS**
   Database-specific connection options.

   :SQLite: ``timeout``, ``init_command``
   :PostgreSQL: ``sslmode``, ``connect_timeout``
   :Example: ``{'timeout': 20, 'init_command': 'PRAGMA foreign_keys=ON;'}``

Cache Configuration
-------------------

Cache Framework Setup
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Cache configuration
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
           'LOCATION': 'personal-finance-cache',
           'OPTIONS': {
               'MAX_ENTRIES': 1000,
           }
       }
   }

Redis Cache Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Redis cache settings (production.py)
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': env('REDIS_URL', 'redis://localhost:6379/0'),
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
               'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
               'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
               'IGNORE_EXCEPTIONS': True,
           },
           'KEY_PREFIX': 'pf',
           'VERSION': 1,
           'TIMEOUT': 300,  # 5 minutes default
       }
   }

Cache Settings
~~~~~~~~~~~~~~

**CACHE_TTL**
   Default cache timeout in seconds.

   :Default: ``300`` (5 minutes)
   :Environment: ``CACHE_TTL``
   :Range: ``60`` - ``3600``

**CACHE_MAX_ENTRIES**
   Maximum number of cache entries.

   :Default: ``1000``
   :Environment: ``CACHE_MAX_ENTRIES``
   :Range: ``100`` - ``100000``

Session Configuration
---------------------

Session Framework Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Session configuration
   SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
   SESSION_CACHE_ALIAS = 'default'
   SESSION_COOKIE_AGE = 1209600  # 2 weeks
   SESSION_COOKIE_NAME = 'pf_sessionid'
   SESSION_SAVE_EVERY_REQUEST = False
   SESSION_EXPIRE_AT_BROWSER_CLOSE = False

Session Security
~~~~~~~~~~~~~~~~

**SESSION_COOKIE_SECURE**
   Require HTTPS for session cookies.

   :Default: ``False`` (local), ``True`` (production)
   :Environment: ``SESSION_COOKIE_SECURE``

**SESSION_COOKIE_HTTPONLY**
   Prevent JavaScript access to session cookies.

   :Default: ``True``
   :Security: Always keep enabled

**SESSION_COOKIE_SAMESITE**
   SameSite attribute for session cookies.

   :Default: ``'Lax'``
   :Options: ``'Strict'``, ``'Lax'``, ``'None'``

Static Files Configuration
--------------------------

Static Files Settings
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Static files configuration
   STATIC_URL = '/static/'
   STATIC_ROOT = BASE_DIR / 'staticfiles'

   STATICFILES_DIRS = [
       BASE_DIR / 'static',
       BASE_DIR / 'personal_finance' / 'static',
   ]

   STATICFILES_FINDERS = [
       'django.contrib.staticfiles.finders.FileSystemFinder',
       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
   ]

Static Files Storage
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Production static files storage
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

   # WhiteNoise configuration
   WHITENOISE_USE_FINDERS = True
   WHITENOISE_AUTOREFRESH = True  # Development only

Media Files Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Media files
   MEDIA_URL = '/media/'
   MEDIA_ROOT = BASE_DIR / 'media'

   # File upload settings
   FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
   DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
   DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

REST Framework Configuration
----------------------------

DRF Settings
~~~~~~~~~~~~

.. code-block:: python

   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework.authentication.TokenAuthentication',
           'rest_framework.authentication.SessionAuthentication',
       ],
       'DEFAULT_PERMISSION_CLASSES': [
           'rest_framework.permissions.IsAuthenticated',
       ],
       'DEFAULT_RENDERER_CLASSES': [
           'rest_framework.renderers.JSONRenderer',
           'rest_framework.renderers.BrowsableAPIRenderer',
       ],
       'DEFAULT_PARSER_CLASSES': [
           'rest_framework.parsers.JSONParser',
           'rest_framework.parsers.MultiPartParser',
           'rest_framework.parsers.FormParser',
       ],
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 50,
       'DEFAULT_FILTER_BACKENDS': [
           'django_filters.rest_framework.DjangoFilterBackend',
           'rest_framework.filters.SearchFilter',
           'rest_framework.filters.OrderingFilter',
       ],
       'DEFAULT_THROTTLE_CLASSES': [
           'rest_framework.throttling.AnonRateThrottle',
           'rest_framework.throttling.UserRateThrottle',
       ],
       'DEFAULT_THROTTLE_RATES': {
           'anon': '100/hour',
           'user': '1000/hour',
           'login': '5/min',
       },
       'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
       'DEFAULT_VERSION': 'v1',
       'ALLOWED_VERSIONS': ['v1'],
   }

API Authentication Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Token Authentication**
   Token-based API authentication.

   :Tokens: Auto-generated for users
   :Header: ``Authorization: Token <token>``
   :Expiry: Configurable via ``API_TOKEN_EXPIRY_HOURS``

**Session Authentication**
   Browser session-based authentication.

   :Use Case: Web interface API calls
   :CSRF: Required for write operations

API Rate Limiting
~~~~~~~~~~~~~~~~~

**DEFAULT_THROTTLE_RATES**
   Rate limits for different user types.

   :Anonymous: ``100/hour``
   :Authenticated: ``1000/hour``
   :Login: ``5/min``
   :Environment: Override via ``API_RATE_LIMIT_*`` variables

CORS Configuration
------------------

Cross-Origin Resource Sharing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # CORS settings
   CORS_ALLOWED_ORIGINS = [
       'http://localhost:3000',  # React dev server
       'http://127.0.0.1:3000',
   ]

   CORS_ALLOWED_ORIGIN_REGEXES = [
       r"^https://.*\.vercel\.app$",  # Vercel deployments
       r"^https://.*\.netlify\.app$", # Netlify deployments
   ]

   CORS_ALLOW_CREDENTIALS = True

   CORS_ALLOWED_HEADERS = [
       'accept',
       'accept-encoding',
       'authorization',
       'content-type',
       'dnt',
       'origin',
       'user-agent',
       'x-csrftoken',
       'x-requested-with',
   ]

CORS Settings
~~~~~~~~~~~~~

**CORS_ALLOW_ALL_ORIGINS**
   Allow all origins (development only).

   :Default: ``False``
   :Development: ``True``
   :Production: ``False``

**CORS_ALLOW_CREDENTIALS**
   Allow credentials in CORS requests.

   :Default: ``True``
   :Required: For session authentication

Celery Configuration
--------------------

Celery Settings
~~~~~~~~~~~~~~~

.. code-block:: python

   # Celery configuration
   CELERY_BROKER_URL = env('CELERY_BROKER_URL', 'redis://localhost:6379/1')
   CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')

   CELERY_ACCEPT_CONTENT = ['json']
   CELERY_TASK_SERIALIZER = 'json'
   CELERY_RESULT_SERIALIZER = 'json'
   CELERY_TIMEZONE = TIME_ZONE

   # Task routing
   CELERY_TASK_ROUTES = {
       'personal_finance.analytics.tasks.*': {'queue': 'analytics'},
       'personal_finance.backtesting.tasks.*': {'queue': 'backtesting'},
       'personal_finance.realtime.tasks.*': {'queue': 'realtime'},
   }

   # Task execution settings
   CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', False)
   CELERY_TASK_EAGER_PROPAGATES = True
   CELERY_WORKER_PREFETCH_MULTIPLIER = 1
   CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
   CELERY_TASK_TIME_LIMIT = 600       # 10 minutes

Celery Beat (Scheduling)
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Celery Beat scheduler settings
   CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

   # Periodic tasks
   CELERY_BEAT_SCHEDULE = {
       'update-market-data': {
           'task': 'personal_finance.realtime.tasks.update_market_data',
           'schedule': 300.0,  # Every 5 minutes during market hours
       },
       'generate-daily-reports': {
           'task': 'personal_finance.analytics.tasks.generate_daily_reports',
           'schedule': crontab(hour=0, minute=0),  # Daily at midnight
       },
       'cleanup-old-logs': {
           'task': 'personal_finance.core.tasks.cleanup_old_logs',
           'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Weekly
       },
   }

Task Configuration
~~~~~~~~~~~~~~~~~~

**CELERY_TASK_SOFT_TIME_LIMIT**
   Soft timeout for tasks in seconds.

   :Default: ``300`` (5 minutes)
   :Range: ``60`` - ``3600``

**CELERY_TASK_TIME_LIMIT**
   Hard timeout for tasks in seconds.

   :Default: ``600`` (10 minutes)
   :Range: ``120`` - ``7200``

**CELERY_WORKER_CONCURRENCY**
   Number of worker processes.

   :Default: CPU count
   :Environment: ``CELERY_WORKER_CONCURRENCY``

Channels Configuration
----------------------

WebSocket Settings
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Channels configuration
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               'hosts': [env('REDIS_URL', 'redis://localhost:6379/3')],
               'capacity': 1500,
               'expiry': 60,
           },
       },
   }

WebSocket Routing
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # WebSocket URL routing (config/websocket.py)
   from django.urls import path
   from personal_finance.realtime.consumers import (
       PriceUpdateConsumer,
       PortfolioConsumer,
       NotificationConsumer,
   )

   websocket_urlpatterns = [
       path('ws/prices/', PriceUpdateConsumer.as_asgi()),
       path('ws/portfolio/', PortfolioConsumer.as_asgi()),
       path('ws/notifications/', NotificationConsumer.as_asgi()),
   ]

Channels Settings
~~~~~~~~~~~~~~~~~

**CHANNEL_CAPACITY**
   Maximum messages per channel.

   :Default: ``1500``
   :Range: ``100`` - ``10000``

**CHANNEL_EXPIRY**
   Message expiry time in seconds.

   :Default: ``60``
   :Range: ``10`` - ``300``

Logging Configuration
---------------------

Logging Setup
~~~~~~~~~~~~~

.. code-block:: python

   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
               'style': '{',
           },
           'simple': {
               'format': '{levelname} {message}',
               'style': '{',
           },
           'json': {
               '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
               'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
           },
       },
       'handlers': {
           'console': {
               'class': 'logging.StreamHandler',
               'formatter': 'simple',
           },
           'file': {
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': BASE_DIR / 'logs' / 'django.log',
               'maxBytes': 10485760,  # 10MB
               'backupCount': 5,
               'formatter': 'verbose',
           },
           'celery': {
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': BASE_DIR / 'logs' / 'celery.log',
               'maxBytes': 10485760,
               'backupCount': 3,
               'formatter': 'verbose',
           },
       },
       'root': {
           'level': 'INFO',
           'handlers': ['console', 'file'],
       },
       'loggers': {
           'django': {
               'handlers': ['console', 'file'],
               'level': env('DJANGO_LOG_LEVEL', 'INFO'),
               'propagate': False,
           },
           'personal_finance': {
               'handlers': ['console', 'file'],
               'level': env('APPLICATION_LOG_LEVEL', 'INFO'),
               'propagate': False,
           },
           'celery': {
               'handlers': ['celery'],
               'level': env('CELERY_LOG_LEVEL', 'INFO'),
               'propagate': False,
           },
       },
   }

Log Levels and Handlers
~~~~~~~~~~~~~~~~~~~~~~~

**Log Levels**
   Standard Python logging levels.

   :DEBUG: Detailed diagnostic information
   :INFO: General information messages
   :WARNING: Something unexpected happened
   :ERROR: Serious problem occurred
   :CRITICAL: Very serious error occurred

**File Rotation**
   Automatic log file rotation settings.

   :Max Size: ``10MB`` per file
   :Backup Count: ``5`` files
   :Location: ``logs/`` directory

Security Settings
-----------------

Security Headers
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Security settings
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   SECURE_HSTS_SECONDS = 31536000  # 1 year
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_HSTS_PRELOAD = True

   X_FRAME_OPTIONS = 'DENY'

   # Content Security Policy
   CSP_DEFAULT_SRC = ("'self'",)
   CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "cdnjs.cloudflare.com")
   CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "fonts.googleapis.com")
   CSP_FONT_SRC = ("'self'", "fonts.gstatic.com")
   CSP_IMG_SRC = ("'self'", "data:")

CSRF Protection
~~~~~~~~~~~~~~~

**CSRF_COOKIE_SECURE**
   Require HTTPS for CSRF cookies.

   :Default: ``False`` (local), ``True`` (production)

**CSRF_COOKIE_SAMESITE**
   SameSite attribute for CSRF cookies.

   :Default: ``'Lax'``
   :Options: ``'Strict'``, ``'Lax'``

**CSRF_TRUSTED_ORIGINS**
   Trusted origins for CSRF protection.

   :Example: ``['https://yourfinance.com']``

Password Validation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   AUTH_PASSWORD_VALIDATORS = [
       {
           'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
       },
       {
           'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
           'OPTIONS': {'min_length': 8},
       },
       {
           'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
       },
       {
           'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
       },
   ]

Internationalization
--------------------

I18n Settings
~~~~~~~~~~~~~

.. code-block:: python

   # Internationalization
   LANGUAGE_CODE = 'en-us'
   TIME_ZONE = 'UTC'
   USE_I18N = True
   USE_L10N = True
   USE_TZ = True

   # Available languages
   LANGUAGES = [
       ('en', 'English'),
       ('pt-br', 'Portuguese (Brazil)'),
       ('es', 'Spanish'),
   ]

   # Locale paths
   LOCALE_PATHS = [
       BASE_DIR / 'locale',
   ]

Timezone Configuration
~~~~~~~~~~~~~~~~~~~~~~

**TIME_ZONE**
   Default timezone for the application.

   :Default: ``'UTC'``
   :Options: Any timezone from ``pytz.all_timezones``
   :Example: ``'America/New_York'``, ``'Europe/London'``

**USE_TZ**
   Enable timezone support.

   :Default: ``True``
   :Recommendation: Always keep enabled

Environment-Specific Settings
-----------------------------

Local Development (local.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from .base import *
   import os

   # Development-specific settings
   DEBUG = True
   SECRET_KEY = env('DJANGO_SECRET_KEY', 'dev-secret-not-for-production')

   ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

   # Database - SQLite for development
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }

   # Email backend for development
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

   # CORS - Allow all origins in development
   CORS_ALLOW_ALL_ORIGINS = True

   # Disable caching in development
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
       }
   }

   # Django Debug Toolbar
   if DEBUG:
       INSTALLED_APPS += ['debug_toolbar']
       MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
       INTERNAL_IPS = ['127.0.0.1']

Production (production.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from .base import *
   import dj_database_url

   # Production settings
   DEBUG = False
   SECRET_KEY = env('DJANGO_SECRET_KEY')
   ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

   # Database - PostgreSQL
   DATABASES = {
       'default': dj_database_url.config(
           conn_max_age=env.int('DATABASE_CONN_MAX_AGE', 300)
       )
   }

   # Security settings
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

   # Static files - WhiteNoise with compression
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

   # Email - Production SMTP
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = env('EMAIL_HOST')
   EMAIL_PORT = env.int('EMAIL_PORT', 587)
   EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
   EMAIL_HOST_USER = env('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

   # Logging - JSON format for production
   LOGGING['formatters']['production'] = {
       '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
       'format': '%(levelname)s %(asctime)s %(name)s %(message)s'
   }

Test Settings (test.py)
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from .base import *

   # Test-specific settings
   DEBUG = False
   SECRET_KEY = 'test-secret-key-not-for-production'

   # In-memory database for tests
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': ':memory:',
       }
   }

   # Disable migrations for faster tests
   class DisableMigrations:
       def __contains__(self, item):
           return True
       def __getitem__(self, item):
           return None

   MIGRATION_MODULES = DisableMigrations()

   # Fast password hasher for tests
   PASSWORD_HASHERS = [
       'django.contrib.auth.hashers.MD5PasswordHasher',
   ]

   # Disable caching in tests
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
       }
   }

   # Eager task execution for tests
   CELERY_TASK_ALWAYS_EAGER = True
   CELERY_TASK_EAGER_PROPAGATES = True

   # Disable real email sending in tests
   EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

Custom Settings
---------------

Application-Specific Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Personal Finance specific settings

   # Feature flags
   ENABLE_BACKTESTING = env.bool('ENABLE_BACKTESTING', True)
   ENABLE_REALTIME_UPDATES = env.bool('ENABLE_REALTIME_UPDATES', True)
   ENABLE_TAX_CALCULATIONS = env.bool('ENABLE_TAX_CALCULATIONS', True)
   ENABLE_DATA_PROFILING = env.bool('ENABLE_DATA_PROFILING', True)
   ENABLE_ADVANCED_ANALYTICS = env.bool('ENABLE_ADVANCED_ANALYTICS', False)

   # Market data settings
   MARKET_DATA_PROVIDER = env('MARKET_DATA_PROVIDER', 'yahoo_finance')
   YAHOO_FINANCE_API_KEY = env('YAHOO_FINANCE_API_KEY', None)
   ALPHA_VANTAGE_API_KEY = env('ALPHA_VANTAGE_API_KEY', None)

   # Backtesting settings
   BACKTESTING_MAX_LOOKBACK_YEARS = env.int('BACKTESTING_MAX_LOOKBACK_YEARS', 10)
   BACKTESTING_DEFAULT_COMMISSION = env.float('BACKTESTING_DEFAULT_COMMISSION', 0.001)

   # Real-time update settings
   REALTIME_UPDATE_INTERVAL = env.int('REALTIME_UPDATE_INTERVAL', 30)
   REALTIME_BATCH_SIZE = env.int('REALTIME_BATCH_SIZE', 50)

   # Performance settings
   DATABASE_POOL_SIZE = env.int('DATABASE_POOL_SIZE', 5)
   CACHE_DEFAULT_TIMEOUT = env.int('CACHE_DEFAULT_TIMEOUT', 300)

Portfolio Settings
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Portfolio management settings
   PORTFOLIO_MAX_POSITIONS = env.int('PORTFOLIO_MAX_POSITIONS', 1000)
   PORTFOLIO_REBALANCE_THRESHOLD = env.float('PORTFOLIO_REBALANCE_THRESHOLD', 0.05)
   PORTFOLIO_CURRENCY_DEFAULT = env('PORTFOLIO_CURRENCY_DEFAULT', 'USD')

   # Risk management
   RISK_MAX_POSITION_SIZE = env.float('RISK_MAX_POSITION_SIZE', 0.1)  # 10% max
   RISK_MAX_SECTOR_ALLOCATION = env.float('RISK_MAX_SECTOR_ALLOCATION', 0.25)  # 25% max

Analytics Settings
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Analytics configuration
   ANALYTICS_LOOKBACK_PERIODS = {
       'short': 30,   # 30 days
       'medium': 90,  # 3 months
       'long': 365,   # 1 year
   }

   ANALYTICS_BENCHMARK_SYMBOLS = ['SPY', 'QQQ', 'IWM']  # Default benchmarks
   ANALYTICS_RISK_FREE_RATE = env.float('ANALYTICS_RISK_FREE_RATE', 0.02)  # 2%

Tax Calculation Settings
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Tax calculation settings
   TAX_YEAR_START_MONTH = 1  # January
   TAX_LONG_TERM_THRESHOLD_DAYS = 365
   TAX_WASH_SALE_PERIOD_DAYS = 30

   # Default tax rates (can be overridden per user)
   TAX_RATES_DEFAULT = {
       'short_term': 0.22,  # 22%
       'long_term': 0.15,   # 15%
       'qualified_dividend': 0.15,  # 15%
   }

Settings Validation
-------------------

Configuration Validation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # settings/validation.py
   import os
   from django.core.exceptions import ImproperlyConfigured

   def validate_production_settings():
       \"\"\"Validate production-specific settings.\"\"\"
       required_vars = [
           'DJANGO_SECRET_KEY',
           'DATABASE_URL',
           'REDIS_URL',
           'EMAIL_HOST',
           'EMAIL_HOST_USER',
           'EMAIL_HOST_PASSWORD',
       ]

       for var in required_vars:
           if not os.environ.get(var):
               raise ImproperlyConfigured(f\"Missing required environment variable: {var}\")

       # Validate security settings
       if not os.environ.get('DJANGO_ALLOWED_HOSTS'):
           raise ImproperlyConfigured(\"DJANGO_ALLOWED_HOSTS must be set in production\")

   def validate_api_keys():
       \"\"\"Validate external API configuration.\"\"\"
       if not any([
           os.environ.get('YAHOO_FINANCE_API_KEY'),
           os.environ.get('ALPHA_VANTAGE_API_KEY'),
       ]):
           import warnings
           warnings.warn(\"No market data API keys configured. Using free tier limits.\")

Custom Settings Commands
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # management/commands/check_config.py
   from django.core.management.base import BaseCommand
   from django.conf import settings
   from django.core.checks import run_checks

   class Command(BaseCommand):
       help = \"Check application configuration\"

       def add_arguments(self, parser):
           parser.add_argument(
               '--env',
               choices=['local', 'production', 'test'],
               help='Check specific environment configuration',
           )

       def handle(self, *args, **options):
           # Run Django system checks
           errors = run_checks()

           if errors:
               self.stdout.write(
                   self.style.ERROR(f\"Found {len(errors)} configuration errors:\")
               )
               for error in errors:
                   self.stdout.write(self.style.ERROR(f\"  {error}\"))
           else:
               self.stdout.write(
                   self.style.SUCCESS(\"All configuration checks passed!\")
               )

           # Custom validation
           self.check_custom_settings()

       def check_custom_settings(self):
           \"\"\"Check custom application settings.\"\"\"
           # Check feature flags consistency
           if settings.ENABLE_REALTIME_UPDATES and not settings.REDIS_URL:
               self.stdout.write(
                   self.style.WARNING(\"Real-time updates enabled but Redis not configured\")
               )

           # Check API key configuration
           if settings.ENABLE_BACKTESTING and not any([
               settings.YAHOO_FINANCE_API_KEY,
               settings.ALPHA_VANTAGE_API_KEY,
           ]):
               self.stdout.write(
                   self.style.WARNING(\"Backtesting enabled but no market data API keys configured\")
               )

See Also
--------

* :doc:`environment` - Environment variables reference
* :doc:`security` - Security configuration details
* :doc:`../api/authentication` - API authentication configuration
* :doc:`../deployment/production` - Production deployment settings
