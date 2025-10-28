"""Assets API serializers."""
from rest_framework import serializers

from .models import Asset, Holding, Portfolio


class AssetSerializer(serializers.ModelSerializer):
    """Serializer for Asset model."""

    asset_type_display = serializers.CharField(
        source="get_asset_type_display",
        read_only=True,
    )
    country_display = serializers.CharField(
        source="get_country_display",
        read_only=True,
    )
    market_display = serializers.CharField(
        source="get_market_display",
        read_only=True,
    )
    display_name = serializers.CharField(
        source="get_display_name",
        read_only=True,
    )
    full_description = serializers.CharField(
        source="get_full_description",
        read_only=True,
    )

    class Meta:
        model = Asset
        fields = [
            "id",
            "ticker",
            "name",
            "asset_type",
            "asset_type_display",
            "country",
            "country_display",
            "market",
            "market_display",
            "description",
            "isin",
            "cusip",
            "sedol",
            "currency",
            "sector",
            "industry",
            "is_active",
            "metadata",
            "display_name",
            "full_description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AssetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Asset instances."""

    class Meta:
        model = Asset
        fields = [
            "ticker",
            "name",
            "asset_type",
            "country",
            "market",
            "description",
            "isin",
            "cusip",
            "sedol",
            "currency",
            "sector",
            "industry",
            "is_active",
            "metadata",
        ]

    def validate_ticker(self, value):
        """Validate ticker format."""
        import re
        if not re.match(r'^[A-Z0-9\-_.]+$', value):
            raise serializers.ValidationError(
                "Ticker must contain only uppercase letters, "
                "numbers, hyphens, underscores, and dots."
            )
        return value.upper()

    def validate_isin(self, value):
        """Validate ISIN format if provided."""
        if value:
            import re
            if not re.match(r'^[A-Z]{2}[A-Z0-9]{10}$', value):
                raise serializers.ValidationError(
                    "ISIN must be 12 characters: 2 letters followed by "
                    "10 alphanumeric characters."
                )
        return value

    def validate_cusip(self, value):
        """Validate CUSIP format if provided."""
        if value:
            import re
            if not re.match(r'^[A-Z0-9]{9}$', value):
                raise serializers.ValidationError(
                    "CUSIP must be exactly 9 alphanumeric characters."
                )
        return value

    def validate_sedol(self, value):
        """Validate SEDOL format if provided."""
        if value:
            import re
            if not re.match(r'^[A-Z0-9]{7}$', value):
                raise serializers.ValidationError(
                    "SEDOL must be exactly 7 alphanumeric characters."
                )
        return value


class AssetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing assets."""

    asset_type_display = serializers.CharField(
        source="get_asset_type_display",
        read_only=True,
    )
    country_display = serializers.CharField(
        source="get_country_display",
        read_only=True,
    )
    market_display = serializers.CharField(
        source="get_market_display",
        read_only=True,
    )

    class Meta:
        model = Asset
        fields = [
            "id",
            "ticker",
            "name",
            "asset_type",
            "asset_type_display",
            "country",
            "country_display",
            "market",
            "market_display",
            "currency",
            "is_active",
            "created_at",
        ]


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for Portfolio model."""

    user_email = serializers.CharField(
        source="user.email",
        read_only=True,
    )
    holdings_count = serializers.IntegerField(
        source="holdings.count",
        read_only=True,
    )
    total_value = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Portfolio
        fields = [
            "id",
            "user",
            "user_email",
            "name",
            "description",
            "is_default",
            "is_active",
            "holdings_count",
            "total_value",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user_email",
            "holdings_count",
            "total_value",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Create portfolio with current user."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class PortfolioListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing portfolios."""

    user_email = serializers.CharField(
        source="user.email",
        read_only=True,
    )
    holdings_count = serializers.IntegerField(
        source="holdings.count",
        read_only=True,
    )

    class Meta:
        model = Portfolio
        fields = [
            "id",
            "name",
            "user_email",
            "is_default",
            "is_active",
            "holdings_count",
            "created_at",
        ]


class HoldingSerializer(serializers.ModelSerializer):
    """Serializer for Holding model."""

    user_email = serializers.CharField(
        source="user.email",
        read_only=True,
    )
    asset_ticker = serializers.CharField(
        source="asset.ticker",
        read_only=True,
    )
    asset_name = serializers.CharField(
        source="asset.name",
        read_only=True,
    )
    portfolio_name = serializers.CharField(
        source="portfolio.name",
        read_only=True,
        allow_null=True,
    )
    total_cost_basis = serializers.DecimalField(
        max_digits=20,
        decimal_places=8,
        read_only=True,
    )
    current_value = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        read_only=True,
    )
    unrealized_gain_loss = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Holding
        fields = [
            "id",
            "user",
            "user_email",
            "asset",
            "asset_ticker",
            "asset_name",
            "portfolio",
            "portfolio_name",
            "quantity",
            "average_price",
            "currency",
            "total_cost_basis",
            "current_value",
            "unrealized_gain_loss",
            "acquired_at",
            "last_transaction_at",
            "is_active",
            "notes",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user_email",
            "asset_ticker",
            "asset_name",
            "portfolio_name",
            "total_cost_basis",
            "current_value",
            "unrealized_gain_loss",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Create holding with current user."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )
        return value

    def validate_average_price(self, value):
        """Validate average price is positive if provided."""
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "Average price must be greater than zero."
            )
        return value


class HoldingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Holding instances."""

    class Meta:
        model = Holding
        fields = [
            "asset",
            "portfolio",
            "quantity",
            "average_price",
            "currency",
            "acquired_at",
            "last_transaction_at",
            "is_active",
            "notes",
            "metadata",
        ]

    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )
        return value

    def validate_average_price(self, value):
        """Validate average price is positive if provided."""
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "Average price must be greater than zero."
            )
        return value


class HoldingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing holdings."""

    user_email = serializers.CharField(
        source="user.email",
        read_only=True,
    )
    asset_ticker = serializers.CharField(
        source="asset.ticker",
        read_only=True,
    )
    asset_name = serializers.CharField(
        source="asset.name",
        read_only=True,
    )
    portfolio_name = serializers.CharField(
        source="portfolio.name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Holding
        fields = [
            "id",
            "user_email",
            "asset_ticker",
            "asset_name",
            "portfolio_name",
            "quantity",
            "average_price",
            "currency",
            "total_cost_basis",
            "current_value",
            "unrealized_gain_loss",
            "is_active",
            "created_at",
        ]
