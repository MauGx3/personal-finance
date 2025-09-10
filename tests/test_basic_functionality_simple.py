"""
Simplified basic functionality tests focused on Django core features.
Tests only the original models that exist in the base repository.
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
    """Test core user functionality."""
    
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
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )
        assert str(user) == "testuser"


@pytest.mark.django_db
class TestAssetModels:
    """Test asset models using only original schema fields."""
    
    def test_asset_creation_simple(self):
        """Test basic asset model creation using only fields from migration schema."""
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
        assert asset.currency == "USD"
        assert asset.exchange == "NASDAQ"
        assert asset.is_active is True
    
    def test_asset_str_representation(self):
        """Test asset string representation."""
        from personal_finance.assets.models import Asset
        
        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK
        )
        assert str(asset) == "AAPL — Apple Inc."
    
    def test_portfolio_creation(self):
        """Test portfolio model creation."""
        from personal_finance.assets.models import Portfolio
        
        user = User.objects.create_user(username="testuser", email="test@example.com")
        
        portfolio = Portfolio.objects.create(
            user=user,
            name="My Portfolio",
            description="Test portfolio"
        )
        
        assert portfolio.name == "My Portfolio"
        assert portfolio.user == user
        assert portfolio.is_default is False
    
    def test_holding_creation(self):
        """Test holding model creation."""
        from personal_finance.assets.models import Asset, Portfolio, Holding
        
        user = User.objects.create_user(username="testuser", email="test@example.com")
        
        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK
        )
        
        portfolio = Portfolio.objects.create(
            user=user,
            name="My Portfolio"
        )
        
        holding = Holding.objects.create(
            user=user,
            asset=asset,
            portfolio=portfolio,
            quantity=Decimal("10.5"),
            average_price=Decimal("150.25")
        )
        
        assert holding.user == user
        assert holding.asset == asset
        assert holding.portfolio == portfolio
        assert holding.quantity == Decimal("10.5")
        assert holding.average_price == Decimal("150.25")


@pytest.mark.django_db  
class TestDatabaseConnectivity:
    """Test database connectivity and basic operations."""
    
    def test_database_connection(self):
        """Test that we can connect to database and perform basic operations."""
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
    
    def test_migrations_applied(self):
        """Test that basic migrations are applied."""
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Check that assets_asset table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='assets_asset'
            """)
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'assets_asset'


@pytest.mark.django_db
class TestBasicFunctionality:
    """Test basic Django functionality."""
    
    def test_django_settings_loaded(self):
        """Test that Django settings are properly loaded."""
        from django.conf import settings
        
        assert hasattr(settings, 'INSTALLED_APPS')
        assert 'personal_finance.assets' in settings.INSTALLED_APPS
        assert 'personal_finance.users' in settings.INSTALLED_APPS