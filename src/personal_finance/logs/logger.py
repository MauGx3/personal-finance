import logging
import sys
from pathlib import Path
from typing import Optional


class PackageLogger:
    """Handler for all logging operations in the personal finance package."""

    def __init__(self, name: str = "personal_finance"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create formatters and handlers
        self._setup_logger()

    def _setup_logger(self, log_file: Optional[Path] = None):
        """Setup logger with console and file handlers."""
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (optional)
        if log_file:
            file_handler = logging.FileHandler(str(log_file))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

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


# Create default logger instance
logger = PackageLogger()
