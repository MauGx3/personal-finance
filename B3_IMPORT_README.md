# B3 Import Functionality

This module provides comprehensive import capabilities for B3 (Brazilian Stock Exchange) documents, enabling users to import transaction data from common B3 documents into their personal finance management system.

## Supported Documents

### 1. Nota de Corretagem (Brokerage Note)
- **Purpose**: Official document detailing stock transactions executed on a trading day
- **Contains**: Stock purchases, sales, fees, taxes, and settlement information
- **Format**: Text-based document with structured transaction data

### 2. Extrato (Statement) 
- **Purpose**: Account statement showing cash movements and balances
- **Contains**: Deposits, withdrawals, dividends, fees, and running balance
- **Format**: Chronological list of account movements

## Features

- ✅ **Automatic document type detection**
- ✅ **Brazilian decimal format parsing** (1.250,50 → 1250.50)
- ✅ **Transaction categorization** (Buy/Sell/Dividends/Fees)
- ✅ **Brazilian Real (BRL) currency support**
- ✅ **B3 ticker format handling** (PETR4, VALE3, etc.)
- ✅ **Comprehensive error handling and validation**
- ✅ **Fee and tax extraction**
- ✅ **Net value calculations**

## Usage

### Command Line Interface

```bash
# Import with auto-detection
python import_b3.py --file document.txt --auto-detect

# Import specific document type
python import_b3.py --file nota_corretagem.txt --type nota_corretagem
python import_b3.py --file extrato.txt --type extrato

# Save results to JSON
python import_b3.py --file document.txt --auto-detect --output results.json

# Verbose output for debugging
python import_b3.py --file document.txt --auto-detect --verbose
```

### Programmatic Usage

```python
from personal_finance.data_sources.b3_import import B3DocumentImporter

# Initialize importer
importer = B3DocumentImporter()

# Load document content
with open('nota_corretagem.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Auto-detect document type
document_type = importer.detect_document_type(content)

# Import document
result = importer.import_document(content, document_type)

# Access parsed data
print(f"Found {len(result.transactions)} transactions")
for tx in result.transactions:
    print(f"{tx.date}: {tx.ticker} {tx.transaction_type.value} "
          f"{tx.quantity} @ R$ {tx.unit_price}")
```

### Integration with Data Sources

```python
from personal_finance.data_sources.services import DataSourceManager

# Initialize data source manager (includes B3 support)
manager = DataSourceManager()

# Get Brazilian stock price
price_data = manager.get_current_price("PETR4")

# Search Brazilian stocks
results = manager.search_symbol("PETROBRAS")
```

## Data Structures

### B3Transaction
Represents a single transaction from Nota de Corretagem:

```python
@dataclass
class B3Transaction:
    date: date
    transaction_type: B3TransactionType  # BUY, SELL, DIVIDEND, etc.
    ticker: str                          # PETR4, VALE3, etc.
    market_type: B3MarketType           # SPOT, OPTIONS, etc.
    quantity: int
    unit_price: Decimal
    total_value: Decimal
    brokerage_fee: Decimal
    settlement_fee: Decimal
    # ... other fees
    net_value: Decimal                  # Auto-calculated
```

### B3ExtractEntry
Represents an entry from Extrato:

```python
@dataclass
class B3ExtractEntry:
    date: date
    description: str
    credit: Optional[Decimal]
    debit: Optional[Decimal]
    balance: Optional[Decimal]
    document_number: Optional[str]
```

## Supported Transaction Types

- **C** (Compra) → `B3TransactionType.BUY`
- **V** (Venda) → `B3TransactionType.SELL`
- **DIV** → `B3TransactionType.DIVIDEND`
- **JCP** → `B3TransactionType.JCP` (Juros sobre Capital Próprio)
- **SPLIT** → `B3TransactionType.SPLIT`
- **GROUP** → `B3TransactionType.GROUPING`
- **BONUS** → `B3TransactionType.BONUS`
- **SUB** → `B3TransactionType.SUBSCRIPTION`

## Market Types

- **VISTA** → `B3MarketType.SPOT` (Spot market)
- **TERMO** → `B3MarketType.FORWARD` (Forward market)
- **OPCOES** → `B3MarketType.OPTIONS` (Options market)
- **FUTURO** → `B3MarketType.FUTURES` (Futures market)
- **ETF** → `B3MarketType.ETF` (Exchange Traded Funds)

## Examples

### Sample Nota de Corretagem
```
                            NOTA DE CORRETAGEM
Data pregão: 15/03/2024

PETR4         PETROBRAS PN  C   100    25,50        2.550,00      D
VALE3         VALE ON       C   200    45,75        9.150,00      D  
ITUB4         ITAU PN       V   150    30,20        4.530,00      C

Taxa de corretagem                                        25,00  
Emolumentos                                                5,00
```

### Sample Extrato
```
DATA       HISTÓRICO                               DÉBITO      CRÉDITO     SALDO

01/03/2024 Saldo anterior                                                120.000,00
15/03/2024 Compra PETR4 - 100 cotas                2.550,00             122.450,00
20/03/2024 Dividendos PETR4                                    125,50    117.908,25
```

## Testing

Run the test suite to verify functionality:

```bash
# Simple functionality tests
python test_b3_simple.py

# Test with sample documents
python import_b3.py --file examples/sample_nota_corretagem.txt --auto-detect
python import_b3.py --file examples/sample_extrato.txt --auto-detect
```

## Error Handling

The import system provides comprehensive error handling:

- **Parsing errors**: Invalid number formats, missing data
- **Date errors**: Invalid or missing dates
- **Document structure errors**: Unrecognized format
- **Encoding errors**: Automatic fallback to latin-1 for Brazilian documents

All errors are collected and reported in the import result, allowing you to process valid data while being aware of any issues.

## Currency Support

- All monetary values are handled in **Brazilian Real (BRL)**
- Automatic conversion of Brazilian decimal format (comma as decimal separator)
- Support for thousands separators (dots)

## Future Enhancements

- PDF parsing support (currently text-only)
- Integration with B3 real-time APIs
- Advanced fee allocation algorithms
- Support for additional document types
- Automatic tax calculation for Brazilian regulations

## Contributing

When adding new features:

1. Follow the existing pattern for parsers
2. Add comprehensive tests
3. Update documentation
4. Handle Brazilian-specific formats (dates, decimals, etc.)
5. Consider encoding issues (UTF-8 vs latin-1)