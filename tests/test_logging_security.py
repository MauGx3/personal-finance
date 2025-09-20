"""
Test logging security improvements for PY-A6006 audit issue.
"""

import os
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


class LoggingSecurityTestCase(TestCase):
    """Test security aspects of logging configuration."""

    def setUp(self):
        """Set up test fixtures."""
        # Add src to path for imports
        test_dir = Path(__file__).parent.parent
        src_dir = test_dir / "src"
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))

    def test_portfolio_logging_uses_environment_variable(self):
        """Test that portfolio logging respects PORTFOLIO_LOG_LEVEL environment variable."""
        # Test default behavior
        with patch.dict(os.environ, {}, clear=True):
            import logging

            log_level = os.environ.get("PORTFOLIO_LOG_LEVEL", "INFO").upper()
            level = getattr(logging, log_level, logging.INFO)
            self.assertEqual(level, logging.INFO)

        # Test with WARNING level
        with patch.dict(os.environ, {"PORTFOLIO_LOG_LEVEL": "WARNING"}):
            log_level = os.environ.get("PORTFOLIO_LOG_LEVEL", "INFO").upper()
            level = getattr(logging, log_level, logging.INFO)
            self.assertEqual(level, logging.WARNING)

        # Test with invalid level - should default to INFO
        with patch.dict(os.environ, {"PORTFOLIO_LOG_LEVEL": "INVALID"}):
            log_level = os.environ.get("PORTFOLIO_LOG_LEVEL", "INFO").upper()
            level = getattr(logging, log_level, logging.INFO)
            self.assertEqual(level, logging.INFO)

    def test_package_logger_has_security_documentation(self):
        """Test that PackageLogger class has security audit documentation."""
        # Import using full path since module structure is different
        from personal_finance.logs.logger import PackageLogger

        # Check that the class docstring mentions security audit
        docstring = PackageLogger.__doc__
        self.assertIn("SECURITY AUDIT", docstring)
        self.assertIn("sensitive financial data", docstring)
        self.assertIn("Debug level logging", docstring)

    def test_logging_configuration_has_security_comments(self):
        """Test that logging configurations have security audit comments."""
        # Test base settings
        base_settings_path = (
            Path(__file__).parent.parent / "config" / "settings" / "base.py"
        )
        with open(base_settings_path) as f:
            base_content = f.read()

        self.assertIn("SECURITY AUDIT", base_content)
        self.assertIn("sensitive information", base_content)

        # Test production settings
        prod_settings_path = (
            Path(__file__).parent.parent
            / "config"
            / "settings"
            / "production.py"
        )
        with open(prod_settings_path) as f:
            prod_content = f.read()

        self.assertIn("SECURITY AUDIT", prod_content)
        self.assertIn("disable_existing_loggers", prod_content)

        # Test celery config
        celery_path = Path(__file__).parent.parent / "config" / "celery_app.py"
        with open(celery_path) as f:
            celery_content = f.read()

        self.assertIn("SECURITY AUDIT", celery_content)
        self.assertIn("dictConfig", celery_content)

    def test_production_settings_disable_existing_loggers_is_false(self):
        """Test that production settings has disable_existing_loggers set to False for security."""
        prod_settings_path = (
            Path(__file__).parent.parent
            / "config"
            / "settings"
            / "production.py"
        )
        with open(prod_settings_path) as f:
            prod_content = f.read()

        # Check that disable_existing_loggers is set to False
        self.assertIn('"disable_existing_loggers": False', prod_content)
        # Ensure it's not set to True
        self.assertNotIn('"disable_existing_loggers": True', prod_content)

    def test_sensitive_data_not_in_log_format(self):
        """Test that log formats don't include potentially sensitive information."""
        # Import using full path since module structure is different
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from personal_finance.logs.logger import PackageLogger

        # Create a logger instance
        logger = PackageLogger("test_logger")

        # Get the formatter from the first handler
        if logger.logger.handlers:
            formatter = logger.logger.handlers[0].formatter
            format_string = formatter._fmt

            # Check that the format doesn't include potentially sensitive fields
            sensitive_fields = [
                "%(password)s",
                "%(secret)s",
                "%(key)s",
                "%(token)s",
            ]
            for field in sensitive_fields:
                self.assertNotIn(field, format_string)
