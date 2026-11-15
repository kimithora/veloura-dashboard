from django.contrib import admin
from .models import Production, MaterialRequest, MaterialUsage, Fitting, QualityControl


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ('production_id', 'order', 'designer', 'status', 'progress', 'start_date', 'estimated_completion')
    list_filter = ('status', 'designer')
    search_fields = ('production_id', 'order__order_number')
    ordering = ['-created_at']


@admin.register(MaterialRequest)
class MaterialRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'production', 'material', 'quantity', 'status', 'requested_by')
    list_filter = ('status', 'material')
    search_fields = ('request_id', 'material__name')
    ordering = ['-created_at']


@admin.register(MaterialUsage)
class MaterialUsageAdmin(admin.ModelAdmin):
    list_display = ('usage_id', 'production', 'material', 'quantity_used', 'used_at', 'used_by')
    list_filter = ('used_at', 'material')
    search_fields = ('usage_id', 'material__name')
    ordering = ['-used_at']


@admin.register(Fitting)
class FittingAdmin(admin.ModelAdmin):
    list_display = ('fitting_id', 'order', 'customer', 'status', 'scheduled_date')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('fitting_id', 'order__order_number')
    ordering = ['-scheduled_date']


@admin.register(QualityControl)
class QualityControlAdmin(admin.ModelAdmin):
    list_display = ('qc_id', 'order', 'status', 'qc_by', 'qc_date')
    list_filter = ('status', 'qc_date')
    search_fields = ('qc_id', 'order__order_number')
    ordering = ['-created_at']
