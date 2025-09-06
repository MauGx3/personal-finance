from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Asset
from .forms import AssetForm


class AssetListView(ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"


class AssetDetailView(DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"


class AssetCreateView(CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("assets:asset_list")


class AssetUpdateView(UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("assets:asset_list")


class AssetDeleteView(DeleteView):
    model = Asset
    template_name = "assets/asset_confirm_delete.html"
    success_url = reverse_lazy("assets:asset_list")
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Asset


class AssetsView(LoginRequiredMixin, ListView):
    """Simple view for displaying financial assets."""
    model = Asset
    template_name = "assets/assets.html"
    context_object_name = 'assets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Financial Assets'
        return context
