"""Chart generation utilities using Plotly for financial data visualization.

This module provides comprehensive charting capabilities for portfolio analysis,
performance tracking, and asset visualization using Plotly for interactive charts.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, date, timedelta

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from django.utils import timezone

try:
    from personal_finance.portfolios.models import Portfolio, Position, PortfolioSnapshot
except ImportError:
    Portfolio = Position = PortfolioSnapshot = None

try:
    from personal_finance.assets.models import Asset
except ImportError:
    Asset = None

# Try to import PriceHistory model if it exists, otherwise use stub
try:
    from personal_finance.assets.models import PriceHistory
except ImportError:
    # PriceHistory doesn't exist in current schema - will be added later
    from personal_finance.assets.stubs import PriceHistory, PriceHistoryStubManager
try:
    from personal_finance.analytics.services import PerformanceAnalytics, TechnicalIndicators
except ImportError:
    PerformanceAnalytics = TechnicalIndicators = None

logger = logging.getLogger(__name__)


class PortfolioCharts:
    """Generate interactive charts for portfolio analysis and visualization.
    
    This class provides methods to create various chart types for portfolio
    performance analysis, asset allocation, and risk metrics using Plotly.
    """
    
    def __init__(self):
        """Initialize chart generator with default styling."""
        # Check if Plotly is available
        try:
            self.default_colors = px.colors.qualitative.Set3
            self.performance_colors = {
                'positive': '#00C851',
                'negative': '#ff4444',
                'neutral': '#33b5e5'
            }
        except (AttributeError, ImportError):
            # Fallback if plotly is not available
            self.default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            self.performance_colors = {
                'positive': '#00C851',
                'negative': '#ff4444', 
                'neutral': '#33b5e5'
            }
    
    def create_portfolio_performance_chart(self, 
                                         portfolio: Portfolio,
                                         start_date: date,
                                         end_date: date) -> Dict[str, Any]:
        """Create portfolio performance chart over time.
        
        Args:
            portfolio: Portfolio instance to chart
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary containing Plotly figure JSON and metadata
            
        Raises:
            ValueError: If no performance data is available for the period
        """
        # Check if required models are available
        if PortfolioSnapshot is None:
            logger.warning("PortfolioSnapshot model not available")
            return self._create_empty_chart("Portfolio snapshots not available")
        
        try:
            # Get portfolio snapshots for the period
            snapshots = PortfolioSnapshot.objects.filter(
                portfolio=portfolio,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            if not snapshots.exists():
                logger.warning(f"No snapshot data for portfolio {portfolio.id}")
                return self._create_empty_chart("No performance data available")
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame([{
                'date': snapshot.date,
                'total_value': float(snapshot.total_value),
                'total_return': float(snapshot.total_return_percent),
                'daily_return': float(snapshot.daily_return_percent or 0)
            } for snapshot in snapshots])
            
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                subplot_titles=('Portfolio Value', 'Daily Returns'),
                row_heights=[0.7, 0.3]
            )
            
            # Portfolio value line chart
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['total_value'],
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='#2E86AB', width=2),
                    hovertemplate='<b>%{x}</b><br>Value: $%{y:,.2f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Daily returns bar chart
            colors = [self.performance_colors['positive'] if ret >= 0 
                     else self.performance_colors['negative'] 
                     for ret in df['daily_return']]
            
            fig.add_trace(
                go.Bar(
                    x=df['date'],
                    y=df['daily_return'],
                    name='Daily Return',
                    marker_color=colors,
                    hovertemplate='<b>%{x}</b><br>Return: %{y:.2f}%<extra></extra>'
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title=f'{portfolio.name} Performance',
                showlegend=True,
                height=600,
                template='plotly_white',
                hovermode='x unified'
            )
            
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="Portfolio Value ($)", row=1, col=1)
            fig.update_yaxes(title_text="Daily Return (%)", row=2, col=1)
            
            return {
                'figure': fig.to_json(),
                'title': f'{portfolio.name} Performance',
                'type': 'performance'
            }
            
        except Exception as e:
            logger.error(f"Error creating performance chart: {e}")
            return self._create_empty_chart("Error generating performance chart")
    
    def create_asset_allocation_chart(self, portfolio) -> Dict[str, Any]:
        """Create pie chart showing portfolio asset allocation.
        
        Args:
            portfolio: Portfolio instance to analyze
            
        Returns:
            Dictionary containing Plotly figure JSON and metadata
        """
        # Check if required models are available
        if Portfolio is None or Position is None:
            logger.warning("Portfolio or Position models not available")
            return self._create_empty_chart("Portfolio models not available")
        try:
            positions = portfolio.positions.filter(is_active=True)
            
            if not positions.exists():
                return self._create_empty_chart("No active positions in portfolio")
            
            # Calculate allocation data
            allocation_data = []
            total_value = Decimal('0')
            
            for position in positions:
                current_value = position.current_value
                total_value += current_value
                allocation_data.append({
                    'symbol': position.asset.symbol,
                    'name': position.asset.name,
                    'value': float(current_value),
                    'quantity': float(position.quantity)
                })
            
            # Calculate percentages
            for item in allocation_data:
                item['percentage'] = (item['value'] / float(total_value)) * 100
            
            # Sort by value
            allocation_data.sort(key=lambda x: x['value'], reverse=True)
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=[f"{item['symbol']}<br>{item['name']}" for item in allocation_data],
                values=[item['percentage'] for item in allocation_data],
                hovertemplate='<b>%{label}</b><br>' +
                             'Value: $%{customdata:,.2f}<br>' +
                             'Allocation: %{percent}<br>' +
                             '<extra></extra>',
                customdata=[item['value'] for item in allocation_data],
                textinfo='label+percent',
                textposition='auto',
                marker_colors=self.default_colors[:len(allocation_data)]
            )])
            
            fig.update_layout(
                title=f'{portfolio.name} Asset Allocation',
                template='plotly_white',
                height=500,
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
            )
            
            return {
                'figure': fig.to_json(),
                'title': f'{portfolio.name} Asset Allocation',
                'type': 'allocation'
            }
            
        except Exception as e:
            logger.error(f"Error creating allocation chart: {e}")
            return self._create_empty_chart("Error generating allocation chart")
    
    def create_risk_metrics_chart(self, portfolio) -> Dict[str, Any]:
        """Create risk metrics visualization chart.
        
        Args:
            portfolio: Portfolio instance to analyze
            
        Returns:
            Dictionary containing Plotly figure JSON and metadata
        """
        # Check if required models are available
        if Portfolio is None or PerformanceAnalytics is None:
            logger.warning("Portfolio model or PerformanceAnalytics not available")
            return self._create_empty_chart("Risk analysis not available")
        
        try:
            analytics = PerformanceAnalytics()
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=365)
            
            # Calculate risk metrics
            metrics = analytics.calculate_portfolio_metrics(
                portfolio, start_date, end_date
            )
            
            if not metrics or all(v is None for v in metrics.values()):
                return self._create_empty_chart("Insufficient data for risk analysis")
            
            # Create gauge charts for key metrics
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Sharpe Ratio', 'Max Drawdown', 'Volatility', 'Beta'),
                specs=[[{"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "indicator"}]]
            )
            
            # Sharpe Ratio gauge
            sharpe = metrics.get('sharpe_ratio', 0) or 0
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=sharpe,
                title={'text': "Sharpe Ratio"},
                gauge={'axis': {'range': [-2, 3]},
                       'bar': {'color': self._get_risk_color(sharpe, 'sharpe')},
                       'steps': [{'range': [-2, 0], 'color': "lightgray"},
                                {'range': [0, 1], 'color': "yellow"},
                                {'range': [1, 3], 'color': "green"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 1}}
            ), row=1, col=1)
            
            # Max Drawdown gauge
            max_drawdown = abs(metrics.get('max_drawdown', 0) or 0)
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=max_drawdown,
                title={'text': "Max Drawdown (%)"},
                gauge={'axis': {'range': [0, 50]},
                       'bar': {'color': self._get_risk_color(max_drawdown, 'drawdown')},
                       'steps': [{'range': [0, 10], 'color': "green"},
                                {'range': [10, 25], 'color': "yellow"},
                                {'range': [25, 50], 'color': "red"}]}
            ), row=1, col=2)
            
            # Volatility gauge
            volatility = (metrics.get('volatility', 0) or 0) * 100
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=volatility,
                title={'text': "Volatility (%)"},
                gauge={'axis': {'range': [0, 40]},
                       'bar': {'color': self._get_risk_color(volatility, 'volatility')},
                       'steps': [{'range': [0, 15], 'color': "green"},
                                {'range': [15, 25], 'color': "yellow"},
                                {'range': [25, 40], 'color': "red"}]}
            ), row=2, col=1)
            
            # Beta gauge
            beta = metrics.get('beta', 1) or 1
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=beta,
                title={'text': "Beta"},
                gauge={'axis': {'range': [0, 2]},
                       'bar': {'color': self._get_risk_color(beta, 'beta')},
                       'steps': [{'range': [0, 0.8], 'color': "green"},
                                {'range': [0.8, 1.2], 'color': "yellow"},
                                {'range': [1.2, 2], 'color': "red"}],
                       'threshold': {'line': {'color': "blue", 'width': 4},
                                   'thickness': 0.75, 'value': 1}}
            ), row=2, col=2)
            
            fig.update_layout(
                title=f'{portfolio.name} Risk Metrics',
                template='plotly_white',
                height=600
            )
            
            return {
                'figure': fig.to_json(),
                'title': f'{portfolio.name} Risk Metrics',
                'type': 'risk'
            }
            
        except Exception as e:
            logger.error(f"Error creating risk metrics chart: {e}")
            return self._create_empty_chart("Error generating risk metrics chart")
    
    def _get_risk_color(self, value: float, metric_type: str) -> str:
        """Get appropriate color based on risk metric value.
        
        Args:
            value: Metric value
            metric_type: Type of risk metric
            
        Returns:
            Color string for the metric
        """
        if metric_type == 'sharpe':
            if value >= 1:
                return 'green'
            elif value >= 0:
                return 'yellow'
            else:
                return 'red'
        elif metric_type == 'drawdown':
            if value <= 10:
                return 'green'
            elif value <= 25:
                return 'yellow'
            else:
                return 'red'
        elif metric_type == 'volatility':
            if value <= 15:
                return 'green'
            elif value <= 25:
                return 'yellow'
            else:
                return 'red'
        elif metric_type == 'beta':
            if 0.8 <= value <= 1.2:
                return 'yellow'
            elif value < 0.8:
                return 'green'
            else:
                return 'red'
        
        return 'blue'  # Default color
    
    def _create_empty_chart(self, message: str) -> Dict[str, Any]:
        """Create empty chart with message.
        
        Args:
            message: Message to display
            
        Returns:
            Dictionary containing empty chart JSON
        """
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            template='plotly_white',
            height=400,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
        )
        
        return {
            'figure': fig.to_json(),
            'title': 'No Data Available',
            'type': 'empty'
        }


class AssetCharts:
    """Generate charts for individual asset analysis and technical indicators."""
    
    def __init__(self):
        """Initialize asset chart generator."""
        self.technical_indicators = TechnicalIndicators()
    
    def create_price_chart_with_indicators(self, 
                                         asset: Asset,
                                         days: int = 252,
                                         indicators: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create price chart with technical indicators.
        
        Args:
            asset: Asset to chart
            days: Number of days of historical data
            indicators: List of technical indicators to include
            
        Returns:
            Dictionary containing Plotly figure JSON and metadata
        """
        # Check if required models are available
        if PriceHistory is None:
            logger.warning("PriceHistory model not available")
            return self._create_empty_chart("Price history not available")
        
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get price history
            price_history = PriceHistory.objects.filter(
                asset=asset,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            if not price_history.exists():
                return self._create_empty_chart(f"No price data for {asset.symbol}")
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'date': ph.date,
                'open': float(ph.open_price),
                'high': float(ph.high_price),
                'low': float(ph.low_price),
                'close': float(ph.close_price),
                'volume': int(ph.volume)
            } for ph in price_history])
            
            # Create candlestick chart
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                subplot_titles=(f'{asset.symbol} Price', 'Volume', 'Indicators'),
                row_heights=[0.6, 0.2, 0.2]
            )
            
            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                ),
                row=1, col=1
            )
            
            # Volume chart
            fig.add_trace(
                go.Bar(
                    x=df['date'],
                    y=df['volume'],
                    name='Volume',
                    marker_color='lightblue'
                ),
                row=2, col=1
            )
            
            # Add technical indicators if requested
            if indicators:
                self._add_technical_indicators(fig, df, asset, indicators)
            
            fig.update_layout(
                title=f'{asset.symbol} - {asset.name}',
                template='plotly_white',
                height=800,
                xaxis_rangeslider_visible=False
            )
            
            fig.update_xaxes(title_text="Date", row=3, col=1)
            fig.update_yaxes(title_text="Price ($)", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_yaxes(title_text="Indicator Value", row=3, col=1)
            
            return {
                'figure': fig.to_json(),
                'title': f'{asset.symbol} Technical Analysis',
                'type': 'technical'
            }
            
        except Exception as e:
            logger.error(f"Error creating price chart: {e}")
            return self._create_empty_chart("Error generating price chart")
    
    def _add_technical_indicators(self, 
                                fig: go.Figure, 
                                df: pd.DataFrame, 
                                asset: Asset,
                                indicators: List[str]) -> None:
        """Add technical indicators to price chart.
        
        Args:
            fig: Plotly figure to modify
            df: Price data DataFrame
            asset: Asset instance
            indicators: List of indicator names to add
        """
        for indicator in indicators:
            try:
                if indicator.lower() == 'sma_20':
                    sma_data = self.technical_indicators.simple_moving_average(
                        asset, period=20, days=len(df)
                    )
                    if sma_data:
                        fig.add_trace(
                            go.Scatter(
                                x=df['date'],
                                y=[float(d['sma']) for d in sma_data],
                                name='SMA 20',
                                line=dict(color='orange')
                            ),
                            row=1, col=1
                        )
                
                elif indicator.lower() == 'rsi':
                    rsi_data = self.technical_indicators.relative_strength_index(
                        asset, period=14, days=len(df)
                    )
                    if rsi_data:
                        fig.add_trace(
                            go.Scatter(
                                x=df['date'],
                                y=[float(d['rsi']) for d in rsi_data],
                                name='RSI',
                                line=dict(color='purple')
                            ),
                            row=3, col=1
                        )
                        
                        # Add RSI reference lines
                        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
                        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
                
            except Exception as e:
                logger.warning(f"Failed to add indicator {indicator}: {e}")
    
    def _create_empty_chart(self, message: str) -> Dict[str, Any]:
        """Create empty chart with message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            template='plotly_white',
            height=400,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False)
        )
        
        return {
            'figure': fig.to_json(),
            'title': 'No Data Available',
            'type': 'empty'
        }