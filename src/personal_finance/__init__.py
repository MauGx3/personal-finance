"""
Personal Finance Package

A package for managing personal finance data and analysis.
"""

# Import main modules to make them available at package level
from . import portfolio
from . import yahoo_finance
from . import logs
from . import database

# Define what gets imported with "from personal_finance import *"
__all__ = ["portfolio", "yahoo_finance", "logs", "database"]

# Package metadata
__version__ = "0.1.0"
__author__ = "Mauricio Gioachini"
__email__ = "maugx3@gmail.com"
