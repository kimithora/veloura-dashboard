from django.urls import path
from . import views

app_name = 'designs'

urlpatterns = [
    path('', views.DesignListView.as_view(), name='design_list'),
    path('add/', views.DesignCreateView.as_view(), name='design_add'),
    path('<int:pk>/', views.DesignDetailView.as_view(), name='design_detail'),
    path('<int:pk>/edit/', views.DesignUpdateView.as_view(), name='design_edit'),
    path('<int:pk>/status/', views.update_design_status, name='update_design_status'),
]
