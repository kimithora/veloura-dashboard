from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'full_name', 'phone', 'email', 'source', 'total_spending')
    list_filter = ('source',)
    search_fields = ('customer_id', 'full_name', 'phone', 'email')
    ordering = ['-created_at']
