import pytest
from django.contrib.auth import get_user_model

from personal_finance.assets.models import Asset
from personal_finance.assets.serializers import AssetSerializer


User = get_user_model()


@pytest.mark.django_db
def test_asset_serializer_basic():
    asset = Asset.objects.create(
        symbol="TEST",
        name="Test Asset",
    asset_type="STOCK",
        currency="USD",
        exchange="TESTEX",
        isin="US0000000000",
        cusip="00000000",
        metadata={"foo": "bar"},
        is_active=True,
    )
    serializer = AssetSerializer(asset)
    data = serializer.data
    assert data["symbol"] == "TEST"
    assert data["name"] == "Test Asset"
    assert data["asset_type"] == "STOCK"
    assert data["currency"] == "USD"
    assert data["isin"] == "US0000000000"
    assert "id" in data
