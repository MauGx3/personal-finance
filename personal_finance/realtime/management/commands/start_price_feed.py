"""
Management command to start the real-time price feed service.

This command starts the WebSocket price feed service for live market data updates.
Designed for production deployment with proper error handling and monitoring.
"""

import asyncio
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

from personal_finance.realtime.services import price_feed_service

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command to start real-time price feed service."""
    
    help = 'Start the real-time price feed service for live market data updates'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Update interval in seconds (default: 30)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Maximum batch size for price updates (default: 50)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        if options['verbose']:
            logging.basicConfig(level=logging.DEBUG)
        
        interval = options['interval']
        batch_size = options['batch_size']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting real-time price feed service...\n'
                f'Update interval: {interval} seconds\n'
                f'Batch size: {batch_size}\n'
            )
        )
        
        # Update service configuration
        price_feed_service.update_interval = interval
        price_feed_service.max_batch_size = batch_size
        
        try:
            # Run the async service
            asyncio.run(self._run_service())
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Price feed service stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Price feed service error: {e}')
            )
    
    async def _run_service(self):
        """Run the price feed service."""
        await price_feed_service.start()
        
        try:
            # Keep the service running
            while price_feed_service.is_running:
                await asyncio.sleep(1)
        finally:
            await price_feed_service.stop()