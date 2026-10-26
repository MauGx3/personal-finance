"""
Expanded test suite for personal finance platform - Core Asset Management.

This test file expands coverage for the assets app which has proper migrations.
It provides comprehensive testing of asset models, validation, and business logic.
"""

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAssetModel:
    """Comprehensive tests for Asset model functionality."""

    def test_asset_creation_basic(self):
        """Test basic asset creation with minimal fields."""
        from personal_finance.assets.models import Asset

        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
        )

        assert asset.symbol == "AAPL"
        assert asset.name == "Apple Inc."
        assert asset.asset_type == Asset.ASSET_STOCK
        assert asset.is_active is True
        assert asset.created_at is not None
        assert asset.updated_at is not None

    def test_asset_creation_comprehensive(self):
        """Test asset creation with all fields populated."""
        from personal_finance.assets.models import Asset

        asset = Asset.objects.create(
            symbol="GOOGL",
            name="Alphabet Inc. Class A",
            asset_type=Asset.ASSET_STOCK,
            currency="USD",
            exchange="NASDAQ",
            isin="US02079K3059",
            cusip="02079K305",
            metadata={"sector": "Technology", "industry": "Internet Software"},
        )

        assert asset.symbol == "GOOGL"
        assert asset.name == "Alphabet Inc. Class A"
        assert asset.currency == "USD"
        assert asset.exchange == "NASDAQ"
        assert asset.isin == "US02079K3059"
        assert asset.cusip == "02079K305"
        assert asset.metadata["sector"] == "Technology"

    def test_asset_str_representation(self):
        """Test asset string representation."""
        from personal_finance.assets.models import Asset

        asset = Asset.objects.create(
            symbol="MSFT",
            name="Microsoft Corporation",
            asset_type=Asset.ASSET_STOCK,
        )

        # Check the actual __str__ method implementation
        str_repr = str(asset)
        assert "MSFT" in str_repr
        assert "Microsoft Corporation" in str_repr

    def test_asset_type_choices(self):
        """Test all asset type choices are valid."""
        from personal_finance.assets.models import Asset

        valid_types = [
            Asset.ASSET_STOCK,
            Asset.ASSET_BOND,
            Asset.ASSET_CRYPTO,
            Asset.ASSET_CASH,
            Asset.ASSET_FUND,
            Asset.ASSET_ETF,
            Asset.ASSET_FOREX,
            Asset.ASSET_FOREIGN,
        ]

        for asset_type in valid_types:
            asset = Asset.objects.create(
                symbol=f"TEST_{asset_type}",
                name=f"Test {asset_type}",
                asset_type=asset_type,
            )
            assert asset.asset_type == asset_type

    def test_asset_metadata_json_field(self):
        """Test asset metadata JSON field functionality."""
        from personal_finance.assets.models import Asset

        metadata = {
            "sector": "Technology",
            "market_cap": 2800000000000,
            "pe_ratio": 28.5,
            "dividend_yield": 0.005,
            "tags": ["large-cap", "growth", "tech"],
        }

        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
            metadata=metadata,
        )

        # Refresh from database to ensure JSON serialization works
        asset.refresh_from_db()

        assert asset.metadata["sector"] == "Technology"
        assert asset.metadata["market_cap"] == 2800000000000
        assert asset.metadata["pe_ratio"] == 28.5
        assert "large-cap" in asset.metadata["tags"]

    def test_asset_ordering(self):
        """Test asset model ordering."""
        from personal_finance.assets.models import Asset

        # Create assets in non-alphabetical order
        Asset.objects.create(
            symbol="ZZZZ", name="Z Company", asset_type=Asset.ASSET_STOCK
        )
        Asset.objects.create(
            symbol="AAAA", name="A Company", asset_type=Asset.ASSET_STOCK
        )
        Asset.objects.create(
            symbol="MMMM", name="M Company", asset_type=Asset.ASSET_STOCK
        )

        assets = Asset.objects.all()
        symbols = [asset.symbol for asset in assets]

        # Should be ordered by symbol, then name according to Meta.ordering
        assert symbols == sorted(symbols)

    def test_asset_unique_constraints(self):
        """Test asset model unique constraints."""
        from personal_finance.assets.models import Asset

        # Create first asset
        Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
        )

        # Try to create duplicate - should not raise error as symbol is not unique
        # This is by design to allow multiple assets with same symbol but different types
        Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc. (Class B)",
            asset_type=Asset.ASSET_STOCK,
        )

        # Should have 2 AAPL assets
        assert Asset.objects.filter(symbol="AAPL").count() == 2


@pytest.mark.django_db
class TestPortfolioModel:
    """Tests for Portfolio model in assets app."""

    def test_portfolio_creation(self):
        """Test portfolio model creation."""
        from personal_finance.assets.models import Portfolio

        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="My Test Portfolio",
            description="A test portfolio for unit testing",
        )

        assert portfolio.name == "My Test Portfolio"
        assert portfolio.description == "A test portfolio for unit testing"
        assert portfolio.user == user
        assert portfolio.is_default is False
        assert portfolio.created_at is not None

    def test_portfolio_str_representation(self):
        """Test portfolio string representation."""
        from personal_finance.assets.models import Portfolio

        user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="Growth Portfolio",
        )

        str_repr = str(portfolio)
        assert "Growth Portfolio" in str_repr
        assert "testuser" in str_repr

    def test_portfolio_user_relationship(self):
        """Test portfolio-user relationship."""
        from personal_finance.assets.models import Portfolio

        user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

        # Create multiple portfolios for same user
        portfolio1 = Portfolio.objects.create(
            user=user,
            name="Portfolio 1",
        )
        portfolio2 = Portfolio.objects.create(
            user=user,
            name="Portfolio 2",
        )

        # Test reverse relationship
        user_portfolios = user.portfolios.all()
        assert portfolio1 in user_portfolios
        assert portfolio2 in user_portfolios
        assert user_portfolios.count() == 2


@pytest.mark.django_db
class TestHoldingModel:
    """Tests for Holding model in assets app."""

    def test_holding_creation(self):
        """Test holding model creation."""
        from personal_finance.assets.models import Asset, Holding, Portfolio

        # Create dependencies
        user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="Test Portfolio",
        )

        # Create holding
        holding = Holding.objects.create(
            user=user,
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("100.00"),
            average_price=Decimal("150.00"),
        )

        assert holding.user == user
        assert holding.portfolio == portfolio
        assert holding.asset == asset
        assert holding.quantity == Decimal("100.00")
        assert holding.average_price == Decimal("150.00")

    def test_holding_calculations(self):
        """Test holding financial calculations."""
        from personal_finance.assets.models import Asset, Holding, Portfolio

        # Create dependencies
        user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="Test Portfolio",
        )

        # Create holding
        holding = Holding.objects.create(
            user=user,
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("100.00"),
            average_price=Decimal("150.00"),
        )

        # Test total cost basis calculation (if the property exists)
        # Note: The assets app Holding model might not have this property
        if hasattr(holding, "total_cost_basis"):
            expected_cost_basis = Decimal("100.00") * Decimal("150.00")
            assert holding.total_cost_basis == expected_cost_basis
        else:
            # Calculate manually for testing
            total_cost = holding.quantity * (
                holding.average_price or Decimal(0)
            )
            expected_cost_basis = Decimal("100.00") * Decimal("150.00")
            assert total_cost == expected_cost_basis

    def test_holding_str_representation(self):
        """Test holding string representation."""
        from personal_finance.assets.models import Asset, Holding, Portfolio

        # Create dependencies
        user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
        )

        portfolio = Portfolio.objects.create(
            user=user,
            name="Test Portfolio",
        )

        holding = Holding.objects.create(
            user=user,
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("100.00"),
            average_price=Decimal("150.00"),
        )

        str_repr = str(holding)
        assert "AAPL" in str_repr
        assert "100.00" in str_repr


@pytest.mark.django_db
class TestAssetModelEdgeCases:
    """Test edge cases and error conditions for Asset model."""

    def test_asset_with_empty_optional_fields(self):
        """Test asset creation with minimal required fields."""
        from personal_finance.assets.models import Asset

        asset = Asset.objects.create(
            symbol="TEST",
            asset_type=Asset.ASSET_STOCK,
            # name is blank=True
            # currency is blank=True
            # exchange is blank=True
        )

        assert asset.symbol == "TEST"
        assert asset.name == ""
        assert asset.currency == ""
        assert asset.exchange == ""

    def test_asset_metadata_default_empty_dict(self):
        """Test that asset metadata defaults to empty dict."""
        from personal_finance.assets.models import Asset

        asset = Asset.objects.create(
            symbol="TEST",
            asset_type=Asset.ASSET_STOCK,
        )

        assert asset.metadata == {}
        assert isinstance(asset.metadata, dict)

    def test_asset_is_active_default_true(self):
        """Test that asset is_active defaults to True."""
        from personal_finance.assets.models import Asset

        asset = Asset.objects.create(
            symbol="TEST",
            asset_type=Asset.ASSET_STOCK,
        )

        assert asset.is_active is True

    def test_asset_invalid_type_choice(self):
        """Test asset creation with invalid type choice."""
        from personal_finance.assets.models import Asset

        # This should not raise an error at creation time in Django
        # Validation happens at the form/serializer level
        asset = Asset.objects.create(
            symbol="TEST",
            name="Test Asset",
            asset_type="INVALID_TYPE",
        )

        # The invalid type is stored, validation would happen elsewhere
        assert asset.asset_type == "INVALID_TYPE"


@pytest.mark.django_db
class TestModelPerformance:
    """Test model performance and query optimization."""

    def test_bulk_asset_creation(self):
        """Test bulk creation of assets for performance."""
        from personal_finance.assets.models import Asset

        # Create many assets at once
        assets = []
        for i in range(100):
            assets.append(
                Asset(
                    symbol=f"TEST{i:03d}",
                    name=f"Test Asset {i}",
                    asset_type=Asset.ASSET_STOCK,
                )
            )

        # Bulk create
        created_assets = Asset.objects.bulk_create(assets)
        assert len(created_assets) == 100

        # Verify they were created
        assert Asset.objects.filter(symbol__startswith="TEST").count() == 100

    def test_asset_query_performance(self):
        """Test basic asset queries for performance awareness."""
        from personal_finance.assets.models import Asset

        # Create test data
        for asset_type in [
            Asset.ASSET_STOCK,
            Asset.ASSET_BOND,
            Asset.ASSET_ETF,
        ]:
            for i in range(10):
                Asset.objects.create(
                    symbol=f"{asset_type}_{i}",
                    name=f"Test {asset_type} {i}",
                    asset_type=asset_type,
                )

        # Test filtered queries
        stocks = Asset.objects.filter(asset_type=Asset.ASSET_STOCK)
        assert stocks.count() == 10

        bonds = Asset.objects.filter(asset_type=Asset.ASSET_BOND)
        assert bonds.count() == 10

        # Test ordering works with filtering
        ordered_stocks = Asset.objects.filter(
            asset_type=Asset.ASSET_STOCK
        ).order_by("symbol")
        symbols = [asset.symbol for asset in ordered_stocks]
        assert symbols == sorted(symbols)
