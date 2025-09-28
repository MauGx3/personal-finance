from .base import *  # noqa: F403
from .base import INSTALLED_APPS
from .base import MIDDLEWARE
from .base import env
import importlib.util as importlib_util
import os

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default=(
        "zHnb34mMGKgkItue7qqeNDylaW2P3ZSeDTx6QoiizDpnuft17xs1jRYsrfdEOBED"
    ),
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
}

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = env("EMAIL_HOST", default="mailpit")
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ["whitenoise.runserver_nostatic", *INSTALLED_APPS]


# django-debug-toolbar
# ------------------------------------------------------------------------------
# Only enable the debug toolbar if the package is installable. This prevents
# a hard crash when `DJANGO_SETTINGS_MODULE=config.settings.local` is used in
# a PaaS or other environment that doesn't install development dependencies.
if importlib_util.find_spec("debug_toolbar") is not None:
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
    INSTALLED_APPS += ["debug_toolbar"]
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    # https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": [
            "debug_toolbar.panels.redirects.RedirectsPanel",
            # Disable profiling panel due to an issue with Python 3.12:
            # https://github.com/jazzband/django-debug-toolbar/issues/1875
            "debug_toolbar.panels.profiling.ProfilingPanel",
        ],
        "SHOW_TEMPLATE_CONTEXT": True,
    }
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
    INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
    # treat USE_DOCKER as opt-in. Default to "no" so missing env doesn't crash
    # when running on PaaS platforms where this env var isn't provided.
    if os.environ.get("USE_DOCKER", "no") == "yes":
        import socket

        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS += [".".join([*ip.split(".")[:-1], "1"]) for ip in ips]
else:
    # Keep sensible defaults so other code can safely reference INTERNAL_IPS.
    INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

# django-extensions
# ------------------------------------------------------------------------------
# Only add django-extensions when it's available. This mirrors the defensive
# approach for debug_toolbar so that importing local settings on PaaS doesn't
# crash the process if dev packages aren't installed.
if importlib_util.find_spec("django_extensions") is not None:
    INSTALLED_APPS += ["django_extensions"]
# Celery
# ------------------------------------------------------------------------------

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True
# Your stuff...
# ------------------------------------------------------------------------------

# Safety: if for some reason local settings end up running in an environment
# without development dependencies installed, remove dev-only apps that
# cannot be imported to avoid a hard crash during app registry population.
for _dev_pkg in ("debug_toolbar", "django_extensions"):
    if (
        _dev_pkg in INSTALLED_APPS
        and importlib_util.find_spec(_dev_pkg) is None
    ):
        INSTALLED_APPS = [a for a in INSTALLED_APPS if a != _dev_pkg]
