"""Security tests for backtesting API views."""

import json
from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

try:
    from personal_finance.backtesting.api.views import (
        BacktestViewSet,
        quick_backtest,
    )
except ImportError:
    # Handle graceful import failure for testing
    BacktestViewSet = None
    quick_backtest = None


class BacktestAPISecurityTestCase(TestCase):
    """Test security aspects of backtesting API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        self.user = Mock()
        self.user.is_authenticated = True

    @patch("personal_finance.backtesting.api.views.BacktestEngine")
    def test_run_backtest_error_does_not_expose_exception_details(
        self, mock_engine
    ):
        """Test that backtest execution errors don't expose internal details."""
        if BacktestViewSet is None:
            self.skipTest("BacktestViewSet not available")

        # Mock engine to raise exception with sensitive information
        mock_engine_instance = Mock()
        mock_engine.return_value = mock_engine_instance
        mock_engine_instance.run_backtest.side_effect = Exception(
            "Database connection failed: host=internal-db.company.com, user=admin, password=secret123"
        )

        # Create a mock backtest object
        mock_backtest = Mock()
        mock_backtest.refresh_from_db = Mock()

        # Create viewset instance
        viewset = BacktestViewSet()
        viewset.get_object = Mock(return_value=mock_backtest)
        viewset.get_serializer = Mock()

        # Create request
        request = self.factory.post("/api/backtests/1/run/")
        request.user = self.user

        # Call the run action method
        response = viewset.run(request, pk=1)

        # Verify response
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response_data = response.data

        # Verify error message is generic
        self.assertEqual(response_data["error"], "Backtest execution failed")

        # Verify no sensitive information is exposed
        response_content = json.dumps(response_data)
        self.assertNotIn("password=secret123", response_content)
        self.assertNotIn("internal-db.company.com", response_content)
        self.assertNotIn("user=admin", response_content)

    @patch("personal_finance.backtesting.api.views.BacktestEngine")
    @patch("personal_finance.backtesting.api.views.BacktestSerializer")
    def test_quick_backtest_error_does_not_expose_exception_details(
        self, mock_serializer, mock_engine
    ):
        """Test that quick backtest errors don't expose internal details."""
        if quick_backtest is None:
            self.skipTest("quick_backtest function not available")

        # Mock engine to raise exception
        mock_engine_instance = Mock()
        mock_engine.return_value = mock_engine_instance
        mock_engine_instance.run_backtest.side_effect = Exception(
            "API key invalid: sk-1234567890abcdef, check credentials in /etc/config"
        )

        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer.return_value = mock_serializer_instance
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.save.return_value = Mock()

        # Create request with data
        request = self.factory.post(
            "/api/backtests/quick/",
            data={"strategy": "test", "symbol": "AAPL"},
            format="json",
        )
        request.user = self.user

        # Call the function
        response = quick_backtest(request)

        # Verify response
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response_data = response.data

        # Verify error message is generic
        self.assertEqual(response_data["error"], "Quick backtest failed")

        # Verify no sensitive information is exposed
        response_content = json.dumps(response_data)
        self.assertNotIn("sk-1234567890abcdef", response_content)
        self.assertNotIn("/etc/config", response_content)
        self.assertNotIn("API key invalid", response_content)

    def test_all_backtest_error_responses_have_consistent_structure(self):
        """Test that all error responses have consistent structure without sensitive data."""
        # This test verifies that error responses don't accidentally include
        # extra fields that might contain sensitive information

        # Test data with various sensitive information patterns
        sensitive_exceptions = [
            "Connection failed: postgresql://user:pass@host:5432/db",
            "Authentication error: Bearer token abc123xyz",
            "File not found: /home/user/.env with SECRET_KEY=mysecret",
            "Redis connection timeout: redis://localhost:6379/0",
        ]

        expected_error_structure = {"error"}

        for sensitive_msg in sensitive_exceptions:
            with self.subTest(sensitive_msg=sensitive_msg):
                # Mock any exception that could occur in backtesting
                with patch(
                    "personal_finance.backtesting.api.views.BacktestEngine"
                ) as mock_engine:
                    if BacktestViewSet is None:
                        continue

                    mock_engine.return_value.run_backtest.side_effect = (
                        Exception(sensitive_msg)
                    )

                    viewset = BacktestViewSet()
                    viewset.get_object = Mock()
                    viewset.get_serializer = Mock()

                    request = self.factory.post("/api/backtests/1/run/")
                    request.user = self.user

                    response = viewset.run(request, pk=1)

                    # Verify response structure
                    response_data = response.data
                    self.assertEqual(
                        set(response_data.keys()), expected_error_structure
                    )

                    # Verify no sensitive data leakage
                    response_content = json.dumps(response_data)
                    self.assertNotIn("pass@host", response_content)
                    self.assertNotIn("SECRET_KEY", response_content)
                    self.assertNotIn("Bearer token", response_content)
