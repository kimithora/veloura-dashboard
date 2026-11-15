"""
Catalogue app models.

Defines Brand, Category, Product, ProductVariant and Barcode.
Supports three product sources: Veloura Original, Third-Party Purchased,
Third-Party Consignment.
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from core.models import BaseModel, AuditMixin
from suppliers.models import Supplier


class Brand(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(BaseModel):
    """
    Base product definition. Variants (size/color) hold stock and barcodes.
    """

    class Source(models.TextChoices):
        VEL_ORIGINAL = 'VEL_ORIGINAL', 'Veloura Original'
        THIRD_PURCHASED = 'THIRD_PURCHASED', 'Third-Party Purchased'
        THIRD_CONSIGNMENT = 'THIRD_CONSIGNMENT', 'Third-Party Consignment'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'

    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products'
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, related_name='products', blank=True, null=True
    )
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.VEL_ORIGINAL)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='supplied_products',
        help_text='Required for third-party products.',
    )
    purchase_price = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
        help_text='Cost price (for third-party / own manufacture).',
    )
    selling_price = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
    )
    min_stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['status']),
            models.Index(fields=['source']),
        ]

    def __str__(self):
        return f'{self.sku} - {self.name}'

    @property
    def total_stock(self):
        return sum(v.stock_quantity for v in self.variants.filter(is_active=True))

    @property
    def is_low_stock(self):
        return self.total_stock <= self.min_stock


class ProductVariant(BaseModel):
    """
    A specific size/color variant of a product, with its own stock and barcode.
    """
    class Size(models.TextChoices):
        XS = 'XS', 'XS'
        S = 'S', 'S'
        M = 'M', 'M'
        L = 'L', 'L'
        XL = 'XL', 'XL'
        XXL = 'XXL', 'XXL'
        ONE_SIZE = 'ONE_SIZE', 'One Size'

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variants'
    )
    sku = models.CharField(max_length=64, unique=True)
    barcode = models.CharField(max_length=64, unique=True, blank=True)
    size = models.CharField(max_length=16, choices=Size.choices, default=Size.ONE_SIZE)
    color = models.CharField(max_length=64, default='Standard')
    stock_quantity = models.PositiveIntegerField(default=0)
    selling_price = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text='Leave empty to use the product selling price.',
    )
    purchase_price = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['product__sku', 'size', 'color']
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        unique_together = [('product', 'size', 'color')]
        indexes = [
            models.Index(fields=['barcode']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f'{self.product.sku} / {self.size} / {self.color}'

    @property
    def effective_selling_price(self):
        return self.selling_price if self.selling_price is not None else self.product.selling_price

    @property
    def effective_purchase_price(self):
        return self.purchase_price if self.purchase_price is not None else self.product.purchase_price

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.product.min_stock


class Barcode(BaseModel):
    """
    Barcode identifier history for a product variant. Prevents duplicate
    barcode identifiers and supports regeneration with authorization.
    """
    class Format(models.TextChoices):
        CODE_128 = 'CODE_128', 'Code 128'
        EAN13 = 'EAN13', 'EAN-13'

    product_variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name='barcodes'
    )
    barcode_value = models.CharField(max_length=64, unique=True)
    format = models.CharField(max_length=10, choices=Format.choices, default=Format.CODE_128)
    is_active = models.BooleanField(default=True)
    regenerated_from = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='regenerations',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Barcode'
        verbose_name_plural = 'Barcodes'
        indexes = [
            models.Index(fields=['barcode_value']),
            models.Index(fields=['product_variant']),
        ]

    def __str__(self):
        return self.barcode_value

    def save(self, *args, **kwargs):
        # Validate uniqueness at the database level is enforced by unique=True.
        super().save(*args, **kwargs)
