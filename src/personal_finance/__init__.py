"""
Personal Finance Package

A package for managing personal finance data and analysis.
"""

# Import main modules defensively to avoid failing import when optional
# dependencies are missing (e.g., external data libraries used by portfolio).
try:  # pragma: no cover - best-effort optional imports
    from . import portfolio  # type: ignore  # noqa: F401
except Exception:
    portfolio = None  # type: ignore

try:  # pragma: no cover
    from . import yahoo_finance  # type: ignore  # noqa: F401
except Exception:
    yahoo_finance = None  # type: ignore

try:  # pragma: no cover
    from . import database  # type: ignore  # noqa: F401
except Exception:
    database = None  # type: ignore

# Optional: expose logger if available without causing circular import on init
try:  # pragma: no cover - defensive
    from .logs.logger import logger  # type: ignore  # noqa: F401
except Exception:
    logger = None  # type: ignore

# Define what gets imported with "from personal_finance import *"
__all__ = ["portfolio", "yahoo_finance", "database", "logger"]

# Package metadata
__version__ = "0.1.0"
__author__ = "Mauricio Gioachini"
__email__ = "maugx3@gmail.com"
