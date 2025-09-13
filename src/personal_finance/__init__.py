"""
Personal Finance Package

A package for managing personal finance data and analysis.
"""

import logging
from typing import Optional, Any

# Import the dependency management system
from .dependencies import dependency_manager, setup_core_dependencies
from .dependency_config import DEPENDENCY_CONFIG, FEATURE_FLAGS

# Initialize the dependency management system
setup_core_dependencies()

# Configure logging
_logger = logging.getLogger(__name__)

# Module-level variables for backward compatibility
portfolio: Optional[Any] = None
yahoo_finance: Optional[Any] = None
database: Optional[Any] = None
logger: Optional[Any] = None


def _import_module_safely(module_name: str, import_path: str) -> Optional[Any]:
    """
    Safely import a module using the dependency management system.
    
    Args:
        module_name: Human-readable name for logging
        import_path: Python import path
        
    Returns:
        Imported module or None if not available
    """
    try:
        if import_path.startswith('.'):
            # Relative import
            from importlib import import_module
            return import_module(import_path, package='personal_finance')
        else:
            # Absolute import
            return __import__(import_path)
    except Exception as e:
        _logger.info(f"Module {module_name} not available: {e}")
        return None


def _initialize_modules():
    """Initialize core modules with structured dependency management."""
    global portfolio, yahoo_finance, database, logger
    
    # Import core modules using the dependency system
    portfolio = _import_module_safely("portfolio", ".portfolio")
    yahoo_finance = _import_module_safely("yahoo_finance", ".yahoo_finance") 
    database = _import_module_safely("database", ".database")
    
    # Import logger separately as it might have different dependencies
    logger = _import_module_safely("logger", ".logs.logger")


# Initialize modules on import
_initialize_modules()

# Define what gets imported with "from personal_finance import *"
__all__ = ["portfolio", "yahoo_finance", "database", "logger"]

# Package metadata
__version__ = "0.1.0"
__author__ = "Mauricio Gioachini"
__email__ = "maugx3@gmail.com"
