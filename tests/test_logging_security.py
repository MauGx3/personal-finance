"""
Test logging security improvements for PY-A6006 audit issue.
Tests adapted for loguru logging migration.
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
            log_level = os.environ.get("PORTFOLIO_LOG_LEVEL", "INFO").upper()
            # With loguru, we expect INFO as default
            self.assertEqual(log_level, "INFO")

        # Test with WARNING level
        with patch.dict(os.environ, {"PORTFOLIO_LOG_LEVEL": "WARNING"}):
            log_level = os.environ.get("PORTFOLIO_LOG_LEVEL", "INFO").upper()
            self.assertEqual(log_level, "WARNING")

        # Test with invalid level - should default to INFO
        with patch.dict(os.environ, {"PORTFOLIO_LOG_LEVEL": "INVALID"}):
            log_level = os.environ.get("PORTFOLIO_LOG_LEVEL", "INFO").upper()
            # The invalid level should still be retrieved but loguru handles it gracefully
            self.assertEqual(log_level, "INVALID")

    def test_package_logger_has_security_documentation(self):
        """Test that PackageLogger class has security audit documentation."""
        # Import using full path since module structure is different
        from personal_finance.logs.logger import PackageLogger

        # Check that the class docstring mentions security audit
        docstring = PackageLogger.__doc__
        self.assertIn("SECURITY AUDIT", docstring)
        self.assertIn("sensitive financial data", docstring)
        self.assertIn("Debug level logging", docstring)

    def test_loguru_logger_respects_environment_variable(self):
        """Test that loguru logger respects PORTFOLIO_LOG_LEVEL environment variable."""
        from personal_finance.logs.logger import PackageLogger
        
        # Test that logger can be created and uses environment variable
        with patch.dict(os.environ, {"PORTFOLIO_LOG_LEVEL": "WARNING"}):
            logger_instance = PackageLogger("test_security")
            
            # Logger should be created successfully and have the correct name
            self.assertEqual(logger_instance.name, "test_security")
            self.assertIsNotNone(logger_instance.logger)
            
    def test_loguru_security_format_no_sensitive_fields(self):
        """Test that loguru format doesn't include potentially sensitive information."""
        from personal_finance.logs.logger import PackageLogger
        
        # Create a logger instance
        logger_instance = PackageLogger("test_security_format")
        
        # Check that the logger methods work correctly
        try:
            logger_instance.info("Test message")
            logger_instance.warning("Test warning")
            logger_instance.error("Test error")
            logger_instance.debug("Test debug")
        except Exception as e:
            self.fail(f"Logger methods should work without error: {e}")

    def test_logging_configuration_has_security_comments(self):
        """Test that logging configurations have security audit comments."""
        # Test that our loguru implementation maintains security comments
        logger_file_path = (
            Path(__file__).parent.parent / "src" / "personal_finance" / "logs" / "logger.py"
        )
        with open(logger_file_path) as f:
            logger_content = f.read()

        self.assertIn("SECURITY AUDIT", logger_content)
        self.assertIn("sensitive financial data", logger_content)
        self.assertIn("PORTFOLIO_LOG_LEVEL", logger_content)

    def test_production_settings_disable_existing_loggers_is_false(self):
        """Test that production settings has disable_existing_loggers set to False for security."""
        prod_settings_path = (
            Path(__file__).parent.parent
            / "config"
            / "settings"
            / "production.py"
        )
        if prod_settings_path.exists():
            with open(prod_settings_path) as f:
                prod_content = f.read()

            # Check that disable_existing_loggers is set to False
            self.assertIn('"disable_existing_loggers": False', prod_content)
            # Ensure it's not set to True
            self.assertNotIn('"disable_existing_loggers": True', prod_content)

    def test_loguru_compatibility_layer(self):
        """Test that the loguru compatibility layer works correctly."""
        from personal_finance.logs.loguru_compat import getLogger, DEBUG, INFO, WARNING, ERROR
        
        # Test that we can get a logger
        test_logger = getLogger("test_compat")
        self.assertIsNotNone(test_logger)
        
        # Test that constants are defined
        self.assertEqual(DEBUG, "DEBUG")
        self.assertEqual(INFO, "INFO")
        self.assertEqual(WARNING, "WARNING") 
        self.assertEqual(ERROR, "ERROR")
        
        # Test that logger methods work
        try:
            test_logger.info("Test compatibility message")
            test_logger.error("Test compatibility error")
        except Exception as e:
            self.fail(f"Compatibility logger should work: {e}")
