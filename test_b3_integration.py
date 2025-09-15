"""Integration test for B3 data source with the main data source manager."""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from personal_finance.data_sources.services import DataSourceManager
from personal_finance.data_sources.b3_import import B3DocumentImporter


def test_b3_data_source_integration():
    """Test B3 data source integration with DataSourceManager."""

    print("Testing B3 Data Source Integration...")

    # Initialize data source manager
    manager = DataSourceManager()

    # Check that B3 data source is available
    b3_sources = [
        source for source in manager.sources if source.name == "B3 Brazil"
    ]
    assert len(b3_sources) == 1, "B3 data source should be available"

    b3_source = b3_sources[0]
    print(f"✓ B3 data source found: {b3_source.name}")

    # Test price fetching (should work with placeholder data)
    price_data = b3_source.get_current_price("PETR4")
    assert price_data is not None, "Should get price data"
    assert price_data.currency == "BRL", "Currency should be BRL"
    print(f"✓ Price data: {price_data.symbol} = R$ {price_data.current_price}")

    # Test symbol search
    search_results = b3_source.search_symbol("PETR")
    assert len(search_results) > 0, "Should find Brazilian stocks"
    print(f"✓ Search results for 'PETR': {len(search_results)} stocks found")

    # Test document import
    sample_nota = """
    NOTA DE CORRETAGEM
    Data pregão: 15/03/2024
    PETR4    C    100    25,50    2.550,00
    VALE3    V    50     45,75    2.287,50
    """

    result = b3_source.import_document(sample_nota, "nota_corretagem")
    assert len(result.transactions) == 2, "Should parse 2 transactions"
    print(f"✓ Document import: {len(result.transactions)} transactions parsed")

    # Test auto-detection
    detected_type = b3_source.detect_document_type(sample_nota)
    assert detected_type == "nota_corretagem", "Should detect document type"
    print(f"✓ Auto-detection: {detected_type}")

    print("\n🎉 All B3 integration tests passed!")


def test_data_source_manager_with_b3():
    """Test DataSourceManager with B3 support."""

    print("\nTesting DataSourceManager with B3...")

    manager = DataSourceManager()

    # Test getting source status
    status = manager.get_source_status()
    assert "B3 Brazil" in status, "B3 should be in status"
    print(f"✓ Data sources available: {list(status.keys())}")

    # Test price fetching through manager (should try B3 for Brazilian tickers)
    price_data = manager.get_current_price("PETR4")
    if price_data:
        print(
            f"✓ Manager price fetch: {price_data.symbol} = {price_data.current_price} {price_data.currency}"
        )
    else:
        print(
            "⚠️  Manager price fetch returned None (expected if sources are unavailable)"
        )

    print("✓ DataSourceManager integration working")


if __name__ == "__main__":
    test_b3_data_source_integration()
    test_data_source_manager_with_b3()
    print("\n✅ All integration tests completed successfully!")
