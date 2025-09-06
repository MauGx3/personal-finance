import os

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from personal_finance.assets.models import Asset
from personal_finance.assets.models import Holding
from personal_finance.assets.models import Portfolio


@pytest.mark.django_db
def test_create_asset():
    asset = Asset.objects.create(
        symbol="TEST",
        name="Test Asset",
        asset_type=Asset.ASSET_STOCK,
    )
    assert Asset.objects.filter(pk=asset.pk).exists()
    # __str__ should include the symbol
    assert "TEST" in str(asset)


@pytest.mark.django_db
def test_portfolio_and_holding_relationships():
    user_model = get_user_model()
    manager = user_model.objects
    create_user = getattr(manager, "create_user", None)
    if callable(create_user):
        # Some projects use email as the USERNAME_FIELD, others use username.
        # Build kwargs accordingly so the test works with both setups.
        username_field = getattr(user_model, "USERNAME_FIELD", "username")

        kwargs = {
            "password": os.environ.get("TEST_PASSWORD", "pass1234"),
            "email": "test@example.com",
        }
        if username_field != "email":
            # provide a username when the USERNAME_FIELD is not email
            kwargs[username_field] = "testuser"
        user = create_user(**kwargs)
    else:
        # fallback for projects using a custom manager without create_user
        user = manager.create(username="testuser")

    asset = Asset.objects.create(
        symbol="AAA",
        name="Asset AAA",
        asset_type=Asset.ASSET_STOCK,
    )
    portfolio = Portfolio.objects.create(
        user=user,
        name="My Portfolio",
        is_default=True,
    )

    holding = Holding.objects.create(
        user=user,
        asset=asset,
        portfolio=portfolio,
        quantity=1,
    )

    # relationships
    assert holding.user == user
    assert holding.asset == asset
    assert holding.portfolio == portfolio
    assert holding in portfolio.holdings.all()

    # unique constraint: cannot create duplicate holding for same
    # user/asset/portfolio
    with pytest.raises(IntegrityError):
        Holding.objects.create(
            user=user,
            asset=asset,
            portfolio=portfolio,
            quantity=2,
        )
