#!/usr/bin/env python3
"""Demonstration of B3 import functionality.

This script demonstrates the key features of the B3 import system
including parsing Nota de Corretagem and Extrato documents.
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from personal_finance.data_sources.b3_import import B3DocumentImporter


def demonstrate_nota_corretagem():
    """Demonstrate Nota de Corretagem parsing."""
    print("🇧🇷 DEMONSTRATING B3 NOTA DE CORRETAGEM IMPORT")
    print("=" * 60)

    # Sample Nota de Corretagem content
    sample_nota = """
                            NOTA DE CORRETAGEM
                         CORRETORA DEMO LTDA.
                              CNPJ: 12.345.678/0001-90

Data pregão: 15/03/2024

ESPECIFICAÇÃO DO TÍTULO    Q    PREÇO/AJUSTE    VALOR/AJUSTE    D/C

PETR4         PETROBRAS PN  C   100    25,50        2.550,00      D
VALE3         VALE ON       C   200    45,75        9.150,00      D  
ITUB4         ITAU PN       V   150    30,20        4.530,00      C
BBDC4         BRADESCO PN   C    50    28,40        1.420,00      D

Taxa de corretagem                                        35,00  
Taxa de liquidação                                        18,50
Emolumentos                                                8,00
    """

    # Initialize importer
    importer = B3DocumentImporter()

    print("📄 Sample Nota de Corretagem content:")
    print(sample_nota[:200] + "...")

    # Import document
    result = importer.import_document(sample_nota, "nota_corretagem")

    print(f"\n📊 PARSING RESULTS:")
    print(f"   📈 Transactions found: {len(result.transactions)}")
    print(f"   ⚠️  Warnings: {len(result.warnings)}")
    print(f"   ❌ Errors: {len(result.errors)}")

    print(f"\n💰 FINANCIAL SUMMARY:")
    print(f"   📅 Trade Date: {result.summary['trade_date']}")
    print(
        f"   💸 Total Buy Value: R$ {result.summary['total_buy_value']:,.2f}"
    )
    print(
        f"   💰 Total Sell Value: R$ {result.summary['total_sell_value']:,.2f}"
    )

    print(f"\n📋 TRANSACTION DETAILS:")
    for i, tx in enumerate(result.transactions, 1):
        action = "🔴 SELL" if tx.transaction_type.value == "V" else "🟢 BUY"
        print(f"   {i}. {action} {tx.ticker}")
        print(f"      Quantity: {tx.quantity:,} shares")
        print(f"      Unit Price: R$ {tx.unit_price}")
        print(f"      Total Value: R$ {tx.total_value:,}")
        print(f"      Net Value: R$ {tx.net_value:,}")
        print()


def demonstrate_extrato():
    """Demonstrate Extrato parsing."""
    print("\n🇧🇷 DEMONSTRATING B3 EXTRATO IMPORT")
    print("=" * 60)

    # Sample Extrato content
    sample_extrato = """
                              EXTRATO DE CONTA CORRENTE
                                CORRETORA DEMO LTDA.

Cliente: João Silva                                       CPF: 123.456.789-00
Período: 01/03/2024 a 31/03/2024

DATA       HISTÓRICO                               DÉBITO      CRÉDITO     SALDO

01/03/2024 Saldo anterior                                                120.000,00
03/03/2024 Transferência recebida                             5.000,00   125.000,00
15/03/2024 Compra PETR4 - 100 cotas                2.550,00             122.450,00
15/03/2024 Compra VALE3 - 200 cotas                9.150,00             113.300,00  
15/03/2024 Venda ITUB4 - 150 cotas                            4.530,00   117.830,00
20/03/2024 Dividendos PETR4                                    125,50    117.955,50
22/03/2024 JCP VALE3                                           89,75     118.045,25
25/03/2024 Taxa de corretagem                        35,00               118.010,25
31/03/2024 Saldo final                                                  118.010,25
    """

    # Initialize importer
    importer = B3DocumentImporter()

    print("📄 Sample Extrato content:")
    print(sample_extrato[:200] + "...")

    # Import document
    result = importer.import_document(sample_extrato, "extrato")

    print(f"\n📊 PARSING RESULTS:")
    print(f"   📋 Extract entries found: {len(result.extract_entries)}")
    print(f"   ⚠️  Warnings: {len(result.warnings)}")
    print(f"   ❌ Errors: {len(result.errors)}")

    if result.extract_entries:
        print(f"\n📅 PERIOD SUMMARY:")
        print(f"   Start Date: {result.summary.get('period_start')}")
        print(f"   End Date: {result.summary.get('period_end')}")

        print(f"\n💳 ACCOUNT MOVEMENTS (showing first 5):")
        for i, entry in enumerate(result.extract_entries[:5], 1):
            credit_str = f"R$ {entry.credit:,.2f}" if entry.credit else ""
            debit_str = f"R$ {entry.debit:,.2f}" if entry.debit else ""
            balance_str = f"R$ {entry.balance:,.2f}" if entry.balance else ""

            print(f"   {i}. {entry.date} - {entry.description[:30]:<30}")
            print(
                f"      Credit: {credit_str:<12} Debit: {debit_str:<12} Balance: {balance_str}"
            )
            print()


def demonstrate_auto_detection():
    """Demonstrate automatic document type detection."""
    print("\n🤖 DEMONSTRATING AUTO-DETECTION")
    print("=" * 60)

    importer = B3DocumentImporter()

    test_cases = [
        ("NOTA DE CORRETAGEM\nData pregão: 15/03/2024", "Nota de Corretagem"),
        ("EXTRATO DE CONTA\nSaldo em 15/03/2024", "Extrato"),
        ("Some random content", "Unknown document"),
    ]

    for content, description in test_cases:
        detected = importer.detect_document_type(content)
        status = "✅ DETECTED" if detected else "❌ NOT DETECTED"
        detected_type = detected or "Unknown"

        print(f"   {description}:")
        print(f'      Content: "{content[:30]}..."')
        print(f"      Result: {status} as '{detected_type}'")
        print()


def demonstrate_supported_features():
    """Demonstrate supported features."""
    print("\n🔧 SUPPORTED FEATURES")
    print("=" * 60)

    print("📄 Document Types:")
    print("   ✅ Nota de Corretagem (Brokerage Note)")
    print("   ✅ Extrato (Account Statement)")

    print("\n💱 Transaction Types:")
    print("   ✅ Compra (C) - Buy orders")
    print("   ✅ Venda (V) - Sell orders")
    print("   ✅ Dividendos - Dividend payments")
    print("   ✅ JCP - Juros sobre Capital Próprio")

    print("\n🏛️ Market Types:")
    print("   ✅ Mercado à Vista (Spot Market)")
    print("   ✅ Mercado de Opções (Options)")
    print("   ✅ Mercado Futuro (Futures)")
    print("   ✅ ETFs")

    print("\n💰 Currency & Formats:")
    print("   ✅ Brazilian Real (BRL)")
    print("   ✅ Brazilian decimal format (1.250,50)")
    print("   ✅ Automatic encoding detection (UTF-8/Latin-1)")

    print("\n📊 Data Extraction:")
    print("   ✅ Stock tickers (PETR4, VALE3, etc.)")
    print("   ✅ Quantities and prices")
    print("   ✅ Fees and taxes")
    print("   ✅ Net value calculations")
    print("   ✅ Account movements and balances")


def main():
    """Main demonstration function."""
    print("🚀 B3 IMPORT FUNCTIONALITY DEMONSTRATION")
    print("========================================")
    print("This demo showcases the B3 (Brazilian Stock Exchange)")
    print("document import capabilities for personal finance management.\n")

    try:
        demonstrate_nota_corretagem()
        demonstrate_extrato()
        demonstrate_auto_detection()
        demonstrate_supported_features()

        print("\n🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("\n📚 NEXT STEPS:")
        print("   1. Try importing your own B3 documents:")
        print(
            "      python import_b3.py --file your_document.txt --auto-detect"
        )
        print("   2. Export results to JSON for further processing:")
        print(
            "      python import_b3.py --file document.txt --auto-detect --output results.json"
        )
        print("   3. Read the documentation: B3_IMPORT_README.md")
        print("   4. Check out the sample documents in examples/")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
