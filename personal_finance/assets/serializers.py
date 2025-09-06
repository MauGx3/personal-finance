from django.contrib.auth import get_user_model
from rest_framework import serializers

from personal_finance.assets.models import Asset
from personal_finance.assets.models import Holding
from personal_finance.assets.models import Portfolio

UserModel = get_user_model()


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            "id",
            "symbol",
            "name",
            "asset_type",
            "currency",
            "exchange",
            "isin",
            "cusip",
            "metadata",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PortfolioSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=UserModel.objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Portfolio
        fields = [
            "id",
            "user",
            "name",
            "description",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HoldingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=UserModel.objects.all(),
        default=serializers.CurrentUserDefault(),
    )
    asset = serializers.PrimaryKeyRelatedField(queryset=Asset.objects.all())
    portfolio = serializers.PrimaryKeyRelatedField(
        queryset=Portfolio.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Holding
        fields = [
            "id",
            "user",
            "asset",
            "portfolio",
            "quantity",
            "average_price",
            "currency",
            "acquired_at",
            "in_portfolio",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
