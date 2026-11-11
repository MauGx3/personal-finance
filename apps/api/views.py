"""REST API. Every endpoint is scoped to the authenticated user's data."""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.assets.models import Asset
from apps.core.money import quantize_money
from apps.portfolios.models import Holding, Portfolio, Transaction
from apps.portfolios.services.valuation import snapshot

from .serializers import (
    AssetSerializer,
    HoldingSerializer,
    PortfolioSerializer,
    TransactionSerializer,
)


def _money(value):
    return None if value is None else str(quantize_money(value))


class AssetViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """The shared asset catalog. Assets are never deleted, only deactivated."""

    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    filterset_fields = ["exchange", "asset_class", "currency", "is_active"]
    search_fields = ["ticker", "name", "isin"]


class PortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioSerializer
    queryset = Portfolio.objects.none()  # for schema generation; see get_queryset

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)

    @action(detail=True)
    def valuation(self, request, pk=None):
        """Holdings valued at the latest stored prices, in the base currency."""
        result = snapshot([self.get_object()])
        return Response(
            {
                "base_currency": result.base_currency,
                "as_of": result.as_of,
                "total_value": _money(result.total_value),
                "total_cost": _money(result.total_cost),
                "unrealized_gain": _money(result.unrealized_gain),
                "realized_gain": _money(result.realized_gain),
                "income": _money(result.income),
                "unpriced": result.unpriced,
                "missing_fx": result.missing_fx,
                "positions": [
                    {
                        "ticker": row.asset.ticker,
                        "currency": row.asset.currency,
                        "quantity": str(row.quantity.normalize()),
                        "average_price": _money(row.average_price),
                        "price": _money(row.price),
                        "price_day": row.price_day,
                        "value": _money(row.value),
                        "value_base": _money(row.value_base),
                        "gain": _money(row.gain),
                        "weight_pct": _money(row.weight),
                    }
                    for row in result.rows
                ],
            }
        )


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.none()  # for schema generation; see get_queryset
    filterset_fields = ["portfolio", "asset", "kind", "trade_date"]
    ordering_fields = ["trade_date", "id"]

    def get_queryset(self):
        return Transaction.objects.filter(portfolio__user=self.request.user).select_related("asset")

    def get_serializer(self, *args, **kwargs):
        try:
            return super().get_serializer(*args, **kwargs)
        except DjangoValidationError as exc:  # pragma: no cover - defensive
            raise ValidationError(exc.message_dict) from exc


class HoldingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HoldingSerializer
    queryset = Holding.objects.none()  # for schema generation; see get_queryset
    filterset_fields = ["portfolio", "asset"]

    def get_queryset(self):
        return Holding.objects.filter(portfolio__user=self.request.user).select_related("asset")
