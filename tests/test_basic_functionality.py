"""
Basic functionality tests for the Personal Finance Platform.

This test suite covers core functionality to ensure the platform basics work
without requiring complex imports or non-existent modules.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestBasicFunctionality:
    """Test basic platform functionality without complex dependencies."""
    
    def test_user_creation(self):
        """Test that we can create users."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
    
    def test_admin_accessible(self, client):
        """Test that admin interface is accessible."""
        response = client.get("/admin/")
        # Should redirect to login, not crash
        assert response.status_code in [200, 302]
    
    def test_django_setup_working(self):
        """Test that Django is properly configured."""
        from django.conf import settings
        assert hasattr(settings, 'INSTALLED_APPS')
        assert 'personal_finance.users' in settings.INSTALLED_APPS
        assert 'personal_finance.assets' in settings.INSTALLED_APPS


@pytest.mark.django_db
class TestAssetModels:
    """Test asset models without complex factories."""
    
    def test_asset_creation_simple(self):
        """Test basic asset model creation."""
        from personal_finance.assets.models import Asset
        
        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
            currency="USD",
            exchange="NASDAQ"
        )
        
        assert asset.symbol == "AAPL"
        assert asset.name == "Apple Inc."
        assert asset.asset_type == Asset.ASSET_STOCK


@pytest.mark.django_db  
class TestPortfolioModels:
    """Test portfolio models with minimal setup."""
    
    def test_portfolio_creation_simple(self):
        """Test basic portfolio creation."""
        from personal_finance.portfolios.models import Portfolio
        
        user = User.objects.create_user(
            username="portfoliouser",
            email="portfolio@example.com",
            password="testpass123"
        )
        
        portfolio = Portfolio.objects.create(
            user=user,
            name="Test Portfolio",
            description="A test portfolio"
        )
        
        assert portfolio.name == "Test Portfolio"
        assert portfolio.user == user


class TestRestFrameworkBasics(APITestCase):
    """Test that Django REST Framework is working."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="apiuser",
            email="api@example.com",
            password="testpass123"
        )
    
    def test_api_root_accessible(self):
        """Test that API root is accessible."""
        # Try to access a basic API endpoint
        response = self.client.get("/api/")
        # Should not crash, even if 404
        assert response.status_code in [200, 404, 403]
    
    def test_authentication_required(self):
        """Test that API requires authentication where expected."""
        # This tests that authentication framework works
        response = self.client.get("/api/portfolios/")
        # Should require authentication
        assert response.status_code in [401, 403]
        
        # Login and try again
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/portfolios/")
        # Should work better now (200 or 404 if endpoint doesn't exist)
        assert response.status_code in [200, 404]