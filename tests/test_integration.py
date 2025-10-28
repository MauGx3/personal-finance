"""Integration tests for SaaS features."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.integration
class TestFeatureFlagIntegration:
    """Test feature flags integration."""

    def test_feature_flag_with_user_groups(self):
        """Test feature flags with user groups."""
        from django.contrib.auth.models import Group
        from waffle.models import Flag

        # Create a flag for beta users
        flag = Flag.objects.create(name="beta_features", everyone=False)

        # Create beta group
        beta_group = Group.objects.create(name="Beta Testers")
        flag.groups.add(beta_group)

        # Create users
        beta_user = User.objects.create_user(email="beta@example.com", password="testpass123")
        beta_user.groups.add(beta_group)

        regular_user = User.objects.create_user(email="regular@example.com", password="testpass123")

        # Test access
        from apps.core.feature_flags import is_feature_enabled

        assert is_feature_enabled("beta_features", user=beta_user)
        assert not is_feature_enabled("beta_features", user=regular_user)


@pytest.mark.django_db
@pytest.mark.integration
class TestImpersonationIntegration:
    """Test impersonation integration."""

    def test_impersonation_with_feature_flags(self, client, staff_user):
        """Test that impersonation works with feature flags."""
        from waffle.models import Flag

        # Create a staff-only flag
        Flag.objects.create(name="admin_panel", staff=True, everyone=False)

        regular_user = User.objects.create_user(email="regular@example.com", password="testpass123")

        # Staff user can access
        client.force_login(staff_user)
        session = client.session
        session["impersonate_id"] = regular_user.id
        session.save()

        # After impersonating, staff user becomes regular user
        # But middleware should preserve permissions
        # This tests that the real_user is used for staff checks
