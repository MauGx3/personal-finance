"""Tests for visualization views security."""

import json
from unittest.mock import patch, Mock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from personal_finance.visualization.views import (
    dashboard_summary_api,
    portfolio_performance_chart_api,
    portfolio_allocation_chart_api,
    portfolio_risk_metrics_chart_api,
    asset_price_chart_api,
)

User = get_user_model()


class VisualizationAPISecurityTestCase(TestCase):
    """Test security aspects of visualization APIs."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = Mock()
        self.user.is_authenticated = True

    @patch("personal_finance.visualization.views.Portfolio")
    def test_dashboard_summary_api_error_does_not_expose_exception_details(
        self, mock_portfolio
    ):
        """Test that exception details are not exposed in API response."""
        # Mock Portfolio.objects.filter to raise an exception
        mock_portfolio.objects.filter.side_effect = Exception(
            "Internal database error with sensitive info"
        )

        request = self.factory.get("/api/dashboard/summary/")
        request.user = self.user

        response = dashboard_summary_api(request)

        # Verify response is JsonResponse with 500 status
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 500)

        # Parse response content
        response_data = json.loads(response.content.decode())

        # Verify error message is generic
        self.assertEqual(
            response_data["error"], "Failed to generate dashboard summary"
        )

        # Verify no sensitive information is exposed
        self.assertNotIn("message", response_data)
        self.assertNotIn("Internal database error", response.content.decode())
        self.assertNotIn("sensitive info", response.content.decode())

        # Verify only expected keys are present
        expected_keys = {"error"}
        self.assertEqual(set(response_data.keys()), expected_keys)

    @patch("personal_finance.visualization.views.get_object_or_404")
    def test_portfolio_performance_chart_api_error_security(self, mock_get_object):
        """Test that portfolio performance chart API doesn't expose exception details."""
        # Mock to raise an exception with sensitive information
        mock_get_object.side_effect = Exception(
            "Database connection failed: server=db.internal.company.com:5432"
        )

        request = self.factory.get("/api/portfolio/1/performance/")
        request.user = self.user

        response = portfolio_performance_chart_api(request, 1)

        # Verify response structure
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 500)

        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data["error"], "Failed to generate performance chart")
        self.assertNotIn("message", response_data)
        self.assertNotIn("server=db.internal", response.content.decode())

    @patch("personal_finance.visualization.views.get_object_or_404")
    def test_portfolio_allocation_chart_api_error_security(self, mock_get_object):
        """Test that portfolio allocation chart API doesn't expose exception details."""
        mock_get_object.side_effect = Exception("Auth token: sk-1234567890abcdef")

        request = self.factory.get("/api/portfolio/1/allocation/")
        request.user = self.user

        response = portfolio_allocation_chart_api(request, 1)

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data["error"], "Failed to generate allocation chart")
        self.assertNotIn("sk-1234567890abcdef", response.content.decode())

    @patch("personal_finance.visualization.views.get_object_or_404")
    def test_portfolio_risk_metrics_chart_api_error_security(self, mock_get_object):
        """Test that portfolio risk metrics chart API doesn't expose exception details."""
        mock_get_object.side_effect = Exception("API_KEY=secret_key_here")

        request = self.factory.get("/api/portfolio/1/risk-metrics/")
        request.user = self.user

        response = portfolio_risk_metrics_chart_api(request, 1)

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data["error"], "Failed to generate risk metrics chart")
        self.assertNotIn("secret_key_here", response.content.decode())

    @patch("personal_finance.visualization.views.get_object_or_404")
    def test_asset_price_chart_api_error_security(self, mock_get_object):
        """Test that asset price chart API doesn't expose exception details."""
        mock_get_object.side_effect = Exception(
            "File not found: /etc/secrets/config.ini"
        )

        request = self.factory.get("/api/asset/1/price-chart/")
        request.user = self.user

        response = asset_price_chart_api(request, 1)

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data["error"], "Failed to generate asset price chart")
        self.assertNotIn("/etc/secrets", response.content.decode())


class DashboardSummaryAPISecurityTestCase(TestCase):
    """Test security aspects of dashboard summary API - legacy test class."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = Mock()
        self.user.is_authenticated = True

    @patch("personal_finance.visualization.views.Portfolio")
    def test_dashboard_summary_api_error_does_not_expose_exception_details(
        self, mock_portfolio
    ):
        """Test that exception details are not exposed in API response."""
        # Mock Portfolio.objects.filter to raise an exception
        mock_portfolio.objects.filter.side_effect = Exception(
            "Internal database error with sensitive info"
        )

        request = self.factory.get("/api/dashboard/summary/")
        request.user = self.user

        response = dashboard_summary_api(request)

        # Verify response is JsonResponse with 500 status
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 500)

        # Parse response content
        response_data = json.loads(response.content.decode())

        # Verify error message is generic
        self.assertEqual(
            response_data["error"], "Failed to generate dashboard summary"
        )

        # Verify no sensitive information is exposed
        self.assertNotIn("message", response_data)
        self.assertNotIn("Internal database error", response.content.decode())
        self.assertNotIn("sensitive info", response.content.decode())

        # Verify only expected keys are present
        expected_keys = {"error"}
        self.assertEqual(set(response_data.keys()), expected_keys)
