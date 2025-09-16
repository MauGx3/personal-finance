"""
Personal Finance Package

A package for managing personal finance data and analysis.
"""

from src.feature_registry import register_optional_feature

# Register optional modules using the feature registry
# This replaces fragile try/except blocks with structured feature management
portfolio = register_optional_feature(
    "portfolio", "personal_finance.portfolio"
)
yahoo_finance = register_optional_feature(
    "yahoo_finance", "personal_finance.yahoo_finance"
)
database = register_optional_feature("database", "personal_finance.database")
logger = register_optional_feature(
    "logger", "personal_finance.logs.logger", "logger"
)

# Define what gets imported with "from personal_finance import *"
__all__ = ["portfolio", "yahoo_finance", "database", "logger"]

# Package metadata
__version__ = "0.1.0"
__author__ = "Mauricio Gioachini"
__email__ = "maugx3@gmail.com"
