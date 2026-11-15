"""
Django admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('username',)
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Veloura Profile', {'fields': ('phone', 'address', 'role')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Veloura Profile', {'fields': ('phone', 'address', 'role')}),
    )
