"""
Inventory app models.

Defines Material (raw & supporting materials) and StockMovement ledger.
StockMovement uses a generic foreign key so it can reference either a
ProductVariant (finished goods) or a Material (raw/supporting materials).
"""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from core.models import BaseModel, AuditMixin


class Material(BaseModel, AuditMixin):
    """
    Raw materials and supporting materials held in inventory.
    """

    class Category(models.TextChoices):
        RAW_MATERIAL = 'RAW_MATERIAL', 'Raw Material'
        SUPPORTING_MATERIAL = 'SUPPORTING_MATERIAL', 'Supporting Material'

    class Unit(models.TextChoices):
        PCS = 'PCS', 'Pieces'
        METER = 'METER', 'Meter'
        ROLL = 'ROLL', 'Roll'
        KG = 'KG', 'Kilogram'
        YARD = 'YARD', 'Yard'

    material_id = models.CharField(max_length=32, unique=True, blank=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices)
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.PCS)
    stock_quantity = models.DecimalField(
        max_digits=12, decimal_places=3, default=0,
        validators=[MinValueValidator(0)],
    )
    min_stock = models.DecimalField(
        max_digits=12, decimal_places=3, default=0,
        validators=[MinValueValidator(0)],
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='supplied_materials',
    )
    purchase_price = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        indexes = [
            models.Index(fields=['material_id']),
            models.Index(fields=['category']),
        ]

    def save(self, *args, **kwargs):
        if not self.material_id:
            last = Material.objects.order_by('-material_id').first()
            num = 1
            if last and last.material_id and last.material_id.startswith('MAT-'):
                try:
                    num = int(last.material_id.split('-')[1]) + 1
                except (ValueError, IndexError):
                    num = 1
            self.material_id = 'MAT-{:04d}'.format(num)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.material_id, self.name)

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock

    @property
    def valuation(self):
        return self.stock_quantity * self.purchase_price


class StockMovement(BaseModel):
    """
    Stock movement ledger. Every inventory change (sales, purchase,
    production usage/output, return, adjustment, damage/loss) is recorded
    here with previous/new stock and a reference to the originating record.

    Note: the ledger records the movement; the source item stock is updated
    explicitly in the service layer inside a database transaction.
    """

    class MovementType(models.TextChoices):
        PURCHASE = 'PURCHASE', 'Purchase'
        SALES = 'SALES', 'Sales'
        PRODUCTION_USAGE = 'PRODUCTION_USAGE', 'Production Usage'
        PRODUCTION_OUTPUT = 'PRODUCTION_OUTPUT', 'Production Output'
        RETURN = 'RETURN', 'Return'
        ADJUSTMENT = 'ADJUSTMENT', 'Adjustment'
        DAMAGE_LOSS = 'DAMAGE_LOSS', 'Damage or Loss'

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    movement_type = models.CharField(max_length=24, choices=MovementType.choices)
    quantity = models.DecimalField(
        max_digits=12, decimal_places=3, default=0,
        validators=[MinValueValidator(0)],
        help_text='Absolute quantity moved.',
    )
    previous_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    new_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    reference = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stock_movements',
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        indexes = [
            models.Index(fields=['movement_type', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return '{} - {}'.format(self.get_movement_type_display(), self.quantity)
