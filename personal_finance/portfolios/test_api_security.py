"""Security tests for portfolios API views."""

import json
from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

try:
    from personal_finance.portfolios.api.views import PortfolioViewSet
except ImportError:
    # Handle graceful import failure for testing
    PortfolioViewSet = None


class PortfolioAPISecurityTestCase(TestCase):
    """Test security aspects of portfolios API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        self.user = Mock()
        self.user.is_authenticated = True

    @patch("personal_finance.portfolios.api.views.AnalyticsService")
    def test_performance_metrics_error_does_not_expose_exception_details(
        self, mock_service
    ):
        """Test that portfolio performance metrics errors don't expose internal details."""
        if PortfolioViewSet is None:
            self.skipTest("PortfolioViewSet not available")

        # Mock service to raise exception with sensitive information
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.calculate_portfolio_metrics.side_effect = Exception(
            "Database timeout: postgresql://portfolio_user:P@ssw0rd123@db-cluster.internal.company.com:5432/portfolio_db"
        )

        # Create viewset instance
        viewset = PortfolioViewSet()
        mock_portfolio = Mock()
        mock_portfolio.name = "Test Portfolio"
        viewset.get_object = Mock(return_value=mock_portfolio)

        # Create request
        request = self.factory.get("/api/portfolios/1/performance-metrics/")
        request.user = self.user

        # Call the performance_metrics action
        response = viewset.performance_metrics(request, pk=1)

        # Verify response
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response_data = response.data

        # Verify error message is generic
        self.assertEqual(response_data["error"], "Failed to calculate metrics")

        # Verify no sensitive information is exposed
        response_content = json.dumps(response_data)
        self.assertNotIn("P@ssw0rd123", response_content)
        self.assertNotIn("db-cluster.internal.company.com", response_content)
        self.assertNotIn("portfolio_user", response_content)

    @patch("personal_finance.portfolios.api.views.AnalyticsService")
    def test_allocation_data_error_does_not_expose_exception_details(
        self, mock_service
    ):
        """Test that allocation data errors don't expose internal details."""
        if PortfolioViewSet is None:
            self.skipTest("PortfolioViewSet not available")

        # Mock service to raise exception
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.calculate_portfolio_allocation.side_effect = Exception(
            "External API error: Invalid JWT token 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.secret_payload.signature' for service auth.financial-data.com"
        )

        viewset = PortfolioViewSet()
        mock_portfolio = Mock()
        viewset.get_object = Mock(return_value=mock_portfolio)

        request = self.factory.get("/api/portfolios/1/allocation-data/")
        request.user = self.user

        response = viewset.allocation_data(request, pk=1)

        # Verify response
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response_data = response.data
        self.assertEqual(
            response_data["error"], "Failed to get allocation data"
        )

        # Verify no JWT token or service details exposed
        response_content = json.dumps(response_data)
        self.assertNotIn(
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9", response_content
        )
        self.assertNotIn("auth.financial-data.com", response_content)
        self.assertNotIn("secret_payload", response_content)

    @patch("personal_finance.portfolios.api.views.AssetPriceHistory")
    def test_historical_performance_error_does_not_expose_exception_details(
        self, mock_history
    ):
        """Test that historical performance errors don't expose internal details."""
        if PortfolioViewSet is None:
            self.skipTest("PortfolioViewSet not available")

        # Mock to raise exception with system information
        mock_history.objects.filter.side_effect = Exception(
            "Memory allocation failed: OOMKilled by kernel, available RAM: 512MB, required: 2GB, swap: /dev/sda2"
        )

        viewset = PortfolioViewSet()
        mock_portfolio = Mock()
        mock_portfolio.positions.filter.return_value.select_related.return_value = []
        viewset.get_object = Mock(return_value=mock_portfolio)

        request = self.factory.get("/api/portfolios/1/historical-performance/")
        request.user = self.user

        response = viewset.historical_performance(request, pk=1)

        # Verify response
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response_data = response.data
        self.assertEqual(
            response_data["error"], "Failed to get historical data"
        )

        # Verify no system information exposed
        response_content = json.dumps(response_data)
        self.assertNotIn("OOMKilled", response_content)
        self.assertNotIn("/dev/sda2", response_content)
        self.assertNotIn("512MB", response_content)

    def test_all_portfolio_error_responses_have_consistent_structure(self):
        """Test that all portfolio API error responses have consistent structure."""
        if PortfolioViewSet is None:
            self.skipTest("PortfolioViewSet not available")

        # Test various types of sensitive information
        sensitive_exceptions = [
            "LDAP authentication failed: cn=admin,dc=company,dc=com password='AdminP@ss2024'",
            "S3 bucket access denied: s3://company-financial-data/ with access key AKIA1234567890EXAMPLE",
            "Redis session expired: redis://session:secret123@cache-01.internal:6380/0",
            "Config file error: Unable to read /etc/app/secrets.env, contains DATABASE_URL",
        ]

        expected_error_fields = {"error"}

        for sensitive_msg in sensitive_exceptions:
            with self.subTest(sensitive_msg=sensitive_msg):
                with patch(
                    "personal_finance.portfolios.api.views.AnalyticsService"
                ) as mock_service:
                    mock_service.return_value.calculate_portfolio_metrics.side_effect = Exception(
                        sensitive_msg
                    )

                    viewset = PortfolioViewSet()
                    viewset.get_object = Mock()

                    request = self.factory.get(
                        "/api/portfolios/1/performance-metrics/"
                    )
                    request.user = self.user

                    response = viewset.performance_metrics(request, pk=1)

                    # Verify response structure
                    response_data = response.data
                    self.assertEqual(
                        set(response_data.keys()), expected_error_fields
                    )

                    # Verify no sensitive data leakage
                    response_content = json.dumps(response_data)
                    self.assertNotIn("AdminP@ss2024", response_content)
                    self.assertNotIn("AKIA1234567890EXAMPLE", response_content)
                    self.assertNotIn("secret123", response_content)
                    self.assertNotIn("/etc/app/secrets.env", response_content)

    def test_error_messages_are_user_friendly_and_actionable(self):
        """Test that error messages provide user-friendly guidance without technical details."""
        if PortfolioViewSet is None:
            self.skipTest("PortfolioViewSet not available")

        # Mock various system-level errors
        system_errors = [
            "java.sql.SQLException: Connection pool exhausted",
            "numpy.linalg.LinAlgError: Matrix is singular",
            "OSError: [Errno 28] No space left on device: '/tmp'",
            "TimeoutError: Query exceeded 30 second limit",
        ]

        for error_msg in system_errors:
            with self.subTest(error_msg=error_msg):
                with patch(
                    "personal_finance.portfolios.api.views.AnalyticsService"
                ) as mock_service:
                    mock_service.return_value.calculate_portfolio_metrics.side_effect = Exception(
                        error_msg
                    )

                    viewset = PortfolioViewSet()
                    viewset.get_object = Mock()

                    request = self.factory.get(
                        "/api/portfolios/1/performance-metrics/"
                    )
                    request.user = self.user

                    response = viewset.performance_metrics(request, pk=1)

                    # Verify user sees generic, actionable message
                    response_data = response.data
                    self.assertEqual(
                        response_data["error"], "Failed to calculate metrics"
                    )

                    # Verify no technical jargon exposed
                    response_content = json.dumps(response_data)
                    self.assertNotIn("SQLException", response_content)
                    self.assertNotIn("LinAlgError", response_content)
                    self.assertNotIn("/tmp", response_content)
                    self.assertNotIn("30 second limit", response_content)
