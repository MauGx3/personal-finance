"""Asset pages: review an asset, fix its class, see its price history."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import UpdateView

from apps.portfolios.models import Holding, Transaction

from .models import Asset


class AssetDetailView(LoginRequiredMixin, UpdateView):
    model = Asset
    fields = ["name", "asset_class", "currency", "sector", "provider_symbol", "is_active"]
    template_name = "assets/asset_detail.html"

    def get_success_url(self) -> str:
        messages.success(self.request, "Asset updated.")
        return reverse("assets:detail", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        quotes = list(self.object.quotes.order_by("-day")[:260])[::-1]
        context["price_history"] = [(q.day, q.close) for q in quotes]
        context["latest"] = quotes[-1] if quotes else None
        context["holdings"] = Holding.objects.filter(
            asset=self.object, portfolio__user=user
        ).select_related("portfolio")
        context["transactions"] = Transaction.objects.filter(
            asset=self.object, portfolio__user=user
        ).select_related("portfolio")[:50]
        return context
