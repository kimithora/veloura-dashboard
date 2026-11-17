from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    path('', views.ProductionListView.as_view(), name='production_list'),
    path('add/', views.ProductionCreateView.as_view(), name='production_add'),
    path('<int:pk>/', views.ProductionDetailView.as_view(), name='production_detail'),
    path('<int:pk>/update/', views.production_update, name='production_update'),
    path('material-requests/', views.MaterialRequestListView.as_view(), name='material_request_list'),
    path('material-requests/add/', views.MaterialRequestCreateView.as_view(), name='material_request_add'),
    path('material-requests/<int:pk>/action/', views.material_request_action, name='material_request_action'),
    path('material-usage/add/', views.MaterialUsageCreateView.as_view(), name='material_usage_add'),
    path('qc/', views.QualityControlListView.as_view(), name='qc_list'),
    path('qc/add/', views.QualityControlCreateView.as_view(), name='qc_add'),
    path('fittings/', views.FittingListView.as_view(), name='fitting_list'),
    path('fittings/add/', views.FittingCreateView.as_view(), name='fitting_add'),
]
