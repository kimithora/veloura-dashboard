"""
URL configuration for the core app.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('health/', views.health_check, name='health_check'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('cashier-dashboard/', views.cashier_dashboard, name='cashier_dashboard'),
    path('designer-dashboard/', views.designer_dashboard, name='designer_dashboard'),
]
