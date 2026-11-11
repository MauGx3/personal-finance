"""Local development settings."""

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}
