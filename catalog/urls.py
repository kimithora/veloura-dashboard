from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Brand
    path('brands/', views.BrandListView.as_view(), name='brand_list'),
    path('brands/add/', views.BrandCreateView.as_view(), name='brand_add'),
    path('brands/<int:pk>/edit/', views.BrandUpdateView.as_view(), name='brand_edit'),
    path('brands/<int:pk>/delete/', views.BrandDeleteView.as_view(), name='brand_delete'),

    # Category
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Product
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/archive/', views.ProductArchiveView.as_view(), name='product_archive'),

    # Product Variant
    path('products/<int:product_pk>/variants/add/', views.ProductVariantCreateView.as_view(), name='variant_add'),
    path('variants/<int:pk>/edit/', views.ProductVariantUpdateView.as_view(), name='variant_edit'),
    path('variants/<int:pk>/delete/', views.ProductVariantDeleteView.as_view(), name='variant_delete'),

    # Barcode
    path('barcodes/', views.BarcodeListView.as_view(), name='barcode_list'),
    path('barcodes/<int:pk>/regenerate/', views.regenerate_barcode, name='barcode_regenerate'),
    path('barcodes/label/<int:barcode_pk>/png/', views.barcode_label_png, name='barcode_label_png'),
    path('barcodes/label/<int:barcode_pk>/pdf/', views.barcode_label_pdf, name='barcode_label_pdf'),
    path('products/<int:variant_pk>/custom-barcode/', views.create_custom_barcode, name='custom_barcode'),
]
