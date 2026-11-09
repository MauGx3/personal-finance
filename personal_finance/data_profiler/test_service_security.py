"""Security tests for data profiler services."""

import json
from unittest.mock import patch

from django.test import TestCase

try:
    from personal_finance.data_profiler.services import DataProfilerService
except ImportError:
    # Handle graceful import failure for testing
    DataProfilerService = None


class DataProfilerServiceSecurityTestCase(TestCase):
    """Test security aspects of data profiler service."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = DataProfilerService() if DataProfilerService else None

    def test_extract_profile_results_error_does_not_expose_exception_details(
        self,
    ):
        """Test that profile extraction errors don't expose internal details."""
        if self.service is None:
            self.skipTest("DataProfilerService not available")

        # Mock the internal method to raise an exception with sensitive information
        with patch.object(
            self.service, "_extract_summary_stats"
        ) as mock_extract:
            mock_extract.side_effect = Exception(
                "File access denied: /home/user/.ssh/id_rsa contains private key data, path=/var/secrets/app.env"
            )

            # Call the method that should handle the exception
            result = self.service.extract_profile_results({})

            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)

            # Verify error message is generic
            self.assertEqual(
                result["error"], "Failed to extract profile results"
            )

            # Verify no sensitive information is exposed
            result_str = json.dumps(result)
            self.assertNotIn("/home/user/.ssh/id_rsa", result_str)
            self.assertNotIn("private key data", result_str)
            self.assertNotIn("/var/secrets/app.env", result_str)

    def test_service_handles_various_sensitive_exception_types(self):
        """Test that the service properly sanitizes various types of sensitive exceptions."""
        if self.service is None:
            self.skipTest("DataProfilerService not available")

        # Test various types of sensitive information
        sensitive_exceptions = [
            "AWS credentials error: ACCESS_KEY_ID=AKIA1234567890, SECRET_ACCESS_KEY=abcd1234",
            "Database connection failed: mysql://root:MySuperSecret123@localhost:3306/production",
            "Configuration error: JWT_SECRET=my_super_secret_jwt_key_2024 not found in /etc/config/",
            "API authentication failed: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sensitive_payload",
            "Environment variable missing: REDIS_PASSWORD=prod_redis_pass_2024 not set",
        ]

        for sensitive_msg in sensitive_exceptions:
            with self.subTest(sensitive_msg=sensitive_msg):
                with patch.object(
                    self.service, "_extract_summary_stats"
                ) as mock_extract:
                    mock_extract.side_effect = Exception(sensitive_msg)

                    result = self.service.extract_profile_results({})

                    # Verify no sensitive data leakage
                    result_str = json.dumps(result)

                    # Check for specific patterns that should NOT appear
                    sensitive_patterns = [
                        "AKIA1234567890",
                        "MySuperSecret123",
                        "my_super_secret_jwt_key_2024",
                        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
                        "prod_redis_pass_2024",
                        "abcd1234",
                        "sensitive_payload",
                    ]

                    for pattern in sensitive_patterns:
                        self.assertNotIn(pattern, result_str)

                    # Verify only generic error message
                    self.assertEqual(
                        result["error"], "Failed to extract profile results"
                    )

    def test_error_response_structure_is_consistent(self):
        """Test that error responses have consistent structure across different exceptions."""
        if self.service is None:
            self.skipTest("DataProfilerService not available")

        # Test various exception types
        exception_types = [
            ValueError("Invalid value in data"),
            KeyError("Missing required key"),
            TypeError("Wrong data type"),
            RuntimeError("Runtime error occurred"),
            OSError("Operating system error"),
        ]

        expected_keys = {"error"}

        for exception in exception_types:
            with self.subTest(exception=type(exception).__name__):
                with patch.object(
                    self.service, "_extract_summary_stats"
                ) as mock_extract:
                    mock_extract.side_effect = exception

                    result = self.service.extract_profile_results({})

                    # Verify consistent structure
                    self.assertEqual(set(result.keys()), expected_keys)
                    self.assertEqual(
                        result["error"], "Failed to extract profile results"
                    )

    def test_successful_execution_maintains_normal_behavior(self):
        """Test that normal execution path is not affected by security changes."""
        if self.service is None:
            self.skipTest("DataProfilerService not available")

        # Mock successful execution
        mock_report = {
            "global_stats": {"samples": 100, "null_count": 5},
            "column_stats": {"column1": {"type": "int", "mean": 50}},
        }

        with (
            patch.object(
                self.service, "_extract_summary_stats"
            ) as mock_summary,
            patch.object(
                self.service, "_extract_column_stats"
            ) as mock_columns,
            patch.object(
                self.service, "_extract_sensitive_data"
            ) as mock_sensitive,
        ):
            mock_summary.return_value = {"total_rows": 100}
            mock_columns.return_value = {"column1": {"type": "int"}}
            mock_sensitive.return_value = {"pii_detected": False}

            result = self.service.extract_profile_results(mock_report)

            # Verify successful result structure
            self.assertIsInstance(result, dict)
            self.assertNotIn("error", result)
            self.assertIn("summary_stats", result)
            self.assertIn("column_stats", result)
            self.assertIn("sensitive_data", result)

    def test_logging_preserves_detailed_errors_for_debugging(self):
        """Test that detailed errors are still logged for debugging purposes."""
        if self.service is None:
            self.skipTest("DataProfilerService not available")

        sensitive_error = "Database connection failed: postgresql://admin:secret@db.internal:5432/prod"

        with (
            patch.object(
                self.service, "_extract_summary_stats"
            ) as mock_extract,
            patch(
                "personal_finance.data_profiler.services.logger"
            ) as mock_logger,
        ):
            mock_extract.side_effect = Exception(sensitive_error)

            # Call the method
            result = self.service.extract_profile_results({})

            # Verify detailed error was logged for debugging
            mock_logger.error.assert_called_once()
            logged_message = mock_logger.error.call_args[0][0]
            self.assertIn("Error extracting profile results", logged_message)

            # Verify the actual exception was passed to logger (for server-side debugging)
            logged_exception = mock_logger.error.call_args[0][1]
            self.assertEqual(str(logged_exception), sensitive_error)

            # Verify client response is still sanitized
            self.assertEqual(
                result["error"], "Failed to extract profile results"
            )
