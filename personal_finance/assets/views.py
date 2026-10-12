from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import AssetForm
from .models import Asset


class AssetListView(ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"


class AssetDetailView(DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"


class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("assets:list")
    login_url = reverse_lazy("account_login")


class AssetUpdateView(UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("assets:list")


class AssetDeleteView(DeleteView):
    model = Asset
    template_name = "assets/asset_confirm_delete.html"
    success_url = reverse_lazy("assets:list")


class AssetsView(LoginRequiredMixin, ListView):
    """Simple view for displaying financial assets."""

    model = Asset
    template_name = "assets/assets.html"
    context_object_name = "assets"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Financial Assets"
        return context
