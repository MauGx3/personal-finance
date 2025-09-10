"""
Minimal core functionality tests for the personal finance platform.

This test suite only tests functionality that actually exists and has proper migrations:
- Django user model
- Assets app models (Asset, Portfolio, Holding)
- Basic model relationships and constraints

No complex imports, no unmigrated apps, no external dependencies.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from decimal import Decimal

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test basic user functionality."""
    
    def test_user_creation(self):
        """Test creating a basic user."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")


@pytest.mark.django_db
class TestAssetModels:
    """Test asset models that have proper migrations."""
    
    def test_asset_creation(self):
        """Test basic asset creation."""
        from personal_finance.assets.models import Asset
        
        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type="STOCK",
            currency="USD",
            exchange="NASDAQ"
        )
        assert asset.symbol == "AAPL"
        assert asset.name == "Apple Inc."
        assert asset.asset_type == "STOCK"
        assert str(asset) == "AAPL — Apple Inc."
    
    def test_portfolio_creation(self):
        """Test basic portfolio creation."""
        from personal_finance.assets.models import Portfolio
        
        user = User.objects.create_user(username="testuser", email="test@example.com")
        portfolio = Portfolio.objects.create(
            user=user,
            name="Test Portfolio",
            description="A test portfolio"
        )
        assert portfolio.name == "Test Portfolio"
        assert portfolio.user == user
        assert str(portfolio) == "Test Portfolio (testuser)"
    
    def test_holding_creation(self):
        """Test basic holding creation."""
        from personal_finance.assets.models import Asset, Portfolio, Holding
        
        user = User.objects.create_user(username="testuser", email="test@example.com")
        asset = Asset.objects.create(symbol="AAPL", asset_type="STOCK")
        portfolio = Portfolio.objects.create(user=user, name="Test Portfolio")
        
        holding = Holding.objects.create(
            user=user,
            asset=asset,
            portfolio=portfolio,
            quantity=Decimal("10.5"),
            currency="USD"
        )
        assert holding.quantity == Decimal("10.5")
        assert holding.user == user
        assert holding.asset == asset
        assert holding.portfolio == portfolio


@pytest.mark.django_db
class TestBasicConstraints:
    """Test basic model constraints."""
    
    def test_asset_str_method(self):
        """Test asset string representation."""
        from personal_finance.assets.models import Asset
        
        asset = Asset.objects.create(symbol="GOOGL", asset_type="STOCK")
        assert "GOOGL" in str(asset)
    
    def test_portfolio_user_relationship(self):
        """Test portfolio-user relationship."""
        from personal_finance.assets.models import Portfolio
        
        user = User.objects.create_user(username="testuser", email="test@example.com")
        portfolio = Portfolio.objects.create(user=user, name="My Portfolio")
        
        # Test reverse relationship
        assert portfolio in user.portfolios.all()
    
    def test_holding_relationships(self):
        """Test holding model relationships."""
        from personal_finance.assets.models import Asset, Portfolio, Holding
        
        user = User.objects.create_user(username="testuser", email="test@example.com")
        asset = Asset.objects.create(symbol="MSFT", asset_type="STOCK")
        portfolio = Portfolio.objects.create(user=user, name="Tech Portfolio")
        
        holding = Holding.objects.create(
            user=user,
            asset=asset,
            portfolio=portfolio,
            quantity=Decimal("5")
        )
        
        # Test relationships work both ways
        assert holding in user.holdings.all()
        assert holding in asset.holdings.all()
        assert holding in portfolio.holdings.all()


@pytest.mark.django_db
class TestDjangoBasics:
    """Test basic Django functionality."""
    
    def test_database_connection(self):
        """Test that database connection works."""
        user_count = User.objects.count()
        assert user_count >= 0  # Should not fail
    
    def test_model_creation_timestamps(self):
        """Test that timestamp fields work."""
        from personal_finance.assets.models import Asset
        
        asset = Asset.objects.create(symbol="TEST", asset_type="STOCK")
        assert asset.created_at is not None
        assert asset.updated_at is not None
        assert asset.created_at <= asset.updated_at