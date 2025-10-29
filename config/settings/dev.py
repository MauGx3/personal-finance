"""
Development settings for Personal Finance project.
"""

# ! not needed right now, base code is already 100% dev-specific
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow localhost for development
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database
DATABASES["default"] = env.db("DATABASE_URL", default="sqlite:///db.sqlite3")

# Email backend for development (console output)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable HTTPS-only settings for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# CORS for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Logging for development
LOGGING["loggers"]["django"]["level"] = "INFO"
LOGGING["loggers"]["personal_finance"] = {
    "handlers": ["console"],
    "level": "DEBUG",
    "propagate": False,
}

# Django Debug Toolbar (if installed)
if DEBUG:
    import importlib.util

    if importlib.util.find_spec("debug_toolbar"):
        INSTALLED_APPS.append("debug_toolbar")
        MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
        INTERNAL_IPS = ["127.0.0.1", "localhost"]
