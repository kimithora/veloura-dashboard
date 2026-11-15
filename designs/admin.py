from django.contrib import admin
from .models import Design, DesignVersion


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ('design_id', 'name', 'order', 'category', 'status', 'designer', 'created_at')
    list_filter = ('status', 'category', 'designer')
    search_fields = ('design_id', 'name', 'order__order_number')
    ordering = ['-created_at']


@admin.register(DesignVersion)
class DesignVersionAdmin(admin.ModelAdmin):
    list_display = ('design', 'version_number', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('design__design_id',)
    ordering = ['-version_number']
