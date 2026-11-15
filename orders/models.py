from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from core.models import BaseModel, AuditMixin
from customers.models import Customer


class Order(BaseModel, AuditMixin):
    """
    Custom couture order. Created by cashier, received and worked on by designer.
    """

    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', 'Order Received'
        MEASUREMENT = 'MEASUREMENT', 'Measurement'
        DESIGNING = 'DESIGNING', 'Designing'
        DESIGN_APPROVAL = 'DESIGN_APPROVAL', 'Design Approval'
        MATERIAL_PREP = 'MATERIAL_PREP', 'Material Preparation'
        PRODUCTION = 'PRODUCTION', 'Production'
        FITTING = 'FITTING', 'Fitting'
        QC = 'QC', 'Quality Control'
        COMPLETED = 'COMPLETED', 'Completed'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    order_number = models.CharField(max_length=64, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='custom_orders'
    )
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='created_orders',
        help_text='Cashier who created the order.',
    )
    designer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_orders',
        help_text='Designer assigned to this order.',
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.RECEIVED
    )
    order_date = models.DateTimeField(auto_now_add=True, db_index=True)
    required_date = models.DateField(null=True, blank=True, help_text='Delivery deadline.')
    description = models.TextField(blank=True, help_text='Customer request summary.')
    total_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    dp_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-order_date']
        verbose_name = 'Custom Order'
        verbose_name_plural = 'Custom Orders'
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status', '-order_date']),
            models.Index(fields=['designer', '-order_date']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_number()
        super().save(*args, **kwargs)

    def _generate_number(self):
        from django.utils import timezone
        today = timezone.localdate()
        prefix = 'ORD-{:%Y%m%d}-'.format(today)
        last = Order.objects.filter(order_number__startswith=prefix).order_by('-order_number').first()
        num = 1
        if last and last.order_number:
            try:
                num = int(last.order_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                num = 1
        return '{}{:04d}'.format(prefix, num)

    @property
    def remaining_balance(self):
        return (self.total_amount or 0) - (self.dp_amount or 0)

    def __str__(self):
        return self.order_number


class OrderStatusHistory(BaseModel):
    """
    Every status change on an order is recorded here.
    """
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='status_history'
    )
    status = models.CharField(max_length=20, choices=Order.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='order_status_changes',
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        indexes = [
            models.Index(fields=['order', '-changed_at']),
        ]

    def __str__(self):
        return '{} -> {}'.format(self.order.order_number, self.status)
