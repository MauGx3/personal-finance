"""Test portfolio detail view."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.assets.models import Asset, Holding, Portfolio


class PortfolioDetailViewTest(TestCase):
    """Test portfolio detail view."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client = Client()

    def test_portfolio_detail_view_requires_login(self):
        """Test that portfolio detail view requires authentication."""
        response = self.client.get(reverse("assets:portfolio-detail"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_portfolio_detail_view_with_no_portfolio(self):
        """Test portfolio detail view when user has no portfolios."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("assets:portfolio-detail"))
        self.assertEqual(response.status_code, 200)
        # Should show empty state
        self.assertIn(b"No Holdings Yet", response.content)

    def test_portfolio_detail_view_with_portfolio(self):
        """Test portfolio detail view with a portfolio and holdings."""
        # Create portfolio
        portfolio = Portfolio.objects.create(
            user=self.user, name="Test Portfolio", description="A test portfolio"
        )

        # Create asset
        asset = Asset.objects.create(ticker="AAPL", name="Apple Inc.", asset_type="STOCK")

        # Create holding
        Holding.objects.create(
            user=self.user,
            asset=asset,
            portfolio=portfolio,
            quantity=10.0,
            average_price=150.00,
            currency="USD",
        )

        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("assets:portfolio-detail"))
        self.assertEqual(response.status_code, 200)

        # Should contain portfolio and asset info
        self.assertIn(b"Test Portfolio", response.content)
        self.assertIn(b"AAPL", response.content)
        self.assertIn(b"Apple Inc.", response.content)

    def test_portfolio_detail_view_specific_portfolio(self):
        """Test accessing a specific portfolio by ID."""
        # Create two portfolios
        portfolio1 = Portfolio.objects.create(user=self.user, name="Portfolio 1")
        Portfolio.objects.create(user=self.user, name="Portfolio 2")

        self.client.login(username="testuser", password="testpass")

        # Access specific portfolio
        url = reverse("assets:portfolio-detail-id", args=[portfolio1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Portfolio 1", response.content)
        self.assertNotIn(b"Portfolio 2", response.content)
