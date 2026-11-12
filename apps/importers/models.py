"""A record of each statement import, so an import can be reviewed or undone."""

from django.db import models

from apps.portfolios.models import Portfolio


class ImportBatch(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="import_batches"
    )
    filename = models.CharField(max_length=255)
    parser = models.CharField(max_length=50)
    created_count = models.PositiveIntegerField(default=0)
    skipped_count = models.PositiveIntegerField(default=0)
    warnings = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "import batches"

    def __str__(self) -> str:
        return f"{self.filename} ({self.created_at:%Y-%m-%d})"
