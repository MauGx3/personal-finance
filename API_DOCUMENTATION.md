# Personal Finance API Documentation

## Overview

The Personal Finance API provides comprehensive RESTful endpoints for portfolio management, asset tracking, analytics, and performance monitoring. This API follows REST principles and includes OpenAPI/Swagger documentation.

## Base URL
```
/api/
```

## Authentication

All endpoints require authentication using Django's token authentication:

```http
Authorization: Token your_api_token_here
```

Get your token via:
```http
POST /api/auth-token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

## API Endpoints

### 🏦 Portfolio Management

#### Portfolios
- `GET /api/portfolios/` - List user's portfolios
- `POST /api/portfolios/` - Create new portfolio
- `GET /api/portfolios/{id}/` - Get portfolio details
- `PUT /api/portfolios/{id}/` - Update portfolio
- `DELETE /api/portfolios/{id}/` - Delete portfolio

**Special Portfolio Endpoints:**
- `GET /api/portfolios/{id}/performance_metrics/` - Get performance metrics
- `GET /api/portfolios/{id}/allocation/` - Get allocation data for charts
- `GET /api/portfolios/{id}/historical_performance/` - Get historical data

#### Positions
- `GET /api/positions/` - List positions (filterable by portfolio)
- `POST /api/positions/` - Create new position
- `GET /api/positions/{id}/` - Get position details
- `PUT /api/positions/{id}/` - Update position
- `DELETE /api/positions/{id}/` - Delete position

#### Transactions
- `GET /api/transactions/` - List transactions (filterable)
- `POST /api/transactions/` - Create new transaction
- `GET /api/transactions/{id}/` - Get transaction details
- `PUT /api/transactions/{id}/` - Update transaction
- `DELETE /api/transactions/{id}/` - Delete transaction

#### Portfolio Snapshots
- `GET /api/portfolio-snapshots/` - List historical snapshots
- `GET /api/portfolio-snapshots/{id}/` - Get snapshot details

### 📈 Asset Management

#### Assets
- `GET /api/assets/` - List assets (searchable and filterable)
- `POST /api/assets/` - Create new asset
- `GET /api/assets/{id}/` - Get asset details
- `PUT /api/assets/{id}/` - Update asset
- `DELETE /api/assets/{id}/` - Delete asset

**Special Asset Endpoints:**
- `GET /api/assets/search/` - Search assets by symbol/name
- `GET /api/assets/{id}/performance_metrics/` - Get asset performance
- `GET /api/assets/{id}/technical_indicators/` - Get technical indicators
- `GET /api/assets/{id}/price_history/` - Get historical prices
- `POST /api/assets/{id}/update_price/` - Manually update price
- `POST /api/assets/{id}/refresh_data/` - Refresh from data sources

#### Price History
- `GET /api/price-history/` - List price history (filterable)
- `GET /api/price-history/{id}/` - Get specific price record

### 📊 Analytics & Risk

#### Market Data
- `GET /api/analytics/market_data/` - Get market indices, sectors, currencies

#### Risk Analytics  
- `GET /api/analytics/correlation_matrix/` - Asset correlation matrix
- `GET /api/analytics/risk_metrics/` - Comprehensive risk metrics
- `GET /api/analytics/asset_allocation_analysis/` - Allocation analysis
- `GET /api/analytics/scenario_analysis/` - Scenario/stress testing

### 👥 User Management

#### Users
- `GET /api/users/` - List users (admin only)
- `GET /api/users/me/` - Get current user profile
- `PUT /api/users/me/` - Update current user profile

## Query Parameters

### Common Filters

**Date Ranges:**
```
?start_date=2024-01-01&end_date=2024-12-31
```

**Portfolio Filtering:**
```
?portfolio_id=1
```

**Asset Filtering:**
```
?asset_type=STOCK&exchange=NASDAQ&sector=Technology
```

**Search:**
```
?search=AAPL
```

**Pagination:**
```
?page=1&page_size=50
```

### Performance Metrics Parameters

```
GET /api/portfolios/1/performance_metrics/
?start_date=2024-01-01
&end_date=2024-12-31
&benchmark=SPY
```

### Allocation Parameters

```
GET /api/portfolios/1/allocation/
?group_by=asset_type|sector|individual
```

### Asset Search Parameters

```
GET /api/assets/search/
?q=apple
&asset_type=STOCK
&exchange=NASDAQ
&limit=20
```

## Response Format

### Success Response
```json
{
    "count": 25,
    "next": "http://api.example.com/api/portfolios/?page=2",
    "previous": null,
    "results": [...]
}
```

### Error Response
```json
{
    "error": "Portfolio not found",
    "details": {
        "code": "not_found",
        "message": "The requested portfolio does not exist or you don't have permission to access it."
    }
}
```

## Data Models

### Portfolio
```json
{
    "id": 1,
    "name": "Growth Portfolio",
    "description": "Long-term growth focused investments",
    "is_active": true,
    "created": "2024-01-15T10:30:00Z",
    "modified": "2024-01-20T15:45:00Z",
    "total_value": "125000.00",
    "total_cost_basis": "100000.00",
    "total_return": "25000.00",
    "total_return_percentage": "25.0000",
    "position_count": 8
}
```

### Position
```json
{
    "id": 1,
    "portfolio": 1,
    "portfolio_name": "Growth Portfolio",
    "asset": {
        "id": 1,
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_type": "STOCK",
        "current_price": "175.50",
        "price_change": "2.50",
        "price_change_percentage": "1.44"
    },
    "quantity": "100.00000000",
    "average_cost": "150.00000000",
    "first_purchase_date": "2024-01-15",
    "total_cost_basis": "15000.00",
    "current_value": "17550.00",
    "unrealized_gain_loss": "2550.00",
    "unrealized_return_percentage": "17.0000"
}
```

### Asset
```json
{
    "id": 1,
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "asset_type": "STOCK",
    "currency": "USD",
    "exchange": "NASDAQ",
    "current_price": "175.50",
    "previous_close": "173.00",
    "price_change": "2.50",
    "price_change_percentage": "1.44",
    "day_high": "176.25",
    "day_low": "174.80",
    "volume": 52847392,
    "market_cap": "2750000000000.00",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "last_price_update": "2024-01-20T20:00:00Z"
}
```

### Performance Metrics
```json
{
    "total_return": "25.5500",
    "total_return_percentage": "25.55",
    "annualized_return": "18.75",
    "volatility": "15.25",
    "sharpe_ratio": "1.23",
    "max_drawdown": "-8.45",
    "var_95": "-2850.00",
    "beta": "1.15",
    "alpha": "3.25",
    "sortino_ratio": "1.67",
    "calmar_ratio": "2.22",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "days_analyzed": 365
}
```

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 422 | Unprocessable Entity | Validation errors |
| 500 | Internal Server Error | Server error |

## Rate Limiting

- **Standard endpoints**: 1000 requests per hour
- **Analytics endpoints**: 100 requests per hour
- **Market data**: 50 requests per hour

## Webhooks (Future)

The API will support webhooks for real-time updates:

- Portfolio value changes
- Price alerts
- Risk threshold breaches
- Transaction notifications

## SDK Examples

### Python
```python
import requests

# Authentication
response = requests.post('/api/auth-token/', {
    'username': 'your_username',
    'password': 'your_password'
})
token = response.json()['token']

headers = {'Authorization': f'Token {token}'}

# Get portfolios
portfolios = requests.get('/api/portfolios/', headers=headers)

# Get performance metrics
metrics = requests.get(
    '/api/portfolios/1/performance_metrics/',
    params={'start_date': '2024-01-01', 'benchmark': 'SPY'},
    headers=headers
)
```

### JavaScript
```javascript
// Authentication
const authResponse = await fetch('/api/auth-token/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'your_username',
        password: 'your_password'
    })
});
const {token} = await authResponse.json();

// Get portfolios
const portfolios = await fetch('/api/portfolios/', {
    headers: {'Authorization': `Token ${token}`}
});

// Create new position
const newPosition = await fetch('/api/positions/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        portfolio: 1,
        asset: 5,
        quantity: '100.0',
        average_cost: '150.0',
        first_purchase_date: '2024-01-15'
    })
});
```

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/api/docs/`
- **OpenAPI Schema**: `/api/schema/`

The schema includes:
- Complete endpoint documentation
- Request/response examples
- Parameter validation rules
- Authentication requirements
- Model schemas with field descriptions

## Best Practices

1. **Pagination**: Always handle paginated responses for list endpoints
2. **Error Handling**: Check response status codes and handle errors gracefully
3. **Rate Limiting**: Implement exponential backoff for rate-limited requests
4. **Data Validation**: Validate data before sending to avoid 422 errors
5. **Security**: Never expose API tokens in client-side code
6. **Caching**: Cache market data and analytics responses appropriately
7. **Bulk Operations**: Use bulk endpoints when available for better performance

## Support

For API support and questions:
- Documentation: `/api/docs/`
- GitHub Issues: Repository issue tracker
- Contact: API support team

---

*This API follows semantic versioning. Current version: v1.0*