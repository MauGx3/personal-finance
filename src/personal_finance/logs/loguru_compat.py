"""
Loguru compatibility layer for existing logging.* calls.

This module provides a compatibility layer to replace standard logging calls
with loguru equivalents while maintaining the same API.

SECURITY AUDIT: This compatibility layer maintains the same security
requirements as the original logging implementation.
"""

import os
from loguru import logger as loguru_logger

# Configure loguru to replace standard logging
loguru_logger.remove()  # Remove default handler

# Get log level from environment for security compliance
log_level = os.environ.get("PORTFOLIO_LOG_LEVEL", "INFO").upper()

# Add console handler with format similar to logging.basicConfig
loguru_logger.add(
    __import__('sys').stdout,
    level=log_level,
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {level} - {message}",
    colorize=True
)


class LoguruLogger:
    """Loguru-based logger that mimics the standard logging.Logger interface."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = loguru_logger.bind(name=name)
    
    def info(self, message: str, *args):
        """Log info level message."""
        if args:
            message = message % args
        self.logger.info(message)
    
    def error(self, message: str, *args):
        """Log error level message."""
        if args:
            message = message % args
        self.logger.error(message)
    
    def warning(self, message: str, *args):
        """Log warning level message."""  
        if args:
            message = message % args
        self.logger.warning(message)
    
    def debug(self, message: str, *args):
        """Log debug level message."""
        if args:
            message = message % args
        self.logger.debug(message)


# Compatibility functions to replace logging module functions
def getLogger(name: str = "root") -> LoguruLogger:
    """Get a logger instance with the specified name."""
    return LoguruLogger(name)


def basicConfig(level=None, format=None, **kwargs):
    """Configure basic logging - compatibility function."""
    # This is handled in the module initialization above
    # We maintain this function for compatibility but it's essentially a no-op
    pass


# Constants for compatibility with logging module
DEBUG = "DEBUG"
INFO = "INFO" 
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"