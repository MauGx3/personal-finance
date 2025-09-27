"""Basic validation test for data sources implementation."""

import sys
from decimal import Decimal
from datetime import datetime

def test_basic_imports():
    """Test that all modules can be imported without errors."""
    try:
        from personal_finance.data_sources import (
            DataSourceService, 
            create_mock_service,
            PricePoint,
            HistoricalSeries
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_mock_service_basic_functionality():
    """Test basic functionality with mock service."""
    try:
        from personal_finance.data_sources import create_mock_service
        
        service = create_mock_service()
        print("✓ Mock service created")
        
        # Test current price
        price = service.get_current_price("AAPL")
        if price and price.symbol == "AAPL":
            print(f"✓ Current price: {price.symbol} = ${price.price}")
        else:
            print("✗ Current price failed")
            return False
        
        # Test historical data
        historical = service.fetch_historical("AAPL")
        if historical and historical.symbol == "AAPL" and len(historical.data_points) > 0:
            print(f"✓ Historical data: {len(historical.data_points)} data points")
        else:
            print("✗ Historical data failed")
            return False
        
        # Test bulk request
        bulk_results = service.bulk_get_current(["AAPL", "MSFT"])
        if bulk_results and "AAPL" in bulk_results and "MSFT" in bulk_results:
            print(f"✓ Bulk request: {len(bulk_results)} symbols")
        else:
            print("✗ Bulk request failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Mock service test failed: {e}")
        return False

def test_data_types():
    """Test data type creation and validation."""
    try:
        from personal_finance.data_sources.types import PricePoint
        
        # Test PricePoint creation
        price_point = PricePoint(
            symbol="TEST",
            price=Decimal("100.50"),
            timestamp=datetime.now()
        )
        
        if price_point.symbol == "TEST" and price_point.price == Decimal("100.50"):
            print("✓ PricePoint creation successful")
            return True
        else:
            print("✗ PricePoint creation failed")
            return False
            
    except Exception as e:
        print(f"✗ Data types test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("Running basic validation tests for data sources implementation...\n")
    
    tests = [
        test_basic_imports,
        test_data_types, 
        test_mock_service_basic_functionality,
    ]
    
    passed = 0
    for test in tests:
        print(f"Running {test.__name__}...")
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)