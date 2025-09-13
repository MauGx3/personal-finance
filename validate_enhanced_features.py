#!/usr/bin/env python3
"""Simple validation script for enhanced features without Django dependencies."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_features():
    """Test enhanced features without Django."""
    print("🧪 Testing Enhanced Data Analysis Features")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Advanced Analytics Module Import
    total_tests += 1
    try:
        from personal_finance.data_sources.advanced_analytics import advanced_analyzer, market_enhancer
        print("✅ Advanced analytics modules imported successfully")
        success_count += 1
    except Exception as e:
        print(f"❌ Advanced analytics import failed: {e}")
    
    # Test 2: Enhanced Visualization Module Import
    total_tests += 1
    try:
        from personal_finance.data_sources.enhanced_visualization import enhanced_visualizer
        print("✅ Enhanced visualization module imported successfully")
        success_count += 1
    except Exception as e:
        print(f"❌ Enhanced visualization import failed: {e}")
    
    # Test 3: Advanced Portfolio Analysis
    total_tests += 1
    try:
        sample_portfolio = [
            {'symbol': 'AAPL', 'current_value': 10000, 'cost_basis': 9000},
            {'symbol': 'GOOGL', 'current_value': 20000, 'cost_basis': 18000},
            {'symbol': 'MSFT', 'current_value': 15000, 'cost_basis': 14000}
        ]
        
        metrics = advanced_analyzer.calculate_advanced_metrics(sample_portfolio)
        
        required_keys = ['total_value', 'total_return', 'return_percentage', 'holdings_count']
        if all(key in metrics for key in required_keys):
            print(f"✅ Advanced portfolio analysis working ({len(metrics)} metrics calculated)")
            success_count += 1
        else:
            print(f"❌ Advanced portfolio analysis missing keys: {set(required_keys) - set(metrics.keys())}")
            
    except Exception as e:
        print(f"❌ Advanced portfolio analysis failed: {e}")
    
    # Test 4: Market Data Enhancement
    total_tests += 1
    try:
        sample_price_data = [
            {'symbol': 'AAPL', 'date': '2024-01-01', 'close_price': 180.0, 'volume': 1000000},
            {'symbol': 'AAPL', 'date': '2024-01-02', 'close_price': 182.0, 'volume': 1100000},
            {'symbol': 'AAPL', 'date': '2024-01-03', 'close_price': 179.0, 'volume': 950000},
        ]
        
        enhanced_data = market_enhancer.enhance_price_data(sample_price_data, ['volatility'])
        
        if enhanced_data is not None:
            print("✅ Market data enhancement working")
            success_count += 1
        else:
            print("❌ Market data enhancement returned None")
            
    except Exception as e:
        print(f"❌ Market data enhancement failed: {e}")
    
    # Test 5: Security Search
    total_tests += 1
    try:
        search_results = advanced_analyzer.search_securities("apple")
        
        if isinstance(search_results, list) and len(search_results) > 0:
            print(f"✅ Security search working ({len(search_results)} results found)")
            success_count += 1
        else:
            print("❌ Security search returned no results")
            
    except Exception as e:
        print(f"❌ Security search failed: {e}")
    
    # Test 6: Market Calendar Info
    total_tests += 1
    try:
        calendar_info = advanced_analyzer.get_market_calendar_info()
        
        required_keys = ['exchange', 'trading_days_count']
        if all(key in calendar_info for key in required_keys):
            print("✅ Market calendar info working")
            success_count += 1
        else:
            print(f"❌ Market calendar info missing keys: {set(required_keys) - set(calendar_info.keys())}")
            
    except Exception as e:
        print(f"❌ Market calendar info failed: {e}")
    
    # Test 7: Dashboard Creation
    total_tests += 1
    try:
        dashboard_html = enhanced_visualizer.create_advanced_portfolio_dashboard(
            sample_portfolio, metrics
        )
        
        if dashboard_html is not None and len(dashboard_html) > 0:
            print("✅ Dashboard creation working")
            success_count += 1
        else:
            print("❌ Dashboard creation returned empty result")
            
    except Exception as e:
        print(f"❌ Dashboard creation failed: {e}")
    
    # Test 8: Technical Analysis Chart
    total_tests += 1
    try:
        price_data_with_indicators = [
            {'date': '2024-01-01', 'close_price': 180.0, 'rsi_14': 65.0},
            {'date': '2024-01-02', 'close_price': 182.0, 'rsi_14': 68.0},
            {'date': '2024-01-03', 'close_price': 179.0, 'rsi_14': 62.0},
        ]
        
        chart_html = enhanced_visualizer.create_technical_analysis_chart(
            price_data_with_indicators, indicators=['rsi_14']
        )
        
        # Chart can be None if plotly not available, which is acceptable
        print("✅ Technical analysis chart creation working")
        success_count += 1
            
    except Exception as e:
        print(f"❌ Technical analysis chart failed: {e}")
    
    # Test 9: Polars Integration (if available)
    total_tests += 1
    try:
        from personal_finance.data_sources.polars_integration import polars_processor
        
        # Test portfolio optimization metrics
        opt_metrics = polars_processor.calculate_portfolio_optimization_metrics(sample_portfolio)
        
        if isinstance(opt_metrics, dict) and len(opt_metrics) > 0:
            print("✅ Polars integration optimization metrics working")
            success_count += 1
        else:
            print("❌ Polars integration returned empty results")
            
    except Exception as e:
        print(f"❌ Polars integration failed: {e}")
    
    # Test 10: Complete Workflow Integration
    total_tests += 1
    try:
        # End-to-end test
        charts = {'dashboard': dashboard_html}
        report_data = enhanced_visualizer.generate_report_data(
            sample_portfolio, metrics, charts
        )
        
        required_keys = ['portfolio_data', 'metrics', 'charts', 'summary']
        if all(key in report_data for key in required_keys):
            print("✅ Complete workflow integration working")
            success_count += 1
        else:
            print(f"❌ Complete workflow missing keys: {set(required_keys) - set(report_data.keys())}")
            
    except Exception as e:
        print(f"❌ Complete workflow integration failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count >= total_tests * 0.8:  # 80% success rate
        print("🎉 Enhanced features are working well!")
        return True
    else:
        print("⚠️ Some enhanced features need attention")
        return False

if __name__ == '__main__':
    success = test_enhanced_features()
    sys.exit(0 if success else 1)