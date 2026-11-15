from django.contrib import admin
from .models import Material, StockMovement


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('material_id', 'name', 'category', 'unit', 'stock_quantity', 'min_stock', 'is_low_stock', 'supplier')
    list_filter = ('category', 'unit', 'supplier')
    search_fields = ('material_id', 'name')
    ordering = ['-created_at']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'user', 'reference')
    list_filter = ('movement_type', 'user', 'created_at')
    search_fields = ('reference', 'notes', 'user__username')
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
