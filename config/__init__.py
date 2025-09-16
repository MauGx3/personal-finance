"""
Celery Configuration with Structured Feature Management

Makes Celery import optional during Django import-time using a structured
approach instead of fragile try/except blocks.
"""

import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


def _import_celery_app() -> Optional[Any]:
    """
    Import Celery app with structured error handling.
    
    Returns:
        Celery app instance if available, None otherwise
    """
    try:
        from .celery_app import app as celery_app
        logger.debug("Celery app imported successfully")
        return celery_app
    except ImportError as e:
        logger.debug(f"Celery not available: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error importing Celery: {e}")
        return None


# Import Celery app only when available
# This structured approach replaces fragile try/except blocks
celery_app = _import_celery_app()

# Configure exports based on availability
if celery_app is not None:
    __all__ = ("celery_app",)
else:
    __all__ = ()
