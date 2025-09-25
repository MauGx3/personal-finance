import os
import sys
from pathlib import Path
from typing import Optional

from loguru import logger as loguru_logger


class PackageLogger:
    """Handler for all logging operations in the personal finance package.

    SECURITY AUDIT: This logger should be reviewed to ensure:
    - No sensitive financial data (account numbers, SSNs, etc.) is logged
    - Debug level logging is disabled in production environments  
    - Log messages are properly sanitized before output
    """

    def __init__(self, name: str = "personal_finance"):
        self.name = name
        self.logger = loguru_logger
        
        # Configure the logger with security-compliant defaults
        self._setup_logger()

    def _setup_logger(self, log_file: Optional[Path] = None):
        """Setup logger with console and file handlers."""
        # Remove default handler and configure with our format
        self.logger.remove()
        
        # Get log level from environment variable for security compliance
        log_level = os.environ.get("PORTFOLIO_LOG_LEVEL", "INFO").upper()
        
        # Console handler with custom format matching original logging format
        self.logger.add(
            sys.stdout,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {extra[name]} - {level} - {message}",
            colorize=True
        )
        
        # Bind the logger name to maintain compatibility
        self.logger = self.logger.bind(name=self.name)

        # File handler (optional)
        if log_file:
            self.logger.add(
                str(log_file),
                level=log_level,
                format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {extra[name]} - {level} - {message}",
                rotation="10 MB",  # Add rotation for better log management
                retention="30 days"  # Retention for security compliance
            )

    def info(self, message: str):
        """Log info level message."""
        self.logger.info(message)

    def error(self, message: str):
        """Log error level message."""
        self.logger.error(message)

    def warning(self, message: str):
        """Log warning level message."""
        self.logger.warning(message)

    def debug(self, message: str):
        """Log debug level message."""
        self.logger.debug(message)

    def add_file_handler(self, log_file: Path):
        """Add file handler to the logger."""
        log_level = os.environ.get("PORTFOLIO_LOG_LEVEL", "INFO").upper()
        self.logger.add(
            str(log_file),
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {extra[name]} - {level} - {message}",
            rotation="10 MB",
            retention="30 days"
        )


# Create default logger instance
logger = PackageLogger()
