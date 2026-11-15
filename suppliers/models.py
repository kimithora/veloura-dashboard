"""
Suppliers app models.

Defines the Supplier entity with two models: Direct Purchase and Consignment.
"""

from django.core.validators import MinValueValidator
from django.db import models

from core.models import BaseModel, AuditMixin


class Supplier(BaseModel, AuditMixin):
    """
    Supplier. Two models supported:
      - Direct Purchase: Veloura owns the inventory.
      - Consignment: supplier retains ownership until sale.
    """

    class SupplierType(models.TextChoices):
        DIRECT_PURCHASE = 'DIRECT_PURCHASE', 'Direct Purchase'
        CONSIGNMENT = 'CONSIGNMENT', 'Consignment'

    supplier_id = models.CharField(max_length=32, unique=True, blank=True)
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    supplier_type = models.CharField(
        max_length=16, choices=SupplierType.choices, default=SupplierType.DIRECT_PURCHASE
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        indexes = [
            models.Index(fields=['supplier_id']),
            models.Index(fields=['supplier_type']),
        ]

    def save(self, *args, **kwargs):
        if not self.supplier_id:
            last = Supplier.objects.order_by('-supplier_id').first()
            num = 1
            if last and last.supplier_id and last.supplier_id.startswith('SUP-'):
                try:
                    num = int(last.supplier_id.split('-')[1]) + 1
                except (ValueError, IndexError):
                    num = 1
            self.supplier_id = f'SUP-{num:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.supplier_id} - {self.name}'

    @property
    def is_consignment(self):
        return self.supplier_type == self.SupplierType.CONSIGNMENT
