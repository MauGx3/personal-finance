Security Configuration
=====================

Comprehensive security configuration reference for production deployment.

.. contents:: Table of Contents
   :local:
   :depth: 2

Security Overview
-----------------

The Personal Finance Platform implements defense-in-depth security with multiple layers of protection:

1. **Application Security** - Django security features and custom middleware
2. **Infrastructure Security** - HTTPS, headers, and network protection
3. **Data Protection** - Encryption, access controls, and audit logging
4. **API Security** - Authentication, rate limiting, and input validation
5. **Deployment Security** - Container security and environment isolation

Django Security Settings
-------------------------

Core Security Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Security settings in config/settings/production.py

   # Secret key management
   SECRET_KEY = env('DJANGO_SECRET_KEY')  # Never hardcode!

   # Debug mode (must be False in production)
   DEBUG = False

   # Allowed hosts (specific domains only)
   ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])

   # Trusted origins for CSRF protection
   CSRF_TRUSTED_ORIGINS = [
       'https://yourfinance.com',
       'https://api.yourfinance.com',
   ]

HTTPS and SSL Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # SSL/TLS enforcement
   SECURE_SSL_REDIRECT = True
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

   # HSTS (HTTP Strict Transport Security)
   SECURE_HSTS_SECONDS = 31536000  # 1 year
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_HSTS_PRELOAD = True

   # Secure cookies
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SESSION_COOKIE_HTTPONLY = True
   CSRF_COOKIE_HTTPONLY = True

   # Cookie SameSite protection
   SESSION_COOKIE_SAMESITE = 'Lax'
   CSRF_COOKIE_SAMESITE = 'Lax'

Security Headers
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Browser security headers
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

   # Frame protection
   X_FRAME_OPTIONS = 'DENY'

   # Content Security Policy
   CSP_DEFAULT_SRC = ("'self'",)
   CSP_SCRIPT_SRC = (
       "'self'",
       "'unsafe-inline'",  # Required for Django admin
       "cdnjs.cloudflare.com",
       "cdn.jsdelivr.net",
   )
   CSP_STYLE_SRC = (
       "'self'",
       "'unsafe-inline'",
       "fonts.googleapis.com",
       "cdnjs.cloudflare.com",
   )
   CSP_FONT_SRC = (
       "'self'",
       "fonts.gstatic.com",
       "cdnjs.cloudflare.com",
   )
   CSP_IMG_SRC = (
       "'self'",
       "data:",
       "https:",  # Allow external images from HTTPS sources
   )
   CSP_CONNECT_SRC = (
       "'self'",
       "wss:",  # WebSocket connections
       "https://api.finance.yahoo.com",  # Market data APIs
       "https://www.alphavantage.co",
   )

Authentication Security
-----------------------

Password Security
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Strong password validation
   AUTH_PASSWORD_VALIDATORS = [
       {
           'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
       },
       {
           'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
           'OPTIONS': {'min_length': 12},  # Increased from default 8
       },
       {
           'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
       },
       {
           'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
       },
       {
           'NAME': 'personal_finance.core.validators.CustomPasswordValidator',
           'OPTIONS': {
               'require_uppercase': True,
               'require_lowercase': True,
               'require_numbers': True,
               'require_symbols': True,
           },
       },
   ]

Custom Password Validator
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/core/validators.py
   import re
   from django.core.exceptions import ValidationError
   from django.utils.translation import gettext as _

   class CustomPasswordValidator:
       \"\"\"Custom password validator with additional security requirements.\"\"\"

       def __init__(self, require_uppercase=True, require_lowercase=True,
                    require_numbers=True, require_symbols=True):
           self.require_uppercase = require_uppercase
           self.require_lowercase = require_lowercase
           self.require_numbers = require_numbers
           self.require_symbols = require_symbols

       def validate(self, password, user=None):
           errors = []

           if self.require_uppercase and not re.search(r'[A-Z]', password):
               errors.append(_('Password must contain at least one uppercase letter.'))

           if self.require_lowercase and not re.search(r'[a-z]', password):
               errors.append(_('Password must contain at least one lowercase letter.'))

           if self.require_numbers and not re.search(r'[0-9]', password):
               errors.append(_('Password must contain at least one number.'))

           if self.require_symbols and not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
               errors.append(_('Password must contain at least one symbol.'))

           if errors:
               raise ValidationError(errors)

       def get_help_text(self):
           return _(
               'Password must contain uppercase letters, lowercase letters, '
               'numbers, and symbols.'
           )

Session Security
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Session security settings
   SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
   SESSION_CACHE_ALIAS = 'default'
   SESSION_COOKIE_AGE = 3600  # 1 hour (shorter for financial apps)
   SESSION_COOKIE_NAME = 'pf_sessionid'
   SESSION_SAVE_EVERY_REQUEST = True  # Update expiry on each request
   SESSION_EXPIRE_AT_BROWSER_CLOSE = True

   # Session security middleware
   MIDDLEWARE += [
       'personal_finance.core.middleware.SessionSecurityMiddleware',
   ]

Session Security Middleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/core/middleware.py
   import time
   from django.contrib.auth import logout
   from django.shortcuts import redirect
   from django.urls import reverse

   class SessionSecurityMiddleware:
       \"\"\"Enhanced session security middleware.\"\"\"

       def __init__(self, get_response):
           self.get_response = get_response

       def __call__(self, request):
           if request.user.is_authenticated:
               # Check for session hijacking
               if self._is_session_hijacked(request):
                   logout(request)
                   return redirect(reverse('login'))

               # Update last activity
               request.session['last_activity'] = time.time()

               # Store security fingerprint
               self._update_security_fingerprint(request)

           response = self.get_response(request)
           return response

       def _is_session_hijacked(self, request):
           \"\"\"Check for potential session hijacking.\"\"\"
           current_ip = self._get_client_ip(request)
           current_ua = request.META.get('HTTP_USER_AGENT', '')

           # Check if IP has changed (basic check)
           session_ip = request.session.get('session_ip')
           if session_ip and session_ip != current_ip:
               return True

           # Check if user agent has changed significantly
           session_ua = request.session.get('session_ua')
           if session_ua and self._ua_changed_significantly(session_ua, current_ua):
               return True

           return False

       def _get_client_ip(self, request):
           \"\"\"Get client IP address.\"\"\"
           x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
           if x_forwarded_for:
               return x_forwarded_for.split(',')[0].strip()
           return request.META.get('REMOTE_ADDR')

       def _update_security_fingerprint(self, request):
           \"\"\"Update session security fingerprint.\"\"\"
           request.session['session_ip'] = self._get_client_ip(request)
           request.session['session_ua'] = request.META.get('HTTP_USER_AGENT', '')

API Security
------------

Token Authentication
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # API authentication settings
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework.authentication.TokenAuthentication',
           'personal_finance.core.authentication.SecureTokenAuthentication',
       ],
       'DEFAULT_PERMISSION_CLASSES': [
           'rest_framework.permissions.IsAuthenticated',
       ],
       'DEFAULT_THROTTLE_CLASSES': [
           'personal_finance.core.throttling.BurstRateThrottle',
           'personal_finance.core.throttling.SustainedRateThrottle',
       ],
       'DEFAULT_THROTTLE_RATES': {
           'burst': '20/min',      # 20 requests per minute
           'sustained': '1000/day', # 1000 requests per day
           'login': '5/min',       # Login attempts
           'sensitive': '10/hour', # Sensitive operations
       },
   }

Secure Token Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/core/authentication.py
   import hashlib
   import hmac
   from django.contrib.auth.models import AnonymousUser
   from rest_framework.authentication import TokenAuthentication
   from rest_framework.exceptions import AuthenticationFailed

   class SecureTokenAuthentication(TokenAuthentication):
       \"\"\"Enhanced token authentication with additional security.\"\"\"

       def authenticate_credentials(self, key):
           model = self.get_model()
           try:
               token = model.objects.select_related('user').get(key=key)
           except model.DoesNotExist:
               raise AuthenticationFailed('Invalid token.')

           if not token.user.is_active:
               raise AuthenticationFailed('User inactive or deleted.')

           # Check token expiry
           if self._is_token_expired(token):
               token.delete()  # Remove expired token
               raise AuthenticationFailed('Token expired.')

           # Log token usage
           self._log_token_usage(token)

           return (token.user, token)

       def _is_token_expired(self, token):
           \"\"\"Check if token has expired.\"\"\"
           from django.utils import timezone
           from datetime import timedelta

           expiry_hours = getattr(settings, 'API_TOKEN_EXPIRY_HOURS', 24)
           expiry_time = token.created + timedelta(hours=expiry_hours)
           return timezone.now() > expiry_time

       def _log_token_usage(self, token):
           \"\"\"Log API token usage for audit purposes.\"\"\"
           import logging
           logger = logging.getLogger('personal_finance.security')

           logger.info(
               'API token used',
               extra={
                   'user_id': token.user.id,
                   'token_key': token.key[:8] + '...',  # Partial key for identification
                   'timestamp': timezone.now().isoformat(),
               }
           )

Rate Limiting and Throttling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/core/throttling.py
   from rest_framework.throttling import UserRateThrottle
   from django.core.cache import cache
   import hashlib

   class BurstRateThrottle(UserRateThrottle):
       \"\"\"Short-term burst rate limiting.\"\"\"
       scope = 'burst'

       def get_cache_key(self, request, view):
           if request.user and request.user.is_authenticated:
               ident = request.user.pk
           else:
               ident = self.get_ident(request)

           return self.cache_format % {
               'scope': self.scope,
               'ident': ident
           }

   class SustainedRateThrottle(UserRateThrottle):
       \"\"\"Long-term sustained rate limiting.\"\"\"
       scope = 'sustained'

   class SensitiveOperationThrottle(UserRateThrottle):
       \"\"\"Rate limiting for sensitive operations.\"\"\"
       scope = 'sensitive'

       def allow_request(self, request, view):
           # Additional checks for sensitive operations
           if self._is_suspicious_request(request):
               return False

           return super().allow_request(request, view)

       def _is_suspicious_request(self, request):
           \"\"\"Check for suspicious request patterns.\"\"\"
           # Check for rapid fire requests from same IP
           client_ip = self._get_client_ip(request)
           cache_key = f'suspicious_ip:{client_ip}'

           request_count = cache.get(cache_key, 0)
           if request_count > 100:  # More than 100 requests in cache period
               return True

           cache.set(cache_key, request_count + 1, 300)  # 5 minute window
           return False

Input Validation and Sanitization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/core/validators.py
   import re
   from decimal import Decimal, InvalidOperation
   from django.core.exceptions import ValidationError
   from django.utils.translation import gettext as _

   class SecurityValidator:
       \"\"\"Security-focused input validation.\"\"\"

       @staticmethod
       def validate_symbol(symbol):
           \"\"\"Validate stock/asset symbols.\"\"\"
           if not symbol or len(symbol) > 10:
               raise ValidationError(_('Invalid symbol format.'))

           # Only allow alphanumeric characters and dots
           if not re.match(r'^[A-Z0-9.]+$', symbol.upper()):
               raise ValidationError(_('Symbol contains invalid characters.'))

           return symbol.upper()

       @staticmethod
       def validate_monetary_amount(amount):
           \"\"\"Validate monetary amounts.\"\"\"
           try:
               decimal_amount = Decimal(str(amount))
               if decimal_amount < 0:
                   raise ValidationError(_('Amount cannot be negative.'))
               if decimal_amount > Decimal('999999999.99'):
                   raise ValidationError(_('Amount too large.'))
               return decimal_amount
           except (ValueError, InvalidOperation):
               raise ValidationError(_('Invalid amount format.'))

       @staticmethod
       def validate_date_range(start_date, end_date):
           \"\"\"Validate date ranges.\"\"\"
           from datetime import date, timedelta

           if start_date > end_date:
               raise ValidationError(_('Start date must be before end date.'))

           # Prevent excessively long date ranges (DoS protection)
           max_range = timedelta(days=365 * 10)  # 10 years max
           if (end_date - start_date) > max_range:
               raise ValidationError(_('Date range too large.'))

           # Prevent future dates for historical data
           if end_date > date.today():
               raise ValidationError(_('End date cannot be in the future.'))

Data Protection
---------------

Database Security
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Database security settings
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': env('DATABASE_NAME'),
           'USER': env('DATABASE_USER'),
           'PASSWORD': env('DATABASE_PASSWORD'),
           'HOST': env('DATABASE_HOST'),
           'PORT': env('DATABASE_PORT', '5432'),
           'OPTIONS': {
               'sslmode': 'require',  # Require SSL connection
               'sslcert': '/path/to/client-cert.pem',
               'sslkey': '/path/to/client-key.pem',
               'sslrootcert': '/path/to/ca-cert.pem',
           },
           'CONN_MAX_AGE': 300,
           'CONN_HEALTH_CHECKS': True,
       }
   }

   # Database connection pooling
   DATABASE_POOL_CLASS = 'django_postgrespool2.pool.DatabasePool'
   DATABASE_POOL_ARGS = {
       'max_overflow': 0,
       'pool_size': 5,
       'recycle': -1
   }

Field-Level Encryption
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/core/fields.py
   from cryptography.fernet import Fernet
   from django.db import models
   from django.conf import settings
   import base64

   class EncryptedField(models.CharField):
       \"\"\"Field that automatically encrypts/decrypts sensitive data.\"\"\"

       def __init__(self, *args, **kwargs):
           self.encryption_key = self._get_encryption_key()
           super().__init__(*args, **kwargs)

       def _get_encryption_key(self):
           \"\"\"Get encryption key from settings.\"\"\"
           key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
           if not key:
               raise ValueError('FIELD_ENCRYPTION_KEY must be set in settings')
           return Fernet(key.encode())

       def from_db_value(self, value, expression, connection):
           if value is None:
               return value

           try:
               # Decrypt the value
               decrypted = self.encryption_key.decrypt(value.encode())
               return decrypted.decode()
           except Exception:
               # Return as-is if decryption fails (for migration compatibility)
               return value

       def to_python(self, value):
           return value

       def get_prep_value(self, value):
           if value is None:
               return value

           # Encrypt the value
           encrypted = self.encryption_key.encrypt(value.encode())
           return encrypted.decode()

   class EncryptedJSONField(models.JSONField):
       \"\"\"JSON field with encryption for sensitive structured data.\"\"\"

       def __init__(self, *args, **kwargs):
           self.encryption_key = self._get_encryption_key()
           super().__init__(*args, **kwargs)

       def _get_encryption_key(self):
           key = getattr(settings, 'FIELD_ENCRYPTION_KEY', None)
           if not key:
               raise ValueError('FIELD_ENCRYPTION_KEY must be set in settings')
           return Fernet(key.encode())

       def from_db_value(self, value, expression, connection):
           if value is None:
               return value

           try:
               # Decrypt then parse JSON
               decrypted = self.encryption_key.decrypt(value.encode())
               return json.loads(decrypted.decode())
           except Exception:
               # Fallback to regular JSON parsing
               return json.loads(value)

       def get_prep_value(self, value):
           if value is None:
               return value

           # Serialize to JSON then encrypt
           json_str = json.dumps(value)
           encrypted = self.encryption_key.encrypt(json_str.encode())
           return encrypted.decode()

Sensitive Data Logging
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/core/logging.py
   import logging
   import re
   from typing import Any, Dict

   class SensitiveDataFilter(logging.Filter):
       \"\"\"Filter sensitive data from logs.\"\"\"

       # Patterns to redact
       SENSITIVE_PATTERNS = [
           (re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'\\s]+)', re.IGNORECASE), r'\\1[REDACTED]'),
           (re.compile(r'(token["\']?\s*[:=]\s*["\']?)([^"\'\\s]+)', re.IGNORECASE), r'\\1[REDACTED]'),
           (re.compile(r'(api_?key["\']?\s*[:=]\s*["\']?)([^"\'\\s]+)', re.IGNORECASE), r'\\1[REDACTED]'),
           (re.compile(r'(secret["\']?\s*[:=]\s*["\']?)([^"\'\\s]+)', re.IGNORECASE), r'\\1[REDACTED]'),
           (re.compile(r'\\b\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}\\b'), '[CREDIT_CARD_REDACTED]'),  # Credit cards
           (re.compile(r'\\b\\d{3}-?\\d{2}-?\\d{4}\\b'), '[SSN_REDACTED]'),  # SSN
           (re.compile(r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'), '[EMAIL_REDACTED]'),  # Email
       ]

       def filter(self, record: logging.LogRecord) -> bool:
           \"\"\"Filter sensitive information from log records.\"\"\"
           # Redact sensitive data from message
           if hasattr(record, 'msg') and isinstance(record.msg, str):
               record.msg = self._redact_sensitive_data(record.msg)

           # Redact sensitive data from args
           if hasattr(record, 'args') and record.args:
               record.args = tuple(
                   self._redact_if_string(arg) for arg in record.args
               )

           return True

       def _redact_sensitive_data(self, data: str) -> str:
           \"\"\"Apply redaction patterns to string data.\"\"\"
           result = data
           for pattern, replacement in self.SENSITIVE_PATTERNS:
               result = pattern.sub(replacement, result)
           return result

       def _redact_if_string(self, value: Any) -> Any:
           \"\"\"Redact value if it's a string, otherwise return as-is.\"\"\"
           if isinstance(value, str):
               return self._redact_sensitive_data(value)
           return value

Access Control and Audit
-------------------------

Permission-Based Access Control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/core/permissions.py
   from rest_framework import permissions
   from django.contrib.auth.models import Permission

   class IsOwnerOrReadOnly(permissions.BasePermission):
       \"\"\"Custom permission to only allow owners to edit objects.\"\"\"

       def has_object_permission(self, request, view, obj):
           # Read permissions for any request
           if request.method in permissions.SAFE_METHODS:
               return True

           # Write permissions only to the owner
           return obj.user == request.user

   class PortfolioPermission(permissions.BasePermission):
       \"\"\"Permission for portfolio access.\"\"\"

       def has_permission(self, request, view):
           # Must be authenticated
           if not request.user or not request.user.is_authenticated:
               return False

           # Check specific permissions
           if request.method == 'POST':
               return request.user.has_perm('portfolio.add_portfolio')
           elif request.method in ['PUT', 'PATCH']:
               return request.user.has_perm('portfolio.change_portfolio')
           elif request.method == 'DELETE':
               return request.user.has_perm('portfolio.delete_portfolio')

           return True

       def has_object_permission(self, request, view, obj):
           # Users can only access their own portfolios
           return obj.user == request.user

Audit Logging
~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/core/audit.py
   import logging
   from django.contrib.auth.signals import user_logged_in, user_logged_out
   from django.db.models.signals import post_save, post_delete
   from django.dispatch import receiver

   audit_logger = logging.getLogger('personal_finance.audit')

   class AuditMixin:
       \"\"\"Mixin to add audit logging to views.\"\"\"

       def perform_create(self, serializer):
           instance = serializer.save()
           audit_logger.info(
               f'Created {instance.__class__.__name__}',
               extra={
                   'user_id': self.request.user.id,
                   'action': 'CREATE',
                   'model': instance.__class__.__name__,
                   'object_id': instance.pk,
                   'ip_address': self._get_client_ip(),
               }
           )

       def perform_update(self, serializer):
           instance = serializer.save()
           audit_logger.info(
               f'Updated {instance.__class__.__name__}',
               extra={
                   'user_id': self.request.user.id,
                   'action': 'UPDATE',
                   'model': instance.__class__.__name__,
                   'object_id': instance.pk,
                   'ip_address': self._get_client_ip(),
               }
           )

       def perform_destroy(self, instance):
           audit_logger.info(
               f'Deleted {instance.__class__.__name__}',
               extra={
                   'user_id': self.request.user.id,
                   'action': 'DELETE',
                   'model': instance.__class__.__name__,
                   'object_id': instance.pk,
                   'ip_address': self._get_client_ip(),
               }
           )
           instance.delete()

       def _get_client_ip(self):
           x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
           if x_forwarded_for:
               return x_forwarded_for.split(',')[0].strip()
           return self.request.META.get('REMOTE_ADDR')

   @receiver(user_logged_in)
   def log_user_login(sender, request, user, **kwargs):
       audit_logger.info(
           'User logged in',
           extra={
               'user_id': user.id,
               'username': user.username,
               'ip_address': request.META.get('REMOTE_ADDR'),
               'user_agent': request.META.get('HTTP_USER_AGENT'),
           }
       )

   @receiver(user_logged_out)
   def log_user_logout(sender, request, user, **kwargs):
       if user:
           audit_logger.info(
               'User logged out',
               extra={
                   'user_id': user.id,
                   'username': user.username,
                   'ip_address': request.META.get('REMOTE_ADDR'),
               }
           )

Deployment Security
-------------------

Docker Security
~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   # Secure Dockerfile
   FROM python:3.11-slim-bullseye

   # Create non-root user
   RUN groupadd --gid 1000 appuser \\
       && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

   # Set security-focused environment variables
   ENV PYTHONDONTWRITEBYTECODE=1 \\
       PYTHONUNBUFFERED=1 \\
       PYTHONPATH=/app \\
       PIP_NO_CACHE_DIR=1 \\
       PIP_DISABLE_PIP_VERSION_CHECK=1

   # Install system dependencies with security updates
   RUN apt-get update \\
       && apt-get upgrade -y \\
       && apt-get install -y --no-install-recommends \\
           build-essential \\
           libpq-dev \\
           curl \\
       && apt-get clean \\
       && rm -rf /var/lib/apt/lists/*

   # Set working directory and copy requirements
   WORKDIR /app
   COPY requirements*.txt ./

   # Install Python dependencies
   RUN pip install --upgrade pip \\
       && pip install -r requirements.txt \\
       && pip install -r requirements-prod.txt

   # Copy application code
   COPY . .

   # Change ownership to non-root user
   RUN chown -R appuser:appuser /app

   # Switch to non-root user
   USER appuser

   # Expose port (non-privileged)
   EXPOSE 8000

   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
       CMD curl -f http://localhost:8000/health/ || exit 1

   # Run application
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]

Container Runtime Security
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # docker-compose.security.yml
   version: '3.8'

   services:
     web:
       build: .
       security_opt:
         - no-new-privileges:true
       cap_drop:
         - ALL
       cap_add:
         - NET_BIND_SERVICE
       read_only: true
       tmpfs:
         - /tmp:noexec,nosuid,size=100m
         - /var/log:noexec,nosuid,size=50m
       ulimits:
         nproc: 65535
         nofile:
           soft: 65535
           hard: 65535
       environment:
         - DJANGO_SETTINGS_MODULE=config.settings.production
       volumes:
         - type: tmpfs
           target: /app/logs
           tmpfs:
             size: 100m

Environment Variable Security
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env.security.example

   # Generate secure random keys
   DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
   FIELD_ENCRYPTION_KEY=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')

   # Database encryption at rest
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require&sslcert=/certs/client.crt&sslkey=/certs/client.key

   # Redis with AUTH
   REDIS_URL=redis://:strongpassword@redis:6379/0

   # API keys (use environment-specific secrets management)
   YAHOO_FINANCE_API_KEY=${VAULT_YAHOO_API_KEY}
   ALPHA_VANTAGE_API_KEY=${VAULT_ALPHA_VANTAGE_KEY}

Security Monitoring
-------------------

Intrusion Detection
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # personal_finance/core/security_monitoring.py
   import logging
   from django.core.cache import cache
   from django.contrib.auth.signals import user_login_failed
   from django.dispatch import receiver

   security_logger = logging.getLogger('personal_finance.security')

   class SecurityMonitor:
       \"\"\"Monitor and respond to security events.\"\"\"

       @staticmethod
       def log_suspicious_activity(request, event_type, details):
           \"\"\"Log suspicious activity with context.\"\"\"
           client_ip = SecurityMonitor._get_client_ip(request)

           security_logger.warning(
               f'Suspicious activity detected: {event_type}',
               extra={
                   'event_type': event_type,
                   'ip_address': client_ip,
                   'user_agent': request.META.get('HTTP_USER_AGENT'),
                   'details': details,
                   'timestamp': timezone.now().isoformat(),
               }
           )

           # Track suspicious IPs
           cache_key = f'suspicious_ip:{client_ip}'
           count = cache.get(cache_key, 0) + 1
           cache.set(cache_key, count, 3600)  # 1 hour

           # Alert if threshold exceeded
           if count > 10:
               SecurityMonitor._trigger_security_alert(client_ip, event_type)

       @staticmethod
       def _trigger_security_alert(ip_address, event_type):
           \"\"\"Trigger security alert for high-risk activity.\"\"\"
           from django.core.mail import send_mail
           from django.conf import settings

           subject = f'Security Alert: {event_type} from {ip_address}'
           message = f'''
           Security alert triggered for IP: {ip_address}
           Event type: {event_type}
           Time: {timezone.now()}

           Please investigate this activity.
           '''

           send_mail(
               subject,
               message,
               settings.DEFAULT_FROM_EMAIL,
               [settings.ADMIN_EMAIL],
               fail_silently=False,
           )

       @staticmethod
       def _get_client_ip(request):
           x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
           if x_forwarded_for:
               return x_forwarded_for.split(',')[0].strip()
           return request.META.get('REMOTE_ADDR')

   @receiver(user_login_failed)
   def log_failed_login(sender, credentials, request, **kwargs):
       \"\"\"Log failed login attempts.\"\"\"
       SecurityMonitor.log_suspicious_activity(
           request,
           'FAILED_LOGIN',
           {'username': credentials.get('username', 'unknown')}
       )

Security Testing
----------------

Automated Security Tests
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # tests/test_security.py
   import pytest
   from django.test import TestCase, Client
   from django.contrib.auth.models import User
   from django.urls import reverse

   class SecurityTestCase(TestCase):
       \"\"\"Test security features.\"\"\"

       def setUp(self):
           self.client = Client()
           self.user = User.objects.create_user(
               username='testuser',
               password='TestPassword123!',
               email='test@example.com'
           )

       def test_csrf_protection(self):
           \"\"\"Test CSRF protection is enabled.\"\"\"
           response = self.client.post(
               reverse('api:portfolio-list'),
               {'name': 'Test Portfolio'},
               HTTP_X_REQUESTED_WITH='XMLHttpRequest'
           )
           self.assertEqual(response.status_code, 403)  # CSRF failure

       def test_xss_protection(self):
           \"\"\"Test XSS protection headers.\"\"\"
           response = self.client.get('/')
           self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
           self.assertEqual(response['X-Frame-Options'], 'DENY')

       def test_rate_limiting(self):
           \"\"\"Test API rate limiting.\"\"\"
           # Make multiple requests rapidly
           for _ in range(25):  # Exceed burst limit of 20/min
               response = self.client.get('/api/v1/portfolios/')

           self.assertEqual(response.status_code, 429)  # Rate limited

       def test_sql_injection_protection(self):
           \"\"\"Test SQL injection protection.\"\"\"
           malicious_input = \"'; DROP TABLE auth_user; --\"

           response = self.client.get(
               reverse('api:portfolio-list'),
               {'search': malicious_input}
           )

           # Should not cause error - parameterized queries protect us
           self.assertIn(response.status_code, [200, 400])

           # Verify user table still exists
           self.assertTrue(User.objects.exists())

       def test_session_security(self):
           \"\"\"Test session security settings.\"\"\"
           # Login user
           self.client.login(username='testuser', password='TestPassword123!')

           # Check session cookie settings
           response = self.client.get('/')

           # Should have secure session cookie
           session_cookie = response.cookies.get('pf_sessionid')
           if session_cookie:
               self.assertTrue(session_cookie['secure'])
               self.assertTrue(session_cookie['httponly'])

Security Checklist
-------------------

Pre-Deployment Security Checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Django Configuration**
  ☐ ``DEBUG = False`` in production
  ☐ ``SECRET_KEY`` is unique and secure
  ☐ ``ALLOWED_HOSTS`` properly configured
  ☐ ``SECURE_SSL_REDIRECT = True``
  ☐ Security headers enabled
  ☐ CSRF protection enabled
  ☐ Session security configured

**Database Security**
  ☐ Database credentials secured
  ☐ SSL connections enforced
  ☐ Sensitive fields encrypted
  ☐ Connection pooling configured
  ☐ Backup encryption enabled

**API Security**
  ☐ Authentication required for all endpoints
  ☐ Rate limiting configured
  ☐ Input validation implemented
  ☐ Output sanitization enabled
  ☐ API versioning in place

**Infrastructure Security**
  ☐ HTTPS enforced
  ☐ Security headers configured
  ☐ Container security hardened
  ☐ Network isolation implemented
  ☐ Monitoring and alerting configured

**Access Control**
  ☐ Principle of least privilege
  ☐ Role-based access control
  ☐ Audit logging enabled
  ☐ Password policies enforced
  ☐ Session management secure

**Monitoring and Response**
  ☐ Security logging configured
  ☐ Intrusion detection enabled
  ☐ Incident response plan
  ☐ Regular security testing
  ☐ Dependency vulnerability scanning

Regular Security Maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Weekly Tasks**
  - Review security logs
  - Check for failed authentication attempts
  - Monitor API usage patterns
  - Verify backup integrity

**Monthly Tasks**
  - Update dependencies
  - Review user access permissions
  - Test incident response procedures
  - Security awareness training

**Quarterly Tasks**
  - Penetration testing
  - Security architecture review
  - Disaster recovery testing
  - Security policy updates

See Also
--------

* :doc:`environment` - Environment configuration security
* :doc:`django_settings` - Django security settings
* :doc:`../deployment/production` - Production security deployment
* :doc:`../api/authentication` - API security configuration
