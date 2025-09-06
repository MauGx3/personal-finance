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