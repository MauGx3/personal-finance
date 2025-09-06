from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Asset, Portfolio, Holding
from .forms import AssetForm, PortfolioForm, HoldingForm


# Asset Views
class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = "assets/assets.html"  # Changed to match test expectation
    context_object_name = "assets"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Financial Assets'
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"


class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("assets:asset_list")


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("assets:asset_list")


class AssetDeleteView(LoginRequiredMixin, DeleteView):
    model = Asset
    template_name = "assets/asset_confirm_delete.html"
    success_url = reverse_lazy("assets:asset_list")


# Portfolio Views
class PortfolioListView(LoginRequiredMixin, ListView):
    model = Portfolio
    template_name = "assets/portfolio_list.html"
    context_object_name = "portfolios"
    
    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)


class PortfolioDetailView(LoginRequiredMixin, DetailView):
    model = Portfolio
    template_name = "assets/portfolio_detail.html"
    context_object_name = "portfolio"
    
    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)


class PortfolioCreateView(LoginRequiredMixin, CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = "assets/portfolio_form.html"
    success_url = reverse_lazy("assets:portfolio_list")
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PortfolioUpdateView(LoginRequiredMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = "assets/portfolio_form.html"
    success_url = reverse_lazy("assets:portfolio_list")
    
    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)


class PortfolioDeleteView(LoginRequiredMixin, DeleteView):
    model = Portfolio
    template_name = "assets/portfolio_confirm_delete.html"
    success_url = reverse_lazy("assets:portfolio_list")
    
    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)


# Holding Views
class HoldingListView(LoginRequiredMixin, ListView):
    model = Holding
    template_name = "assets/holding_list.html"
    context_object_name = "holdings"
    
    def get_queryset(self):
        return Holding.objects.filter(user=self.request.user)


class HoldingDetailView(LoginRequiredMixin, DetailView):
    model = Holding
    template_name = "assets/holding_detail.html"
    context_object_name = "holding"
    
    def get_queryset(self):
        return Holding.objects.filter(user=self.request.user)


class HoldingCreateView(LoginRequiredMixin, CreateView):
    model = Holding
    form_class = HoldingForm
    template_name = "assets/holding_form.html"
    success_url = reverse_lazy("assets:holding_list")
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter portfolios to only show user's portfolios
        form.fields['portfolio'].queryset = Portfolio.objects.filter(user=self.request.user)
        return form


class HoldingUpdateView(LoginRequiredMixin, UpdateView):
    model = Holding
    form_class = HoldingForm
    template_name = "assets/holding_form.html"
    success_url = reverse_lazy("assets:holding_list")
    
    def get_queryset(self):
        return Holding.objects.filter(user=self.request.user)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter portfolios to only show user's portfolios
        form.fields['portfolio'].queryset = Portfolio.objects.filter(user=self.request.user)
        return form


class HoldingDeleteView(LoginRequiredMixin, DeleteView):
    model = Holding
    template_name = "assets/holding_confirm_delete.html"
    success_url = reverse_lazy("assets:holding_list")
    
    def get_queryset(self):
        return Holding.objects.filter(user=self.request.user)
