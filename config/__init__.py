"""Make Celery import optional during Django import-time.

Tests or environments that don't have Celery installed should not
fail import of the Django project. Import Celery lazily if present.
"""

try:
    # Import Celery app only when Celery is installed. If import fails,
    # don't raise during Django project import (e.g., in CI without Celery).
    from .celery_app import app as celery_app  # type: ignore  # noqa: F401

    __all__ = ("celery_app",)
except Exception:  # pragma: no cover - defensive import
    # Celery isn't available in this environment; continue without it.
    __all__ = ()
