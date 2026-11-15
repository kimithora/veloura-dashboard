from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('pos/', views.pos, name='pos'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('barcode/lookup/', views.barcode_lookup, name='barcode_lookup'),
    path('checkout/', views.checkout, name='checkout'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('<int:pk>/invoice/', views.invoice_pdf, name='invoice_pdf'),
]
