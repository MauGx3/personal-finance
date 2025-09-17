"""Banco Inter document import services.

This module provides parsers for Banco Inter documents:
- Relatório Mensal de Investimentos (Monthly Investment Report)
- Nota de corretagem (Brokerage Note)
- Extrato (Bank Statement)
"""

import logging
import asyncio
import re
from abc import ABC, abstractmethod
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Awaitable
from math import isfinite

import pandas as pd

try:
    import pdfplumber

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from django.contrib.auth import get_user_model
from django.utils import timezone

from personal_finance.assets.models import Asset
from personal_finance.portfolios.models import Portfolio, Position, Transaction
from .models import DocumentImport

User = get_user_model()
logger = logging.getLogger(__name__)

# Polars optional support removed for now; mark as unavailable
POLARS_AVAILABLE = False


class ImporterError(Exception):
    """Base exception for import operations."""

    pass


class ParseError(ImporterError):
    """Exception raised when document parsing fails."""

    pass


class DataValidationError(ImporterError):
    """Exception raised when imported data validation fails."""

    pass


class BancoInterDocumentParser(ABC):
    """Abstract base class for Banco Inter document parsers."""

    def __init__(self, file_path: str, user: Any):
        self.file_path = Path(file_path)
        self.user = user
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """Parse the document and return structured data.

        Returns:
            Dictionary with parsed data including transactions, positions, etc.
        """

    raise NotImplementedError()

    @abstractmethod
    def validate_format(self) -> bool:
        """Validate that the file matches expected format.

        Returns:
            True if format is valid, False otherwise.
        """

    raise NotImplementedError()

    def _parse_decimal(
        self, value: Any, default: Decimal = Decimal("0")
    ) -> Decimal:
        """Parse Brazilian number format to Decimal.

        Handles formats like:
        - R$ 1.234,56
        - 1.234,56
        - (1.234,56) for negative values
        """
        # Handle None-like and pandas missing values safely
        try:
            if value is None or pd.isna(value):
                return default
        except Exception:
            # pd.isna may raise for exotic types; ignore and continue
            pass

        # If it's already a Decimal, return as-is
        if isinstance(value, Decimal):
            return value

        # Handle integers directly
        if isinstance(value, int) and not isinstance(value, bool):
            return Decimal(value)

        # Handle floats carefully: use str() to avoid binary float artifacts
        if isinstance(value, float):
            # Guard against NaN/Inf
            try:
                if not isfinite(value):
                    return default
            except Exception:
                pass
            return Decimal(str(value))

        # Convert to string and normalize
        s = str(value).strip()
        if not s:
            return default

        # Normalize unicode minus sign to ASCII hyphen
        s = s.replace("\u2212", "-")

        # Normalize fullwidth digits and punctuation (e.g. '１' -> '1',
        # '，' -> ',') to handle PDF-extracted numerals and punctuation.
        # This helps handle PDF-extracted fullwidth numerals and punctuation.
        try:
            trans = {
                ord("０"): "0",
                ord("１"): "1",
                ord("２"): "2",
                ord("３"): "3",
                ord("４"): "4",
                ord("５"): "5",
                ord("６"): "6",
                ord("７"): "7",
                ord("８"): "8",
                ord("９"): "9",
                ord("，"): ",",
                ord("．"): ".",
                ord("％"): "%",
                ord("＋"): "+",
                ord("－"): "-",
            }
            s = s.translate(trans)
        except Exception:
            # If translation fails for any reason, continue with original
            # string
            pass

        # Remove BOM and various control/odd whitespace characters that
        # sometimes appear in PDF-extracted strings (NUL, NBSP, ZWSP, NNBSP)
        s = s.replace("\ufeff", "")
        s = re.sub(r"[\x00-\x1F\x7F\u00A0\u200B\u202F\u2060]+", "", s)

        # Remove percent characters (ASCII and fullwidth) but keep the
        # numeric value (do not convert to ratio)
        s = re.sub(r"[%％]", "", s).strip()

        # Detect negative numbers in parentheses or leading minus
        is_negative = False
        s_strip = s.strip()
        if s_strip.startswith("(") and s_strip.endswith(")"):
            is_negative = True
            s = s_strip[1:-1].strip()

        # Remove common currency markers like 'R$' (case-insensitive)
        s = re.sub(r"(?i)r\$", "", s)

        # Remove spaces that might separate thousands (including thin space)
        s = s.replace("\u2009", "").replace(" ", "")

        # Normalize number separators:
        if "." in s and "," in s:
            # Decide which is decimal by the last occurrence: the separator
            # that appears later is likely the decimal separator.
            last_dot = s.rfind(".")
            last_comma = s.rfind(",")
            if last_dot > last_comma:
                # '.' is decimal separator, remove commas as thousands
                s = s.replace(",", "")
            else:
                # ',' is decimal separator, remove dots as thousands and
                # swap comma to dot for Decimal conversion
                s = s.replace(".", "").replace(",", ".")
        elif "," in s and "." not in s:
            # only comma present -> decimal separator
            s = s.replace(",", ".")
        else:
            # multiple dots -> thousands separators, keep last as decimal
            if s.count(".") > 1:
                parts = s.split(".")
                s = "".join(parts[:-1]) + "." + parts[-1]

        # Strip any remaining non-digit (keep leading '-' and one '.')
        # This removes currency letters like 'Isento' -> will be detected below
        s = re.sub(r"[^0-9\.-]", "", s)

        # After cleaning, if there's no digit, return default
        if not re.search(r"\d", s):
            return default

        # Final conversion to Decimal
        try:
            result = Decimal(s)
            return -result if is_negative else result
        except (InvalidOperation, ValueError) as e:
            self.logger.warning("Failed to parse decimal '%s': %s", s, str(e))
            return default

    def _parse_date(
        self, value: Any, formats: List[str] = None
    ) -> Optional[datetime]:
        """Parse date from string using common Brazilian formats."""
        if not value or pd.isna(value):
            return None

        value = str(value).strip()

        # Default Brazilian date formats
        if formats is None:
            formats = [
                "%d/%m/%Y",
                "%d/%m/%y",
                "%d-%m-%Y",
                "%d-%m-%y",
                "%Y-%m-%d",
                "%d.%m.%Y",
                "%d.%m.%y",
            ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        self.logger.warning(f"Failed to parse date '{value}' with any format")
        return None

    def _get_or_create_asset(
        self, symbol: str, name: str = "", asset_type: str = Asset.ASSET_STOCK
    ) -> Asset:
        """Get existing asset or create new one."""
        # Clean symbol
        symbol = symbol.strip().upper()

        # Try to find existing asset
        asset = Asset.objects.filter(symbol=symbol).first()

        if not asset:
            asset = Asset.objects.create(
                symbol=symbol,
                name=name or symbol,
                asset_type=asset_type,
                currency="BRL",  # Banco Inter is Brazilian
                exchange="B3",  # Brazilian stock exchange
            )
            self.logger.info(f"Created new asset: {asset}")

        return asset


class BancoInterMonthlyReportParser(BancoInterDocumentParser):
    """Parser for Banco Inter Monthly Investment Reports.

    (Relatório Mensal de Investimentos)
    """

    def validate_format(self) -> bool:
        """Validate if file is a Banco Inter monthly report."""
        try:
            if self.file_path.suffix.lower() not in [".csv", ".xlsx", ".xls"]:
                return False

            # Try reading first few rows to check headers
            if self.file_path.suffix.lower() == ".csv":
                df = pd.read_csv(self.file_path, nrows=5, encoding="utf-8")
            else:
                df = pd.read_excel(self.file_path, nrows=5)

            # Look for characteristic headers
            headers = [col.lower() for col in df.columns]
            required_patterns = ["ativo", "posição", "valor", "rentabilidade"]

            return any(
                pattern in " ".join(headers) for pattern in required_patterns
            )

        except Exception as e:
            self.logger.error(f"Error validating monthly report format: {e}")
            return False

    def parse(self) -> Dict[str, Any]:
        """Parse monthly investment report."""
        try:
            # Read the file
            if self.file_path.suffix.lower() == ".csv":
                df = pd.read_csv(self.file_path, encoding="utf-8")
            else:
                df = pd.read_excel(self.file_path)

            positions = []

            # Process each row as a position
            for _, row in df.iterrows():
                position_data = self._parse_position_row(row)
                if position_data:
                    positions.append(position_data)

            return {
                "positions": positions,
                "report_date": timezone.now().date(),
                "source": "banco_inter_monthly_report",
            }

        except Exception as e:
            raise ParseError(f"Failed to parse monthly report: {e}")

    def _parse_position_row(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Parse a single position row from monthly report."""
        try:
            # Try to find symbol/asset name column
            symbol = None
            for col in row.index:
                if any(
                    keyword in col.lower()
                    for keyword in ["ativo", "código", "papel"]
                ):
                    symbol = str(row[col]).strip()
                    break

            if not symbol or symbol.lower() in ["nan", "total"]:
                return None

            # Extract position data
            position_data = {
                "symbol": symbol,
                "quantity": Decimal("0"),
                "value": Decimal("0"),
                "return_percentage": Decimal("0"),
            }

            # Parse columns
            for col in row.index:
                col_lower = col.lower()
                if "posição" in col_lower or "quantidade" in col_lower:
                    position_data["quantity"] = self._parse_decimal(row[col])
                elif "valor" in col_lower and "atual" in col_lower:
                    position_data["value"] = self._parse_decimal(row[col])
                elif "rentabilidade" in col_lower:
                    position_data["return_percentage"] = self._parse_decimal(
                        row[col]
                    )

            return position_data

        except Exception as e:
            self.logger.warning(f"Failed to parse position row: {e}")
            return None


class BancoInterBrokerageNoteParser(BancoInterDocumentParser):
    """Parser for Banco Inter Brokerage Notes (Nota de Corretagem)."""

    def validate_format(self) -> bool:
        """Validate if file is a Banco Inter brokerage note."""
        try:
            if self.file_path.suffix.lower() not in [
                ".pdf",
                ".csv",
                ".xlsx",
                ".xls",
            ]:
                return False

            # For PDF, we'd need to extract text first
            if self.file_path.suffix.lower() == ".pdf":
                # Would need PyPDF2 or similar for PDF parsing
                # For now, return True if it's a PDF
                return True

            # For CSV/Excel files
            if self.file_path.suffix.lower() == ".csv":
                df = pd.read_csv(self.file_path, nrows=10, encoding="utf-8")
            else:
                df = pd.read_excel(self.file_path, nrows=10)

            # Look for brokerage note patterns
            text_content = " ".join(df.astype(str).values.flatten()).lower()
            patterns = ["nota de corretagem", "compra", "venda", "corretagem"]

            return any(pattern in text_content for pattern in patterns)

        except Exception as e:
            self.logger.error(f"Error validating brokerage note format: {e}")
            return False

    def parse(self) -> Dict[str, Any]:
        """Parse brokerage note."""
        try:
            if self.file_path.suffix.lower() == ".pdf":
                return self._parse_pdf_brokerage_note()
            else:
                return self._parse_tabular_brokerage_note()

        except Exception as e:
            raise ParseError(f"Failed to parse brokerage note: {e}")

    def _parse_pdf_brokerage_note(self) -> Dict[str, Any]:
        """Parse PDF brokerage note (placeholder implementation)."""
        # This would require PDF parsing libraries like PyPDF2,
        # pdfplumber, etc.
        # For now, return a placeholder structure
        return {
            "transactions": [],
            "trade_date": timezone.now().date(),
            "total_fees": Decimal("0"),
            "source": "banco_inter_brokerage_note_pdf",
        }

    def _parse_tabular_brokerage_note(self) -> Dict[str, Any]:
        """Parse tabular format brokerage note."""
        # Read the file
        if self.file_path.suffix.lower() == ".csv":
            df = pd.read_csv(self.file_path, encoding="utf-8")
        else:
            df = pd.read_excel(self.file_path)

        transactions = []

        for _, row in df.iterrows():
            transaction_data = self._parse_transaction_row(row)
            if transaction_data:
                transactions.append(transaction_data)

        return {
            "transactions": transactions,
            "trade_date": timezone.now().date(),
            "source": "banco_inter_brokerage_note",
        }

    def _parse_transaction_row(
        self, row: pd.Series
    ) -> Optional[Dict[str, Any]]:
        """Parse a single transaction row."""
        try:
            # Extract transaction data
            transaction_data = {
                "symbol": "",
                "transaction_type": "BUY",
                "quantity": Decimal("0"),
                "price": Decimal("0"),
                "fees": Decimal("0"),
                "date": timezone.now().date(),
            }

            # Parse columns based on common patterns
            for col in row.index:
                col_lower = col.lower()
                if any(
                    keyword in col_lower
                    for keyword in ["papel", "ativo", "código"]
                ):
                    transaction_data["symbol"] = str(row[col]).strip()
                elif "tipo" in col_lower or "operação" in col_lower:
                    op_type = str(row[col]).lower()
                    transaction_data["transaction_type"] = (
                        "SELL" if "venda" in op_type else "BUY"
                    )
                elif "quantidade" in col_lower:
                    transaction_data["quantity"] = self._parse_decimal(
                        row[col]
                    )
                elif "preço" in col_lower:
                    transaction_data["price"] = self._parse_decimal(row[col])
                elif "taxa" in col_lower or "corretagem" in col_lower:
                    transaction_data["fees"] = self._parse_decimal(row[col])
                elif "data" in col_lower:
                    parsed_date = self._parse_date(row[col])
                    if parsed_date:
                        transaction_data["date"] = parsed_date.date()

            if transaction_data["symbol"] and transaction_data["quantity"] > 0:
                return transaction_data

            return None

        except Exception as e:
            self.logger.warning(f"Failed to parse transaction row: {e}")
            return None


class BancoInterExtractParser(BancoInterDocumentParser):
    """Parser for Banco Inter Bank Statements (Extrato)."""

    def validate_format(self) -> bool:
        """Validate if file is a Banco Inter extract."""
        try:
            if self.file_path.suffix.lower() not in [
                ".csv",
                ".xlsx",
                ".xls",
                ".pdf",
            ]:
                return False

            if self.file_path.suffix.lower() == ".pdf":
                return True  # Assume PDF extracts are valid

            # For tabular files
            if self.file_path.suffix.lower() == ".csv":
                df = pd.read_csv(self.file_path, nrows=10, encoding="utf-8")
            else:
                df = pd.read_excel(self.file_path, nrows=10)

            # Look for extract patterns
            headers = [col.lower() for col in df.columns]
            patterns = ["data", "descrição", "valor", "saldo"]

            return (
                sum(
                    1
                    for pattern in patterns
                    if any(pattern in header for header in headers)
                )
                >= 2
            )

        except Exception as e:
            self.logger.error(f"Error validating extract format: {e}")
            return False

    def parse(self) -> Dict[str, Any]:
        """Parse bank extract."""
        try:
            if self.file_path.suffix.lower() == ".pdf":
                return self._parse_pdf_extract()
            else:
                return self._parse_tabular_extract()

        except Exception as e:
            raise ParseError(f"Failed to parse extract: {e}")

    def _parse_pdf_extract(self) -> Dict[str, Any]:
        """Parse PDF extract (placeholder implementation)."""
        return {
            "transactions": [],
            "period_start": timezone.now().date(),
            "period_end": timezone.now().date(),
            "source": "banco_inter_extract_pdf",
        }

    def _parse_tabular_extract(self) -> Dict[str, Any]:
        """Parse tabular format extract."""
        # Read the file
        if self.file_path.suffix.lower() == ".csv":
            df = pd.read_csv(self.file_path, encoding="utf-8")
        else:
            df = pd.read_excel(self.file_path)

        transactions = []

        for _, row in df.iterrows():
            transaction_data = self._parse_extract_row(row)
            if transaction_data:
                transactions.append(transaction_data)

        return {
            "transactions": transactions,
            "period_start": timezone.now().date(),
            "period_end": timezone.now().date(),
            "source": "banco_inter_extract",
        }

    def _parse_extract_row(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Parse a single extract transaction row."""
        try:
            transaction_data = {
                "date": timezone.now().date(),
                "description": "",
                "amount": Decimal("0"),
                "balance": Decimal("0"),
            }

            # Parse columns
            for col in row.index:
                col_lower = col.lower()
                if "data" in col_lower:
                    parsed_date = self._parse_date(row[col])
                    if parsed_date:
                        transaction_data["date"] = parsed_date.date()
                elif "descrição" in col_lower or "histórico" in col_lower:
                    transaction_data["description"] = str(row[col]).strip()
                elif "valor" in col_lower:
                    transaction_data["amount"] = self._parse_decimal(row[col])
                elif "saldo" in col_lower:
                    transaction_data["balance"] = self._parse_decimal(row[col])

            if transaction_data["description"]:
                return transaction_data

            return None

        except Exception as e:
            self.logger.warning(f"Failed to parse extract row: {e}")
            return None


class BancoInterConsolidatedReportParser(BancoInterDocumentParser):
    """Parser for Banco Inter Consolidated Reports (Relatório Consolidado)."""

    def validate_format(self) -> bool:
        """Validate if file is a Banco Inter consolidated report."""
        try:
            if not PDF_AVAILABLE:
                self.logger.warning(
                    "PDF processing not available, cannot parse consolidated"
                    " reports"
                )
                return False

            if self.file_path.suffix.lower() != ".pdf":
                return False

            with pdfplumber.open(self.file_path) as pdf:
                # Check first few pages for characteristic content
                for page_num in range(min(3, len(pdf.pages))):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_lower = text.lower()
                        # Look for consolidated report patterns
                        patterns = [
                            "relatório consolidado",
                            "posição detalhada",
                            "ganhos financeiros",
                            "movimentações no mês",
                        ]
                        if any(pattern in text_lower for pattern in patterns):
                            return True

            return False

        except Exception as e:
            self.logger.error(
                f"Error validating consolidated report format: {e}"
            )
            return False

    def parse(self) -> Dict[str, Any]:
        """Parse consolidated report."""
        try:
            if not PDF_AVAILABLE:
                raise ImportError("PDF processing not available")

            with pdfplumber.open(self.file_path) as pdf:
                # Parse positions and transactions
                positions = self._extract_positions(pdf)
                transactions = self._extract_transactions(pdf)

                return {
                    "positions": positions,
                    "transactions": transactions,
                    "report_date": timezone.now().date(),
                    "source": "banco_inter_consolidated_report",
                }

        except Exception as e:
            raise ParseError(f"Failed to parse consolidated report: {e}")

    def _extract_positions(self, pdf) -> List[Dict[str, Any]]:
        """Extract investment positions from the PDF."""
        positions = []

        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            # Look for position tables (usually on pages 9-12 based on
            # the sample)
            if (
                "saldo anterior" in text.lower()
                and "saldo bruto" in text.lower()
            ):
                # This page contains position data
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue

                    # Process position table rows
                    for row in table:
                        if (
                            not row or len(row) < 7
                        ):  # Need at least asset name and some values
                            continue

                        position = self._parse_position_from_table_row(row)
                        if position:
                            positions.append(position)

        return positions

    def _parse_position_from_table_row(
        self, row: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Parse a position from a table row."""
        try:
            # Skip headers and sub-totals
            if (
                not row
                or not row[0]
                or any(
                    keyword in str(row[0]).lower()
                    for keyword in [
                        "ativos",
                        "sub-total",
                        "total",
                        "saldo anterior",
                        "31/07/2025",
                    ]
                )
            ):
                return None

            asset_name = str(row[0]).strip()
            if not asset_name or len(asset_name) < 2:
                return None

            position_data = {
                "symbol": asset_name,
                "asset_name": asset_name,
                "previous_balance": Decimal("0"),
                "deposits": Decimal("0"),
                "withdrawals": Decimal("0"),
                "events": Decimal("0"),
                "current_balance": Decimal("0"),
                "monthly_return": Decimal("0"),
                "yearly_return": Decimal("0"),
                "total_return": Decimal("0"),
                "allocation_percent": Decimal("0"),
            }

            # Parse values from the row based on expected columns
            # Expected format: Asset, Previous Balance, Deposits,
            # Withdrawals, Events, Current Balance, Monthly %,
            # 12 Month %, Total %, Allocation %
            if len(row) >= 10:
                position_data["previous_balance"] = self._parse_decimal(
                    row[1] if len(row) > 1 else "0"
                )
                position_data["deposits"] = self._parse_decimal(
                    row[2] if len(row) > 2 else "0"
                )
                position_data["withdrawals"] = self._parse_decimal(
                    row[3] if len(row) > 3 else "0"
                )
                position_data["events"] = self._parse_decimal(
                    row[4] if len(row) > 4 else "0"
                )
                position_data["current_balance"] = self._parse_decimal(
                    row[5] if len(row) > 5 else "0"
                )
                position_data["monthly_return"] = self._parse_decimal(
                    row[6] if len(row) > 6 else "0"
                )
                position_data["yearly_return"] = self._parse_decimal(
                    row[7] if len(row) > 7 else "0"
                )
                position_data["total_return"] = self._parse_decimal(
                    row[8] if len(row) > 8 else "0"
                )
                position_data["allocation_percent"] = self._parse_decimal(
                    row[9] if len(row) > 9 else "0"
                )

            # Only return if we have meaningful data
            if (
                position_data["current_balance"] > 0
                or position_data["previous_balance"] > 0
            ):
                return position_data

            return None

        except Exception as e:
            self.logger.warning(f"Failed to parse position row: {e}")
            return None

    def _extract_transactions(self, pdf) -> List[Dict[str, Any]]:
        """Extract transactions from the PDF."""
        transactions = []

        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            # Look for transaction pages (usually pages 13-15 based on sample)
            if (
                "movimentações no mês" in text.lower()
                or self._contains_transaction_patterns(text)
            ):
                # Extract transactions from this page
                page_transactions = self._parse_transactions_from_text(text)
                transactions.extend(page_transactions)

        return transactions

    def _contains_transaction_patterns(self, text: str) -> bool:
        """Check if text contains transaction patterns."""
        patterns = [
            "pgto/rec juros",
            "aplicação",
            "resgate",
            "crédito eventos",
            "cred evento b3",
            "banco inter s a",
        ]
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in patterns)

    def _parse_transactions_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse transactions from page text."""
        transactions = []
        lines = text.split("\n")

        current_date = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line contains a date
            date_match = self._extract_date_from_line(line)
            if date_match:
                current_date = date_match
                continue

            # Check if this line contains a transaction
            transaction = self._parse_transaction_line(line, current_date)
            if transaction:
                transactions.append(transaction)

        return transactions

    def _extract_date_from_line(self, line: str) -> Optional[datetime]:
        """Extract date from a line if it contains one."""
        # Look for Brazilian date patterns

        # Pattern for dates like "29 de Agosto de 2025"
        date_pattern = r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})"
        match = re.search(date_pattern, line)
        if match:
            day, month_name, year = match.groups()
            # Map Portuguese month names to numbers
            month_map = {
                "janeiro": 1,
                "fevereiro": 2,
                "março": 3,
                "abril": 4,
                "maio": 5,
                "junho": 6,
                "julho": 7,
                "agosto": 8,
                "setembro": 9,
                "outubro": 10,
                "novembro": 11,
                "dezembro": 12,
            }
            month = month_map.get(month_name.lower())
            if month:
                try:
                    return datetime(int(year), month, int(day))
                except ValueError:
                    pass

        return None

    def _parse_transaction_line(
        self, line: str, date: Optional[datetime]
    ) -> Optional[Dict[str, Any]]:
        """Parse a transaction from a line."""
        try:
            # Look for transaction patterns with amounts

            # Pattern for amounts like "R$ 1.234,56" or "R$ 1,23"
            amount_pattern = r"R\$\s*([\d.,]+)"
            amounts = re.findall(amount_pattern, line)

            if not amounts:
                return None

            # Get the last amount found (usually the main amount)
            amount_str = amounts[-1]
            amount = self._parse_decimal(amount_str)

            if amount == 0:
                return None

            # Determine transaction type and description
            line_lower = line.lower()

            # Clean the line to get description
            description = re.sub(amount_pattern, "", line).strip()
            description = re.sub(
                r"\s+", " ", description
            )  # Normalize whitespace

            # Determine transaction type
            transaction_type = "DEPOSIT"  # Default
            if any(keyword in line_lower for keyword in ["resgate", "débito"]):
                transaction_type = "WITHDRAWAL"
            elif any(
                keyword in line_lower for keyword in ["aplicação", "crédito"]
            ):
                transaction_type = "DEPOSIT"

            return {
                "description": description,
                "amount": amount,
                "transaction_type": transaction_type,
                "date": date.date() if date else timezone.now().date(),
                "symbol": self._extract_symbol_from_description(description),
            }

        except Exception as e:
            self.logger.warning(
                f"Failed to parse transaction line '{line}': {e}"
            )
            return None

    def _extract_symbol_from_description(self, description: str) -> str:
        """Extract asset symbol from transaction description."""
        # Look for common patterns in Brazilian investment descriptions

        # Look for stock codes (e.g., ITUB4, PETR4)
        stock_pattern = r"\b([A-Z]{4}\d{1,2})\b"
        match = re.search(stock_pattern, description.upper())
        if match:
            return match.group(1)

        # Look for fund codes (e.g., IAAG11, VISC11)
        fund_pattern = r"\b([A-Z]{4}\d{2})\b"
        match = re.search(fund_pattern, description.upper())
        if match:
            return match.group(1)

        # For other types, use a simplified version of the description
        simplified = re.sub(r"[^A-Za-z0-9\s]", "", description)
        words = simplified.split()
        if words:
            return "_".join(words[:3]).upper()  # First 3 words as symbol

        return "UNKNOWN"


class BancoInterImportService:
    """Service for importing Banco Inter documents."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _import_document_sync(
        self, file_path: str, document_type: str, user: User
    ) -> DocumentImport:
        """Synchronous implementation of import_document.

        This contains the original logic and performs ORM operations.
        It's intentionally kept synchronous and may only be called from
        a background thread when invoked from an async context.
        """
        # Create import record
        import_record = DocumentImport.objects.create(
            user=user,
            document_type=document_type,
            original_filename=Path(file_path).name,
            file_path=file_path,
            status="PROCESSING",
        )

        try:
            # Get appropriate parser
            parser = self._get_parser(document_type, file_path, user)

            # Validate format
            if not parser.validate_format():
                raise ImportError(
                    f"Invalid document format for {document_type}"
                )

            # Parse document
            parsed_data = parser.parse()

            # Import data into database
            imported_count = self._import_parsed_data(
                parsed_data, user, import_record
            )

            # Update import record
            import_record.status = "COMPLETED"
            import_record.imported_transactions_count = imported_count
            # Sanitize parsed_data to ensure JSON serializable primitives
            # are stored in the processing_log (Decimals -> str,
            # dates -> isoformat)
            import_record.processing_log = self._sanitize_for_json(parsed_data)
            import_record.save()

            self.logger.info(
                "Successfully imported "
                f"{imported_count} transactions from "
                f"{file_path}"
            )

        except Exception as e:
            # Update import record with error
            import_record.status = "FAILED"
            import_record.error_message = str(e)
            import_record.save()

            self.logger.error(f"Failed to import {file_path}: {e}")
            raise

        return import_record

    def import_document(
        self, file_path: str, document_type: str, user: User
    ) -> Union[DocumentImport, Awaitable[DocumentImport]]:
        """Async-aware wrapper for importing documents.

        If called from a synchronous context, this will execute the
        synchronous import implementation and return the DocumentImport
        instance. If called from an async context (i.e. an event loop is
        running), this function will return an awaitable (a coroutine)
        that should be awaited; internally it will run the synchronous
        import implementation in a thread to avoid Django's
        SynchronousOnlyOperation.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop: safe to run synchronously
            return self._import_document_sync(file_path, document_type, user)

        # Running inside an event loop: delegate to a thread and return
        # the coroutine to be awaited by the caller.
        return asyncio.to_thread(
            self._import_document_sync, file_path, document_type, user
        )

    def _get_parser(
        self, document_type: str, file_path: str, user: User
    ) -> BancoInterDocumentParser:
        """Get appropriate parser for document type."""
        parser_map = {
            "BANCO_INTER_MONTHLY_REPORT": BancoInterMonthlyReportParser,
            "BANCO_INTER_BROKERAGE_NOTE": BancoInterBrokerageNoteParser,
            "BANCO_INTER_EXTRACT": BancoInterExtractParser,
            "BANCO_INTER_CONSOLIDATED_REPORT": (
                BancoInterConsolidatedReportParser
            ),
        }

        parser_class = parser_map.get(document_type)
        if not parser_class:
            raise ImportError(f"Unknown document type: {document_type}")

        return parser_class(file_path, user)

    def _import_parsed_data(
        self,
        parsed_data: Dict[str, Any],
        user: User,
        import_record: DocumentImport,
    ) -> int:
        """Import parsed data into database models."""
        imported_count = 0

        # Get or create default portfolio for imports
        portfolio, created = Portfolio.objects.get_or_create(
            user=user,
            name="Banco Inter Import",
            defaults={
                "description": (
                    "Portfolio created for Banco Inter document imports"
                ),
                "is_active": True,
            },
        )

        # Import transactions
        if "transactions" in parsed_data:
            for transaction_data in parsed_data["transactions"]:
                try:
                    # Get or create asset (handle different transaction
                    # formats)
                    symbol = transaction_data.get("symbol", "CASH")
                    asset = self._get_or_create_asset(symbol)

                    # Get or create position
                    position, created = Position.objects.get_or_create(
                        portfolio=portfolio,
                        asset=asset,
                        defaults={
                            "quantity": Decimal("0"),
                            "average_cost": Decimal("0"),
                            "first_purchase_date": transaction_data.get(
                                "date", timezone.now().date()
                            ),
                        },
                    )

                    # Create transaction (handle different formats)
                    # For consolidated reports, transactions are more like
                    # cash flows
                    if "amount" in transaction_data:
                        # Consolidated report transaction (cash flow)
                        Transaction.objects.create(
                            position=position,
                            transaction_type=transaction_data.get(
                                "transaction_type", "DEPOSIT"
                            ),
                            quantity=transaction_data[
                                "amount"
                            ],  # Use amount as quantity for cash flows
                            price=Decimal(
                                "1"
                            ),  # Price of 1 for cash transactions
                            fees=Decimal("0"),
                            transaction_date=transaction_data.get(
                                "date", timezone.now().date()
                            ),
                            notes=(
                                "Imported from "
                                + str(
                                    import_record.get_document_type_display()
                                )
                                + ": "
                                + str(transaction_data.get("description", ""))
                            ),
                        )
                    else:
                        # Standard brokerage note transaction
                        Transaction.objects.create(
                            position=position,
                            transaction_type=transaction_data.get(
                                "transaction_type", "BUY"
                            ),
                            quantity=transaction_data.get(
                                "quantity", Decimal("0")
                            ),
                            price=transaction_data.get("price", Decimal("0")),
                            fees=transaction_data.get("fees", Decimal("0")),
                            transaction_date=transaction_data.get(
                                "date", timezone.now().date()
                            ),
                            notes=(
                                "Imported from "
                                f"{import_record.get_document_type_display()}"
                            ),
                        )

                    imported_count += 1

                except Exception as e:
                    self.logger.warning(
                        f"Failed to import transaction {transaction_data}: {e}"
                    )

        # Import positions (for monthly reports and consolidated reports)
        if "positions" in parsed_data:
            for position_data in parsed_data["positions"]:
                try:
                    # Get or create asset
                    asset = self._get_or_create_asset(position_data["symbol"])

                    # For consolidated reports, we have more detailed
                    # position data
                    if "current_balance" in position_data:
                        # Consolidated report position
                        quantity = position_data.get(
                            "current_balance", Decimal("0")
                        )
                        # Try to calculate average cost if we have enough data
                        if (
                            quantity > 0
                            and "previous_balance" in position_data
                        ):
                            # Use current balance as quantity for valuation
                            average_cost = Decimal(
                                "1"
                            )  # Default for valuations
                        else:
                            average_cost = Decimal("0")
                    else:
                        # Simple monthly report position
                        quantity = position_data.get("quantity", Decimal("0"))
                        average_cost = Decimal("0")

                    # Update or create position
                    position, created = Position.objects.update_or_create(
                        portfolio=portfolio,
                        asset=asset,
                        defaults={
                            "quantity": quantity,
                            "average_cost": average_cost,
                            "first_purchase_date": timezone.now().date(),
                        },
                    )

                    imported_count += 1

                except Exception as e:
                    self.logger.warning(
                        f"Failed to import position {position_data}: {e}"
                    )

        return imported_count

    def _get_or_create_asset(self, symbol: str) -> Asset:
        """Get existing asset or create new one."""
        symbol = symbol.strip().upper()

        asset = Asset.objects.filter(symbol=symbol).first()

        if not asset:
            asset = Asset.objects.create(
                symbol=symbol,
                name=symbol,
                asset_type=Asset.ASSET_STOCK,
                currency="BRL",
                exchange="B3",
            )
            self.logger.info(f"Created new asset: {asset}")

        return asset

    def _sanitize_for_json(self, obj: Any) -> Any:
        """Recursively convert non-JSON-serializable objects into
        JSON-friendly primitives.

        - Decimal -> str (preserve exactness)
        - datetime/date -> ISO 8601 string
        - tuples -> lists
        - dicts/lists are walked recursively
        """

        # Local imports/types are fine
        if isinstance(obj, Decimal):
            return str(obj)

        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, date) and not isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items()}

        if isinstance(obj, (list, tuple)):
            return [self._sanitize_for_json(v) for v in obj]

        # Fallback: leave as-is (JSONField will error if truly unserializable)
        return obj
