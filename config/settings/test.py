"""Minimal test settings used by pytest.

This file avoids importing the project's full settings (and django-environ)
so tests can run in constrained CI/dev environments. It mirrors the
essential bits used by the test suite: in-memory database, minimal apps,
and lightweight static/media config.
"""

from pathlib import Path

# Base project directory (approximate, only used for path-like settings)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Minimal secret key for tests
SECRET_KEY = "test-secret-key"

# File-backed SQLite DB for tests. Using a file (instead of :memory:) ensures
# Django's test runner can run migrations reliably across connections used by
# the test runner and the test processes. The file will be created inside the
# repository under a hidden file so it's easy to clean up.
TEST_DB_PATH = BASE_DIR / ".test_db.sqlite3"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(TEST_DB_PATH),
        # Avoid ATOMIC_REQUESTS for tests (added complexity with sqlite file DB)
        "ATOMIC_REQUESTS": False,
    }
}

# INSTALLED APPS: keep only apps with migrations and that tests rely on
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.sites",
    # Third party apps required by admin hooks in the codebase
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Minimal DRF presence to avoid import errors from views/tests
    "rest_framework",
    # Local testable apps
    "personal_finance.users",
    "personal_finance.assets",
]

# Minimal middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # allauth requires its AccountMiddleware to be installed
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.test_urls"

# Required by django-allauth
SITE_ID = 1

# Minimal templates so admin and auth-related code can render without pulling
# the full project template configuration.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

# Minimal static/media setup
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
# Ensure STATIC_ROOT and COMPRESS_ROOT are set so compressor's AppConf
# doesn't raise ImproperlyConfigured during imports in tests.
STATIC_ROOT = str(BASE_DIR / "staticfiles_test")
COMPRESS_ROOT = STATIC_ROOT

# Password hasher — fast for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use a simple test runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"


# Minimal logging to avoid importing complex logging config
LOGGING = {"version": 1, "disable_existing_loggers": True}
