"""
Personal Finance Package

A package for managing personal finance data and analysis.
"""

# Import main modules to make them available at package level
from . import portfolio  # noqa: F401
from . import yahoo_finance  # noqa: F401
from . import database  # noqa: F401

# Optional: expose logger if available without causing circular import on init
try:  # pragma: no cover - defensive
	from .logs.logger import logger  # type: ignore  # noqa: F401
except Exception:  # pragma: no cover
	logger = None  # type: ignore

# Define what gets imported with "from personal_finance import *"
__all__ = ["portfolio", "yahoo_finance", "database", "logger"]

# Package metadata
__version__ = "0.1.0"
__author__ = "Mauricio Gioachini"
__email__ = "maugx3@gmail.com"
