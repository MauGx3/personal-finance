"""Tests for chart generation functionality."""

import json
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone

from personal_finance.visualization.charts import PortfolioCharts, AssetCharts


class PortfolioChartsTestCase(TestCase):
    """Test portfolio chart generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.chart_generator = PortfolioCharts()
        
        # Mock portfolio
        self.mock_portfolio = Mock()
        self.mock_portfolio.id = 1
        self.mock_portfolio.name = "Test Portfolio"
        
        # Mock position
        self.mock_position = Mock()
        self.mock_position.asset.symbol = "AAPL"
        self.mock_position.asset.name = "Apple Inc."
        self.mock_position.current_value = Decimal('1000.00')
        self.mock_position.quantity = Decimal('10.00')
        
    def test_create_empty_chart(self):
        """Test creation of empty chart with message."""
        result = self.chart_generator._create_empty_chart("Test message")
        
        self.assertIsInstance(result, dict)
        self.assertIn('figure', result)
        self.assertEqual(result['title'], 'No Data Available')
        self.assertEqual(result['type'], 'empty')
        
        # Verify figure is valid JSON
        figure_data = json.loads(result['figure'])
        self.assertIn('data', figure_data)
        self.assertIn('layout', figure_data)
    
    def test_get_risk_color_sharpe_ratio(self):
        """Test risk color assignment for Sharpe ratio."""
        # Good Sharpe ratio (>= 1)
        self.assertEqual(
            self.chart_generator._get_risk_color(1.5, 'sharpe'), 
            'green'
        )
        
        # Moderate Sharpe ratio (0 to 1)
        self.assertEqual(
            self.chart_generator._get_risk_color(0.5, 'sharpe'), 
            'yellow'
        )
        
        # Poor Sharpe ratio (< 0)
        self.assertEqual(
            self.chart_generator._get_risk_color(-0.5, 'sharpe'), 
            'red'
        )
    
    def test_get_risk_color_drawdown(self):
        """Test risk color assignment for max drawdown."""
        # Low drawdown (<= 10%)
        self.assertEqual(
            self.chart_generator._get_risk_color(5.0, 'drawdown'), 
            'green'
        )
        
        # Moderate drawdown (10-25%)
        self.assertEqual(
            self.chart_generator._get_risk_color(15.0, 'drawdown'), 
            'yellow'
        )
        
        # High drawdown (> 25%)
        self.assertEqual(
            self.chart_generator._get_risk_color(30.0, 'drawdown'), 
            'red'
        )
    
    @patch('personal_finance.visualization.charts.PortfolioSnapshot')
    def test_create_portfolio_performance_chart_no_data(self, mock_snapshot):
        """Test performance chart creation with no data."""
        # Mock empty queryset
        mock_snapshot.objects.filter.return_value.order_by.return_value.exists.return_value = False
        
        start_date = date.today() - timedelta(days=365)
        end_date = date.today()
        
        result = self.chart_generator.create_portfolio_performance_chart(
            self.mock_portfolio, start_date, end_date
        )
        
        self.assertEqual(result['type'], 'empty')
        self.assertIn('No performance data available', result['figure'])
    
    @patch('personal_finance.visualization.charts.Position')
    def test_create_asset_allocation_chart_no_positions(self, mock_position):
        """Test allocation chart creation with no positions."""
        # Mock empty positions
        self.mock_portfolio.positions.filter.return_value.exists.return_value = False
        
        result = self.chart_generator.create_asset_allocation_chart(self.mock_portfolio)
        
        self.assertEqual(result['type'], 'empty')
        self.assertIn('No active positions', result['figure'])


class AssetChartsTestCase(TestCase):
    """Test asset chart generation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.chart_generator = AssetCharts()
        
        # Mock asset
        self.mock_asset = Mock()
        self.mock_asset.id = 1
        self.mock_asset.symbol = "AAPL"
        self.mock_asset.name = "Apple Inc."
    
    def test_create_empty_chart(self):
        """Test creation of empty asset chart."""
        result = self.chart_generator._create_empty_chart("No data")
        
        self.assertIsInstance(result, dict)
        self.assertIn('figure', result)
        self.assertEqual(result['title'], 'No Data Available')
        self.assertEqual(result['type'], 'empty')
    
    @patch('personal_finance.visualization.charts.PriceHistory')
    def test_create_price_chart_no_data(self, mock_price_history):
        """Test price chart creation with no historical data."""
        # Mock empty queryset
        mock_price_history.objects.filter.return_value.order_by.return_value.exists.return_value = False
        
        result = self.chart_generator.create_price_chart_with_indicators(
            self.mock_asset, days=252
        )
        
        self.assertEqual(result['type'], 'empty')
        self.assertIn('No price data', result['figure'])


class ChartIntegrationTestCase(TestCase):
    """Test chart component integration."""
    
    def test_chart_data_structure(self):
        """Test that chart data follows expected structure."""
        chart_generator = PortfolioCharts()
        result = chart_generator._create_empty_chart("Test")
        
        # Verify required keys
        required_keys = ['figure', 'title', 'type']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Verify figure is valid JSON
        try:
            figure_data = json.loads(result['figure'])
            self.assertIsInstance(figure_data, dict)
        except json.JSONDecodeError:
            self.fail("Chart figure should be valid JSON")
    
    def test_default_colors_available(self):
        """Test that default color schemes are available."""
        chart_generator = PortfolioCharts()
        
        self.assertIsNotNone(chart_generator.default_colors)
        self.assertIsInstance(chart_generator.performance_colors, dict)
        
        # Check required performance colors
        required_colors = ['positive', 'negative', 'neutral']
        for color in required_colors:
            self.assertIn(color, chart_generator.performance_colors)