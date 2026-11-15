from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from core.models import BaseModel, AuditMixin
from orders.models import Order


class Design(BaseModel, AuditMixin):
    """
    Fashion design linked to a custom order.
    """

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PENDING_APPROVAL = 'PENDING_APPROVAL', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        IN_PRODUCTION = 'IN_PRODUCTION', 'In Production'
        COMPLETED = 'COMPLETED', 'Completed'

    class Category(models.TextChoices):
        DRESS = 'DRESS', 'Dress'
        SHIRT = 'SHIRT', 'Shirt'
        BLAZER = 'BLAZER', 'Blazer'
        SKIRT = 'SKIRT', 'Skirt'
        TROUSERS = 'TROUSERS', 'Trousers'
        ACCESSORIES = 'ACCESSORIES', 'Accessories'

    design_id = models.CharField(max_length=32, unique=True, blank=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='designs'
    )
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.DRESS)
    sketch = models.ImageField(upload_to='designs/sketches/', blank=True, null=True)
    customer_reference = models.ImageField(upload_to='designs/references/', blank=True, null=True)
    fabric = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, blank=True)
    style_description = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    designer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='designs',
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    estimated_cost = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    estimated_duration_days = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Design'
        verbose_name_plural = 'Designs'
        indexes = [
            models.Index(fields=['design_id']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['designer', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.design_id:
            last = Design.objects.order_by('-design_id').first()
            num = 1
            if last and last.design_id and last.design_id.startswith('DSN-'):
                try:
                    num = int(last.design_id.split('-')[1]) + 1
                except (ValueError, IndexError):
                    num = 1
            self.design_id = 'DSN-{:04d}'.format(num)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.design_id, self.name)


class DesignVersion(BaseModel):
    """
    Design revision history.
    """
    design = models.ForeignKey(
        Design, on_delete=models.CASCADE, related_name='versions'
    )
    version_number = models.PositiveIntegerField(default=1)
    sketch = models.ImageField(upload_to='designs/versions/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='design_versions',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        verbose_name = 'Design Version'
        verbose_name_plural = 'Design Versions'
        unique_together = [('design', 'version_number')]

    def __str__(self):
        return '{} v{}'.format(self.design.design_id, self.version_number)
