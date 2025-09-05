from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AssetsConfig(AppConfig):
    name = "personal_finance.assets"
    verbose_name = _("Assets")
