# Assets App

This app provides financial asset management functionality for the Personal Finance application.

## Models

### Asset

The `Asset` model represents financial assets such as stocks, ETFs, bonds, cryptocurrencies, etc.

#### Key Fields

- **ticker**: Unique symbol/ticker (e.g., "AAPL", "BTC-USD")
- **name**: Full asset name
- **asset_type**: Type of asset (Stock, ETF, Crypto, Bond, etc.)
- **country**: Country where the asset is primarily traded
- **market**: Primary market/exchange (NYSE, NASDAQ, LSE, etc.)
- **description**: Optional description
- **isin**: International Securities Identification Number
- **cusip**: CUSIP identifier
- **sedol**: SEDOL identifier
- **currency**: Asset currency (ISO 4217 code)
- **sector**: Industry sector
- **industry**: Specific industry
- **is_active**: Whether the asset is currently active
- **metadata**: JSON field for additional data

#### Asset Types

- STOCK: Traditional stocks
- ETF: Exchange-traded funds
- BOND: Fixed income securities
- CRYPTO: Cryptocurrencies
- FUND: Mutual funds
- FOREX: Foreign exchange
- COMMODITY: Commodities
- REAL_ESTATE: Real estate assets
- DERIVATIVE: Derivative instruments

#### Usage Examples

```python
from apps.assets.models import Asset

# Create a stock asset
apple = Asset.objects.create(
    ticker="AAPL",
    name="Apple Inc.",
    asset_type=Asset.ASSET_STOCK,
    country=Asset.COUNTRY_US,
    market=Asset.MARKET_NASDAQ,
    sector="Technology",
    industry="Consumer Electronics",
    currency="USD",
)

# Check asset properties
if apple.is_equity:
    print(f"{apple.name} is an equity")

# Get display information
print(apple.get_display_name())  # "Apple Inc. (AAPL)"
print(apple.get_full_description())  # "Apple Inc. (AAPL) - Stock on NASDAQ (United States)"
```

## API

The app includes REST API serializers for CRUD operations:

- `AssetSerializer`: Full asset serialization with display fields
- `AssetCreateSerializer`: For creating assets with validation
- `AssetListSerializer`: Lightweight serialization for listings

## Admin

The Asset model is registered with Django admin with comprehensive filtering and search capabilities.

## Testing

Unit tests are provided in `tests/test_models.py` covering:

- Asset creation and validation
- String representations
- Property methods
- Uniqueness constraints
- Display methods

Run tests with:

```bash
python manage.py test apps.assets
```
