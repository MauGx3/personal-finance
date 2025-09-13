"""
URL patterns for real-time API endpoints and views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api, views

app_name = 'realtime'

# API router
router = DefaultRouter()
router.register('realtime', api.RealtimeViewSet, basename='realtime')

urlpatterns = [
    # Dashboard views
    path('dashboard/', views.RealtimeDashboardView.as_view(), name='dashboard'),
    path('status/', views.realtime_status, name='status'),
    path('websocket-info/', views.websocket_info, name='websocket_info'),
    path('test/', views.websocket_test, name='test'),
    
    # API endpoints
    path('api/', include(router.urls)),
]