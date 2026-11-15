from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_id', 'name', 'contact_person', 'phone', 'supplier_type')
    list_filter = ('supplier_type',)
    search_fields = ('supplier_id', 'name', 'contact_person', 'email')
    ordering = ['-created_at']
