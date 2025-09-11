"""Portfolio management models."""

from decimal import Decimal
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel

User = get_user_model()


class Portfolio(TimeStampedModel):
    """User portfolio containing multiple positions.
    
    A portfolio represents a collection of investment positions owned by a user.
    It tracks the overall performance and allocation of investments.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='portfolios',
        help_text="Portfolio owner"
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name for the portfolio"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of portfolio strategy or purpose"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this portfolio is actively tracked"
    )
    
    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self) -> str:
        return f"{self.user.username} - {self.name}"
    
    @property
    def total_value(self) -> Decimal:
        """Calculate current total portfolio value.
        
        Returns:
            Current market value of all positions in the portfolio.
        """
        return sum(
            position.current_value for position in self.positions.filter(is_active=True)
        )
    
    @property
    def total_cost_basis(self) -> Decimal:
        """Calculate total cost basis of portfolio.
        
        Returns:
            Total amount invested (cost basis) across all positions.
        """
        return sum(
            position.total_cost_basis for position in self.positions.filter(is_active=True)
        )
    
    @property
    def total_return(self) -> Decimal:
        """Calculate total portfolio return.
        
        Returns:
            Absolute dollar return (current value - cost basis).
        """
        return self.total_value - self.total_cost_basis
    
    @property
    def total_return_percentage(self) -> Optional[Decimal]:
        """Calculate percentage return of portfolio.
        
        Returns:
            Percentage return or None if cost basis is zero.
        """
        if self.total_cost_basis == 0:
            return None
        return (self.total_return / self.total_cost_basis) * 100


class Position(TimeStampedModel):
    """Individual investment position within a portfolio.
    
    Represents a specific asset holding with quantity, cost basis,
    and performance tracking capabilities.
    """
    
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='positions',
        help_text="Portfolio containing this position"
    )
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='positions',
        help_text="The asset held in this position"
    )
    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Number of shares/units held"
    )
    average_cost = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Average cost per share/unit"
    )
    first_purchase_date = models.DateField(
        help_text="Date of first purchase for this position"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this position is currently held"
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional notes about this position"
    )
    
    class Meta:
        ordering = ['asset__symbol']
        unique_together = ['portfolio', 'asset']
    
    def __str__(self) -> str:
        return f"{self.portfolio.name} - {self.asset.symbol} ({self.quantity})"
    
    @property
    def total_cost_basis(self) -> Decimal:
        """Calculate total cost basis for this position.
        
        Returns:
            Total amount invested in this position.
        """
        return self.quantity * self.average_cost
    
    @property
    def current_value(self) -> Decimal:
        """Calculate current market value of position.
        
        Returns:
            Current market value based on latest price.
        """
        current_price = self.asset.current_price or Decimal('0')
        return self.quantity * current_price
    
    @property
    def unrealized_gain_loss(self) -> Decimal:
        """Calculate unrealized gain/loss for position.
        
        Returns:
            Dollar amount of unrealized gain (positive) or loss (negative).
        """
        return self.current_value - self.total_cost_basis
    
    @property
    def unrealized_return_percentage(self) -> Optional[Decimal]:
        """Calculate unrealized return percentage.
        
        Returns:
            Percentage return or None if cost basis is zero.
        """
        if self.total_cost_basis == 0:
            return None
        return (self.unrealized_gain_loss / self.total_cost_basis) * 100
    
    def update_from_transactions(self):
        """Update position metrics based on transaction history.
        
        This method recalculates quantity and average cost based on all
        transactions for this position.
        """
        transactions = self.transactions.order_by('transaction_date', 'created')
        
        total_quantity = Decimal('0')
        total_cost = Decimal('0')
        
        for transaction in transactions:
            if transaction.transaction_type == Transaction.TransactionType.BUY:
                total_quantity += transaction.quantity
                total_cost += (transaction.quantity * transaction.price) + transaction.fees
            elif transaction.transaction_type == Transaction.TransactionType.SELL:
                # For sells, reduce quantity but keep weighted average cost
                if total_quantity > 0:
                    # Calculate proportion sold
                    proportion_sold = transaction.quantity / total_quantity
                    total_cost -= total_cost * proportion_sold
                    total_quantity -= transaction.quantity
        
        if total_quantity > 0:
            self.quantity = total_quantity
            self.average_cost = total_cost / total_quantity
        else:
            self.quantity = Decimal('0')
            self.average_cost = Decimal('0')
        
        self.save(update_fields=['quantity', 'average_cost'])


class Transaction(TimeStampedModel):
    """Investment transaction record.
    
    Tracks all buy/sell transactions for portfolio positions,
    enabling detailed cost basis and performance calculations.
    """
    
    class TransactionType(models.TextChoices):
        BUY = 'BUY', 'Buy'
        SELL = 'SELL', 'Sell'
        DIVIDEND = 'DIV', 'Dividend'
        SPLIT = 'SPLIT', 'Stock Split'
        MERGER = 'MERGER', 'Merger/Acquisition'
    
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="Position affected by this transaction"
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
        help_text="Type of transaction"
    )
    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        help_text="Number of shares/units in transaction"
    )
    price = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Price per share/unit"
    )
    fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Transaction fees and commissions"
    )
    transaction_date = models.DateField(
        help_text="Date the transaction occurred"
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional transaction notes"
    )
    
    class Meta:
        ordering = ['-transaction_date', '-created']
    
    def __str__(self) -> str:
        return (
            f"{self.transaction_type} {self.quantity} "
            f"{self.position.asset.symbol} @ ${self.price}"
        )
    
    @property
    def total_value(self) -> Decimal:
        """Calculate total transaction value including fees.
        
        Returns:
            Total dollar amount of transaction.
        """
        return (self.quantity * self.price) + self.fees
    
    def save(self, *args, **kwargs):
        """Override save to update position after transaction."""
        super().save(*args, **kwargs)
        # Only call update if position has the method implemented
        if hasattr(self.position, 'update_from_transactions'):
            self.position.update_from_transactions()


class PortfolioSnapshot(TimeStampedModel):
    """Historical snapshot of portfolio performance.
    
    Stores point-in-time portfolio values for performance tracking
    and historical analysis.
    """
    
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='snapshots',
        help_text="Portfolio being tracked"
    )
    snapshot_date = models.DateField(
        help_text="Date of the snapshot"
    )
    total_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Total portfolio value on snapshot date"
    )
    total_cost_basis = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Total cost basis on snapshot date"
    )
    cash_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Cash balance in portfolio"
    )
    
    class Meta:
        ordering = ['-snapshot_date']
        unique_together = ['portfolio', 'snapshot_date']
    
    def __str__(self) -> str:
        return f"{self.portfolio.name} - {self.snapshot_date} (${self.total_value})"
    
    @property
    def total_return(self) -> Decimal:
        """Calculate total return for this snapshot.
        
        Returns:
            Dollar amount of return.
        """
        return self.total_value - self.total_cost_basis
    
    @property
    def return_percentage(self) -> Optional[Decimal]:
        """Calculate return percentage for this snapshot.
        
        Returns:
            Percentage return or None if cost basis is zero.
        """
        if self.total_cost_basis == 0:
            return None
        return (self.total_return / self.total_cost_basis) * 100