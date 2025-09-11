"""URL configuration for backtesting app."""

from django.urls import path, include

app_name = 'backtesting'

urlpatterns = [
    path('api/', include('personal_finance.backtesting.api.urls')),
]