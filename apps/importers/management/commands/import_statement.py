"""Import a statement file from the command line."""

from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.importers.base import StatementError
from apps.importers.services import import_statement
from apps.portfolios.models import Portfolio


class Command(BaseCommand):
    help = "Import a B3 or generic CSV statement into a portfolio."

    def add_arguments(self, parser) -> None:
        parser.add_argument("files", nargs="+", type=Path)
        parser.add_argument("--portfolio", help="Portfolio name (default: the default portfolio).")
        parser.add_argument("--user", help="Owner's email (default: the only user).")
        parser.add_argument("--parser", help="Parser name (default: auto-detect).")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options) -> None:
        users = get_user_model().objects.all()
        if options["user"]:
            users = users.filter(email=options["user"])
        if users.count() != 1:
            raise CommandError("Pass --user EMAIL to choose the portfolio owner.")
        user = users.get()
        if options["portfolio"]:
            try:
                portfolio = Portfolio.objects.get(user=user, name=options["portfolio"])
            except Portfolio.DoesNotExist as exc:
                raise CommandError(f"No portfolio named {options['portfolio']!r}.") from exc
        else:
            portfolio = Portfolio.default_for(user)

        for path in options["files"]:
            try:
                with path.open("rb") as handle:
                    outcome = import_statement(
                        portfolio, handle, path.name, options["parser"], options["dry_run"]
                    )
            except (OSError, StatementError) as exc:
                raise CommandError(f"{path}: {exc}") from exc
            verb = "would create" if outcome.dry_run else "created"
            self.stdout.write(
                f"{path.name} [{outcome.parser.label}]: {verb} {outcome.created}, "
                f"skipped {outcome.skipped} already imported"
            )
            for warning in outcome.warnings:
                self.stderr.write(self.style.WARNING(f"  {warning}"))
