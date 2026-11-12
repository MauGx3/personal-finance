"""Rebuild the affected holding whenever a transaction changes.

Bulk imports use ``bulk_create`` (which sends no signals) and rebuild once at
the end instead.
"""

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Transaction
from .services.holdings import rebuild_holding


@receiver(pre_save, sender=Transaction)
def _remember_previous_asset(instance: Transaction, **kwargs) -> None:
    instance._previous_key = None
    if instance.pk:
        previous = (
            Transaction.objects.filter(pk=instance.pk)
            .values_list("portfolio_id", "asset_id")
            .first()
        )
        instance._previous_key = previous


@receiver(post_save, sender=Transaction)
def _rebuild_after_save(instance: Transaction, **kwargs) -> None:
    key = (instance.portfolio_id, instance.asset_id)
    rebuild_holding(*key)
    previous = getattr(instance, "_previous_key", None)
    if previous and previous != key:
        rebuild_holding(*previous)


@receiver(post_delete, sender=Transaction)
def _rebuild_after_delete(instance: Transaction, **kwargs) -> None:
    rebuild_holding(instance.portfolio_id, instance.asset_id)
