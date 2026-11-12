"""Local development settings."""

from .base import *  # skipcq: PYL-W0614 - settings modules extend base on purpose

DEBUG = True
ALLOWED_HOSTS = ["*"]
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}
