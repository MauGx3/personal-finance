# Generated migration for tax app

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('portfolios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(help_text='Tax year (e.g., 2024)', unique=True)),
                ('filing_deadline', models.DateField(help_text='Tax filing deadline')),
                ('standard_deduction_single', models.DecimalField(decimal_places=2, help_text='Standard deduction for single filers', max_digits=10)),
                ('standard_deduction_married', models.DecimalField(decimal_places=2, help_text='Standard deduction for married filing jointly', max_digits=10)),
                ('long_term_capital_gains_thresholds', models.JSONField(default=dict, help_text='Long-term capital gains tax brackets')),
                ('short_term_capital_gains_rate', models.DecimalField(decimal_places=4, default='0.37', help_text='Short-term capital gains tax rate (ordinary income)', max_digits=5)),
            ],
            options={
                'ordering': ['-year'],
            },
        ),
        migrations.CreateModel(
            name='TaxLot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('purchase_date', models.DateField(help_text='Date of purchase')),
                ('quantity', models.DecimalField(decimal_places=8, help_text='Number of shares/units', max_digits=18)),
                ('cost_basis', models.DecimalField(decimal_places=2, help_text='Total cost including fees', max_digits=15)),
                ('cost_per_share', models.DecimalField(decimal_places=4, help_text='Cost per share/unit', max_digits=12)),
                ('fees', models.DecimalField(decimal_places=2, default='0.00', help_text='Transaction fees', max_digits=10)),
                ('lot_id', models.CharField(blank=True, help_text='Unique identifier for this lot', max_length=100)),
                ('is_wash_sale', models.BooleanField(default=False, help_text='Is this lot affected by wash sale rules')),
                ('wash_sale_loss_deferred', models.DecimalField(blank=True, decimal_places=2, help_text='Deferred loss amount due to wash sale', max_digits=15, null=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes or comments')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['purchase_date', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='CapitalGainLoss',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sale_date', models.DateField(help_text='Date of sale')),
                ('quantity_sold', models.DecimalField(decimal_places=8, help_text='Number of shares/units sold', max_digits=18)),
                ('sale_price_per_share', models.DecimalField(decimal_places=4, help_text='Sale price per share/unit', max_digits=12)),
                ('total_sale_proceeds', models.DecimalField(decimal_places=2, help_text='Total proceeds from sale', max_digits=15)),
                ('total_cost_basis', models.DecimalField(decimal_places=2, help_text='Total cost basis of sold shares', max_digits=15)),
                ('gain_loss_amount', models.DecimalField(decimal_places=2, help_text='Capital gain/loss amount', max_digits=15)),
                ('gain_loss_type', models.CharField(choices=[('SHORT_TERM', 'Short-term (≤1 year)'), ('LONG_TERM', 'Long-term (>1 year)')], help_text='Type based on holding period', max_length=20)),
                ('holding_period_days', models.IntegerField(help_text='Number of days held')),
                ('sale_fees', models.DecimalField(decimal_places=2, default='0.00', help_text='Fees associated with the sale', max_digits=10)),
                ('is_wash_sale', models.BooleanField(default=False, help_text='Is this sale affected by wash sale rules')),
                ('wash_sale_loss_deferred', models.DecimalField(blank=True, decimal_places=2, help_text='Loss amount deferred due to wash sale', max_digits=15, null=True)),
                ('tax_year', models.ForeignKey(help_text='Tax year this gain/loss applies to', on_delete=django.db.models.deletion.CASCADE, to='tax.taxyear')),
                ('tax_lot', models.ForeignKey(help_text='Tax lot this gain/loss comes from', on_delete=django.db.models.deletion.CASCADE, to='tax.taxlot')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-sale_date'],
            },
        ),
        migrations.CreateModel(
            name='DividendIncome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payment_date', models.DateField(help_text='Date dividend was paid')),
                ('ex_dividend_date', models.DateField(help_text='Ex-dividend date')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Dividend amount received', max_digits=15)),
                ('dividend_type', models.CharField(choices=[('QUALIFIED', 'Qualified dividend'), ('ORDINARY', 'Ordinary dividend'), ('RETURN_OF_CAPITAL', 'Return of capital'), ('CAPITAL_GAIN', 'Capital gain distribution')], help_text='Type of dividend for tax purposes', max_length=20)),
                ('shares_held', models.DecimalField(decimal_places=8, help_text='Number of shares held on record date', max_digits=18)),
                ('dividend_per_share', models.DecimalField(decimal_places=4, help_text='Dividend amount per share', max_digits=12)),
                ('reinvested', models.BooleanField(default=False, help_text='Was dividend reinvested')),
                ('withholding_tax', models.DecimalField(blank=True, decimal_places=2, help_text='Tax withheld (for foreign dividends)', max_digits=10, null=True)),
                ('tax_year', models.ForeignKey(help_text='Tax year this dividend applies to', on_delete=django.db.models.deletion.CASCADE, to='tax.taxyear')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-payment_date'],
            },
        ),
        migrations.CreateModel(
            name='TaxLossHarvestingOpportunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('identified_date', models.DateField(auto_now_add=True, help_text='Date opportunity was identified')),
                ('unrealized_loss', models.DecimalField(decimal_places=2, help_text='Unrealized loss amount', max_digits=15)),
                ('current_value', models.DecimalField(decimal_places=2, help_text='Current market value', max_digits=15)),
                ('cost_basis', models.DecimalField(decimal_places=2, help_text='Original cost basis', max_digits=15)),
                ('potential_tax_savings', models.DecimalField(decimal_places=2, help_text='Estimated tax savings', max_digits=10)),
                ('days_until_wash_sale_safe', models.IntegerField(help_text='Days until wash sale rule expires')),
                ('recommendation', models.TextField(help_text='Harvesting recommendation')),
                ('status', models.CharField(choices=[('IDENTIFIED', 'Identified'), ('RECOMMENDED', 'Recommended for harvest'), ('EXECUTED', 'Harvested'), ('EXPIRED', 'Opportunity expired'), ('DECLINED', 'Declined to harvest')], default='IDENTIFIED', help_text='Current status of opportunity', max_length=20)),
                ('executed_date', models.DateField(blank=True, help_text='Date opportunity was executed', null=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes')),
                ('tax_lot', models.ForeignKey(help_text='Tax lot with harvesting opportunity', on_delete=django.db.models.deletion.CASCADE, to='tax.taxlot')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-identified_date'],
            },
        ),
        migrations.CreateModel(
            name='TaxOptimizationRecommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('recommendation_type', models.CharField(choices=[('TAX_LOSS_HARVEST', 'Tax loss harvesting'), ('GAIN_REALIZATION', 'Realize long-term gains'), ('ASSET_LOCATION', 'Optimize asset location'), ('REBALANCING', 'Tax-efficient rebalancing'), ('ROTH_CONVERSION', 'Roth conversion opportunity'), ('CHARITABLE_GIVING', 'Charitable giving strategy'), ('TIMING', 'Optimize timing of transactions')], help_text='Type of optimization recommendation', max_length=30)),
                ('priority', models.CharField(choices=[('HIGH', 'High priority'), ('MEDIUM', 'Medium priority'), ('LOW', 'Low priority')], default='MEDIUM', help_text='Priority level of recommendation', max_length=10)),
                ('description', models.TextField(help_text='Detailed description of recommendation')),
                ('potential_savings', models.DecimalField(blank=True, decimal_places=2, help_text='Estimated tax savings', max_digits=15, null=True)),
                ('action_required', models.TextField(help_text='Specific actions to implement recommendation')),
                ('deadline', models.DateField(blank=True, help_text='Deadline to implement (if applicable)', null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending review'), ('ACCEPTED', 'Accepted'), ('IMPLEMENTED', 'Implemented'), ('DECLINED', 'Declined'), ('EXPIRED', 'Expired')], default='PENDING', help_text='Current status', max_length=20)),
                ('implemented_date', models.DateField(blank=True, help_text='Date recommendation was implemented', null=True)),
                ('notes', models.TextField(blank=True, help_text='Additional notes or comments')),
                ('tax_year', models.ForeignKey(help_text='Tax year this recommendation applies to', on_delete=django.db.models.deletion.CASCADE, to='tax.taxyear')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TaxReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('report_type', models.CharField(choices=[('ANNUAL_SUMMARY', 'Annual tax summary'), ('CAPITAL_GAINS', 'Capital gains/losses report'), ('DIVIDEND_INCOME', 'Dividend income report'), ('TAX_LOSS_HARVEST', 'Tax loss harvesting report'), ('FORM_8949', 'Form 8949 data'), ('SCHEDULE_D', 'Schedule D data'), ('FORM_1099_DIV', 'Form 1099-DIV data')], help_text='Type of tax report', max_length=20)),
                ('file_path', models.CharField(blank=True, help_text='Path to generated report file', max_length=500)),
                ('file_format', models.CharField(choices=[('PDF', 'PDF document'), ('CSV', 'CSV file'), ('XLSX', 'Excel file'), ('JSON', 'JSON data')], default='PDF', help_text='Format of generated report', max_length=10)),
                ('report_data', models.JSONField(default=dict, help_text='Raw report data')),
                ('summary_statistics', models.JSONField(default=dict, help_text='Summary statistics for the report')),
                ('generation_parameters', models.JSONField(default=dict, help_text='Parameters used to generate report')),
                ('is_final', models.BooleanField(default=False, help_text='Is this the final version for filing')),
                ('notes', models.TextField(blank=True, help_text='Additional notes about the report')),
                ('tax_year', models.ForeignKey(help_text='Tax year for this report', on_delete=django.db.models.deletion.CASCADE, to='tax.taxyear')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]