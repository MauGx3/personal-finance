"""
Loguru compatibility layer for existing logging.* calls.

This module provides a compatibility layer to replace standard logging calls
with loguru equivalents while maintaining the same API.

SECURITY AUDIT: This compatibility layer maintains the same security
requirements as the original logging implementation.
"""

import os
from loguru import logger as loguru_logger
from .level import LOG_FORMAT, resolve_level

# Configure loguru to replace standard logging
module_logger = loguru_logger
module_logger.remove()  # Remove default handler

# Get log level from environment and validate it for security compliance
log_level = resolve_level(os.environ.get("PORTFOLIO_LOG_LEVEL"))

# Container-aware configuration: produce JSON when running in containers so
# logs are structured and easy to ship. Developers can set
# PORTFOLIO_CONTAINERIZED=1 in container images.
containerized = os.environ.get("PORTFOLIO_CONTAINERIZED") in (
    "1",
    "true",
    "True",
)

# Add console handler with a shared format. When containerized, serialize
# (JSON) the output; otherwise print human-friendly colorized logs.
module_logger.add(
    __import__("sys").stdout,
    level=log_level,
    format=LOG_FORMAT.replace("{extra[name]} - ", ""),
    colorize=not containerized,
    serialize=containerized,
)


class LoguruLogger:
    """Loguru-based logger that mimics the standard logging.Logger
    interface.
    """

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

    def trace(self, message: str, *args):
        """Log trace level message (very verbose)."""
        if args:
            message = message % args
        try:
            self.logger.trace(message)
        except AttributeError:
            # Fall back to debug if trace is not available
            self.logger.debug(message)


# Compatibility functions to replace logging module functions
def getLogger(name: str = "root") -> LoguruLogger:
    """Get a logger instance with the specified name."""
    return LoguruLogger(name)


def basicConfig(level=None, fmt=None, **_kwargs):
    """Compatibility stub for logging.basicConfig.

    This module configures loguru at import time; this function remains for
    compatibility and intentionally does nothing.
    """
    return None


# Constants for compatibility with logging module
TRACE = "TRACE"
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"
