"""Analytics API serializers."""

from rest_framework import serializers


class MarketDataSerializer(serializers.Serializer):
    """Serializer for market data and economic indicators."""

    # Market indices
    market_indices = serializers.DictField(child=serializers.DictField())

    # Economic indicators
    economic_indicators = serializers.DictField(child=serializers.DictField())

    # Sector performance
    sector_performance = serializers.ListField(child=serializers.DictField())

    # Currency rates
    currency_rates = serializers.DictField(
        child=serializers.DecimalField(max_digits=20, decimal_places=8)
    )

    # Market sentiment indicators
    vix = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )

    # Data timestamp
    last_updated = serializers.DateTimeField()

    def to_internal_value(self, data):
        """Convert input data to internal representation."""
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Convert instance to serialized representation."""
        return super().to_representation(instance)

    def create(self, validated_data):
        """Market data is read-only, creation not supported."""
        raise NotImplementedError("MarketDataSerializer is read-only")

    def update(self, instance, validated_data):
        """Market data is read-only, updates not supported."""
        raise NotImplementedError("MarketDataSerializer is read-only")
