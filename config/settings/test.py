"""Test settings: in-memory database, fast hashing, no network."""

from .base import *

DEBUG = False
SECRET_KEY = "test-secret-key"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}
PRICE_PROVIDERS = {
    **PRICE_PROVIDERS,
    "fake": "tests.fakes.FakeProvider",
}
PRICE_PROVIDER = "fake"
MIDDLEWARE = [m for m in MIDDLEWARE if "whitenoise" not in m]
