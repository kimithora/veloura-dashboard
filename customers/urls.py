from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customer_list'),
    path('add/', views.CustomerCreateView.as_view(), name='customer_add'),
    path('<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    path('<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
    path('measurements/', views.MeasurementListView.as_view(), name='measurement_list'),
    path('measurements/add/', views.MeasurementCreateView.as_view(), name='measurement_add'),
    path('orders/', views.CustomerOrdersTableView.as_view(), name='customer_orders'),
]
