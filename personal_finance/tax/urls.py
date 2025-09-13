"""URL configuration for tax app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TaxYearViewSet, TaxLotViewSet, CapitalGainLossViewSet,
    DividendIncomeViewSet, TaxLossHarvestingOpportunityViewSet,
    TaxOptimizationRecommendationViewSet, TaxReportViewSet,
    TaxAnalyticsViewSet
)

app_name = 'tax'

# API Router
router = DefaultRouter()
router.register(r'tax-years', TaxYearViewSet, basename='taxyear')
router.register(r'tax-lots', TaxLotViewSet, basename='taxlot')
router.register(r'capital-gains-losses', CapitalGainLossViewSet, basename='capitalgainloss')
router.register(r'dividend-income', DividendIncomeViewSet, basename='dividendincome')
router.register(r'loss-harvesting', TaxLossHarvestingOpportunityViewSet, basename='lossharvesting')
router.register(r'recommendations', TaxOptimizationRecommendationViewSet, basename='recommendations')
router.register(r'reports', TaxReportViewSet, basename='reports')
router.register(r'analytics', TaxAnalyticsViewSet, basename='analytics')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
]