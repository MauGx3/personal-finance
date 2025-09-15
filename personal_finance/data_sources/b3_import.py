"""B3 (Brazilian Stock Exchange) document import functionality.

This module provides data import capabilities for B3 documents including:
- Nota de Corretagem (Brokerage Note)
- Extrato (Statement)

Supports parsing common B3 document formats and extracting transaction data
for portfolio management and tax reporting.
"""

import re
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
from enum import Enum

logger = logging.getLogger(__name__)


class B3TransactionType(Enum):
    """Types of B3 transactions."""
    
    BUY = "C"  # Compra
    SELL = "V"  # Venda
    DIVIDEND = "DIV"  # Dividendo
    JCP = "JCP"  # Juros sobre Capital Próprio
    SPLIT = "SPLIT"  # Desdobramento
    GROUPING = "GROUP"  # Grupamento
    BONUS = "BONUS"  # Bonificação
    SUBSCRIPTION = "SUB"  # Subscrição


class B3MarketType(Enum):
    """B3 market types."""
    
    SPOT = "VISTA"  # Mercado à vista
    FORWARD = "TERMO"  # Mercado a termo
    OPTIONS = "OPCOES"  # Mercado de opções
    FUTURES = "FUTURO"  # Mercado futuro
    ETF = "ETF"  # Exchange Traded Fund


@dataclass
class B3Transaction:
    """Represents a B3 transaction from Nota de Corretagem or Extrato."""
    
    date: date
    transaction_type: B3TransactionType
    ticker: str
    market_type: B3MarketType
    quantity: int
    unit_price: Decimal
    total_value: Decimal
    brokerage_fee: Decimal = Decimal('0.00')
    settlement_fee: Decimal = Decimal('0.00')
    registration_fee: Decimal = Decimal('0.00')
    emoluments: Decimal = Decimal('0.00')
    iss_tax: Decimal = Decimal('0.00')
    irrf_tax: Decimal = Decimal('0.00')
    net_value: Optional[Decimal] = None
    
    def __post_init__(self):
        """Calculate net value if not provided."""
        if self.net_value is None:
            total_fees = (
                self.brokerage_fee + self.settlement_fee + 
                self.registration_fee + self.emoluments + 
                self.iss_tax + self.irrf_tax
            )
            if self.transaction_type == B3TransactionType.BUY:
                self.net_value = self.total_value + total_fees
            else:
                self.net_value = self.total_value - total_fees


@dataclass
class B3ExtractEntry:
    """Represents an entry from B3 Extrato (Statement)."""
    
    date: date
    description: str
    credit: Optional[Decimal] = None
    debit: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    document_number: Optional[str] = None


@dataclass
class B3ImportResult:
    """Result of B3 document import."""
    
    transactions: List[B3Transaction]
    extract_entries: List[B3ExtractEntry]
    summary: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class B3DocumentParser(ABC):
    """Abstract base class for B3 document parsers."""
    
    @abstractmethod
    def parse(self, content: str) -> B3ImportResult:
        """Parse B3 document content.
        
        Args:
            content: Raw document content (text or extracted from PDF)
            
        Returns:
            B3ImportResult with parsed transactions and data
        """
        pass


class NotaCorretagemParser(B3DocumentParser):
    """Parser for B3 Nota de Corretagem (Brokerage Note)."""
    
    # Regex patterns for parsing Nota de Corretagem
    PATTERNS = {
        'date': r'Data pregão:\s*(\d{2}/\d{2}/\d{4})',
        'transaction': r'(\w+\d*)\s+[^\n]*?([CV])\s+(\d+)\s+([\d,\.]+)\s+([\d,\.]+)',
        'fees': r'Taxa de liquidação\s+([\d,\.]+)',
        'brokerage': r'Taxa de corretagem\s+([\d,\.]+)',
        'emoluments': r'Emolumentos\s+([\d,\.]+)',
    }
    
    def parse(self, content: str) -> B3ImportResult:
        """Parse Nota de Corretagem content."""
        transactions = []
        errors = []
        warnings = []
        
        try:
            # Extract trade date
            date_match = re.search(self.PATTERNS['date'], content)
            if not date_match:
                errors.append("Could not find trade date in document")
                trade_date = date.today()
                warnings.append("Using current date as fallback")
            else:
                date_str = date_match.group(1)
                trade_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            
            # Extract transactions - look for lines with ticker, C/V, quantity, price, total
            lines = content.split('\n')
            for line in lines:
                # Look for transaction lines that have the pattern: TICKER ... C/V ... numbers
                if re.search(r'\b\w+\d+\b.*[CV]\s+\d+\s+[\d,\.]+\s+[\d,\.]+', line):
                    # Extract components using a more flexible pattern
                    parts = line.split()
                    ticker = None
                    tx_type = None
                    quantity = None
                    price = None
                    total = None
                    
                    # Find ticker (usually at the start, format like PETR4, VALE3, etc.)
                    for part in parts:
                        if re.match(r'\w+\d+$', part):
                            ticker = part
                            break
                    
                    # Find transaction type (C or V)
                    for part in parts:
                        if part in ['C', 'V']:
                            tx_type = part
                            break
                    
                    # Find numeric values (quantity, price, total)
                    numeric_parts = []
                    for part in parts:
                        if re.match(r'[\d,\.]+$', part):
                            numeric_parts.append(part)
                    
                    # Try to assign the numeric values
                    if len(numeric_parts) >= 3:
                        quantity = numeric_parts[0]
                        price = numeric_parts[1] 
                        total = numeric_parts[2]
                    
                    if all([ticker, tx_type, quantity, price, total]):
                        try:
                            quantity_int = int(quantity)
                            unit_price = self._parse_decimal(price)
                            total_value = self._parse_decimal(total)
                            
                            # Determine transaction type
                            tx_type_enum = (B3TransactionType.BUY 
                                          if tx_type == 'C' 
                                          else B3TransactionType.SELL)
                            
                            # Extract fees (simplified - in real implementation, 
                            # fees would be allocated proportionally)
                            fees = self._extract_fees(content)
                            
                            transaction = B3Transaction(
                                date=trade_date,
                                transaction_type=tx_type_enum,
                                ticker=ticker,
                                market_type=B3MarketType.SPOT,
                                quantity=quantity_int,
                                unit_price=unit_price,
                                total_value=total_value,
                                **fees
                            )
                            
                            transactions.append(transaction)
                            
                        except (ValueError, IndexError) as e:
                            errors.append(f"Error parsing transaction {line.strip()}: {e}")
                            
        except Exception as e:
            errors.append(f"General parsing error: {e}")
        
        summary = {
            'document_type': 'Nota de Corretagem',
            'trade_date': trade_date,
            'total_transactions': len(transactions),
            'total_buy_value': sum(
                t.total_value for t in transactions 
                if t.transaction_type == B3TransactionType.BUY
            ),
            'total_sell_value': sum(
                t.total_value for t in transactions 
                if t.transaction_type == B3TransactionType.SELL
            )
        }
        
        return B3ImportResult(
            transactions=transactions,
            extract_entries=[],
            summary=summary,
            errors=errors,
            warnings=warnings
        )
    
    def _parse_decimal(self, value_str: str) -> Decimal:
        """Parse Brazilian decimal format to Decimal."""
        # Replace comma with dot for decimal separator
        # Handle thousands separator
        cleaned = value_str.replace('.', '').replace(',', '.')
        return Decimal(cleaned)
    
    def _extract_fees(self, content: str) -> Dict[str, Decimal]:
        """Extract fees from document content."""
        fees = {
            'brokerage_fee': Decimal('0.00'),
            'settlement_fee': Decimal('0.00'),
            'emoluments': Decimal('0.00'),
        }
        
        # Extract brokerage fee
        brokerage_match = re.search(self.PATTERNS['brokerage'], content)
        if brokerage_match:
            fees['brokerage_fee'] = self._parse_decimal(brokerage_match.group(1))
        
        # Extract settlement fee
        settlement_match = re.search(self.PATTERNS['fees'], content)
        if settlement_match:
            fees['settlement_fee'] = self._parse_decimal(settlement_match.group(1))
        
        # Extract emoluments
        emoluments_match = re.search(self.PATTERNS['emoluments'], content)
        if emoluments_match:
            fees['emoluments'] = self._parse_decimal(emoluments_match.group(1))
        
        return fees


class ExtratoParser(B3DocumentParser):
    """Parser for B3 Extrato (Statement)."""
    
    # Regex patterns for parsing Extrato
    PATTERNS = {
        'entry': r'(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d,\.\-]+)?\s+([\d,\.\-]+)?\s+([\d,\.\-]+)',
        'balance': r'Saldo\s+em\s+(\d{2}/\d{2}/\d{4}):\s+R\$\s+([\d,\.\-]+)',
    }
    
    def parse(self, content: str) -> B3ImportResult:
        """Parse Extrato content."""
        extract_entries = []
        errors = []
        warnings = []
        
        try:
            # Extract entries
            entry_matches = re.findall(self.PATTERNS['entry'], content)
            
            for match in entry_matches:
                date_str, description, credit_str, debit_str, balance_str = match
                
                try:
                    entry_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                    
                    credit = None
                    if credit_str and credit_str.strip():
                        credit = self._parse_decimal(credit_str)
                    
                    debit = None  
                    if debit_str and debit_str.strip():
                        debit = self._parse_decimal(debit_str)
                    
                    balance = None
                    if balance_str and balance_str.strip():
                        balance = self._parse_decimal(balance_str)
                    
                    entry = B3ExtractEntry(
                        date=entry_date,
                        description=description.strip(),
                        credit=credit,
                        debit=debit,
                        balance=balance
                    )
                    
                    extract_entries.append(entry)
                    
                except (ValueError, IndexError) as e:
                    errors.append(f"Error parsing extract entry {match}: {e}")
                    
        except Exception as e:
            errors.append(f"General parsing error: {e}")
        
        summary = {
            'document_type': 'Extrato',
            'total_entries': len(extract_entries),
            'period_start': min(e.date for e in extract_entries) if extract_entries else None,
            'period_end': max(e.date for e in extract_entries) if extract_entries else None,
        }
        
        return B3ImportResult(
            transactions=[],
            extract_entries=extract_entries,
            summary=summary,
            errors=errors,
            warnings=warnings
        )
    
    def _parse_decimal(self, value_str: str) -> Decimal:
        """Parse Brazilian decimal format to Decimal."""
        # Handle negative values
        is_negative = '-' in value_str
        cleaned = value_str.replace('-', '').replace('.', '').replace(',', '.')
        result = Decimal(cleaned)
        return -result if is_negative else result


class B3DocumentImporter:
    """Main class for importing B3 documents."""
    
    def __init__(self):
        self.parsers = {
            'nota_corretagem': NotaCorretagemParser(),
            'extrato': ExtratoParser(),
        }
    
    def import_document(self, content: str, document_type: str) -> B3ImportResult:
        """Import B3 document.
        
        Args:
            content: Document content (text or extracted from PDF)
            document_type: Type of document ('nota_corretagem' or 'extrato')
            
        Returns:
            B3ImportResult with parsed data
        """
        if document_type not in self.parsers:
            raise ValueError(f"Unsupported document type: {document_type}")
        
        parser = self.parsers[document_type]
        return parser.parse(content)
    
    def detect_document_type(self, content: str) -> Optional[str]:
        """Auto-detect document type from content.
        
        Args:
            content: Document content
            
        Returns:
            Document type or None if not detected
        """
        # Simple heuristics for document type detection
        content_lower = content.lower()
        
        if 'nota de corretagem' in content_lower or 'data pregão' in content_lower:
            return 'nota_corretagem'
        elif 'extrato' in content_lower or 'saldo em' in content_lower:
            return 'extrato'
        
        return None
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported document types."""
        return list(self.parsers.keys())