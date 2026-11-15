from django.contrib import admin
from .models import Brand, Category, Product, ProductVariant, Barcode


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'brand', 'source', 'status', 'selling_price')
    list_filter = ('source', 'status', 'category', 'brand')
    search_fields = ('sku', 'name')
    ordering = ['-created_at']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('sku', 'product', 'size', 'color', 'barcode', 'stock_quantity', 'is_active')
    list_filter = ('is_active', 'size', 'color')
    search_fields = ('sku', 'barcode', 'product__name')
    ordering = ['-created_at']


@admin.register(Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    list_display = ('barcode_value', 'product_variant', 'format', 'is_active', 'created_at')
    list_filter = ('format', 'is_active')
    search_fields = ('barcode_value',)
    ordering = ['-created_at']
