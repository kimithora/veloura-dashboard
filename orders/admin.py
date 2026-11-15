from django.contrib import admin
from .models import Order, OrderStatusHistory


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'cashier', 'designer', 'status', 'order_date', 'total_amount')
    list_filter = ('status', 'designer', 'cashier')
    search_fields = ('order_number', 'customer__full_name')
    ordering = ['-order_date']
    date_hierarchy = 'order_date'


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'changed_by', 'changed_at')
    list_filter = ('status', 'changed_at')
    search_fields = ('order__order_number',)
    ordering = ['-changed_at']
