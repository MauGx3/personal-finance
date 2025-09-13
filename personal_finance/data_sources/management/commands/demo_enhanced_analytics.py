"""Enhanced data analysis demonstration command.

This command demonstrates the advanced data analysis capabilities
implemented using modern finance libraries as per S.C.A.F.F. requirements.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import json
from typing import Dict, List, Any

try:
    from personal_finance.data_sources.advanced_analytics import (
        advanced_analyzer, market_enhancer
    )
    from personal_finance.data_sources.polars_integration import polars_processor
    from personal_finance.data_sources.data_cleaning import financial_cleaner
    from personal_finance.data_sources.data_profiling import financial_profiler
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"Warning: Enhanced data analysis modules not available: {e}")


class Command(BaseCommand):
    """Management command to demonstrate enhanced data analysis features."""
    
    help = 'Demonstrate enhanced data analysis capabilities'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--demo-type',
            type=str,
            default='comprehensive',
            choices=['comprehensive', 'portfolio', 'market', 'cleaning', 'performance'],
            help='Type of demo to run'
        )
        
        parser.add_argument(
            '--symbols',
            nargs='+',
            default=['AAPL', 'GOOGL', 'MSFT'],
            help='Stock symbols for demo data'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of data to generate'
        )
        
        parser.add_argument(
            '--output-format',
            type=str,
            default='summary',
            choices=['summary', 'detailed', 'json'],
            help='Output format'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        if not MODULES_AVAILABLE:
            raise CommandError("Enhanced data analysis modules not available")
        
        demo_type = options['demo_type']
        symbols = options['symbols']
        days = options['days']
        output_format = options['output_format']
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Enhanced Data Analysis Demo')
        )
        self.stdout.write(f"Demo type: {demo_type}")
        self.stdout.write(f"Symbols: {', '.join(symbols)}")
        self.stdout.write(f"Days: {days}")
        self.stdout.write("=" * 60)
        
        try:
            if demo_type == 'comprehensive':
                self._run_comprehensive_demo(symbols, days, output_format)
            elif demo_type == 'portfolio':
                self._run_portfolio_demo(symbols, output_format)
            elif demo_type == 'market':
                self._run_market_demo(symbols, days, output_format)
            elif demo_type == 'cleaning':
                self._run_cleaning_demo(output_format)
            elif demo_type == 'performance':
                self._run_performance_demo(symbols, days, output_format)
                
        except Exception as e:
            raise CommandError(f"Demo failed: {e}")
    
    def _run_comprehensive_demo(self, symbols: List[str], days: int, output_format: str):
        """Run comprehensive demo showcasing all features."""
        self.stdout.write(self.style.HTTP_INFO("📊 Comprehensive Data Analysis Demo"))
        
        # 1. Data Cleaning Demo
        self.stdout.write("\n1️⃣ Data Cleaning Demonstration")
        messy_data = self._create_messy_sample_data(symbols)
        cleaned_data = financial_cleaner.clean_portfolio_data(messy_data)
        
        self.stdout.write(f"   ✅ Cleaned {len(messy_data)} records")
        if output_format == 'detailed':
            self.stdout.write(f"   Original: {messy_data[0]}")
            self.stdout.write(f"   Cleaned:  {cleaned_data[0]}")
        
        # 2. Data Profiling Demo
        self.stdout.write("\n2️⃣ Data Profiling Analysis")
        profile_results = financial_profiler.profile_portfolio_data(cleaned_data)
        
        self.stdout.write(f"   ✅ Profiled {len(cleaned_data)} records")
        if 'recommendations' in profile_results:
            self.stdout.write(f"   📋 {len(profile_results['recommendations'])} recommendations")
        
        # 3. Advanced Portfolio Analytics
        self.stdout.write("\n3️⃣ Advanced Portfolio Analytics")
        portfolio_data = self._create_portfolio_sample_data(symbols)
        advanced_metrics = advanced_analyzer.calculate_advanced_metrics(portfolio_data)
        
        self._display_portfolio_metrics(advanced_metrics, output_format)
        
        # 4. Market Data Enhancement
        self.stdout.write("\n4️⃣ Market Data Enhancement")
        price_data = self._create_price_sample_data(symbols, days)
        enhanced_data = market_enhancer.enhance_price_data(price_data)
        
        self.stdout.write(f"   ✅ Enhanced {len(price_data)} price records")
        if hasattr(enhanced_data, 'columns'):
            new_columns = [col for col in enhanced_data.columns 
                          if col not in ['symbol', 'date', 'close_price']]
            self.stdout.write(f"   📈 Added indicators: {', '.join(new_columns)}")
        
        # 5. Market Calendar Info
        self.stdout.write("\n5️⃣ Market Calendar Information")
        calendar_info = advanced_analyzer.get_market_calendar_info()
        self.stdout.write(f"   📅 Exchange: {calendar_info.get('exchange', 'N/A')}")
        self.stdout.write(f"   📊 Trading days this month: {calendar_info.get('trading_days_count', 'N/A')}")
        
        # 6. Security Search
        self.stdout.write("\n6️⃣ Security Search Demo")
        search_results = advanced_analyzer.search_securities("apple")
        self.stdout.write(f"   🔍 Found {len(search_results)} results for 'apple'")
        
        if output_format == 'json':
            self._output_json_results({
                'cleaned_data_count': len(cleaned_data),
                'profile_results': profile_results,
                'advanced_metrics': advanced_metrics,
                'calendar_info': calendar_info,
                'search_results': search_results,
            })
    
    def _run_portfolio_demo(self, symbols: List[str], output_format: str):
        """Run portfolio-focused demo."""
        self.stdout.write(self.style.HTTP_INFO("💼 Portfolio Analysis Demo"))
        
        portfolio_data = self._create_portfolio_sample_data(symbols)
        metrics = advanced_analyzer.calculate_advanced_metrics(portfolio_data)
        
        self._display_portfolio_metrics(metrics, output_format)
        
        # Sector allocation
        if 'sector_allocation' in metrics:
            self.stdout.write("\n📊 Sector Allocation:")
            for sector, weight in metrics['sector_allocation'].items():
                self.stdout.write(f"   {sector}: {weight:.1%}")
        
        # Risk metrics
        if 'risk_metrics' in metrics:
            self.stdout.write("\n⚠️  Risk Analysis:")
            risk = metrics['risk_metrics']
            self.stdout.write(f"   Max position weight: {risk.get('max_position_weight', 0):.1%}")
            self.stdout.write(f"   Number of positions: {risk.get('number_of_positions', 0)}")
            concentration = risk.get('concentration_risk', 0)
            if concentration > 0:
                self.stdout.write(f"   ⚠️  Concentration risk detected: {concentration:.1%}")
    
    def _run_market_demo(self, symbols: List[str], days: int, output_format: str):
        """Run market data demo."""
        self.stdout.write(self.style.HTTP_INFO("📈 Market Data Enhancement Demo"))
        
        price_data = self._create_price_sample_data(symbols, days)
        
        # Test different enhancement scenarios
        indicators_sets = [
            ['volatility'],
            ['momentum'],
            ['trend_strength'],
            ['volatility', 'momentum', 'trend_strength']
        ]
        
        for i, indicators in enumerate(indicators_sets, 1):
            self.stdout.write(f"\n{i}️⃣ Testing indicators: {', '.join(indicators)}")
            enhanced_data = market_enhancer.enhance_price_data(price_data, indicators)
            
            if hasattr(enhanced_data, 'columns'):
                new_cols = [col for col in enhanced_data.columns if col.endswith(('_20d', '_10d', '_strength'))]
                self.stdout.write(f"   ✅ Added columns: {', '.join(new_cols)}")
            else:
                self.stdout.write(f"   ✅ Enhanced {len(enhanced_data)} records")
    
    def _run_cleaning_demo(self, output_format: str):
        """Run data cleaning demo."""
        self.stdout.write(self.style.HTTP_INFO("🧹 Data Cleaning Demo"))
        
        # Create various messy data scenarios
        scenarios = [
            {
                'name': 'Currency Symbols',
                'data': [{'price': '$150.50', 'amount': '€1,234.56'}]
            },
            {
                'name': 'Parentheses Negatives',
                'data': [{'value': '(1,000.00)', 'gain': '($500.00)'}]
            },
            {
                'name': 'Mixed Formats',
                'data': [{'Stock Symbol': 'AAPL', 'Purchase-Date': '2024/01/01'}]
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            self.stdout.write(f"\n{i}️⃣ Scenario: {scenario['name']}")
            original = scenario['data']
            cleaned = financial_cleaner.clean_portfolio_data(original)
            
            if output_format == 'detailed':
                self.stdout.write(f"   Before: {original[0]}")
                self.stdout.write(f"   After:  {cleaned[0]}")
            else:
                self.stdout.write(f"   ✅ Successfully cleaned messy {scenario['name'].lower()}")
    
    def _run_performance_demo(self, symbols: List[str], days: int, output_format: str):
        """Run performance comparison demo."""
        self.stdout.write(self.style.HTTP_INFO("⚡ Performance Comparison Demo"))
        
        import time
        
        # Create larger dataset for meaningful comparison
        large_data = self._create_price_sample_data(symbols * 5, days * 2)
        
        self.stdout.write(f"Testing with {len(large_data)} records...")
        
        # Test Polars vs Pandas performance
        test_scenarios = [
            'create_dataframe',
            'calculate_moving_averages',
            'filter_operations',
        ]
        
        results = {}
        for scenario in test_scenarios:
            self.stdout.write(f"\n📊 Testing: {scenario}")
            
            # Test with Polars
            start_time = time.time()
            self._run_polars_test(large_data, scenario)
            polars_time = time.time() - start_time
            
            # Test with Pandas fallback
            start_time = time.time()
            self._run_pandas_test(large_data, scenario)
            pandas_time = time.time() - start_time
            
            results[scenario] = {
                'polars': polars_time,
                'pandas': pandas_time,
                'speedup': pandas_time / polars_time if polars_time > 0 else 1
            }
            
            self.stdout.write(f"   Polars: {polars_time:.4f}s")
            self.stdout.write(f"   Pandas: {pandas_time:.4f}s")
            self.stdout.write(f"   Speedup: {results[scenario]['speedup']:.2f}x")
        
        if output_format == 'json':
            self._output_json_results({'performance_results': results})
    
    def _run_polars_test(self, data: List[Dict], scenario: str):
        """Run Polars performance test."""
        try:
            if scenario == 'create_dataframe':
                polars_processor.create_price_dataframe(data)
            elif scenario == 'calculate_moving_averages':
                df = polars_processor.create_price_dataframe(data)
                polars_processor.calculate_moving_averages(df, [5, 10])
            elif scenario == 'filter_operations':
                df = polars_processor.create_price_dataframe(data)
                # Simulate filtering operations
                if hasattr(df, 'filter'):
                    df.filter(df['close_price'] > 100)
        except Exception:
            pass  # Fallback handling
    
    def _run_pandas_test(self, data: List[Dict], scenario: str):
        """Run Pandas performance test."""
        try:
            import pandas as pd
            if scenario == 'create_dataframe':
                pd.DataFrame(data)
            elif scenario == 'calculate_moving_averages':
                df = pd.DataFrame(data)
                if 'close_price' in df.columns:
                    df['ma_5'] = df['close_price'].rolling(5).mean()
                    df['ma_10'] = df['close_price'].rolling(10).mean()
            elif scenario == 'filter_operations':
                df = pd.DataFrame(data)
                if 'close_price' in df.columns:
                    df[df['close_price'] > 100]
        except Exception:
            pass  # Fallback handling
    
    def _create_portfolio_sample_data(self, symbols: List[str]) -> List[Dict]:
        """Create sample portfolio data."""
        portfolio = []
        for i, symbol in enumerate(symbols):
            portfolio.append({
                'symbol': symbol,
                'quantity': 100 + (i * 25),
                'cost_basis': float(10000 + (i * 2500)),
                'current_value': float(11000 + (i * 2800)),
                'purchase_date': date.today() - timedelta(days=30 + i * 10),
            })
        return portfolio
    
    def _create_price_sample_data(self, symbols: List[str], days: int) -> List[Dict]:
        """Create sample price data."""
        price_data = []
        base_prices = {'AAPL': 180, 'GOOGL': 2800, 'MSFT': 350}
        
        for symbol in symbols:
            base_price = base_prices.get(symbol, 100)
            for day in range(days):
                date_obj = date.today() - timedelta(days=days - day)
                # Simulate price movement
                price_change = (day % 7 - 3) * 0.02  # Simple price simulation
                price = base_price * (1 + price_change + (day * 0.001))
                
                price_data.append({
                    'symbol': symbol,
                    'date': date_obj.isoformat(),
                    'close_price': round(price, 2),
                    'volume': 1000000 + (day * 10000),
                })
        
        return price_data
    
    def _create_messy_sample_data(self, symbols: List[str]) -> List[Dict]:
        """Create messy sample data for cleaning demo."""
        return [
            {
                'Stock Symbol': symbols[0],
                'Purchase Price': '$150.50',
                'Current Value': '($18,025.00)',
                'Qty Owned': '100',
            },
            {
                'Stock Symbol': symbols[1] if len(symbols) > 1 else 'GOOGL',
                'Purchase Price': '€2,800.75',
                'Current Value': '75,250.00',
                'Qty Owned': '25',
            }
        ]
    
    def _display_portfolio_metrics(self, metrics: Dict[str, Any], output_format: str):
        """Display portfolio metrics."""
        if not metrics:
            self.stdout.write("   ❌ No metrics available")
            return
        
        if output_format == 'summary':
            self.stdout.write(f"   💰 Total Value: ${metrics.get('total_value', 0):,.2f}")
            self.stdout.write(f"   📊 Total Return: ${metrics.get('total_return', 0):,.2f}")
            self.stdout.write(f"   📈 Return %: {metrics.get('return_percentage', 0):.2f}%")
            self.stdout.write(f"   🏢 Holdings: {metrics.get('holdings_count', 0)}")
            
            if 'diversification_score' in metrics:
                score = metrics['diversification_score']
                self.stdout.write(f"   🎯 Diversification: {score:.3f}")
        
        elif output_format == 'detailed':
            for key, value in metrics.items():
                if isinstance(value, dict):
                    self.stdout.write(f"   {key}:")
                    for sub_key, sub_value in value.items():
                        self.stdout.write(f"     {sub_key}: {sub_value}")
                else:
                    self.stdout.write(f"   {key}: {value}")
    
    def _output_json_results(self, results: Dict[str, Any]):
        """Output results in JSON format."""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("JSON Results:")
        self.stdout.write(json.dumps(results, indent=2, default=str))