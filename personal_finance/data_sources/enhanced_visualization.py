"""Enhanced visualization module for modern data analysis.

This module provides advanced visualization capabilities leveraging the modern
data analysis stack including Polars, advanced analytics, and interactive charts.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
import json

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = px = None

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = sns = None

try:
    from django.conf import settings
    from django.utils import timezone
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    # Create a simple timezone substitute
    class MockTimezone:
        @staticmethod
        def now():
            return datetime.now()
    timezone = MockTimezone()

logger = logging.getLogger(__name__)


class EnhancedPortfolioVisualizer:
    """Enhanced portfolio visualization using modern libraries."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.plotly_available = PLOTLY_AVAILABLE
        self.matplotlib_available = MATPLOTLIB_AVAILABLE
        self.polars_available = POLARS_AVAILABLE
        self.pandas_available = PANDAS_AVAILABLE
        
        logger.info(f"Enhanced visualizer initialized - "
                   f"plotly: {self.plotly_available}, "
                   f"matplotlib: {self.matplotlib_available}")
    
    def create_advanced_portfolio_dashboard(self, 
                                          portfolio_data: List[Dict],
                                          metrics: Dict[str, Any]) -> Optional[str]:
        """Create an advanced interactive portfolio dashboard.
        
        Args:
            portfolio_data: Portfolio holdings data
            metrics: Portfolio metrics from advanced analyzer
            
        Returns:
            HTML string for the dashboard or None if libraries unavailable
        """
        try:
            if not self.plotly_available:
                return self._create_basic_dashboard_fallback(portfolio_data, metrics)
            
            # Create subplot figure with multiple charts
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Portfolio Allocation', 'Performance Metrics',
                               'Risk Analysis', 'Sector Distribution'),
                specs=[[{"type": "pie"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "pie"}]],
                horizontal_spacing=0.1,
                vertical_spacing=0.15
            )
            
            # 1. Portfolio Allocation (Pie Chart)
            if portfolio_data:
                symbols = [item.get('symbol', '') for item in portfolio_data]
                values = [item.get('current_value', 0) for item in portfolio_data]
                
                fig.add_trace(
                    go.Pie(labels=symbols, values=values, name="Allocation"),
                    row=1, col=1
                )
            
            # 2. Performance Metrics (Bar Chart)
            if metrics:
                metric_names = ['Total Value', 'Total Return', 'Return %']
                metric_values = [
                    metrics.get('total_value', 0),
                    metrics.get('total_return', 0),
                    metrics.get('return_percentage', 0)
                ]
                
                fig.add_trace(
                    go.Bar(x=metric_names, y=metric_values, name="Performance"),
                    row=1, col=2
                )
            
            # 3. Risk Analysis (Scatter Plot)
            if 'risk_metrics' in metrics and portfolio_data:
                symbols = [item.get('symbol', '') for item in portfolio_data]
                values = [item.get('current_value', 0) for item in portfolio_data]
                returns = []
                
                for item in portfolio_data:
                    current_val = item.get('current_value', 0)
                    cost_basis = item.get('cost_basis', 1)
                    return_val = (current_val - cost_basis) / cost_basis if cost_basis > 0 else 0
                    returns.append(return_val)
                
                fig.add_trace(
                    go.Scatter(x=values, y=returns, text=symbols, mode='markers+text',
                              name="Risk-Return", textposition="top center"),
                    row=2, col=1
                )
            
            # 4. Sector Distribution
            if 'sector_allocation' in metrics:
                sectors = list(metrics['sector_allocation'].keys())
                weights = list(metrics['sector_allocation'].values())
                
                fig.add_trace(
                    go.Pie(labels=sectors, values=weights, name="Sectors"),
                    row=2, col=2
                )
            
            # Update layout
            fig.update_layout(
                title_text="Advanced Portfolio Dashboard",
                showlegend=True,
                height=800,
                width=1200
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id="portfolio-dashboard")
            
        except Exception as e:
            logger.error(f"Error creating advanced dashboard: {e}")
            return self._create_basic_dashboard_fallback(portfolio_data, metrics)
    
    def create_technical_analysis_chart(self, 
                                      price_data: Union[List[Dict], pd.DataFrame, pl.DataFrame],
                                      indicators: List[str] = None) -> Optional[str]:
        """Create interactive technical analysis chart.
        
        Args:
            price_data: Price data with technical indicators
            indicators: List of indicators to display
            
        Returns:
            HTML string for the chart or None if libraries unavailable
        """
        try:
            if not self.plotly_available:
                return None
            
            # Convert to pandas for easier plotting
            if isinstance(price_data, list):
                df = pd.DataFrame(price_data) if PANDAS_AVAILABLE else None
            elif isinstance(price_data, pl.DataFrame) and PANDAS_AVAILABLE:
                df = price_data.to_pandas()
            else:
                df = price_data
            
            if df is None or df.empty:
                return None
            
            # Create subplots for main chart and indicators
            rows = 2 if indicators else 1
            fig = make_subplots(
                rows=rows, cols=1,
                shared_xaxes=True,
                subplot_titles=('Price Chart', 'Technical Indicators'),
                row_heights=[0.7, 0.3] if rows > 1 else [1.0],
                vertical_spacing=0.1
            )
            
            # Main price chart
            if 'date' in df.columns and 'close_price' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df['date'], y=df['close_price'], 
                              mode='lines', name='Close Price'),
                    row=1, col=1
                )
                
                # Add moving averages if available
                for col in df.columns:
                    if col.startswith('ma_'):
                        fig.add_trace(
                            go.Scatter(x=df['date'], y=df[col], 
                                      mode='lines', name=col.upper()),
                            row=1, col=1
                        )
                
                # Add Bollinger Bands if available
                if all(col in df.columns for col in ['bb_upper', 'bb_lower', 'bb_middle']):
                    fig.add_trace(
                        go.Scatter(x=df['date'], y=df['bb_upper'], 
                                  mode='lines', name='BB Upper', line=dict(dash='dash')),
                        row=1, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=df['date'], y=df['bb_lower'], 
                                  mode='lines', name='BB Lower', line=dict(dash='dash')),
                        row=1, col=1
                    )
            
            # Technical indicators subplot
            if rows > 1 and indicators:
                for indicator in indicators:
                    if indicator in df.columns:
                        fig.add_trace(
                            go.Scatter(x=df['date'], y=df[indicator], 
                                      mode='lines', name=indicator.upper()),
                            row=2, col=1
                        )
            
            # Update layout
            fig.update_layout(
                title_text="Technical Analysis Chart",
                height=600,
                showlegend=True,
                xaxis_rangeslider_visible=False
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id="technical-chart")
            
        except Exception as e:
            logger.error(f"Error creating technical analysis chart: {e}")
            return None
    
    def create_performance_comparison_chart(self, 
                                          performance_data: Dict[str, Dict]) -> Optional[str]:
        """Create performance comparison chart.
        
        Args:
            performance_data: Performance data from different strategies/periods
            
        Returns:
            HTML string for the chart
        """
        try:
            if not self.plotly_available:
                return None
            
            fig = go.Figure()
            
            # Add performance bars
            categories = list(performance_data.keys())
            values = []
            
            for category, data in performance_data.items():
                if isinstance(data, dict):
                    # Use return percentage if available
                    value = data.get('return_percentage', data.get('total_return', 0))
                else:
                    value = data
                values.append(value)
            
            # Color bars based on performance (green for positive, red for negative)
            colors = ['green' if v >= 0 else 'red' for v in values]
            
            fig.add_trace(
                go.Bar(x=categories, y=values, marker_color=colors, name='Performance')
            )
            
            # Update layout
            fig.update_layout(
                title_text="Performance Comparison",
                xaxis_title="Category",
                yaxis_title="Return (%)",
                height=400,
                showlegend=False
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id="performance-chart")
            
        except Exception as e:
            logger.error(f"Error creating performance comparison chart: {e}")
            return None
    
    def create_risk_return_scatter(self, 
                                 portfolio_data: List[Dict],
                                 benchmark_data: Optional[Dict] = None) -> Optional[str]:
        """Create risk-return scatter plot.
        
        Args:
            portfolio_data: Individual holdings data
            benchmark_data: Optional benchmark data for comparison
            
        Returns:
            HTML string for the chart
        """
        try:
            if not self.plotly_available:
                return None
            
            fig = go.Figure()
            
            # Calculate risk-return for each holding
            symbols = []
            returns = []
            risks = []
            values = []
            
            for holding in portfolio_data:
                symbol = holding.get('symbol', '')
                current_val = holding.get('current_value', 0)
                cost_basis = holding.get('cost_basis', 1)
                
                if cost_basis > 0:
                    return_val = (current_val - cost_basis) / cost_basis
                    # Simple risk approximation (would need historical data for proper calculation)
                    risk_val = abs(return_val) * 0.5  # Simplified risk measure
                    
                    symbols.append(symbol)
                    returns.append(return_val * 100)  # Convert to percentage
                    risks.append(risk_val * 100)
                    values.append(current_val)
            
            if symbols:
                # Create scatter plot with bubble sizes based on position value
                fig.add_trace(
                    go.Scatter(
                        x=risks, y=returns, text=symbols,
                        mode='markers+text',
                        marker=dict(
                            size=[v/max(values)*50 + 10 for v in values] if values else 20,
                            sizemode='diameter',
                            opacity=0.7,
                            color=returns,
                            colorscale='RdYlGn',
                            showscale=True,
                            colorbar=dict(title="Return (%)")
                        ),
                        textposition="middle center",
                        name="Holdings"
                    )
                )
                
                # Add benchmark if provided
                if benchmark_data:
                    bench_return = benchmark_data.get('return_percentage', 0)
                    bench_risk = benchmark_data.get('volatility', 0) * 100
                    
                    fig.add_trace(
                        go.Scatter(
                            x=[bench_risk], y=[bench_return],
                            mode='markers+text',
                            text=['Benchmark'],
                            marker=dict(size=20, color='black', symbol='diamond'),
                            textposition="top center",
                            name="Benchmark"
                        )
                    )
            
            # Update layout
            fig.update_layout(
                title_text="Risk-Return Analysis",
                xaxis_title="Risk (%)",
                yaxis_title="Return (%)",
                height=500,
                showlegend=True
            )
            
            # Add quadrant lines
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.add_vline(x=0, line_dash="dash", line_color="gray")
            
            return fig.to_html(include_plotlyjs='cdn', div_id="risk-return-chart")
            
        except Exception as e:
            logger.error(f"Error creating risk-return scatter: {e}")
            return None
    
    def _create_basic_dashboard_fallback(self, 
                                       portfolio_data: List[Dict],
                                       metrics: Dict[str, Any]) -> str:
        """Create basic HTML dashboard when advanced libraries unavailable."""
        html = """
        <div id="basic-dashboard" style="padding: 20px; font-family: Arial, sans-serif;">
            <h2>Portfolio Dashboard (Basic View)</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div style="border: 1px solid #ccc; padding: 15px; border-radius: 5px;">
                    <h3>Portfolio Summary</h3>
        """
        
        if metrics:
            html += f"""
                    <p><strong>Total Value:</strong> ${metrics.get('total_value', 0):,.2f}</p>
                    <p><strong>Total Return:</strong> ${metrics.get('total_return', 0):,.2f}</p>
                    <p><strong>Return %:</strong> {metrics.get('return_percentage', 0):.2f}%</p>
                    <p><strong>Holdings:</strong> {metrics.get('holdings_count', 0)}</p>
            """
        
        html += """
                </div>
                <div style="border: 1px solid #ccc; padding: 15px; border-radius: 5px;">
                    <h3>Holdings</h3>
        """
        
        if portfolio_data:
            html += "<ul>"
            for holding in portfolio_data[:5]:  # Show first 5 holdings
                symbol = holding.get('symbol', 'N/A')
                value = holding.get('current_value', 0)
                html += f"<li>{symbol}: ${value:,.2f}</li>"
            html += "</ul>"
        
        html += """
                </div>
            </div>
        </div>
        """
        
        return html
    
    def generate_report_data(self, 
                           portfolio_data: List[Dict],
                           metrics: Dict[str, Any],
                           charts: Dict[str, str]) -> Dict[str, Any]:
        """Generate comprehensive report data for templates.
        
        Args:
            portfolio_data: Portfolio holdings data
            metrics: Portfolio metrics
            charts: Dictionary of chart HTML strings
            
        Returns:
            Dictionary containing all report data
        """
        return {
            'portfolio_data': portfolio_data,
            'metrics': metrics,
            'charts': charts,
            'timestamp': timezone.now(),
            'summary': {
                'total_holdings': len(portfolio_data) if portfolio_data else 0,
                'largest_position': max(
                    (h.get('current_value', 0) for h in portfolio_data), 
                    default=0
                ) if portfolio_data else 0,
                'performance_status': 'positive' if metrics.get('total_return', 0) > 0 else 'negative',
                'diversification_level': 'high' if metrics.get('diversification_score', 0) > 0.7 else 'moderate',
            }
        }


# Create global instance for easy importing
enhanced_visualizer = EnhancedPortfolioVisualizer()