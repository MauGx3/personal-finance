"""Management command to calculate tax implications for transactions."""

import logging
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from personal_finance.portfolios.models import Transaction
from personal_finance.tax.services import TaxCalculationService

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Calculate tax implications for transactions.
    
    This command processes transactions and calculates tax lots,
    capital gains/losses, and dividend income for tax reporting.
    """
    
    help = 'Calculate tax implications for transactions'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--user',
            type=str,
            help='Username to calculate taxes for (all users if not specified)'
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Tax year to process (current year if not specified)'
        )
        parser.add_argument(
            '--transaction-id',
            type=int,
            help='Process specific transaction ID'
        )
        parser.add_argument(
            '--reprocess',
            action='store_true',
            help='Reprocess existing tax calculations'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        self.dry_run = options['dry_run']
        self.verbose = options['verbose']
        
        if self.verbose:
            logging.basicConfig(level=logging.INFO)
        
        tax_service = TaxCalculationService()
        
        try:
            if options['transaction_id']:
                self._process_single_transaction(tax_service, options['transaction_id'])
            else:
                self._process_transactions(
                    tax_service,
                    options['user'],
                    options['year'],
                    options['reprocess']
                )
                
        except Exception as e:
            logger.error(f"Error calculating taxes: {str(e)}")
            raise CommandError(f"Tax calculation failed: {str(e)}")
    
    def _process_single_transaction(self, tax_service: TaxCalculationService, transaction_id: int):
        """Process a single transaction for tax calculations.
        
        Args:
            tax_service: Tax calculation service instance
            transaction_id: ID of transaction to process
        """
        try:
            trans = Transaction.objects.select_related(
                'position__asset', 'position__portfolio__user'
            ).get(id=transaction_id)
            
            self.stdout.write(f"Processing transaction {transaction_id}: {trans}")
            
            if not self.dry_run:
                with transaction.atomic():
                    tax_service.process_transaction_for_taxes(trans)
                    
            self.stdout.write(
                self.style.SUCCESS(f"Successfully processed transaction {transaction_id}")
            )
            
        except Transaction.DoesNotExist:
            raise CommandError(f"Transaction {transaction_id} not found")
    
    def _process_transactions(
        self, 
        tax_service: TaxCalculationService, 
        username: str = None,
        year: int = None,
        reprocess: bool = False
    ):
        """Process multiple transactions for tax calculations.
        
        Args:
            tax_service: Tax calculation service instance
            username: Optional username filter
            year: Optional year filter
            reprocess: Whether to reprocess existing calculations
        """
        # Build query
        queryset = Transaction.objects.select_related(
            'position__asset', 'position__portfolio__user'
        ).order_by('date', 'id')
        
        if username:
            try:
                user = User.objects.get(username=username)
                queryset = queryset.filter(position__portfolio__user=user)
                self.stdout.write(f"Filtering to user: {username}")
            except User.DoesNotExist:
                raise CommandError(f"User {username} not found")
        
        if year:
            queryset = queryset.filter(date__year=year)
            self.stdout.write(f"Filtering to year: {year}")
        
        total_count = queryset.count()
        self.stdout.write(f"Found {total_count} transactions to process")
        
        if total_count == 0:
            self.stdout.write("No transactions found matching criteria")
            return
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
            
            # Show summary of what would be processed
            buy_count = queryset.filter(transaction_type='buy').count()
            sell_count = queryset.filter(transaction_type='sell').count()
            dividend_count = queryset.filter(transaction_type='dividend').count()
            
            self.stdout.write(f"Would process:")
            self.stdout.write(f"  - {buy_count} buy transactions (tax lots)")
            self.stdout.write(f"  - {sell_count} sell transactions (capital gains/losses)")
            self.stdout.write(f"  - {dividend_count} dividend transactions")
            return
        
        # Process transactions in batches
        batch_size = 100
        processed_count = 0
        error_count = 0
        
        self.stdout.write("Starting tax calculation processing...")
        
        for i in range(0, total_count, batch_size):
            batch = queryset[i:i + batch_size]
            
            with transaction.atomic():
                for trans in batch:
                    try:
                        # Skip if already processed and not reprocessing
                        if not reprocess and self._is_transaction_processed(trans):
                            if self.verbose:
                                self.stdout.write(f"Skipping already processed: {trans}")
                            continue
                        
                        tax_service.process_transaction_for_taxes(trans)
                        processed_count += 1
                        
                        if self.verbose:
                            self.stdout.write(f"Processed: {trans}")
                            
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error processing transaction {trans.id}: {str(e)}")
                        self.stdout.write(
                            self.style.ERROR(f"Error processing {trans}: {str(e)}")
                        )
            
            # Progress update
            progress = min(i + batch_size, total_count)
            self.stdout.write(
                f"Progress: {progress}/{total_count} "
                f"({processed_count} processed, {error_count} errors)"
            )
        
        # Final summary
        self.stdout.write(
            self.style.SUCCESS(
                f"Tax calculation complete: {processed_count} processed, {error_count} errors"
            )
        )
        
        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Some transactions had errors. Check logs for details."
                )
            )
    
    def _is_transaction_processed(self, trans: Transaction) -> bool:
        """Check if a transaction has already been processed for taxes.
        
        Args:
            trans: Transaction to check
            
        Returns:
            True if transaction has been processed
        """
        from personal_finance.tax.models import TaxLot, CapitalGainLoss, DividendIncome
        
        if trans.transaction_type == 'buy':
            return TaxLot.objects.filter(transaction=trans).exists()
        elif trans.transaction_type == 'sell':
            return CapitalGainLoss.objects.filter(transaction=trans).exists()
        elif trans.transaction_type == 'dividend':
            return DividendIncome.objects.filter(
                position=trans.position,
                payment_date=trans.date,
                total_amount=trans.quantity * trans.price
            ).exists()
        
        return False