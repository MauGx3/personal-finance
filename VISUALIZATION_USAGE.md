# Visualization Layer Usage Guide

This guide demonstrates how to use the newly implemented visualization features in the personal finance application.

## Quick Start

### Accessing the Dashboard

1. **Main Dashboard**: Navigate to `/dashboard/` to view your portfolio overview
2. **Portfolio Details**: Click on any portfolio or go to `/dashboard/portfolio/{id}/` for detailed analysis

### Dashboard Features

#### Portfolio Overview
```python
# View all portfolios with summary metrics
- Total portfolio value across all accounts
- Number of active portfolios and positions
- Top performing assets with color-coded returns
- Interactive portfolio selection
```

#### Chart Types Available

1. **Performance Charts**: Track portfolio value and returns over time
2. **Allocation Charts**: Visualize asset distribution with interactive pie charts
3. **Risk Metrics**: Monitor Sharpe ratio, volatility, max drawdown, and beta
4. **Technical Analysis**: Individual asset charts with indicators

## Using the Chart APIs

### Portfolio Performance Chart
```javascript
// Fetch performance data for a portfolio
fetch('/dashboard/api/portfolio/1/performance/?days=365')
  .then(response => response.json())
  .then(data => {
    const plotData = JSON.parse(data.figure);
    Plotly.newPlot('chart-container', plotData.data, plotData.layout);
  });
```

### Asset Allocation Chart
```javascript
// Get current portfolio allocation
fetch('/dashboard/api/portfolio/1/allocation/')
  .then(response => response.json())
  .then(data => {
    const plotData = JSON.parse(data.figure);
    Plotly.newPlot('allocation-chart', plotData.data, plotData.layout);
  });
```

### Technical Analysis Chart
```javascript
// Asset price chart with technical indicators
const indicators = ['sma_20', 'rsi'];
const url = `/dashboard/api/asset/1/price/?days=252&${indicators.map(i => `indicators=${i}`).join('&')}`;

fetch(url)
  .then(response => response.json())
  .then(data => {
    const plotData = JSON.parse(data.figure);
    Plotly.newPlot('price-chart', plotData.data, plotData.layout);
  });
```

## Programmatic Chart Generation

### Creating Charts in Python

```python
from personal_finance.visualization.charts import PortfolioCharts, AssetCharts
from personal_finance.portfolios.models import Portfolio
from personal_finance.assets.models import Asset
from datetime import date, timedelta

# Initialize chart generators
portfolio_charts = PortfolioCharts()
asset_charts = AssetCharts()

# Generate portfolio performance chart
portfolio = Portfolio.objects.get(id=1)
end_date = date.today()
start_date = end_date - timedelta(days=365)

performance_chart = portfolio_charts.create_portfolio_performance_chart(
    portfolio, start_date, end_date
)

# Generate asset allocation chart
allocation_chart = portfolio_charts.create_asset_allocation_chart(portfolio)

# Generate risk metrics chart
risk_chart = portfolio_charts.create_risk_metrics_chart(portfolio)

# Generate asset price chart with technical indicators
asset = Asset.objects.get(symbol='AAPL')
price_chart = asset_charts.create_price_chart_with_indicators(
    asset, days=252, indicators=['sma_20', 'rsi']
)
```

### Chart Data Structure

All chart methods return a dictionary with the following structure:
```python
{
    'figure': '{"data": [...], "layout": {...}}',  # Plotly JSON
    'title': 'Chart Title',
    'type': 'performance|allocation|risk|technical|empty'
}
```

## Dashboard Customization

### Time Period Selection

Available time periods for performance charts:
- Last 30 Days
- Last 3 Months  
- Last 6 Months
- Last Year (default)
- Last 2 Years

### Technical Indicators

Supported technical indicators for asset charts:
- **SMA 20**: Simple Moving Average (20 periods)
- **RSI**: Relative Strength Index (14 periods)
- **MACD**: Moving Average Convergence Divergence

### Chart Interactions

All charts support:
- **Zoom**: Click and drag to zoom into specific time periods
- **Pan**: Hold and drag to pan across the chart
- **Hover**: Hover over data points for detailed information
- **Legend**: Click legend items to show/hide data series
- **Download**: Use the toolbar to download charts as images

## Error Handling

The visualization system includes comprehensive error handling:

```python
# Charts handle missing data gracefully
if not portfolio.positions.exists():
    return create_empty_chart("No active positions in portfolio")

# API errors return structured responses
{
    "error": "Failed to generate chart",
    "message": "Insufficient data for analysis",
    "type": "empty"
}
```

## Performance Considerations

### Chart Loading

- Charts load asynchronously to prevent blocking the UI
- Loading spinners display during data fetch
- Error states provide retry options

### Data Optimization

- Portfolio snapshots are queried efficiently with date ranges
- Chart data is cached where appropriate
- Large datasets are paginated to prevent timeout

### Responsive Design

- Charts automatically resize based on container dimensions
- Mobile-optimized layouts adjust chart heights
- Touch-friendly interactions on mobile devices

## Advanced Usage

### Custom Chart Styling

```python
# Modify chart colors and styling
chart_generator = PortfolioCharts()
chart_generator.performance_colors = {
    'positive': '#00C851',  # Green for gains
    'negative': '#ff4444',  # Red for losses
    'neutral': '#33b5e5'    # Blue for neutral
}
```

### Adding New Chart Types

```python
# Extend the PortfolioCharts class
class CustomPortfolioCharts(PortfolioCharts):
    def create_sector_allocation_chart(self, portfolio):
        """Create sector-based allocation chart."""
        # Implementation here
        pass
```

### Integration with External Systems

```python
# Export chart data for external analysis
chart_data = portfolio_charts.create_performance_chart(portfolio, start, end)
figure_json = chart_data['figure']

# Save to file or send to external API
with open('portfolio_chart.json', 'w') as f:
    f.write(figure_json)
```

## Troubleshooting

### Common Issues

1. **No Data Available**: Ensure portfolio has positions and price history
2. **Chart Not Loading**: Check browser console for JavaScript errors
3. **API Timeout**: Reduce date range or number of indicators

### Debug Mode

Enable Django debug mode to see detailed error messages:
```python
# In settings/local.py
DEBUG = True
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'personal_finance.visualization': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

This visualization layer provides a comprehensive foundation for financial data analysis and can be extended with additional chart types and features as needed.