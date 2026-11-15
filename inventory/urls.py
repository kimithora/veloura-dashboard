from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('materials/', views.MaterialListView.as_view(), name='material_list'),
    path('materials/add/', views.MaterialCreateView.as_view(), name='material_add'),
    path('materials/<int:pk>/edit/', views.MaterialUpdateView.as_view(), name='material_edit'),
    path('materials/<int:pk>/delete/', views.MaterialDeleteView.as_view(), name='material_delete'),
    path('materials/<int:pk>/adjust/', views.material_stock_adjust, name='material_stock_adjust'),
    path('movements/', views.StockMovementListView.as_view(), name='movement_list'),
]
