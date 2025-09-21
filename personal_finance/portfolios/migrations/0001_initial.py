# Generated migration for portfolios app

import django.core.validators
import django.utils.timezone
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("assets", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Portfolio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Display name for the portfolio",
                        max_length=100,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Optional description of portfolio strategy or purpose",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Whether this portfolio is actively tracked",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="Portfolio owner",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portfolios",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Position",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=8,
                        help_text="Number of shares/units held",
                        max_digits=20,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0")
                            )
                        ],
                    ),
                ),
                (
                    "average_cost",
                    models.DecimalField(
                        decimal_places=8,
                        help_text="Average cost per share/unit",
                        max_digits=20,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0")
                            )
                        ],
                    ),
                ),
                (
                    "first_purchase_date",
                    models.DateField(
                        help_text="Date of first purchase for this position"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Whether this position is currently held",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        help_text="Optional notes about this position",
                    ),
                ),
                (
                    "asset",
                    models.ForeignKey(
                        help_text="The asset held in this position",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="positions",
                        to="assets.asset",
                    ),
                ),
                (
                    "portfolio",
                    models.ForeignKey(
                        help_text="Portfolio containing this position",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="positions",
                        to="portfolios.portfolio",
                    ),
                ),
            ],
            options={
                "ordering": ["asset__symbol"],
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[
                            ("BUY", "Buy"),
                            ("SELL", "Sell"),
                            ("DIV", "Dividend"),
                            ("SPLIT", "Stock Split"),
                            ("MERGER", "Merger/Acquisition"),
                        ],
                        help_text="Type of transaction",
                        max_length=10,
                    ),
                ),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=8,
                        help_text="Number of shares/units in transaction",
                        max_digits=20,
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=8,
                        help_text="Price per share/unit",
                        max_digits=20,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0")
                            )
                        ],
                    ),
                ),
                (
                    "fees",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0"),
                        help_text="Transaction fees and commissions",
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0")
                            )
                        ],
                    ),
                ),
                (
                    "transaction_date",
                    models.DateField(
                        help_text="Date the transaction occurred"
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True, help_text="Optional transaction notes"
                    ),
                ),
                (
                    "position",
                    models.ForeignKey(
                        help_text="Position affected by this transaction",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="portfolios.position",
                    ),
                ),
            ],
            options={
                "ordering": ["-transaction_date", "-created"],
            },
        ),
        migrations.CreateModel(
            name="PortfolioSnapshot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "snapshot_date",
                    models.DateField(help_text="Date of the snapshot"),
                ),
                (
                    "total_value",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Total portfolio value on snapshot date",
                        max_digits=20,
                    ),
                ),
                (
                    "total_cost_basis",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Total cost basis on snapshot date",
                        max_digits=20,
                    ),
                ),
                (
                    "cash_balance",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0"),
                        help_text="Cash balance in portfolio",
                        max_digits=20,
                    ),
                ),
                (
                    "portfolio",
                    models.ForeignKey(
                        help_text="Portfolio being tracked",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="snapshots",
                        to="portfolios.portfolio",
                    ),
                ),
            ],
            options={
                "ordering": ["-snapshot_date"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="portfoliosnapshot",
            unique_together={("portfolio", "snapshot_date")},
        ),
        migrations.AlterUniqueTogether(
            name="position",
            unique_together={("portfolio", "asset")},
        ),
        migrations.AlterUniqueTogether(
            name="portfolio",
            unique_together={("user", "name")},
        ),
    ]
