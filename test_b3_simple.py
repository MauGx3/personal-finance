"""Simple test for B3 import functionality without Django dependencies."""

import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from personal_finance.data_sources.b3_import import (
    B3DocumentImporter,
    B3TransactionType,
    B3MarketType,
    NotaCorretagemParser,
    ExtratoParser,
)


def test_nota_corretagem_parsing():
    """Test Nota de Corretagem parsing."""
    print("Testing Nota de Corretagem parsing...")

    content = """
                            NOTA DE CORRETAGEM
    Data pregão: 15/03/2024
    
    PETR4         PETROBRAS PN  C   100    25,50        2.550,00      D
    VALE3         VALE ON       C   200    45,75        9.150,00      D  
    ITUB4         ITAU PN       V   150    30,20        4.530,00      C
    
    Taxa de corretagem                                        25,00  
    Emolumentos                                                5,00
    """

    parser = NotaCorretagemParser()
    result = parser.parse(content)

    print(f"  Transactions found: {len(result.transactions)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")

    assert len(result.transactions) == 3, (
        f"Expected 3 transactions, got {len(result.transactions)}"
    )

    # Check first transaction
    tx1 = result.transactions[0]
    assert tx1.ticker == "PETR4"
    assert tx1.transaction_type == B3TransactionType.BUY
    assert tx1.quantity == 100
    assert tx1.unit_price == Decimal("25.50")
    assert tx1.total_value == Decimal("2550.00")

    # Check sell transaction
    sell_tx = [
        tx
        for tx in result.transactions
        if tx.transaction_type == B3TransactionType.SELL
    ][0]
    assert sell_tx.ticker == "ITUB4"
    assert sell_tx.quantity == 150

    print("  ✓ Nota de Corretagem parsing test passed!")


def test_extrato_parsing():
    """Test Extrato parsing."""
    print("\nTesting Extrato parsing...")

    content = """
    EXTRATO DE CONTA CORRENTE
    
    DATA       HISTÓRICO                               DÉBITO      CRÉDITO     SALDO

    01/03/2024 Saldo anterior                                                120.000,00
    15/03/2024 Compra PETR4 - 100 cotas                2.550,00             122.450,00
    15/03/2024 Venda ITUB4 - 150 cotas                            4.530,00   117.830,00
    20/03/2024 Dividendos PETR4                                    125,50    117.908,25
    """

    parser = ExtratoParser()
    result = parser.parse(content)

    print(f"  Extract entries found: {len(result.extract_entries)}")
    print(f"  Errors: {len(result.errors)}")

    assert len(result.extract_entries) > 0, "Should find extract entries"

    # Check that dates are parsed correctly
    entries_with_dates = [
        e for e in result.extract_entries if e.date is not None
    ]
    assert len(entries_with_dates) > 0, "Should have entries with valid dates"

    print("  ✓ Extrato parsing test passed!")


def test_document_importer():
    """Test the main B3DocumentImporter."""
    print("\nTesting B3DocumentImporter...")

    importer = B3DocumentImporter()

    # Test document type detection
    nota_content = "NOTA DE CORRETAGEM\nData pregão: 15/03/2024"
    detected = importer.detect_document_type(nota_content)
    assert detected == "nota_corretagem", (
        f"Should detect nota_corretagem, got {detected}"
    )

    extrato_content = "EXTRATO DE CONTA\nSaldo em 15/03/2024: R$ 1.000,00"
    detected = importer.detect_document_type(extrato_content)
    assert detected == "extrato", f"Should detect extrato, got {detected}"

    # Test supported types
    supported = importer.get_supported_types()
    assert "nota_corretagem" in supported
    assert "extrato" in supported

    print("  ✓ B3DocumentImporter test passed!")


def test_decimal_parsing():
    """Test Brazilian decimal format parsing."""
    print("\nTesting decimal parsing...")

    parser = NotaCorretagemParser()

    # Test various Brazilian number formats
    test_cases = [
        ("1.250,50", "1250.50"),
        ("25,75", "25.75"),
        ("100,00", "100.00"),
        ("1.000.250,75", "1000250.75"),
    ]

    for input_val, expected in test_cases:
        result = parser._parse_decimal(input_val)
        expected_decimal = Decimal(expected)
        assert result == expected_decimal, (
            f"Expected {expected_decimal}, got {result} for input {input_val}"
        )

    print("  ✓ Decimal parsing test passed!")


def test_real_document_samples():
    """Test with the actual sample documents."""
    print("\nTesting with real document samples...")

    importer = B3DocumentImporter()

    # Test sample Nota de Corretagem
    try:
        with open(
            "examples/sample_nota_corretagem.txt", "r", encoding="utf-8"
        ) as f:
            content = f.read()

        result = importer.import_document(content, "nota_corretagem")
        print(
            f"  Sample Nota de Corretagem: {len(result.transactions)} transactions"
        )
        assert len(result.transactions) > 0, (
            "Should find transactions in sample document"
        )

    except FileNotFoundError:
        print("  ⚠️  Sample nota_corretagem.txt not found, skipping")

    # Test sample Extrato
    try:
        with open("examples/sample_extrato.txt", "r", encoding="utf-8") as f:
            content = f.read()

        result = importer.import_document(content, "extrato")
        print(f"  Sample Extrato: {len(result.extract_entries)} entries")
        assert len(result.extract_entries) > 0, (
            "Should find entries in sample document"
        )

    except FileNotFoundError:
        print("  ⚠️  Sample extrato.txt not found, skipping")

    print("  ✓ Real document samples test passed!")


if __name__ == "__main__":
    print("🧪 Running B3 Import Tests\n")

    test_nota_corretagem_parsing()
    test_extrato_parsing()
    test_document_importer()
    test_decimal_parsing()
    test_real_document_samples()

    print("\n🎉 All B3 import tests passed successfully!")
    print("\n📋 Summary:")
    print("   ✅ Nota de Corretagem parsing")
    print("   ✅ Extrato parsing")
    print("   ✅ Document type auto-detection")
    print("   ✅ Brazilian decimal format handling")
    print("   ✅ Real document samples")
    print("\n🔥 B3 import functionality is working correctly!")
