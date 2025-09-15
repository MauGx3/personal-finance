#!/usr/bin/env python3
"""CLI utility for importing B3 documents.

This script provides a command-line interface for importing Brazilian B3
documents (Nota de Corretagem and Extrato) into the personal finance system.

Usage:
    python import_b3.py --file document.txt --type nota_corretagem
    python import_b3.py --file statement.txt --type extrato
    python import_b3.py --file document.txt --auto-detect
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from personal_finance.data_sources.b3_import import (
    B3DocumentImporter,
    B3ImportResult,
)


def load_document(file_path: str) -> str:
    """Load document content from file.

    Args:
        file_path: Path to the document file

    Returns:
        Document content as string

    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file can't be decoded as UTF-8
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except UnicodeDecodeError:
        # Try with latin-1 encoding (common for Brazilian documents)
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except UnicodeDecodeError:
            print(
                f"Error: Could not decode file '{file_path}'. Please ensure it's a text file."
            )
            sys.exit(1)


def print_import_result(result: B3ImportResult) -> None:
    """Print import result in a formatted way."""
    print("\n" + "=" * 60)
    print("B3 DOCUMENT IMPORT RESULT")
    print("=" * 60)

    # Summary
    print("\nSUMMARY:")
    for key, value in result.summary.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    # Transactions
    if result.transactions:
        print(f"\nTRANSACTIONS ({len(result.transactions)}):")
        print("-" * 60)
        for i, tx in enumerate(result.transactions, 1):
            print(
                f"{i:2d}. {tx.date} | {tx.ticker} | {tx.transaction_type.value} | "
                f"Qty: {tx.quantity} | Price: R$ {tx.unit_price} | "
                f"Total: R$ {tx.total_value}"
            )

    # Extract entries
    if result.extract_entries:
        print(f"\nEXTRACT ENTRIES ({len(result.extract_entries)}):")
        print("-" * 60)
        for i, entry in enumerate(result.extract_entries, 1):
            credit_str = f"R$ {entry.credit}" if entry.credit else ""
            debit_str = f"R$ {entry.debit}" if entry.debit else ""
            balance_str = f"R$ {entry.balance}" if entry.balance else ""
            print(
                f"{i:2d}. {entry.date} | {entry.description[:30]:30} | "
                f"C: {credit_str:10} | D: {debit_str:10} | Bal: {balance_str}"
            )

    # Warnings
    if result.warnings:
        print(f"\nWARNINGS ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")

    # Errors
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for error in result.errors:
            print(f"  ❌ {error}")

    print("\n" + "=" * 60)


def save_json_result(result: B3ImportResult, output_file: str) -> None:
    """Save import result to JSON file."""
    # Convert result to JSON-serializable format
    data = {
        "summary": result.summary,
        "transactions": [
            {
                "date": tx.date.isoformat(),
                "transaction_type": tx.transaction_type.value,
                "ticker": tx.ticker,
                "market_type": tx.market_type.value,
                "quantity": int(tx.quantity),
                "unit_price": str(tx.unit_price),
                "total_value": str(tx.total_value),
                "brokerage_fee": str(tx.brokerage_fee),
                "settlement_fee": str(tx.settlement_fee),
                "net_value": str(tx.net_value),
            }
            for tx in result.transactions
        ],
        "extract_entries": [
            {
                "date": entry.date.isoformat(),
                "description": entry.description,
                "credit": str(entry.credit) if entry.credit else None,
                "debit": str(entry.debit) if entry.debit else None,
                "balance": str(entry.balance) if entry.balance else None,
            }
            for entry in result.extract_entries
        ],
        "errors": result.errors,
        "warnings": result.warnings,
    }

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"Error saving to {output_file}: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Import B3 (Brazilian Stock Exchange) documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file nota_corretagem.txt --type nota_corretagem
  %(prog)s --file extrato.txt --type extrato
  %(prog)s --file document.txt --auto-detect
  %(prog)s --file document.txt --auto-detect --output result.json
        """,
    )

    parser.add_argument(
        "--file", "-f", required=True, help="Path to the B3 document file"
    )

    parser.add_argument(
        "--type",
        "-t",
        choices=["nota_corretagem", "extrato"],
        help="Document type (nota_corretagem or extrato)",
    )

    parser.add_argument(
        "--auto-detect",
        "-a",
        action="store_true",
        help="Auto-detect document type",
    )

    parser.add_argument("--output", "-o", help="Save results to JSON file")

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.type and not args.auto_detect:
        print("Error: Either --type or --auto-detect must be specified.")
        parser.print_help()
        sys.exit(1)

    # Load document
    print(f"Loading document: {args.file}")
    content = load_document(args.file)

    if args.verbose:
        print(f"Document size: {len(content)} characters")
        print(f"First 200 characters:\n{content[:200]}...")

    # Initialize importer
    importer = B3DocumentImporter()

    # Determine document type
    if args.auto_detect:
        detected_type = importer.detect_document_type(content)
        if not detected_type:
            print("Error: Could not auto-detect document type.")
            print("Please specify document type manually with --type")
            sys.exit(1)
        document_type = detected_type
        print(f"Auto-detected document type: {document_type}")
    else:
        document_type = args.type
        print(f"Using specified document type: {document_type}")

    # Import document
    print(f"Importing {document_type}...")
    try:
        result = importer.import_document(content, document_type)
    except Exception as e:
        print(f"Error during import: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)

    # Display results
    print_import_result(result)

    # Save to JSON if requested
    if args.output:
        save_json_result(result, args.output)

    # Exit with appropriate code
    if result.errors:
        print("\nImport completed with errors.")
        sys.exit(1)
    elif result.warnings:
        print("\nImport completed with warnings.")
        sys.exit(0)
    else:
        print("\nImport completed successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
