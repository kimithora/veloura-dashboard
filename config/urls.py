"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. Includes all feature apps.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('customers/', include('customers.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('catalog/', include('catalog.urls')),
    path('inventory/', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('payments/', include('payments.urls')),
    path('orders/', include('orders.urls')),
    path('designs/', include('designs.urls')),
    path('production/', include('production.urls')),
    path('documents/', include('documents.urls')),
    path('analytics/', include('analytics.urls')),
    path('notifications/', include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
