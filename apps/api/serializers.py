"""REST serializers."""

from rest_framework import serializers

from apps.assets.models import Asset
from apps.portfolios.models import Holding, Portfolio, Transaction


class AssetSerializer(serializers.ModelSerializer):
    quote_symbol = serializers.CharField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            "id", "ticker", "exchange", "name", "asset_class", "currency", "isin",
            "sector", "provider_symbol", "quote_symbol", "is_active",
        ]  # fmt: skip


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ["id", "name", "description", "is_default", "created_at"]
        read_only_fields = ["created_at"]


class OwnedPortfolioField(serializers.PrimaryKeyRelatedField):
    """Only the requesting user's portfolios are valid targets."""

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.context["request"].user)


class TransactionSerializer(serializers.ModelSerializer):
    portfolio = OwnedPortfolioField()
    ticker = serializers.CharField(source="asset.ticker", read_only=True)
    total = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id", "portfolio", "asset", "ticker", "kind", "trade_date", "quantity", "price",
            "fees", "amount", "total", "currency", "broker", "notes",
        ]  # fmt: skip

    def validate(self, attrs):
        instance = Transaction(**{**self._current_values(), **attrs})
        instance.clean()
        return attrs

    def _current_values(self) -> dict:
        if not self.instance:
            return {}
        return {
            f: getattr(self.instance, f) for f in ("kind", "quantity", "price", "fees", "amount")
        }


class HoldingSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(source="asset.ticker", read_only=True)
    currency = serializers.CharField(source="asset.currency", read_only=True)
    cost_basis = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)

    class Meta:
        model = Holding
        fields = [
            "id", "portfolio", "asset", "ticker", "currency", "quantity", "average_price",
            "cost_basis", "realized_gain", "income", "first_trade", "last_trade", "ledger_error",
        ]  # fmt: skip
