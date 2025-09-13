"""Tax reporting and optimization models."""

from decimal import Decimal
from typing import Dict, List, Any

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

try:
    from personal_finance.portfolios.models import Portfolio, Position, Transaction
except ImportError:
    import warnings
    warnings.warn(
        "Could not import Portfolio, Position, or Transaction from personal_finance.portfolios.models. "
        "Some tax models may not function correctly if portfolios app is missing."
    )
    Portfolio = None
    Position = None
    Transaction = None

User = get_user_model()


class TaxYear(models.Model):
    """Tax year configuration and settings.
    
    Stores tax year specific information including rates, brackets,
    and deadlines for accurate tax calculations.
    """
    
    year = models.IntegerField(unique=True, help_text="Tax year (e.g., 2024)")
    filing_deadline = models.DateField(help_text="Tax filing deadline")
    standard_deduction_single = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Standard deduction for single filers"
    )
    standard_deduction_married = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Standard deduction for married filing jointly"
    )
    long_term_capital_gains_thresholds = models.JSONField(
        default=dict,
        help_text="Long-term capital gains tax brackets"
    )
    short_term_capital_gains_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.37'),
        help_text="Short-term capital gains tax rate (ordinary income)"
    )
    
    class Meta:
        ordering = ['-year']
        
    def __str__(self) -> str:
        return f"Tax Year {self.year}"


class TaxLot(models.Model):
    """Individual tax lot for position tracking.
    
    Represents a specific purchase of shares with acquisition date,
    cost basis, and remaining quantity for accurate tax calculations.
    """
    
    position = models.ForeignKey(
        'portfolios.Position', on_delete=models.CASCADE, related_name='tax_lots'
    )
    acquisition_date = models.DateField(help_text="Date shares were acquired")
    original_quantity = models.DecimalField(
        max_digits=15, decimal_places=6,
        help_text="Original quantity purchased"
    )
    remaining_quantity = models.DecimalField(
        max_digits=15, decimal_places=6,
        help_text="Remaining quantity not yet sold"
    )
    cost_basis_per_share = models.DecimalField(
        max_digits=15, decimal_places=6,
        help_text="Cost basis per share including fees"
    )
    total_cost_basis = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Total cost basis for this lot"
    )
    transaction = models.ForeignKey(
        'portfolios.Transaction', on_delete=models.CASCADE,
        help_text="Transaction that created this tax lot"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['acquisition_date', 'id']  # FIFO by default
        indexes = [
            models.Index(fields=['position', 'acquisition_date']),
            models.Index(fields=['remaining_quantity']),
        ]
        
    def __str__(self) -> str:
        return f"{self.position.asset.symbol} - {self.remaining_quantity} shares @ ${self.cost_basis_per_share}"
    
    @property
    def is_long_term(self) -> bool:
        """Check if this lot qualifies for long-term capital gains.
        
        Returns:
            bool: True if held for more than 1 year
        """
        holding_period = timezone.now().date() - self.acquisition_date
        return holding_period.days > 365
    
    @property
    def current_value(self) -> Decimal:
        """Calculate current market value of remaining shares.
        
        Returns:
            Decimal: Current market value
        """
        if self.position.asset.current_price:
            return self.remaining_quantity * self.position.asset.current_price
        return Decimal('0')
    
    @property
    def unrealized_gain_loss(self) -> Decimal:
        """Calculate unrealized gain/loss for remaining shares.
        
        Returns:
            Decimal: Unrealized gain (positive) or loss (negative)
        """
        return self.current_value - (self.remaining_quantity * self.cost_basis_per_share)


class CapitalGainLoss(models.Model):
    """Realized capital gains and losses for tax reporting.
    
    Records all realized gains/losses from asset sales with proper
    cost basis calculations and tax treatment determination.
    """
    
    TERM_CHOICES = [
        ('short', 'Short-term (≤ 1 year)'),
        ('long', 'Long-term (> 1 year)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE)
    position = models.ForeignKey('portfolios.Position', on_delete=models.CASCADE)
    transaction = models.ForeignKey(
        'portfolios.Transaction', on_delete=models.CASCADE,
        help_text="Sale transaction that realized the gain/loss"
    )
    tax_lot = models.ForeignKey(
        TaxLot, on_delete=models.CASCADE,
        help_text="Tax lot sold to realize gain/loss"
    )
    
    # Sale details
    sale_date = models.DateField(help_text="Date of sale")
    sale_price_per_share = models.DecimalField(
        max_digits=15, decimal_places=6,
        help_text="Sale price per share"
    )
    quantity_sold = models.DecimalField(
        max_digits=15, decimal_places=6,
        help_text="Quantity of shares sold"
    )
    gross_proceeds = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Gross proceeds from sale"
    )
    
    # Cost basis details
    cost_basis_per_share = models.DecimalField(
        max_digits=15, decimal_places=6,
        help_text="Cost basis per share"
    )
    total_cost_basis = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Total cost basis for shares sold"
    )
    
    # Tax calculations
    gain_loss_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Realized gain (positive) or loss (negative)"
    )
    term = models.CharField(
        max_length=5, choices=TERM_CHOICES,
        help_text="Short-term or long-term classification"
    )
    wash_sale_adjustment = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        help_text="Wash sale rule adjustment"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-sale_date', 'position__asset__symbol']
        indexes = [
            models.Index(fields=['user', 'tax_year']),
            models.Index(fields=['sale_date']),
            models.Index(fields=['term']),
        ]
        
    def __str__(self) -> str:
        gain_loss = "gain" if self.gain_loss_amount > 0 else "loss"
        return f"{self.position.asset.symbol} {self.term} {gain_loss}: ${abs(self.gain_loss_amount)}"


class DividendIncome(models.Model):
    """Dividend income tracking for tax reporting.
    
    Records dividend payments with proper tax classification
    (qualified vs. ordinary) for accurate tax reporting.
    """
    
    DIVIDEND_TYPES = [
        ('qualified', 'Qualified Dividend'),
        ('ordinary', 'Ordinary Dividend'),
        ('capital_gain', 'Capital Gain Distribution'),
        ('return_of_capital', 'Return of Capital'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE)
    position = models.ForeignKey('portfolios.Position', on_delete=models.CASCADE)
    
    payment_date = models.DateField(help_text="Dividend payment date")
    ex_dividend_date = models.DateField(help_text="Ex-dividend date")
    dividend_type = models.CharField(
        max_length=20, choices=DIVIDEND_TYPES,
        help_text="Type of dividend for tax treatment"
    )
    amount_per_share = models.DecimalField(
        max_digits=10, decimal_places=6,
        help_text="Dividend amount per share"
    )
    shares_held = models.DecimalField(
        max_digits=15, decimal_places=6,
        help_text="Number of shares held on ex-dividend date"
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Total dividend amount received"
    )
    tax_withheld = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        help_text="Tax withheld from dividend"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date', 'position__asset__symbol']
        indexes = [
            models.Index(fields=['user', 'tax_year']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['dividend_type']),
        ]
        
    def __str__(self) -> str:
        return f"{self.position.asset.symbol} dividend: ${self.total_amount} ({self.dividend_type})"


class TaxLossHarvestingOpportunity(models.Model):
    """Tax loss harvesting opportunities identification.
    
    Identifies positions with unrealized losses that could be
    harvested for tax benefits while avoiding wash sale rules.
    """
    
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('recommended', 'Recommended'),
        ('executed', 'Executed'),
        ('expired', 'Expired'),
        ('wash_sale_risk', 'Wash Sale Risk'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey('portfolios.Position', on_delete=models.CASCADE)
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE)
    
    identified_date = models.DateField(auto_now_add=True)
    potential_loss_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Potential tax loss if position is sold"
    )
    current_unrealized_loss = models.DecimalField(
        max_digits=15, decimal_places=2,
        help_text="Current unrealized loss"
    )
    wash_sale_end_date = models.DateField(
        null=True, blank=True,
        help_text="Date when wash sale period ends"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='identified'
    )
    
    # Recommendations
    recommended_sale_date = models.DateField(
        null=True, blank=True,
        help_text="Recommended date to execute sale"
    )
    alternative_investments = models.JSONField(
        default=list,
        help_text="Suggested alternative investments to avoid wash sale"
    )
    tax_benefit_estimate = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text="Estimated tax benefit from harvesting loss"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-potential_loss_amount', '-identified_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['identified_date']),
            models.Index(fields=['potential_loss_amount']),
        ]
        
    def __str__(self) -> str:
        return f"{self.position.asset.symbol} loss harvesting: ${abs(self.potential_loss_amount)}"


class TaxOptimizationRecommendation(models.Model):
    """Tax optimization recommendations and strategies.
    
    Provides personalized tax optimization recommendations based on
    portfolio analysis and tax situation.
    """
    
    RECOMMENDATION_TYPES = [
        ('asset_location', 'Asset Location Optimization'),
        ('rebalancing', 'Tax-Efficient Rebalancing'),
        ('loss_harvesting', 'Tax Loss Harvesting'),
        ('holding_period', 'Holding Period Optimization'),
        ('dividend_timing', 'Dividend Timing Strategy'),
        ('retirement_contribution', 'Retirement Contribution'),
        ('roth_conversion', 'Roth IRA Conversion'),
    ]
    
    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(
        'portfolios.Portfolio', on_delete=models.CASCADE, null=True, blank=True
    )
    
    recommendation_type = models.CharField(
        max_length=25, choices=RECOMMENDATION_TYPES
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Financial impact
    estimated_tax_savings = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text="Estimated annual tax savings"
    )
    implementation_cost = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0'),
        help_text="Cost to implement recommendation"
    )
    
    # Implementation details
    action_required = models.TextField(
        help_text="Specific actions needed to implement"
    )
    deadline = models.DateField(
        null=True, blank=True,
        help_text="Deadline for optimal implementation"
    )
    
    # Status tracking
    is_implemented = models.BooleanField(default=False)
    implementation_date = models.DateField(null=True, blank=True)
    implementation_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-estimated_tax_savings', '-created_at']
        indexes = [
            models.Index(fields=['user', 'tax_year']),
            models.Index(fields=['priority', 'is_implemented']),
            models.Index(fields=['deadline']),
        ]
        
    def __str__(self) -> str:
        return f"{self.title} (${self.estimated_tax_savings or 0} savings)"


class TaxReport(models.Model):
    """Generated tax reports and forms.
    
    Stores generated tax reports with calculation details and
    support for various tax forms and schedules.
    """
    
    REPORT_TYPES = [
        ('schedule_d', 'Schedule D - Capital Gains and Losses'),
        ('form_1099_div', 'Form 1099-DIV - Dividends'),
        ('form_8949', 'Form 8949 - Sales and Dispositions'),
        ('tax_summary', 'Annual Tax Summary'),
        ('loss_carryforward', 'Loss Carryforward Report'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tax_year = models.ForeignKey(TaxYear, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    
    generated_date = models.DateTimeField(auto_now_add=True)
    report_data = models.JSONField(help_text="Complete report data and calculations")
    
    # Summary totals
    total_short_term_gains = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0')
    )
    total_short_term_losses = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0')
    )
    total_long_term_gains = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0')
    )
    total_long_term_losses = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0')
    )
    net_capital_gain_loss = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0')
    )
    total_dividend_income = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0')
    )
    
    # File storage
    pdf_file = models.FileField(
        upload_to='tax_reports/', null=True, blank=True,
        help_text="Generated PDF report file"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-generated_date']
        unique_together = ['user', 'tax_year', 'report_type']
        indexes = [
            models.Index(fields=['user', 'tax_year']),
            models.Index(fields=['generated_date']),
        ]
        
    def __str__(self) -> str:
        return f"{self.get_report_type_display()} - {self.tax_year.year}"
    
    @property
    def net_short_term(self) -> Decimal:
        """Calculate net short-term capital gain/loss."""
        return self.total_short_term_gains - self.total_short_term_losses
    
    @property
    def net_long_term(self) -> Decimal:
        """Calculate net long-term capital gain/loss."""
        return self.total_long_term_gains - self.total_long_term_losses