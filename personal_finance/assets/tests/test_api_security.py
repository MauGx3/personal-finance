"""Security tests for assets API views."""

import json
from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

try:
    from personal_finance.assets.api.views import AssetViewSet
except ImportError:
    # Handle graceful import failure for testing
    AssetViewSet = None


class AssetAPISecurityTestCase(TestCase):
    """Test security aspects of assets API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = APIRequestFactory()
        self.user = Mock()
        self.user.is_authenticated = True

    @patch("personal_finance.assets.api.views.AnalyticsService")
    def test_performance_metrics_error_does_not_expose_exception_details(
        self, mock_service
    ):
        """Test that performance metrics errors don't expose internal details."""
        if AssetViewSet is None:
            self.skipTest("AssetViewSet not available")

        # Mock service to raise exception with sensitive information
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.calculate_asset_performance_metrics.side_effect = Exception(
            "Database error: Connection timeout to finance-db.internal:3306, credentials in /var/secrets/db.conf"
        )

        # Create viewset instance
        viewset = AssetViewSet()
        mock_asset = Mock()
        mock_asset.symbol = "AAPL"
        viewset.get_object = Mock(return_value=mock_asset)

        # Create request
        request = self.factory.get("/api/assets/1/performance-metrics/")
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
        self.assertNotIn("finance-db.internal", response_content)
        self.assertNotIn("/var/secrets", response_content)
        self.assertNotIn("3306", response_content)

    @patch("personal_finance.assets.api.views.AnalyticsService")
    def test_technical_indicators_error_does_not_expose_exception_details(
        self, mock_service
    ):
        """Test that technical indicators errors don't expose internal details."""
        if AssetViewSet is None:
            self.skipTest("AssetViewSet not available")

        # Mock service to raise exception
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.calculate_technical_indicators.side_effect = Exception(
            "API quota exceeded for key: ak_1234567890, rate limit: 100 req/min"
        )

        viewset = AssetViewSet()
        mock_asset = Mock()
        viewset.get_object = Mock(return_value=mock_asset)

        request = self.factory.get("/api/assets/1/technical-indicators/")
        request.user = self.user

        response = viewset.technical_indicators(request, pk=1)

        # Verify response
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response_data = response.data
        self.assertEqual(
            response_data["error"], "Failed to calculate indicators"
        )

        # Verify no API key exposed
        response_content = json.dumps(response_data)
        self.assertNotIn("ak_1234567890", response_content)
        self.assertNotIn("quota exceeded", response_content)

    @patch("personal_finance.assets.api.views.AssetDetailSerializer")
    def test_update_price_validation_error_does_not_expose_exception_details(
        self, mock_serializer
    ):
        """Test that price update validation errors don't expose internal details."""
        if AssetViewSet is None:
            self.skipTest("AssetViewSet not available")

        # Mock serializer to raise validation exception
        mock_serializer_instance = Mock()
        mock_serializer.return_value = mock_serializer_instance
        mock_serializer_instance.is_valid.side_effect = ValueError(
            "Invalid decimal: received '../../etc/passwd' in price field"
        )

        viewset = AssetViewSet()
        mock_asset = Mock()
        viewset.get_object = Mock(return_value=mock_asset)

        request = self.factory.patch(
            "/api/assets/1/update-price/",
            data={"price": "../../etc/passwd"},
            format="json",
        )
        request.user = self.user

        response = viewset.update_price(request, pk=1)

        # Verify response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.data
        self.assertEqual(response_data["error"], "Invalid price data")

        # Verify no path traversal attempt is exposed
        response_content = json.dumps(response_data)
        self.assertNotIn("../../etc/passwd", response_content)
        self.assertNotIn("Invalid decimal", response_content)

    @patch("personal_finance.assets.api.views.DataSourceService")
    def test_refresh_data_error_does_not_expose_exception_details(
        self, mock_service
    ):
        """Test that data refresh errors don't expose internal details."""
        if AssetViewSet is None:
            self.skipTest("AssetViewSet not available")

        # Mock service to raise exception with external service details
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.refresh_asset_data.side_effect = Exception(
            "HTTP 403 Forbidden: Invalid API key for api.external-data.com, contact support@external-data.com"
        )

        viewset = AssetViewSet()
        mock_asset = Mock()
        viewset.get_object = Mock(return_value=mock_asset)

        request = self.factory.post("/api/assets/1/refresh-data/")
        request.user = self.user

        response = viewset.refresh_data(request, pk=1)

        # Verify response
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        response_data = response.data
        self.assertEqual(response_data["error"], "Failed to refresh data")

        # Verify no external service details exposed
        response_content = json.dumps(response_data)
        self.assertNotIn("api.external-data.com", response_content)
        self.assertNotIn("support@external-data.com", response_content)
        self.assertNotIn("HTTP 403", response_content)

    def test_all_asset_error_responses_have_consistent_structure(self):
        """Test that all asset API error responses have consistent structure."""
        if AssetViewSet is None:
            self.skipTest("AssetViewSet not available")

        # Test various types of sensitive information
        sensitive_exceptions = [
            "AWS S3 access denied: bucket=private-data, key=AKIAEXAMPLE",
            "MongoDB connection failed: mongodb://admin:secret@cluster.internal/",
            "Cache miss: Redis server redis://auth:password@cache.internal:6379",
            "File system error: Permission denied /etc/shadow",
        ]

        expected_error_fields = {"error"}

        for sensitive_msg in sensitive_exceptions:
            with self.subTest(sensitive_msg=sensitive_msg):
                with patch(
                    "personal_finance.assets.api.views.AnalyticsService"
                ) as mock_service:
                    mock_service.return_value.calculate_asset_performance_metrics.side_effect = Exception(
                        sensitive_msg
                    )

                    viewset = AssetViewSet()
                    viewset.get_object = Mock()

                    request = self.factory.get(
                        "/api/assets/1/performance-metrics/"
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
                    self.assertNotIn("AKIAEXAMPLE", response_content)
                    self.assertNotIn("admin:secret", response_content)
                    self.assertNotIn("auth:password", response_content)
                    self.assertNotIn("/etc/shadow", response_content)
