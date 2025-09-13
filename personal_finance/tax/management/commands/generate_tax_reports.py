"""Management command to generate tax reports."""

import logging
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from personal_finance.tax.models import TaxYear
from personal_finance.tax.report_service import TaxReportService

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Generate tax reports for users.

    This command generates various tax reports including Schedule D,
    Form 1099-DIV equivalent, and comprehensive tax summaries.
    """

    help = "Generate tax reports"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--user",
            type=str,
            help="Username to generate reports for (all users if not specified)",
        )
        parser.add_argument(
            "--year",
            type=int,
            help="Tax year for reports (current year if not specified)",
        )
        parser.add_argument(
            "--report-type",
            choices=[
                "schedule_d",
                "form_1099_div",
                "form_8949",
                "tax_summary",
                "loss_carryforward",
                "all",
            ],
            default="all",
            help="Type of report to generate (default: all)",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            help="Directory to save report files (optional)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what reports would be generated without creating them",
        )
        parser.add_argument(
            "--verbose", action="store_true", help="Verbose output"
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        self.dry_run = options["dry_run"]
        self.verbose = options["verbose"]
        self.output_dir = options["output_dir"]

        if self.verbose:
            logging.basicConfig(level=logging.INFO)

        if self.output_dir:
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            self.stdout.write(f"Output directory: {output_path.absolute()}")

        report_service = TaxReportService()

        try:
            # Get or create tax year
            year = options["year"] or 2024
            tax_year, created = TaxYear.objects.get_or_create(
                year=year,
                defaults={
                    "filing_deadline": f"{year + 1}-04-15",
                    "standard_deduction_single": 13850,
                    "standard_deduction_married": 27700,
                    "long_term_capital_gains_thresholds": {
                        "0": {"min": 0, "max": 44625, "rate": 0.0},
                        "15": {"min": 44626, "max": 492300, "rate": 0.15},
                        "20": {"min": 492301, "max": None, "rate": 0.20},
                    },
                },
            )

            if created:
                self.stdout.write(f"Created tax year {year}")

            if options["user"]:
                self._generate_reports_for_user(
                    report_service,
                    options["user"],
                    tax_year,
                    options["report_type"],
                )
            else:
                self._generate_reports_for_all_users(
                    report_service, tax_year, options["report_type"]
                )

        except Exception as e:
            logger.error(f"Error generating tax reports: {str(e)}")
            raise CommandError(f"Tax report generation failed: {str(e)}")

    def _generate_reports_for_user(
        self,
        report_service: TaxReportService,
        username: str,
        tax_year: TaxYear,
        report_type: str,
    ):
        """Generate tax reports for a specific user.

        Args:
            report_service: Tax report service instance
            username: Username to generate reports for
            tax_year: Tax year for reports
            report_type: Type of report to generate
        """
        try:
            user = User.objects.get(username=username)
            self.stdout.write(
                f"Generating {report_type} reports for user: {username}"
            )

            if self.dry_run:
                self.stdout.write(
                    self.style.WARNING("DRY RUN - No reports will be created")
                )
                self._show_report_preview(user, tax_year, report_type)
                return

            reports = self._generate_reports(
                report_service, user, tax_year, report_type
            )
            self._display_report_summary(reports, username)

        except User.DoesNotExist:
            raise CommandError(f"User {username} not found")

    def _generate_reports_for_all_users(
        self,
        report_service: TaxReportService,
        tax_year: TaxYear,
        report_type: str,
    ):
        """Generate tax reports for all users with portfolios.

        Args:
            report_service: Tax report service instance
            tax_year: Tax year for reports
            report_type: Type of report to generate
        """
        users = User.objects.filter(portfolios__isnull=False).distinct()
        total_users = users.count()

        self.stdout.write(
            f"Generating {report_type} reports for {total_users} users"
        )

        if self.dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN - No reports will be created")
            )
            for user in users[:5]:  # Show preview for first 5 users
                self._show_report_preview(user, tax_year, report_type)
            if total_users > 5:
                self.stdout.write(f"... and {total_users - 5} more users")
            return

        total_reports = 0
        users_with_reports = 0
        error_count = 0

        for i, user in enumerate(users, 1):
            try:
                reports = self._generate_reports(
                    report_service, user, tax_year, report_type
                )

                if reports:
                    users_with_reports += 1
                    total_reports += len(reports)

                    if self.verbose:
                        self._display_report_summary(reports, user.username)

                # Progress update
                if i % 10 == 0 or i == total_users:
                    self.stdout.write(
                        f"Progress: {i}/{total_users} users processed"
                    )

            except Exception as e:
                error_count += 1
                logger.error(
                    f"Error generating reports for user {user.username}: {str(e)}"
                )
                self.stdout.write(
                    self.style.ERROR(f"Error for {user.username}: {str(e)}")
                )

        # Final summary
        self.stdout.write(
            self.style.SUCCESS(
                f"Report generation complete: {total_reports} reports generated "
                f"for {users_with_reports} users ({error_count} errors)"
            )
        )

    def _generate_reports(
        self,
        report_service: TaxReportService,
        user: User,
        tax_year: TaxYear,
        report_type: str,
    ) -> dict:
        """Generate the specified reports for a user.

        Args:
            report_service: Tax report service instance
            user: User to generate reports for
            tax_year: Tax year for reports
            report_type: Type of report to generate

        Returns:
            Dictionary of generated reports
        """
        reports = {}

        if report_type == "all":
            reports = report_service.generate_all_tax_reports(user, tax_year)
        elif report_type == "schedule_d":
            reports["schedule_d"] = report_service.generate_schedule_d_report(
                user, tax_year
            )
        elif report_type == "form_1099_div":
            reports["form_1099_div"] = report_service.generate_dividend_report(
                user, tax_year
            )
        elif report_type == "form_8949":
            reports["form_8949"] = report_service.generate_form_8949_report(
                user, tax_year
            )
        elif report_type == "tax_summary":
            reports["tax_summary"] = (
                report_service.generate_tax_summary_report(user, tax_year)
            )
        elif report_type == "loss_carryforward":
            reports["loss_carryforward"] = (
                report_service.generate_loss_carryforward_report(
                    user, tax_year
                )
            )

        # Save report files if output directory specified
        if self.output_dir and reports:
            self._save_report_files(reports, user, tax_year)

        return reports

    def _show_report_preview(
        self, user: User, tax_year: TaxYear, report_type: str
    ):
        """Show a preview of what reports would be generated.

        Args:
            user: User to preview
            tax_year: Tax year for preview
            report_type: Type of report to preview
        """
        try:
            from personal_finance.portfolios.models import Transaction
        except ImportError:
            Transaction = None
            
        from personal_finance.tax.models import CapitalGainLoss, DividendIncome

        # Count relevant data
        if Transaction is not None:
            transaction_count = Transaction.objects.filter(
                position__portfolio__user=user, date__year=tax_year.year
            ).count()
        else:
            transaction_count = 0

        capital_gains_count = CapitalGainLoss.objects.filter(
            user=user, tax_year=tax_year
        ).count()

        dividend_count = DividendIncome.objects.filter(
            user=user, tax_year=tax_year
        ).count()

        self.stdout.write(f"\nPreview for {user.username}:")
        self.stdout.write(
            f"  Transactions in {tax_year.year}: {transaction_count}"
        )
        self.stdout.write(f"  Capital gains/losses: {capital_gains_count}")
        self.stdout.write(f"  Dividend payments: {dividend_count}")

        if report_type == "all":
            self.stdout.write("  Would generate: 5 report types")
        else:
            self.stdout.write(f"  Would generate: {report_type}")

    def _display_report_summary(self, reports: dict, username: str):
        """Display summary of generated reports.

        Args:
            reports: Dictionary of generated reports
            username: Username for the reports
        """
        if not reports:
            self.stdout.write(f"No reports generated for {username}")
            return

        self.stdout.write(f"\nReports generated for {username}:")

        for report_type, report in reports.items():
            self.stdout.write(
                f"  {report_type}: {report.get_report_type_display()}"
            )

            # Show key metrics
            if (
                hasattr(report, "net_capital_gain_loss")
                and report.net_capital_gain_loss
            ):
                gain_loss = (
                    "gain" if report.net_capital_gain_loss > 0 else "loss"
                )
                self.stdout.write(
                    f"    Net capital {gain_loss}: ${abs(report.net_capital_gain_loss):,.2f}"
                )

            if (
                hasattr(report, "total_dividend_income")
                and report.total_dividend_income
            ):
                self.stdout.write(
                    f"    Total dividends: ${report.total_dividend_income:,.2f}"
                )

    def _save_report_files(self, reports: dict, user: User, tax_year: TaxYear):
        """Save report data to files.

        Args:
            reports: Dictionary of generated reports
            user: User the reports belong to
            tax_year: Tax year for the reports
        """
        import json
        import re

        if not self.output_dir:
            return  # No output directory specified, skip saving

        output_path = Path(
            self.output_dir
        ).resolve()  # Resolve to absolute path for security

        # Sanitize username to prevent directory traversal
        # Remove or replace characters that could be used for path traversal
        safe_username = re.sub(
            r"[^\w\-]", "_", user.username
        )  # Replace non-alphanumeric chars with '_'
        safe_username = safe_username.strip(
            "_"
        )  # Remove leading/trailing underscores
        if not safe_username:
            safe_username = "unknown_user"  # Fallback for empty usernames

        # Sanitize year (though it's an int, ensure it's safe)
        safe_year = (
            str(tax_year.year)
            if isinstance(tax_year.year, int)
            else "unknown_year"
        )

        user_dir = output_path / f"{safe_username}_{safe_year}"
        user_dir.mkdir(parents=True, exist_ok=True)

        # Ensure the user_dir is within the output_path to prevent traversal
        try:
            user_dir.resolve().relative_to(output_path.resolve())
        except ValueError:
            raise CommandError(
                f"Invalid path detected for user {user.username}: potential directory traversal"
            )

        for report_type, report in reports.items():
            if not hasattr(report, "report_data") or not report.report_data:
                continue  # Skip if no data to save

            # Save JSON data
            json_file = user_dir / f"{report_type}.json"
            try:
                with open(json_file, "w") as f:
                    json.dump(report.report_data, f, indent=2, default=str)
                if self.verbose:
                    self.stdout.write(f"Saved {json_file}")
            except (OSError, IOError) as e:
                logger.error(f"Error saving file {json_file}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"Failed to save {json_file}: {str(e)}")
                )

        self.stdout.write(f"Report files saved to: {user_dir}")
