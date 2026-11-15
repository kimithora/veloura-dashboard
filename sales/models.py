from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from core.models import BaseModel, AuditMixin
from catalog.models import ProductVariant
from customers.models import Customer


class Transaction(BaseModel, AuditMixin):
    class PaymentStatus(models.TextChoices):
        UNPAID = 'UNPAID', 'Unpaid'
        PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
        PAID = 'PAID', 'Paid'
        REFUNDED = 'REFUNDED', 'Refunded'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REFUNDED = 'REFUNDED', 'Refunded'

    transaction_number = models.CharField(max_length=64, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transactions',
    )
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='transactions',
    )
    transaction_date = models.DateTimeField(auto_now_add=True, db_index=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    stock_deducted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['transaction_number']),
            models.Index(fields=['cashier', '-transaction_date']),
            models.Index(fields=['status', 'payment_status']),
        ]

    def save(self, *args, **kwargs):
        if not self.transaction_number:
            self.transaction_number = self._generate_number()
        super().save(*args, **kwargs)

    def _generate_number(self):
        from django.utils import timezone
        today = timezone.localdate()
        prefix = 'TRX-{:%Y%m%d}-'.format(today)
        last = Transaction.objects.filter(transaction_number__startswith=prefix).order_by('-transaction_number').first()
        num = 1
        if last and last.transaction_number:
            try:
                num = int(last.transaction_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                num = 1
        return '{}{:04d}'.format(prefix, num)

    @property
    def paid_amount(self):
        """Total confirmed payments (decimal)."""
        from django.db.models import Sum
        agg = self.payments.filter(status='CONFIRMED').aggregate(total=Sum('amount'))
        return agg['total'] or Decimal('0')

    @property
    def remaining_balance(self):
        """Grand total minus confirmed payments (decimal)."""
        return (self.grand_total or Decimal('0')) - self.paid_amount

    @property
    def is_fully_paid(self):
        return self.payment_status == self.PaymentStatus.PAID

    def __str__(self):
        return self.transaction_number


class TransactionItem(BaseModel):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name='items'
    )
    product_variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name='transaction_items'
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs):
        self.total = (self.unit_price * self.quantity) - self.discount
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} x{} @ {}'.format(self.product_variant.sku, self.quantity, self.unit_price)
