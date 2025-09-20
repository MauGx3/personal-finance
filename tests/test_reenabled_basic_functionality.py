"""
Re-enabled basic functionality tests for personal finance platform.

This file re-enables comprehensive testing for assets and portfolios
now that proper migrations are in place.
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import connection


User = get_user_model()


@pytest.mark.django_db
class TestAssetBasicFunctionality:
    """Test basic asset functionality with proper migrations."""

    def test_asset_creation_and_retrieval(self):
        """Test asset creation and basic retrieval."""
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

        # Test retrieval
        retrieved_asset = Asset.objects.get(symbol="AAPL")
        assert retrieved_asset.name == "Apple Inc."

    def test_asset_str_representation(self):
        """Test asset string representation."""
        from personal_finance.assets.models import Asset

        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK
        )
        
        str_repr = str(asset)
        # The exact format depends on the model's __str__ method
        assert "AAPL" in str_repr

    def test_multiple_asset_types(self):
        """Test creating assets of different types."""
        from personal_finance.assets.models import Asset

        # Test different asset types
        asset_data = [
            ("AAPL", "Apple Inc.", Asset.ASSET_STOCK),
            ("BTC-USD", "Bitcoin", Asset.ASSET_CRYPTO),
            ("TLT", "20+ Year Treasury", Asset.ASSET_ETF),
            ("USD", "US Dollar", Asset.ASSET_CASH),
        ]

        created_assets = []
        for symbol, name, asset_type in asset_data:
            asset = Asset.objects.create(
                symbol=symbol,
                name=name,
                asset_type=asset_type
            )
            created_assets.append(asset)
            assert asset.asset_type == asset_type

        # Verify all were created
        assert Asset.objects.count() == 4


@pytest.mark.django_db  
class TestPortfolioBasicFunctionality:
    """Test basic portfolio functionality with proper migrations."""

    def test_portfolio_creation(self):
        """Test portfolio model creation."""
        from personal_finance.assets.models import Portfolio

        user = User.objects.create_user(
            username="testuser", 
            email="test@example.com",
            password="testpass123"
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="My Test Portfolio",
            description="Test portfolio for functionality testing"
        )

        assert portfolio.name == "My Test Portfolio"
        assert portfolio.description == "Test portfolio for functionality testing"
        assert portfolio.user == user
        assert portfolio.is_default is False

    def test_portfolio_user_relationship(self):
        """Test portfolio-user relationship functionality."""
        from personal_finance.assets.models import Portfolio

        user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )

        # Create multiple portfolios for the same user
        portfolio1 = Portfolio.objects.create(
            user=user,
            name="Growth Portfolio"
        )
        
        portfolio2 = Portfolio.objects.create(
            user=user,
            name="Income Portfolio"
        )

        # Test forward relationship
        assert portfolio1.user == user
        assert portfolio2.user == user

        # Test reverse relationship
        user_portfolios = user.portfolios.all()
        assert portfolio1 in user_portfolios
        assert portfolio2 in user_portfolios
        assert user_portfolios.count() == 2

    def test_portfolio_unique_constraint(self):
        """Test portfolio unique constraint (user + name)."""
        from personal_finance.assets.models import Portfolio
        from django.db import IntegrityError

        user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )

        # Create first portfolio
        Portfolio.objects.create(
            user=user,
            name="My Portfolio"
        )

        # Try to create second portfolio with same name for same user
        # This should fail due to unique_together constraint
        with pytest.raises(IntegrityError):
            Portfolio.objects.create(
                user=user,
                name="My Portfolio"
            )


@pytest.mark.django_db
class TestHoldingBasicFunctionality:
    """Test basic holding functionality with proper migrations."""

    def test_holding_creation(self):
        """Test holding model creation."""
        from personal_finance.assets.models import Asset, Portfolio, Holding

        # Create dependencies
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="My Portfolio"
        )

        # Create holding
        holding = Holding.objects.create(
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("10.5"),
            cost_basis_per_unit=Decimal("150.25")
        )

        assert holding.portfolio == portfolio
        assert holding.asset == asset
        assert holding.quantity == Decimal("10.5")
        assert holding.cost_basis_per_unit == Decimal("150.25")

    def test_holding_calculations(self):
        """Test holding financial calculations."""
        from personal_finance.assets.models import Asset, Portfolio, Holding

        # Create dependencies
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="My Portfolio"
        )

        # Create holding with known values
        holding = Holding.objects.create(
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("100.00"),
            cost_basis_per_unit=Decimal("150.00")
        )

        # Test total cost basis calculation
        expected_cost_basis = Decimal("100.00") * Decimal("150.00")
        assert holding.total_cost_basis == expected_cost_basis

    def test_holding_portfolio_relationship(self):
        """Test holding-portfolio relationship."""
        from personal_finance.assets.models import Asset, Portfolio, Holding

        # Create dependencies
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )

        asset1 = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK
        )

        asset2 = Asset.objects.create(
            symbol="GOOGL",
            name="Alphabet Inc.",
            asset_type=Asset.ASSET_STOCK
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="My Portfolio"
        )

        # Create multiple holdings in same portfolio
        holding1 = Holding.objects.create(
            portfolio=portfolio,
            asset=asset1,
            quantity=Decimal("100.00"),
            cost_basis_per_unit=Decimal("150.00")
        )

        holding2 = Holding.objects.create(
            portfolio=portfolio,
            asset=asset2,
            quantity=Decimal("50.00"),
            cost_basis_per_unit=Decimal("2500.00")
        )

        # Test reverse relationship
        portfolio_holdings = portfolio.holdings.all()
        assert holding1 in portfolio_holdings
        assert holding2 in portfolio_holdings
        assert portfolio_holdings.count() == 2


@pytest.mark.django_db
class TestDatabaseConnectivity:
    """Test database connectivity and basic operations."""

    def test_database_connection(self):
        """Test that we can connect to database and perform basic operations."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

    def test_basic_crud_operations(self):
        """Test basic CRUD operations work."""
        from personal_finance.assets.models import Asset

        # Create
        asset = Asset.objects.create(
            symbol="TEST",
            name="Test Asset",
            asset_type=Asset.ASSET_STOCK
        )
        asset_id = asset.id

        # Read
        retrieved_asset = Asset.objects.get(id=asset_id)
        assert retrieved_asset.symbol == "TEST"

        # Update
        retrieved_asset.name = "Updated Test Asset"
        retrieved_asset.save()

        updated_asset = Asset.objects.get(id=asset_id)
        assert updated_asset.name == "Updated Test Asset"

        # Delete
        updated_asset.delete()
        
        with pytest.raises(Asset.DoesNotExist):
            Asset.objects.get(id=asset_id)

    def test_transaction_rollback(self):
        """Test that database transactions work properly."""
        from personal_finance.assets.models import Asset
        from django.db import transaction

        initial_count = Asset.objects.count()

        try:
            with transaction.atomic():
                Asset.objects.create(
                    symbol="TEST1",
                    name="Test Asset 1",
                    asset_type=Asset.ASSET_STOCK
                )
                
                Asset.objects.create(
                    symbol="TEST2",
                    name="Test Asset 2",
                    asset_type=Asset.ASSET_STOCK
                )
                
                # Force an error to test rollback
                raise Exception("Intentional error for rollback test")
                
        except Exception:
            pass  # Expected exception

        # Both assets should be rolled back
        final_count = Asset.objects.count()
        assert final_count == initial_count


@pytest.mark.django_db
class TestModelValidationAndConstraints:
    """Test model validation and database constraints."""

    def test_decimal_field_precision(self):
        """Test decimal field precision handling."""
        from personal_finance.assets.models import Asset, Portfolio, Holding

        # Create dependencies
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="TEST",
            name="Test Asset",
            asset_type=Asset.ASSET_STOCK
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="Test Portfolio"
        )

        # Test high precision decimal values
        holding = Holding.objects.create(
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("123.12345678"),  # 8 decimal places
            cost_basis_per_unit=Decimal("1500.99")
        )

        # Refresh from database to ensure precision is maintained
        holding.refresh_from_db()
        
        assert holding.quantity == Decimal("123.12345678")
        assert holding.cost_basis_per_unit == Decimal("1500.99")

    def test_foreign_key_constraints(self):
        """Test foreign key constraint enforcement."""
        from personal_finance.assets.models import Asset, Portfolio, Holding

        # Create dependencies
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="TEST",
            name="Test Asset",
            asset_type=Asset.ASSET_STOCK
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="Test Portfolio"
        )

        holding = Holding.objects.create(
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("100.00"),
            cost_basis_per_unit=Decimal("50.00")
        )

        # Test cascade delete
        portfolio_id = portfolio.id
        holding_id = holding.id
        
        portfolio.delete()

        # Holding should be cascade deleted
        assert not Holding.objects.filter(id=holding_id).exists()
        assert not Portfolio.objects.filter(id=portfolio_id).exists()

        # Asset should still exist (not cascade deleted)
        assert Asset.objects.filter(id=asset.id).exists()


@pytest.mark.django_db
class TestQueryOptimization:
    """Test query optimization and performance patterns."""

    def test_select_related_optimization(self):
        """Test select_related query optimization."""
        from personal_finance.assets.models import Asset, Portfolio, Holding

        # Create test data
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="Test Portfolio"
        )

        holding = Holding.objects.create(
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("100.00"),
            cost_basis_per_unit=Decimal("150.00")
        )

        # Test optimized query with select_related
        optimized_holdings = Holding.objects.select_related(
            'portfolio', 'asset'
        ).all()

        # Should be able to access related objects without additional queries
        for holding in optimized_holdings:
            portfolio_name = holding.portfolio.name  # No additional query
            asset_symbol = holding.asset.symbol      # No additional query
            assert portfolio_name is not None
            assert asset_symbol is not None

    def test_bulk_operations(self):
        """Test bulk create and update operations."""
        from personal_finance.assets.models import Asset

        # Test bulk create
        assets_data = []
        for i in range(10):
            assets_data.append(Asset(
                symbol=f"TEST{i:03d}",
                name=f"Test Asset {i}",
                asset_type=Asset.ASSET_STOCK
            ))

        # Bulk create should be more efficient than individual creates
        created_assets = Asset.objects.bulk_create(assets_data)
        assert len(created_assets) == 10

        # Verify they were created
        test_assets = Asset.objects.filter(symbol__startswith="TEST").count()
        assert test_assets == 10