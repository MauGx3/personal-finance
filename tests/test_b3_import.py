"""Tests for B3 import functionality."""

import pytest
from datetime import date
from decimal import Decimal

from personal_finance.data_sources.b3_import import (
    B3DocumentImporter,
    NotaCorretagemParser,
    ExtratoParser,
    B3Transaction,
    B3TransactionType,
    B3MarketType,
    B3ExtractEntry,
)


class TestNotaCorretagemParser:
    """Test cases for Nota de Corretagem parser."""

    def test_parse_basic_nota(self):
        """Test parsing a basic Nota de Corretagem."""
        content = """
        NOTA DE CORRETAGEM
        Data pregão: 15/03/2024
        
        PETR4    C    100    25,50    2.550,00
        VALE3    V    200    45,75    9.150,00
        
        Taxa de corretagem: 10,00
        Taxa de liquidação: 5,00
        Emolumentos: 2,50
        """

        parser = NotaCorretagemParser()
        result = parser.parse(content)

        assert len(result.transactions) == 2
        assert len(result.errors) == 0

        # Check first transaction (buy)
        tx1 = result.transactions[0]
        assert tx1.ticker == "PETR4"
        assert tx1.transaction_type == B3TransactionType.BUY
        assert tx1.quantity == 100
        assert tx1.unit_price == Decimal("25.50")
        assert tx1.total_value == Decimal("2550.00")

        # Check second transaction (sell)
        tx2 = result.transactions[1]
        assert tx2.ticker == "VALE3"
        assert tx2.transaction_type == B3TransactionType.SELL
        assert tx2.quantity == 200
        assert tx2.unit_price == Decimal("45.75")
        assert tx2.total_value == Decimal("9150.00")

    def test_parse_decimal_format(self):
        """Test parsing Brazilian decimal format."""
        parser = NotaCorretagemParser()

        # Test various formats
        assert parser._parse_decimal("1.250,50") == Decimal("1250.50")
        assert parser._parse_decimal("25,75") == Decimal("25.75")
        assert parser._parse_decimal("100,00") == Decimal("100.00")

    def test_parse_invalid_content(self):
        """Test parsing invalid content."""
        parser = NotaCorretagemParser()
        result = parser.parse("Invalid content")

        assert len(result.transactions) == 0
        assert len(result.errors) > 0


class TestExtratoParser:
    """Test cases for Extrato parser."""

    def test_parse_basic_extrato(self):
        """Test parsing a basic Extrato."""
        content = """
        EXTRATO DE CONTA
        
        15/03/2024  Compra PETR4        2.560,00      125.340,50
        16/03/2024  Venda VALE3                9.145,00  134.485,50
        17/03/2024  Taxa corretagem        10,00       134.475,50
        """

        parser = ExtratoParser()
        result = parser.parse(content)

        assert len(result.extract_entries) == 3
        assert len(result.errors) == 0

        # Check entries
        entry1 = result.extract_entries[0]
        assert entry1.date == date(2024, 3, 15)
        assert "Compra PETR4" in entry1.description
        assert entry1.balance == Decimal("125340.50")

    def test_parse_negative_values(self):
        """Test parsing negative values in extrato."""
        parser = ExtratoParser()

        # Test negative parsing
        assert parser._parse_decimal("-1.250,50") == Decimal("-1250.50")
        assert parser._parse_decimal("1.250,50") == Decimal("1250.50")


class TestB3DocumentImporter:
    """Test cases for B3DocumentImporter."""

    def test_document_type_detection(self):
        """Test auto-detection of document types."""
        importer = B3DocumentImporter()

        # Test Nota de Corretagem detection
        nota_content = "NOTA DE CORRETAGEM\nData pregão: 15/03/2024"
        assert importer.detect_document_type(nota_content) == "nota_corretagem"

        # Test Extrato detection
        extrato_content = "EXTRATO DE CONTA\nSaldo em 15/03/2024: R$ 1.000,00"
        assert importer.detect_document_type(extrato_content) == "extrato"

        # Test unknown content
        unknown_content = "Some random content"
        assert importer.detect_document_type(unknown_content) is None

    def test_import_nota_corretagem(self):
        """Test importing Nota de Corretagem."""
        importer = B3DocumentImporter()

        content = """
        NOTA DE CORRETAGEM
        Data pregão: 15/03/2024
        PETR4    C    100    25,50    2.550,00
        """

        result = importer.import_document(content, "nota_corretagem")

        assert len(result.transactions) == 1
        assert result.summary["document_type"] == "Nota de Corretagem"
        assert result.summary["total_transactions"] == 1

    def test_import_extrato(self):
        """Test importing Extrato."""
        importer = B3DocumentImporter()

        content = """
        EXTRATO DE CONTA
        15/03/2024  Compra PETR4        2.560,00      125.340,50
        """

        result = importer.import_document(content, "extrato")

        assert len(result.extract_entries) == 1
        assert result.summary["document_type"] == "Extrato"

    def test_unsupported_document_type(self):
        """Test handling of unsupported document type."""
        importer = B3DocumentImporter()

        with pytest.raises(ValueError, match="Unsupported document type"):
            importer.import_document("content", "unsupported_type")


class TestB3Transaction:
    """Test cases for B3Transaction data class."""

    def test_net_value_calculation_buy(self):
        """Test net value calculation for buy transaction."""
        tx = B3Transaction(
            date=date(2024, 3, 15),
            transaction_type=B3TransactionType.BUY,
            ticker="PETR4",
            market_type=B3MarketType.SPOT,
            quantity=100,
            unit_price=Decimal("25.50"),
            total_value=Decimal("2550.00"),
            brokerage_fee=Decimal("10.00"),
            settlement_fee=Decimal("5.00"),
        )

        # For buy: net = total + fees
        assert tx.net_value == Decimal("2565.00")

    def test_net_value_calculation_sell(self):
        """Test net value calculation for sell transaction."""
        tx = B3Transaction(
            date=date(2024, 3, 15),
            transaction_type=B3TransactionType.SELL,
            ticker="VALE3",
            market_type=B3MarketType.SPOT,
            quantity=200,
            unit_price=Decimal("45.75"),
            total_value=Decimal("9150.00"),
            brokerage_fee=Decimal("10.00"),
            settlement_fee=Decimal("5.00"),
        )

        # For sell: net = total - fees
        assert tx.net_value == Decimal("9135.00")


if __name__ == "__main__":
    pytest.main([__file__])
