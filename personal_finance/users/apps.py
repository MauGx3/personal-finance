import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "personal_finance.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import personal_finance.users.signals  # noqa: F401, PLC0415
