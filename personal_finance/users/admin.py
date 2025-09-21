from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .models import User

# Graceful handling of allauth imports for CI/CD compatibility
try:
    from allauth.account.decorators import secure_admin_login
    from .forms import UserAdminChangeForm
    from .forms import UserAdminCreationForm
    ALLAUTH_AVAILABLE = True
except ImportError:
    ALLAUTH_AVAILABLE = False
    # Use default Django forms when allauth is not available
    UserAdminChangeForm = None
    UserAdminCreationForm = None

if ALLAUTH_AVAILABLE and getattr(settings, 'DJANGO_ADMIN_FORCE_ALLAUTH', False):
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    # Use custom forms if available, otherwise use default Django forms
    if ALLAUTH_AVAILABLE and UserAdminChangeForm:
        form = UserAdminChangeForm
        add_form = UserAdminCreationForm
    
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]
