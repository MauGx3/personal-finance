#!/usr/bin/env python
"""
Simple test to verify the minimal test setup works.
This script can be run directly to test Django setup without pytest.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')

try:
    django.setup()
    print("✓ Django setup successful")
    
    # Test basic imports
    from django.contrib.auth import get_user_model
    User = get_user_model()
    print("✓ User model import successful")
    
    from personal_finance.assets.models import Asset, Portfolio, Holding
    print("✓ Asset models import successful")
    
    # Test basic database operations
    print(f"✓ User count: {User.objects.count()}")
    print(f"✓ Asset count: {Asset.objects.count()}")
    print(f"✓ Portfolio count: {Portfolio.objects.count()}")
    print(f"✓ Holding count: {Holding.objects.count()}")
    
    print("\n✓ All basic tests passed - minimal setup is working!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)