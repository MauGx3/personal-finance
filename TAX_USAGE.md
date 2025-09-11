# Tax Reporting and Optimization Usage Guide

This guide covers the comprehensive tax reporting and optimization features of the personal finance platform.

## Overview

The tax module provides comprehensive tools for:
- **Tax Calculation**: Automatic calculation of capital gains/losses and dividend income
- **Tax Loss Harvesting**: Identification and optimization of tax loss opportunities
- **Tax Optimization**: Personalized recommendations for tax-efficient strategies
- **Tax Reporting**: Generation of tax forms and reports (Schedule D, 1099-DIV equivalent, etc.)
- **Wash Sale Detection**: Automatic detection and handling of wash sale rules
- **Tax Lot Tracking**: Precise cost basis tracking with FIFO/LIFO methods

## Features

### 🧮 Tax Calculation Engine

Automatically processes transactions to calculate:
- Capital gains and losses (short-term vs long-term)
- Dividend income classification (qualified vs ordinary)
- Cost basis tracking with tax lot management
- Wash sale rule compliance

### 📊 Tax Loss Harvesting

Identifies opportunities to realize losses for tax benefits:
- Unrealized loss analysis across all positions
- Wash sale period tracking and avoidance
- Alternative investment suggestions
- Tax benefit estimation

### 🎯 Tax Optimization Recommendations

Provides personalized recommendations for:
- Asset location optimization (taxable vs tax-advantaged accounts)
- Tax-efficient rebalancing strategies
- Holding period optimization for long-term capital gains
- Year-end tax planning strategies

### 📋 Tax Report Generation

Generates comprehensive tax reports:
- **Schedule D**: Capital gains and losses summary
- **Form 1099-DIV**: Dividend income equivalent
- **Form 8949**: Detailed sales and dispositions
- **Tax Summary**: Comprehensive annual overview
- **Loss Carryforward**: Multi-year loss tracking

## API Endpoints

### Tax Analytics

```bash
# Get comprehensive tax summary
GET /api/tax/analytics/summary/?year=2024&portfolio_id=1

# Trigger tax calculations
POST /api/tax/analytics/calculate/
{
    "year": 2024,
    "portfolio_id": 1,
    "reprocess": false
}
```

### Tax Loss Harvesting

```bash
# List current opportunities
GET /api/tax/loss-harvesting/

# Analyze for new opportunities
POST /api/tax/loss-harvesting/analyze/
{
    "minimum_loss_threshold": 100.00,
    "generate_recommendations": true
}
```

### Tax Reports

```bash
# List generated reports
GET /api/tax/reports/

# Generate new reports
POST /api/tax/reports/generate/
{
    "year": 2024,
    "report_type": "all"  # or specific: schedule_d, form_1099_div, etc.
}
```

### Tax Optimization

```bash
# List recommendations
GET /api/tax/recommendations/

# Generate new recommendations
POST /api/tax/recommendations/generate/
{
    "year": 2024
}

# Mark recommendation as implemented
POST /api/tax/recommendations/{id}/mark_implemented/
{
    "notes": "Moved bonds to 401k account"
}
```

### Tax Data Views

```bash
# View capital gains/losses
GET /api/tax/capital-gains-losses/?tax_year=1&term=long

# View dividend income
GET /api/tax/dividend-income/?tax_year=1&dividend_type=qualified

# View tax lots
GET /api/tax/tax-lots/?position__portfolio=1
```

## Management Commands

### Calculate Tax Implications

Process transactions for tax calculations:

```bash
# Calculate taxes for all users
python manage.py calculate_taxes

# Calculate for specific user and year
python manage.py calculate_taxes --user admin --year 2024

# Reprocess existing calculations
python manage.py calculate_taxes --user admin --reprocess

# Process specific transaction
python manage.py calculate_taxes --transaction-id 123

# Dry run to preview
python manage.py calculate_taxes --user admin --dry-run --verbose
```

### Identify Loss Harvesting Opportunities

Find tax loss harvesting opportunities:

```bash
# Analyze all users
python manage.py identify_loss_harvesting

# Analyze specific user
python manage.py identify_loss_harvesting --user admin

# Set minimum loss threshold
python manage.py identify_loss_harvesting --minimum-loss 500

# Generate recommendations
python manage.py identify_loss_harvesting --generate-recommendations

# Preview analysis
python manage.py identify_loss_harvesting --dry-run --verbose
```

### Generate Tax Reports

Create comprehensive tax reports:

```bash
# Generate all reports for all users
python manage.py generate_tax_reports

# Generate for specific user and year
python manage.py generate_tax_reports --user admin --year 2024

# Generate specific report type
python manage.py generate_tax_reports --report-type schedule_d

# Save to file
python manage.py generate_tax_reports --output-dir /tmp/tax_reports

# Preview what would be generated
python manage.py generate_tax_reports --dry-run --verbose
```

## Usage Examples

### Basic Tax Calculation

```python
from personal_finance.tax.services import TaxCalculationService
from personal_finance.tax.models import TaxYear

# Initialize service
tax_service = TaxCalculationService()

# Get tax year
tax_year = TaxYear.objects.get(year=2024)

# Calculate capital gains/losses
capital_gains = tax_service.calculate_capital_gains_losses(user, tax_year)
print(f"Net capital gain/loss: ${capital_gains['totals']['net_capital_gain_loss']}")

# Calculate dividend income
dividends = tax_service.calculate_dividend_income(user, tax_year)
print(f"Total qualified dividends: ${dividends['qualified_dividends']}")
```

### Tax Loss Harvesting Analysis

```python
from personal_finance.tax.services import TaxLossHarvestingService

# Initialize service
loss_service = TaxLossHarvestingService()

# Find opportunities
opportunities = loss_service.identify_loss_harvesting_opportunities(
    user, minimum_loss_threshold=Decimal('250')
)

# Generate recommendations
loss_service.generate_loss_harvesting_recommendations(opportunities)

for opp in opportunities:
    print(f"{opp.position.asset.symbol}: ${opp.potential_loss_amount} loss")
    print(f"  Status: {opp.status}")
    print(f"  Estimated benefit: ${opp.tax_benefit_estimate}")
```

### Tax Report Generation

```python
from personal_finance.tax.report_service import TaxReportService

# Initialize service
report_service = TaxReportService()

# Generate Schedule D
schedule_d = report_service.generate_schedule_d_report(user, tax_year)
print(f"Net capital gain/loss: ${schedule_d.net_capital_gain_loss}")

# Generate all reports
reports = report_service.generate_all_tax_reports(user, tax_year)
for report_type, report in reports.items():
    print(f"{report_type}: {report.get_report_type_display()}")
```

### Tax Optimization

```python
from personal_finance.tax.services import TaxOptimizationService

# Initialize service
optimization_service = TaxOptimizationService()

# Generate recommendations
recommendations = optimization_service.generate_tax_optimization_recommendations(user)

for rec in recommendations:
    print(f"{rec.title}")
    print(f"  Priority: {rec.priority}")
    print(f"  Estimated savings: ${rec.estimated_tax_savings}")
    print(f"  Deadline: {rec.deadline}")
```

## Admin Interface

### Tax Management Dashboard

Access comprehensive tax management through Django admin:

1. **Tax Years**: Configure tax year settings and brackets
2. **Tax Lots**: View and manage individual tax lots
3. **Capital Gains/Losses**: Monitor realized gains and losses
4. **Dividend Income**: Track dividend payments and classifications
5. **Loss Harvesting**: Review identified opportunities
6. **Recommendations**: Manage tax optimization suggestions
7. **Reports**: Access generated tax reports

### Key Admin Features

- **Color-coded displays**: Visual indicators for gains/losses
- **Advanced filtering**: Filter by user, tax year, asset type, etc.
- **Bulk operations**: Process multiple records efficiently
- **Performance visualization**: Charts and graphs for key metrics
- **Export capabilities**: Export data for external analysis

## Tax Year Configuration

### Setting Up Tax Years

```python
from personal_finance.tax.models import TaxYear

# Create tax year with current brackets
tax_year_2024 = TaxYear.objects.create(
    year=2024,
    filing_deadline='2025-04-15',
    standard_deduction_single=13850,
    standard_deduction_married=27700,
    long_term_capital_gains_thresholds={
        '0': {'min': 0, 'max': 44625, 'rate': 0.0},
        '15': {'min': 44626, 'max': 492300, 'rate': 0.15},
        '20': {'min': 492301, 'max': None, 'rate': 0.20}
    },
    short_term_capital_gains_rate=0.37
)
```

## Best Practices

### For Developers

1. **Always use Decimal**: Use Decimal type for financial calculations
2. **Validate wash sales**: Check wash sale rules before sales
3. **Track tax lots**: Maintain detailed cost basis records
4. **Regular processing**: Run tax calculations regularly
5. **Error handling**: Implement comprehensive error handling

### For Users

1. **Regular updates**: Keep transaction data current
2. **Review opportunities**: Check loss harvesting regularly
3. **Plan ahead**: Use optimization recommendations
4. **Document decisions**: Keep notes on tax strategies
5. **Consult professionals**: Verify with tax advisors

## Security and Compliance

### Data Protection
- User data isolation and access controls
- Encrypted storage of sensitive financial data
- Audit trails for all tax calculations
- Secure API endpoints with authentication

### Tax Compliance
- Accurate wash sale rule implementation
- Proper short-term vs long-term classification
- Correct dividend type handling
- Standard tax lot accounting methods (FIFO)

## Performance Optimization

### Database Optimization
- Strategic indexing for tax queries
- Efficient bulk processing operations
- Optimized tax lot management
- Cached calculation results

### Calculation Efficiency
- Batch processing for large datasets
- Incremental tax calculations
- Memory-efficient algorithms
- Progress tracking for long operations

## Troubleshooting

### Common Issues

1. **Missing tax lots**: Ensure buy transactions are processed first
2. **Incorrect gains/losses**: Verify transaction data accuracy
3. **Wash sale detection**: Check for related asset purchases
4. **Performance issues**: Use pagination for large datasets

### Debug Commands

```bash
# Verify tax calculations
python manage.py calculate_taxes --user admin --dry-run --verbose

# Check for data inconsistencies
python manage.py shell
>>> from personal_finance.tax.models import TaxLot
>>> lots = TaxLot.objects.filter(remaining_quantity__lt=0)
>>> print(f"Invalid lots: {lots.count()}")

# Review tax lot assignments
>>> from django.db.models import Sum
>>> summary = TaxLot.objects.aggregate(
...     total_cost=Sum('total_cost_basis'),
...     total_remaining=Sum('remaining_quantity')
... )
>>> print(summary)
```

## Integration Examples

### Automated Tax Processing

Set up automated tax processing with periodic tasks:

```python
# In celery tasks
from celery import shared_task

@shared_task
def process_daily_tax_calculations():
    """Process tax calculations for recent transactions."""
    from personal_finance.tax.services import TaxCalculationService
    
    tax_service = TaxCalculationService()
    # Process recent transactions
    # Generate reports if month-end
    # Send notifications for opportunities
```

### Custom Tax Strategies

Extend the system with custom tax strategies:

```python
from personal_finance.tax.services import TaxOptimizationService

class CustomTaxOptimizationService(TaxOptimizationService):
    def generate_custom_recommendations(self, user, portfolio):
        """Generate custom tax recommendations."""
        recommendations = []
        
        # Implement custom logic
        # Add to recommendations list
        
        return recommendations
```

This comprehensive tax reporting and optimization system provides all the tools needed for sophisticated tax management within the personal finance platform!