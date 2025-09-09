"""Management command to identify tax loss harvesting opportunities."""

import logging
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from personal_finance.tax.services import TaxLossHarvestingService

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Identify tax loss harvesting opportunities.
    
    This command analyzes portfolios to find positions with unrealized
    losses that could be harvested for tax benefits.
    """
    
    help = 'Identify tax loss harvesting opportunities'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--user',
            type=str,
            help='Username to analyze (all users if not specified)'
        )
        parser.add_argument(
            '--minimum-loss',
            type=float,
            default=100.0,
            help='Minimum loss amount to consider (default: $100)'
        )
        parser.add_argument(
            '--generate-recommendations',
            action='store_true',
            help='Generate specific recommendations for opportunities'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be found without creating records'
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
        
        loss_service = TaxLossHarvestingService()
        minimum_loss = Decimal(str(options['minimum_loss']))
        
        try:
            if options['user']:
                self._analyze_user(
                    loss_service, 
                    options['user'], 
                    minimum_loss,
                    options['generate_recommendations']
                )
            else:
                self._analyze_all_users(
                    loss_service, 
                    minimum_loss,
                    options['generate_recommendations']
                )
                
        except Exception as e:
            logger.error(f"Error identifying loss harvesting opportunities: {str(e)}")
            raise CommandError(f"Loss harvesting analysis failed: {str(e)}")
    
    def _analyze_user(
        self, 
        loss_service: TaxLossHarvestingService, 
        username: str,
        minimum_loss: Decimal,
        generate_recommendations: bool
    ):
        """Analyze tax loss harvesting opportunities for a specific user.
        
        Args:
            loss_service: Tax loss harvesting service instance
            username: Username to analyze
            minimum_loss: Minimum loss threshold
            generate_recommendations: Whether to generate recommendations
        """
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"Analyzing tax loss harvesting for user: {username}")
            
            opportunities = loss_service.identify_loss_harvesting_opportunities(
                user, minimum_loss
            )
            
            self._display_opportunities(opportunities, user.username)
            
            if generate_recommendations and opportunities and not self.dry_run:
                loss_service.generate_loss_harvesting_recommendations(opportunities)
                self.stdout.write(
                    self.style.SUCCESS("Generated recommendations for opportunities")
                )
                
        except User.DoesNotExist:
            raise CommandError(f"User {username} not found")
    
    def _analyze_all_users(
        self, 
        loss_service: TaxLossHarvestingService,
        minimum_loss: Decimal,
        generate_recommendations: bool
    ):
        """Analyze tax loss harvesting opportunities for all users.
        
        Args:
            loss_service: Tax loss harvesting service instance
            minimum_loss: Minimum loss threshold
            generate_recommendations: Whether to generate recommendations
        """
        users = User.objects.filter(portfolios__isnull=False).distinct()
        total_users = users.count()
        
        self.stdout.write(f"Analyzing {total_users} users for tax loss harvesting opportunities")
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
        
        total_opportunities = 0
        users_with_opportunities = 0
        
        for i, user in enumerate(users, 1):
            try:
                opportunities = loss_service.identify_loss_harvesting_opportunities(
                    user, minimum_loss
                )
                
                if opportunities:
                    users_with_opportunities += 1
                    total_opportunities += len(opportunities)
                    
                    if self.verbose:
                        self._display_opportunities(opportunities, user.username)
                    
                    if generate_recommendations and not self.dry_run:
                        loss_service.generate_loss_harvesting_recommendations(opportunities)
                
                # Progress update
                if i % 10 == 0 or i == total_users:
                    self.stdout.write(f"Progress: {i}/{total_users} users analyzed")
                    
            except Exception as e:
                logger.error(f"Error analyzing user {user.username}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"Error analyzing {user.username}: {str(e)}")
                )
        
        # Final summary
        self.stdout.write(
            self.style.SUCCESS(
                f"Analysis complete: {total_opportunities} opportunities found "
                f"for {users_with_opportunities} users"
            )
        )
    
    def _display_opportunities(self, opportunities, username: str):
        """Display tax loss harvesting opportunities.
        
        Args:
            opportunities: List of opportunities to display
            username: Username for the opportunities
        """
        if not opportunities:
            self.stdout.write(f"No opportunities found for {username}")
            return
        
        self.stdout.write(f"\nTax Loss Harvesting Opportunities for {username}:")
        self.stdout.write("-" * 80)
        
        total_potential_loss = Decimal('0')
        total_estimated_benefit = Decimal('0')
        
        for opp in opportunities:
            status_color = self.style.WARNING if opp.status == 'wash_sale_risk' else self.style.SUCCESS
            
            self.stdout.write(
                f"  {opp.position.asset.symbol:8} | "
                f"Loss: ${opp.potential_loss_amount:>8,.2f} | "
                f"Status: {status_color(opp.status):15} | "
                f"Benefit: ${opp.tax_benefit_estimate or 0:>6,.2f}"
            )
            
            if opp.wash_sale_end_date:
                self.stdout.write(f"           | Wash sale ends: {opp.wash_sale_end_date}")
            
            if opp.alternative_investments:
                alternatives = ", ".join(opp.alternative_investments[:3])
                self.stdout.write(f"           | Alternatives: {alternatives}")
            
            total_potential_loss += opp.potential_loss_amount
            total_estimated_benefit += opp.tax_benefit_estimate or Decimal('0')
        
        self.stdout.write("-" * 80)
        self.stdout.write(
            f"Total: {len(opportunities)} opportunities, "
            f"${total_potential_loss:,.2f} losses, "
            f"${total_estimated_benefit:,.2f} estimated benefit"
        )
        self.stdout.write("")