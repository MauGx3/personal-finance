Visualization Module Reference
===============================

The visualization module provides comprehensive charting and dashboard capabilities for financial data analysis.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The visualization system delivers:

* **Interactive Dashboards**: Real-time portfolio and asset dashboards
* **Chart Generation**: Programmatic chart creation with Plotly
* **Technical Analysis**: Price charts with technical indicators
* **Performance Visualization**: Portfolio performance tracking and analytics
* **Responsive Design**: Mobile-optimized charts and layouts

.. automodule:: personal_finance.visualization.charts
   :members:
   :undoc-members:

Dashboard Access
----------------

Web Interface
~~~~~~~~~~~~~

* **Main Dashboard**: ``/dashboard/`` - Portfolio overview with summary metrics
* **Portfolio Details**: ``/dashboard/portfolio/{id}/`` - Detailed portfolio analysis
* **Asset Analysis**: ``/dashboard/asset/{id}/`` - Individual asset charts

Dashboard Features
~~~~~~~~~~~~~~~~~~

**Portfolio Overview**
  - Total portfolio value across all accounts
  - Number of active portfolios and positions
  - Top performing assets with color-coded returns
  - Interactive portfolio selection

**Chart Types Available**
  1. **Performance Charts**: Track portfolio value and returns over time
  2. **Allocation Charts**: Visualize asset distribution with interactive pie charts
  3. **Risk Metrics**: Monitor Sharpe ratio, volatility, max drawdown, and beta
  4. **Technical Analysis**: Individual asset charts with indicators

Chart API Reference
-------------------

REST Endpoints
~~~~~~~~~~~~~~

.. http:get:: /dashboard/api/portfolio/{id}/performance/

   Get portfolio performance chart data.

   :query int days: Number of days of history (default: 365)

   **Response:**

   .. code-block:: json

      {
          "figure": "{\"data\": [...], \"layout\": {...}}",
          "title": "Portfolio Performance - Last 365 Days",
          "type": "performance"
      }

.. http:get:: /dashboard/api/portfolio/{id}/allocation/

   Get portfolio allocation chart data.

   **Response:**

   .. code-block:: json

      {
          "figure": "{\"data\": [...], \"layout\": {...}}",
          "title": "Current Asset Allocation",
          "type": "allocation"
      }

.. http:get:: /dashboard/api/asset/{id}/price/

   Get asset price chart with technical indicators.

   :query int days: Number of days of price history
   :query array indicators: Technical indicators to include (sma_20, rsi, macd)

   **Response:**

   .. code-block:: json

      {
          "figure": "{\"data\": [...], \"layout\": {...}}",
          "title": "AAPL Price Chart with Indicators",
          "type": "technical"
      }

Chart Data Structure
~~~~~~~~~~~~~~~~~~~~

All chart endpoints return data in this format:

.. code-block:: python

   {
       'figure': str,    # Plotly JSON string
       'title': str,     # Chart title
       'type': str       # Chart type: performance|allocation|risk|technical|empty
   }

JavaScript Client Usage
-----------------------

Basic Chart Loading
~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   // Load portfolio performance chart
   function loadPerformanceChart(portfolioId, containerId) {
       fetch(`/dashboard/api/portfolio/${portfolioId}/performance/?days=365`)
           .then(response => response.json())
           .then(data => {
               const plotData = JSON.parse(data.figure);
               Plotly.newPlot(containerId, plotData.data, plotData.layout);
           })
           .catch(error => {
               console.error('Failed to load chart:', error);
           });
   }

   // Load asset allocation chart
   function loadAllocationChart(portfolioId, containerId) {
       fetch(`/dashboard/api/portfolio/${portfolioId}/allocation/`)
           .then(response => response.json())
           .then(data => {
               const plotData = JSON.parse(data.figure);
               Plotly.newPlot(containerId, plotData.data, plotData.layout);
           });
   }

Advanced Chart Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   // Technical analysis chart with indicators
   function loadTechnicalChart(assetId, containerId, indicators = ['sma_20', 'rsi']) {
       const params = new URLSearchParams({
           days: 252,
           ...indicators.reduce((acc, indicator) => {
               acc[`indicators`] = indicator;
               return acc;
           }, {})
       });

       fetch(`/dashboard/api/asset/${assetId}/price/?${params}`)
           .then(response => response.json())
           .then(data => {
               if (data.type === 'empty') {
                   showEmptyChartMessage(containerId, data.title);
               } else {
                   const plotData = JSON.parse(data.figure);
                   Plotly.newPlot(containerId, plotData.data, plotData.layout);
               }
           });
   }

   function showEmptyChartMessage(containerId, message) {
       document.getElementById(containerId).innerHTML =
           `<div class=\"alert alert-info\">${message}</div>`;
   }

React Integration
~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   import { useState, useEffect } from 'react';

   function useChartData(url) {
       const [chartData, setChartData] = useState(null);
       const [loading, setLoading] = useState(true);
       const [error, setError] = useState(null);

       useEffect(() => {
           fetch(url)
               .then(response => response.json())
               .then(data => {
                   setChartData(data);
                   setLoading(false);
               })
               .catch(err => {
                   setError(err);
                   setLoading(false);
               });
       }, [url]);

       return { chartData, loading, error };
   }

   function PortfolioChart({ portfolioId, timeframe = 365 }) {
       const url = `/dashboard/api/portfolio/${portfolioId}/performance/?days=${timeframe}`;
       const { chartData, loading, error } = useChartData(url);

       useEffect(() => {
           if (chartData && chartData.type !== 'empty') {
               const plotData = JSON.parse(chartData.figure);
               Plotly.newPlot('chart-container', plotData.data, plotData.layout);
           }
       }, [chartData]);

       if (loading) return <div>Loading chart...</div>;
       if (error) return <div>Error loading chart: {error.message}</div>;
       if (chartData?.type === 'empty') return <div>{chartData.title}</div>;

       return <div id=\"chart-container\" />;
   }

Programmatic Chart Generation
-----------------------------

Chart Services
~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.visualization.charts.PortfolioCharts
   :members:
   :undoc-members:

.. autoclass:: personal_finance.visualization.charts.AssetCharts
   :members:
   :undoc-members:

Python Chart Creation
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

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

Advanced Chart Customization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Custom chart styling
   chart_generator = PortfolioCharts()
   chart_generator.performance_colors = {
       'positive': '#00C851',  # Green for gains
       'negative': '#ff4444',  # Red for losses
       'neutral': '#33b5e5'    # Blue for neutral
   }

   # Generate chart with custom styling
   custom_chart = chart_generator.create_portfolio_performance_chart(
       portfolio, start_date, end_date
   )

Chart Configuration
-------------------

Time Periods
~~~~~~~~~~~~

Available time periods for performance charts:

* **30 Days** - Short-term performance tracking
* **3 Months** - Quarterly analysis
* **6 Months** - Semi-annual review
* **1 Year** - Annual performance (default)
* **2 Years** - Long-term trends

Technical Indicators
~~~~~~~~~~~~~~~~~~~~

Supported indicators for asset price charts:

.. data:: TECHNICAL_INDICATORS

   * **SMA 20** - Simple Moving Average (20 periods)
   * **RSI** - Relative Strength Index (14 periods)
   * **MACD** - Moving Average Convergence Divergence

Indicator Configuration:

.. code-block:: python

   indicators_config = {
       'sma_20': {
           'name': 'SMA (20)',
           'color': '#FFA726',
           'width': 2
       },
       'rsi': {
           'name': 'RSI (14)',
           'color': '#42A5F5',
           'secondary_y': True,
           'range': [0, 100]
       },
       'macd': {
           'name': 'MACD',
           'color': '#66BB6A',
           'secondary_y': True
       }
   }

Interactive Features
--------------------

Chart Interactions
~~~~~~~~~~~~~~~~~~

All charts support these interactive features:

* **Zoom**: Click and drag to zoom into specific time periods
* **Pan**: Hold and drag to pan across the chart
* **Hover**: Hover over data points for detailed information
* **Legend**: Click legend items to show/hide data series
* **Download**: Use toolbar to download charts as images
* **Responsive**: Automatically resize based on container dimensions

Mobile Optimization
~~~~~~~~~~~~~~~~~~~

Charts are optimized for mobile devices:

* Touch-friendly interactions
* Responsive layouts that adjust chart heights
* Simplified hover information for smaller screens
* Optimized loading for slower connections

Error Handling
--------------

Chart Error States
~~~~~~~~~~~~~~~~~~

The system handles various error conditions gracefully:

.. code-block:: python

   # No data available
   if not portfolio.positions.exists():
       return create_empty_chart("No active positions in portfolio")

   # Insufficient data
   if len(price_data) < 30:
       return create_empty_chart("Insufficient data for analysis")

   # API errors
   try:
       chart_data = generate_chart(portfolio)
   except Exception as e:
       logger.error(f"Chart generation failed: {e}")
       return create_empty_chart("Failed to generate chart")

Error Response Format
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

   {
       "error": "Failed to generate chart",
       "message": "Insufficient data for analysis",
       "type": "empty",
       "title": "No Data Available"
   }

Performance Optimization
------------------------

Loading Strategy
~~~~~~~~~~~~~~~~

Charts load asynchronously to prevent UI blocking:

.. code-block:: javascript

   // Show loading state
   function showChartLoading(containerId) {
       document.getElementById(containerId).innerHTML =
           '<div class=\"text-center\"><div class=\"spinner-border\"></div></div>';
   }

   // Load chart with loading state
   function loadChartWithSpinner(url, containerId) {
       showChartLoading(containerId);

       fetch(url)
           .then(response => response.json())
           .then(data => {
               const plotData = JSON.parse(data.figure);
               Plotly.newPlot(containerId, plotData.data, plotData.layout);
           })
           .catch(error => {
               showChartError(containerId, error.message);
           });
   }

Data Optimization
~~~~~~~~~~~~~~~~~

* **Efficient Queries**: Portfolio snapshots queried with date ranges
* **Caching**: Chart data cached where appropriate
* **Pagination**: Large datasets paginated to prevent timeouts
* **Lazy Loading**: Charts loaded on-demand as user navigates

Memory Management
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Efficient data processing
   def generate_performance_data(portfolio, start_date, end_date):
       # Use values_list to reduce memory usage
       snapshots = portfolio.snapshots.filter(
           date__gte=start_date,
           date__lte=end_date
       ).values_list('date', 'total_value', 'daily_return')

       # Process in batches for large datasets
       batch_size = 1000
       for batch in chunk_queryset(snapshots, batch_size):
           yield process_snapshot_batch(batch)

Custom Chart Extensions
-----------------------

Extending Chart Classes
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Custom portfolio chart implementation
   class CustomPortfolioCharts(PortfolioCharts):
       def create_sector_allocation_chart(self, portfolio):
           \"\"\"Create sector-based allocation chart.\"\"\"
           positions = portfolio.positions.select_related('asset__sector')

           sector_allocation = {}
           for position in positions:
               sector = position.asset.sector or 'Unknown'
               sector_allocation[sector] = sector_allocation.get(sector, 0) + float(position.current_value)

           # Generate pie chart
           figure = go.Figure(data=[go.Pie(
               labels=list(sector_allocation.keys()),
               values=list(sector_allocation.values()),
               hole=.3
           )])

           figure.update_layout(title=\"Portfolio by Sector\")
           return self._format_chart_response(figure, \"Sector Allocation\", \"allocation\")

       def create_performance_comparison_chart(self, portfolios, start_date, end_date):
           \"\"\"Compare performance across multiple portfolios.\"\"\"
           figure = go.Figure()

           for portfolio in portfolios:
               snapshots = portfolio.snapshots.filter(
                   date__gte=start_date, date__lte=end_date
               ).order_by('date')

               dates = [s.date for s in snapshots]
               values = [float(s.total_value) for s in snapshots]

               figure.add_trace(go.Scatter(
                   x=dates, y=values,
                   mode='lines',
                   name=portfolio.name
               ))

           figure.update_layout(
               title=\"Portfolio Performance Comparison\",
               xaxis_title=\"Date\",
               yaxis_title=\"Portfolio Value ($)\"
           )

           return self._format_chart_response(figure, \"Performance Comparison\", \"performance\")

Integration Examples
--------------------

Dashboard Integration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # views.py - Dashboard view with charts
   from django.shortcuts import render
   from personal_finance.visualization.charts import PortfolioCharts

   def portfolio_dashboard(request, portfolio_id):
       portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)

       chart_service = PortfolioCharts()

       context = {
           'portfolio': portfolio,
           'chart_urls': {
               'performance': f'/dashboard/api/portfolio/{portfolio_id}/performance/',
               'allocation': f'/dashboard/api/portfolio/{portfolio_id}/allocation/',
               'risk_metrics': f'/dashboard/api/portfolio/{portfolio_id}/risk/'
           }
       }

       return render(request, 'dashboard/portfolio_detail.html', context)

Export Integration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Export chart data for external analysis
   def export_chart_data(portfolio, chart_type, format='json'):
       chart_service = PortfolioCharts()

       if chart_type == 'performance':
           chart_data = chart_service.create_portfolio_performance_chart(portfolio)
       elif chart_type == 'allocation':
           chart_data = chart_service.create_asset_allocation_chart(portfolio)
       else:
           raise ValueError(f\"Unsupported chart type: {chart_type}\")

       if format == 'json':
           return chart_data['figure']
       elif format == 'csv':
           # Convert Plotly data to CSV
           return convert_plotly_to_csv(chart_data['figure'])
       else:
           raise ValueError(f\"Unsupported format: {format}\")

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. **Chart Not Loading**
   - Check browser console for JavaScript errors
   - Verify API endpoint accessibility
   - Ensure Plotly.js library is loaded

2. **No Data Available**
   - Verify portfolio has positions and price history
   - Check date ranges for data availability
   - Review portfolio snapshot generation

3. **Performance Issues**
   - Reduce time range for large datasets
   - Limit number of technical indicators
   - Check database query performance

Debug Tools
~~~~~~~~~~~

.. code-block:: python

   # Enable detailed chart logging
   import logging
   logging.getLogger('personal_finance.visualization').setLevel(logging.DEBUG)

   # Test chart generation directly
   from personal_finance.visualization.charts import PortfolioCharts

   charts = PortfolioCharts()
   chart_data = charts.create_portfolio_performance_chart(portfolio)

   print(f\"Chart type: {chart_data['type']}\")
   print(f\"Chart title: {chart_data['title']}\")
   print(f\"Data length: {len(chart_data['figure'])}\")

See Also
--------

* :doc:`../api/rest_endpoints` - Dashboard API endpoints
* :doc:`portfolios` - Portfolio management
* :doc:`analytics` - Analytics integration with charts
* :doc:`../development/testing` - Testing visualization components
