# Integration guide for stock analysis URLs

# Add this to your main config/urls.py file:

from django.urls import path, include

urlpatterns = [
    # ... existing URL patterns ...
    
    # Stock Analysis API
    path('analytics/', include('personal_finance.analytics.urls')),
    
    # ... other URL patterns ...
]

# This will make the stock analysis API available at:
# - /analytics/api/stock/{symbol}/analysis/
# - /analytics/api/stock/{symbol}/financials/
# - /analytics/api/stock/{symbol}/technical/
# - /analytics/api/stock/{symbol}/quote/
# - /analytics/api/stock/{symbol}/sentiment/
# - /analytics/api/stock/{symbol}/sector-comparison/
# - /analytics/api/stocks/compare/