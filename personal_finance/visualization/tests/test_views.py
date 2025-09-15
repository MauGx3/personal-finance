"""Tests for visualization views security."""

import json
from unittest.mock import patch, Mock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from personal_finance.visualization.views import dashboard_summary_api

User = get_user_model()


class DashboardSummaryAPISecurityTestCase(TestCase):
    """Test security aspects of dashboard summary API."""

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
