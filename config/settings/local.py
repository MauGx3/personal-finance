from .base import *  # noqa: F403
from .base import INSTALLED_APPS
from .base import MIDDLEWARE
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="zHnb34mMGKgkItue7qqeNDylaW2P3ZSeDTx6QoiizDpnuft17xs1jRYsrfdEOBED",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]  # noqa: S104

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
# Only enable django-debug-toolbar when the package is available in the
# environment. This prevents import-time failures (e.g., in notebooks or CI)
# when debug_toolbar is not installed.
try:
    import importlib.util

    if importlib.util.find_spec("debug_toolbar") is not None:
        # Enable the app and middleware
        INSTALLED_APPS += ["debug_toolbar"]
        MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

        # Configure debug toolbar panels and behavior
        DEBUG_TOOLBAR_CONFIG = {
            "DISABLE_PANELS": [
                "debug_toolbar.panels.redirects.RedirectsPanel",
                # Disable profiling panel due to an issue with Python 3.12:
                # https://github.com/jazzband/django-debug-toolbar/issues/1875
                "debug_toolbar.panels.profiling.ProfilingPanel",
            ],
            "SHOW_TEMPLATE_CONTEXT": True,
        }

        # INTERNAL_IPS for debug toolbar
        INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
        if env("USE_DOCKER") == "yes":
            import socket

            hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
            INTERNAL_IPS += [
                ".".join([*ip.split(".")[:-1], "1"]) for ip in ips
            ]
except Exception:
    # debug_toolbar not available in this environment; continue without it
    pass

# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
# Only enable django-extensions when the package is available in the
# environment to avoid import-time failures in lightweight environments
# (notebooks, CI) where it may not be installed.
try:
    import importlib.util

    if importlib.util.find_spec("django_extensions") is not None:
        INSTALLED_APPS += ["django_extensions"]
except Exception:
    # django-extensions not available; continue without it
    pass
# Celery
# ------------------------------------------------------------------------------

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True
# Your stuff...
# ------------------------------------------------------------------------------
