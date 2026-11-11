"""Fetch the latest prices and exchange rates."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.data_sources.registry import get_provider
from apps.data_sources.services import sync_all


class Command(BaseCommand):
    help = "Sync daily closes for held assets and the exchange rates they need."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--all", action="store_true", help="Include assets that are not held.")
        parser.add_argument("--days", type=int, help="Re-fetch this many days instead of resuming.")
        parser.add_argument("--provider", help="Provider name (default: settings.PRICE_PROVIDER).")

    def handle(self, *args, **options) -> None:
        start = None
        if options["days"]:
            start = timezone.localdate() - timedelta(days=options["days"])
        report = sync_all(
            get_provider(options["provider"]), include_unheld=options["all"], start=start
        )
        for symbol, count in {**report.quotes, **report.fx}.items():
            self.stdout.write(f"{symbol}: {count} days")
        for symbol, error in report.errors.items():
            self.stderr.write(self.style.WARNING(f"{symbol}: {error}"))
        self.stdout.write(
            self.style.SUCCESS(f"Stored {report.total} rows, {len(report.errors)} symbols failed.")
        )
