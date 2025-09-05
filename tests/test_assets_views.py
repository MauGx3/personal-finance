import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from personal_finance.assets.models import Asset

User = get_user_model()


@pytest.mark.django_db
def test_assets_view_requires_login():
    """Test that assets view requires authentication."""
    client = Client()
    url = reverse('assets:list')
    response = client.get(url)
    # Should redirect to login page
    assert response.status_code == 302
    assert '/accounts/login/' in response.url


@pytest.mark.django_db
def test_assets_view_authenticated_access():
    """Test that authenticated users can access assets view."""
    # Create a user
    username_field = getattr(User, 'USERNAME_FIELD', 'username')
    kwargs = {'password': 'testpass123', 'email': 'test@example.com'}
    if username_field != 'email':
        kwargs[username_field] = 'testuser'
    
    user = User.objects.create_user(**kwargs)
    
    client = Client()
    client.force_login(user)
    
    url = reverse('assets:list')
    response = client.get(url)
    
    assert response.status_code == 200
    assert 'Financial Assets' in response.context['title']


@pytest.mark.django_db
def test_assets_view_renders_template():
    """Test that assets view uses correct template."""
    # Create a user
    username_field = getattr(User, 'USERNAME_FIELD', 'username')
    kwargs = {'password': 'testpass123', 'email': 'test@example.com'}
    if username_field != 'email':
        kwargs[username_field] = 'testuser'
    
    user = User.objects.create_user(**kwargs)
    
    client = Client()
    client.force_login(user)
    
    url = reverse('assets:list')
    response = client.get(url)
    
    assert response.status_code == 200
    assert 'assets/assets.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_assets_page_contains_expected_elements():
    """Test that the assets page contains expected UI elements."""
    # Create a user
    username_field = getattr(User, 'USERNAME_FIELD', 'username')
    kwargs = {'password': 'testpass123', 'email': 'test@example.com'}
    if username_field != 'email':
        kwargs[username_field] = 'testuser'
    
    user = User.objects.create_user(**kwargs)
    
    # Create a test asset
    Asset.objects.create(
        symbol='TEST',
        name='Test Asset',
        asset_type=Asset.ASSET_STOCK,
        currency='USD'
    )
    
    client = Client()
    client.force_login(user)
    
    url = reverse('assets:list')
    response = client.get(url)
    
    content = response.content.decode('utf-8')
    
    # Check for key UI elements
    assert 'Financial Assets' in content
    assert 'Add Asset' in content
    assert 'assetsTable' in content
    assert '/api/assets/' in content  # API endpoint reference
    assert 'loadAssets()' in content  # JavaScript function


@pytest.mark.django_db 
def test_assets_url_name():
    """Test that the assets URL is correctly named."""
    url = reverse('assets:list')
    assert url == '/assets/'