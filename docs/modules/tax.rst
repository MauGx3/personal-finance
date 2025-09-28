Tax Reporting and Optimization
==============================

Comprehensive tax reporting and optimization reference for developers and system administrators.

.. currentmodule:: personal_finance.tax

.. contents:: Table of Contents
   :local:
   :depth: 3

Module Overview
---------------

The Tax module provides comprehensive tools for tax calculation, optimization, and reporting:

.. toctree::
   :maxdepth: 2

   Models <models/tax>
   Services <services/tax>
   APIs <api/tax>
   Tasks <tasks/tax>

Core Features
~~~~~~~~~~~~~

- **Tax Calculation Engine**: Automated capital gains/losses and dividend income processing
- **Tax Loss Harvesting**: Opportunity identification and optimization strategies
- **Tax Optimization**: Personalized recommendations for tax-efficient strategies
- **Tax Reporting**: Generation of tax forms and comprehensive reports
- **Wash Sale Detection**: Automatic detection and compliance with wash sale rules
- **Tax Lot Tracking**: Precise cost basis tracking with multiple accounting methods

Tax Calculation Engine
----------------------

Core Calculation Services
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.tax.services.TaxCalculationService
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: calculate_capital_gains_losses
   .. automethod:: calculate_dividend_income
   .. automethod:: process_tax_implications

Capital Gains and Losses
~~~~~~~~~~~~~~~~~~~~~~~~~

The platform calculates capital gains and losses with precision:

**Short-term vs Long-term Classification**
   Positions held for ≤365 days are classified as short-term, >365 days as long-term.

**Cost Basis Methods**
   - FIFO (First In, First Out) - Default
   - LIFO (Last In, First Out) - Optional
   - Specific Identification - Manual selection

**Example: Capital Gains Calculation**

.. code-block:: python

   from personal_finance.tax.services import TaxCalculationService
   from personal_finance.tax.models import TaxYear
   from decimal import Decimal

   # Initialize service
   tax_service = TaxCalculationService()
   tax_year = TaxYear.objects.get(year=2024)
   user = request.user

   # Calculate comprehensive capital gains/losses
   results = tax_service.calculate_capital_gains_losses(user, tax_year)

   print(f\"Short-term gains: ${results['short_term']['gains']}\")
   print(f\"Short-term losses: ${results['short_term']['losses']}\")
   print(f\"Long-term gains: ${results['long_term']['gains']}\")
   print(f\"Long-term losses: ${results['long_term']['losses']}\")
   print(f\"Net capital gain/loss: ${results['totals']['net_capital_gain_loss']}\")

   # Access detailed transaction data
   for transaction in results['detailed_transactions']:
       print(f\"{transaction['symbol']}: {transaction['gain_loss']} ({transaction['term']})\")

Dividend Income Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~

The system classifies and tracks dividend income:

**Dividend Types**
   - **Qualified Dividends**: Eligible for capital gains tax rates
   - **Ordinary Dividends**: Taxed at ordinary income rates
   - **Return of Capital**: Reduces cost basis, not taxable until basis is zero

.. code-block:: python

   # Calculate dividend income for tax year
   dividends = tax_service.calculate_dividend_income(user, tax_year)

   print(f\"Qualified dividends: ${dividends['qualified_dividends']}\")
   print(f\"Ordinary dividends: ${dividends['ordinary_dividends']}\")
   print(f\"Return of capital: ${dividends['return_of_capital']}\")
   print(f\"Total dividend income: ${dividends['total_dividend_income']}\")

   # Generate 1099-DIV equivalent data
   form_1099_data = tax_service.generate_1099_div_data(user, tax_year)
   for payer, amounts in form_1099_data.items():
       print(f\"{payer}: Qualified ${amounts['qualified']}, Ordinary ${amounts['ordinary']}\")

Tax Lot Management
~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.tax.models.TaxLot
   :members:
   :undoc-members:
   :show-inheritance:

Tax lots provide precise cost basis tracking:

.. code-block:: python

   from personal_finance.tax.models import TaxLot
   from django.db.models import Sum

   # View tax lots for a position
   position = user.portfolios.first().positions.filter(asset__symbol='AAPL').first()
   tax_lots = TaxLot.objects.filter(position=position, remaining_quantity__gt=0)

   for lot in tax_lots:
       print(f\"Acquired: {lot.acquisition_date}\")
       print(f\"Quantity: {lot.remaining_quantity} @ ${lot.price_per_share}\")
       print(f\"Cost basis: ${lot.remaining_cost_basis}\")
       print(f\"Days held: {lot.days_held}\")
       print(f\"Term: {'Long' if lot.is_long_term else 'Short'}\")
       print(\"-\" * 40)

   # Aggregate lot information
   summary = tax_lots.aggregate(
       total_quantity=Sum('remaining_quantity'),
       total_cost_basis=Sum('remaining_cost_basis')
   )
   print(f\"Total position: {summary['total_quantity']} shares, ${summary['total_cost_basis']} basis\")

Tax Loss Harvesting
-------------------

Loss Harvesting Service
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.tax.services.TaxLossHarvestingService
   :members:
   :undoc-members:
   :show-inheritance:

The platform identifies tax loss harvesting opportunities automatically:

.. code-block:: python

   from personal_finance.tax.services import TaxLossHarvestingService
   from decimal import Decimal

   # Initialize service
   loss_service = TaxLossHarvestingService()

   # Identify opportunities with minimum loss threshold
   opportunities = loss_service.identify_loss_harvesting_opportunities(
       user=user,
       minimum_loss_threshold=Decimal('250.00'),
       generate_recommendations=True
   )

   print(f\"Found {len(opportunities)} loss harvesting opportunities\")

   for opp in opportunities:
       print(f\"\\n{opp.position.asset.symbol} - {opp.position.asset.name}\")
       print(f\"  Current value: ${opp.current_market_value}\")
       print(f\"  Cost basis: ${opp.cost_basis}\")
       print(f\"  Unrealized loss: ${opp.potential_loss_amount}\")
       print(f\"  Tax benefit estimate: ${opp.tax_benefit_estimate}\")
       print(f\"  Status: {opp.get_status_display()}\")

       # Show wash sale considerations
       if opp.wash_sale_risk:
           print(f\"  ⚠️  Wash sale risk: {opp.wash_sale_notes}\")

       # Display recommendations
       if hasattr(opp, 'recommendations'):
           for rec in opp.recommendations.all():
               print(f\"  💡 {rec.recommendation_text}\")

Wash Sale Detection
~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.tax.models.WashSaleRule
   :members:
   :undoc-members:

The system automatically detects and handles wash sales:

.. code-block:: python

   from personal_finance.tax.services import WashSaleDetectionService

   wash_service = WashSaleDetectionService()

   # Check for wash sales on a specific transaction
   sale_transaction = user.transactions.filter(
       transaction_type='sell',
       asset__symbol='MSFT'
   ).first()

   wash_sale_info = wash_service.check_wash_sale(sale_transaction)

   if wash_sale_info['is_wash_sale']:
       print(f\"🚨 Wash sale detected for {sale_transaction.asset.symbol}\")
       print(f\"Sale date: {sale_transaction.date}\")
       print(f\"Loss amount: ${wash_sale_info['disallowed_loss']}\")
       print(f\"Repurchase date: {wash_sale_info['repurchase_date']}\")
       print(f\"Adjusted basis: ${wash_sale_info['adjusted_basis']}\")
   else:
       print(f\"✅ No wash sale issues for {sale_transaction.asset.symbol}\")

   # Bulk wash sale analysis
   all_wash_sales = wash_service.analyze_portfolio_wash_sales(
       user,
       tax_year=tax_year
   )

   print(f\"\\nTotal wash sales identified: {len(all_wash_sales)}\")
   total_disallowed = sum(ws['disallowed_loss'] for ws in all_wash_sales)
   print(f\"Total disallowed losses: ${total_disallowed}\")

Tax Optimization
----------------

Optimization Service
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.tax.services.TaxOptimizationService
   :members:
   :undoc-members:

The platform provides personalized tax optimization recommendations:

.. code-block:: python

   from personal_finance.tax.services import TaxOptimizationService

   optimization_service = TaxOptimizationService()

   # Generate comprehensive tax optimization recommendations
   recommendations = optimization_service.generate_tax_optimization_recommendations(
       user=user,
       tax_year=tax_year,
       include_asset_location=True,
       include_rebalancing=True,
       include_holding_period=True
   )

   print(f\"Generated {len(recommendations)} tax optimization recommendations\")

   for rec in recommendations:
       print(f\"\\n📋 {rec.title}\")
       print(f\"   Priority: {rec.get_priority_display()}\")
       print(f\"   Category: {rec.get_category_display()}\")
       print(f\"   Estimated tax savings: ${rec.estimated_tax_savings}\")
       print(f\"   Implementation effort: {rec.get_implementation_effort_display()}\")

       if rec.deadline:
           print(f\"   ⏰ Deadline: {rec.deadline}\")

       print(f\"   📝 Description: {rec.description}\")

       if rec.implementation_steps:
           print(f\"   🔧 Steps: {rec.implementation_steps}\")

Asset Location Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optimize asset placement across account types:

.. code-block:: python

   # Analyze asset location efficiency
   asset_location_analysis = optimization_service.analyze_asset_location(user)

   print(\"Asset Location Analysis:\")
   print(f\"Current tax efficiency score: {asset_location_analysis['efficiency_score']}/100\")

   for account_type, recommendations in asset_location_analysis['recommendations'].items():
       print(f\"\\n{account_type.upper()} Account Recommendations:\")
       for rec in recommendations:
           print(f\"  • {rec['action']}: {rec['asset_class']}\")
           print(f\"    Reason: {rec['reason']}\")
           print(f\"    Estimated annual savings: ${rec['estimated_savings']}\")

Tax Report Generation
---------------------

Report Service
~~~~~~~~~~~~~~

.. autoclass:: personal_finance.tax.report_service.TaxReportService
   :members:
   :undoc-members:

Generate comprehensive tax reports and forms:

.. code-block:: python

   from personal_finance.tax.report_service import TaxReportService

   report_service = TaxReportService()

   # Generate all tax reports for the year
   reports = report_service.generate_all_tax_reports(user, tax_year)

   print(\"Generated Tax Reports:\")
   for report_type, report in reports.items():
       print(f\"\\n📄 {report.get_report_type_display()}\")
       print(f\"   Generated: {report.generated_at}\")
       print(f\"   Status: {report.get_status_display()}\")
       if report.file_path:
           print(f\"   File: {report.file_path}\")

Schedule D Generation
~~~~~~~~~~~~~~~~~~~~~

Generate IRS Schedule D (Capital Gains and Losses):

.. code-block:: python

   # Generate detailed Schedule D
   schedule_d = report_service.generate_schedule_d_report(user, tax_year)

   print(\"📋 IRS Schedule D - Capital Gains and Losses\")
   print(f\"Tax Year: {schedule_d.tax_year.year}\")
   print(f\"Generated: {schedule_d.generated_at}\")

   # Short-term capital gains/losses
   print(f\"\\nShort-term capital gains: ${schedule_d.short_term_gains}\")
   print(f\"Short-term capital losses: ${schedule_d.short_term_losses}\")
   print(f\"Net short-term gain/loss: ${schedule_d.net_short_term}\")

   # Long-term capital gains/losses
   print(f\"\\nLong-term capital gains: ${schedule_d.long_term_gains}\")
   print(f\"Long-term capital losses: ${schedule_d.long_term_losses}\")
   print(f\"Net long-term gain/loss: ${schedule_d.net_long_term}\")

   # Combined totals
   print(f\"\\nNet capital gain/loss: ${schedule_d.net_capital_gain_loss}\")

   # Carryover information
   if schedule_d.loss_carryover_from_previous_year:
       print(f\"Loss carryover from prior year: ${schedule_d.loss_carryover_from_previous_year}\")

   if schedule_d.loss_carryover_to_next_year:
       print(f\"Loss carryover to next year: ${schedule_d.loss_carryover_to_next_year}\")

Form 1099-DIV Generation
~~~~~~~~~~~~~~~~~~~~~~~~

Generate dividend income reports:

.. code-block:: python

   # Generate 1099-DIV equivalent reports
   dividend_reports = report_service.generate_1099_div_reports(user, tax_year)

   print(\"📄 Dividend Income Reports (1099-DIV Equivalent)\")

   for payer, report in dividend_reports.items():
       print(f\"\\nPayer: {payer}\")
       print(f\"  Qualified dividends: ${report['qualified_dividends']}\")
       print(f\"  Ordinary dividends: ${report['ordinary_dividends']}\")
       if report['return_of_capital'] > 0:
           print(f\"  Return of capital: ${report['return_of_capital']}\")
       if report['capital_gain_distributions'] > 0:
           print(f\"  Capital gain distributions: ${report['capital_gain_distributions']}\")

REST API Reference
------------------

Tax Analytics Endpoints
~~~~~~~~~~~~~~~~~~~~~~~

**Get Tax Summary**

.. http:get:: /api/v1/tax/analytics/summary/

   Retrieve comprehensive tax analytics summary.

   **Query Parameters:**

   - **year** (integer) -- Tax year (default: current year)
   - **portfolio_id** (integer) -- Specific portfolio ID (optional)
   - **include_projections** (boolean) -- Include year-end projections

   **Example Request:**

   .. code-block:: http

      GET /api/v1/tax/analytics/summary/?year=2024&portfolio_id=1 HTTP/1.1
      Authorization: Token your-api-token

   **Example Response:**

   .. code-block:: json

      {
        \"tax_year\": 2024,
        \"portfolio_id\": 1,
        \"capital_gains_losses\": {
          \"short_term\": {
            \"gains\": \"5250.00\",
            \"losses\": \"-1200.00\",
            \"net\": \"4050.00\"
          },
          \"long_term\": {
            \"gains\": \"8900.00\",
            \"losses\": \"-750.00\",
            \"net\": \"8150.00\"
          },
          \"total_net\": \"12200.00\"
        },
        \"dividend_income\": {
          \"qualified\": \"2100.00\",
          \"ordinary\": \"350.00\",
          \"return_of_capital\": \"50.00\",
          \"total\": \"2500.00\"
        },
        \"tax_implications\": {
          \"estimated_tax_owed\": \"3845.00\",
          \"effective_tax_rate\": \"0.261\"
        },
        \"loss_harvesting_opportunities\": 3,
        \"wash_sale_violations\": 0,
        \"year_end_projections\": {
          \"projected_net_gains\": \"15000.00\",
          \"recommended_actions\": [
            \"Consider realizing losses before year-end\",
            \"Review asset location optimization\"
          ]
        }
      }

**Trigger Tax Calculations**

.. http:post:: /api/v1/tax/analytics/calculate/

   Trigger comprehensive tax calculations for user.

   **Request Body:**

   .. code-block:: json

      {
        \"year\": 2024,
        \"portfolio_id\": 1,
        \"reprocess\": false,
        \"include_projections\": true
      }

Loss Harvesting Endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~

**List Loss Harvesting Opportunities**

.. http:get:: /api/v1/tax/loss-harvesting/

   List current tax loss harvesting opportunities.

   **Query Parameters:**

   - **minimum_loss** (decimal) -- Minimum loss amount to include
   - **status** (string) -- Filter by status: ``identified``, ``recommended``, ``implemented``

**Analyze New Opportunities**

.. http:post:: /api/v1/tax/loss-harvesting/analyze/

   Analyze portfolio for new loss harvesting opportunities.

   **Request Body:**

   .. code-block:: json

      {
        \"minimum_loss_threshold\": \"250.00\",
        \"generate_recommendations\": true,
        \"exclude_wash_sale_risks\": true
      }

Tax Reports Endpoints
~~~~~~~~~~~~~~~~~~~~

**List Generated Reports**

.. http:get:: /api/v1/tax/reports/

   List all generated tax reports for user.

**Generate New Reports**

.. http:post:: /api/v1/tax/reports/generate/

   Generate comprehensive tax reports.

   **Request Body:**

   .. code-block:: json

      {
        \"year\": 2024,
        \"report_types\": [\"schedule_d\", \"form_1099_div\", \"tax_summary\"],
        \"format\": \"pdf\",
        \"email_when_complete\": true
      }

Tax Data Views
~~~~~~~~~~~~~~

**Capital Gains/Losses**

.. http:get:: /api/v1/tax/capital-gains-losses/

   Detailed capital gains and losses data.

   **Query Parameters:**

   - **tax_year** (integer) -- Tax year ID
   - **term** (string) -- Filter by term: ``short`` or ``long``
   - **asset_type** (string) -- Filter by asset type

**Dividend Income**

.. http:get:: /api/v1/tax/dividend-income/

   Detailed dividend income data.

   **Tax Lots**

.. http:get:: /api/v1/tax/tax-lots/

   Tax lot information for positions.

Management Commands
-------------------

Calculate Tax Implications
~~~~~~~~~~~~~~~~~~~~~~~~~~

Process transactions and calculate tax implications:

.. code-block:: bash

   # Calculate taxes for all users (current year)
   python manage.py calculate_taxes

   # Calculate for specific user and year
   python manage.py calculate_taxes --user admin --year 2024

   # Reprocess existing calculations (force recalculation)
   python manage.py calculate_taxes --user admin --year 2024 --reprocess

   # Process specific transaction
   python manage.py calculate_taxes --transaction-id 12345

   # Dry run to preview calculations without saving
   python manage.py calculate_taxes --user admin --dry-run --verbose

   # Process only recent transactions (performance optimization)
   python manage.py calculate_taxes --since-date 2024-01-01

**Command Options:**

+-------------------+------------------------------------------+
| Option            | Description                              |
+===================+==========================================+
| ``--user``        | Process taxes for specific user         |
+-------------------+------------------------------------------+
| ``--year``        | Process specific tax year                |
+-------------------+------------------------------------------+
| ``--reprocess``   | Force recalculation of existing data    |
+-------------------+------------------------------------------+
| ``--transaction-id`` | Process specific transaction only     |
+-------------------+------------------------------------------+
| ``--dry-run``     | Preview calculations without saving      |
+-------------------+------------------------------------------+
| ``--verbose``     | Enable detailed output                   |
+-------------------+------------------------------------------+
| ``--since-date``  | Only process transactions since date    |
+-------------------+------------------------------------------+

Identify Loss Harvesting
~~~~~~~~~~~~~~~~~~~~~~~~

Find and analyze tax loss harvesting opportunities:

.. code-block:: bash

   # Analyze all users for current year
   python manage.py identify_loss_harvesting

   # Analyze specific user
   python manage.py identify_loss_harvesting --user admin

   # Set minimum loss threshold ($500)
   python manage.py identify_loss_harvesting --minimum-loss 500

   # Generate actionable recommendations
   python manage.py identify_loss_harvesting --generate-recommendations

   # Exclude positions with wash sale risks
   python manage.py identify_loss_harvesting --exclude-wash-sales

   # Preview analysis without saving
   python manage.py identify_loss_harvesting --dry-run --verbose

Generate Tax Reports
~~~~~~~~~~~~~~~~~~~~

Create comprehensive tax reports and forms:

.. code-block:: bash

   # Generate all reports for all users (current tax year)
   python manage.py generate_tax_reports

   # Generate for specific user and year
   python manage.py generate_tax_reports --user admin --year 2024

   # Generate specific report type only
   python manage.py generate_tax_reports --report-type schedule_d

   # Save reports to custom directory
   python manage.py generate_tax_reports --output-dir /app/tax_reports/2024/

   # Generate in specific format
   python manage.py generate_tax_reports --format pdf --user admin

   # Email reports when complete
   python manage.py generate_tax_reports --email-reports --user admin

   # Preview what would be generated
   python manage.py generate_tax_reports --dry-run --verbose

**Report Types Available:**

- ``schedule_d`` - IRS Schedule D (Capital Gains and Losses)
- ``form_1099_div`` - Dividend Income Summary (1099-DIV equivalent)
- ``form_8949`` - Sales and Other Dispositions of Capital Assets
- ``tax_summary`` - Comprehensive annual tax summary
- ``loss_carryforward`` - Multi-year loss tracking
- ``all`` - Generate all available reports

Admin Interface
---------------

Tax Management Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~

The Django admin interface provides comprehensive tax management capabilities:

**Tax Years Administration**
   - Configure tax year settings and brackets
   - Set filing deadlines and thresholds
   - Manage long-term vs short-term rates

**Tax Lots Management**
   - View detailed tax lot information
   - Monitor cost basis tracking
   - Resolve tax lot inconsistencies

**Capital Gains/Losses Overview**
   - Color-coded displays for gains (green) and losses (red)
   - Advanced filtering by user, asset, date range
   - Bulk operations for tax lot adjustments

**Loss Harvesting Dashboard**
   - Monitor identified opportunities
   - Track implementation status
   - Analyze potential tax benefits

**Reports Administration**
   - Access all generated tax reports
   - Manage report templates and formats
   - Monitor generation status and errors

Advanced Features
-----------------

Custom Tax Strategies
~~~~~~~~~~~~~~~~~~~~~

Extend the system with custom tax optimization strategies:

.. code-block:: python

   from personal_finance.tax.services import TaxOptimizationService

   class CustomTaxOptimizationService(TaxOptimizationService):
       \"\"\"Custom tax optimization with advanced strategies.\"\"\"

       def generate_custom_recommendations(self, user, portfolio):
           \"\"\"Generate custom tax recommendations.\"\"\"
           recommendations = []

           # Example: Asset location optimization
           self._analyze_asset_location(user, portfolio, recommendations)

           # Example: Tax-loss harvesting with ETF substitution
           self._analyze_etf_substitution_opportunities(user, recommendations)

           # Example: Charitable giving optimization
           self._analyze_charitable_giving_opportunities(user, recommendations)

           return recommendations

       def _analyze_asset_location(self, user, portfolio, recommendations):
           \"\"\"Analyze optimal asset placement across account types.\"\"\"
           taxable_accounts = portfolio.accounts.filter(account_type='taxable')
           ira_accounts = portfolio.accounts.filter(account_type='traditional_ira')
           roth_accounts = portfolio.accounts.filter(account_type='roth_ira')

           # Analyze bond placement in tax-advantaged accounts
           # Analyze REIT placement optimization
           # Analyze international fund tax efficiency

       def _analyze_etf_substitution_opportunities(self, user, recommendations):
           \"\"\"Find ETF substitution opportunities for tax loss harvesting.\"\"\"
           # Identify similar ETFs for wash sale avoidance
           # Calculate correlation coefficients
           # Suggest temporary substitutions

Automated Tax Processing
~~~~~~~~~~~~~~~~~~~~~~~~

Set up automated tax processing with Celery:

.. code-block:: python

   from celery import shared_task
   from personal_finance.tax.services import TaxCalculationService, TaxLossHarvestingService

   @shared_task
   def process_daily_tax_calculations():
       \"\"\"Process tax calculations for recent transactions.\"\"\"
       from django.contrib.auth.models import User
       from datetime import date, timedelta

       tax_service = TaxCalculationService()

       # Process recent transactions for all users
       yesterday = date.today() - timedelta(days=1)

       for user in User.objects.filter(is_active=True):
           try:
               tax_service.process_recent_transactions(user, since_date=yesterday)
           except Exception as e:
               logger.error(f\"Tax calculation failed for user {user.id}: {e}\")

   @shared_task
   def weekly_loss_harvesting_analysis():
       \"\"\"Weekly analysis of loss harvesting opportunities.\"\"\"
       from django.contrib.auth.models import User

       loss_service = TaxLossHarvestingService()

       for user in User.objects.filter(is_active=True):
           opportunities = loss_service.identify_loss_harvesting_opportunities(
               user, minimum_loss_threshold=Decimal('100')
           )

           # Send notifications if significant opportunities found
           if opportunities and sum(opp.potential_loss_amount for opp in opportunities) > 500:
               send_loss_harvesting_notification.delay(user.id, len(opportunities))

   @shared_task
   def monthly_tax_reports():
       \"\"\"Generate monthly tax reports.\"\"\"
       from personal_finance.tax.report_service import TaxReportService

       report_service = TaxReportService()

       for user in User.objects.filter(is_active=True):
           # Generate year-to-date tax summary
           report_service.generate_ytd_tax_summary(user)

Performance Optimization
------------------------

Database Optimization
~~~~~~~~~~~~~~~~~~~~~

The tax module includes several database optimizations:

**Strategic Indexing**

.. code-block:: python

   # Key database indexes for tax calculations
   class TaxLot(models.Model):
       class Meta:
           indexes = [
               models.Index(fields=['position', 'acquisition_date']),  # FIFO processing
               models.Index(fields=['position', 'remaining_quantity']),  # Active lots
               models.Index(fields=['acquisition_date', 'is_long_term']),  # Term classification
           ]

   class CapitalGainsLoss(models.Model):
       class Meta:
           indexes = [
               models.Index(fields=['tax_year', 'user']),  # User tax calculations
               models.Index(fields=['transaction_date', 'term']),  # Date-based queries
               models.Index(fields=['asset', 'tax_year']),  # Asset-specific analysis
           ]

**Efficient Bulk Processing**

.. code-block:: python

   def bulk_calculate_capital_gains(transactions):
       \"\"\"Efficiently process large numbers of transactions.\"\"\"
       from django.db import transaction

       with transaction.atomic():
           # Batch process transactions in chunks
           chunk_size = 1000
           for i in range(0, len(transactions), chunk_size):
               chunk = transactions[i:i + chunk_size]

               # Bulk create/update tax implications
               tax_implications = []
               for txn in chunk:
                   implication = calculate_single_transaction_tax(txn)
                   tax_implications.append(implication)

               CapitalGainsLoss.objects.bulk_create(
                   tax_implications,
                   batch_size=chunk_size,
                   update_conflicts=True,
                   update_fields=['gain_loss_amount', 'cost_basis', 'proceeds']
               )

Memory Optimization
~~~~~~~~~~~~~~~~~~~

Handle large datasets efficiently:

.. code-block:: python

   def memory_efficient_tax_calculation(user, tax_year):
       \"\"\"Process tax calculations with memory efficiency.\"\"\"
       from django.db.models import Prefetch

       # Use select_related and prefetch_related strategically
       transactions = user.transactions.filter(
           date__year=tax_year.year
       ).select_related(
           'asset', 'portfolio'
       ).prefetch_related(
           Prefetch('tax_lots', queryset=TaxLot.objects.select_related('position'))
       ).order_by('date')

       # Process in batches to manage memory usage
       batch_size = 500
       for batch in batch_queryset(transactions, batch_size):
           process_transaction_batch(batch)

Security and Compliance
-----------------------

Data Protection
~~~~~~~~~~~~~~~

Tax data requires special security considerations:

.. code-block:: python

   from personal_finance.core.fields import EncryptedDecimalField

   class TaxLot(models.Model):
       \"\"\"Tax lot with encrypted sensitive fields.\"\"\"

       # Encrypt cost basis information
       total_cost_basis = EncryptedDecimalField(max_digits=15, decimal_places=2)
       remaining_cost_basis = EncryptedDecimalField(max_digits=15, decimal_places=2)

       class Meta:
           # Audit trail for tax data changes
           permissions = [
               ('view_tax_details', 'Can view detailed tax information'),
               ('modify_tax_lots', 'Can modify tax lot assignments'),
           ]

Audit Trails
~~~~~~~~~~~~

Comprehensive audit logging for tax calculations:

.. code-block:: python

   import logging
   from django.db.models.signals import post_save, pre_delete

   tax_audit_logger = logging.getLogger('personal_finance.tax.audit')

   @receiver(post_save, sender=CapitalGainsLoss)
   def log_capital_gains_calculation(sender, instance, created, **kwargs):
       \"\"\"Audit capital gains calculations.\"\"\"
       action = 'CREATED' if created else 'UPDATED'

       tax_audit_logger.info(
           f'Capital gains calculation {action}',
           extra={
               'user_id': instance.user.id,
               'transaction_id': instance.transaction.id,
               'asset_symbol': instance.asset.symbol,
               'gain_loss_amount': str(instance.gain_loss_amount),
               'tax_year': instance.tax_year.year,
               'action': action,
           }
       )

Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Missing Tax Lots**
   Tax lots must be created for all buy transactions before calculating gains/losses.

   .. code-block:: python

      # Diagnose missing tax lots
      from personal_finance.tax.models import TaxLot

      positions_without_lots = Position.objects.filter(
          quantity__gt=0,
          tax_lots__isnull=True
      )

      print(f\"Positions missing tax lots: {positions_without_lots.count()}\")

      # Create missing tax lots
      from personal_finance.tax.services import TaxCalculationService
      tax_service = TaxCalculationService()

      for position in positions_without_lots:
          tax_service.create_missing_tax_lots(position)

**Incorrect Gains/Losses**
   Verify transaction data accuracy and tax lot assignments.

   .. code-block:: bash

      # Debug specific calculation
      python manage.py calculate_taxes --user admin --transaction-id 12345 --dry-run --verbose

**Wash Sale Detection Issues**
   Ensure related asset purchases within 30-day window are properly identified.

   .. code-block:: python

      # Check wash sale detection
      from personal_finance.tax.services import WashSaleDetectionService

      wash_service = WashSaleDetectionService()

      # Analyze specific asset
      wash_sales = wash_service.find_potential_wash_sales(
          user, asset_symbol='AAPL'
      )

      for ws in wash_sales:
          print(f\"Sale: {ws['sale_date']}, Repurchase: {ws['repurchase_date']}\")

**Performance Issues with Large Datasets**
   Use pagination and batch processing for users with many transactions.

   .. code-block:: python

      # Process large datasets efficiently
      python manage.py calculate_taxes --user heavy_trader --batch-size 100 --verbose

Debug Commands and Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Verify Tax Calculations**

.. code-block:: python

   # Check calculation consistency
   from django.db.models import Sum
   from personal_finance.tax.models import CapitalGainsLoss

   # Verify total gains/losses match individual transactions
   user_gains = CapitalGainsLoss.objects.filter(
       user=user, tax_year__year=2024
   ).aggregate(
       total_gains=Sum('gain_loss_amount')
   )
   print(f\"Total gains/losses: ${user_gains['total_gains']}\")

**Check Tax Lot Consistency**

.. code-block:: python

   # Verify tax lot integrity
   from personal_finance.tax.models import TaxLot

   # Find negative remaining quantities (data issue)
   invalid_lots = TaxLot.objects.filter(remaining_quantity__lt=0)
   print(f\"Invalid tax lots found: {invalid_lots.count()}\")

   # Check for orphaned tax lots
   orphaned_lots = TaxLot.objects.filter(position__isnull=True)
   print(f\"Orphaned tax lots: {orphaned_lots.count()}\")

**Monitor Wash Sale Rules**

.. code-block:: python

   # Review wash sale violations
   from personal_finance.tax.models import WashSaleRule

   active_violations = WashSaleRule.objects.filter(
       is_active=True,
       end_date__gte=date.today()
   )

   for violation in active_violations:
       print(f\"Active wash sale: {violation.asset.symbol}\")
       print(f\"  Period: {violation.start_date} to {violation.end_date}\")
       print(f\"  Disallowed loss: ${violation.disallowed_loss_amount}\")

Integration Examples
--------------------

Third-party Tax Software Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export data for popular tax software:

.. code-block:: python

   from personal_finance.tax.exporters import TurboTaxExporter, TaxActExporter

   # Export for TurboTax
   turbotax_exporter = TurboTaxExporter()
   turbotax_file = turbotax_exporter.export_user_data(user, tax_year)

   # Export for TaxAct
   taxact_exporter = TaxActExporter()
   taxact_file = taxact_exporter.export_user_data(user, tax_year)

   print(f\"TurboTax export: {turbotax_file}\")
   print(f\"TaxAct export: {taxact_file}\")

Custom Reporting Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create custom tax reports with external libraries:

.. code-block:: python

   from reportlab.pdfgen import canvas
   from personal_finance.tax.report_service import TaxReportService

   def generate_custom_tax_summary(user, tax_year, output_path):
       \"\"\"Generate custom PDF tax summary.\"\"\"
       report_service = TaxReportService()

       # Get tax data
       summary_data = report_service.get_comprehensive_tax_summary(user, tax_year)

       # Create PDF
       c = canvas.Canvas(output_path, pagesize=(612, 792))

       # Add content
       c.drawString(100, 750, f\"Tax Summary for {tax_year.year}\")
       c.drawString(100, 720, f\"Total Capital Gains: ${summary_data['total_capital_gains']}\")
       c.drawString(100, 700, f\"Total Dividend Income: ${summary_data['total_dividends']}\")

       c.save()
       return output_path

Best Practices
--------------

For Developers
~~~~~~~~~~~~~~

1. **Use Decimal for Financial Calculations**
   Always use Python's Decimal type for precise financial calculations.

2. **Validate Wash Sale Rules**
   Check wash sale implications before processing any sale transactions.

3. **Maintain Tax Lot Integrity**
   Ensure tax lots are created for all purchases and properly consumed for sales.

4. **Implement Comprehensive Error Handling**
   Tax calculations can fail for various reasons; implement proper error handling.

5. **Regular Data Validation**
   Implement automated checks for tax data consistency and accuracy.

For System Administrators
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Monitor Performance**
   Tax calculations can be resource-intensive; monitor system performance during processing.

2. **Schedule Regular Processing**
   Set up automated tax calculation tasks for optimal user experience.

3. **Backup Tax Data**
   Implement comprehensive backup strategies for tax-related data.

4. **Security Monitoring**
   Monitor access to tax data and implement proper audit trails.

5. **Compliance Updates**
   Stay current with tax law changes and update system configurations accordingly.

For Users
~~~~~~~~~

1. **Keep Data Current**
   Ensure transaction data is accurate and up-to-date for proper tax calculations.

2. **Review Regularly**
   Regularly review tax implications and loss harvesting opportunities.

3. **Plan Ahead**
   Use tax optimization recommendations for strategic planning.

4. **Consult Professionals**
   Always verify tax strategies with qualified tax professionals.

5. **Document Decisions**
   Maintain records of tax-related decisions and implementations.

See Also
--------

* :doc:`../api/rest_endpoints` - Complete API reference including tax endpoints
* :doc:`../config/django_settings` - Tax-related configuration settings
* :doc:`../modules/portfolio` - Portfolio management integration
* :doc:`../architecture/overview` - System architecture and data flow
