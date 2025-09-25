"""
WSGI config for personal-finance project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from loguru import logger
from urllib.parse import urlparse

# This allows easy placement of apps within the interior
# personal_finance directory.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR / "personal_finance"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# Startup runtime diagnostics (safe / masked) to help PaaS debugging.
# This prints minimal info to stdout/stderr without exposing secrets.


def _mask_secret(value: str | None) -> str:
    """Return a masked representation for secrets (non-sensitive length).

    Examples: None -> '<UNSET>', 'abc' -> '<SET length=3>'
    """
    if not value:
        return "<UNSET>"
    # show length only for secrets
    return f"<SET length={len(value)}>"


def _mask_db_url(url: str | None) -> str:
    """Return a masked DB URL showing only scheme, host and port.

    If parsing fails or values are missing returns '<INVALID>' or '<UNSET>'.
    """
    if not url:
        return "<UNSET>"
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        return "<INVALID>"
    host = parsed.hostname or "?"
    port = parsed.port or "?"
    return f"{parsed.scheme}://{host}:{port}"


# Logging configured via loguru
logger.info(
    f"Startup diagnostics: DJANGO_SETTINGS_MODULE={os.environ.get('DJANGO_SETTINGS_MODULE')}"
)
logger.info(f"USE_DOCKER={os.environ.get('USE_DOCKER', '<UNSET>')}")
logger.info(
    f"DATABASE_URL={_mask_db_url(os.environ.get('DATABASE_URL'))}"
)
logger.info("POSTGRES_HOST=%s", os.environ.get("POSTGRES_HOST", "<UNSET>"))
logger.info("POSTGRES_PORT=%s", os.environ.get("POSTGRES_PORT", "<UNSET>"))
logger.info(
    "DJANGO_SECRET_KEY=%s",
    _mask_secret(os.environ.get("DJANGO_SECRET_KEY")),
)

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
application = get_wsgi_application()
