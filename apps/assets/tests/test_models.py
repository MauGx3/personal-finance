"""Tests for Asset model."""

from django.test import TestCase

from apps.assets.models import Asset


class TestAsset(TestCase):
    """Test cases for the Asset model."""

    def test_asset_creation(self):
        """Test basic asset creation."""
        asset = Asset(
            ticker="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
            country=Asset.COUNTRY_US,
            market=Asset.MARKET_NASDAQ,
            description="Technology company",
            currency="USD",
            sector="Technology",
            industry="Consumer Electronics",
        )
        self.assertEqual(asset.ticker, "AAPL")
        self.assertEqual(asset.name, "Apple Inc.")
        self.assertEqual(asset.asset_type, Asset.ASSET_STOCK)
        self.assertEqual(asset.country, Asset.COUNTRY_US)
        self.assertEqual(asset.market, Asset.MARKET_NASDAQ)
        self.assertEqual(asset.description, "Technology company")
        self.assertEqual(asset.currency, "USD")
        self.assertEqual(asset.sector, "Technology")
        self.assertEqual(asset.industry, "Consumer Electronics")
        self.assertTrue(asset.is_active)

    def test_asset_string_representation(self):
        """Test string representation of asset."""
        asset = Asset(
            ticker="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
        )
        self.assertEqual(str(asset), "AAPL - Apple Inc.")

    def test_asset_display_name(self):
        """Test display name method."""
        asset = Asset(
            ticker="AAPL",
            name="Apple Inc.",
        )
        self.assertEqual(asset.get_display_name(), "Apple Inc. (AAPL)")

    def test_asset_type_properties(self):
        """Test asset type property methods."""
        stock_asset = Asset(asset_type=Asset.ASSET_STOCK)
        etf_asset = Asset(asset_type=Asset.ASSET_ETF)
        crypto_asset = Asset(asset_type=Asset.ASSET_CRYPTO)
        bond_asset = Asset(asset_type=Asset.ASSET_BOND)

        self.assertTrue(stock_asset.is_equity)
        self.assertTrue(etf_asset.is_equity)
        self.assertFalse(crypto_asset.is_equity)
        self.assertTrue(bond_asset.is_fixed_income)
        self.assertFalse(stock_asset.is_crypto)
        self.assertTrue(crypto_asset.is_crypto)

    def test_asset_full_description(self):
        """Test full description method."""
        asset = Asset(
            ticker="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
            market=Asset.MARKET_NASDAQ,
            country=Asset.COUNTRY_US,
        )
        description = asset.get_full_description()
        self.assertIn("Apple Inc.", description)
        self.assertIn("(AAPL)", description)
        self.assertIn("Stock", description)
        self.assertIn("NASDAQ", description)
        self.assertIn("United States", description)

    def test_asset_unique_ticker(self):
        """Test that ticker must be unique."""
        Asset.objects.create(
            ticker="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
            country=Asset.COUNTRY_US,
            market=Asset.MARKET_NASDAQ,
        )

        with self.assertRaises(Exception):  # IntegrityError
            Asset.objects.create(
                ticker="AAPL",
                name="Another Apple",
                asset_type=Asset.ASSET_STOCK,
                country=Asset.COUNTRY_US,
                market=Asset.MARKET_NASDAQ,
            )

    def test_asset_unique_isin(self):
        """Test that ISIN must be unique if provided."""
        Asset.objects.create(
            ticker="AAPL",
            name="Apple Inc.",
            asset_type=Asset.ASSET_STOCK,
            country=Asset.COUNTRY_US,
            market=Asset.MARKET_NASDAQ,
            isin="US0378331005",
        )

        with self.assertRaises(Exception):  # IntegrityError
            Asset.objects.create(
                ticker="MSFT",
                name="Microsoft",
                asset_type=Asset.ASSET_STOCK,
                country=Asset.COUNTRY_US,
                market=Asset.MARKET_NASDAQ,
                isin="US0378331005",
            )
