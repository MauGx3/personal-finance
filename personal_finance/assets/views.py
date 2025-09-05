from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class AssetsView(LoginRequiredMixin, TemplateView):
    """View for displaying and managing financial assets."""
    template_name = "assets/assets.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Financial Assets'
        return context