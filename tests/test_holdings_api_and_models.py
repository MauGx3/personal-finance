import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from personal_finance.assets.tests.factories import AssetFactory
from personal_finance.assets.tests.factories import HoldingFactory
from personal_finance.assets.tests.factories import PortfolioFactory
from personal_finance.assets.tests.factories import UserFactory

UserModel = get_user_model()


@pytest.mark.django_db
class TestHoldingsApi:
    def test_create_holding_defaults_user(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        asset = AssetFactory()
        payload = {
            "asset": asset.id,
            "quantity": "2.5",
            "average_price": "10.0",
            "currency": "USD",
        }
        resp = client.post("/api/holdings/", payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["user"] == user.id
        assert str(data["quantity"]) == "2.50000000"

    def test_unique_user_asset_portfolio_constraint(self):
        user = UserFactory()
        asset = AssetFactory()
        portfolio = PortfolioFactory(user=user)
        # First one
        HoldingFactory(user=user, asset=asset, portfolio=portfolio)
        # Second with same triplet should fail at API layer as 400
        client = APIClient()
        client.force_authenticate(user=user)
        payload = {
            "asset": asset.id,
            "portfolio": portfolio.id,
            "quantity": "1.0",
        }
        resp = client.post("/api/holdings/", payload, format="json")
        # DRF may raise IntegrityError mapped to 400 by default
        assert resp.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_409_CONFLICT,
        )
