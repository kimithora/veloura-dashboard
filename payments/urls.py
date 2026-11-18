from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('record/<int:transaction_pk>/', views.record_payment, name='record_payment'),
    path('confirm/<int:payment_pk>/', views.confirm_payment, name='confirm_payment'),
    path('void/<int:payment_pk>/', views.void_payment, name='void_payment'),
    path('<int:payment_pk>/', views.payment_detail, name='payment_detail'),
    path('transaction/<int:transaction_pk>/', views.transaction_payments, name='transaction_payments'),
    # Custom order payments
    path('orders/', views.order_payment_list, name='order_payment_list'),
    path('order/<int:order_pk>/record/', views.record_order_payment, name='record_order_payment'),
    path('order/confirm/<int:payment_pk>/', views.confirm_order_payment, name='confirm_order_payment'),
    path('order/void/<int:payment_pk>/', views.void_order_payment, name='void_order_payment'),
]
