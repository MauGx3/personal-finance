# Banco Inter Import Documentation

This document describes the Banco Inter document import functionality added to the personal finance application.

## Overview

The application now supports importing financial data from three types of Banco Inter documents:

1. **Relatório Mensal de Investimentos** (Monthly Investment Report)
2. **Nota de Corretagem** (Brokerage Note)
3. **Extrato** (Bank Statement)

## Supported File Formats

- CSV (.csv)
- Excel (.xlsx, .xls)
- PDF (.pdf) - Limited support, mainly for brokerage notes and extracts

## API Endpoints

### Upload Document
```
POST /api/data-sources/import/upload/
```

**Parameters:**
- `file`: The document file to import
- `document_type`: Type of document (see Document Types below)

**Example:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "file=@monthly_report.csv" \
  -F "document_type=BANCO_INTER_MONTHLY_REPORT" \
  http://localhost:8000/api/data-sources/import/upload/
```

### List Imports
```
GET /api/data-sources/import/
```

**Query Parameters:**
- `status`: Filter by status (PENDING, PROCESSING, COMPLETED, FAILED)
- `document_type`: Filter by document type

### Get Import Details
```
GET /api/data-sources/import/{import_id}/
```

### Retry Failed Import
```
POST /api/data-sources/import/{import_id}/retry/
```

### Get Supported Document Types
```
GET /api/data-sources/import/types/
```

## Document Types

### BANCO_INTER_MONTHLY_REPORT
Monthly investment portfolio report showing current positions and performance.

**Expected CSV Format:**
```csv
Ativo,Posição,Valor Atual,Rentabilidade
PETR4,100,"R$ 2.500,00","5,50%"
VALE3,50,"R$ 3.200,00","2,30%"
```

**Required Columns (flexible naming):**
- Asset/Symbol (Ativo, Código, Papel)
- Position/Quantity (Posição, Quantidade)
- Current Value (Valor, Valor Atual)
- Return (Rentabilidade) - Optional

### BANCO_INTER_BROKERAGE_NOTE
Trading confirmation document showing buy/sell transactions with fees.

**Expected CSV Format:**
```csv
Data,Papel,Tipo,Quantidade,Preço,Taxa
01/01/2024,PETR4,Compra,100,"R$ 25,00","R$ 10,00"
```

**Required Columns:**
- Date (Data)
- Asset/Symbol (Papel, Ativo, Código)
- Transaction Type (Tipo, Operação)
- Quantity (Quantidade)
- Price (Preço)
- Fees (Taxa, Corretagem) - Optional

### BANCO_INTER_EXTRACT
Bank account statement showing all account transactions.

**Expected CSV Format:**
```csv
Data,Descrição,Valor,Saldo
01/01/2024,"Transferência recebida","R$ 1.000,00","R$ 5.000,00"
```

**Required Columns:**
- Date (Data)
- Description (Descrição, Histórico)
- Amount (Valor)
- Balance (Saldo) - Optional

## Number Format Support

The import system supports Brazilian number formats:
- `R$ 1.234,56` → 1234.56
- `1.234,56` → 1234.56
- `(123,45)` → -123.45 (negative values in parentheses)

## Date Format Support

Supported date formats:
- `dd/mm/yyyy` (e.g., 31/12/2024)
- `dd/mm/yy` (e.g., 31/12/24)
- `dd-mm-yyyy` (e.g., 31-12-2024)
- `yyyy-mm-dd` (e.g., 2024-12-31)
- `dd.mm.yyyy` (e.g., 31.12.2024)

## Import Process

1. **File Upload**: User uploads a supported document file
2. **Format Validation**: System validates file format and structure
3. **Data Parsing**: Document content is parsed and structured
4. **Data Import**: Parsed data is imported into the application:
   - Assets are created automatically if they don't exist
   - A "Banco Inter Import" portfolio is created for imported data
   - Transactions and positions are created as appropriate
5. **Status Update**: Import status is updated (COMPLETED or FAILED)

## Error Handling

The system provides detailed error messages for:
- Unsupported file formats
- Invalid document structure
- Data parsing errors
- Database import errors

Failed imports can be retried using the retry endpoint.

## Database Models

### DocumentImport
Tracks all import operations with:
- User who initiated the import
- Document type and filename
- Import status and error messages
- Count of imported transactions
- Detailed processing log

## Admin Interface

Administrators can view and manage document imports through the Django admin interface at `/admin/data_sources/documentimport/`.

## Testing

Run tests for the import functionality:
```bash
python manage.py test personal_finance.data_sources.tests
```

## Security Considerations

- File uploads are limited to 10MB
- Only authenticated users can import documents
- Users can only access their own import records
- File types are restricted to supported formats
- Uploaded files are stored securely

## Future Enhancements

Planned improvements include:
- Enhanced PDF parsing support
- Automatic duplicate detection
- Import validation rules
- Bulk import operations
- Import scheduling
- Additional bank support
